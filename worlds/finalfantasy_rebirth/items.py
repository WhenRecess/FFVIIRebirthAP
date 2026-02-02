"""
Item definitions for Final Fantasy VII: Rebirth
"""
from BaseClasses import ItemClassification
import csv
from typing import Dict

# Example item table
# In production, this would be much larger and loaded from CSV
item_table: Dict[str, dict] = {
    # Progression items (required to complete the game)
    "Chocobo Lure": {
        "classification": ItemClassification.progression,
        "count": 1,
        "description": "Allows catching and riding chocobos"
    },
    "Grappling Hook": {
        "classification": ItemClassification.progression,
        "count": 1,
        "description": "Allows reaching high places"
    },
    "Ancient Key": {
        "classification": ItemClassification.progression,
        "count": 1,
        "description": "Opens ancient temple doors"
    },
    
    # Useful items (helpful but not required)
    "Fire Materia": {
        "classification": ItemClassification.useful,
        "count": 3,
        "description": "Elemental attack materia"
    },
    "Ice Materia": {
        "classification": ItemClassification.useful,
        "count": 3,
        "description": "Elemental attack materia"
    },
    "Lightning Materia": {
        "classification": ItemClassification.useful,
        "count": 3,
        "description": "Elemental attack materia"
    },
    "Healing Materia": {
        "classification": ItemClassification.useful,
        "count": 5,
        "description": "Restores HP"
    },
    
    # Filler items (common rewards)
    "Potion": {
        "classification": ItemClassification.filler,
        "count": 20,
        "description": "Restores 500 HP"
    },
    "Ether": {
        "classification": ItemClassification.filler,
        "count": 15,
        "description": "Restores 50 MP"
    },
    "Phoenix Down": {
        "classification": ItemClassification.filler,
        "count": 10,
        "description": "Revives KO'd character"
    },
    "Gil Bundle": {
        "classification": ItemClassification.filler,
        "count": 50,
        "description": "1000 Gil"
    },
    
    # TODO: Add more items based on game data export
    # - Story progression items
    # - Equipment pieces
    # - Materia types
    # - Key items
    # - Summon materia
    # - Weapons
    # - Accessories
}


def load_items_from_csv(csv_path: str, base_id: int) -> Dict[str, int]:
    """
    Load items from a CSV file and return item_name_to_id mapping.
    
    Expected CSV format:
    ItemName,Classification,Count,Description
    "Chocobo Lure",progression,1,"Allows catching chocobos"
    "Potion",filler,20,"Restores 500 HP"
    
    Args:
        csv_path: Path to items CSV file
        base_id: Base ID to start numbering from
        
    Returns:
        Dictionary mapping item names to AP item IDs
    """
    item_name_to_id = {}
    current_id = base_id
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                item_name = row.get('ItemName', '').strip()
                
                if not item_name:
                    continue
                
                # Parse classification
                classification_str = row.get('Classification', 'filler').lower()
                if classification_str == 'progression':
                    classification = ItemClassification.progression
                elif classification_str == 'useful':
                    classification = ItemClassification.useful
                elif classification_str == 'trap':
                    classification = ItemClassification.trap
                else:
                    classification = ItemClassification.filler
                
                # Get count (number of times this item appears)
                count = int(row.get('Count', 1))
                
                # Store in item_table
                if item_name not in item_table:
                    item_table[item_name] = {
                        "classification": classification,
                        "count": count,
                        "description": row.get('Description', '')
                    }
                
                # Assign ID
                item_name_to_id[item_name] = current_id
                current_id += 1
    
    except FileNotFoundError:
        print(f"Warning: Items CSV not found at {csv_path}")
    except Exception as e:
        print(f"Error loading items CSV: {e}")
    
    return item_name_to_id


def get_item_classification(item_name: str) -> ItemClassification:
    """Get the classification for an item by name"""
    return item_table.get(item_name, {}).get("classification", ItemClassification.filler)


# Example of how to export items to CSV for editing:
def export_items_to_csv(output_path: str):
    """
    Export current item_table to CSV for easy editing.
    Run this once to generate a template CSV.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ItemName', 'Classification', 'Count', 'Description'])
        
        for item_name, data in item_table.items():
            classification = data['classification']
            if classification == ItemClassification.progression:
                class_str = 'progression'
            elif classification == ItemClassification.useful:
                class_str = 'useful'
            elif classification == ItemClassification.trap:
                class_str = 'trap'
            else:
                class_str = 'filler'
            
            writer.writerow([
                item_name,
                class_str,
                data.get('count', 1),
                data.get('description', '')
            ])
    
    print(f"Exported {len(item_table)} items to {output_path}")


# If run as script, export template CSV
if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    export_items_to_csv(os.path.join(data_dir, "items_template.csv"))
