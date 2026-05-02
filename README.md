# Minecraft Schematic AI Classifier

> Système d'intelligence artificielle capable d'analyser automatiquement 
> des structures Minecraft exportées au format schématic et de déterminer 
> si elles représentent une maison ou non.


## Description

Ce projet se situe à la croisée de l'intelligence artificielle et du jeu vidéo.
Il implémente un pipeline complet de classification binaire de structures 3D 
Minecraft, depuis la lecture des fichiers `.schem` / `.schematic` jusqu'au 
déploiement d'une API REST accessible via une interface web.

Les fichiers schématics Minecraft encodent des structures 3D bloc par bloc 
au format binaire NBT. Ce projet transforme ces fichiers en tenseurs numériques 
exploitables par des modèles de machine learning afin de répondre à la 
problématique suivante :

**Comment déterminer automatiquement si une structure Minecraft est une maison ?**

## Architecture du projet

minecraft-schematic-ai-classifier/
│
├── data/
│   ├── maison/          # Schématics labellisés comme maisons
│   └── autre/           # Schématics labellisés comme non-maisons
│
├── parsing/
│   ├── parser.py        # Lecture et décodage des fichiers NBT
│   ├── preprocessor.py  # Nettoyage, simplification et normalisation
│   └── features.py      # Extraction de features géométriques
│
├── model/
│   ├── train.py         # Entraînement du modèle Random Forest
│   ├── evaluate.py      # Calcul des métriques
│   └── classifier.pkl   # Modèle entraîné sauvegardé
│
├── api/
│   └── main.py          # API REST FastAPI — endpoint /predict
│
├── frontend/
│   └── index.html       # Interface web upload + résultat
│
├── notebooks/
│   └── exploration.ipynb
│
├── dataset.csv          
├── requirements.txt     
└── README.md
