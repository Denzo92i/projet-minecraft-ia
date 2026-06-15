Minecraft Schematic AI Classifier
Système d'intelligence artificielle capable d'analyser automatiquement des structures Minecraft exportées au format .schem ou .schematic pour les classifier et évaluer leur qualité architecturale.

🚀 À propos du projet
Ce projet implémente un pipeline complet de Machine Learning appliqué au gaming. Il transforme des données binaires NBT (Minecraft) en tenseurs numériques, permet la classification binaire (Maison vs Non-Maison) et génère des scores esthétiques basés sur la densité des matériaux.

⚙️ Prérequis techniques
Pour faire tourner le projet, vous avez besoin de :

Docker & Docker Compose (installés et démarrés).

Un navigateur web moderne.

🛠️ Installation et Démarrage
Le projet est entièrement conteneurisé. Pour le lancer, rien de plus simple :

Cloner le dépôt :

Bash
git clone https://github.com/Denzo92i/projet-minecraft-ia.git
cd projet-minecraft-ia
Lancer l'environnement :

Bash
docker-compose up --build
Accéder à l'application :

API : http://localhost:8000

Frontend : Ouvrez frontend/index.html dans votre navigateur.

Viewer 3D : Ouvrez frontend/viewer.html pour visualiser les structures.

🧠 Pipeline de données & IA
Le projet suit une logique de traitement séquentiel pour garantir la précision :

Parsing NBT : Lecture du format Sponge/Minecraft via nbtlib.

Prétraitement : Nettoyage des voxels d'air et normalisation de la grille 3D.

Extraction de features : Calcul de la densité, volume englobant et ratio de matériaux.

Classification : Utilisation d'un modèle Random Forest (scikit-learn) pour la prédiction binaire.

Scoring : Algorithme de normalisation par amplification de densité (x15) pour générer un score de 1 à 5.

📂 Structure du dépôt
(Garde ici ton arborescence que tu as déjà, elle est très claire)

👥 Équipe & Remerciements
Projet développé par Dylan, Lola et Nicolas dans le cadre du cursus NationsGlory.

Note obtenue : 17/20

Quelques conseils pour finaliser ton repo :
Ajoute une capture d'écran : Dans ton README.md, ajoute une ligne comme celle-ci sous la section "À propos" :
![Interface du projet](image_902451.png) (Vérifie que le nom du fichier est bien présent dans ton repo). Voir le résultat visuel immédiatement augmente énormément la qualité perçue du projet.

Fichier .gitignore : Vérifie que ton dossier __pycache__ ou les fichiers temporaires ne sont pas poussés sur GitHub. Si ce n'est pas fait, crée un fichier nommé .gitignore à la racine contenant :

Plaintext
__pycache__/
*.pyc
.ipynb_checkpoints/
*.pkl
.env
Le fichier dataset.csv : Si ton jeu de données n'est pas confidentiel, assure-toi qu'il est bien présent dans le repo pour qu'on puisse voir la structure de tes données d'entraînement.
