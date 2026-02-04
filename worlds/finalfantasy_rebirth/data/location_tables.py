"""
Location Data Tables for Final Fantasy VII: Rebirth
================================================================

This module contains all static location definitions organized by type.
Locations represent "checks" - places where randomized items can be found.

Location Categories:
    STORY_LOCATIONS
        Main story progression points and boss fights.
        These are always included in randomization.
    
    VR_SUMMON_BATTLES
        Chadley's VR summon challenge battles.
        Defeating a summon in VR unlocks it for use.
    
    QUEST_LOCATIONS
        Side quest completion rewards.
        Optional content that can be toggled via options.
    
    MINIGAME_LOCATIONS
        Minigame completion rewards (Queen's Blood, Chocobo Racing, etc.).
        Optional content that can be toggled via options.

Dynamic Locations:
    Additional locations are generated from game data in
    randomization/location_generator.py:
    - Colosseum battles (from Colosseum.json)
    - Territory encounters (from EnemyTerritory.json)

Location Data Structure (FFVIIRLocationData):
    - display_name: Human-readable name shown to players
    - region: Which game region contains this location
    - location_type: Category string ("story", "boss", "quest", etc.)
    - game_id: Original game's internal ID (if applicable)
    - description: Brief description of how to complete this check
"""
from typing import Dict, NamedTuple


class FFVIIRLocationData(NamedTuple):
    """Data structure for an Archipelago location."""
    display_name: str
    region: str
    location_type: str
    game_id: str = ""  # Original game ID
    description: str = ""


# ============================================================================
# STORY LOCATIONS - Main story progression checks
# ============================================================================
STORY_LOCATIONS: Dict[str, FFVIIRLocationData] = {
    # Chapter 1 - Kalm
    "Story: Kalm Flashback Complete": FFVIIRLocationData(
        "Story: Kalm Flashback Complete", "Kalm", "story", "", 
        "Complete the Nibelheim flashback"
    ),
    
    # Chapter 2 - Grasslands Introduction
    "Story: Reach Chocobo Ranch": FFVIIRLocationData(
        "Story: Reach Chocobo Ranch", "Grasslands", "story", "", 
        "Arrive at Bill's Ranch"
    ),
    "Story: First Chocobo Caught": FFVIIRLocationData(
        "Story: First Chocobo Caught", "Grasslands", "story", "", 
        "Catch your first chocobo"
    ),
    
    # Chapter 3 - Grasslands Exploration
    "Boss: Midgardsormr": FFVIIRLocationData(
        "Boss: Midgardsormr", "Grasslands", "boss", "", 
        "Defeat the giant serpent"
    ),
    
    # Chapter 4-5 - Junon
    "Story: Arrive at Junon": FFVIIRLocationData(
        "Story: Arrive at Junon", "Junon", "story", "", 
        "Enter Junon"
    ),
    "Boss: Bottomswell": FFVIIRLocationData(
        "Boss: Bottomswell", "Junon", "boss", "", 
        "Defeat Bottomswell"
    ),
    "Story: Junon Parade": FFVIIRLocationData(
        "Story: Junon Parade", "Junon", "story", "", 
        "Complete the Junon parade sequence"
    ),
    
    # Chapter 6 - Costa del Sol
    "Story: Arrive at Costa del Sol": FFVIIRLocationData(
        "Story: Arrive at Costa del Sol", "Costa del Sol", "story", "", 
        "Arrive at Costa del Sol"
    ),
    
    # Chapter 7 - Corel / Gold Saucer
    "Story: Arrive at Corel": FFVIIRLocationData(
        "Story: Arrive at Corel", "Corel", "story", "", 
        "Enter North Corel"
    ),
    "Story: Gold Saucer First Visit": FFVIIRLocationData(
        "Story: Gold Saucer First Visit", "Gold Saucer", "story", "", 
        "First visit to Gold Saucer"
    ),
    "Boss: Dyne": FFVIIRLocationData(
        "Boss: Dyne", "Corel", "boss", "", 
        "Defeat Dyne in Corel Prison"
    ),
    
    # Chapter 8-9 - Gongaga
    "Story: Arrive at Gongaga": FFVIIRLocationData(
        "Story: Arrive at Gongaga", "Gongaga", "story", "", 
        "Arrive at Gongaga village"
    ),
    
    # Chapter 10 - Cosmo Canyon
    "Story: Arrive at Cosmo Canyon": FFVIIRLocationData(
        "Story: Arrive at Cosmo Canyon", "Cosmo Canyon", "story", "", 
        "Arrive at Cosmo Canyon"
    ),
    "Boss: Gi Nattak": FFVIIRLocationData(
        "Boss: Gi Nattak", "Cosmo Canyon", "boss", "", 
        "Defeat Gi Nattak in Cave of the Gi"
    ),
    
    # Chapter 11-12 - Nibelheim
    "Story: Return to Nibelheim": FFVIIRLocationData(
        "Story: Return to Nibelheim", "Nibelheim", "story", "", 
        "Return to Nibelheim"
    ),
    "Boss: Lost Number": FFVIIRLocationData(
        "Boss: Lost Number", "Nibelheim", "boss", "", 
        "Defeat Lost Number in Shinra Mansion"
    ),
    
    # Chapter 13-14 - Endgame
    "Story: Temple of the Ancients": FFVIIRLocationData(
        "Story: Temple of the Ancients", "Temple of the Ancients", "story", "", 
        "Explore the Temple"
    ),
    "Boss: Red Dragon": FFVIIRLocationData(
        "Boss: Red Dragon", "Temple of the Ancients", "boss", "", 
        "Defeat Red Dragon"
    ),
    "Boss: Demon Wall": FFVIIRLocationData(
        "Boss: Demon Wall", "Temple of the Ancients", "boss", "", 
        "Defeat Demon Wall"
    ),
}


# ============================================================================
# VR SUMMON BATTLE LOCATIONS
# ============================================================================
VR_SUMMON_BATTLES: Dict[str, FFVIIRLocationData] = {
    "VR: Summon - Ifrit": FFVIIRLocationData(
        "VR: Summon - Ifrit", "VR Simulator", "summon_battle", 
        "COL30_SUMMON_Ifrit_Free_vr", "Defeat Ifrit"
    ),
    "VR: Summon - Shiva": FFVIIRLocationData(
        "VR: Summon - Shiva", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Shiva_Free_vr", "Defeat Shiva"
    ),
    "VR: Summon - Titan": FFVIIRLocationData(
        "VR: Summon - Titan", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Taitan_Free_vr", "Defeat Titan"
    ),
    "VR: Summon - Odin": FFVIIRLocationData(
        "VR: Summon - Odin", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Odin_Free_vr", "Defeat Odin"
    ),
    "VR: Summon - Phoenix": FFVIIRLocationData(
        "VR: Summon - Phoenix", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Phoenix_Free_vr", "Defeat Phoenix"
    ),
    "VR: Summon - Alexander": FFVIIRLocationData(
        "VR: Summon - Alexander", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Alexander_Free_vr", "Defeat Alexander"
    ),
    "VR: Summon - Kujata": FFVIIRLocationData(
        "VR: Summon - Kujata", "VR Simulator", "summon_battle",
        "COL30_SUMMON_Kjata_Free_vr", "Defeat Kujata"
    ),
    "VR: Summon - Neo Bahamut": FFVIIRLocationData(
        "VR: Summon - Neo Bahamut", "VR Simulator", "summon_battle",
        "COL30_SUMMON_NeoBahamut_Free_vr", "Defeat Neo Bahamut"
    ),
}


# ============================================================================
# QUEST LOCATIONS
# ============================================================================
QUEST_LOCATIONS: Dict[str, FFVIIRLocationData] = {
    # Grasslands quests
    "Quest: Where the Wind Blows": FFVIIRLocationData(
        "Quest: Where the Wind Blows", "Grasslands", "quest", "", 
        "Complete 'Where the Wind Blows'"
    ),
    "Quest: Flowers from the Hill": FFVIIRLocationData(
        "Quest: Flowers from the Hill", "Grasslands", "quest", "", 
        "Gather flowers for the farm"
    ),
    "Quest: When Words Won't Do": FFVIIRLocationData(
        "Quest: When Words Won't Do", "Grasslands", "quest", "", 
        "Help with monster problems"
    ),
    
    # Junon quests
    "Quest: The Hardest Sell": FFVIIRLocationData(
        "Quest: The Hardest Sell", "Junon", "quest", "", 
        "Help the salesman"
    ),
    
    # Costa del Sol quests
    "Quest: Stupid Cupid": FFVIIRLocationData(
        "Quest: Stupid Cupid", "Costa del Sol", "quest", "", 
        "Help the lovesick vacationer"
    ),
    
    # Gold Saucer quests
    "Quest: Gold Saucer Date": FFVIIRLocationData(
        "Quest: Gold Saucer Date", "Gold Saucer", "quest", "", 
        "Go on a date at Gold Saucer"
    ),
    
    # Cosmo Canyon quests
    "Quest: Guardian of the Canyon": FFVIIRLocationData(
        "Quest: Guardian of the Canyon", "Cosmo Canyon", "quest", "", 
        "Help Red XIII"
    ),
}


# ============================================================================
# MINIGAME LOCATIONS
# ============================================================================
MINIGAME_LOCATIONS: Dict[str, FFVIIRLocationData] = {
    # Fort Condor
    "Fort Condor: First Victory": FFVIIRLocationData(
        "Fort Condor: First Victory", "Junon", "minigame", "", 
        "Win your first Fort Condor match"
    ),
    "Fort Condor: Master": FFVIIRLocationData(
        "Fort Condor: Master", "Junon", "minigame", "", 
        "Defeat all Fort Condor opponents"
    ),
    
    # Queen's Blood (card game)
    "Queen's Blood: First Win": FFVIIRLocationData(
        "Queen's Blood: First Win", "Kalm", "minigame", "", 
        "Win your first Queen's Blood match"
    ),
    "Queen's Blood: Champion": FFVIIRLocationData(
        "Queen's Blood: Champion", "Gold Saucer", "minigame", "", 
        "Become Queen's Blood champion"
    ),
    
    # Chocobo Racing
    "Chocobo Racing: First Win": FFVIIRLocationData(
        "Chocobo Racing: First Win", "Gold Saucer", "minigame", "", 
        "Win your first chocobo race"
    ),
    "Chocobo Racing: S-Class": FFVIIRLocationData(
        "Chocobo Racing: S-Class", "Gold Saucer", "minigame", "", 
        "Win an S-Class race"
    ),
    
    # Piano minigame
    "Piano: Performance Perfect": FFVIIRLocationData(
        "Piano: Performance Perfect", "Nibelheim", "minigame", "", 
        "Perfect score on piano"
    ),
}
