#!/usr/bin/env python3
"""
FF7 Rebirth Materia Price Randomizer
Randomizes sell prices for materia in Materia.uasset
Uses filtered retoc extraction from game paks to ensure fresh assets
"""

import os
import json
import subprocess
import shutil
import random
import argparse
from pathlib import Path

# Configuration
GAME_PAKS_DIR = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks"
RETOC_EXE = "bin/retoc_filtered.exe"
UASSETGUI_EXE = r"UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows\UAssetGUI.exe"
MAPPINGS_FILE = r"bin/Mappings/4.26.1-0+++UE4+Release-4.26-End.usmap"
UNPACK_FRESH_DIR = "UnpackFresh_Materia"

# Base materia sell prices (approximate values from game)
# These will be used to populate empty SaleValueLv_Array
BASE_MATERIA_PRICES = {
    # Magic Materia (green)
    "M_MAG_001": 300,   # Fire
    "M_MAG_002": 300,   # Blizzard
    "M_MAG_003": 300,   # Thunder
    "M_MAG_004": 250,   # Aero (Wind)
    "M_MAG_005": 400,   # Cure
    "M_MAG_006": 500,   # Raise
    "M_MAG_007": 300,   # Poison
    "M_MAG_008": 400,   # Barrier
    "M_MAG_009": 400,   # Time
    "M_MAG_010": 400,   # Bind
    "M_MAG_011": 400,   # Subversion
    "M_MAG_012": 400,   # Revival
    "M_MAG_101": 600,   # Fira
    "M_MAG_102": 600,   # Blizzara
    "M_MAG_103": 600,   # Thundara
    "M_MAG_104": 500,   # Aerora
    "M_MAG_105": 800,   # Cura
    "M_MAG_106": 1000,  # Raise (upgraded)
    "M_MAG_107": 600,   # Poisona
    "M_MAG_108": 800,   # Manaward
    "M_MAG_109": 800,   # Haste
    "M_MAG_110": 800,   # Stop
    "M_MAG_111": 800,   # Breach
    
    # Support Materia (blue)
    "M_SUP_001": 500,   # Magnify
    "M_SUP_002": 500,   # HP Absorption
    "M_SUP_003": 500,   # MP Absorption
    "M_SUP_004": 500,   # Elemental
    "M_SUP_005": 500,   # Synergy
    "M_SUP_006": 500,   # AP Up
    "M_SUP_007": 500,   # Item Master
    
    # Command Materia (yellow)
    "M_CMD_001": 400,   # Assess
    "M_CMD_002": 400,   # Enemy Skill
    "M_CMD_003": 400,   # Steal
    "M_CMD_004": 400,   # Sense
    "M_CMD_005": 400,   # Prayer
    "M_CMD_006": 400,   # Chakra
    "M_CMD_007": 400,   # ATB Boost
    "M_CMD_008": 400,   # ATB Stagger
    
    # Complete/Independent Materia (purple)
    "M_SPT_001": 600,   # HP Up
    "M_SPT_002": 600,   # MP Up
    "M_SPT_003": 600,   # Auto-Cure
    "M_SPT_004": 600,   # Steadfast Block
    "M_SPT_005": 600,   # First Strike
    "M_SPT_006": 600,   # ATB Assist
    "M_SPT_007": 600,   # Skill Master
    "M_SPT_008": 600,   # Item Economizer
    "M_SPT_009": 600,   # Gil Up
    "M_SPT_010": 600,   # EXP Up
    "M_SPT_011": 600,   # Luck Up
    
    # Summon Materia (red)
    "M_SUM_001": 0,     # Chocobo (can't sell)
    "M_SUM_002": 0,     # Shiva
    "M_SUM_003": 0,     # Ifrit
    "M_SUM_004": 0,     # Leviathan
    "M_SUM_010": 0,     # Fat Chocobo
}

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

def extract_from_game_paks(output_dir):
    """Extract fresh Materia.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")
    
    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False
    
    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False
    
    # Extract Materia from game paks (Zen to Legacy conversion)
    extract_dir = os.path.join(output_dir, "extracted_from_game_materia")
    os.makedirs(extract_dir, exist_ok=True)
    
    # Use filter "Materia" to get DataObject/Resident/Materia.uasset
    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "Materia" --version UE4_26'
    
    if not run_command(cmd, "Extracting Materia from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False
    
    # Find the specific Materia.uasset we need (DataObject/Resident/Materia.uasset)
    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "Materia.uasset"
    if not target_file.exists():
        log(f"✗ Materia.uasset not found at expected path: {target_file}", "red")
        return False
    
    log(f"✓ Found Materia.uasset ({target_file.stat().st_size:,} bytes)", "green")
    
    # Copy to UnpackFresh directory
    materia_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(materia_dir, exist_ok=True)
    
    # Copy .uasset and .uexp
    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(materia_dir, f"Materia{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied Materia{ext}", "green")
    
    return True

def export_to_json(output_dir):
    """Export Materia.uasset to JSON"""
    log("\n=== STEP 1: EXPORTING TO JSON ===", "cyan")
    
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Materia.uasset")
    json_path = os.path.join(output_dir, "temp", "Materia.json")
    
    if not os.path.exists(uasset_path):
        log(f"✗ Materia.uasset not found at: {uasset_path}", "red")
        return False
    
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Exporting Materia to JSON"):
        log("✗ JSON export failed", "red")
        return False
    
    if not os.path.exists(json_path):
        log("✗ JSON file was not created", "red")
        return False
    
    size = os.path.getsize(json_path)
    log(f"✓ JSON exported successfully ({size:,} bytes)", "green")
    return True

def create_sale_value_array(base_price, num_levels=4, randomize=True, seed_offset=0, min_mult=0.5, max_mult=2.0):
    """Create a SaleValueLv_Array with values for each materia level"""
    if base_price <= 0:
        return []  # Can't sell this materia
    
    values = []
    for level in range(num_levels):
        # Price increases with level (1.0x, 1.5x, 2.0x, 2.5x)
        level_multiplier = 1.0 + (level * 0.5)
        price = int(base_price * level_multiplier)
        
        if randomize:
            # Apply random multiplier
            random_mult = random.uniform(min_mult, max_mult)
            price = int(price * random_mult)
            price = max(1, price)  # Ensure at least 1 gil
        
        # Create the property entry
        values.append({
            "$type": "UAssetAPI.GameTypes.FF7Rebirth.PropertyTypes.FF7IntProperty, UAssetAPI",
            "Name": "SaleValueLv_Array",
            "ArrayIndex": 0,
            "IsZero": False,
            "PropertyTagFlags": "None",
            "PropertyTagExtensions": "NoExtension",
            "Value": price
        })
    
    return values

def randomize_prices(output_dir, seed, min_mult=0.5, max_mult=2.0):
    """Randomize materia sell prices in JSON"""
    log(f"\n=== STEP 2: RANDOMIZING MATERIA PRICES (seed: {seed}) ===", "cyan")
    log(f"  Price multiplier range: {min_mult}x - {max_mult}x", "yellow")
    
    json_path = os.path.join(output_dir, "temp", "Materia.json")
    
    if not os.path.exists(json_path):
        log(f"✗ JSON file not found: {json_path}", "red")
        return False
    
    # Load JSON
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Set random seed for reproducibility
    random.seed(seed)
    
    # Find and randomize prices
    exports = data.get('Exports', [])
    if not exports:
        log("✗ No exports found in JSON", "red")
        return False
    
    export = exports[0]
    data_array = export.get('Data', [])
    
    materia_modified = 0
    arrays_populated = 0
    
    log(f"Scanning {len(data_array)} materia entries...", "yellow")
    
    for idx, materia_data in enumerate(data_array):
        materia_name = materia_data.get('Name', 'unknown')
        properties = materia_data.get('Value', [])
        
        if not properties:
            continue
        
        # Find SaleValueLv_Array property
        sale_array_prop = None
        sale_array_idx = None
        lv_max = 4  # Default max level
        
        for i, prop in enumerate(properties):
            prop_name = prop.get('Name')
            if prop_name == 'SaleValueLv_Array':
                sale_array_prop = prop
                sale_array_idx = i
            elif prop_name == 'LvMax':
                lv_max = prop.get('Value', 4)
        
        if sale_array_prop is None:
            continue
        
        # Get base price for this materia
        base_price = BASE_MATERIA_PRICES.get(materia_name, 500)  # Default 500 if not in our list
        
        if base_price <= 0:
            # Can't sell this materia (summons, etc.)
            continue
        
        # Check if array is empty and needs to be populated
        current_values = sale_array_prop.get('Value', [])
        
        if len(current_values) == 0:
            # Populate empty array with randomized values
            new_values = create_sale_value_array(
                base_price, 
                num_levels=max(1, lv_max),
                randomize=True,
                seed_offset=idx,
                min_mult=min_mult,
                max_mult=max_mult
            )
            sale_array_prop['Value'] = new_values
            arrays_populated += 1
            materia_modified += 1
            log(f"  + Populated {materia_name}: {len(new_values)} levels", "green")
        else:
            # Randomize existing values
            for val_entry in current_values:
                original = val_entry.get('Value', 0)
                if original > 0:
                    new_price = int(original * random.uniform(min_mult, max_mult))
                    new_price = max(1, new_price)
                    val_entry['Value'] = new_price
            materia_modified += 1
    
    log(f"✓ Modified {materia_modified} materia entries", "green")
    log(f"  - Arrays populated: {arrays_populated}", "green")
    
    # Save randomized JSON
    randomized_path = os.path.join(output_dir, "temp", "Materia_randomized.json")
    with open(randomized_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    log(f"✓ Saved randomized JSON to {randomized_path}", "green")
    return True

def import_from_json(output_dir):
    """Import randomized JSON back to uasset"""
    log("\n=== STEP 3: IMPORTING FROM JSON ===", "cyan")
    
    json_path = os.path.join(output_dir, "temp", "Materia_randomized.json")
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Materia.uasset")
    
    if not os.path.exists(json_path):
        log(f"✗ Randomized JSON not found: {json_path}", "red")
        return False
    
    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Importing JSON to Materia.uasset"):
        log("✗ JSON import failed", "red")
        return False
    
    log("✓ Successfully imported JSON back to uasset", "green")
    return True

def repack_to_zen(output_dir, mod_name="RandomizedMateriaPrices"):
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
    
    # Convert legacy to Zen format
    cmd = f'"{ RETOC_EXE}" to-zen "{legacy_dir}" "{zen_output}" --version UE4_26'
    
    if not run_command(cmd, "Converting to Zen format"):
        log("✗ Zen conversion failed", "red")
        return False
    
    # retoc outputs files without .utoc extension, need to rename
    utoc_no_ext = zen_output
    utoc_with_ext = zen_output + ".utoc"
    
    if os.path.exists(utoc_no_ext):
        shutil.move(utoc_no_ext, utoc_with_ext)
        log(f"  ✓ Renamed output to {utoc_with_ext}", "green")
    
    # Check output files
    expected_files = ['.utoc', '.ucas', '.pak']
    base_path = zen_output
    
    for ext in expected_files:
        file_path = base_path + ext
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            log(f"  ✓ Created {os.path.basename(file_path)} ({size:,} bytes)", "green")
        else:
            log(f"  ✗ Missing {ext} file", "red")
    
    return True

def deploy_mod(output_dir, mod_name="RandomizedMateriaPrices"):
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
    parser = argparse.ArgumentParser(description='Randomize FF7 Rebirth Materia Prices')
    parser.add_argument('seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--min-mult', type=float, default=0.5, help='Minimum price multiplier (default: 0.5)')
    parser.add_argument('--max-mult', type=float, default=2.0, help='Maximum price multiplier (default: 2.0)')
    parser.add_argument('--auto-deploy', action='store_true', help='Automatically deploy to game mods folder')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    
    args = parser.parse_args()
    
    log("=" * 60, "cyan")
    log("FF7 REBIRTH MATERIA PRICE RANDOMIZER", "cyan")
    log("=" * 60, "cyan")
    
    # Run the pipeline
    if not extract_from_game_paks(args.output_dir):
        return 1
    
    if not export_to_json(args.output_dir):
        return 1
    
    if not randomize_prices(args.output_dir, args.seed, args.min_mult, args.max_mult):
        return 1
    
    if not import_from_json(args.output_dir):
        return 1
    
    if not repack_to_zen(args.output_dir):
        return 1
    
    if args.auto_deploy:
        if not deploy_mod(args.output_dir):
            return 1
    
    log("\n" + "=" * 60, "green")
    log("MATERIA PRICE RANDOMIZATION COMPLETE!", "green")
    log("=" * 60, "green")
    
    return 0

if __name__ == '__main__':
    exit(main())
