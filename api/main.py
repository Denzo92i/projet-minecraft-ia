from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import sys
import os
import tempfile

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(ROOT_DIR, 'api')
PARSING_DIR = os.path.join(ROOT_DIR, 'parsing')

sys.path.insert(0, API_DIR)
sys.path.insert(0, PARSING_DIR)

from parser import lire_schem
from preprocessor import pretraiter, convertir_grille, crop_air
from features import extraire_features
from database import init_db, ajouter_vote, get_scores, get_all_votes

init_db()

app = FastAPI(title="Minecraft House Classifier")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

modele_path = os.path.join(ROOT_DIR, 'model', 'classifier.pkl')
with open(modele_path, "rb") as f:
    modele = pickle.load(f)

# Cache en mémoire : on stocke la grille RÉELLE (avant normalisation 32x32x32)
# pour que le viewer affiche la vraie structure lisible
grilles_cache = {}


class Vote(BaseModel):
    filename: str
    size: int
    aesthetic: int
    complexity: int


def calculer_scores_auto(features):
    densite       = features[0]
    prop_verre    = features[3]
    prop_deco     = features[4]
    prop_toit     = features[5]
    hauteur       = features[8]
    largeur       = features[9]
    profondeur    = features[10]
    a_un_toit     = features[12]
    air_interieur = features[13]
    diversite     = features[14]

    volume = hauteur * largeur * profondeur
    if volume < 500:        size_score = 1
    elif volume < 2000:     size_score = 2
    elif volume < 5000:     size_score = 3
    elif volume < 15000:    size_score = 4
    else:                   size_score = 5

    score_esth = 1
    if diversite >= 2:      score_esth += 1
    if prop_verre > 0.01:   score_esth += 1
    if prop_deco > 0.005:   score_esth += 1
    if diversite >= 5:      score_esth += 1
    aesthetic_score = min(score_esth, 5)

    score_comp = 1
    if a_un_toit:           score_comp += 1
    if air_interieur:       score_comp += 1
    if prop_toit > 0.02:    score_comp += 1
    if densite > 0.15:      score_comp += 1
    complexity_score = min(score_comp, 5)

    global_score = round((size_score + aesthetic_score + complexity_score) / 3, 1)

    return {
        "size": int(size_score),
        "aesthetic": int(aesthetic_score),
        "complexity": int(complexity_score),
        "global": float(global_score)
    }


@app.get("/")
def accueil():
    return {"message": "Minecraft House Classifier API 🏠"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not (file.filename.endswith('.schem') or file.filename.endswith('.schematic')):
        return {"error": "Fichier invalide"}

    with tempfile.NamedTemporaryFile(delete=False, suffix='.schem') as tmp:
        contenu = await file.read()
        tmp.write(contenu)
        chemin_tmp = tmp.name

    try:
        grille_brute, palette = lire_schem(chemin_tmp)

        # Grille simplifiée + croppée (taille réelle, pas normalisée)
        # C'est cette grille qu'on envoie au viewer pour un affichage lisible
        grille_simplifiee = convertir_grille(grille_brute, palette)
        grille_croppee = crop_air(grille_simplifiee)

        # On limite à 64x64x64 max pour le viewer (évite les trop grosses structures)
        MAX = 64
        h = min(grille_croppee.shape[0], MAX)
        l = min(grille_croppee.shape[1], MAX)
        w = min(grille_croppee.shape[2], MAX)
        grille_viewer = grille_croppee[:h, :l, :w]

        # On stocke dans le cache pour le viewer
        grilles_cache[file.filename] = grille_viewer.tolist()

        # Pour le modèle IA on utilise le pipeline complet (normalisation 32x32x32)
        grille_propre = pretraiter(grille_brute, palette)
        features = extraire_features(grille_propre)

        features_2d = features.reshape(1, -1)
        prediction = modele.predict(features_2d)[0]
        probabilites = modele.predict_proba(features_2d)[0]
        confidence = float(probabilites[prediction])
        is_house = bool(prediction == 1)

        if is_house:
            scores_auto = calculer_scores_auto(features)
            scores_humains = get_scores(file.filename)
            return {
                "is_house": True,
                "confidence": round(confidence, 2),
                "filename": file.filename,
                "scores_auto": scores_auto,
                "scores_humains": scores_humains
            }

        return {
            "is_house": False,
            "confidence": round(confidence, 2)
        }

    finally:
        os.unlink(chemin_tmp)


@app.post("/vote")
def voter(vote: Vote):
    if not all(1 <= v <= 5 for v in [vote.size, vote.aesthetic, vote.complexity]):
        return {"error": "Les notes doivent être entre 1 et 5"}

    ajouter_vote(vote.filename, vote.size, vote.aesthetic, vote.complexity)
    scores = get_scores(vote.filename)
    return {
        "message": "Vote enregistré !",
        "scores": scores
    }


@app.get("/scores/{filename}")
def get_scores_fichier(filename: str):
    scores = get_scores(filename)
    if scores:
        return scores
    return {"message": "Pas encore de votes pour ce fichier"}


@app.get("/gallery")
def get_gallery():
    return get_all_votes()


@app.get("/preview/{filename}")
def get_preview(filename: str):
    if filename not in grilles_cache:
        return {"error": "Grille non disponible. Réanalyse le fichier d'abord."}
    return {
        "filename": filename,
        "grid": grilles_cache[filename]
    }