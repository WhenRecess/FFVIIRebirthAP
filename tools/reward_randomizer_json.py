#!/usr/bin/env python3
"""
FF7 Rebirth Reward Randomizer (JSON Mode)
==========================================

Randomizes chest and quest rewards by modifying UAssetGUI-exported JSON.

WORKFLOW:
1. Export Reward.uasset to JSON using UAssetGUI
2. Run this script to randomize ItemID_Array values
3. Convert JSON back to .uasset/.uexp using ReUE4SS/Retoc
4. Deploy to game

USAGE:
  python reward_randomizer_json.py <input.json> <output.json> <seed>

EXAMPLE:
  # First: Export Reward.uasset with UAssetGUI
  python reward_randomizer_json.py Reward.json Reward_randomized.json 12345
  
  # Then: Convert back with ReUE4SS
  retoc.exe Reward_randomized.json

WHAT IT DOES:
  - Finds all "ItemID_Array" properties in the JSON
  - Replaces item name values with randomized items from pool
  - Preserves ItemCount_Array, ItemAddType_Array, UniqueIndex
"""

import json
import random
import sys
from pathlib import Path
from typing import List, Tuple


def load_item_pool():
    """Load valid item names from reward data itself"""
    data_dir = Path(__file__).parent / "data"
    
    # Extract all unique item names from the parsed reward data
    # This ensures we only use items that actually exist in the game
    reward_file = data_dir / "_reward_parsed.json"
    item_names = set()
    
    with open(reward_file, 'r') as f:
        rewards = json.load(f)
        for reward_entry in rewards.values():
            if 'items' in reward_entry:
                for item in reward_entry['items']:
                    if 'name' in item:
                        item_names.add(item['name'])
    
    item_names = list(item_names)
    print(f"Loaded {len(item_names)} valid item names from reward data")
    
    # Group by prefix for better matching
    by_prefix = {}
    for name in item_names:
        prefix = name.split('_')[0] if '_' in name else 'OTHER'
        if prefix not in by_prefix:
            by_prefix[prefix] = []
        by_prefix[prefix].append(name)
    
    return item_names, by_prefix


def find_and_replace_items(obj, item_pool, items_by_prefix, rng, stats):
    """
    Recursively find and replace ItemID_Array values in JSON structure
    Modifies in-place and tracks statistics
    """
    if isinstance(obj, dict):
        # Check if this is an ItemID_Array
        if obj.get("Name") == "ItemID_Array" and "Value" in obj:
            value = obj["Value"]
            if isinstance(value, list):
                for item_entry in value:
                    if isinstance(item_entry, dict) and "Value" in item_entry:
                        old_item = item_entry["Value"]
                        
                        # Try to pick same category (M_MAG → M_MAG, etc.)
                        prefix = old_item.split('_')[0] if '_' in old_item else 'OTHER'
                        candidates = items_by_prefix.get(prefix, item_pool)
                        
                        new_item = rng.choice(candidates)
                        item_entry["Value"] = new_item
                        
                        stats["modified"] += 1
                        if stats["modified"] <= 10:
                            stats["examples"].append(f"{old_item} → {new_item}")
        
        # Recurse into dict values
        for value in obj.values():
            find_and_replace_items(value, item_pool, items_by_prefix, rng, stats)
    
    elif isinstance(obj, list):
        # Recurse into list items
        for item in obj:
            find_and_replace_items(item, item_pool, items_by_prefix, rng, stats)


def randomize_rewards_json(input_path, output_path, seed):
    """Randomize reward items in UAssetGUI-exported JSON"""
    
    print(f"=== FF7 Rebirth Reward Randomizer (JSON) ===")
    print(f"Input: {Path(input_path).name}")
    print(f"Seed: {seed}\n")
    
    # Load item pool
    item_pool, items_by_prefix = load_item_pool()
    rng = random.Random(seed)
    
    # Load JSON
    print(f"Loading JSON...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"JSON loaded successfully")
    
    # Find and replace all items
    print(f"Scanning for ItemID_Array properties...\n")
    stats = {"modified": 0, "examples": []}
    find_and_replace_items(data, item_pool, items_by_prefix, rng, stats)
    
    if stats["modified"] == 0:
        print("ERROR: No ItemID_Array properties found")
        print("Make sure you exported Reward.uasset with UAssetGUI")
        return False
    
    # Show results
    print(f"Randomized {stats['modified']} items")
    print(f"\nFirst 10 changes:")
    for example in stats["examples"]:
        print(f"  {example}")
    if stats["modified"] > 10:
        print(f"  ... and {stats['modified'] - 10} more")
    
    # Save output
    print(f"\nSaving to {Path(output_path).name}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Done!")
    return True


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return
    
    # Parse arguments
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.replace('.json', '_randomized.json')
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
    
    # Validate input
    if not Path(input_path).exists():
        print(f"ERROR: Input file not found: {input_path}")
        return
    
    # Run randomization
    success = randomize_rewards_json(input_path, output_path, seed)
    
    if success:
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("1. Convert JSON back to .uasset/.uexp:")
        print(f"   retoc.exe {Path(output_path).name}")
        print("2. Copy Reward.uasset and Reward.uexp to game mods folder")
        print("3. Launch game and test rewards!")


if __name__ == '__main__':
    main()
