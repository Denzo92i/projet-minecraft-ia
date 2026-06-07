import nbtlib
import numpy as np

def lire_schem(chemin_fichier):
    # On ouvre et décode le fichier
    nbt = nbtlib.load(chemin_fichier)

    # FORMAT MODERNE .schem (Sponge)
    if "Schematic" in nbt:
        data = nbt["Schematic"]
        largeur = int(data["Width"])
        hauteur = int(data["Height"])
        longueur = int(data["Length"])

        # Les blocs sont dans data["Blocks"]
        blocks = data["Blocks"]
        palette = {}
        for nom_bloc, index in blocks["Palette"].items():
            palette[int(index)] = nom_bloc

        blocs_bruts = np.array(blocks["Data"], dtype=np.int32)
        taille_attendue = hauteur * longueur * largeur
        blocs_bruts = blocs_bruts[:taille_attendue]

    # FORMAT ANCIEN .schematic (WorldEdit/MCEdit)
    elif "Width" in nbt:
        largeur = int(nbt["Width"])
        hauteur = int(nbt["Height"])
        longueur = int(nbt["Length"])

        blocs_bruts = np.array(nbt["Blocks"], dtype=np.uint8)
        taille_attendue = hauteur * longueur * largeur
        blocs_bruts = blocs_bruts[:taille_attendue]

        # Pas de palette dans l'ancien format
        # On crée une palette avec les IDs numériques
        palette = {int(i): f"bloc_{i}" for i in np.unique(blocs_bruts)}

    else:
        raise ValueError(f"Format non reconnu dans {chemin_fichier}")

    grille_3d = blocs_bruts.reshape((hauteur, longueur, largeur))

    return grille_3d, palette

if __name__ == "__main__":
    grille, palette = lire_schem("data/maison/29572.schem")
    print(f"Dimensions : {grille.shape}")
    print(f"Types de blocs : {len(palette)}")