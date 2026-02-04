"""
Region Data Tables for Final Fantasy VII: Rebirth
================================================================

This module defines the game's regions and their access requirements.
Regions form the structure of the Archipelago world graph.

Data Structures:
    REGIONS: List[str]
        Complete list of all region names in the game.
        The "Menu" region is the starting point.
    
    REGION_REQUIREMENTS: Dict[str, List[str]]
        Maps region names to lists of required items.
        Empty list means the region is accessible from start.
        Multiple items means ALL are required (AND logic).
    
    CHAPTER_REGIONS: Dict[int, List[str]]
        Maps chapter numbers to regions that become available.
        Used for determining when locations unlock.

Region Progression:
    Chapter 1:  Kalm
    Chapter 2:  Grasslands
    Chapter 3:  Grasslands (continued)
    Chapter 4:  Junon
    Chapter 5:  Junon (continued)
    Chapter 6:  Costa del Sol
    Chapter 7:  Corel, Gold Saucer
    Chapter 8:  Gongaga
    Chapter 9:  Gongaga (continued)
    Chapter 10: Cosmo Canyon
    Chapter 11: Nibelheim
    Chapter 12: Mt. Nibel
    Chapter 13: Temple of the Ancients
    Chapter 14: Forgotten Capital

Special Regions:
    - VR Simulator: Accessible with "VR Simulator Access" item
    - Unknown: Catch-all for unmapped locations
"""
from typing import Dict, List, Optional


# ============================================================================
# REGION DEFINITIONS
# ============================================================================
REGIONS: List[str] = [
    "Menu",               # Starting point
    "Kalm",               # Chapter 1
    "Grasslands",         # Open world region
    "Junon",              # Chapter 4-5
    "Costa del Sol",      # Beach area
    "Corel",              # Mining town
    "Gold Saucer",        # Entertainment complex (includes Colosseum)
    "Gongaga",            # Destroyed reactor town
    "Cosmo Canyon",       # Red XIII's home
    "Nibelheim",          # Cloud/Tifa's hometown
    "Mt. Nibel",          # Mountain dungeon
    "Temple of the Ancients",
    "Forgotten Capital",
    "VR Simulator",       # Chadley's VR missions
    "Unknown",            # Catch-all for unmapped locations
]


# ============================================================================
# REGION REQUIREMENTS - Items needed to access each region
# ============================================================================
REGION_REQUIREMENTS: Dict[str, List[str]] = {
    "Menu": [],
    "Kalm": [],
    "Grasslands": ["Chapter 1 Complete"],
    "Junon": ["Chapter 3 Complete"],
    "Costa del Sol": ["Chapter 4 Complete"],
    "Corel": ["Chapter 5 Complete"],
    "Gold Saucer": ["Chapter 5 Complete"],
    "Gongaga": ["Chapter 7 Complete"],
    "Cosmo Canyon": ["Chapter 9 Complete"],
    "Nibelheim": ["Chapter 10 Complete"],
    "Mt. Nibel": ["Chapter 11 Complete"],
    "Temple of the Ancients": ["Chapter 12 Complete"],
    "Forgotten Capital": ["Chapter 13 Complete"],
    "VR Simulator": ["VR Simulator Access"],  # Can be accessed from any Chadley terminal
    "Unknown": [],
}


# ============================================================================
# CHAPTER TO REGION MAPPING
# ============================================================================
CHAPTER_REGIONS: Dict[int, List[str]] = {
    1: ["Kalm"],
    2: ["Grasslands"],
    3: ["Grasslands"],
    4: ["Junon"],
    5: ["Junon"],
    6: ["Costa del Sol"],
    7: ["Corel", "Gold Saucer"],
    8: ["Gongaga"],
    9: ["Gongaga"],
    10: ["Cosmo Canyon"],
    11: ["Nibelheim"],
    12: ["Mt. Nibel"],
    13: ["Temple of the Ancients"],
    14: ["Forgotten Capital"],
}


def get_region_chapter(region: str) -> Optional[int]:
    """Get the chapter number that unlocks a given region."""
    for chapter, regions in CHAPTER_REGIONS.items():
        if region in regions:
            return chapter
    return None


def get_regions_for_chapter(chapter: int) -> List[str]:
    """Get all regions available at a given chapter."""
    regions = []
    for ch in range(1, chapter + 1):
        regions.extend(CHAPTER_REGIONS.get(ch, []))
    return list(set(regions))


def get_region_connections() -> Dict[str, List[str]]:
    """
    Get a mapping of region connections for building the region graph.
    
    Returns dict where key is source region and value is list of directly
    connected destination regions.
    """
    # For now, all regions connect through Menu (hub-and-spoke)
    # This can be expanded for more realistic connections
    connections = {
        "Menu": [r for r in REGIONS if r != "Menu"],
    }
    
    # Add some logical connections between adjacent regions
    adjacent_regions = [
        ("Grasslands", "Junon"),
        ("Junon", "Costa del Sol"),
        ("Costa del Sol", "Corel"),
        ("Corel", "Gold Saucer"),
        ("Gongaga", "Cosmo Canyon"),
        ("Cosmo Canyon", "Nibelheim"),
        ("Nibelheim", "Mt. Nibel"),
    ]
    
    for region_a, region_b in adjacent_regions:
        if region_a not in connections:
            connections[region_a] = []
        if region_b not in connections:
            connections[region_b] = []
        connections[region_a].append(region_b)
        connections[region_b].append(region_a)
    
    return connections
