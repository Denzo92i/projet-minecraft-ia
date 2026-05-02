import nbtlib
# Librairie qui sait lire le format binaire NBT de Minecraft

import numpy as np
# NumPy = librairie pour manipuler des tableaux de nombres
# "as np" = raccourci pour écrire np.array() au lieu de numpy.array()

def lire_schem(chemin_fichier):
# Fonction réutilisable qui prend en paramètre le chemin vers le fichier .schem

    nbt = nbtlib.load(chemin_fichier)
    # On ouvre et décode le fichier .schem
    # nbt contient maintenant toutes les données brutes du fichier

    data = nbt["Schematic"]
    # On accède à la clé "Schematic" qui contient toutes les données
    # C'est comme ouvrir une boîte qui en contient une autre

    # DIMENSIONS
    largeur = int(data["Width"])
    hauteur = int(data["Height"])
    longueur = int(data["Length"])
    # On lit les 3 dimensions depuis le fichier
    # int() = conversion en nombre entier car nbtlib renvoie ses propres types

    print(f"Dimensions : {largeur} x {hauteur} x {longueur}")

    blocks = data["Blocks"]
    # La palette et les blocs sont rangés dans une sous-clé "Blocks"
    # Structure : Schematic → Blocks → Palette / Data / BlockEntities

    # PALETTE DE BLOCS
    palette = {}
    # Dictionnaire vide : numéro → nom du bloc
    # ex: {0: "minecraft:air", 1: "minecraft:oak_planks", ...}

    for nom_bloc, index in blocks["Palette"].items():
        palette[int(index)] = nom_bloc
    # On parcourt la palette du fichier
    # Pour chaque entrée on stocke : son numéro → son nom

    print(f"Nombre de types de blocs différents : {len(palette)}")

    # GRILLE DE BLOCS
    blocs_bruts = np.array(blocks["Data"], dtype=np.int32)
    # On récupère la liste de tous les blocs depuis la clé "Data"
    # C'est un tableau 1D pour l'instant
    # dtype=np.int32 = chaque valeur est un entier 32 bits

    taille_attendue = hauteur * longueur * largeur
    # On calcule la taille exacte du cube 3D
    # ex: 20 x 22 x 19 = 8360 cases

    blocs_bruts = blocs_bruts[:taille_attendue]
    # --- NOUVEAU ---
    # On tronque le tableau à la taille exacte attendue
    # Le format Sponge ajoute parfois des octets en trop à la fin
    # [:taille_attendue] = on garde seulement les N premières valeurs
    # ex: 8588 valeurs → on garde seulement les 8360 premières

    grille_3d = blocs_bruts.reshape((hauteur, longueur, largeur))
    # reshape = on transforme la liste 1D en cube 3D
    # ex: 8360 valeurs → cube de 20 x 22 x 19

    print(f"Forme de la grille 3D : {grille_3d.shape}")
    # .shape = affiche les dimensions du tableau NumPy

    # TOP 5 DES BLOCS LES PLUS PRESENTS
    index_uniques, comptes = np.unique(blocs_bruts, return_counts=True)
    # np.unique = trouve toutes les valeurs uniques dans le tableau
    # return_counts=True = compte combien de fois chaque valeur apparaît

    print("\nTop 5 blocs les plus présents :")

    top5 = sorted(zip(comptes, index_uniques), reverse=True)[:5]
    # zip() = associe chaque compte avec son index de bloc
    # sorted(..., reverse=True) = trie du plus grand au plus petit
    # [:5] = on garde seulement les 5 premiers

    for compte, idx in top5:
        print(f"  {palette.get(idx, '?')} : {compte} blocs")
    # Pour chaque bloc du top 5 on affiche son nom et son nombre
    # palette.get(idx, '?') = cherche le nom, affiche '?' si pas trouvé

    return grille_3d, palette
    # La fonction retourne la grille 3D et la palette pour les réutiliser

# LANCEMENT DU TEST
if __name__ == "__main__":
    # Ce bloc ne s'exécute QUE si on lance parser.py directement
    # Il ne s'exécute PAS quand un autre fichier l'importe
    grille, palette = lire_schem("data/maison/29572.schem")