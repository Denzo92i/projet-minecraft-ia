# Point d'entrée principal de l'API FastAPI
# Gère la classification de fichiers .schem/.schematic via un modèle Random Forest

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pickle
import os
import logging

from parsing.parser import lire_schem
from parsing.preprocessor import pretraiter
from parsing.features import extraire_features

# Configuration du logger pour tracer les erreurs sans crasher le serveur
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Minecraft Schematic AI Classifier",
    description="Classifie des structures Minecraft (.schem/.schematic) et génère des scores esthétiques.",
    version="1.0.0",
)

# Middleware CORS : autorise le frontend (même cross-origin) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CHARGEMENT DU MODÈLE
# =========================

MODEL_PATH = "model/classifier.pkl"

# Chargement au démarrage du serveur (une seule fois, pas à chaque requête)
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    logger.info("✅ Modèle chargé depuis %s", MODEL_PATH)
else:
    model = None
    logger.warning("⚠️ Modèle non trouvé à %s — /predict retournera une erreur", MODEL_PATH)

# Base de données en mémoire pour stocker les votes utilisateurs
# (réinitialisée au redémarrage du serveur — suffisant pour un projet de démonstration)
votes_db: dict = {}


# =========================
# SCHÉMAS PYDANTIC
# =========================

class Vote(BaseModel):
    """Corps de la requête POST /vote"""
    filename: str
    size: int       # Note de 1 à 5
    aesthetic: int  # Note de 1 à 5
    complexity: int # Note de 1 à 5


# =========================
# HELPERS
# =========================

def compute_ui_scores(grid: np.ndarray) -> dict:
    """
    Calcule les scores automatiques à partir de la grille voxel normalisée.

    La densité brute d'un build Minecraft est très faible (souvent < 5%)
    car la majorité de la grille est de l'air. On applique un facteur x15
    pour ramener la plage utile [0, ~0.2] vers [0, 1] avant de scorer.

    Args:
        grid: Grille 3D numpy après prétraitement (blocs non-air = non-zéro)

    Returns:
        Dictionnaire avec les scores size, aesthetic, complexity et global (1-5)
    """
    total = grid.size
    blocks = int(np.count_nonzero(grid))

    if total == 0:
        # Grille vide : on retourne le score minimal pour éviter une division par zéro
        return {"size": 1, "aesthetic": 1, "complexity": 1, "global": 1.0}

    # Densité brute : ratio blocs solides / volume total
    density = blocks / total

    # Amplification pour corriger le biais de sparsité (voir README — section Méthodologie)
    norm_density = float(np.clip(density * 15, 0, 1))

    # Conversion en scores 1-5 avec des coefficients différenciés par dimension
    size       = int(np.clip(norm_density * 5,       1, 5))
    aesthetic  = int(np.clip(norm_density * 4 + 1,   1, 5))
    complexity = int(np.clip(norm_density * 6 + 1,   1, 5))
    global_score = round((size + aesthetic + complexity) / 3, 2)

    return {
        "size": size,
        "aesthetic": aesthetic,
        "complexity": complexity,
        "global": global_score,
    }


def save_temp_file(file_content: bytes, filename: str) -> str:
    """
    Sauvegarde temporairement un fichier uploadé sur disque pour le parser.
    Retourne le chemin du fichier temporaire créé.
    """
    # Préfixe "tmp_" pour identifier facilement les fichiers à nettoyer
    filepath = f"tmp_{filename}"
    with open(filepath, "wb") as f:
        f.write(file_content)
    return filepath


# =========================
# ROUTES
# =========================

@app.get("/health")
def health_check():
    """
    Endpoint de santé utilisé par Docker et les outils de monitoring.
    Retourne le statut du serveur et indique si le modèle est chargé.
    """
    return {
        "status": "ok",
        "model_loaded": model is not None,
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """
    Endpoint principal : reçoit un fichier .schem ou .schematic,
    le parse, extrait les features et retourne la classification + les scores.
    """
    # Validation du format de fichier avant tout traitement
    if not file.filename.endswith((".schem", ".schematic")):
        raise HTTPException(
            status_code=422,
            detail="Format invalide : seuls les fichiers .schem et .schematic sont acceptés."
        )

    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle de classification n'est pas chargé. Vérifiez model/classifier.pkl."
        )

    # Lecture du contenu en mémoire avant d'écrire sur disque
    file_content = await file.read()
    filepath = save_temp_file(file_content, file.filename)

    try:
        # Pipeline : parsing NBT → prétraitement → extraction de features → prédiction
        grille_brute, palette = lire_schem(filepath)
        grille = pretraiter(grille_brute, palette)
        features = np.array(extraire_features(grille)).reshape(1, -1)

        # Prédiction probabiliste (plus riche que predict() seul)
        proba = model.predict_proba(features)[0]
        pred = int(np.argmax(proba))
        confidence = float(np.max(proba))

        # Scores automatiques basés sur la densité voxel
        scores_auto = compute_ui_scores(grille)

        # Scores humains s'ils existent déjà pour ce fichier
        scores_humains = votes_db.get(file.filename)

        return {
            "filename": file.filename,
            "is_house": bool(pred),
            "confidence": round(confidence, 4),
            "scores_auto": scores_auto,
            "scores_humains": scores_humains,
        }

    except ValueError as e:
        # Erreur de parsing ou de format NBT inattendu
        logger.error("Erreur de parsing pour %s : %s", file.filename, e)
        raise HTTPException(status_code=422, detail=f"Erreur de lecture du fichier : {e}")

    except Exception as e:
        # Erreur inattendue : on log sans exposer les détails internes au client
        logger.error("Erreur inattendue pour %s : %s", file.filename, e)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")

    finally:
        # Nettoyage garanti du fichier temporaire, même en cas d'erreur
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info("Fichier temporaire supprimé : %s", filepath)


@app.post("/vote")
def vote(v: Vote):
    """
    Enregistre le vote d'un utilisateur pour un fichier donné
    et retourne les scores moyens mis à jour.
    """
    # Validation des plages de notes (1-5 uniquement)
    for field, value in [("size", v.size), ("aesthetic", v.aesthetic), ("complexity", v.complexity)]:
        if not (1 <= value <= 5):
            raise HTTPException(
                status_code=422,
                detail=f"Le champ '{field}' doit être compris entre 1 et 5."
            )

    # Initialisation de l'entrée si c'est le premier vote pour ce fichier
    if v.filename not in votes_db:
        votes_db[v.filename] = {
            "size": 0,
            "aesthetic": 0,
            "complexity": 0,
            "nb_votes": 0,
        }

    # Accumulation des votes pour calculer la moyenne ensuite
    entry = votes_db[v.filename]
    entry["size"]       += v.size
    entry["aesthetic"]  += v.aesthetic
    entry["complexity"] += v.complexity
    entry["nb_votes"]   += 1

    n = entry["nb_votes"]

    return {
        "scores": {
            "size":       round(entry["size"]       / n, 2),
            "aesthetic":  round(entry["aesthetic"]  / n, 2),
            "complexity": round(entry["complexity"] / n, 2),
            "global":     round((entry["size"] + entry["aesthetic"] + entry["complexity"]) / (3 * n), 2),
            "nb_votes":   n,
        }
    }


@app.get("/preview/{filename}")
def preview(filename: str):
    """
    Retourne la grille voxel prétraitée d'un fichier déjà présent dans data/.
    Utilisé par le viewer 3D du frontend.
    """
    # Recherche du fichier dans les deux catégories du dataset
    maison_path = f"data/maison/{filename}"
    autre_path  = f"data/autre/{filename}"

    if os.path.exists(maison_path):
        path = maison_path
    elif os.path.exists(autre_path):
        path = autre_path
    else:
        raise HTTPException(status_code=404, detail=f"Fichier '{filename}' introuvable dans data/.")

    try:
        grille_brute, palette = lire_schem(path)
        grille = pretraiter(grille_brute, palette)
        return {"grid": grille.tolist()}

    except Exception as e:
        logger.error("Erreur preview pour %s : %s", filename, e)
        raise HTTPException(status_code=500, detail=f"Erreur lors du prétraitement : {e}")