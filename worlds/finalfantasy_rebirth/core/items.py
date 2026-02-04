"""
Item Definitions for Final Fantasy VII: Rebirth
================================================================

This module provides the public interface for accessing item data.
It acts as a facade over the internal data structures, providing
a clean API for the main world class and external consumers.

The actual item definitions are stored in:
    - data/item_tables.py: Static item definitions by category
    - randomization/item_pool.py: Dynamic item pool generation

Item Classifications (Archipelago standard):
    - Progression: Required to complete the game or access new areas
    - Useful: Helpful but not required (equipment, materia)
    - Filler: Common items to fill remaining slots (consumables, gil)
    - Trap: Optional negative effect items

Exported Functions:
    - get_all_items(): Returns complete item table
    - get_progression_items(): Returns list of progression item names
    - get_useful_items(): Returns list of useful item names
    - get_filler_items(): Returns list of filler item names
    - get_trap_items(): Returns list of trap item names
    - lookup_item(name): Returns item data for a specific item

Example:
    from .items import item_table, get_progression_items
    
    # Check if an item exists
    if "Chocobo License" in item_table:
        print("Chocobo License is available")
    
    # Get all progression items
    for item_name in get_progression_items():
        print(f"Progression: {item_name}")
"""
from typing import Dict, List, Optional
from BaseClasses import ItemClassification

from ..data import FFVIIRItemData
from ..randomization import build_item_table, get_items_by_classification, get_item_data

# Build the main item table on module load
item_table: Dict[str, FFVIIRItemData] = build_item_table(
    include_traps=False,
    include_game_data=True
)


def get_all_items() -> Dict[str, FFVIIRItemData]:
    """Get the complete item table."""
    return item_table


def get_progression_items() -> List[str]:
    """Get all progression item names."""
    return get_items_by_classification(item_table, ItemClassification.progression)


def get_useful_items() -> List[str]:
    """Get all useful item names."""
    return get_items_by_classification(item_table, ItemClassification.useful)


def get_filler_items() -> List[str]:
    """Get all filler item names."""
    return get_items_by_classification(item_table, ItemClassification.filler)


def get_trap_items() -> List[str]:
    """Get all trap item names."""
    return get_items_by_classification(item_table, ItemClassification.trap)


def lookup_item(item_name: str) -> Optional[FFVIIRItemData]:
    """Look up item data by name."""
    return get_item_data(item_table, item_name)


# Re-export for backwards compatibility
__all__ = [
    "item_table",
    "FFVIIRItemData",
    "get_all_items",
    "get_progression_items",
    "get_useful_items",
    "get_filler_items",
    "get_trap_items",
    "lookup_item",
    "get_items_by_classification",
]
