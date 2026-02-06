#!/usr/bin/env python3
"""
FF7 Rebirth Item Price Randomizer
Randomizes BuyValue and SaleValue for all items in Item.uasset
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
UNPACK_FRESH_DIR = "UnpackFresh_Item"

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
    """Extract fresh Item.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")
    
    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False
    
    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False
    
    # Extract Item from game paks (Zen to Legacy conversion)
    extract_dir = os.path.join(output_dir, "extracted_from_game")
    os.makedirs(extract_dir, exist_ok=True)
    
    # Use filter "Item" to get DataObject/Resident/Item.uasset
    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "Item" --version UE4_26'
    
    if not run_command(cmd, "Extracting Item from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False
    
    # Find the specific Item.uasset we need (DataObject/Resident/Item.uasset)
    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "Item.uasset"
    if not target_file.exists():
        log(f"✗ Item.uasset not found at expected path: {target_file}", "red")
        return False
    
    log(f"✓ Found Item.uasset ({target_file.stat().st_size:,} bytes)", "green")
    
    # Copy to UnpackFresh directory
    item_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(item_dir, exist_ok=True)
    
    # Copy .uasset and .uexp
    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(item_dir, f"Item{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied Item{ext}", "green")
    
    return True

def export_to_json(output_dir):
    """Export Item.uasset to JSON"""
    log("\n=== STEP 1: EXPORTING TO JSON ===", "cyan")
    
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Item.uasset")
    json_path = os.path.join(output_dir, "temp", "Item.json")
    
    if not os.path.exists(uasset_path):
        log(f"✗ Item.uasset not found at: {uasset_path}", "red")
        return False
    
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Exporting Item to JSON"):
        log("✗ JSON export failed", "red")
        return False
    
    if not os.path.exists(json_path):
        log("✗ JSON file was not created", "red")
        return False
    
    size = os.path.getsize(json_path)
    log(f"✓ JSON exported successfully ({size:,} bytes)", "green")
    return True

def randomize_prices(output_dir, seed, min_mult=0.5, max_mult=2.0):
    """Randomize item prices in JSON"""
    log(f"\n=== STEP 2: RANDOMIZING PRICES (seed: {seed}) ===", "cyan")
    log(f"  Price multiplier range: {min_mult}x - {max_mult}x", "yellow")
    
    json_path = os.path.join(output_dir, "temp", "Item.json")
    
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
    
    buy_modified = 0
    sale_modified = 0
    items_modified = 0
    
    log(f"Scanning {len(data_array)} items...", "yellow")
    
    for item_data in data_array:
        item_name = item_data.get('Name', 'unknown')
        properties = item_data.get('Value', [])
        
        item_had_price = False
        
        for prop in properties:
            prop_name = prop.get('Name')
            
            # Randomize BuyValue
            if prop_name == 'BuyValue':
                original = prop.get('Value', 0)
                if original > 0:
                    new_price = int(original * random.uniform(min_mult, max_mult))
                    new_price = max(1, new_price)  # Ensure at least 1 gil
                    prop['Value'] = new_price
                    buy_modified += 1
                    item_had_price = True
            
            # Randomize SaleValue
            if prop_name == 'SaleValue':
                original = prop.get('Value', 0)
                if original > 0:
                    new_price = int(original * random.uniform(min_mult, max_mult))
                    new_price = max(1, new_price)  # Ensure at least 1 gil
                    prop['Value'] = new_price
                    sale_modified += 1
                    item_had_price = True
        
        if item_had_price:
            items_modified += 1
    
    log(f"✓ Modified {items_modified} items", "green")
    log(f"  - BuyValue changes: {buy_modified}", "green")
    log(f"  - SaleValue changes: {sale_modified}", "green")
    
    # Save randomized JSON
    randomized_path = os.path.join(output_dir, "temp", "Item_randomized.json")
    with open(randomized_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    log(f"✓ Randomized JSON saved", "green")
    return True

def import_from_json(output_dir):
    """Import JSON back to Item.uasset"""
    log("\n=== STEP 3: IMPORTING FROM JSON TO UASSET ===", "cyan")
    
    json_path = os.path.join(output_dir, "temp", "Item_randomized.json")
    uasset_output = os.path.join(output_dir, "temp", "Item.uasset")
    
    if not os.path.exists(json_path):
        log(f"✗ Randomized JSON not found: {json_path}", "red")
        return False
    
    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_output}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Importing JSON to Item.uasset"):
        log("✗ JSON import failed", "red")
        return False
    
    # Verify files were created
    uasset_file = os.path.join(output_dir, "temp", "Item.uasset")
    uexp_file = os.path.join(output_dir, "temp", "Item.uexp")
    
    if not os.path.exists(uasset_file):
        log("✗ Item.uasset was not created", "red")
        return False
    
    uasset_size = os.path.getsize(uasset_file)
    uexp_size = os.path.getsize(uexp_file) if os.path.exists(uexp_file) else 0
    
    log(f"✓ Assets imported successfully", "green")
    log(f"  - Item.uasset: {uasset_size:,} bytes", "green")
    if uexp_size > 0:
        log(f"  - Item.uexp: {uexp_size:,} bytes", "green")
    return True

def repack_with_retoc(output_dir, seed):
    """Convert back to Zen format and repack with retoc"""
    log("\n=== STEP 4: CONVERTING TO ZEN AND REPACKING ===", "cyan")
    
    # Copy modified files to UnpackFresh for repacking
    src_uasset = os.path.join(output_dir, "temp", "Item.uasset")
    src_uexp = os.path.join(output_dir, "temp", "Item.uexp")
    dest_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    
    shutil.copy2(src_uasset, os.path.join(dest_dir, "Item.uasset"))
    if os.path.exists(src_uexp):
        shutil.copy2(src_uexp, os.path.join(dest_dir, "Item.uexp"))
    
    log("Copied modified files to UnpackFresh directory", "yellow")
    
    # Convert from Legacy to Zen format
    input_dir = os.path.join(output_dir, UNPACK_FRESH_DIR)
    mod_base = ensure_p_suffix('RandomizedItemPrices')
    output_base = os.path.join(output_dir, mod_base)
    
    # Clean up old output files to prevent stale .utoc issues
    for ext in ['', '.utoc', '.pak', '.ucas']:
        old_file = output_base + ext
        if os.path.exists(old_file):
            os.remove(old_file)
    
    # retoc to-zen - no filter needed since UnpackFresh_Item only contains the one asset we want
    cmd = f'"{RETOC_EXE}" to-zen "{input_dir}" "{output_base}" --version UE4_26'
    
    if not run_command(cmd, "Converting to Zen format and repacking"):
        log("✗ Retoc repacking failed", "red")
        return False
    
    # retoc creates: <base> (utoc), <base>.pak, <base>.ucas
    # Rename <base> to <base>.utoc
    utoc_no_ext = output_base
    utoc_with_ext = output_base + ".utoc"
    
    if os.path.exists(utoc_no_ext):
        shutil.move(utoc_no_ext, utoc_with_ext)
        log(f"  Renamed {mod_base} -> {mod_base}.utoc", "yellow")
    
    # Verify output files exist
    expected_files = [f"{mod_base}.utoc", f"{mod_base}.pak", f"{mod_base}.ucas"]
    all_exist = True
    for fname in expected_files:
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            log(f"  ✓ {fname} ({size:,} bytes)", "green")
        else:
            log(f"  ✗ {fname} not found", "red")
            all_exist = False
    
    if not all_exist:
        log("✗ Retoc did not create all output files", "red")
        return False
    
    log(f"✓ Repacking complete", "green")
    return True

def deploy_mod(output_dir, seed):
    """Deploy the mod to the game"""
    log("\n=== STEP 5: DEPLOYING MOD ===", "cyan")
    
    mod_name = ensure_p_suffix("RandomizedItemPrices")
    mods_dir = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods"
    
    os.makedirs(mods_dir, exist_ok=True)
    
    # Copy pak, ucas, and utoc files
    files_to_copy = [
        (f"{mod_name}.pak", f"{mod_name}.pak"),
        (f"{mod_name}.ucas", f"{mod_name}.ucas"),
        (f"{mod_name}.utoc", f"{mod_name}.utoc"),
    ]
    
    for src_name, dst_name in files_to_copy:
        src = os.path.join(output_dir, src_name)
        if os.path.exists(src):
            dst = os.path.join(mods_dir, dst_name)
            shutil.copy2(src, dst)
            size = os.path.getsize(dst)
            log(f"  ✓ {dst_name} ({size:,} bytes)", "green")
        else:
            log(f"  ⚠ {src_name} not found (may be expected)", "yellow")
    
    log(f"✓ Deployed to: {mods_dir}", "green")

def main():
    parser = argparse.ArgumentParser(description="FF7R Item Price Randomizer")
    parser.add_argument("seed", type=int, help="Random seed for price randomization")
    parser.add_argument("--auto-deploy", action="store_true", help="Automatically deploy to game")
    parser.add_argument("--work-dir", default=".", help="Working directory for temp files")
    parser.add_argument("--min-mult", type=float, default=0.5, help="Minimum price multiplier (default: 0.5)")
    parser.add_argument("--max-mult", type=float, default=2.0, help="Maximum price multiplier (default: 2.0)")
    
    args = parser.parse_args()
    
    output_dir = args.work_dir
    seed = args.seed
    
    log("==============================================================", "cyan")
    log("   FF7 REBIRTH ITEM PRICE RANDOMIZER", "cyan")
    log("==============================================================", "cyan")
    log(f"Seed: {seed}")
    log(f"Work directory: {output_dir}")
    log(f"Price range: {args.min_mult}x - {args.max_mult}x")
    log("")
    
    # Run the pipeline
    steps = [
        ("Extract from game paks", lambda: extract_from_game_paks(output_dir)),
        ("Export to JSON", lambda: export_to_json(output_dir)),
        ("Randomize prices", lambda: randomize_prices(output_dir, seed, args.min_mult, args.max_mult)),
        ("Import from JSON", lambda: import_from_json(output_dir)),
        ("Repack with retoc", lambda: repack_with_retoc(output_dir, seed)),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            log(f"\n✗ Pipeline failed at: {step_name}", "red")
            return 1
    
    # Deploy if requested
    if args.auto_deploy:
        deploy_mod(output_dir, seed)
    
    log("==============================================================", "green")
    log("              RANDOMIZATION COMPLETE!", "green")
    log("==============================================================", "green")
    
    if args.auto_deploy:
        log(f"\n✓ Mod deployed as RandomizedItemPrices_P", "green")
        log("  Launch the game to test the randomized item prices!")
    else:
        log(f"\n✓ Randomized mod created (RandomizedItemPrices_P)", "green")
        log("  Use --auto-deploy to automatically deploy to game")
    
    return 0

if __name__ == "__main__":
    exit(main())
