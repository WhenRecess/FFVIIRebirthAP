"""
Item Pool Builder for Final Fantasy VII: Rebirth
================================================================

This module provides the ItemPoolBuilder class for constructing
the complete item pool used in randomization. It combines:

    1. Static item tables from data/item_tables.py
    2. Dynamically generated equipment from game data exports

Key Components:
    ItemPoolBuilder
        Builder class with chainable methods for configuring the pool.
        Methods: with_progression_items(), with_useful_items(),
                 with_filler_items(), with_traps(), 
                 with_equipment_from_game_data()
    
    build_item_table()
        Convenience function that builds a standard item table
        with common configuration options.
    
    get_items_by_classification()
        Filter items by their Archipelago classification.
    
    get_item_data()
        Look up a specific item's data by name.

Usage:
    # Standard usage via convenience function
    from .item_pool import build_item_table
    items = build_item_table(include_traps=False)
    
    # Custom configuration via builder
    from .item_pool import ItemPoolBuilder
    items = (ItemPoolBuilder()
        .with_progression_items()
        .with_useful_items()
        .with_filler_items()
        .with_equipment_from_game_data()
        .build())
"""
from typing import Dict, List, Optional
from BaseClasses import ItemClassification

from ..data import (
    PROGRESSION_ITEMS,
    USEFUL_ITEMS,
    SUMMON_MATERIA,
    FILLER_ITEMS,
    TRAP_ITEMS,
    FFVIIRItemData,
    get_game_data,
    ItemType,
)
from ..data.game_loader import get_item_display_name


class ItemPoolBuilder:
    """Builder class for constructing the item pool."""
    
    def __init__(self):
        self._items: Dict[str, FFVIIRItemData] = {}
        self._include_traps = False
        self._include_equipment = True
    
    def with_progression_items(self) -> "ItemPoolBuilder":
        """Add all progression items to the pool."""
        self._items.update(PROGRESSION_ITEMS)
        return self
    
    def with_useful_items(self) -> "ItemPoolBuilder":
        """Add all static useful items to the pool."""
        self._items.update(USEFUL_ITEMS)
        self._items.update(SUMMON_MATERIA)
        return self
    
    def with_filler_items(self) -> "ItemPoolBuilder":
        """Add all filler items to the pool."""
        self._items.update(FILLER_ITEMS)
        return self
    
    def with_traps(self, include: bool = True) -> "ItemPoolBuilder":
        """Optionally include trap items."""
        self._include_traps = include
        if include:
            self._items.update(TRAP_ITEMS)
        return self
    
    def with_equipment_from_game_data(self) -> "ItemPoolBuilder":
        """Generate equipment items from extracted game data."""
        game_data = get_game_data()
        
        # Accessories
        for item in game_data.get_items_by_type(ItemType.ACCESSORY):
            display = get_item_display_name(item.game_id)
            self._items[display] = FFVIIRItemData(
                display, 
                ItemClassification.useful,
                item.game_id, 
                1, 
                "Accessory equipment"
            )
        
        # Armor
        for item in game_data.get_items_by_type(ItemType.ARMOR):
            display = get_item_display_name(item.game_id)
            self._items[display] = FFVIIRItemData(
                display,
                ItemClassification.useful,
                item.game_id,
                1,
                "Armor equipment"
            )
        
        # Weapons
        for item in game_data.get_items_by_type(ItemType.WEAPON):
            display = get_item_display_name(item.game_id)
            self._items[display] = FFVIIRItemData(
                display,
                ItemClassification.useful,
                item.game_id,
                1,
                "Weapon"
            )
        
        # Materia
        for item in game_data.get_items_by_type(ItemType.MATERIA):
            display = get_item_display_name(item.game_id)
            self._items[display] = FFVIIRItemData(
                display,
                ItemClassification.useful,
                item.game_id,
                1,
                "Materia"
            )
        
        return self
    
    def build(self) -> Dict[str, FFVIIRItemData]:
        """Build and return the complete item table."""
        return self._items.copy()


def build_item_table(
    include_traps: bool = False,
    include_game_data: bool = True
) -> Dict[str, FFVIIRItemData]:
    """
    Build the complete item table by combining all categories.
    
    Args:
        include_traps: Whether to include trap items
        include_game_data: Whether to generate items from game data
    
    Returns:
        Complete item table dictionary
    """
    builder = ItemPoolBuilder()
    builder.with_progression_items()
    builder.with_useful_items()
    builder.with_filler_items()
    
    if include_traps:
        builder.with_traps()
    
    if include_game_data:
        try:
            builder.with_equipment_from_game_data()
        except Exception as e:
            print(f"Warning: Could not load equipment from game data: {e}")
    
    return builder.build()


def get_items_by_classification(
    item_table: Dict[str, FFVIIRItemData],
    classification: ItemClassification
) -> List[str]:
    """Get all item names with a specific classification."""
    return [
        name for name, data in item_table.items() 
        if data.classification == classification
    ]


def get_item_data(
    item_table: Dict[str, FFVIIRItemData],
    item_name: str
) -> Optional[FFVIIRItemData]:
    """Get item data by name."""
    return item_table.get(item_name)
