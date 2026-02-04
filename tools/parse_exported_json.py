"""
FFVII Rebirth Exported JSON Parser

This script parses the JSON files exported by UAssetExporter and extracts
structured data by analyzing the name references and data patterns.

Usage:
    python parse_exported_json.py <json_file>
    python parse_exported_json.py --all <data_folder>
"""

import json
import struct
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict


class ExportedJsonParser:
    def __init__(self, json_data: Dict):
        self.data = json_data
        self.names = json_data.get("names", [])
        self.name_lookup = {i: name for i, name in enumerate(self.names)}
        self.exports = json_data.get("exports", [])
        
    def get_name(self, index: int) -> Optional[str]:
        """Get name from index."""
        if 0 <= index < len(self.names):
            return self.names[index]
        return None
    
    def categorize_names(self) -> Dict[str, List[str]]:
        """Categorize all names by their patterns."""
        categories = defaultdict(list)
        
        for name in self.names:
            if name.startswith("/Script/") or name.startswith("/Game/"):
                categories["internal"].append(name)
            elif name.startswith("COL"):
                if "POS" in name or "POSITION" in name:
                    categories["colosseum_positions"].append(name)
                elif "_EXTRA_" in name:
                    categories["colosseum_extra"].append(name)
                else:
                    categories["colosseum_battles"].append(name)
            elif name.startswith("rwr") or name.startswith("rwd"):
                categories["rewards"].append(name)
            elif name.startswith("$Release_"):
                categories["unlock_conditions"].append(name)
            elif name.startswith("EN") and "_" in name:
                categories["enemies"].append(name)
            elif name.startswith("SU") and "_" in name:
                categories["summons"].append(name)
            elif name.startswith("mob"):
                categories["mob_templates"].append(name)
            elif name.startswith("ter"):
                categories["territories"].append(name)
            elif name.startswith("POS_"):
                categories["positions"].append(name)
            elif name.startswith("E_ACC_") or name.startswith("E_ARM_") or name.startswith("E_"):
                categories["equipment"].append(name)
            elif name.startswith("IT_") or name.startswith("it_"):
                categories["items"].append(name)
            elif name.startswith("W_"):
                categories["weapons"].append(name)
            elif name.startswith("M_"):
                categories["materia"].append(name)
            elif name.startswith("key_"):
                categories["key_items"].append(name)
            elif name.startswith("ShopItem_"):
                categories["shop_entries"].append(name)
            elif name.startswith("SHOP_COUNTER_"):
                categories["shop_counters"].append(name)
            elif name.startswith("CraftItem_"):
                categories["craft_entries"].append(name)
            elif name.startswith("BGM_"):
                categories["bgm"].append(name)
            elif re.match(r"^[A-Z]{2,4}_[A-Z0-9_]+$", name):
                categories["game_ids"].append(name)
            elif name in ["None", "ArrayProperty", "IntProperty", "NameProperty", "StructProperty", "ByteProperty"]:
                categories["property_types"].append(name)
            else:
                categories["other"].append(name)
        
        return dict(categories)
    
    def extract_colosseum_records(self) -> List[Dict]:
        """Extract Colosseum battle records."""
        records = []
        categories = self.categorize_names()
        
        battles = categories.get("colosseum_battles", [])
        rewards = categories.get("rewards", [])
        unlocks = categories.get("unlock_conditions", [])
        bgms = categories.get("bgm", [])
        
        # Create lookup for rewards by battle ID
        reward_lookup = defaultdict(list)
        for reward in rewards:
            # Extract the battle ID from reward name
            # e.g., "rwrdCOL30_GOLDA_08" -> "COL30_GOLDA_08"
            match = re.match(r"(rwr?d)(COL[^_]+_.+)", reward)
            if match:
                battle_id = match.group(2)
                reward_lookup[battle_id].append(reward)
        
        # Create unlock lookup
        unlock_lookup = {}
        for unlock in unlocks:
            # e.g., "$Release_COL30_GOLDA_01" -> "COL30_GOLDA_01"
            battle_id = unlock.replace("$Release_", "")
            unlock_lookup[battle_id] = unlock
        
        for battle in battles:
            record = {
                "battle_id": battle,
                "rewards": reward_lookup.get(battle, []),
                "unlock_condition": unlock_lookup.get(battle),
            }
            
            # Try to parse battle components
            parts = battle.split("_")
            if len(parts) >= 2:
                record["colosseum"] = parts[0]  # e.g., "COL30"
                record["round_type"] = parts[1] if len(parts) > 1 else None  # e.g., "GOLDA"
                record["round_number"] = parts[2] if len(parts) > 2 else None  # e.g., "08"
            
            records.append(record)
        
        return sorted(records, key=lambda x: x["battle_id"])
    
    def extract_enemy_records(self) -> List[Dict]:
        """Extract enemy records."""
        records = []
        categories = self.categorize_names()
        
        enemies = categories.get("enemies", [])
        
        for enemy in enemies:
            parts = enemy.split("_", 1)
            record = {
                "enemy_id": enemy,
                "base_code": parts[0] if parts else enemy,
                "variant": parts[1] if len(parts) > 1 else None
            }
            records.append(record)
        
        return sorted(records, key=lambda x: x["enemy_id"])
    
    def extract_summon_records(self) -> List[Dict]:
        """Extract summon records."""
        records = []
        categories = self.categorize_names()
        
        summons = categories.get("summons", [])
        
        for summon in summons:
            parts = summon.split("_", 1)
            record = {
                "summon_id": summon,
                "base_code": parts[0] if parts else summon,
                "variant": parts[1] if len(parts) > 1 else None
            }
            records.append(record)
        
        return sorted(records, key=lambda x: x["summon_id"])
    
    def extract_reward_records(self) -> List[Dict]:
        """Extract reward records."""
        records = []
        categories = self.categorize_names()
        
        all_items = []
        all_items.extend([(i, "equipment") for i in categories.get("equipment", [])])
        all_items.extend([(i, "item") for i in categories.get("items", [])])
        all_items.extend([(i, "weapon") for i in categories.get("weapons", [])])
        all_items.extend([(i, "materia") for i in categories.get("materia", [])])
        all_items.extend([(i, "key_item") for i in categories.get("key_items", [])])
        
        for item_id, item_type in all_items:
            records.append({
                "item_id": item_id,
                "type": item_type
            })
        
        return sorted(records, key=lambda x: x["item_id"])
    
    def extract_shop_records(self) -> List[Dict]:
        """Extract shop records."""
        records = []
        categories = self.categorize_names()
        
        shop_entries = categories.get("shop_entries", [])
        counters = categories.get("shop_counters", [])
        
        for entry in shop_entries:
            item_id = entry.replace("ShopItem_", "")
            records.append({
                "entry_id": entry,
                "item_id": item_id,
                "type": "shop_item"
            })
        
        for counter in counters:
            records.append({
                "entry_id": counter,
                "type": "counter"
            })
        
        return sorted(records, key=lambda x: x["entry_id"])
    
    def extract_mob_records(self) -> List[Dict]:
        """Extract mob template records."""
        records = []
        categories = self.categorize_names()
        
        mobs = categories.get("mob_templates", [])
        territories = categories.get("territories", [])
        
        for mob in mobs:
            # Try to extract territory and index from mob name
            # e.g., "mob_ter03_01_01"
            match = re.match(r"mob_ter(\d+)_(\d+)_(\d+)", mob)
            if match:
                records.append({
                    "mob_id": mob,
                    "territory": f"ter{match.group(1)}",
                    "group": match.group(2),
                    "index": match.group(3)
                })
            else:
                records.append({
                    "mob_id": mob
                })
        
        return sorted(records, key=lambda x: x["mob_id"])
    
    def extract_territory_records(self) -> List[Dict]:
        """Extract territory records."""
        records = []
        categories = self.categorize_names()
        
        territories = categories.get("territories", [])
        
        for ter in territories:
            # e.g., "ter03_01"
            match = re.match(r"ter(\d+)_?(\d+)?", ter)
            if match:
                records.append({
                    "territory_id": ter,
                    "region": match.group(1),
                    "subregion": match.group(2) if match.group(2) else None
                })
            else:
                records.append({
                    "territory_id": ter
                })
        
        return sorted(records, key=lambda x: x["territory_id"])
    
    def extract_craft_records(self) -> List[Dict]:
        """Extract crafting recipe records."""
        records = []
        categories = self.categorize_names()
        
        craft_entries = categories.get("craft_entries", [])
        
        for entry in craft_entries:
            # e.g., "CraftItem_E_ACC_0001"
            result_item = entry.replace("CraftItem_", "")
            records.append({
                "recipe_id": entry,
                "result_item": result_item
            })
        
        return sorted(records, key=lambda x: x["recipe_id"])
    
    def extract_all(self) -> Dict[str, Any]:
        """Extract all structured data from the JSON."""
        result = {
            "source_file": self.data.get("file", "unknown"),
            "engine_version": self.data.get("engineVersion", "unknown"),
            "name_count": len(self.names),
            "categories": self.categorize_names()
        }
        
        # Determine what type of data this file contains
        categories = result["categories"]
        
        # Add extracted records based on what's present
        if categories.get("colosseum_battles"):
            result["colosseum_battles"] = self.extract_colosseum_records()
        
        if categories.get("enemies"):
            result["enemies"] = self.extract_enemy_records()
        
        if categories.get("summons"):
            result["summons"] = self.extract_summon_records()
        
        if categories.get("equipment") or categories.get("items") or categories.get("materia"):
            result["items"] = self.extract_reward_records()
        
        if categories.get("shop_entries") or categories.get("shop_counters"):
            result["shop"] = self.extract_shop_records()
        
        if categories.get("mob_templates"):
            result["mobs"] = self.extract_mob_records()
        
        if categories.get("territories"):
            result["territories"] = self.extract_territory_records()
        
        if categories.get("craft_entries"):
            result["crafting"] = self.extract_craft_records()
        
        if categories.get("rewards"):
            result["reward_ids"] = sorted(categories["rewards"])
        
        if categories.get("bgm"):
            result["bgm_tracks"] = sorted(categories["bgm"])
        
        return result


def process_file(input_path: str, output_path: str = None) -> Dict:
    """Process a single JSON file."""
    print(f"Processing: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    parser = ExportedJsonParser(data)
    result = parser.extract_all()
    
    # Determine output path
    if output_path is None:
        output_path = input_path.replace(".json", "_parsed.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved to: {output_path}")
    
    # Print summary
    for key, value in result.items():
        if isinstance(value, list) and key not in ["categories", "reward_ids", "bgm_tracks"]:
            print(f"  {key}: {len(value)} records")
    
    return result


def process_all_files(data_folder: str):
    """Process all JSON files in the data folder."""
    folder = Path(data_folder)
    json_files = list(folder.glob("*.json"))
    
    # Filter out already-parsed files and summary files
    json_files = [f for f in json_files if not f.stem.endswith("_parsed") and not f.stem.startswith("_")]
    
    print(f"Found {len(json_files)} JSON files to process\n")
    
    all_results = {}
    
    for json_file in json_files:
        try:
            output_file = json_file.parent / f"{json_file.stem}_parsed.json"
            result = process_file(str(json_file), str(output_file))
            all_results[json_file.stem] = {
                "status": "success",
                "name_count": result.get("name_count", 0)
            }
            print()
        except Exception as e:
            print(f"  ERROR: {e}")
            all_results[json_file.stem] = {"status": "error", "error": str(e)}
    
    # Create a consolidated summary
    consolidated = consolidate_results(folder)
    
    # Save summary
    summary_path = folder / "_parse_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "files_processed": all_results,
            "totals": consolidated["totals"]
        }, f, indent=2)
    
    print(f"Summary saved to: {summary_path}")
    print(f"\n=== TOTALS ===")
    for key, count in consolidated["totals"].items():
        print(f"  {key}: {count}")


def consolidate_results(folder: Path) -> Dict:
    """Consolidate all parsed results into summary data."""
    parsed_files = list(folder.glob("*_parsed.json"))
    
    all_enemies = set()
    all_summons = set()
    all_items = set()
    all_colosseum = set()
    all_rewards = set()
    all_shops = set()
    all_mobs = set()
    all_territories = set()
    
    for pf in parsed_files:
        try:
            with open(pf, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for e in data.get("enemies", []):
                all_enemies.add(e.get("enemy_id"))
            
            for s in data.get("summons", []):
                all_summons.add(s.get("summon_id"))
            
            for i in data.get("items", []):
                all_items.add(i.get("item_id"))
            
            for c in data.get("colosseum_battles", []):
                all_colosseum.add(c.get("battle_id"))
            
            for r in data.get("reward_ids", []):
                all_rewards.add(r)
            
            for s in data.get("shop", []):
                all_shops.add(s.get("entry_id"))
            
            for m in data.get("mobs", []):
                all_mobs.add(m.get("mob_id"))
            
            for t in data.get("territories", []):
                all_territories.add(t.get("territory_id"))
                
        except Exception as e:
            print(f"Warning: Could not process {pf}: {e}")
    
    # Save consolidated data
    consolidated = {
        "enemies": sorted(all_enemies - {None}),
        "summons": sorted(all_summons - {None}),
        "items": sorted(all_items - {None}),
        "colosseum_battles": sorted(all_colosseum - {None}),
        "reward_ids": sorted(all_rewards - {None}),
        "shop_entries": sorted(all_shops - {None}),
        "mob_templates": sorted(all_mobs - {None}),
        "territories": sorted(all_territories - {None}),
        "totals": {
            "enemies": len(all_enemies - {None}),
            "summons": len(all_summons - {None}),
            "items": len(all_items - {None}),
            "colosseum_battles": len(all_colosseum - {None}),
            "reward_ids": len(all_rewards - {None}),
            "shop_entries": len(all_shops - {None}),
            "mob_templates": len(all_mobs - {None}),
            "territories": len(all_territories - {None})
        }
    }
    
    consolidated_path = folder / "_consolidated_data.json"
    with open(consolidated_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)
    
    print(f"Consolidated data saved to: {consolidated_path}")
    
    return consolidated


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FFVII Rebirth Exported JSON Parser")
        print()
        print("Usage:")
        print("  Single file:  python parse_exported_json.py <json_file> [output.json]")
        print("  All files:    python parse_exported_json.py --all <data_folder>")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        if len(sys.argv) < 3:
            print("Error: Please specify the data folder")
            sys.exit(1)
        process_all_files(sys.argv[2])
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        process_file(input_file, output_file)
