import numpy as np
# NumPy = librairie pour manipuler des tableaux de nombres

def extraire_features(grille_3d):
    # Fonction qui prend le cube 32x32x32 en entrée
    # et retourne une liste de 15 chiffres qui décrivent la structure

    total_blocs = grille_3d.size
    # .size = nombre total de cases dans le cube
    # 32 x 32 x 32 = 32 768 cases au total

    non_air = np.sum(grille_3d != 0)
    # np.sum compte combien de cases sont différentes de 0
    # 0 = air, donc on compte tous les blocs réels
    # ex: 2800 blocs réels sur 32768 cases

    # -----------------------------------------------
    # FEATURE 1 : DENSITÉ GLOBALE
    # -----------------------------------------------
    densite = non_air / total_blocs
    # % de blocs réels dans le cube
    # ex: 2800 / 32768 = 0.085 → 8.5% de la structure est remplie
    # Une maison dense aura une valeur élevée
    # Un arbre creux aura une valeur faible

    # -----------------------------------------------
    # FEATURES 2 à 8 : PROPORTIONS PAR FAMILLE
    # -----------------------------------------------
    prop_bois       = np.sum(grille_3d == 1) / total_blocs
    # % de blocs de type bois (famille 1)
    # Une maison a généralement beaucoup de bois

    prop_pierre     = np.sum(grille_3d == 2) / total_blocs
    # % de blocs de type pierre
    # Une maison médiévale aura beaucoup de pierre

    prop_verre      = np.sum(grille_3d == 3) / total_blocs
    # % de blocs de type verre
    # Une maison a souvent des fenêtres en verre
    # Un arbre n'en a jamais → feature très discriminante !

    prop_decoration = np.sum(grille_3d == 4) / total_blocs
    # % de blocs de décoration (tapis, torches, tableaux...)
    # Une maison habitée a souvent des décorations

    prop_toit       = np.sum(grille_3d == 5) / total_blocs
    # % de blocs de toit (escaliers, dalles...)
    # Une maison a toujours un toit

    prop_vegetation = np.sum(grille_3d == 6) / total_blocs
    # % de blocs de végétation (feuilles, herbe...)
    # Un arbre aura une valeur très élevée ici
    # Une maison aura une valeur très faible → très discriminant !

    prop_redstone   = np.sum(grille_3d == 7) / total_blocs
    # % de blocs redstone (pistons, répéteurs...)
    # Une machine redstone aura une valeur élevée
    # Une maison normale aura une valeur très faible

    # -----------------------------------------------
    # FEATURE 3 : DIMENSIONS RÉELLES
    # -----------------------------------------------
    non_air_coords = np.argwhere(grille_3d != 0)
    # np.argwhere = trouve les coordonnées (y, z, x) de tous les blocs non-air
    # ex: [[0,5,3], [0,5,4], [1,5,3]...] = liste de positions

    if len(non_air_coords) == 0:
        # Si la structure est complètement vide
        hauteur_reelle = largeur_reelle = profondeur_reelle = 0
    else:
        mins = non_air_coords.min(axis=0)
        # .min(axis=0) = valeur minimale sur chaque axe
        # ex: [2, 1, 3] = le bloc le plus bas est à y=2, z=1, x=3

        maxs = non_air_coords.max(axis=0)
        # .max(axis=0) = valeur maximale sur chaque axe
        # ex: [18, 20, 16] = le bloc le plus haut est à y=18

        hauteur_reelle    = maxs[0] - mins[0] + 1
        largeur_reelle    = maxs[1] - mins[1] + 1
        profondeur_reelle = maxs[2] - mins[2] + 1
        # On calcule la taille réelle : max - min + 1
        # ex: hauteur = 18 - 2 + 1 = 17 blocs de haut

    # -----------------------------------------------
    # FEATURE 4 : RATIO HAUTEUR/LARGEUR
    # -----------------------------------------------
    ratio_h_l = hauteur_reelle / (largeur_reelle + 1)
    # Une maison est généralement plus large que haute → ratio < 1
    # Une tour est plus haute que large → ratio > 1
    # +1 pour éviter la division par zéro si largeur = 0

    # -----------------------------------------------
    # FEATURE 5 : PRÉSENCE D'UN TOIT
    # -----------------------------------------------
    moitie_haute = grille_3d[:grille_3d.shape[0]//2, :, :]
    # On prend seulement la moitié supérieure du cube
    # [:shape//2] = de la case 0 jusqu'à la moitié
    # ex: sur un cube de 32 de haut → on prend les 16 premières couches

    a_un_toit = int(np.sum(moitie_haute == 5) > 10)
    # On compte les blocs de toit (famille 5) dans la moitié haute
    # Si plus de 10 → on considère qu'il y a un toit → valeur = 1
    # Sinon → pas de toit → valeur = 0

    # -----------------------------------------------
    # FEATURE 6 : PRÉSENCE D'UN ESPACE INTÉRIEUR
    # -----------------------------------------------
    air_interieur = 0
    # Par défaut on considère qu'il n'y a pas d'intérieur

    centre_h = grille_3d.shape[0] // 2
    centre_l = grille_3d.shape[1] // 2
    centre_w = grille_3d.shape[2] // 2
    # On calcule le centre du cube sur chaque axe
    # // = division entière ex: 32 // 2 = 16

    tranche = grille_3d[centre_h, :, :]
    # On prend une tranche horizontale au milieu du cube
    # C'est comme couper la structure en deux et regarder la coupe

    if np.sum(tranche == 0) > 5 and np.sum(tranche != 0) > 5:
        air_interieur = 1
    # Si la tranche contient à la fois de l'air ET des blocs
    # → probablement un espace intérieur creux = une pièce
    # Une maison a toujours un intérieur creux
    # Un arbre ou une statue pleine n'en a pas

    # -----------------------------------------------
    # FEATURE 7 : DIVERSITÉ DES MATÉRIAUX
    # -----------------------------------------------
    types_presents = len(np.unique(grille_3d)) - 1
    # np.unique = trouve toutes les valeurs uniques dans le cube
    # len() = compte combien il y en a
    # -1 pour ne pas compter l'air (famille 0)
    # Une maison utilise plusieurs matériaux → valeur élevée
    # Un arbre utilise surtout bois + feuilles → valeur faible

    # -----------------------------------------------
    # ON REGROUPE TOUT DANS UN TABLEAU
    # -----------------------------------------------
    features = np.array([
        densite,            # 1.  % de blocs réels
        prop_bois,          # 2.  % de bois
        prop_pierre,        # 3.  % de pierre
        prop_verre,         # 4.  % de verre
        prop_decoration,    # 5.  % de décoration
        prop_toit,          # 6.  % de toit
        prop_vegetation,    # 7.  % de végétation
        prop_redstone,      # 8.  % de redstone
        hauteur_reelle,     # 9.  hauteur en blocs
        largeur_reelle,     # 10. largeur en blocs
        profondeur_reelle,  # 11. profondeur en blocs
        ratio_h_l,          # 12. ratio hauteur/largeur
        a_un_toit,          # 13. présence toit (0 ou 1)
        air_interieur,      # 14. présence intérieur (0 ou 1)
        types_presents      # 15. nombre de familles différentes
    ])
    # np.array() = on transforme la liste en tableau NumPy
    # C'est ce tableau de 15 chiffres que le Random Forest va analyser

    return features
    # On retourne le tableau de 15 features

# -----------------------------------------------
# TEST
# -----------------------------------------------
if __name__ == "__main__":
    # Ce bloc ne s'exécute que si on lance ce fichier directement
    from parser import lire_schem
    from preprocessor import pretraiter

    grille_brute, palette = lire_schem("data/maison/29572.schem")
    # On lit le fichier .schem

    grille_propre = pretraiter(grille_brute, palette)
    # On nettoie et normalise la grille

    features = extraire_features(grille_propre)
    # On extrait les 15 features

    noms = [
        "densité", "prop_bois", "prop_pierre", "prop_verre",
        "prop_decoration", "prop_toit", "prop_vegetation", "prop_redstone",
        "hauteur", "largeur", "profondeur", "ratio_h/l",
        "a_un_toit", "air_interieur", "diversite_materiaux"
    ]
    # Liste des noms pour afficher joliment les résultats

    print("\nFeatures extraites :")
    for nom, valeur in zip(noms, features):
        print(f"  {nom} : {valeur:.3f}")
    # zip() associe chaque nom avec sa valeur
    # :.3f = affiche 3 chiffres après la virgule