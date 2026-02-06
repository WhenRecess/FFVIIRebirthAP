#!/usr/bin/env python3
"""
FF7 Rebirth Shop Inventory Randomizer
Randomizes which items and materia are for sale in shops
Uses filtered retoc extraction from game paks to ensure fresh assets
"""

import os
import json
import subprocess
import shutil
import random
import argparse
from pathlib import Path
from collections import defaultdict

# Configuration
GAME_PAKS_DIR = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks"
RETOC_EXE = "bin/retoc_filtered.exe"
UASSETGUI_EXE = r"UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows\UAssetGUI.exe"
UNPACK_FRESH_DIR = "UnpackFresh_ShopInventory"
UNPACK_FRESH_MATERIA_DIR = "UnpackFresh_Materia"


def log(message, color="white"):
    """Print colored log messages"""
    colors = {
        "cyan": "\033[96m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    try:
        print(f"{colors.get(color, '')}{message}{colors['reset']}")
    except UnicodeEncodeError:
        # Fallback for terminals that can't handle Unicode
        safe_msg = message.encode('ascii', 'replace').decode('ascii')
        print(f"{colors.get(color, '')}{safe_msg}{colors['reset']}")


def ensure_p_suffix(filename):
    """Ensure filename has _P suffix before extension"""
    base = filename.replace('.utoc', '').replace('.pak', '').replace('.ucas', '')
    if not base.endswith('_P'):
        base += '_P'
    return base


def run_command(cmd, description=""):
    """Run a command and return success status"""
    if description:
        log(f"▶ {description}", "cyan")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr:
            print(result.stderr.strip())
        return result.returncode == 0
    except Exception as e:
        log(f"✗ Error: {e}", "red")
        return False


def load_item_pool(output_dir):
    """Load available items and materia from parsed data and Materia.uasset"""
    pool_path = Path(__file__).parent / "data" / "_reward_parsed.json"
    if not pool_path.exists():
        log(f"✗ Reward pool not found: {pool_path}", "red")
        return None

    with open(pool_path, 'r', encoding='utf-8') as f:
        parsed = json.load(f)

    items = defaultdict(list)
    # Parsed is a dict where keys are reward IDs and values have 'items' arrays
    for reward_id, reward_data in parsed.items():
        for item in reward_data.get('items', []):
            item_id = item.get('name', '')
            if not item_id:
                continue
            
            # Categorize by prefix
            if item_id.startswith('M_'):
                items['materia'].append(item_id)
            elif item_id.startswith('IT_') or item_id.startswith('it_'):
                # Exclude key items
                if not item_id.startswith('it_key'):
                    items['consumables'].append(item_id)
            elif item_id.startswith('E_ACC_'):
                items['accessories'].append(item_id)
            elif item_id.startswith('E_ARM_'):
                items['armor'].append(item_id)
            elif item_id.startswith('W_'):
                items['weapons'].append(item_id)

    # Load materia from Materia.uasset JSON (if available)
    materia_json_path = os.path.join(output_dir, "temp", "Materia.json")
    materia_ids = set()
    if os.path.exists(materia_json_path):
        try:
            with open(materia_json_path, 'r', encoding='utf-8') as f:
                materia_data = json.load(f)

            def walk_materia(obj):
                if isinstance(obj, dict):
                    # Only extract Name from FKey entries (materia IDs in the hash map)
                    obj_type = obj.get('$type', '')
                    if 'FKey' in obj_type:
                        name = obj.get('Name')
                        if isinstance(name, str) and name.startswith('M_'):
                            materia_ids.add(name)
                    
                    for val in obj.values():
                        walk_materia(val)
                elif isinstance(obj, list):
                    for item in obj:
                        walk_materia(item)

            walk_materia(materia_data)
        except Exception as e:
            log(f"✗ Failed to load Materia.json: {e}", "red")
    else:
        log(f"✗ Materia.json not found: {materia_json_path}", "red")

    if materia_ids:
        items['materia'].extend(list(materia_ids))

    # Convert to dict of lists and remove duplicates
    item_pool = {k: list(set(v)) for k, v in items.items()}
    
    # Ensure all categories exist
    for category in ['materia', 'consumables', 'accessories', 'armor', 'weapons']:
        if category not in item_pool:
            item_pool[category] = []
    
    log(f"✓ Loaded {len(item_pool['materia'])} materia", "green")
    log(f"✓ Loaded {len(item_pool['consumables'])} consumable items", "green")
    log(f"✓ Loaded {len(item_pool['accessories'])} accessories", "green")
    log(f"✓ Loaded {len(item_pool['armor'])} armor pieces", "green")
    log(f"✓ Loaded {len(item_pool['weapons'])} weapons", "green")
    
    return item_pool


def extract_materia_from_game_paks(output_dir):
    """Extract fresh Materia.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0B: EXTRACTING MATERIA FROM GAME PAKS ===", "cyan")

    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    extract_dir = os.path.join(output_dir, "extracted_from_game_materia")
    os.makedirs(extract_dir, exist_ok=True)

    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "Materia" --version UE4_26'

    if not run_command(cmd, "Extracting Materia from game paks (Zen to Legacy)"):
        log("✗ Failed to extract Materia from game paks", "red")
        return False

    expected = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "Materia.uasset"
    if expected.exists():
        target_file = expected
    else:
        candidates = list(Path(extract_dir).rglob("Materia.uasset"))
        if not candidates:
            log("✗ Materia.uasset not found after extraction", "red")
            return False
        target_file = candidates[0]

    log(f"✓ Found Materia.uasset ({target_file.stat().st_size:,} bytes)", "green")

    materia_dir = os.path.join(output_dir, UNPACK_FRESH_MATERIA_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(materia_dir, exist_ok=True)

    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(materia_dir, f"Materia{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied Materia{ext}", "green")

    return True


def export_materia_to_json(output_dir):
    """Export Materia.uasset to JSON"""
    log("\n=== STEP 1B: EXPORTING MATERIA TO JSON ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_MATERIA_DIR, "End", "Content", "DataObject", "Resident", "Materia.uasset")
    json_path = os.path.join(output_dir, "temp", "Materia.json")

    if not os.path.exists(uasset_path):
        log(f"✗ Materia.uasset not found at: {uasset_path}", "red")
        return False

    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Exporting Materia to JSON"):
        log("✗ Materia JSON export failed", "red")
        return False

    if not os.path.exists(json_path):
        log("✗ Materia JSON file was not created", "red")
        return False

    size = os.path.getsize(json_path)
    log(f"✓ Materia JSON exported successfully ({size:,} bytes)", "green")
    return True


def extract_from_game_paks(output_dir):
    """Extract fresh ShopItem.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")
    
    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False
    
    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False
    
    # Extract ShopItem from game paks (Zen to Legacy conversion)
    extract_dir = os.path.join(output_dir, "extracted_from_game")
    os.makedirs(extract_dir, exist_ok=True)
    
    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "ShopItem" --version UE4_26'
    
    if not run_command(cmd, "Extracting ShopItem from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False
    
    # Find the specific ShopItem.uasset we need
    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "ShopItem.uasset"
    if not target_file.exists():
        log(f"✗ ShopItem.uasset not found at expected path: {target_file}", "red")
        return False
    
    log(f"✓ Found ShopItem.uasset ({target_file.stat().st_size:,} bytes)", "green")
    
    # Copy to UnpackFresh directory
    shop_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(shop_dir, exist_ok=True)
    
    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(shop_dir, f"ShopItem{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied ShopItem{ext}", "green")
    
    return True


def export_to_json(output_dir):
    """Export ShopItem.uasset to JSON"""
    log("\n=== STEP 1: EXPORTING TO JSON ===", "cyan")
    
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "ShopItem.uasset")
    json_path = os.path.join(output_dir, "temp", "ShopItem.json")
    
    if not os.path.exists(uasset_path):
        log(f"✗ ShopItem.uasset not found at: {uasset_path}", "red")
        return False
    
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Exporting ShopItem to JSON"):
        log("✗ JSON export failed", "red")
        return False
    
    if not os.path.exists(json_path):
        log("✗ JSON file was not created", "red")
        return False
    
    size = os.path.getsize(json_path)
    log(f"✓ JSON exported successfully ({size:,} bytes)", "green")
    return True


def get_fname_base(name):
    """
    Parse FName like UAssetAPI does to get the base name.
    
    UAssetAPI parses names like 'M_SUM_101' as base='M_SUM' with Number=102.
    This means if we add 'M_SUM_101' to the NameMap, UAssetAPI will look for 'M_SUM'
    instead! We need to add the BASE name to ensure it can be found.
    
    Names ending with _0XX (number starting with 0) are NOT parsed this way.
    """
    if not name:
        return name
    
    # Check if ends with digit
    if not name[-1].isdigit():
        return name
    
    # Find the last underscore followed by digits
    import re
    match = re.match(r'^(.+)_([0-9]+)$', name)
    if match:
        base, num_str = match.groups()
        # Only parse if number doesn't start with 0
        if num_str and num_str[0] != '0':
            return base
    
    return name


def add_to_namemap(data, new_names):
    """Add new item names to the NameMap if they don't exist.
    
    Also adds BASE names for items with numeric suffixes (e.g., M_SUM for M_SUM_101)
    because UAssetAPI's FName parsing will look for the base name.
    """
    if 'NameMap' not in data:
        log("✗ NameMap not found in JSON", "red")
        return False
    
    existing = set(data['NameMap'])
    added_count = 0
    
    # Collect all names we need to add (including base names)
    names_to_add = set()
    for name in new_names:
        if name:
            names_to_add.add(name)
            # Also add the base name for items with numeric suffixes
            base = get_fname_base(name)
            if base and base != name:
                names_to_add.add(base)
    
    for name in names_to_add:
        if name not in existing:
            data['NameMap'].append(name)
            existing.add(name)
            added_count += 1
    
    if added_count > 0:
        log(f"✓ Added {added_count} new names to NameMap", "green")
    
    return True


def collect_all_nameproperty_values(data):
    """Collect all NameProperty values from the JSON to ensure they're in NameMap"""
    all_names = set()
    
    def walk(obj):
        if isinstance(obj, dict):
            # Check for FF7NameProperty types
            obj_type = obj.get('$type', '')
            if 'NameProperty' in obj_type:
                val = obj.get('Value')
                if val is not None and isinstance(val, str) and val:
                    all_names.add(val)
            
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)
    
    walk(data.get('Exports', []))
    return all_names


def randomize_shop_inventory(output_dir, seed, item_pool, options):
    """Randomize shop inventory in the JSON file"""
    log(f"\n=== STEP 2: RANDOMIZING SHOP INVENTORY (seed: {seed}) ===", "cyan")
    
    json_path = os.path.join(output_dir, "temp", "ShopItem.json")
    
    if not os.path.exists(json_path):
        log(f"✗ JSON file not found: {json_path}", "red")
        return False
    
    # Load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Track changes and new names
    shops_modified = defaultdict(int)
    new_names = set()
    all_item_ids = set()
    excluded_shops = set(options.get('exclude_shops', []))
    items_only = options.get('items_only', False)
    materia_only = options.get('materia_only', False)
    all_items = (
        item_pool.get('materia', [])
        + item_pool.get('consumables', [])
        + item_pool.get('accessories', [])
        + item_pool.get('armor', [])
        + item_pool.get('weapons', [])
    )
    non_materia_items = (
        item_pool.get('consumables', [])
        + item_pool.get('accessories', [])
        + item_pool.get('armor', [])
        + item_pool.get('weapons', [])
    )
    
    def should_randomize_shop(shop_name):
        """Check if this shop should be randomized"""
        for excluded in excluded_shops:
            if excluded.lower() in shop_name.lower():
                return False
        return True
    
    def get_random_item_for_slot(original_item_id, item_pool):
        """Get a random item, allowing materia <-> item swaps by default"""
        if materia_only:
            if item_pool['materia']:
                return random.choice(item_pool['materia'])
            return original_item_id

        if items_only:
            if non_materia_items:
                return random.choice(non_materia_items)
            return original_item_id

        if all_items:
            return random.choice(all_items)

        return original_item_id
    
    def walk_and_randomize(obj, path=""):
        """Recursively walk JSON and randomize ItemId properties"""
        if isinstance(obj, dict):
            name = obj.get('Name', '')
            
            # Check for ItemId property (Name == "ItemId" and has a Value field)
            if name == 'ItemId' and 'Value' in obj:
                original_id = obj.get('Value')
                
                # Make sure it's a string (not null or other type)
                if isinstance(original_id, str) and original_id:
                    all_item_ids.add(original_id)
                    # Extract shop name from path (the Data array item name)
                    shop_name = "Unknown"
                    if 'Data[' in path:
                        # Extract the shop item name from the path
                        parts = path.split('/')
                        for part in parts:
                            if part.startswith('Data['):
                                # This is the array index, the actual name is in the Name field of that object
                                # We'll use the path context instead
                                pass
                    
                    if should_randomize_shop(path):
                        new_id = get_random_item_for_slot(original_id, item_pool)
                        
                        if new_id != original_id:
                            obj['Value'] = new_id
                            new_names.add(new_id)  # Track new item name
                            all_item_ids.add(new_id)
                            # Extract a cleaner shop name for stats
                            if 'ShopItem' in path or 'ChadleyShopItem' in path:
                                shops_modified['ShopItems'] += 1
                            else:
                                shops_modified[shop_name] += 1
            
            # Recurse into nested objects
            for key, val in obj.items():
                new_path = f"{path}/{key}" if path else key
                walk_and_randomize(val, new_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                walk_and_randomize(item, new_path)
    
    # Process the exports
    exports = data.get('Exports', [])
    if not exports:
        log("✗ No exports found in JSON", "red")
        return False
    
    for export in exports:
        if 'Data' in export:
            walk_and_randomize(export['Data'], "ShopItem")
    
    # Collect ALL NameProperty values (not just ItemId) to ensure they're in NameMap
    # This fixes an issue where the original JSON has NameProperty values not in NameMap
    all_nameprop_values = collect_all_nameproperty_values(data)
    log(f"\nEnsuring all {len(all_nameprop_values)} NameProperty values are in NameMap...", "yellow")
    if not add_to_namemap(data, all_nameprop_values):
        log("✗ Failed to update NameMap", "red")
        return False
    
    # 
    # Save modified JSON
    randomized_path = os.path.join(output_dir, "temp", "ShopItem_randomized.json")
    with open(randomized_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    total_changes = sum(shops_modified.values())
    log(f"✓ Modified {total_changes} shop entries across {len(shops_modified)} shop types", "green")
    
    if shops_modified:
        log("\nShop types modified:", "yellow")
        for shop, count in sorted(shops_modified.items())[:10]:
            log(f"  {shop}: {count} items", "cyan")
        if len(shops_modified) > 10:
            log(f"  ... and {len(shops_modified) - 10} more shop types", "cyan")
    
    return True


def import_from_json(output_dir):
    """Import JSON back to .uasset format"""
    log("\n=== STEP 3: IMPORTING FROM JSON ===", "cyan")
    
    json_path = os.path.join(output_dir, "temp", "ShopItem_randomized.json")
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "ShopItem.uasset")
    
    if not os.path.exists(json_path):
        log(f"✗ JSON file not found: {json_path}", "red")
        return False
    
    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Importing ShopItem from JSON"):
        log("✗ Import failed", "red")
        return False
    
    if not os.path.exists(uasset_path):
        log("✗ .uasset file was not created", "red")
        return False
    
    size = os.path.getsize(uasset_path)
    log(f"✓ Import successful ({size:,} bytes)", "green")
    return True


def repack_to_zen(output_dir, mod_name="RandomizedShopInventory"):
    """Repack to Zen format for game loading"""
    log("\n=== STEP 4: REPACKING TO ZEN FORMAT ===", "cyan")
    
    legacy_dir = os.path.join(output_dir, UNPACK_FRESH_DIR)
    zen_output = os.path.join(output_dir, "output", ensure_p_suffix(mod_name))
    
    os.makedirs(os.path.dirname(zen_output), exist_ok=True)
    
    # Clean up old output files to prevent stale .utoc issues
    for ext in ['', '.utoc', '.pak', '.ucas']:
        old_file = zen_output + ext
        if os.path.exists(old_file):
            os.remove(old_file)
    
    cmd = f'"{ RETOC_EXE}" to-zen "{legacy_dir}" "{zen_output}" --version UE4_26'
    
    if not run_command(cmd, "Converting to Zen format"):
        log("✗ Zen conversion failed", "red")
        return False
    
    utoc_no_ext = zen_output
    utoc_with_ext = zen_output + ".utoc"
    
    if os.path.exists(utoc_no_ext):
        shutil.move(utoc_no_ext, utoc_with_ext)
        log(f"  ✓ Renamed output to {utoc_with_ext}", "green")
    
    expected_files = ['.utoc', '.ucas', '.pak']
    for ext in expected_files:
        file_path = zen_output + ext
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            log(f"  ✓ Created {os.path.basename(file_path)} ({size:,} bytes)", "green")
        else:
            log(f"  ✗ Missing {ext} file", "red")
    
    return True


def deploy_mod(output_dir, mod_name="RandomizedShopInventory"):
    """Deploy mod to game's ~mods folder"""
    log("\n=== STEP 5: DEPLOYING MOD ===", "cyan")
    
    mods_dir = os.path.join(GAME_PAKS_DIR, "~mods")
    os.makedirs(mods_dir, exist_ok=True)
    
    base_name = ensure_p_suffix(mod_name)
    source_base = os.path.join(output_dir, "output", base_name)
    
    for ext in ['.utoc', '.ucas', '.pak']:
        src = source_base + ext
        if os.path.exists(src):
            dst = os.path.join(mods_dir, base_name + ext)
            shutil.copy2(src, dst)
            log(f"  ✓ Deployed {base_name}{ext}", "green")
    
    log(f"✓ Mod deployed to {mods_dir}", "green")
    return True


def main():
    parser = argparse.ArgumentParser(description='Randomize FF7 Rebirth Shop Inventory')
    parser.add_argument('seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--auto-deploy', action='store_true', help='Automatically deploy to game mods folder')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--items-only', action='store_true', help='Only randomize items, not materia')
    parser.add_argument('--materia-only', action='store_true', help='Only randomize materia, not items')
    parser.add_argument('--exclude-shop', action='append', dest='exclude_shops',
                       help='Exclude shop types (can be used multiple times)')
    
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.items_only and args.materia_only:
        log("Error: --items-only and --materia-only cannot be used together", "red")
        return 1
    
    log("=" * 60, "cyan")
    log("FF7 REBIRTH SHOP INVENTORY RANDOMIZER", "cyan")
    log("=" * 60, "cyan")
    log(f"Seed: {args.seed}", "yellow")
    
    if args.items_only:
        log("Mode: Items only", "yellow")
    elif args.materia_only:
        log("Mode: Materia only", "yellow")
    else:
        log("Mode: Mixed items + materia", "yellow")
    
    if args.exclude_shops:
        log(f"Excluding shops: {', '.join(args.exclude_shops)}", "yellow")
    
    # Step 0: Extract ShopItem from game paks
    if not extract_from_game_paks(args.output_dir):
        log("\n✗ FAILED: Could not extract ShopItem from game paks", "red")
        return 1

    # Step 0B: Extract Materia from game paks
    if not extract_materia_from_game_paks(args.output_dir):
        log("\n✗ FAILED: Could not extract Materia from game paks", "red")
        return 1
    
    # Step 1: Export ShopItem to JSON
    if not export_to_json(args.output_dir):
        log("\n✗ FAILED: Could not export to JSON", "red")
        return 1

    # Step 1B: Export Materia to JSON
    if not export_materia_to_json(args.output_dir):
        log("\n✗ FAILED: Could not export Materia to JSON", "red")
        return 1

    # Load item pool (now that Materia.json exists)
    item_pool = load_item_pool(args.output_dir)
    if not item_pool:
        log("\n✗ FAILED: Could not load item pool", "red")
        return 1
    
    # Step 2: Randomize
    options = {
        'exclude_shops': args.exclude_shops or [],
        'items_only': args.items_only,
        'materia_only': args.materia_only
    }
    
    if not randomize_shop_inventory(args.output_dir, args.seed, item_pool, options):
        log("\n✗ FAILED: Randomization failed", "red")
        return 1
    
    # Step 3: Import back to .uasset
    if not import_from_json(args.output_dir):
        log("\n✗ FAILED: Could not import from JSON", "red")
        return 1
    
    # Step 4: Repack to zen
    if not repack_to_zen(args.output_dir):
        log("\n✗ FAILED: Could not repack to zen format", "red")
        return 1
    
    # Step 5: Deploy if requested
    if args.auto_deploy:
        if not deploy_mod(args.output_dir):
            log("\n✗ FAILED: Could not deploy mod", "red")
            return 1
        
        log("\n" + "=" * 60, "green")
        log("SUCCESS! Shop inventory randomization complete!", "green")
        log("=" * 60, "green")
        log("Mod has been deployed to ~mods directory.", "green")
        log("Launch the game to see randomized shop inventories!", "green")
    else:
        log("\n" + "=" * 60, "green")
        log("Shop inventory randomization complete!", "green")
        log("=" * 60, "green")
        log(f"Output files: {args.output_dir}", "yellow")
        log(f"To deploy, run with --auto-deploy flag", "yellow")
    
    return 0


if __name__ == '__main__':
    exit(main())
