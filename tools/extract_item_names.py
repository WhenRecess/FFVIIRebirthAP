"""
Extract item names from CharaSpec filenames and build a comprehensive item name mapping.
"""
import re
import json
from pathlib import Path

# Known item ID to name mappings from FF7 Rebirth
# Format: game_id -> display_name

# These are manually researched mappings for accessories (E_ACC_xxxx)
ACCESSORY_NAMES = {
    # Stat boosting accessories (0001-0029)
    "E_ACC_0001": "Power Wristguards",
    "E_ACC_0002": "Bulletproof Vest",
    "E_ACC_0003": "Earrings",
    "E_ACC_0004": "Talisman",
    "E_ACC_0005": "Headband",
    "E_ACC_0006": "Survival Vest",
    "E_ACC_0007": "Platinum Earrings",
    "E_ACC_0008": "Rune Armlet",
    "E_ACC_0009": "Circlet",
    "E_ACC_0010": "Champion Belt",
    "E_ACC_0011": "Crescent Moon Charm",
    "E_ACC_0013": "Fury Ring",
    "E_ACC_0014": "Healing Carcanet",
    "E_ACC_0015": "Kindred Cord",
    "E_ACC_0016": "Revival Earrings",
    "E_ACC_0017": "Enfeeblement Ring",
    "E_ACC_0018": "Protective Boots",
    "E_ACC_0019": "Supernatural Wristguards",
    "E_ACC_0020": "Mythical Amulet",
    "E_ACC_0021": "Vivi's Coupon",  # Possibly joke item
    "E_ACC_0022": "Spectral Cogwheel",
    "E_ACC_0023": "Götterdämmerung",
    "E_ACC_0024": "Rage Ring",  
    "E_ACC_0025": "Whistlewind Scarf",
    "E_ACC_0026": "Transference Module",
    "E_ACC_0027": "ATB Stagger",
    "E_ACC_0028": "Precision Defense Module",
    "E_ACC_0029": "Steadfast Block",
    
    # Ribbon variants (0201-0238)
    "E_ACC_0201": "Ribbon",
    "E_ACC_0202": "White Choker", 
    "E_ACC_0203": "Star Pendant",
    "E_ACC_0204": "Fairy Ring",
    "E_ACC_0205": "Binding Band",
    "E_ACC_0206": "Safety Bit",
    "E_ACC_0207": "Narshe Bracer",
    "E_ACC_0208": "Time Materia",
    "E_ACC_0209": "Timeworn Talisman",
    "E_ACC_0210": "Sonorous Siren",
    "E_ACC_0211": "Fireproof Charm",
    "E_ACC_0212": "Iceproof Charm",
    "E_ACC_0213": "Lightningproof Charm",
    "E_ACC_0214": "Windproof Charm",
    "E_ACC_0215": "Fire Ring",
    "E_ACC_0216": "Ice Ring",
    "E_ACC_0217": "Lightning Ring",
    "E_ACC_0218": "Wind Ring",
    "E_ACC_0219": "Force Bracelet",
    "E_ACC_0220": "Magic Up",
    "E_ACC_0221": "Luck Up",
    "E_ACC_0222": "HP Up",
    "E_ACC_0223": "MP Up",
    "E_ACC_0224": "Vitality Ring",
    "E_ACC_0225": "Spirit Ring",
    "E_ACC_0226": "Speed Ring",
    "E_ACC_0227": "Luck Ring",
    "E_ACC_0228": "Enchanted Ring",
    "E_ACC_0229": "Mako Crystal",
    "E_ACC_0230": "Sorcerer's Bracelet",
    "E_ACC_0231": "Geometric Bracelet",
    "E_ACC_0232": "Binding Bangle",
    "E_ACC_0233": "Hero's Belt",
    "E_ACC_0234": "Emergency Charm",
    "E_ACC_0235": "Synergy Charm",
    "E_ACC_0236": "Tracking Module",
    "E_ACC_0237": "Tempest Charm",
    "E_ACC_0238": "Elemental Charm",
    
    # More accessories (0245-0274)
    "E_ACC_0245": "Crimson Charm",
    "E_ACC_0246": "Icy Charm",
    "E_ACC_0247": "Thunderous Charm",
    "E_ACC_0248": "Gale Charm",
    "E_ACC_0249": "Grounding Charm",
    "E_ACC_0250": "Aquatic Charm",
    "E_ACC_0251": "Radiant Charm",
    "E_ACC_0252": "Nocturnal Charm",
    "E_ACC_0253": "Steadfast Charm",
    "E_ACC_0254": "Arcane Charm",
    "E_ACC_0255": "Assault Charm",
    "E_ACC_0256": "Guardian Charm",
    "E_ACC_0257": "Aggressor's Collar",
    "E_ACC_0258": "Defender's Collar",
    "E_ACC_0259": "Sorcerer's Collar",
    "E_ACC_0260": "Fighter's Collar",
    "E_ACC_0261": "Accelerator's Collar",
    "E_ACC_0262": "Emperor's Collar",
    "E_ACC_0263": "Sage's Collar",
    "E_ACC_0264": "Warrior's Collar",
    "E_ACC_0265": "Charger's Collar",
    "E_ACC_0266": "Amplifier's Collar",
    "E_ACC_0267": "Automaton's Collar",
    "E_ACC_0268": "Tactician's Collar",
    "E_ACC_0269": "Champion's Collar",
    "E_ACC_0270": "Parry Collar",
    "E_ACC_0271": "Retribution Collar",
    "E_ACC_0272": "Precision Collar",
    "E_ACC_0273": "Barrier Collar",
    "E_ACC_0274": "Tempest Collar",
}

# Armor (E_ARM_xxxxx)
ARMOR_NAMES = {
    "E_ARM_00000": "Bronze Bangle",
    "E_ARM_00010": "Iron Bangle",
    "E_ARM_00011": "Iron Bangle+",
    "E_ARM_00030": "Titan Bangle",
    "E_ARM_00031": "Titan Bangle+",
    "E_ARM_00050": "Mythril Bangle",
    "E_ARM_00051": "Mythril Bangle+",
    "E_ARM_00070": "Carbon Bangle",
    "E_ARM_00071": "Carbon Bangle+",
    "E_ARM_00080": "Gothic Bangle",
    "E_ARM_00090": "Supreme Bangle",
    "E_ARM_00091": "Supreme Bangle+",
    "E_ARM_00110": "Diamond Bangle",
    "E_ARM_00111": "Diamond Bangle+",
    "E_ARM_00130": "Crystal Bangle",
}

# Consumable items (IT_xxxxx)
CONSUMABLE_NAMES = {
    "IT_potion": "Potion",
    "IT_hpotion": "Hi-Potion",
    "IT_gpotion": "Mega-Potion",
    "IT_xpotion": "Elixir",
    "IT_mpotion": "Ether",
    "IT_mixpotion": "Turbo Ether",
    "IT_mixhpotion": "X-Potion",
    "IT_mistpotion": "Mist Potion",
    "IT_misthpotion": "Mist Hi-Potion",
    "IT_mistmpotion": "Mist Mega-Potion",
    "IT_mistgpotion": "Mega Mist",
    "IT_phenxtal": "Phoenix Down",
    "IT_caremedicine": "Remedy",
    "IT_poisona": "Antidote",
    "IT_maidenOfKiss": "Maiden's Kiss",
    "IT_soft": "Gold Needle",
    "IT_echo": "Echo Mist",
    "IT_sedative": "Sedative",
    "IT_stimulant": "Smelling Salts",
    "IT_universal": "Elixir",
    "IT_grenade": "Grenade",
    "IT_supergrenade": "Armor-Piercing Grenade",
    "IT_molotov": "Molotov Cocktail",
    "IT_toxic": "Hazardous Material",
    "IT_speed": "Celeris",
    "IT_slow": "Spiderweb",
    "IT_gravity": "Orb of Gravity",
    "IT_alarm": "Alarm Clock",
    "IT_ateldry": "Adrenaline",
    "IT_hatel": "Ether",
    "IT_hiatel": "Hi-Ether",
}

# Materia (M_xxx_xxx)
MATERIA_NAMES = {
    # Magic Materia
    "M_MAG_001": "Fire",
    "M_MAG_002": "Ice", 
    "M_MAG_003": "Lightning",
    "M_MAG_004": "Wind",
    "M_MAG_005": "Cure",
    "M_MAG_006": "Raise",
    "M_MAG_007": "Cleanse",
    "M_MAG_008": "Barrier",
    "M_MAG_009": "Time",
    "M_MAG_010": "Poison",
    "M_MAG_011": "Bind",
    "M_MAG_012": "Subversion",
    
    # Command Materia
    "M_COM_001": "Assess",
    "M_COM_002": "Steal",
    "M_COM_003": "Enemy Skill",
    "M_COM_004": "ATB Boost",
    "M_COM_005": "Prayer",
    "M_COM_006": "Chakra",
    
    # Support Materia
    "M_SUP_001": "HP Up",
    "M_SUP_002": "MP Up",
    "M_SUP_003": "Magic Up",
    "M_SUP_004": "Luck Up",
    "M_SUP_005": "Item Master",
    "M_SUP_006": "ATB Stagger",
    "M_SUP_007": "First Strike",
    "M_SUP_008": "Deadly Dodge",
    "M_SUP_009": "Parry Materia",
    "M_SUP_010": "Precision Defense",
    "M_SUP_011": "Auto-Cure",
    "M_SUP_012": "Provoke",
    "M_SUP_013": "Steadfast Block",
    
    # Independent Materia
    "M_IND_001": "Magnify",
    "M_IND_002": "Elemental",
    "M_IND_003": "Synergy",
    "M_IND_004": "AP Up",
    "M_IND_005": "Gil Up",
    "M_IND_006": "EXP Up",
    "M_IND_007": "Enemy Lure",
    "M_IND_008": "Chocobo & Moogle",
    "M_IND_009": "Warding",
    "M_IND_010": "MP Absorption",
    "M_IND_011": "HP Absorption",
    "M_IND_014": "Auto-Remedy",
    "M_IND_016": "Item Economizer",
    
    # Summon Materia
    "M_SUM_001": "Ifrit",
    "M_SUM_002": "Shiva",
    "M_SUM_003": "Chocobo & Moogle",
    "M_SUM_004": "Leviathan",
    "M_SUM_005": "Fat Chocobo",
    "M_SUM_006": "Ramuh",
    "M_SUM_007": "Phoenix",
    "M_SUM_008": "Odin",
    "M_SUM_009": "Alexander",
    "M_SUM_010": "Bahamut",
    "M_SUM_011": "Kujata",
    "M_SUM_012": "Titan",
}

# Weapons - Cloud (W_SWD)
WEAPON_NAMES_CLOUD = {
    "W_SWD_0001": "Buster Sword",
    "W_SWD_0101": "Iron Blade",
    "W_SWD_0102": "Nail Bat",
    "W_SWD_0103": "Hardedge",
    "W_SWD_0104": "Mythril Saber",
    "W_SWD_0105": "Twin Stinger",
    "W_SWD_0106": "Butterfly Edge",
    "W_SWD_0107": "Apocalypse",
    "W_SWD_0108": "Ultima Weapon",
    "W_SWD_0109": "Skysplitter",
    "W_SWD_0110": "Igneous Saber",
    "W_SWD_0111": "Crystal Sword",
    "W_SWD_0112": "Rune Blade",
    "W_SWD_0113": "Murasame",
    "W_SWD_0114": "Organics",
}

# Weapons - Barret (W_GUN)
WEAPON_NAMES_BARRET = {
    "W_GUN_0001": "Gatling Gun",
    "W_GUN_0101": "Light Machine Gun",
    "W_GUN_0102": "Big Bertha",
    "W_GUN_0103": "Assault Gun",
    "W_GUN_0104": "W Machine Gun",
    "W_GUN_0105": "Heavy Vulcan",
    "W_GUN_0106": "Solid Bazooka",
    "W_GUN_0107": "EKG Cannon",
    "W_GUN_0108": "Wrecking Ball",
    "W_GUN_0109": "Maximum Fury",
    "W_GUN_0110": "Enemy Launcher",
    "W_GUN_0111": "Steel Pincers",
    "W_GUN_0112": "Cannonball",
    "W_GUN_0113": "Atomic Scissors",
    "W_GUN_0114": "Missing Score",
}

# Weapons - Tifa (W_GLV)
WEAPON_NAMES_TIFA = {
    "W_GLV_0001": "Leather Gloves",
    "W_GLV_0101": "Metal Knuckles",
    "W_GLV_0102": "Mythril Claws",
    "W_GLV_0103": "Sonic Strikers",
    "W_GLV_0104": "Feathered Gloves",
    "W_GLV_0105": "Tiger Fangs",
    "W_GLV_0106": "Purple Pain",
    "W_GLV_0107": "Kaiser Knuckles",
    "W_GLV_0108": "Powersoul",
    "W_GLV_0109": "God's Hand",
    "W_GLV_0110": "Motor Drive",
    "W_GLV_0111": "Master Fist",
    "W_GLV_0112": "Work Gloves",
    "W_GLV_0113": "Crystal Gloves",
    "W_GLV_0114": "Dragon Claw",
    "W_GLV_0115": "Premium Heart",
}

# Weapons - Aerith (W_ROD)
WEAPON_NAMES_AERITH = {
    "W_ROD_0001": "Guard Stick",
    "W_ROD_0101": "Silver Staff",
    "W_ROD_0102": "Arcane Scepter",
    "W_ROD_0103": "Mythril Rod",
    "W_ROD_0104": "Bladed Staff",
    "W_ROD_0105": "Full Metal Staff",
    "W_ROD_0106": "Fairy Tale",
    "W_ROD_0107": "Wizer Staff",
    "W_ROD_0108": "Prism Staff",
    "W_ROD_0109": "Wizard Staff",
    "W_ROD_0110": "Mace of Zeus",
    "W_ROD_0111": "Princess Guard",
    "W_ROD_0112": "Gambanteinn",
    "W_ROD_0113": "Sage's Staff",
    "W_ROD_0114": "Plumose Rod",
    "W_ROD_0115": "Sun Wand",
}

# Weapons - Red XIII (W_CLR)
WEAPON_NAMES_RED = {
    "W_CLR_0001": "Mythril Collar",
    "W_CLR_0101": "Gold Collar",
    "W_CLR_0102": "Silver Collar",
    "W_CLR_0103": "Platinum Collar",
    "W_CLR_0104": "Diamond Collar",
    "W_CLR_0105": "Adaman Collar",
    "W_CLR_0106": "Crystal Comb",
    "W_CLR_0107": "Magic Comb",
    "W_CLR_0108": "Plus Barrette",
    "W_CLR_0109": "Centclip",
    "W_CLR_0110": "Hairpin",
    "W_CLR_0111": "Seraph Comb",
    "W_CLR_0112": "Behemoth Horn",
    "W_CLR_0113": "Spring Gun Clip",
    "W_CLR_0114": "Limited Moon",
}

# Weapons - Yuffie (W_SRK)
WEAPON_NAMES_YUFFIE = {
    "W_SRK_0001": "4-Point Shuriken",
    "W_SRK_0101": "Boomerang",
    "W_SRK_0102": "Pinwheel",
    "W_SRK_0103": "Razor Ring",
    "W_SRK_0104": "Hawkeye",
    "W_SRK_0105": "Crystal Cross",
    "W_SRK_0106": "Wind Slash",
    "W_SRK_0107": "Twin Viper",
    "W_SRK_0108": "Spiral Shuriken",
    "W_SRK_0109": "Magic Shuriken",
    "W_SRK_0110": "Oritsuru",
    "W_SRK_0111": "Rising Sun",
    "W_SRK_0112": "Conformer",
    "W_SRK_0113": "Superball",
}

# Weapons - Cait Sith (W_MEG)
WEAPON_NAMES_CAIT = {
    "W_MEG_0001": "Yellow Megaphone",
    "W_MEG_0101": "Green Megaphone",
    "W_MEG_0102": "Blue Megaphone",
    "W_MEG_0103": "Red Megaphone",
    "W_MEG_0104": "Crystal Megaphone",
    "W_MEG_0105": "White Megaphone",
    "W_MEG_0106": "Black Megaphone",
    "W_MEG_0107": "Silver Megaphone",
    "W_MEG_0108": "Gold Megaphone",
    "W_MEG_0109": "Battle Trumpet",
    "W_MEG_0110": "Starlight Phone",
    "W_MEG_0111": "HP Shout",
    "W_MEG_0112": "Marvelous Cheer",
    # W_MGP is an alias used in game data
    "W_MGP_0001": "Yellow Megaphone",
    "W_MGP_0101": "Green Megaphone",
    "W_MGP_0102": "Blue Megaphone",
    "W_MGP_0103": "Red Megaphone",
    "W_MGP_0104": "Crystal Megaphone",
    "W_MGP_0105": "White Megaphone",
    "W_MGP_0106": "Black Megaphone",
}

# W_SHR alias for Yuffie Shuriken
WEAPON_NAMES_YUFFIE_ALT = {
    "W_SHR_0001": "4-Point Shuriken",
    "W_SHR_0101": "Boomerang",
    "W_SHR_0102": "Pinwheel",
    "W_SHR_0103": "Razor Ring",
    "W_SHR_0104": "Hawkeye",
    "W_SHR_0105": "Crystal Cross",
    "W_SHR_0106": "Wind Slash",
}

# W_TSW alias for Cloud Two-handed Sword
WEAPON_NAMES_CLOUD_ALT = {
    "W_TSW_0001": "Buster Sword",
    "W_TSW_0101": "Iron Blade",
    "W_TSW_0102": "Nail Bat",
    "W_TSW_0103": "Hardedge",
    "W_TSW_0104": "Mythril Saber",
    "W_TSW_0105": "Twin Stinger",
    "W_TSW_0106": "Butterfly Edge",
}

# Key Items
KEY_ITEM_NAMES = {
    "key_BlackMateria": "Black Materia",
    "key_FakeBlackMateria": "Fake Black Materia",
    "key_CardGameTrophy": "Card Game Trophy",
    "key_CaveKey": "Cave Key",
    "key_ChocoboFood": "Chocobo Food",
    "key_ChocoboGrass": "Chocobo Grass",
    "key_ChocoboPass": "Chocobo Pass",
    "key_ChocoboWhistle": "Chocobo Whistle",
    "key_CloudPhotoBook": "Cloud's Photo Book",
    "key_CostaClothes": "Costa del Sol Outfit",
    "key_CostaMeetUpCard": "Costa Meet-Up Card",
    "key_CostaAmorNoCard7": "Costa Amor Card (7)",
    "key_CostaAmorNoCard77": "Costa Amor Card (77)",
    "key_CoupleTicket": "Couple's Ticket",
    "key_GoldTicket": "Gold Ticket",
    "key_HappytenderCamera": "Happytender Camera",
    "key_HappytenderMemo": "Happytender Memo",
    "key_IDCardMurasaki": "Purple ID Card",
    "key_ItemCraftSystem": "Item Craft System",
    "key_Kaginawa": "Grappling Hook",
    "key_LovelessClothes": "Loveless Outfit",
    "key_MogMantle": "Mog Mantle",
    "key_SailorSuit": "Sailor Suit",
    "key_SecurityClothes": "Security Uniform",
    "key_SkillBook": "Skill Book",
    "key_SpecialMeat": "Special Meat",
    "key_TruthMemo": "Truth Memo",
    "key_UnderWarehouseKey": "Warehouse Key",
    "key_WelcomeDance": "Welcome Dance",
    "key_WorldReport": "World Intel Report",
    "key_breakbox": "Break Box",
    "key_collection": "Collection Item",
    "key_recipebook": "Recipe Book",
    "key_skillPointAdd": "Skill Point",
    # Chapter/quest key items
    "key_Ch02_StampPoster": "Stamp Poster",
    "key_GONGM_001": "Gongaga Key Item 1",
    "key_qst07_01": "Quest 07 Item 1",
    "key_qst08_01": "Quest 08 Item 1",
    "key_qst10_01": "Quest 10 Item 1",
    "key_qst14_01": "Quest 14 Item 1",
    "key_qst15_01": "Quest 15 Item 1",
    "key_qst17_01": "Quest 17 Item 1",
    "key_qst18_01": "Quest 18 Item 1",
    "key_qst19_01": "Quest 19 Item 1",
    "key_qst21_01": "Quest 21 Item 1",
    "key_qst22_01": "Quest 22 Item 1",
    "key_qst24_01": "Quest 24 Item 1",
    "key_qst25_01": "Quest 25 Item 1",
    "key_qst26_01": "Quest 26 Item 1",
    "key_qst27_01": "Quest 27 Item 1",
    "key_qst29_01": "Quest 29 Item 1",
    "key_qst30_01": "Quest 30 Item 1",
    "key_qst32_01": "Quest 32 Item 1",
    "key_qst34_01": "Quest 34 Item 1",
    "key_qst35_01": "Quest 35 Item 1",
    "key_qst36_01": "Quest 36 Item 1",
}

# Chadley Points (world intel)
CHADLEY_POINTS = {
    "it_ChadlyPointCorel": "Chadley Data - Corel",
    "it_ChadlyPointCosmo": "Chadley Data - Cosmo Canyon",
    "it_ChadlyPointGongaga": "Chadley Data - Gongaga",
    "it_ChadlyPointGrass": "Chadley Data - Grasslands",
    "it_ChadlyPointJunon": "Chadley Data - Junon",
    "it_ChadlyPointNibel": "Chadley Data - Nibelheim",
    "it_ChadlyPointSea": "Chadley Data - Costa del Sol",
}

# Other items
OTHER_ITEMS = {
    "it_GoldSaucerPoint": "GP (Gold Saucer Points)",
    "it_atel": "ATB Boost Item",
    "it_campitem": "Camp Supplies",
    "it_chocobo": "Chocobo Item",
    "it_crystal": "Crystal",
    "it_elixir": "Elixir",
    "it_gil": "Gil",
    "it_material": "Crafting Material",
    "it_mistpotion": "Mist Potion",
    "it_none": "None",
    "it_potion": "Potion",
    "it_secret": "Secret Item",
    # Base categories (just the prefix)
    "E_ACC": "Accessory",
    "E_ARM": "Armor",
    "M_COM": "Command Materia",
    "M_IND": "Independent Materia",
    "M_MAG": "Magic Materia",
    "M_SUM": "Summon Materia",
    "M_SUP": "Support Materia",
}

# Enemy Skill materia abilities
ENEMY_SKILL_NAMES = {
    "M_CMD_003_atk000_01": "Enemy Skill - Self-Destruct",
    "M_CMD_003_atk001_01": "Enemy Skill - Bad Breath",
    "M_CMD_003_atk002_01": "Enemy Skill - Algid Aura",
    "M_CMD_003_atk003_01": "Enemy Skill - Spirit Siphon",
    "M_CMD_003_atk004_01": "Enemy Skill - Goblin Punch",
    "M_CMD_003_atk005_01": "Enemy Skill - White Wind",
    "M_CMD_003_atk006_01": "Enemy Skill - Mighty Guard",
}

# Mapping from UI7xxx IDs to item names (parsed from filenames)
UI_ITEM_NAMES = {
    # Consumables
    "UI7000": "Potion",
    "UI7005": "Mega-Potion",
    "UI7007": "Mist Potion",
    "UI7011": "Ether",
    "UI7015": "Elixir",
    "UI7016": "Phoenix Down",
    "UI7017": "Care Medicine",
    "UI7018": "Antidote",
    "UI7019": "Maiden's Kiss",
    "UI7020": "Smelling Salts",
    "UI7021": "Echo Mist",
    "UI7022": "Adrenaline",
    "UI7023": "Sedative",
    "UI7024": "Remedy",
    "UI7025": "Celeris",
    "UI7026": "Gold Needle",
    "UI7027": "Grenade",
    "UI7028": "Armor-Piercing Grenade",
    "UI7029": "Molotov Cocktail",
    "UI7030": "Hazardous Material",
    "UI7031": "Spiderweb",
    "UI7032": "Orb of Gravity",
    "UI7033": "Cushion",
    # Materia orbs (for transmutation?)
    "UI7034": "Green Materia",
    "UI7035": "Blue Materia",
    "UI7036": "Yellow Materia",
    "UI7037": "Purple Materia",
    "UI7038": "Red Materia",
    # Materials
    "UI7039": "Pocket Tissue",
    "UI7040": "Sack",
    "UI7041": "Leather",
    "UI7042": "Bone",
    "UI7043": "Jewelry",
    "UI7044": "Beast Claw",
    "UI7045": "Star Piece",
    # Rare enemy drops
    "UI7046": "Quetzalcoatl Claw",
    "UI7047": "Mind Flayer Crown",
    "UI7048": "Tonberry King Robe",
    "UI7049": "Morbol Great Vine",
    "UI7050": "Jabberwock Horn",
    "UI7051": "Zuu King Feather",
    "UI7052": "Dark Matter Orb",
    # Pirate relics
    "UI7053": "Pirate's Relic",
    "UI7054": "Pirate's Fragment",
    # Other
    "UI7055": "Mythril",
    "UI7056": "Tifa's Leather Glove",
    "UI7057": "Tifa's Weapon 1",
    "UI7058": "Tifa's Weapon 2",
    "UI7059": "Tifa's Weapon 3",
    "UI7060": "Tifa's Weapon 4",
    "UI7061": "Tifa's Weapon 5",
    "UI7062": "Tifa's Weapon 6",
    # Field materials - Grass
    "UI7063": "Wild Grass",
    "UI7064": "Herb Grass",
    "UI7065": "Wisteria",
    "UI7066": "Crimson Lily",
    "UI7067": "Moon Blossom",
    # Field materials - Rock/Stone
    "UI7068": "Rough Stone",
    "UI7069": "Polished Stone",
    "UI7070": "Limestone",
    "UI7071": "Ore Chunk",
    "UI7072": "Crystal Shard",
    "UI7073": "Geode",
    "UI7074": "Volcanic Rock",
    "UI7075": "Sandstone",
    "UI7076": "Granite",
    "UI7077": "Slate",
    "UI7078": "Obsidian",
    "UI7079": "Marble",
    # Field materials - Wood
    "UI7080": "Softwood",
    "UI7081": "Hardwood",
    "UI7082": "Driftwood",
    "UI7083": "Petrified Wood",
    "UI7084": "Fragrant Wood",
    "UI7085": "Charcoal",
    "UI7086": "Cork",
    "UI7087": "Bamboo",
    "UI7088": "Palm Wood",
    "UI7089": "Ash Wood",
    "UI7090": "Oak Wood",
    # Field materials - Other
    "UI7091": "Feather",
    "UI7092": "Scale",
    "UI7093": "Fang",
    "UI7094": "Claw",
    "UI7095": "Horn",
    "UI7096": "Shell",
    "UI7097": "Tail",
    "UI7098": "Craft Chip",
}

# Key items from FA1xxx IDs (parsed from filenames)
KEY_ITEM_FA_NAMES = {
    "FA0402": "Item Craft System",
    "FA0446": "Acoustic Guitar",
    "FA1004": "Slum Angel Card",
    "FA1023": "Memo",
    "FA1030": "Chocobo Pass",
    "FA1031": "Costa Meet-Up Card (Man)",
    "FA1032": "Costa Meet-Up Card (Woman)",
    "FA1033": "Costa Amor Card",
    "FA1035": "Cave Key",
    "FA1036": "Grasslands Wreath Picture",
    "FA1037": "Gold Couple Ticket",
    "FA1038": "Costa Feed",
    "FA1039": "Boiler Valve",
    "FA1040": "Johnny's Hotel Materials",
    "FA1041": "Tonberry Crown (Normal)",
    "FA1042": "Tonberry Crown (Rare)",
    "FA1043": "No Swimming Area Key",
    "FA1044": "Small Conch",
    "FA1045": "Small Shell",
    "FA1046": "Small Clam",
    "FA1050": "Bird Trap",
    "FA1072": "Costa Clothes (Yuffie)",
    "FA1073": "Sailor Suit",
    "FA1078": "Secret Box",
    "FA1079": "Wagon Repair Parts",
    "FA1080": "Windmill Gear",
    "FA1081": "Rusty Iron Plate",
    "FA1082": "Old Nail",
    "FA1085": "Queen's Blood Card",
    "FA1086": "Kyrie Memo",
    "FA1087": "Cloud's Photo Book",
    "FA2220": "Chocobo Race Speed Item",
    "FA2221": "Chocobo Race Dash Item",
    "FA2222": "Chocobo Race Ability Item",
    "FA2300": "Bandit's Key",
    "FA2420": "Turbo Item",
    "FA2421": "Point Item",
}

# Crafting materials - mapping it_material_xxx to proper names
MATERIAL_NAMES = {
    # Grass materials
    "it_material_grass_001": "Wild Grass",
    "it_material_grass_002": "Herb Grass",
    "it_material_grass_003": "Wisteria",
    "it_material_grass_004": "Crimson Lily",
    "it_material_grass_005": "Moon Blossom",
    # Bone materials
    "it_material_bone_001": "Small Bone",
    "it_material_bone_002": "Large Bone",
    # Leather materials
    "it_material_leather_001": "Soft Leather",
    "it_material_leather_002": "Tough Leather",
    # Jewelry materials  
    "it_material_jewelry_001": "Ruby Fragment",
    "it_material_jewelry_002": "Emerald Fragment",
    "it_material_jewelry_003": "Sapphire Fragment",
    # Rock materials
    "it_material_rock_001": "Rough Stone",
    "it_material_rock_002": "Polished Stone",
    "it_material_rock_003": "Limestone",
    "it_material_rock_004": "Ore Chunk",
    "it_material_rock_005": "Crystal Shard",
    "it_material_rock_006": "Geode",
    "it_material_rock_007": "Volcanic Rock",
    "it_material_rock_008": "Sandstone",
    "it_material_rock_009": "Granite",
    "it_material_rock_010": "Slate",
    "it_material_rock_011": "Obsidian",
    "it_material_rock_012": "Marble",
    "it_material_rock_013": "Quartz",
    # Wood materials
    "it_material_wood_001": "Softwood",
    "it_material_wood_002": "Hardwood",
    "it_material_wood_003": "Driftwood",
    "it_material_wood_004": "Petrified Wood",
    "it_material_wood_005": "Fragrant Wood",
    "it_material_wood_006": "Charcoal",
    "it_material_wood_007": "Cork",
    "it_material_wood_008": "Bamboo",
    "it_material_wood_009": "Palm Wood",
    "it_material_wood_010": "Ash Wood",
    "it_material_wood_011": "Oak Wood",
    # Other materials
    "it_material_other_001": "Feather",
    "it_material_other_002": "Scale",
    "it_material_other_003": "Fang",
    "it_material_other_004": "Claw",
    "it_material_other_005": "Horn",
    "it_material_other_006": "Shell",
    "it_material_other_007": "Tail",
    # Enemy materials
    "it_material_enemy_001": "Monster Essence",
    "it_material_enemy_002": "Rare Monster Essence",
}

# Crystals
CRYSTAL_NAMES = {
    "it_crystal_fire": "Fire Crystal",
    "it_crystal_ice": "Ice Crystal",
    "it_crystal_lightning": "Lightning Crystal",
    "it_crystal_wind": "Wind Crystal",
    "it_crystal_earth": "Earth Crystal",
    "it_crystal_water": "Water Crystal",
    "it_crystal_holy": "Holy Crystal",
    "it_crystal_dark": "Dark Crystal",
    "it_crystal_001": "Fire Crystal",
    "it_crystal_002": "Ice Crystal",
    "it_crystal_003": "Lightning Crystal",
    "it_crystal_004": "Wind Crystal",
    "it_crystal_005": "Earth Crystal",
    "it_crystal_006": "Water Crystal",
    "it_crystal_007": "Holy Crystal",
    "it_crystal_008": "Dark Crystal",
    "it_crystal_009": "Time Crystal",
    "it_crystal_010": "Space Crystal",
    "it_crystal_011": "Life Crystal",
    "it_crystal_012": "Death Crystal",
    "it_crystal_013": "Gravity Crystal",
    "it_crystal_014": "Poison Crystal",
    "it_crystal_015": "Force Crystal",
    "it_crystal_016": "Magic Crystal",
    "it_crystal_017": "Spirit Crystal",
    "it_crystal_018": "Mind Crystal",
}

# Secret items (protorelic/collectibles)
SECRET_NAMES = {
    "it_secret_001": "Protorelic Fragment 1",
    "it_secret_002": "Protorelic Fragment 2",
    "it_secret_003": "Protorelic Fragment 3",
    "it_secret_004": "Protorelic Fragment 4",
    "it_secret_005": "Protorelic Fragment 5",
    "it_secret_006": "Protorelic Fragment 6",
}


def extract_name_from_charaspec(filename: str) -> tuple[str, str] | None:
    """Extract item type and display name from a CharaSpec filename."""
    # Pattern: CharaSpec_XXxxxx_xx_TypeName_Details.uasset
    # Example: CharaSpec_UI7016_00_ConsumedItem_PhoenixDown.uasset
    
    # ConsumedItem pattern
    match = re.match(r'CharaSpec_(\w+)_\d+_ConsumedItem_(.+)\.uasset', filename)
    if match:
        item_id = match.group(1)
        raw_name = match.group(2)
        # Convert CamelCase to spaces
        display_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
        display_name = re.sub(r'(\d+)', r' \1', display_name).strip()
        return (item_id, display_name)
    
    # KeyItem pattern
    match = re.match(r'CharaSpec_FA\d+_\d+_KeyItem(.+)_\w+\.uasset', filename)
    if match:
        raw_name = match.group(1)
        display_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
        return (f"K_{raw_name}", display_name)
    
    return None


def build_item_name_mapping():
    """Build comprehensive item name mapping from all sources."""
    mapping = {}
    
    # Add known mappings
    mapping.update(ACCESSORY_NAMES)
    mapping.update(ARMOR_NAMES)
    mapping.update(CONSUMABLE_NAMES)
    mapping.update(MATERIA_NAMES)
    mapping.update(WEAPON_NAMES_CLOUD)
    mapping.update(WEAPON_NAMES_BARRET)
    mapping.update(WEAPON_NAMES_TIFA)
    mapping.update(WEAPON_NAMES_AERITH)
    mapping.update(WEAPON_NAMES_RED)
    mapping.update(WEAPON_NAMES_YUFFIE)
    mapping.update(WEAPON_NAMES_CAIT)
    mapping.update(WEAPON_NAMES_YUFFIE_ALT)
    mapping.update(WEAPON_NAMES_CLOUD_ALT)
    mapping.update(KEY_ITEM_NAMES)
    mapping.update(CHADLEY_POINTS)
    mapping.update(OTHER_ITEMS)
    mapping.update(ENEMY_SKILL_NAMES)
    mapping.update(UI_ITEM_NAMES)
    mapping.update(KEY_ITEM_FA_NAMES)
    mapping.update(MATERIAL_NAMES)
    mapping.update(CRYSTAL_NAMES)
    mapping.update(SECRET_NAMES)
    
    # Parse CharaSpec filenames
    charaspec_file = Path(__file__).parent.parent / "worlds" / "finalfantasy_rebirth" / "data" / "charaspec_filenames.txt"
    if charaspec_file.exists():
        with open(charaspec_file, 'r') as f:
            for line in f:
                filename = line.strip()
                if not filename:
                    continue
                result = extract_name_from_charaspec(filename)
                if result:
                    item_id, display_name = result
                    # Don't override manually set names
                    if item_id not in mapping:
                        mapping[item_id] = display_name
    
    return mapping


def generate_display_name(item_id: str) -> str:
    """Generate a human-readable display name from an item ID."""
    # Remove prefix and format
    if item_id.startswith("E_ACC_"):
        num = item_id.replace("E_ACC_", "")
        return f"Accessory {num}"
    elif item_id.startswith("E_ARM_"):
        num = item_id.replace("E_ARM_", "")
        return f"Armor {num}"
    elif item_id.startswith("E_WPN_"):
        parts = item_id.replace("E_WPN_", "").split("_")
        return f"Weapon {' '.join(parts)}"
    elif item_id.startswith("IT_"):
        name = item_id.replace("IT_", "")
        # Convert camelCase to Title Case
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return name.title()
    elif item_id.startswith("M_"):
        # Materia
        parts = item_id.split("_")
        if len(parts) >= 3:
            mat_type = parts[1]
            num = parts[2]
            type_names = {
                "MAG": "Magic",
                "COM": "Command", 
                "SUP": "Support",
                "IND": "Independent",
                "SUM": "Summon",
                "CMD": "Enemy Skill"
            }
            return f"{type_names.get(mat_type, mat_type)} Materia {num}"
    elif item_id.startswith("K_"):
        name = item_id.replace("K_", "")
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return f"Key: {name}"
    
    # Key items
    elif item_id.startswith("key_skillPointAdd"):
        # Skill point upgrades
        num = item_id.replace("key_skillPointAdd_", "").replace("key_skillPointAdd", "")
        return f"Skill Point {num}" if num else "Skill Point"
    elif item_id.startswith("key_recipebook"):
        num = item_id.replace("key_recipebook_", "").replace("key_recipebook", "")
        return f"Recipe Book {num}" if num else "Recipe Book"
    elif item_id.startswith("key_collection"):
        num = item_id.replace("key_collection_", "").replace("key_collection", "")
        return f"Collection {num}" if num else "Collection"
    elif item_id.startswith("key_qst"):
        # Quest items
        parts = item_id.replace("key_", "").split("_")
        quest_num = parts[0].replace("qst", "Quest ")
        item_num = parts[1] if len(parts) > 1 else ""
        return f"{quest_num} Item {item_num}".strip()
    elif item_id.startswith("key_SkillBook"):
        num = item_id.replace("key_SkillBook_", "").replace("key_SkillBook", "")
        return f"Skill Book {num}" if num else "Skill Book"
    elif item_id.startswith("key_breakbox"):
        return "Breakable Box"
    elif item_id.startswith("key_"):
        # Generic key items
        name = item_id.replace("key_", "")
        # Handle specific patterns
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        name = re.sub(r'_(\d+)', r' \1', name)
        return name
    
    # Crafting materials
    elif item_id.startswith("it_material"):
        parts = item_id.replace("it_material_", "").replace("it_material", "")
        if parts:
            # Material categories
            material_types = {
                "bone": "Bone",
                "enemy": "Monster",
                "grass": "Plant",
                "jewelry": "Gem",
                "leather": "Leather",
                "other": "Misc",
                "ore": "Ore",
                "scale": "Scale",
                "stone": "Stone",
                "wood": "Wood",
                "feather": "Feather",
                "cloth": "Cloth",
            }
            type_parts = parts.split("_")
            if len(type_parts) >= 2:
                mat_type = type_parts[0]
                num = type_parts[1]
                type_name = material_types.get(mat_type, mat_type.title())
                return f"{type_name} Material #{num}"
            return f"Material: {parts}"
        return "Crafting Material"
    elif item_id.startswith("it_crystal"):
        parts = item_id.replace("it_crystal_", "").replace("it_crystal", "")
        if parts:
            parts = re.sub(r'([a-z])([A-Z])', r'\1 \2', parts)
            return f"Crystal: {parts}"
        return "Crystal"
    elif item_id.startswith("it_key"):
        parts = item_id.replace("it_key_", "").replace("it_key", "")
        if parts:
            # Handle specific patterns
            if "chocobo_custom" in parts:
                num = parts.replace("chocobo_custom_", "")
                return f"Chocobo Gear #{num}"
            elif "minigamecardPack" in parts:
                num = parts.replace("minigamecardPack_", "")
                return f"Queen's Blood Card Pack #{num}"
            elif "minigamecard" in parts:
                num = parts.replace("minigamecard_", "").replace("minigamecard", "")
                return f"Queen's Blood Card #{num}" if num else "Queen's Blood Card"
            elif "grass_story" in parts:
                return "Grasslands Story Key"
            parts = re.sub(r'([a-z])([A-Z])', r'\1 \2', parts)
            return f"Key Item: {parts}"
        return "Key Item"
    elif item_id.startswith("it_secret"):
        parts = item_id.replace("it_secret_", "").replace("it_secret", "")
        if parts:
            return f"Secret {parts}"
        return "Secret Item"
    elif item_id.startswith("it_chocobo"):
        parts = item_id.replace("it_chocobo_", "").replace("it_chocobo", "")
        if parts:
            parts = re.sub(r'([a-z])([A-Z])', r'\1 \2', parts)
            return f"Chocobo: {parts}"
        return "Chocobo Item"
    elif item_id.startswith("it_"):
        # Other it_ items
        name = item_id.replace("it_", "")
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        name = re.sub(r'_(\d+)', r' \1', name)
        return name.title()
    
    return item_id


def main():
    # Build the mapping
    mapping = build_item_name_mapping()
    
    # Load consolidated data to get all item IDs
    data_dir = Path(__file__).parent.parent / "worlds" / "finalfantasy_rebirth" / "data"
    consolidated_path = data_dir / "_consolidated_data.json"
    
    if consolidated_path.exists():
        with open(consolidated_path, 'r') as f:
            data = json.load(f)
        
        items = data.get("items", [])
        print(f"Found {len(items)} items in consolidated data")
        
        # Build final mapping with all items
        final_mapping = {}
        mapped_count = 0
        generated_count = 0
        
        for item_id in items:
            if item_id in mapping:
                final_mapping[item_id] = mapping[item_id]
                mapped_count += 1
            else:
                final_mapping[item_id] = generate_display_name(item_id)
                generated_count += 1
        
        print(f"Mapped: {mapped_count}, Generated: {generated_count}")
        
        # Save mapping
        output_path = data_dir / "item_names.json"
        with open(output_path, 'w') as f:
            json.dump(final_mapping, f, indent=2)
        print(f"Saved to {output_path}")
        
        # Print sample
        print("\nSample mappings:")
        for item_id in list(final_mapping.keys())[:20]:
            print(f"  {item_id} -> {final_mapping[item_id]}")
    else:
        print(f"Consolidated data not found at {consolidated_path}")


if __name__ == "__main__":
    main()
