import sqlite3
import os
import logging

# Logger pour tracer les erreurs sans crasher le serveur
logger = logging.getLogger(__name__)

# Chemin vers la base de données SQLite, relatif à ce fichier
DB_PATH = os.path.join(os.path.dirname(__file__), 'votes.db')


def init_db():
    """Crée la base de données et la table votes si elle n'existe pas encore."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                size_score INTEGER NOT NULL,
                aesthetic_score INTEGER NOT NULL,
                complexity_score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        # Garantit la fermeture même si une erreur survient
        conn.close()


def ajouter_vote(filename: str, size: int, aesthetic: int, complexity: int):
    """
    Insère un nouveau vote dans la base de données.
    Les ? protègent contre les injections SQL.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO votes (filename, size_score, aesthetic_score, complexity_score)
            VALUES (?, ?, ?, ?)
        ''', (filename, size, aesthetic, complexity))
        conn.commit()
    except sqlite3.Error as e:
        logger.error("Erreur lors de l'ajout du vote pour %s : %s", filename, e)
        raise
    finally:
        conn.close()


def get_scores(filename: str) -> dict | None:
    """
    Retourne la moyenne des votes pour un fichier donné.
    Retourne None si aucun vote n'existe pour ce fichier.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(size_score),
                AVG(aesthetic_score),
                AVG(complexity_score),
                COUNT(*)
            FROM votes
            WHERE filename = ?
        ''', (filename,))
        row = cursor.fetchone()
    finally:
        conn.close()

    if row and row[3] > 0:
        return {
            "size":       round(row[0], 1),
            "aesthetic":  round(row[1], 1),
            "complexity": round(row[2], 1),
            "global":     round((row[0] + row[1] + row[2]) / 3, 1),
            "nb_votes":   int(row[3]),
        }
    return None


def get_all_scores(filename: str) -> list:
    """Retourne tous les votes individuels pour un fichier, du plus récent au plus ancien."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT size_score, aesthetic_score, complexity_score, created_at
            FROM votes
            WHERE filename = ?
            ORDER BY created_at DESC
        ''', (filename,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_votes() -> list:
    """
    Retourne toutes les structures ayant reçu des votes avec leurs moyennes.
    Utilisé par /gallery pour afficher les structures les plus récemment votées.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                filename,
                AVG(size_score),
                AVG(aesthetic_score),
                AVG(complexity_score),
                COUNT(*)
            FROM votes
            GROUP BY filename
            ORDER BY MAX(created_at) DESC
        ''')
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "filename":   row[0],
            "size":       round(row[1], 1),
            "aesthetic":  round(row[2], 1),
            "complexity": round(row[3], 1),
            "global":     round((row[1] + row[2] + row[3]) / 3, 1),
            "nb_votes":   int(row[4]),
        }
        for row in rows
    ]