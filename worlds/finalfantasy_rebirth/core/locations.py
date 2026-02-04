"""
Location Definitions for Final Fantasy VII: Rebirth
================================================================

This module provides the public interface for accessing location data.
Locations represent "checks" - places where players can receive items
in the randomized game.

The actual location definitions are stored in:
    - data/location_tables.py: Static location definitions by type
    - randomization/location_generator.py: Dynamic location generation

Location Types:
    - story: Main story progression points
    - boss: Boss fight completions
    - colosseum: Colosseum battle completions
    - summon_battle: VR summon battles
    - vr_battle: VR combat simulations
    - territory: World map territory encounters
    - quest: Side quest completions
    - minigame: Minigame completions (Queen's Blood, etc.)

Exported Functions:
    - get_all_locations(): Returns complete location table
    - get_locations_by_region(region): Filter by region name
    - get_locations_by_type(type): Filter by location type
    - get_location_data(name): Get data for specific location
    - get_all_regions(): Get set of all region names

Example:
    from .locations import location_table, get_locations_by_region
    
    # Get all Gold Saucer locations
    gold_saucer_checks = get_locations_by_region("Gold Saucer")
    print(f"Found {len(gold_saucer_checks)} checks in Gold Saucer")
"""
from typing import Dict, List, Optional, Set

from ..data import FFVIIRLocationData, REGIONS, REGION_REQUIREMENTS
from ..randomization import (
    build_location_table,
    get_locations_by_region as _get_locations_by_region,
    get_locations_by_type as _get_locations_by_type,
    get_location_data as _get_location_data,
    get_all_regions as _get_all_regions,
)

# Build the main location table on module load
location_table: Dict[str, FFVIIRLocationData] = build_location_table(
    include_colosseum=True,
    include_territories=True,
    include_quests=True,
    include_minigames=True
)


def get_all_locations() -> Dict[str, FFVIIRLocationData]:
    """Get the complete location table."""
    return location_table


def get_locations_by_region(region: str) -> List[str]:
    """Get all location names in a specific region."""
    return _get_locations_by_region(location_table, region)


def get_locations_by_type(loc_type: str) -> List[str]:
    """Get all location names of a specific type."""
    return _get_locations_by_type(location_table, loc_type)


def get_location_data(location_name: str) -> Optional[FFVIIRLocationData]:
    """Get location data by name."""
    return _get_location_data(location_table, location_name)


def get_all_regions() -> Set[str]:
    """Get all unique regions from location table."""
    return _get_all_regions(location_table)


# Re-export for backwards compatibility
__all__ = [
    "location_table",
    "FFVIIRLocationData",
    "REGIONS",
    "REGION_REQUIREMENTS",
    "get_all_locations",
    "get_locations_by_region",
    "get_locations_by_type",
    "get_location_data",
    "get_all_regions",
]
