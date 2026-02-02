"""
Location definitions for Final Fantasy VII: Rebirth
"""

from typing import Dict, NamedTuple
from BaseClasses import Location


class FFVIIRebirthLocation(Location):
    """Location class for FFVII Rebirth"""
    game = "Final Fantasy VII: Rebirth"


class LocationData(NamedTuple):
    """Data structure for location definitions"""
    name: str
    code: int
    region: str


# TODO: Populate this table with actual locations from the game
# This is a placeholder showing the expected format
location_table: Dict[str, LocationData] = {
    # Example locations - replace with actual game locations
    # "Grasslands - Combat Spot 1": LocationData("Grasslands - Combat Spot 1", 6001, "Grasslands"),
    # "Grasslands - Treasure Chest 1": LocationData("Grasslands - Treasure Chest 1", 6002, "Grasslands"),
    # "Junon - Boss Fight": LocationData("Junon - Boss Fight", 6100, "Junon"),
}


def load_location_data() -> Dict[str, int]:
    """
    Load location data from CSV file in the data/ directory.
    
    Expected CSV format for territories/encounters:
    TerritoryName,UniqueIndex,MobTemplateList,Region
    Grasslands_Territory_01,0,MobTemplate_01,Grasslands
    Grasslands_Territory_02,1,MobTemplate_02,Grasslands
    
    This matches the format expected from UAssetGUI/UAssetAPI exports.
    
    Returns:
        Dictionary mapping location names to their full location IDs (base_id + offset)
    """
    import csv
    import os
    
    # TODO: Implement CSV loading
    # data_dir = os.path.join(os.path.dirname(__file__), "data")
    # csv_path = os.path.join(data_dir, "territories.csv")
    # 
    # if not os.path.exists(csv_path):
    #     print(f"Warning: {csv_path} not found. Using empty location table.")
    #     return {}
    # 
    # location_name_to_id = {}
    # base_id = 6000  # Should match the base_id in __init__.py
    # 
    # with open(csv_path, "r", encoding="utf-8") as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         territory_name = row["TerritoryName"]
    #         unique_index = int(row["UniqueIndex"])
    #         region = row.get("Region", "Unknown")
    #         
    #         # Create a readable location name
    #         location_name = f"{region} - {territory_name}"
    #         location_id = base_id + unique_index
    #         
    #         location_table[location_name] = LocationData(location_name, location_id, region)
    #         location_name_to_id[location_name] = location_id
    # 
    # return location_name_to_id
    
    return {}  # Placeholder


# Example of location types that might be in FFVII Rebirth:
"""
Combat/Encounter Locations:
- Territory encounters (main source of checks)
- Boss fights
- Optional combat challenges

Treasure Locations:
- Treasure chests scattered in the world
- Hidden items
- Dig spots

Quest Locations:
- Side quest completions
- Intel gathering spots
- NPC interactions

Exploration Locations:
- Lifespring discoveries
- Tower activations
- Chocobo stop discoveries

Mini-game Locations:
- Fort Condor victories
- Chocobo racing wins
- Card game wins
- Piano performances

Story Progression:
- Chapter completions
- Key story moments
"""
