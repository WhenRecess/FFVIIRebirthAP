"""
Generate location mappings from game data exports
==================================================

This script processes the game's exported data to create mappings
between in-game events and Archipelago location IDs.

Output: ap_locations.json - Complete mapping for LocationTracker.lua
"""

import json
from pathlib import Path
from typing import Dict, List

# Paths
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "worlds" / "finalfantasy_rebirth" / "data"
OUTPUT_FILE = REPO_ROOT / "memory_bridge" / "ap_locations.json"

# Base AP location ID
BASE_LOCATION_ID = 770001000

def generate_story_locations() -> Dict:
    """Generate mappings for story progression checks."""
    locations = {}
    
    # Story flags mapped to ResidentWork variables
    story_flags = {
        1001: "Story: Kalm Flashback Complete",
        1002: "Story: Reach Chocobo Ranch",
        1003: "Story: First Chocobo Caught",
        1010: "Story: Arrive at Junon",
        1015: "Story: Junon Parade Complete",
        # Add more as you discover them
    }
    
    for flag_id, name in story_flags.items():
        ap_id = BASE_LOCATION_ID + flag_id
        locations[f"story_flag_{flag_id}"] = {
            "location_id": ap_id,
            "name": name,
            "type": "story_flag",
            "trigger": {
                "type": "resident_work",
                "variable": flag_id,
                "value": 1
            }
        }
    
    return locations

def generate_boss_locations() -> Dict:
    """Generate mappings for boss defeats."""
    locations = {}
    
    # Boss battle IDs (need to be discovered from game)
    bosses = {
        "Boss_001": "Boss: Midgardsormr",
        "Boss_002": "Boss: Bottomswell",
        "Boss_003": "Boss: Dyne",
        # Add more as you find battle IDs
    }
    
    location_id = BASE_LOCATION_ID + 4000  # Bosses start at +4000
    for boss_id, name in bosses.items():
        locations[boss_id] = {
            "location_id": location_id,
            "name": name,
            "type": "boss",
            "trigger": {
                "type": "battle_complete",
                "battle_id": boss_id
            }
        }
        location_id += 1
    
    return locations

def generate_colosseum_locations() -> Dict:
    """Generate mappings from Colosseum.json data."""
    locations = {}
    
    colosseum_file = DATA_DIR / "Colosseum_parsed.json"
    if not colosseum_file.exists():
        print(f"Warning: {colosseum_file} not found")
        return locations
    
    data = json.loads(colosseum_file.read_text(encoding='utf-8'))
    
    location_id = BASE_LOCATION_ID + 5000  # Colosseum starts at +5000
    for idx, entry in enumerate(data, 1):
        key = f"Colosseum_{idx}"
        locations[key] = {
            "location_id": location_id,
            "name": f"Colosseum: Battle {idx}",
            "type": "colosseum",
            "trigger": {
                "type": "colosseum_battle",
                "battle_index": idx
            }
        }
        location_id += 1
    
    print(f"Generated {len(locations)} colosseum locations")
    return locations

def generate_shop_locations() -> Dict:
    """Generate shop purchase locations."""
    locations = {}
    
    # Define shops and their slot counts
    shops = {
        "Shop_Kalm": {"slots": 8, "name": "Kalm Item Shop"},
        "Shop_Chocobo_Ranch": {"slots": 6, "name": "Chocobo Ranch Shop"},
        "Shop_Junon": {"slots": 12, "name": "Junon Item Shop"},
        # Add more shops
    }
    
    location_id = BASE_LOCATION_ID + 3000  # Shops start at +3000
    for shop_id, shop_data in shops.items():
        for slot in range(1, shop_data["slots"] + 1):
            key = f"{shop_id}_Slot_{slot}"
            locations[key] = {
                "location_id": location_id,
                "name": f"{shop_data['name']}: Slot {slot}",
                "type": "shop_purchase",
                "trigger": {
                    "type": "shop_purchase",
                    "shop_id": shop_id,
                    "slot": slot
                }
            }
            location_id += 1
    
    print(f"Generated {len(locations)} shop locations")
    return locations

def generate_field_item_locations() -> Dict:
    """Generate field item (chest) locations."""
    locations = {}
    
    # TODO: Parse from game exports or manual mapping
    # For now, placeholder structure
    field_items = {
        "Grasslands_Chest_001": {"x": 1234.5, "y": 5678.9, "z": 100.0},
        "Grasslands_Chest_002": {"x": 2345.6, "y": 6789.0, "z": 105.5},
        # Add coordinates for all chests
    }
    
    location_id = BASE_LOCATION_ID + 2000  # Field items start at +2000
    for chest_id, coords in field_items.items():
        locations[chest_id] = {
            "location_id": location_id,
            "name": f"Field Item: {chest_id}",
            "type": "field_item",
            "trigger": {
                "type": "inventory_change",
                "position": coords,
                "radius": 100.0  # Detection radius
            }
        }
        location_id += 1
    
    print(f"Generated {len(locations)} field item locations")
    return locations

def main():
    print("Generating location mappings...")
    
    all_locations = {}
    
    # Generate each category
    all_locations.update(generate_story_locations())
    all_locations.update(generate_boss_locations())
    all_locations.update(generate_colosseum_locations())
    all_locations.update(generate_shop_locations())
    all_locations.update(generate_field_item_locations())
    
    # Add metadata
    output = {
        "version": 1,
        "base_id": BASE_LOCATION_ID,
        "total_locations": len(all_locations),
        "locations": all_locations
    }
    
    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(output, indent=2), encoding='utf-8')
    
    print(f"\n✓ Generated {OUTPUT_FILE}")
    print(f"  Total locations: {len(all_locations)}")
    
    # Category breakdown
    categories = {}
    for loc_data in all_locations.values():
        cat = loc_data["type"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nBreakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")

if __name__ == "__main__":
    main()
