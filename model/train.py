import numpy as np
import pandas as pd
import os
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle

# On ajoute le dossier parsing au path pour pouvoir importer nos fichiers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'parsing'))
from parser import lire_schem
from preprocessor import pretraiter
from features import extraire_features

def construire_dataset():
    # Cette fonction parcourt tous les schématics
    # et retourne un tableau de features + labels

    X = []  # liste des features de chaque schématic
    y = []  # liste des labels (1=maison, 0=non-maison)
    erreurs = []  # fichiers qui ont planté

    dossiers = [
        ("data/maison", 1),   # label 1 = maison
        ("data/autre", 0)     # label 0 = non-maison
    ]

    for dossier, label in dossiers:
        print(f"\nTraitement du dossier : {dossier}")
        fichiers = os.listdir(dossier)

        for fichier in fichiers:
            if not (fichier.endswith('.schem') or fichier.endswith('.schematic')):
                continue
            # On ignore les fichiers qui ne sont pas des schématics

            chemin = os.path.join(dossier, fichier)
            # os.path.join = construit le chemin complet
            # ex: "data/maison" + "29572.schem" = "data/maison/29572.schem"

            try:
                # On essaie de traiter le fichier
                grille_brute, palette = lire_schem(chemin)
                grille_propre = pretraiter(grille_brute, palette)
                features = extraire_features(grille_propre)

                X.append(features)
                y.append(label)
                print(f"  ✅ {fichier}")

            except Exception as e:
                # Si le fichier plante on l'ignore et on continue
                erreurs.append(fichier)
                print(f"  ❌ {fichier} → {e}")

    print(f"\nDataset construit : {len(X)} schématics")
    print(f"Erreurs : {len(erreurs)} fichiers ignorés")

    return np.array(X), np.array(y)

def entrainer_modele(X, y):
    # Cette fonction entraîne le Random Forest

    # On divise le dataset en 80% entraînement et 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # test_size=0.2 = 20% des données pour tester
    # random_state=42 = graine aléatoire pour avoir des résultats reproductibles

    print(f"\nEntraînement sur {len(X_train)} schématics")
    print(f"Test sur {len(X_test)} schématics")

    # On crée et entraîne le Random Forest
    modele = RandomForestClassifier(
        n_estimators=100,   # 100 arbres de décision
        random_state=42
    )
    modele.fit(X_train, y_train)
    # .fit() = entraîne le modèle sur les données d'entraînement

    # On évalue le modèle sur les données de test
    y_pred = modele.predict(X_test)
    # .predict() = le modèle prédit les labels des données de test

    accuracy = accuracy_score(y_test, y_pred)
    # accuracy = % de bonnes prédictions

    print(f"\n--- RÉSULTATS ---")
    print(f"Accuracy : {accuracy:.2%}")
    print(f"\nRapport détaillé :")
    print(classification_report(y_test, y_pred, target_names=["non-maison", "maison"]))
    print(f"Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred))

    return modele

def sauvegarder_modele(modele, chemin="model/classifier.pkl"):
    # On sauvegarde le modèle entraîné dans un fichier .pkl
    # pkl = pickle = format Python pour sauvegarder des objets
    with open(chemin, 'wb') as f:
        pickle.dump(modele, f)
    print(f"\nModèle sauvegardé dans {chemin}")

if __name__ == "__main__":
    print("=== CONSTRUCTION DU DATASET ===")
    X, y = construire_dataset()

    print("\n=== ENTRAÎNEMENT DU MODÈLE ===")
    modele = entrainer_modele(X, y)

    print("\n=== SAUVEGARDE DU MODÈLE ===")
    sauvegarder_modele(modele)