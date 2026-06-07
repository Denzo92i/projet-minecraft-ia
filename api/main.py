from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pickle
import numpy as np
import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parsing'))
from parser import lire_schem
from preprocessor import pretraiter
from features import extraire_features

app = FastAPI(title="Minecraft House Classifier")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

modele_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'classifier.pkl')
with open(modele_path, "rb") as f:
    modele = pickle.load(f)

def calculer_scores(features):
    # features = tableau de 15 valeurs qu'on a calculé dans features.py
    # On récupère chaque feature par son index

    densite        = features[0]   # % de blocs non-air
    prop_bois      = features[1]   # % de bois
    prop_pierre    = features[2]   # % de pierre
    prop_verre     = features[3]   # % de verre
    prop_deco      = features[4]   # % de décoration
    prop_toit      = features[5]   # % de toit
    hauteur        = features[8]   # hauteur réelle
    largeur        = features[9]   # largeur réelle
    profondeur     = features[10]  # profondeur réelle
    a_un_toit      = features[12]  # 0 ou 1
    air_interieur  = features[13]  # 0 ou 1
    diversite      = features[14]  # nombre de familles différentes

    # -----------------------------------------------
    # SCORE TAILLE (1 à 5)
    # Basé sur le volume réel de la structure
    # -----------------------------------------------
    volume = hauteur * largeur * profondeur
    if volume < 500:
        size_score = 1      # très petite cabane
    elif volume < 2000:
        size_score = 2      # petite maison
    elif volume < 5000:
        size_score = 3      # maison moyenne
    elif volume < 15000:
        size_score = 4      # grande maison
    else:
        size_score = 5      # manoir / villa énorme

    # -----------------------------------------------
    # SCORE ESTHÉTIQUE (1 à 5)
    # Basé sur la diversité des matériaux + verre + déco
    # -----------------------------------------------
    score_esth = 1
    if diversite >= 2:
        score_esth += 1     # au moins 2 familles de blocs
    if prop_verre > 0.01:
        score_esth += 1     # a des fenêtres en verre
    if prop_deco > 0.005:
        score_esth += 1     # a des décorations
    if diversite >= 5:
        score_esth += 1     # palette très variée
    aesthetic_score = min(score_esth, 5)
    # min(x, 5) = on s'assure de ne jamais dépasser 5

    # -----------------------------------------------
    # SCORE COMPLEXITÉ (1 à 5)
    # Basé sur le toit, l'intérieur, la densité, les matériaux
    # -----------------------------------------------
    score_comp = 1
    if a_un_toit:
        score_comp += 1     # a un toit détecté
    if air_interieur:
        score_comp += 1     # a un espace intérieur
    if prop_toit > 0.02:
        score_comp += 1     # toit bien travaillé
    if densite > 0.15:
        score_comp += 1     # structure dense = complexe
    complexity_score = min(score_comp, 5)

    # Score global = moyenne des 3 scores
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
        return {"error": "Fichier invalide, envoyez un .schem ou .schematic"}

    with tempfile.NamedTemporaryFile(delete=False, suffix='.schem') as tmp:
        contenu = await file.read()
        tmp.write(contenu)
        chemin_tmp = tmp.name

    try:
        grille_brute, palette = lire_schem(chemin_tmp)
        grille_propre = pretraiter(grille_brute, palette)
        features = extraire_features(grille_propre)

        features_2d = features.reshape(1, -1)
        prediction = modele.predict(features_2d)[0]
        probabilites = modele.predict_proba(features_2d)[0]
        confidence = float(probabilites[prediction])
        is_house = bool(prediction == 1)

        # Si c'est une maison on calcule les scores
        if is_house:
            scores = calculer_scores(features)
            return {
                "is_house": True,
                "confidence": round(confidence, 2),
                "scores": scores
            }
        else:
            return {
                "is_house": False,
                "confidence": round(confidence, 2)
            }

    finally:
        os.unlink(chemin_tmp)