"""
Item definitions for Final Fantasy VII: Rebirth Archipelago World.
"""

import csv
from typing import Dict, NamedTuple
from BaseClasses import Item, ItemClassification


class ItemData(NamedTuple):
    """Data structure for an item."""
    code: int
    classification: ItemClassification = ItemClassification.filler


class FFVIIRebirthItem(Item):
    """Item class for Final Fantasy VII: Rebirth."""
    game = "Final Fantasy VII: Rebirth"


# TODO: Replace with actual item data exported from game files
# Example items - these should be replaced with real game data
item_table: Dict[str, ItemData] = {
    # Example weapons
    "Buster Sword": ItemData(0xFF7000, ItemClassification.progression),
    "Mythril Saber": ItemData(0xFF7001, ItemClassification.useful),
    
    # Example armor
    "Bronze Bangle": ItemData(0xFF7100, ItemClassification.filler),
    "Iron Bangle": ItemData(0xFF7101, ItemClassification.useful),
    
    # Example materia
    "Fire Materia": ItemData(0xFF7200, ItemClassification.progression),
    "Ice Materia": ItemData(0xFF7201, ItemClassification.progression),
    "Lightning Materia": ItemData(0xFF7202, ItemClassification.progression),
    
    # Example key items
    "Cargo Ship Access": ItemData(0xFF7300, ItemClassification.progression),
    "Keystone": ItemData(0xFF7301, ItemClassification.progression),
    
    # Example consumables
    "Potion": ItemData(0xFF7400, ItemClassification.filler),
    "Hi-Potion": ItemData(0xFF7401, ItemClassification.filler),
    "Ether": ItemData(0xFF7402, ItemClassification.useful),
    
    # Victory event
    "Victory": ItemData(None, ItemClassification.progression),
}


# Generate item_name_to_id mapping for Archipelago
item_name_to_id: Dict[str, int] = {
    name: data.code for name, data in item_table.items() if data.code is not None
}


def load_items_from_csv(filepath: str) -> Dict[str, int]:
    """
    Load item mappings from a CSV file.
    
    CSV format:
        ItemName,ItemID
        Buster Sword,16707584
        Bronze Bangle,16711936
        
    Args:
        filepath: Path to the CSV file
        
    Returns:
        Dictionary mapping item names to IDs
    """
    items = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_name = row.get('ItemName', '').strip()
                item_id_str = row.get('ItemID', '').strip()
                
                if not item_name or not item_id_str:
                    continue
                
                try:
                    # Support both decimal and hex IDs
                    if item_id_str.startswith('0x') or item_id_str.startswith('0X'):
                        item_id = int(item_id_str, 16)
                    else:
                        item_id = int(item_id_str)
                    
                    items[item_name] = item_id
                except ValueError:
                    print(f"Warning: Invalid item ID '{item_id_str}' for item '{item_name}'")
                    continue
    
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"Error loading items CSV: {e}")
    
    return items


# Example of how to use the CSV loader:
# 
# import os
# 
# # Get path to data directory
# data_dir = os.path.join(os.path.dirname(__file__), "data")
# items_csv = os.path.join(data_dir, "items.csv")
# 
# # Load items if CSV exists
# if os.path.exists(items_csv):
#     csv_items = load_items_from_csv(items_csv)
#     
#     # Merge with item_table or replace it
#     for item_name, item_id in csv_items.items():
#         if item_name not in item_table:
#             item_table[item_name] = ItemData(item_id, ItemClassification.filler)
#     
#     # Regenerate item_name_to_id
#     item_name_to_id = {
#         name: data.code for name, data in item_table.items() if data.code is not None
#     }
