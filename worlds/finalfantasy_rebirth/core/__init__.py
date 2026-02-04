"""
Core Module for Final Fantasy VII: Rebirth
================================================================

This package contains the main interface modules that provide
the public API for the Archipelago world. These modules serve
as facades over the internal data and randomization packages.

Modules:
    - items: Item definitions and lookup functions
    - locations: Location definitions and lookup functions
    - regions: Region builder for world graph
    - options: Randomizer configuration options

The core package aggregates these modules and re-exports their
primary interfaces for convenient access.

Example:
    from .core import item_table, location_table, FFVIIRebirthOptions
    from .core import build_regions
"""

# Item interface
from .items import (
    item_table,
    FFVIIRItemData,
    get_all_items,
    get_progression_items,
    get_useful_items,
    get_filler_items,
    get_trap_items,
    lookup_item,
)

# Location interface
from .locations import (
    location_table,
    FFVIIRLocationData,
    get_all_locations,
    get_locations_by_region,
    get_locations_by_type,
    get_location_data,
    get_all_regions,
)

# Region builder
from .regions import (
    RegionBuilder,
    build_regions,
)

# Options
from .options import (
    FFVIIRebirthOptions,
    ChapterProgression,
    PartyMemberRandomization,
    ColosseumIncluded,
    VRSimulatorIncluded,
    SummonRandomization,
    MateriaRandomization,
    EquipmentRandomization,
    QuestsIncluded,
    MinigamesIncluded,
    TrapItems,
    TrapPercentage,
    StartingGil,
    StartingLevel,
    DeathLink,
    GoalType,
    RequiredBossCount,
)

__all__ = [
    # Items
    "item_table",
    "FFVIIRItemData",
    "get_all_items",
    "get_progression_items",
    "get_useful_items",
    "get_filler_items",
    "get_trap_items",
    "lookup_item",
    # Locations
    "location_table",
    "FFVIIRLocationData",
    "get_all_locations",
    "get_locations_by_region",
    "get_locations_by_type",
    "get_location_data",
    "get_all_regions",
    # Regions
    "RegionBuilder",
    "build_regions",
    # Options
    "FFVIIRebirthOptions",
    "ChapterProgression",
    "PartyMemberRandomization",
    "ColosseumIncluded",
    "VRSimulatorIncluded",
    "SummonRandomization",
    "MateriaRandomization",
    "EquipmentRandomization",
    "QuestsIncluded",
    "MinigamesIncluded",
    "TrapItems",
    "TrapPercentage",
    "StartingGil",
    "StartingLevel",
    "DeathLink",
    "GoalType",
    "RequiredBossCount",
]
