"""
Location definitions for Final Fantasy VII: Rebirth
"""
import csv
from typing import Dict, List

# Example location table
# In production, this would be loaded from exported game data
location_table: Dict[str, dict] = {
    # Story/Boss locations
    "Boss: Midgardsormr": {
        "region": "Grasslands",
        "type": "boss",
        "description": "Defeat Midgardsormr"
    },
    "Story: Kalm Flashback": {
        "region": "Kalm",
        "type": "story",
        "description": "Complete Kalm flashback sequence"
    },
    
    # Territory encounters (from territory DataTable)
    "Grasslands: Encounter 1": {
        "region": "Grasslands",
        "type": "encounter",
        "territory_index": 100,
        "encounter_index": 0
    },
    "Grasslands: Encounter 2": {
        "region": "Grasslands",
        "type": "encounter",
        "territory_index": 100,
        "encounter_index": 1
    },
    
    # Chest locations
    "Grasslands: Chest 1": {
        "region": "Grasslands",
        "type": "chest",
        "description": "Near chocobo stable"
    },
    
    # Mini-games
    "Fort Condor: Victory": {
        "region": "Junon",
        "type": "minigame",
        "description": "Win Fort Condor battle"
    },
    
    # Side quests
    "Side Quest: Missing Chocobos": {
        "region": "Grasslands",
        "type": "quest",
        "description": "Complete Missing Chocobos quest"
    },
    
    # TODO: Add more locations based on game data export
    # - All territory encounters
    # - All boss fights
    # - All chest locations
    # - All quest completions
    # - All mini-game completions
    # - Optional boss fights
}


def load_locations_from_csv(csv_path: str, base_id: int) -> Dict[str, int]:
    """
    Load locations from a CSV file and return location_name_to_id mapping.
    
    Expected CSV format (from territory DataTable export):
    UniqueIndex,TerritoryName,MobTemplateList,WaveMobTemplateList
    100,"Grasslands_01","[1,2,3]","[4,5]"
    101,"Junon_Harbor","[10,11]","[]"
    
    Or simpler format:
    LocationName,Region,Type,Description
    "Boss: Midgardsormr",Grasslands,boss,"Defeat Midgardsormr"
    
    Args:
        csv_path: Path to locations CSV file
        base_id: Base ID to start numbering from
        
    Returns:
        Dictionary mapping location names to AP location IDs
    """
    location_name_to_id = {}
    current_id = base_id
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check if this is a territory table or location table
            fieldnames = reader.fieldnames or []
            
            if 'UniqueIndex' in fieldnames and 'TerritoryName' in fieldnames:
                # This is a territory table - create encounter locations
                return _parse_territory_csv(reader, base_id)
            elif 'LocationName' in fieldnames:
                # This is a location table
                return _parse_location_csv(reader, base_id)
            else:
                print(f"Warning: Unknown CSV format in {csv_path}")
                return {}
    
    except FileNotFoundError:
        print(f"Warning: Locations CSV not found at {csv_path}")
    except Exception as e:
        print(f"Error loading locations CSV: {e}")
    
    return location_name_to_id


def _parse_location_csv(reader, base_id: int) -> Dict[str, int]:
    """Parse a simple location CSV"""
    location_name_to_id = {}
    current_id = base_id
    
    for row in reader:
        location_name = row.get('LocationName', '').strip()
        
        if not location_name:
            continue
        
        # Add to location_table if not already present
        if location_name not in location_table:
            location_table[location_name] = {
                "region": row.get('Region', 'Unknown'),
                "type": row.get('Type', 'generic'),
                "description": row.get('Description', '')
            }
        
        location_name_to_id[location_name] = current_id
        current_id += 1
    
    return location_name_to_id


def _parse_territory_csv(reader, base_id: int) -> Dict[str, int]:
    """
    Parse a territory DataTable export and create encounter locations.
    
    Each territory can have multiple encounters (MobTemplateList entries),
    so we create one location per encounter.
    """
    location_name_to_id = {}
    current_id = base_id
    
    for row in reader:
        unique_index = row.get('UniqueIndex', '')
        territory_name = row.get('TerritoryName', '').strip()
        mob_template_list = row.get('MobTemplateList', '[]')
        
        if not territory_name:
            continue
        
        # Parse mob template list (it's stored as a string representation of an array)
        # Example: "[1,2,3]" -> [1, 2, 3]
        mob_list = _parse_array_string(mob_template_list)
        
        # Create a location for each encounter in this territory
        for idx, mob_id in enumerate(mob_list):
            location_name = f"{territory_name}: Encounter {idx + 1}"
            
            location_table[location_name] = {
                "region": territory_name,
                "type": "encounter",
                "territory_index": int(unique_index) if unique_index.isdigit() else 0,
                "encounter_index": idx,
                "mob_template_id": mob_id
            }
            
            location_name_to_id[location_name] = current_id
            current_id += 1
    
    return location_name_to_id


def _parse_array_string(array_str: str) -> List[int]:
    """
    Parse a string representation of an integer array.
    Example: "[1,2,3]" -> [1, 2, 3]
    """
    try:
        # Remove brackets and split by comma
        array_str = array_str.strip('[]')
        if not array_str:
            return []
        
        return [int(x.strip()) for x in array_str.split(',') if x.strip()]
    except (ValueError, AttributeError):
        return []


def get_location_region(location_name: str) -> str:
    """Get the region name for a location"""
    return location_table.get(location_name, {}).get("region", "Unknown")


def get_location_type(location_name: str) -> str:
    """Get the type of a location (boss, encounter, chest, etc.)"""
    return location_table.get(location_name, {}).get("type", "generic")


# Example of how to export locations to CSV for editing:
def export_locations_to_csv(output_path: str):
    """
    Export current location_table to CSV for easy editing.
    Run this once to generate a template CSV.
    """
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['LocationName', 'Region', 'Type', 'Description'])
        
        for location_name, data in location_table.items():
            writer.writerow([
                location_name,
                data.get('region', 'Unknown'),
                data.get('type', 'generic'),
                data.get('description', '')
            ])
    
    print(f"Exported {len(location_table)} locations to {output_path}")


# If run as script, export template CSV
if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    export_locations_to_csv(os.path.join(data_dir, "locations_template.csv"))
