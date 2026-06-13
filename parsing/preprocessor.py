import numpy as np

# FAMILLES DE BLOCS
# On regroupe les centaines de types de blocs en 8 familles simples
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

# -----------------------------------------------
# MAPPING IDs NUMÉRIQUES LEGACY (format .schematic ancien)
# Minecraft Java Edition 1.12 et inférieur utilisaient des IDs numériques.
# On mappe les IDs les plus courants vers nos 8 familles.
# Source : https://minecraft.wiki/w/Java_Edition_data_values/Pre-flattening
# -----------------------------------------------
LEGACY_ID_MAP = {
    # --- AIR ---
    0: 0,    # Air

    # --- BOIS (famille 1) ---
    5: 1,    # Oak/Spruce/Birch Planks
    17: 1,   # Oak/Spruce/Birch/Jungle Log
    47: 1,   # Bookshelf
    53: 1,   # Oak Stairs
    67: 1,   # Cobblestone Stairs → souvent bois dans les maisons
    96: 1,   # Trapdoor
    64: 1,   # Wooden Door
    85: 1,   # Oak Fence
    107: 1,  # Fence Gate
    126: 1,  # Oak Slab
    125: 1,  # Double Oak Slab
    163: 1,  # Acacia Stairs
    164: 1,  # Dark Oak Stairs
    154: 1,  # Hopper
    58: 1,   # Crafting Table
    61: 1,   # Furnace
    62: 1,   # Burning Furnace
    130: 1,  # Ender Chest (bois)

    # --- PIERRE (famille 2) ---
    1: 2,    # Stone
    2: 2,    # Grass Block
    3: 2,    # Dirt
    4: 2,    # Cobblestone
    7: 2,    # Bedrock
    12: 2,   # Sand
    13: 2,   # Gravel
    14: 2,   # Gold Ore
    15: 2,   # Iron Ore
    16: 2,   # Coal Ore
    24: 2,   # Sandstone
    35: 4,   # Wool → décoration
    43: 2,   # Stone Double Slab
    44: 5,   # Stone Slab → toit
    45: 2,   # Bricks
    48: 2,   # Moss Stone
    49: 2,   # Obsidian
    67: 5,   # Cobblestone Stairs → toit
    87: 2,   # Netherrack
    88: 2,   # Soul Sand
    89: 4,   # Glowstone → décoration (lumière)
    98: 2,   # Stone Bricks
    99: 6,   # Brown Mushroom Block
    100: 6,  # Red Mushroom Block
    109: 5,  # Stone Brick Stairs → toit
    112: 2,  # Nether Brick
    114: 5,  # Nether Brick Stairs → toit
    128: 5,  # Sandstone Stairs → toit
    139: 2,  # Cobblestone Wall
    155: 2,  # Quartz Block
    156: 5,  # Quartz Stairs → toit
    159: 2,  # Stained Clay
    162: 1,  # Acacia/Dark Oak Log
    168: 2,  # Prismarine
    172: 2,  # Hardened Clay
    179: 2,  # Red Sandstone
    180: 5,  # Red Sandstone Stairs → toit

    # --- VERRE (famille 3) ---
    20: 3,   # Glass
    79: 3,   # Ice → transparent
    95: 3,   # Stained Glass
    102: 3,  # Glass Pane
    160: 3,  # Stained Glass Pane

    # --- DÉCORATION (famille 4) ---
    26: 4,   # Bed
    30: 4,   # Cobweb
    37: 4,   # Dandelion
    38: 4,   # Flower
    50: 4,   # Torch
    55: 7,   # Redstone Wire → redstone
    63: 4,   # Sign
    65: 4,   # Ladder
    66: 7,   # Rail → redstone
    69: 7,   # Lever → redstone
    70: 7,   # Stone Pressure Plate → redstone
    72: 7,   # Wooden Pressure Plate → redstone
    75: 4,   # Redstone Torch (off) → lumière
    76: 4,   # Redstone Torch (on) → lumière
    77: 7,   # Stone Button → redstone
    91: 4,   # Jack-o-lantern
    92: 4,   # Cake
    93: 7,   # Repeater (off) → redstone
    94: 7,   # Repeater (on) → redstone
    106: 6,  # Vines → végétation
    111: 6,  # Lily Pad → végétation
    140: 4,  # Flower Pot
    143: 7,  # Wooden Button → redstone
    144: 4,  # Skull
    145: 4,  # Anvil
    149: 7,  # Comparator (off) → redstone
    150: 7,  # Comparator (on) → redstone
    151: 4,  # Daylight Sensor
    158: 7,  # Dropper → redstone
    161: 6,  # Leaves2 → végétation
    166: 4,  # Barrier
    169: 4,  # Sea Lantern → lumière
    176: 4,  # Standing Banner
    177: 4,  # Wall Banner

    # --- TOIT (famille 5) ---
    53: 5,   # Oak Wood Stairs
    108: 5,  # Brick Stairs
    134: 5,  # Spruce Wood Stairs
    135: 5,  # Birch Wood Stairs
    136: 5,  # Jungle Wood Stairs
    163: 5,  # Acacia Wood Stairs
    164: 5,  # Dark Oak Wood Stairs

    # --- VÉGÉTATION (famille 6) ---
    6: 6,    # Sapling
    8: 2,    # Flowing Water → pierre (liquide)
    9: 2,    # Still Water → pierre
    10: 2,   # Flowing Lava → pierre
    11: 2,   # Still Lava → pierre
    18: 6,   # Leaves
    31: 6,   # Tall Grass
    32: 6,   # Dead Bush
    39: 6,   # Brown Mushroom
    40: 6,   # Red Mushroom
    81: 6,   # Cactus
    83: 6,   # Sugar Cane
    86: 4,   # Pumpkin
    103: 6,  # Melon
    175: 6,  # Double Tallgrass / Sunflower etc.

    # --- REDSTONE (famille 7) ---
    23: 7,   # Dispenser
    25: 7,   # Note Block
    27: 7,   # Powered Rail
    28: 7,   # Detector Rail
    29: 7,   # Sticky Piston
    33: 7,   # Piston
    34: 7,   # Piston Head
    46: 7,   # TNT
    54: 1,   # Chest → bois
    57: 2,   # Diamond Block → pierre précieuse
    73: 7,   # Redstone Ore
    74: 7,   # Glowing Redstone Ore
    123: 4,  # Redstone Lamp (off)
    124: 4,  # Redstone Lamp (on)
    137: 7,  # Command Block
    138: 4,  # Beacon
    146: 1,  # Trapped Chest → bois
    152: 7,  # Redstone Block
    153: 7,  # Nether Quartz Ore
    157: 7,  # Activator Rail
    158: 7,  # Dropper
}


def simplifier_bloc(nom_bloc):
    """
    Prend le nom complet d'un bloc minecraft (format moderne)
    et retourne le numéro de sa famille.
    ex: "minecraft:oak_planks" → 1 (bois)
    """
    if "air" in nom_bloc:
        return 0

    elif any(mot in nom_bloc for mot in [
        "planks", "log", "wood", "fence", "door", "trapdoor", "barrel", "bookshelf",
        "chest", "crafting_table", "furnace", "ladder", "sign", "stripped_",
        "acacia", "dark_oak", "spruce", "birch", "jungle", "oak", "mangrove", "bamboo"
    ]):
        # Évite de classer "oak_stairs" comme bois quand c'est un toit
        if any(mot in nom_bloc for mot in ["stairs", "slab"]):
            return 5
        return 1

    elif any(mot in nom_bloc for mot in [
        "stone", "cobblestone", "brick", "concrete", "terracotta", "dirt", "sand", "gravel",
        "granite", "diorite", "andesite", "deepslate", "tuff", "calcite", "basalt",
        "netherrack", "soul_sand", "obsidian", "prismarine", "quartz", "nether_brick",
        "blackstone", "end_stone", "mud", "packed_mud", "clay"
    ]):
        if any(mot in nom_bloc for mot in ["stairs", "slab", "wall"]):
            return 5
        return 2

    elif any(mot in nom_bloc for mot in ["glass", "pane", "ice", "packed_ice", "blue_ice"]):
        return 3

    elif any(mot in nom_bloc for mot in [
        "carpet", "wool", "painting", "pot", "lantern", "torch", "banner", "bed",
        "candle", "frame", "armor_stand", "banner", "skull", "head", "bell",
        "campfire", "cauldron", "composter", "grindstone", "loom", "smithing",
        "enchanting", "anvil", "beacon", "conduit", "lectern", "flower_pot",
        "glowstone", "sea_lantern", "shroomlight", "amethyst", "sculk"
    ]):
        return 4

    elif any(mot in nom_bloc for mot in [
        "stairs", "slab", "roof", "tile"
    ]):
        return 5

    elif any(mot in nom_bloc for mot in [
        "leaves", "grass", "vine", "flower", "sapling", "lily", "fern",
        "cactus", "bamboo", "mushroom", "coral", "seagrass", "kelp",
        "sugar_cane", "melon", "pumpkin", "wheat", "carrot", "potato",
        "wart", "chorus", "azalea", "moss", "dripleaf", "spore_blossom",
        "hanging_roots", "big_dripleaf", "small_dripleaf"
    ]):
        return 6

    elif any(mot in nom_bloc for mot in [
        "redstone", "piston", "repeater", "comparator", "lever", "button",
        "rail", "dispenser", "dropper", "hopper", "observer", "daylight",
        "tnt", "command", "note_block", "target", "sculk_sensor", "calibrated"
    ]):
        return 7

    else:
        return 2  # par défaut : pierre


def simplifier_bloc_legacy(id_numerique):
    """
    Prend un ID numérique (format .schematic legacy, Minecraft <= 1.12)
    et retourne le numéro de sa famille.
    Utilise la table LEGACY_ID_MAP, puis une heuristique de fallback.
    """
    if id_numerique in LEGACY_ID_MAP:
        return LEGACY_ID_MAP[id_numerique]
    # IDs non répertoriés → pierre par défaut (mur, sol, etc.)
    return 2


def convertir_grille(grille_3d, palette):
    """
    Prend la grille 3D brute (avec les IDs numériques)
    et la convertit en grille simplifiée (numéros de familles).
    Détecte automatiquement si la palette est en noms modernes ou IDs legacy.
    """
    grille_simplifiee = np.zeros_like(grille_3d, dtype=np.uint8)

    # Détection : est-ce un format legacy (palette = {int: "bloc_N"}) ?
    est_legacy = all(
        nom.startswith("bloc_") for nom in list(palette.values())[:5]
    ) if palette else False

    for idx_bloc, nom_bloc in palette.items():
        if est_legacy:
            # Format legacy : on extrait l'ID numérique du nom "bloc_N"
            try:
                id_num = int(nom_bloc.split("_")[1])
                famille = simplifier_bloc_legacy(id_num)
            except (IndexError, ValueError):
                famille = 2
        else:
            # Format moderne : on utilise le nom textuel
            famille = simplifier_bloc(nom_bloc)

        grille_simplifiee[grille_3d == idx_bloc] = famille

    return grille_simplifiee


def crop_air(grille_3d):
    """Supprime l'air inutile autour de la structure."""
    non_air = np.argwhere(grille_3d != 0)
    if len(non_air) == 0:
        return grille_3d
    min_coords = non_air.min(axis=0)
    max_coords = non_air.max(axis=0) + 1
    return grille_3d[
        min_coords[0]:max_coords[0],
        min_coords[1]:max_coords[1],
        min_coords[2]:max_coords[2]
    ]


def normaliser(grille_3d, taille_cible=32):
    """Redimensionne la grille à une taille fixe (32x32x32)."""
    grille_normalisee = np.zeros(
        (taille_cible, taille_cible, taille_cible), dtype=np.uint8
    )
    h = min(grille_3d.shape[0], taille_cible)
    l = min(grille_3d.shape[1], taille_cible)
    w = min(grille_3d.shape[2], taille_cible)
    grille_normalisee[:h, :l, :w] = grille_3d[:h, :l, :w]
    return grille_normalisee


def pretraiter(grille_3d, palette, taille_cible=32):
    """Fonction principale : simplification → crop → normalisation."""
    print("Étape 1 : simplification des blocs...")
    grille = convertir_grille(grille_3d, palette)

    print("Étape 2 : suppression de l'air inutile...")
    grille = crop_air(grille)
    print(f"  Taille après crop : {grille.shape}")

    print(f"Étape 3 : normalisation à {taille_cible}x{taille_cible}x{taille_cible}...")
    grille = normaliser(grille, taille_cible)
    print(f"  Taille finale : {grille.shape}")

    return grille


if __name__ == "__main__":
    from parser import lire_schem
    grille_brute, palette = lire_schem("data/maison/29572.schem")
    grille_finale = pretraiter(grille_brute, palette)
    print(f"\nGrille finale prête pour le modèle : {grille_finale.shape}")