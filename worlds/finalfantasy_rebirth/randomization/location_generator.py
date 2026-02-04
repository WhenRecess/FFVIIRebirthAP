"""
Location Generator for Final Fantasy VII: Rebirth
================================================================

This module provides the LocationGenerator class for constructing
the complete location table used in randomization. It combines:

    1. Static location tables from data/location_tables.py
    2. Dynamically generated locations from game data exports:
       - Colosseum battles (from Colosseum.json)
       - Territory encounters (from EnemyTerritory.json)

Key Components:
    LocationGenerator
        Builder class with chainable methods for configuring locations.
        Methods: with_story_locations(), with_vr_summon_battles(),
                 with_quest_locations(), with_minigame_locations(),
                 with_colosseum_from_game_data(), 
                 with_territories_from_game_data()
    
    build_location_table()
        Convenience function that builds a standard location table
        with common configuration options.
    
    get_locations_by_region()
        Filter locations by their assigned region.
    
    get_locations_by_type()
        Filter locations by their type (story, boss, colosseum, etc.).

Region Mapping:
    Dynamically generated locations are assigned to regions based on
    their IDs:
    - COL20/COL30 colosseum battles -> Gold Saucer
    - terVR_* territories -> VR Simulator
    - ter01/ter02 -> Grasslands
    - ter03/ter04 -> Junon
    - etc.
"""
from typing import Dict, List, Optional, Set

from ..data import (
    STORY_LOCATIONS,
    VR_SUMMON_BATTLES,
    QUEST_LOCATIONS,
    MINIGAME_LOCATIONS,
    FFVIIRLocationData,
    get_game_data,
)


class LocationGenerator:
    """Generator class for constructing the location table."""
    
    def __init__(self):
        self._locations: Dict[str, FFVIIRLocationData] = {}
    
    def with_story_locations(self) -> "LocationGenerator":
        """Add story progression locations."""
        self._locations.update(STORY_LOCATIONS)
        return self
    
    def with_vr_summon_battles(self) -> "LocationGenerator":
        """Add VR summon battle locations."""
        self._locations.update(VR_SUMMON_BATTLES)
        return self
    
    def with_quest_locations(self) -> "LocationGenerator":
        """Add side quest locations."""
        self._locations.update(QUEST_LOCATIONS)
        return self
    
    def with_minigame_locations(self) -> "LocationGenerator":
        """Add minigame locations."""
        self._locations.update(MINIGAME_LOCATIONS)
        return self
    
    def with_colosseum_from_game_data(self) -> "LocationGenerator":
        """Generate colosseum battle locations from game data."""
        game_data = get_game_data()
        
        for battle_id, battle in game_data.colosseum_battles.items():
            # Skip tutorial battles - they're not real checks
            if battle.tier == "Tutorial":
                continue
            
            # Determine region based on colosseum type
            if battle.colosseum in ["COL20", "COL30"]:
                region = "Gold Saucer"
            else:
                region = "VR Simulator"
            
            self._locations[battle.display_name] = FFVIIRLocationData(
                display_name=battle.display_name,
                region=region,
                location_type="colosseum",
                game_id=battle.battle_id,
                description=f"Complete {battle.display_name}"
            )
        
        return self
    
    def with_territories_from_game_data(self) -> "LocationGenerator":
        """Generate territory encounter locations from game data."""
        game_data = get_game_data()
        
        # Map territory prefixes to regions
        region_map = {
            "ter01": "Grasslands",
            "ter02": "Grasslands", 
            "ter03": "Junon",
            "ter04": "Junon",
            "ter05": "Costa del Sol",
            "ter06": "Corel",
            "ter07": "Gongaga",
            "ter08": "Cosmo Canyon",
            "ter09": "Nibelheim",
            "terVR": "VR Simulator",
            "territ": "Unknown",  # Generic territory prefix
        }
        
        for ter_id, territory in game_data.territories.items():
            # Determine region from prefix
            region = "VR Simulator"  # Default for most battles
            for prefix, reg in region_map.items():
                if ter_id.startswith(prefix):
                    region = reg
                    break
            
            # Determine location type
            if ter_id.startswith("terVR_"):
                loc_type = "vr_battle"
            else:
                loc_type = "territory"
            
            self._locations[territory.display_name] = FFVIIRLocationData(
                display_name=territory.display_name,
                region=region,
                location_type=loc_type,
                game_id=ter_id,
                description=f"Clear {territory.display_name}"
            )
        
        return self
    
    def build(self) -> Dict[str, FFVIIRLocationData]:
        """Build and return the complete location table."""
        return self._locations.copy()


def build_location_table(
    include_colosseum: bool = True,
    include_territories: bool = True,
    include_quests: bool = True,
    include_minigames: bool = True
) -> Dict[str, FFVIIRLocationData]:
    """
    Build the complete location table by combining all sources.
    
    Args:
        include_colosseum: Whether to include colosseum battles
        include_territories: Whether to include territory encounters
        include_quests: Whether to include side quests
        include_minigames: Whether to include minigames
    
    Returns:
        Complete location table dictionary
    """
    generator = LocationGenerator()
    generator.with_story_locations()
    generator.with_vr_summon_battles()
    
    if include_quests:
        generator.with_quest_locations()
    
    if include_minigames:
        generator.with_minigame_locations()
    
    if include_colosseum:
        try:
            generator.with_colosseum_from_game_data()
        except Exception as e:
            print(f"Warning: Could not generate colosseum locations: {e}")
    
    if include_territories:
        try:
            generator.with_territories_from_game_data()
        except Exception as e:
            print(f"Warning: Could not generate territory locations: {e}")
    
    return generator.build()


def get_locations_by_region(
    location_table: Dict[str, FFVIIRLocationData],
    region: str
) -> List[str]:
    """Get all location names in a specific region."""
    return [
        name for name, data in location_table.items() 
        if data.region == region
    ]


def get_locations_by_type(
    location_table: Dict[str, FFVIIRLocationData],
    loc_type: str
) -> List[str]:
    """Get all location names of a specific type."""
    return [
        name for name, data in location_table.items() 
        if data.location_type == loc_type
    ]


def get_location_data(
    location_table: Dict[str, FFVIIRLocationData],
    location_name: str
) -> Optional[FFVIIRLocationData]:
    """Get location data by name."""
    return location_table.get(location_name)


def get_all_regions(location_table: Dict[str, FFVIIRLocationData]) -> Set[str]:
    """Get all unique regions from location table."""
    return {data.region for data in location_table.values()}
