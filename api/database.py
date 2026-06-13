import sqlite3
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), 'votes.db')

def init_db():
    # Crée la base de données et la table si elle n'existe pas encore
    conn = sqlite3.connect(DB_PATH)
    # sqlite3.connect = ouvre ou crée le fichier votes.db
    
    cursor = conn.cursor()
    # cursor = objet qui permet d'exécuter des requêtes SQL
    
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
    # CREATE TABLE IF NOT EXISTS = crée la table seulement si elle n'existe pas
    # id = identifiant unique auto-incrémenté
    # filename = nom du fichier schematic
    # size/aesthetic/complexity_score = notes de 1 à 5
    # created_at = date et heure du vote automatique
    
    conn.commit()
    # commit = on sauvegarde les changements
    conn.close()
    # close = on ferme la connexion

def ajouter_vote(filename, size, aesthetic, complexity):
    # Ajoute un vote dans la base de données
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO votes (filename, size_score, aesthetic_score, complexity_score)
        VALUES (?, ?, ?, ?)
    ''', (filename, size, aesthetic, complexity))
    # INSERT INTO = on insère une nouvelle ligne
    # VALUES (?, ?, ?, ?) = les ? sont remplacés par les valeurs
    # C'est plus sécurisé que d'écrire les valeurs directement
    
    conn.commit()
    conn.close()

def get_scores(filename):
    # Récupère la moyenne des votes pour un fichier donné
    conn = sqlite3.connect(DB_PATH)
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
    # AVG = moyenne
    # COUNT = nombre de votes
    # WHERE filename = ? = seulement les votes pour ce fichier
    
    row = cursor.fetchone()
    # fetchone = récupère la première (et seule) ligne du résultat
    conn.close()
    
    if row and row[3] > 0:
        # Si il y a au moins un vote
        return {
            "size": round(row[0], 1),
            "aesthetic": round(row[1], 1),
            "complexity": round(row[2], 1),
            "global": round((row[0] + row[1] + row[2]) / 3, 1),
            "nb_votes": int(row[3])
        }
    return None
    # Retourne None si pas de votes pour ce fichier

def get_all_scores(filename):
    # Récupère tous les votes individuels pour un fichier
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT size_score, aesthetic_score, complexity_score, created_at
        FROM votes
        WHERE filename = ?
        ORDER BY created_at DESC
    ''', (filename,))
    # ORDER BY created_at DESC = du plus récent au plus ancien
    
    rows = cursor.fetchall()
    # fetchall = récupère toutes les lignes
    conn.close()
    return rows

def get_all_votes():
    # Récupère toutes les maisons ayant reçu des votes, avec leurs moyennes
    # Utilisé par l'endpoint /gallery pour afficher la galerie style Airbnb
    conn = sqlite3.connect(DB_PATH)
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
    # GROUP BY filename = on regroupe par fichier pour avoir une ligne par maison
    # AVG = moyenne des votes reçus
    # ORDER BY MAX(created_at) DESC = les plus récemment votées en premier
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "filename": row[0],
            "size": round(row[1], 1),
            "aesthetic": round(row[2], 1),
            "complexity": round(row[3], 1),
            "global": round((row[1] + row[2] + row[3]) / 3, 1),
            "nb_votes": int(row[4])
        }
        for row in rows
    ]