"""
Item definitions for Final Fantasy VII: Rebirth
"""

from typing import Dict, NamedTuple
from BaseClasses import Item, ItemClassification


class FFVIIRebirthItem(Item):
    """Item class for FFVII Rebirth"""
    game = "Final Fantasy VII: Rebirth"


class ItemData(NamedTuple):
    """Data structure for item definitions"""
    name: str
    classification: ItemClassification
    code: int
    count: int = 1  # How many of this item exist in the pool


# TODO: Populate this table with actual items from the game
# This is a placeholder showing the expected format
item_table: Dict[str, ItemData] = {
    # Example items - replace with actual game items
    # "Potion": ItemData("Potion", ItemClassification.filler, 6001, 5),
    # "Phoenix Down": ItemData("Phoenix Down", ItemClassification.useful, 6002, 3),
    # "Mythril Saber": ItemData("Mythril Saber", ItemClassification.progression, 6003, 1),
    # "Summon Materia: Ifrit": ItemData("Summon Materia: Ifrit", ItemClassification.progression, 6100, 1),
    # "Key Item: Ancient Key": ItemData("Key Item: Ancient Key", ItemClassification.progression, 6200, 1),
}


def load_item_data() -> Dict[str, int]:
    """
    Load item data from CSV file in the data/ directory.
    
    Expected CSV format:
    Name,ID,Classification,Count
    Potion,1,filler,5
    Phoenix Down,2,useful,3
    Mythril Saber,3,progression,1
    
    Classification values:
    - progression: Required to complete the game
    - useful: Helpful but not required
    - filler: Common items to fill the pool
    - trap: Items that have negative effects
    
    Returns:
        Dictionary mapping item names to their full item IDs (base_id + offset)
    """
    import csv
    import os
    
    # TODO: Implement CSV loading
    # data_dir = os.path.join(os.path.dirname(__file__), "data")
    # csv_path = os.path.join(data_dir, "items.csv")
    # 
    # if not os.path.exists(csv_path):
    #     print(f"Warning: {csv_path} not found. Using empty item table.")
    #     return {}
    # 
    # item_name_to_id = {}
    # base_id = 6000  # Should match the base_id in __init__.py
    # 
    # with open(csv_path, "r", encoding="utf-8") as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         name = row["Name"]
    #         item_id = base_id + int(row["ID"])
    #         classification_str = row["Classification"]
    #         count = int(row.get("Count", 1))
    #         
    #         # Convert classification string to enum
    #         classification = {
    #             "progression": ItemClassification.progression,
    #             "useful": ItemClassification.useful,
    #             "filler": ItemClassification.filler,
    #             "trap": ItemClassification.trap,
    #         }.get(classification_str.lower(), ItemClassification.filler)
    #         
    #         item_table[name] = ItemData(name, classification, item_id, count)
    #         item_name_to_id[name] = item_id
    # 
    # return item_name_to_id
    
    return {}  # Placeholder


# Example of items that might be in FFVII Rebirth:
"""
Consumables:
- Potion, Hi-Potion, Mega Potion
- Ether, Turbo Ether
- Phoenix Down
- Elixir

Equipment (Progression):
- Weapons for each character
- Armor pieces
- Accessories

Materia (Progression/Useful):
- Magic Materia (Fire, Ice, Lightning, etc.)
- Support Materia (All, Magnify, etc.)
- Summon Materia (Ifrit, Shiva, Ramuh, etc.)
- Command Materia

Key Items (Progression):
- Story-critical items
- Quest items
- Keys and access items

Gil/Currency:
- Gil amounts (can be filler)

Chocobo Gear:
- Chocobo equipment for traversal
"""
