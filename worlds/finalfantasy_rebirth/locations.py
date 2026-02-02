"""
Location definitions for Final Fantasy VII: Rebirth Archipelago World.
"""

import csv
from typing import Dict, NamedTuple
from BaseClasses import Location


class LocationData(NamedTuple):
    """Data structure for a location."""
    code: int
    region: str = "Main Game"


class FFVIIRebirthLocation(Location):
    """Location class for Final Fantasy VII: Rebirth."""
    game = "Final Fantasy VII: Rebirth"


# TODO: Replace with actual location data exported from game files
# Example locations - these should be replaced with real game data
location_table: Dict[str, LocationData] = {
    # Example boss locations
    "Boss: Scorpion Sentinel": LocationData(0xFF7000, "Midgar"),
    "Boss: Air Buster": LocationData(0xFF7001, "Midgar"),
    "Boss: Reno": LocationData(0xFF7002, "Midgar"),
    
    # Example chest locations
    "Chest: Sector 7 Slums - Item Shop": LocationData(0xFF7100, "Midgar"),
    "Chest: Sector 7 Slums - Weapon Shop": LocationData(0xFF7101, "Midgar"),
    "Chest: Sector 5 Slums - Church": LocationData(0xFF7102, "Midgar"),
    
    # Example materia locations
    "Materia: Kalm - All": LocationData(0xFF7200, "Kalm"),
    "Materia: Junon - Enemy Skill": LocationData(0xFF7201, "Junon"),
    
    # Example quest locations
    "Quest: Beginner's Hall Completion": LocationData(0xFF7300, "Midgar"),
    "Quest: Chocobo Racing - C Class Victory": LocationData(0xFF7301, "Gold Saucer"),
}


# Generate location_name_to_id mapping for Archipelago
location_name_to_id: Dict[str, int] = {
    name: data.code for name, data in location_table.items()
}


def load_locations_from_csv(filepath: str) -> Dict[str, int]:
    """
    Load location mappings from a CSV file.
    
    CSV format:
        LocationName,LocationID,Region
        Boss: Scorpion Sentinel,16707584,Midgar
        Chest: Sector 7 Slums,16711936,Midgar
        
    Alternative CSV format (territory data):
        RowName,UniqueIndex,MobTemplateList,MobLevels
        Territory_Midgar_01,1,Enemy1;Enemy2,5;7
        Territory_Kalm_01,2,Enemy3,10
        
    Args:
        filepath: Path to the CSV file
        
    Returns:
        Dictionary mapping location names to IDs
    """
    locations = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Check which format the CSV is in
            fieldnames = reader.fieldnames or []
            
            if 'LocationName' in fieldnames and 'LocationID' in fieldnames:
                # Standard format: LocationName,LocationID[,Region]
                for row in reader:
                    location_name = row.get('LocationName', '').strip()
                    location_id_str = row.get('LocationID', '').strip()
                    
                    if not location_name or not location_id_str:
                        continue
                    
                    try:
                        # Support both decimal and hex IDs
                        if location_id_str.startswith('0x') or location_id_str.startswith('0X'):
                            location_id = int(location_id_str, 16)
                        else:
                            location_id = int(location_id_str)
                        
                        locations[location_name] = location_id
                    except ValueError:
                        print(f"Warning: Invalid location ID '{location_id_str}' for location '{location_name}'")
                        continue
            
            elif 'RowName' in fieldnames and 'UniqueIndex' in fieldnames:
                # Territory format: RowName,UniqueIndex,MobTemplateList,MobLevels
                for row in reader:
                    row_name = row.get('RowName', '').strip()
                    unique_index_str = row.get('UniqueIndex', '').strip()
                    mob_list = row.get('MobTemplateList', '').strip()
                    
                    if not row_name or not unique_index_str:
                        continue
                    
                    try:
                        location_id = int(unique_index_str)
                        
                        # Generate location name from row name and mob list
                        # Example: "Territory_Midgar_01" with "Scorpion;Guard" -> "Midgar: Defeat Scorpion"
                        territory_name = row_name.replace('Territory_', '').replace('_', ' ')
                        
                        if mob_list:
                            # Use first mob in the list for location name
                            first_mob = mob_list.split(';')[0].strip()
                            location_name = f"{territory_name}: Defeat {first_mob}"
                        else:
                            location_name = f"{territory_name}: Clear"
                        
                        locations[location_name] = location_id
                    except ValueError:
                        print(f"Warning: Invalid UniqueIndex '{unique_index_str}' for row '{row_name}'")
                        continue
            
            else:
                print(f"Error: CSV format not recognized. Expected 'LocationName,LocationID' or 'RowName,UniqueIndex'")
    
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
    except Exception as e:
        print(f"Error loading locations CSV: {e}")
    
    return locations


# Example of how to use the CSV loader:
# 
# import os
# 
# # Get path to data directory
# data_dir = os.path.join(os.path.dirname(__file__), "data")
# locations_csv = os.path.join(data_dir, "locations.csv")
# 
# # Load locations if CSV exists
# if os.path.exists(locations_csv):
#     csv_locations = load_locations_from_csv(locations_csv)
#     
#     # Merge with location_table or replace it
#     for location_name, location_id in csv_locations.items():
#         if location_name not in location_table:
#             location_table[location_name] = LocationData(location_id, "Main Game")
#     
#     # Regenerate location_name_to_id
#     location_name_to_id = {
#         name: data.code for name, data in location_table.items()
#     }
