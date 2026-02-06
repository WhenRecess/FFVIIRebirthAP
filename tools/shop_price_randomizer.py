#!/usr/bin/env python3
"""
FF7 Rebirth Shop Price Randomizer (JSON Pipeline)
Randomizes OverridePrice_Array values in ShopItem.uasset for all shop entries
Uses the clean JSON pipeline: retoc → UAssetGUI tojson → Python → fromjson → to-zen

Replaces the legacy binary-scanning smart_price_randomizer.py with a structured,
reliable JSON approach matching the rest of the randomizer toolchain.

SHOP TYPES AFFECTED:
  - ShopItem (489 entries) - standard vendors
  - CardShopItem (161) - Queen's Blood card shops
  - GGShopItem (54) - Gold Saucer
  - ChadleyShopItem (35) - Chadley's materia shop
  - MoogleShopItem (27) - Moogle Emporium
  - ChocoboShopItem (24) - Chocobo shops
  - UnderChocoboShopItem (3) - Underground Chocobo
"""

import os
import json
import subprocess
import shutil
import random
import re
import argparse
from pathlib import Path

# Configuration
GAME_PAKS_DIR = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks"
RETOC_EXE = "bin/retoc_filtered.exe"
UASSETGUI_EXE = r"UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows\UAssetGUI.exe"
MAPPINGS_FILE = r"bin/Mappings/4.26.1-0+++UE4+Release-4.26-End.usmap"
UNPACK_FRESH_DIR = "UnpackFresh_ShopItem"
MOD_DEPLOY_DIR = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods"


def log(message, color="white"):
    """Print colored log messages"""
    colors = {
        "cyan": "\033[96m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{message}{colors['reset']}")


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


def get_fname_base(name):
    """Extract FName base name for UAssetAPI compatibility"""
    match = re.match(r'^(.+)_([0-9]+)$', name)
    if match:
        num_str = match.group(2)
        if len(num_str) > 0 and num_str[0] != '0':
            return match.group(1)
    return None


def extract_from_game_paks(output_dir):
    """Extract fresh ShopItem.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")

    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    extract_dir = os.path.join(output_dir, "extracted_from_game")
    os.makedirs(extract_dir, exist_ok=True)

    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "ShopItem" --version UE4_26'

    if not run_command(cmd, "Extracting ShopItem from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False

    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "ShopItem.uasset"
    if not target_file.exists():
        log(f"✗ ShopItem.uasset not found at expected path: {target_file}", "red")
        return False

    log(f"✓ Found ShopItem.uasset ({target_file.stat().st_size:,} bytes)", "green")

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
    """Export ShopItem.uasset to JSON using UAssetGUI"""
    log("\n=== STEP 1: EXPORTING SHOPITEM TO JSON ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "ShopItem.uasset")
    if not os.path.exists(uasset_path):
        log(f"✗ ShopItem.uasset not found at: {uasset_path}", "red")
        return False

    json_path = os.path.join(output_dir, "temp", "ShopItem.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Exporting ShopItem.uasset to JSON"):
        log("✗ Failed to export JSON", "red")
        return False

    if not os.path.exists(json_path):
        log("✗ JSON export failed", "red")
        return False

    size = os.path.getsize(json_path)
    log(f"✓ Exported to {json_path} ({size:,} bytes)", "green")
    return True


def get_shop_type(name):
    """Categorize shop entry by prefix"""
    if name.startswith('CardShopItem'):
        return 'card'
    elif name.startswith('GGShopItem'):
        return 'gold_saucer'
    elif name.startswith('ChadleyShopItem'):
        return 'chadley'
    elif name.startswith('MoogleShopItem'):
        return 'moogle'
    elif name.startswith('ChocoboShopItem') or name.startswith('UnderChocoboShopItem'):
        return 'chocobo'
    elif name.startswith('TestShop'):
        return 'test'
    elif name.startswith('ShopItem'):
        return 'standard'
    return 'unknown'


def randomize_shop_prices(output_dir, seed=None, min_mult=0.5, max_mult=2.0, test_mode=False):
    """Load ShopItem JSON, randomize OverridePrice_Array values, save modified JSON"""
    log("\n=== STEP 2: RANDOMIZING SHOP PRICES ===", "cyan")

    if test_mode:
        log("⚠️ TEST MODE: Setting all prices to 1 gil for testing", "yellow")
    elif seed is not None:
        random.seed(seed)
        log(f"Using seed: {seed}", "yellow")

    log(f"  Price multiplier range: {min_mult}x - {max_mult}x", "yellow")

    json_path = os.path.join(output_dir, "temp", "ShopItem.json")

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        log(f"✗ Failed to load JSON: {e}", "red")
        return False

    if 'Exports' not in data or not data['Exports']:
        log("✗ Unexpected JSON structure (missing 'Exports')", "red")
        return False

    export = data['Exports'][0]
    if 'Data' not in export or not export['Data']:
        log("✗ No Data found in export", "red")
        return False

    from collections import defaultdict
    shop_stats = defaultdict(lambda: {"total": 0, "modified": 0})
    total_prices_modified = 0

    for row in export['Data']:
        entry_name = row.get('Name', '')
        shop_type = get_shop_type(entry_name)
        shop_stats[shop_type]["total"] += 1

        if 'Value' not in row:
            continue

        for prop in row['Value']:
            if prop.get('Name') != 'OverridePrice_Array':
                continue

            arr = prop.get('Value', [])
            if not arr:
                continue

            for elem in arr:
                if not isinstance(elem, dict):
                    continue

                old_price = elem.get('Value', 0)
                if old_price <= 0:
                    continue

                if test_mode:
                    elem['Value'] = 1
                else:
                    multiplier = random.uniform(min_mult, max_mult)
                    new_price = max(1, int(old_price * multiplier))
                    elem['Value'] = new_price

                total_prices_modified += 1
                shop_stats[shop_type]["modified"] += 1

    # Print per-type summary
    for shop_type in sorted(shop_stats.keys()):
        stats = shop_stats[shop_type]
        log(f"  {shop_type}: {stats['modified']} prices modified ({stats['total']} entries)", "yellow")

    log(f"✓ Randomized {total_prices_modified} prices across {len(export['Data'])} shop entries", "green")

    # Ensure FName base names are in NameMap
    add_new_names_to_namemap(data)

    # Save modified JSON
    try:
        with open(json_path, 'w') as f:
            json.dump(data, f)
        log(f"✓ Saved randomized data to {json_path}", "green")
        return True
    except Exception as e:
        log(f"✗ Failed to save JSON: {e}", "red")
        return False


def add_new_names_to_namemap(data):
    """Ensure all entry names and their FName bases are in the NameMap"""
    if 'NameMap' not in data:
        return

    existing = set(data['NameMap'])
    added = set()

    export = data['Exports'][0]
    for row in export.get('Data', []):
        name = row.get('Name', '')
        if name and name not in existing:
            data['NameMap'].append(name)
            existing.add(name)
            added.add(name)

        base = get_fname_base(name)
        if base and base not in existing:
            data['NameMap'].append(base)
            existing.add(base)
            added.add(base)

    if added:
        log(f"  Added {len(added)} names to NameMap", "yellow")


def import_from_json(output_dir):
    """Import modified JSON back to ShopItem.uasset using UAssetGUI"""
    log("\n=== STEP 3: IMPORTING JSON BACK TO SHOPITEM ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "ShopItem.uasset")
    json_path = os.path.join(output_dir, "temp", "ShopItem.json")

    if not os.path.exists(uasset_path):
        log(f"✗ ShopItem.uasset not found at: {uasset_path}", "red")
        return False

    if not os.path.exists(json_path):
        log(f"✗ Modified JSON not found at: {json_path}", "red")
        return False

    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Importing JSON to ShopItem.uasset"):
        log("✗ Failed to import JSON", "red")
        return False

    log(f"✓ Successfully imported randomized shop prices", "green")
    return True


def repack_to_mod(output_dir):
    """Repack ShopItem into Zen format .pak file using retoc"""
    log("\n=== STEP 4: REPACKING TO MOD FILE ===", "cyan")

    unpack_dir = os.path.join(output_dir, UNPACK_FRESH_DIR)

    if not os.path.exists(unpack_dir):
        log(f"✗ Unpack directory not found: {unpack_dir}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    mod_base = ensure_p_suffix('RandomizedShopPrices')
    output_base = os.path.join(output_dir, mod_base)

    # Clean up old output files to prevent stale .utoc issues
    for ext in ['', '.utoc', '.pak', '.ucas']:
        old_file = output_base + ext
        if os.path.exists(old_file):
            os.remove(old_file)

    cmd = f'"{ RETOC_EXE}" to-zen "{unpack_dir}" "{output_base}" --version UE4_26'

    if not run_command(cmd, "Converting to Zen format and repacking"):
        log("✗ Retoc repacking failed", "red")
        return False

    utoc_no_ext = output_base
    utoc_with_ext = output_base + ".utoc"

    if os.path.exists(utoc_no_ext):
        shutil.move(utoc_no_ext, utoc_with_ext)
        log(f"  Renamed {mod_base} -> {mod_base}.utoc", "yellow")

    expected_files = [f"{mod_base}.utoc", f"{mod_base}.pak", f"{mod_base}.ucas"]
    for fname in expected_files:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            log(f"  ✓ Generated {fname} ({os.path.getsize(fpath):,} bytes)", "green")
        else:
            log(f"  ⚠ Missing {fname}", "yellow")

    return True


def deploy_mod(output_dir):
    """Deploy the mod files to game's ~mods directory"""
    log("\n=== STEP 5: DEPLOYING MOD ===", "cyan")

    if not os.path.exists(MOD_DEPLOY_DIR):
        os.makedirs(MOD_DEPLOY_DIR, exist_ok=True)

    mod_files = list(Path(output_dir).glob("RandomizedShopPrices_P.*"))

    if not mod_files:
        log("✗ No mod files found to deploy", "red")
        return False

    # Remove any old shop randomizer mod files (both old and new naming)
    for old_pattern in ["RandomizedShop_Seed*", "RandomizedShop_P.*"]:
        for old_file in Path(MOD_DEPLOY_DIR).glob(old_pattern):
            old_file.unlink()
            log(f"  ✗ Removed old mod file: {old_file.name}", "yellow")

    deployed = []
    for mod_file in mod_files:
        dest = os.path.join(MOD_DEPLOY_DIR, mod_file.name)
        try:
            shutil.copy2(mod_file, dest)
            deployed.append(mod_file.name)
            log(f"  ✓ Deployed {mod_file.name}", "green")
        except Exception as e:
            log(f"  ✗ Failed to deploy {mod_file.name}: {e}", "red")
            return False

    if deployed:
        log(f"✓ Successfully deployed {len(deployed)} mod files to {MOD_DEPLOY_DIR}", "green")
        return True

    return False


def main():
    parser = argparse.ArgumentParser(description="FF7 Rebirth Shop Price Randomizer (JSON Pipeline)")
    parser.add_argument('--seed', type=int, help='Random seed for reproducible randomization')
    parser.add_argument('--min-mult', type=float, default=0.5, help='Minimum price multiplier (default: 0.5x)')
    parser.add_argument('--max-mult', type=float, default=2.0, help='Maximum price multiplier (default: 2.0x)')
    parser.add_argument('--test-mode', action='store_true', help='Set all prices to 1 gil for testing')
    parser.add_argument('--auto-deploy', action='store_true', help='Run full pipeline: extract → export → randomize → import → repack → deploy')

    args = parser.parse_args()
    output_dir = "."

    log("=" * 60, "cyan")
    log("   FF7 REBIRTH SHOP PRICE RANDOMIZER (JSON Pipeline)", "cyan")
    log("=" * 60, "cyan")

    if not args.auto_deploy:
        parser.print_help()
        return

    if not extract_from_game_paks(output_dir):
        return

    if not export_to_json(output_dir):
        return

    if not randomize_shop_prices(output_dir, args.seed, args.min_mult, args.max_mult, args.test_mode):
        return

    if not import_from_json(output_dir):
        return

    if not repack_to_mod(output_dir):
        return

    if not deploy_mod(output_dir):
        return

    log("\n" + "=" * 60, "green")
    log("✓ SHOP PRICE RANDOMIZATION COMPLETE", "green")
    log("=" * 60, "green")
    if args.seed:
        log(f"  Seed: {args.seed}", "green")
    log(f"  Price range: {args.min_mult}x - {args.max_mult}x", "green")


if __name__ == "__main__":
    main()
