import numpy as np

# FAMILLES DE BLOCS
# On regroupe les centaines de types de blocs en 8 familles simples
# Cela réduit la complexité pour le modèle IA
FAMILLES = {
    0: "air",
    1: "bois",
    2: "pierre",
    3: "verre",
    4: "decoration",
    5: "toit",
    6: "vegetation",
    7: "redstone"
}

def simplifier_bloc(nom_bloc):
    # Cette fonction prend le nom complet d'un bloc minecraft
    # et retourne le numéro de sa famille
    # ex: "minecraft:oak_planks" → 1 (bois)

    if "air" in nom_bloc:
        return 0  # famille air

    elif any(mot in nom_bloc for mot in [
        "planks", "log", "wood", "fence", "door", "trapdoor", "barrel", "bookshelf"
    ]):
        return 1  # famille bois
    # any() = vérifie si au moins un des mots est présent dans le nom du bloc

    elif any(mot in nom_bloc for mot in [
        "stone", "cobblestone", "brick", "concrete", "terracotta", "dirt", "sand", "gravel"
    ]):
        return 2  # famille pierre

    elif any(mot in nom_bloc for mot in [
        "glass", "pane"
    ]):
        return 3  # famille verre

    elif any(mot in nom_bloc for mot in [
        "carpet", "wool", "painting", "pot", "lantern", "torch", "banner", "bed"
    ]):
        return 4  # famille decoration

    elif any(mot in nom_bloc for mot in [
        "stairs", "slab", "roof", "tile"
    ]):
        return 5  # famille toit

    elif any(mot in nom_bloc for mot in [
        "leaves", "grass", "vine", "flower", "sapling", "lily", "fern"
    ]):
        return 6  # famille vegetation

    elif any(mot in nom_bloc for mot in [
        "redstone", "piston", "repeater", "comparator", "lever", "button", "rail"
    ]):
        return 7  # famille redstone

    else:
        return 2  # par défaut : on classe en pierre si on ne sait pas

def convertir_grille(grille_3d, palette):
    # Cette fonction prend la grille 3D brute (avec les IDs numériques)
    # et la convertit en grille simplifiée (avec les numéros de familles)

    grille_simplifiee = np.zeros_like(grille_3d, dtype=np.uint8)
    # np.zeros_like = crée un tableau de la même forme rempli de zéros
    # dtype=np.uint8 = entiers entre 0 et 255, suffisant pour nos 8 familles

    for idx_bloc, nom_bloc in palette.items():
        # On parcourt chaque type de bloc de la palette
        famille = simplifier_bloc(nom_bloc)
        # On trouve sa famille
        grille_simplifiee[grille_3d == idx_bloc] = famille
        # On remplace tous les blocs de ce type par le numéro de famille
        # grille_3d == idx_bloc = masque booléen (True là où ce bloc apparaît)

    return grille_simplifiee

def crop_air(grille_3d):
    # Cette fonction supprime l'air inutile autour de la structure
    # ex: un cube 20x22x19 avec beaucoup d'air → on garde juste la structure

    non_air = np.argwhere(grille_3d != 0)
    # np.argwhere = trouve les coordonnées de toutes les cases non nulles
    # (non air car air = 0 dans nos familles)

    if len(non_air) == 0:
        return grille_3d
    # Si la structure est vide on retourne la grille telle quelle

    # On trouve les limites min et max sur chaque axe
    min_coords = non_air.min(axis=0)
    max_coords = non_air.max(axis=0) + 1
    # +1 car le slicing Python est exclusif à droite

    # On découpe la grille pour ne garder que la structure
    grille_croppee = grille_3d[
        min_coords[0]:max_coords[0],  # axe hauteur
        min_coords[1]:max_coords[1],  # axe longueur
        min_coords[2]:max_coords[2]   # axe largeur
    ]

    return grille_croppee

def normaliser(grille_3d, taille_cible=32):
    # Cette fonction redimensionne la grille à une taille fixe
    # taille_cible=32 → toutes les grilles feront 32x32x32
    # C'est nécessaire car le modèle IA attend toujours la même taille en entrée

    grille_normalisee = np.zeros(
        (taille_cible, taille_cible, taille_cible), dtype=np.uint8
    )
    # On crée un cube vide de la taille cible rempli d'air (0)

    # On prend le minimum entre la taille réelle et la taille cible
    # pour ne pas dépasser les bords
    h = min(grille_3d.shape[0], taille_cible)
    l = min(grille_3d.shape[1], taille_cible)
    w = min(grille_3d.shape[2], taille_cible)

    grille_normalisee[:h, :l, :w] = grille_3d[:h, :l, :w]
    # On copie la structure dans le coin du cube normalisé
    # Le reste reste à 0 (air) = padding

    return grille_normalisee

def pretraiter(grille_3d, palette, taille_cible=32):
    # Fonction principale qui enchaîne toutes les étapes
    # C'est elle qu'on appellera depuis les autres fichiers

    print("Étape 1 : simplification des blocs...")
    grille = convertir_grille(grille_3d, palette)

    print("Étape 2 : suppression de l'air inutile...")
    grille = crop_air(grille)
    print(f"  Taille après crop : {grille.shape}")

    print("Étape 3 : normalisation à {taille_cible}x{taille_cible}x{taille_cible}...")
    grille = normaliser(grille, taille_cible)
    print(f"  Taille finale : {grille.shape}")

    return grille

# TEST
if __name__ == "__main__":
    # Ce bloc ne s'exécute que si on lance ce fichier directement
    # Il ne s'exécute PAS si on importe ce fichier depuis un autre
    from parser import lire_schem

    grille_brute, palette = lire_schem("data/maison/29572.schem")
    grille_finale = pretraiter(grille_brute, palette)
    print(f"\nGrille finale prête pour le modèle : {grille_finale.shape}")