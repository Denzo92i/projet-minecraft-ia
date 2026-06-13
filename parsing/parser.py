import nbtlib
import numpy as np

def lire_schem(chemin_fichier):
    # On ouvre et décode le fichier NBT
    nbt = nbtlib.load(chemin_fichier)

    # -------------------------------------------------------
    # FORMAT SPONGE v3 — clé "Schematic" à la racine
    # Exemple : fichiers exportés par WorldEdit moderne
    # -------------------------------------------------------
    if "Schematic" in nbt:
        data = nbt["Schematic"]
        largeur = int(data["Width"])
        hauteur = int(data["Height"])
        longueur = int(data["Length"])

        blocks = data["Blocks"]
        palette = {}
        for nom_bloc, index in blocks["Palette"].items():
            palette[int(index)] = nom_bloc

        blocs_bruts = np.array(blocks["Data"], dtype=np.int32)
        taille_attendue = hauteur * longueur * largeur
        blocs_bruts = blocs_bruts[:taille_attendue]

    # -------------------------------------------------------
    # FORMAT SPONGE v2 — palette et blocs à la racine
    # Exemple : maisondonjon.schem, housev1.schem...
    # -------------------------------------------------------
    elif "Palette" in nbt and "BlockData" in nbt:
        largeur = int(nbt["Width"])
        hauteur = int(nbt["Height"])
        longueur = int(nbt["Length"])

        palette = {}
        for nom_bloc, index in nbt["Palette"].items():
            palette[int(index)] = nom_bloc

        # BlockData est encodé en varint — on le décode
        raw = list(nbt["BlockData"])
        blocs_bruts = decoder_varint(raw, hauteur * longueur * largeur)

    # -------------------------------------------------------
    # FORMAT LEGACY .schematic (WorldEdit/MCEdit)
    # Exemple : MaisonDeBeauf5.schematic, Grande Maison Nain.schematic
    # -------------------------------------------------------
    elif "Width" in nbt and "Blocks" in nbt:
        largeur = int(nbt["Width"])
        hauteur = int(nbt["Height"])
        longueur = int(nbt["Length"])

        blocs_bruts = np.array(nbt["Blocks"], dtype=np.uint8)
        taille_attendue = hauteur * longueur * largeur
        blocs_bruts = blocs_bruts[:taille_attendue]

        # Pas de palette dans l'ancien format — on crée une palette avec les IDs numériques
        palette = {int(i): f"bloc_{i}" for i in np.unique(blocs_bruts)}

    # -------------------------------------------------------
    # FORMAT LITEMATICA — clé "Regions" à la racine
    # -------------------------------------------------------
    elif "Regions" in nbt:
        regions = nbt["Regions"]
        region = list(regions.values())[0]

        largeur = abs(int(region["Size"]["x"]))
        hauteur = abs(int(region["Size"]["y"]))
        longueur = abs(int(region["Size"]["z"]))

        palette = {}
        for i, etat in enumerate(region["BlockStatePalette"]):
            palette[i] = etat["Name"]

        # Les blocs sont encodés en bits dans un tableau de longs
        bits_par_bloc = max(4, int(np.ceil(np.log2(max(len(palette), 2)))))
        longs = list(region["BlockStates"])
        blocs_bruts = decoder_longs(longs, bits_par_bloc, hauteur * longueur * largeur)

    else:
        raise ValueError(f"Format non reconnu dans {chemin_fichier}. Clés disponibles : {list(nbt.keys())}")

    grille_3d = np.array(blocs_bruts, dtype=np.int32).reshape((hauteur, longueur, largeur))

    return grille_3d, palette


def decoder_varint(raw, nb_blocs):
    """
    Décode un tableau de bytes encodés en varint (format Sponge v2).
    Chaque valeur peut occuper 1 à 5 bytes selon sa taille.
    """
    blocs = []
    i = 0
    while len(blocs) < nb_blocs and i < len(raw):
        valeur = 0
        bits = 0
        while True:
            octet = raw[i] & 0xFF
            i += 1
            valeur |= (octet & 0x7F) << bits
            bits += 7
            if not (octet & 0x80):
                break
        blocs.append(valeur)
    # Si on n'a pas assez de blocs, on complète avec des zéros (air)
    while len(blocs) < nb_blocs:
        blocs.append(0)
    return blocs[:nb_blocs]


def decoder_longs(longs, bits_par_bloc, nb_blocs):
    """
    Décode un tableau de longs Java en indices de blocs (format Litematica).
    Chaque long contient plusieurs indices de blocs compactés.
    """
    masque = (1 << bits_par_bloc) - 1
    blocs = []
    for long_val in longs:
        # Conversion en entier non signé 64 bits
        if long_val < 0:
            long_val += (1 << 64)
        for _ in range(64 // bits_par_bloc):
            blocs.append(int(long_val & masque))
            long_val >>= bits_par_bloc
            if len(blocs) >= nb_blocs:
                break
        if len(blocs) >= nb_blocs:
            break
    return blocs[:nb_blocs]


if __name__ == "__main__":
    grille, palette = lire_schem("data/maison/29572.schem")
    print(f"Dimensions : {grille.shape}")
    print(f"Types de blocs : {len(palette)}")