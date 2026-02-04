"""
Item Data Tables for Final Fantasy VII: Rebirth
================================================================

This module contains all static item definitions organized by their
Archipelago classification. Items are defined as dictionaries mapping
item names to FFVIIRItemData tuples.

Classifications:
    PROGRESSION_ITEMS
        Items required to access new areas or complete the game.
        Examples: Chapter unlocks, party members, key traversal items.
    
    USEFUL_ITEMS
        Helpful items that improve gameplay but aren't required.
        Examples: Equipment, materia (generated from game data).
    
    SUMMON_MATERIA
        Special useful items representing summon materia.
        These are progression-adjacent but classified as useful.
    
    FILLER_ITEMS
        Common items to fill remaining location slots.
        Examples: Consumables, gil bundles.
    
    TRAP_ITEMS
        Optional negative effect items (disabled by default).
        Examples: Poison trap, gil loss.

Item Data Structure (FFVIIRItemData):
    - display_name: Human-readable name shown to players
    - classification: Archipelago ItemClassification enum value
    - game_id: Original game's internal ID (e.g., "IT_potion")
    - count: Number of this item in the pool (default: 1)
    - description: Brief description of the item's effect

Note:
    Equipment items are dynamically generated from game data exports
    in randomization/item_pool.py, not defined here.
"""
from typing import Dict, NamedTuple
from BaseClasses import ItemClassification


class FFVIIRItemData(NamedTuple):
    """Data structure for an Archipelago item."""
    display_name: str
    classification: ItemClassification
    game_id: str = ""  # Original game ID (e.g., "E_ACC_0001")
    count: int = 1     # How many of this item exist in the pool
    description: str = ""


# ============================================================================
# PROGRESSION ITEMS - Required to complete the game/access areas
# ============================================================================
PROGRESSION_ITEMS: Dict[str, FFVIIRItemData] = {
    # Story/Chapter progression 
    "Chapter 1 Complete": FFVIIRItemData(
        "Chapter 1 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 2"
    ),
    "Chapter 2 Complete": FFVIIRItemData(
        "Chapter 2 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 3"
    ),
    "Chapter 3 Complete": FFVIIRItemData(
        "Chapter 3 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 4"
    ),
    "Chapter 4 Complete": FFVIIRItemData(
        "Chapter 4 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 5"
    ),
    "Chapter 5 Complete": FFVIIRItemData(
        "Chapter 5 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 6"
    ),
    "Chapter 6 Complete": FFVIIRItemData(
        "Chapter 6 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 7"
    ),
    "Chapter 7 Complete": FFVIIRItemData(
        "Chapter 7 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 8"
    ),
    "Chapter 8 Complete": FFVIIRItemData(
        "Chapter 8 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 9"
    ),
    "Chapter 9 Complete": FFVIIRItemData(
        "Chapter 9 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 10"
    ),
    "Chapter 10 Complete": FFVIIRItemData(
        "Chapter 10 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 11"
    ),
    "Chapter 11 Complete": FFVIIRItemData(
        "Chapter 11 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 12"
    ),
    "Chapter 12 Complete": FFVIIRItemData(
        "Chapter 12 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 13"
    ),
    "Chapter 13 Complete": FFVIIRItemData(
        "Chapter 13 Complete", ItemClassification.progression, "", 1, "Unlocks Chapter 14"
    ),
    
    # Party members
    "Party: Barret": FFVIIRItemData(
        "Party: Barret", ItemClassification.progression, "", 1, "Barret joins the party"
    ),
    "Party: Tifa": FFVIIRItemData(
        "Party: Tifa", ItemClassification.progression, "", 1, "Tifa joins the party"
    ),
    "Party: Aerith": FFVIIRItemData(
        "Party: Aerith", ItemClassification.progression, "", 1, "Aerith joins the party"
    ),
    "Party: Red XIII": FFVIIRItemData(
        "Party: Red XIII", ItemClassification.progression, "", 1, "Red XIII joins the party"
    ),
    "Party: Yuffie": FFVIIRItemData(
        "Party: Yuffie", ItemClassification.progression, "", 1, "Yuffie joins the party"
    ),
    "Party: Cait Sith": FFVIIRItemData(
        "Party: Cait Sith", ItemClassification.progression, "", 1, "Cait Sith joins the party"
    ),
    "Party: Vincent": FFVIIRItemData(
        "Party: Vincent", ItemClassification.progression, "", 1, "Vincent joins the party"
    ),
    "Party: Cid": FFVIIRItemData(
        "Party: Cid", ItemClassification.progression, "", 1, "Cid joins the party"
    ),
    
    # Key abilities/items for traversal
    "Chocobo License": FFVIIRItemData(
        "Chocobo License", ItemClassification.progression, "", 1, "Can ride chocobos"
    ),
    "Grappling Hook": FFVIIRItemData(
        "Grappling Hook", ItemClassification.progression, "", 1, "Access grapple points"
    ),
    "Climbing Gear": FFVIIRItemData(
        "Climbing Gear", ItemClassification.progression, "", 1, "Climb rock walls"
    ),
    
    # Region access
    "Grasslands Access": FFVIIRItemData(
        "Grasslands Access", ItemClassification.progression, "", 1, "Access Grasslands region"
    ),
    "Junon Access": FFVIIRItemData(
        "Junon Access", ItemClassification.progression, "", 1, "Access Junon region"
    ),
    "Costa del Sol Access": FFVIIRItemData(
        "Costa del Sol Access", ItemClassification.progression, "", 1, "Access Costa del Sol"
    ),
    "Corel Access": FFVIIRItemData(
        "Corel Access", ItemClassification.progression, "", 1, "Access Corel region"
    ),
    "Gongaga Access": FFVIIRItemData(
        "Gongaga Access", ItemClassification.progression, "", 1, "Access Gongaga region"
    ),
    "Cosmo Canyon Access": FFVIIRItemData(
        "Cosmo Canyon Access", ItemClassification.progression, "", 1, "Access Cosmo Canyon"
    ),
    "Nibelheim Access": FFVIIRItemData(
        "Nibelheim Access", ItemClassification.progression, "", 1, "Access Nibelheim region"
    ),
    
    # Colosseum/VR access
    "Colosseum Pass": FFVIIRItemData(
        "Colosseum Pass", ItemClassification.progression, "", 1, "Access Gold Saucer Colosseum"
    ),
    "VR Simulator Access": FFVIIRItemData(
        "VR Simulator Access", ItemClassification.progression, "", 1, "Access Chadley's VR missions"
    ),
}


# ============================================================================
# USEFUL ITEMS - Static equipment and materia
# ============================================================================
USEFUL_ITEMS: Dict[str, FFVIIRItemData] = {
    # Placeholder for manually defined useful items
    # Most useful items are generated dynamically from game data
}


# ============================================================================
# SUMMON MATERIA - Special progression-adjacent items
# ============================================================================
SUMMON_MATERIA: Dict[str, FFVIIRItemData] = {
    "Summon: Ifrit": FFVIIRItemData(
        "Summon: Ifrit", ItemClassification.useful, "", 1, "Fire summon"
    ),
    "Summon: Shiva": FFVIIRItemData(
        "Summon: Shiva", ItemClassification.useful, "", 1, "Ice summon"
    ),
    "Summon: Ramuh": FFVIIRItemData(
        "Summon: Ramuh", ItemClassification.useful, "", 1, "Lightning summon"
    ),
    "Summon: Titan": FFVIIRItemData(
        "Summon: Titan", ItemClassification.useful, "", 1, "Earth summon"
    ),
    "Summon: Odin": FFVIIRItemData(
        "Summon: Odin", ItemClassification.useful, "", 1, "Dark summon"
    ),
    "Summon: Phoenix": FFVIIRItemData(
        "Summon: Phoenix", ItemClassification.useful, "", 1, "Fire/Revive summon"
    ),
    "Summon: Alexander": FFVIIRItemData(
        "Summon: Alexander", ItemClassification.useful, "", 1, "Holy summon"
    ),
    "Summon: Kujata": FFVIIRItemData(
        "Summon: Kujata", ItemClassification.useful, "", 1, "Multi-element summon"
    ),
    "Summon: Bahamut": FFVIIRItemData(
        "Summon: Bahamut", ItemClassification.useful, "", 1, "Non-elemental summon"
    ),
    "Summon: Neo Bahamut": FFVIIRItemData(
        "Summon: Neo Bahamut", ItemClassification.useful, "", 1, "Powerful non-elemental summon"
    ),
    "Summon: Chocobo & Moogle": FFVIIRItemData(
        "Summon: Chocobo & Moogle", ItemClassification.useful, "", 1, "Wind summon"
    ),
    "Summon: Fat Chocobo": FFVIIRItemData(
        "Summon: Fat Chocobo", ItemClassification.useful, "", 1, "Non-elemental summon"
    ),
    "Summon: Leviathan": FFVIIRItemData(
        "Summon: Leviathan", ItemClassification.useful, "", 1, "Water summon"
    ),
}


# ============================================================================
# FILLER ITEMS - Consumables and currency
# ============================================================================
FILLER_ITEMS: Dict[str, FFVIIRItemData] = {
    # Recovery items
    "Potion": FFVIIRItemData(
        "Potion", ItemClassification.filler, "IT_potion", 20, "Restores some HP"
    ),
    "Hi-Potion": FFVIIRItemData(
        "Hi-Potion", ItemClassification.filler, "IT_hpotion", 15, "Restores moderate HP"
    ),
    "Mega-Potion": FFVIIRItemData(
        "Mega-Potion", ItemClassification.filler, "IT_mpotion", 10, "Restores party HP"
    ),
    "Ether": FFVIIRItemData(
        "Ether", ItemClassification.filler, "", 15, "Restores some MP"
    ),
    "Turbo Ether": FFVIIRItemData(
        "Turbo Ether", ItemClassification.filler, "", 8, "Restores more MP"
    ),
    "Elixir": FFVIIRItemData(
        "Elixir", ItemClassification.filler, "", 5, "Fully restores HP and MP"
    ),
    "Phoenix Down": FFVIIRItemData(
        "Phoenix Down", ItemClassification.filler, "IT_phenxtal", 10, "Revives KO'd ally"
    ),
    
    # Status items
    "Antidote": FFVIIRItemData(
        "Antidote", ItemClassification.filler, "IT_poisona", 10, "Cures Poison"
    ),
    "Echo Mist": FFVIIRItemData(
        "Echo Mist", ItemClassification.filler, "IT_echo", 8, "Cures Silence"
    ),
    "Soft": FFVIIRItemData(
        "Soft", ItemClassification.filler, "IT_soft", 5, "Cures Petrify"
    ),
    "Maiden's Kiss": FFVIIRItemData(
        "Maiden's Kiss", ItemClassification.filler, "IT_maidenOfKiss", 5, "Cures Toad"
    ),
    "Remedy": FFVIIRItemData(
        "Remedy", ItemClassification.filler, "", 8, "Cures most status effects"
    ),
    
    # Attack items
    "Grenade": FFVIIRItemData(
        "Grenade", ItemClassification.filler, "IT_grenade", 15, "Deals fire damage"
    ),
    "Mega Grenade": FFVIIRItemData(
        "Mega Grenade", ItemClassification.filler, "IT_supergrenade", 8, "Deals heavy fire damage"
    ),
    "Molotov": FFVIIRItemData(
        "Molotov", ItemClassification.filler, "IT_molotov", 10, "Fire attack item"
    ),
    
    # Buff items
    "Speed Drink": FFVIIRItemData(
        "Speed Drink", ItemClassification.filler, "IT_speed", 8, "Increases speed"
    ),
    "Stimulant": FFVIIRItemData(
        "Stimulant", ItemClassification.filler, "IT_stimulant", 10, "Increases attack"
    ),
    
    # Currency
    "Gil Bundle (500)": FFVIIRItemData(
        "Gil Bundle (500)", ItemClassification.filler, "", 35, "500 Gil"
    ),
    "Gil Bundle (1000)": FFVIIRItemData(
        "Gil Bundle (1000)", ItemClassification.filler, "", 30, "1000 Gil"
    ),
    "Gil Bundle (5000)": FFVIIRItemData(
        "Gil Bundle (5000)", ItemClassification.filler, "", 25, "5000 Gil"
    ),
}


# ============================================================================
# TRAP ITEMS - Negative effects
# ============================================================================
TRAP_ITEMS: Dict[str, FFVIIRItemData] = {
    "Poison Trap": FFVIIRItemData(
        "Poison Trap", ItemClassification.trap, "", 5, "Inflicts poison on party"
    ),
    "Confusion Trap": FFVIIRItemData(
        "Confusion Trap", ItemClassification.trap, "", 3, "Inflicts confusion"
    ),
    "Gil Loss": FFVIIRItemData(
        "Gil Loss", ItemClassification.trap, "", 8, "Lose some Gil"
    ),
    "Enemy Encounter": FFVIIRItemData(
        "Enemy Encounter", ItemClassification.trap, "", 5, "Triggers a random battle"
    ),
}
