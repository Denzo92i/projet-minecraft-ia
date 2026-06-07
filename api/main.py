from fastapi import FastAPI, UploadFile, File
# FastAPI = le framework qui crée l'API
# UploadFile = type qui représente un fichier uploadé par l'utilisateur
# File = outil pour dire à FastAPI qu'on attend un fichier en entrée

from fastapi.middleware.cors import CORSMiddleware
# CORS = Cross Origin Resource Sharing
# C'est une sécurité des navigateurs qui bloque les requêtes
# venant d'un autre domaine
# Ce middleware désactive cette restriction pour notre frontend

import pickle
# Librairie pour charger le modèle sauvegardé (.pkl)

import numpy as np
# NumPy pour manipuler les tableaux de nombres

import sys
import os
# sys et os = librairies Python standard pour gérer
# les chemins de fichiers et le système

import tempfile
# Librairie pour créer des fichiers temporaires
# On en a besoin car le fichier uploadé doit être
# sauvegardé sur le disque avant d'être lu par nbtlib

# On ajoute le dossier parsing au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parsing'))
# Sans ça Python ne saurait pas où trouver parser.py, preprocessor.py etc
# os.path.dirname(__file__) = dossier du fichier actuel (api/)
# '..' = on remonte d'un niveau (projet-nationsglory/)
# 'parsing' = on entre dans le dossier parsing

from parser import lire_schem
from preprocessor import pretraiter
from features import extraire_features
# On importe nos fonctions depuis les fichiers qu'on a créés

# CRÉATION DE L'APPLICATION
app = FastAPI(title="Minecraft House Classifier")
# On crée l'application FastAPI
# title = le nom affiché sur la page /docs

# CONFIGURATION CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Accepte les requêtes de n'importe quel domaine
    allow_methods=["*"],    # Accepte GET, POST, PUT, DELETE...
    allow_headers=["*"],    # Accepte tous les headers HTTP
)
# Sans ça le navigateur bloquerait les requêtes du frontend vers l'API

# CHARGEMENT DU MODÈLE
modele_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'classifier.pkl')
# On construit le chemin vers le fichier classifier.pkl
# ex: C:/Users/dylan/.../model/classifier.pkl

with open(modele_path, "rb") as f:
    modele = pickle.load(f)
# "rb" = read binary = on lit en mode binaire
# pickle.load() = on charge le modèle depuis le fichier
# On fait ça UNE SEULE FOIS au démarrage pour ne pas
# recharger le modèle à chaque requête (ce serait lent)

# ENDPOINT ACCUEIL
@app.get("/")
def accueil():
    # @app.get("/") = cette fonction répond aux requêtes GET sur "/"
    # C'est juste pour vérifier que l'API tourne
    return {"message": "Minecraft House Classifier API 🏠"}
    # On retourne un dictionnaire Python → FastAPI le convertit en JSON

# ENDPOINT PRINCIPAL
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # @app.post("/predict") = cette fonction répond aux requêtes POST sur "/predict"
    # C'est ici que tout se passe !
    # async = la fonction peut gérer plusieurs requêtes en même temps
    # file: UploadFile = FastAPI s'attend à recevoir un fichier
    # File(...) = le fichier est obligatoire (... = requis)

    # VÉRIFICATION DU FORMAT
    if not (file.filename.endswith('.schem') or file.filename.endswith('.schematic')):
        return {"error": "Fichier invalide, envoyez un .schem ou .schematic"}
    # On vérifie que l'utilisateur a bien envoyé un fichier schematic
    # Si c'est un .pdf ou .jpg par exemple → on retourne une erreur

    # SAUVEGARDE TEMPORAIRE
    with tempfile.NamedTemporaryFile(delete=False, suffix='.schem') as tmp:
        contenu = await file.read()
        # await = on attend que le fichier soit entièrement reçu
        # file.read() = on lit le contenu binaire du fichier
        tmp.write(contenu)
        # On écrit le contenu dans un fichier temporaire sur le disque
        chemin_tmp = tmp.name
        # On récupère le chemin du fichier temporaire
        # ex: C:/Users/dylan/AppData/Local/Temp/tmpXXXXXX.schem

    try:
        # PIPELINE COMPLET
        grille_brute, palette = lire_schem(chemin_tmp)
        # Étape 1 : on lit le fichier .schem → grille 3D brute

        grille_propre = pretraiter(grille_brute, palette)
        # Étape 2 : on nettoie et normalise → cube 32x32x32

        features = extraire_features(grille_propre)
        # Étape 3 : on extrait les 15 features

        features_2d = features.reshape(1, -1)
        # reshape(1, -1) = on transforme le tableau 1D en 2D
        # Le modèle attend toujours un tableau 2D
        # ex: [0.06, 0.02, ...] → [[0.06, 0.02, ...]]

        prediction = modele.predict(features_2d)[0]
        # .predict() = le modèle prédit la classe
        # Retourne [0] ou [1] → on prend le premier élément [0]
        # 0 = pas une maison, 1 = maison

        probabilites = modele.predict_proba(features_2d)[0]
        # .predict_proba() = retourne les probabilités pour chaque classe
        # ex: [0.13, 0.87] → 13% non-maison, 87% maison

        confidence = float(probabilites[prediction])
        # On récupère la probabilité de la classe prédite
        # ex: si prediction=1 → on prend probabilites[1] = 0.87
        # float() = conversion en nombre Python standard

        return {
            "is_house": bool(prediction == 1),
            # True si maison, False si non-maison
            # bool() = conversion en booléen Python (True/False)
            "confidence": round(confidence, 2)
            # round(x, 2) = arrondi à 2 décimales
            # ex: 0.8734 → 0.87
        }

    finally:
        os.unlink(chemin_tmp)
        # finally = ce bloc s'exécute TOUJOURS même si il y a une erreur
        # os.unlink = supprime le fichier temporaire
        # Important pour ne pas remplir le disque de fichiers inutiles