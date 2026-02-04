"""
Pre-Randomization System for FF7 Rebirth
==========================================

Instead of detecting and reacting to item pickups at runtime,
this system modifies chest/shop/reward data in memory BEFORE
the player encounters them.

Flow:
    1. Generate AP seed (know all location→item mappings)
    2. At game start, scan memory for chest/shop data structures
    3. Patch item IDs to match randomized seed
    4. Game naturally gives correct items
    5. Watch for location checks (chest opened, boss defeated)
    6. Report checks to AP server

Advantages:
    - No runtime item replacement needed
    - Perfect player experience
    - No timing issues
    - Simpler than runtime detection
    
Challenges:
    - Need to find chest data structures
    - Need to find shop data structures
    - Some things may be server-side (can't patch)
"""

from typing import Dict, List
import json
from pathlib import Path

class PreRandomizer:
    """
    Manages pre-randomization data and generates patches
    for the Memory Bridge to apply at game start.
    """
    
    def __init__(self, seed_data: Dict):
        """
        seed_data format:
        {
            "Grasslands_Chest_05": {"item_id": 111, "item_name": "Ether"},
            "Boss_Midgardsormr": {"item_id": 116, "item_name": "Phoenix Down"},
            ...
        }
        """
        self.seed_data = seed_data
        self.chest_patches = []
        self.shop_patches = []
        self.reward_patches = []
        
    def generate_memory_patches(self) -> Dict:
        """
        Generate memory patch instructions for Memory Bridge.
        
        Returns dict with patches organized by type:
        {
            "chests": [
                {"chest_id": 5, "item_id": 111, "quantity": 1},
                ...
            ],
            "shops": [
                {"shop_id": "Shop_Kalm", "slot": 0, "item_id": 112},
                ...
            ],
            "battle_rewards": [
                {"battle_id": "Boss_Midgardsormr", "item_id": 116},
                ...
            ],
            "simulator_rewards": [
                {"challenge_id": "VR_Summon_Bahamut", "item_id": 125},
                ...
            ],
            "colosseum_rewards": [
                {"battle_num": 1, "item_id": 102},
                ...
            ]
        }
        """
        patches = {
            "chests": [],
            "shops": [],
            "battle_rewards": [],
            "simulator_rewards": [],
            "colosseum_rewards": []
        }
        
        for location_key, item_data in self.seed_data.items():
            if location_key.startswith("Chest_"):
                # Extract chest ID from key: Chest_005 → 5
                chest_id = int(location_key.split("_")[1])
                patches["chests"].append({
                    "chest_id": chest_id,
                    "item_id": item_data["item_id"],
                    "quantity": item_data.get("quantity", 1)
                })
                
            elif location_key.startswith("Shop_"):
                # Shop_Kalm_Slot_3 → shop=Kalm, slot=3
                parts = location_key.split("_")
                if len(parts) >= 4 and parts[2] == "Slot":
                    shop_id = parts[1]
                    slot = int(parts[3])
                    patches["shops"].append({
                        "shop_id": f"Shop_{shop_id}",
                        "slot": slot,
                        "item_id": item_data["item_id"]
                    })
                
            elif location_key.startswith("Boss_"):
                # Boss_Midgardsormr → battle reward
                boss_id = location_key.replace("Boss_", "")
                patches["battle_rewards"].append({
                    "battle_id": location_key,
                    "item_id": item_data["item_id"],
                    "quantity": item_data.get("quantity", 1)
                })
                
            elif location_key.startswith("VR_") or location_key.startswith("Simulator_"):
                # VR_Summon_Bahamut or Simulator_Combat_Challenge_5
                patches["simulator_rewards"].append({
        
        print(f"\n✓ Generated randomization patches:")
        print(f"  - Chests: {len(patches['chests'])}")
        print(f"  - Shop slots: {len(patches['shops'])}")
        print(f"  - Battle rewards: {len(patches['battle_rewards'])}")
        print(f"  - Simulator rewards: {len(patches['simulator_rewards'])}")
        print(f"  - Colosseum battles: {len(patches['colosseum_rewards'])}")
        print(f"  Total: {sum(len(v) for v in patches.values())}y", 1)
                })
                
            elif location_key.startswith("Colosseum_"):
                # Colosseum_Battle_12 → battle 12
                battle_num = int(location_key.split("_")[-1])
                patches["colosseum_rewards"].append({
                    "battle_num": battle_num,
                    "item_id": item_data["item_id"],
                    "quantity": item_data.get("quantity", 1)
                })
        
        return patches
    
    def save_patches(self, output_path: Path):
        """Save patches to JSON file for Memory Bridge to read."""
        patches = self.generate_memory_patches()
        output_path.write_text(json.dumps(patches, indent=2), encoding='utf-8')
        print(f"Saved {len(patches['chests'])} chest patches")
        print(f"Saved {len(patches['shops'])} shop patches")
        print(f"Saved {len(patches['rewards'])} reward patches")
# Chests
        "Chest_001": {"item_id": 111, "item_name": "Ether", "quantity": 1},
        "Chest_002": {"item_id": 116, "item_name": "Phoenix Down", "quantity": 1},
        "Chest_003": {"item_id": 112, "item_name": "Hi-Ether", "quantity": 1},
        
        # Shop slots
        "Shop_Kalm_Slot_0": {"item_id": 102, "item_name": "Mega-Potion"},
        "Shop_Kalm_Slot_1": {"item_id": 115, "item_name": "Elixir"},
        "Shop_ChocoboBills_Slot_0": {"item_id": 125, "item_name": "Remedy"},
        
        # Boss rewards
        "Boss_Midgardsormr": {"item_id": 2005, "item_name": "Hunter's Bangle", "quantity": 1},
        "Boss_Bottomswell": {"item_id": 9022, "item_name": "Star Pendant", "quantity": 1},
        
        # Simulator challenges
        "VR_Summon_Bahamut": {"item_id": 10050, "item_name": "Bahamut Materia", "quantity": 1},
        "Simulator_Combat_Challenge_5": {"item_id": 112, "item_name": "Hi-Ether", "quantity": 3},
        
        # Colosseum
        "Colosseum_Battle_1": {"item_id": 102, "item_name": "Mega-Potion", "quantity": 2},
        "Colosseum_Battle_5": {"item_id": 2013, "item_name": "Owl Bracer", "quantity": 1
        "Chest_001": {"item_id": 111, "item_name": "Ether"},
        "Chest_002": {"item_id": 116, "item_name": "Phoenix Down"},
        "Chest_003": {"item_id": 112, "item_name": "Hi-Ether"},
        "Shop_Kalm_Slot_0": {"item_id": 102, "item_name": "Mega-Potion"},
        "Boss_Midgardsormr": {"item_id": 125, "item_name": "Remedy"},
    }


if __name__ == "__main__":
    # Example usage
    seed = generate_test_seed()
    randomizer = PreRandomizer(seed)
    
    output_file = Path("memory_bridge/randomization_patches.json")
    randomizer.save_patches(output_file)
    
    print(f"\nGenerated patches saved to: {output_file}")
    print("\nNext steps:")
    print("1. Use Cheat Engine to find chest data structures")
    print("2. Extend Memory Bridge to apply these patches at game start")
    print("3. Test with a few chests to verify it works")
