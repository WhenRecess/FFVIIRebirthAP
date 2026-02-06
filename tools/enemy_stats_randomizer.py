#!/usr/bin/env python3
"""
FF7 Rebirth Enemy Stats Randomizer
Randomizes HP, ATK, DEF, MAG, MDEF, and Shield for all enemies and bosses
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
UNPACK_FRESH_DIR = "UnpackFresh_BattleCharaSpec"
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

def extract_from_game_paks(output_dir):
    """Extract fresh BattleCharaSpec.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")
    
    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False
    
    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False
    
    # Extract BattleCharaSpec from game paks (Zen to Legacy conversion)
    extract_dir = os.path.join(output_dir, "extracted_from_game")
    os.makedirs(extract_dir, exist_ok=True)
    
    # Use filter "BattleCharaSpec" to get DataObject/Resident/BattleCharaSpec.uasset
    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "BattleCharaSpec" --version UE4_26'
    
    if not run_command(cmd, "Extracting BattleCharaSpec from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False
    
    # Find the specific BattleCharaSpec.uasset we need
    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "BattleCharaSpec.uasset"
    if not target_file.exists():
        log(f"✗ BattleCharaSpec.uasset not found at expected path: {target_file}", "red")
        return False
    
    log(f"✓ Found BattleCharaSpec.uasset ({target_file.stat().st_size:,} bytes)", "green")
    
    # Copy to UnpackFresh directory
    chara_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(chara_dir, exist_ok=True)
    
    # Copy .uasset and .uexp
    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(chara_dir, f"BattleCharaSpec{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied BattleCharaSpec{ext}", "green")
    
    return True

def export_to_json(output_dir):
    """Export BattleCharaSpec.uasset to JSON using UAssetGUI"""
    log("\n=== STEP 1: EXPORTING BATTLECHARASPEC TO JSON ===", "cyan")
    
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "BattleCharaSpec.uasset")
    if not os.path.exists(uasset_path):
        log(f"✗ BattleCharaSpec.uasset not found at: {uasset_path}", "red")
        return False
    
    json_path = os.path.join(output_dir, "temp", "BattleCharaSpec.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Exporting BattleCharaSpec.uasset to JSON"):
        log("✗ Failed to export JSON", "red")
        return False
    
    if not os.path.exists(json_path):
        log("✗ JSON export failed", "red")
        return False
    
    size = os.path.getsize(json_path)
    log(f"✓ Exported to {json_path} ({size:,} bytes)", "green")
    return True

def load_and_randomize(output_dir, seed=None, randomize_bosses=True, stat_variance=0.25, test_mode=False):
    """Load BattleCharaSpec JSON, randomize enemy stats, save modified JSON"""
    log("\n=== STEP 2: RANDOMIZING ENEMY STATS ===", "cyan")
    
    if test_mode:
        log("⚠️ TEST MODE: Setting all stats to 1 (one-hit everything)", "yellow")
    elif seed is not None:
        random.seed(seed)
        log(f"Using seed: {seed}", "yellow")
    
    json_path = os.path.join(output_dir, "temp", "BattleCharaSpec.json")
    
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
    
    # Stats to randomize for each enemy
    STAT_FIELDS = ['HP', 'PhysicsAttack', 'PhysicsDefense', 'MagicAttack', 'MagicDefense', 'Shield']
    
    # Filter enemies and bosses
    enemy_rows = []
    boss_rows = []
    
    for i, row in enumerate(export['Data']):
        if 'Value' not in row:
            continue
        
        # Find the CharaSpecID property to identify enemy type
        chara_spec_id = None
        for prop in row.get('Value', []):
            if prop.get('Name') == 'CharaSpecID':
                chara_spec_id = prop.get('Value')
                break
        
        if chara_spec_id is None:
            continue
        
        # Categorize by prefix (EN=enemy, EB/SU/FA=boss)
        if isinstance(chara_spec_id, str):
            if chara_spec_id.startswith('EB') or ('_Boss' in chara_spec_id) or chara_spec_id.startswith('FA'):
                boss_rows.append(i)
            elif chara_spec_id.startswith('EN'):
                enemy_rows.append(i)
    
    log(f"Found {len(enemy_rows)} regular enemies, {len(boss_rows)} bosses", "yellow")
    
    randomized_count = 0
    
    if test_mode:
        # Test mode: set all stats to 1
        for row_idx in enemy_rows + boss_rows:
            row = export['Data'][row_idx]
            randomized_count += set_stats_to_one(row, STAT_FIELDS)
    else:
        # Randomize regular enemies
        for row_idx in enemy_rows:
            row = export['Data'][row_idx]
            randomized_count += randomize_enemy_row(row, STAT_FIELDS, stat_variance)
        
        # Randomize bosses if requested (with tighter bounds)
        if randomize_bosses:
            boss_variance = stat_variance * 0.7  # 70% of normal variance for bosses
            for row_idx in boss_rows:
                row = export['Data'][row_idx]
                randomized_count += randomize_enemy_row(row, STAT_FIELDS, boss_variance)
    
    log(f"✓ Randomized {randomized_count} stat entries", "green")
    
    # Save modified JSON
    try:
        with open(json_path, 'w') as f:
            json.dump(data, f)
        log(f"✓ Saved randomized data to {json_path}", "green")
        return True
    except Exception as e:
        log(f"✗ Failed to save JSON: {e}", "red")
        return False

def randomize_enemy_row(row, stat_fields, variance):
    """Randomize stat values in a single enemy row"""
    randomized = 0
    
    if 'Value' not in row:
        return randomized
    
    for prop in row['Value']:
        if 'Name' not in prop:
            continue
        
        field_name = prop['Name']
        if field_name not in stat_fields:
            continue
        
        if 'Value' not in prop:
            continue
        
        try:
            old_value = int(prop['Value'])
            if old_value <= 0:
                continue
            
            # Apply random variance (±variance%)
            variance_amount = old_value * variance
            min_value = max(1, int(old_value * (1 - variance)))
            max_value = int(old_value * (1 + variance))
            
            new_value = random.randint(min_value, max_value)
            prop['Value'] = new_value
            randomized += 1
        except (ValueError, TypeError):
            continue
    
    return randomized

def set_stats_to_one(row, stat_fields):
    """Set all stat values to 1 for testing"""
    modified = 0
    
    if 'Value' not in row:
        return modified
    
    for prop in row['Value']:
        if 'Name' not in prop:
            continue
        
        field_name = prop['Name']
        if field_name not in stat_fields:
            continue
        
        if 'Value' not in prop:
            continue
        
        try:
            old_value = int(prop['Value'])
            if old_value > 0:
                prop['Value'] = 1
                modified += 1
        except (ValueError, TypeError):
            continue
    
    return modified

def import_from_json(output_dir):
    """Import modified JSON back to BattleCharaSpec.uasset using UAssetGUI"""
    log("\n=== STEP 3: IMPORTING JSON BACK TO BATTLECHARASPEC ===", "cyan")
    
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "BattleCharaSpec.uasset")
    json_path = os.path.join(output_dir, "temp", "BattleCharaSpec.json")
    
    if not os.path.exists(uasset_path):
        log(f"✗ BattleCharaSpec.uasset not found at: {uasset_path}", "red")
        return False
    
    if not os.path.exists(json_path):
        log(f"✗ Modified JSON not found at: {json_path}", "red")
        return False
    
    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'
    
    if not run_command(cmd, "Importing JSON to BattleCharaSpec.uasset"):
        log("✗ Failed to import JSON", "red")
        return False
    
    log(f"✓ Successfully imported randomized stats", "green")
    return True

def repack_to_mod(output_dir):
    """Repack BattleCharaSpec into Zen format .pak file using retoc"""
    log("\n=== STEP 4: REPACKING TO MOD FILE ===", "cyan")
    
    unpack_dir = os.path.join(output_dir, UNPACK_FRESH_DIR)
    
    if not os.path.exists(unpack_dir):
        log(f"✗ Unpack directory not found: {unpack_dir}", "red")
        return False
    
    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False
    
    # Convert from Legacy to Zen format
    mod_base = ensure_p_suffix('RandomizedEnemyStats')
    output_base = os.path.join(output_dir, mod_base)
    
    # retoc to-zen - no filter needed since UnpackFresh_BattleCharaSpec only contains the one asset
    cmd = f'"{RETOC_EXE}" to-zen "{unpack_dir}" "{output_base}" --version UE4_26'
    
    if not run_command(cmd, "Converting to Zen format and repacking"):
        log("✗ Retoc repacking failed", "red")
        return False
    
    # retoc creates: <base> (utoc), <base>.pak, <base>.ucas
    # Rename <base> to <base>.utoc
    utoc_no_ext = output_base
    utoc_with_ext = output_base + ".utoc"
    
    if os.path.exists(utoc_no_ext) and not os.path.exists(utoc_with_ext):
        shutil.move(utoc_no_ext, utoc_with_ext)
        log(f"  Renamed {mod_base} -> {mod_base}.utoc", "yellow")
    
    # Verify output files exist
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
        log(f"✗ Mod deployment directory not found: {MOD_DEPLOY_DIR}", "red")
        return False
    
    # Find all mod files in output_dir (mod files are placed here after retoc repacking)
    mod_files = list(Path(output_dir).glob("RandomizedEnemyStats_P.*"))
    
    if not mod_files:
        log("✗ No mod files found to deploy", "red")
        return False
    
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
    parser = argparse.ArgumentParser(description="FF7 Rebirth Enemy Stats Randomizer")
    parser.add_argument('--seed', type=int, help='Random seed for reproducible randomization')
    parser.add_argument('--no-bosses', action='store_true', help='Do not randomize boss stats')
    parser.add_argument('--variance', type=float, default=0.25, help='Stat variance (default: 0.25 = ±25%%)')
    parser.add_argument('--test-mode', action='store_true', help='Set all stats to 1 (one-hit everything)')
    parser.add_argument('--extract', action='store_true', help='Extract fresh assets from game paks')
    parser.add_argument('--export', action='store_true', help='Export to JSON')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import from JSON')
    parser.add_argument('--repack', action='store_true', help='Repack to mod file')
    parser.add_argument('--deploy', action='store_true', help='Deploy mod to game')
    parser.add_argument('--auto-deploy', action='store_true', help='Run full pipeline: extract → export → randomize → import → repack → deploy')
    
    args = parser.parse_args()
    
    output_dir = "."
    
    # Run full pipeline if --auto-deploy specified
    if args.auto_deploy:
        args.extract = True
        args.export = True
        args.do_import = True
        args.repack = True
        args.deploy = True
    
    # If no actions specified, show help
    if not (args.extract or args.export or args.do_import or args.repack or args.deploy):
        parser.print_help()
        return
    
    # Execute pipeline steps
    if args.extract:
        if not extract_from_game_paks(output_dir):
            return
    
    if args.export:
        if not export_to_json(output_dir):
            return
    
    if args.export:  # Randomize happens after export
        randomize_bosses = not args.no_bosses
        if not load_and_randomize(output_dir, args.seed, randomize_bosses, args.variance, args.test_mode):
            return
    
    if args.do_import:
        if not import_from_json(output_dir):
            return
    
    if args.repack:
        if not repack_to_mod(output_dir):
            return
    
    if args.deploy:
        if not deploy_mod(output_dir):
            return
    
    log("\n" + "="*60, "green")
    log("✓ RANDOMIZATION COMPLETE", "green")
    log("="*60, "green")

if __name__ == "__main__":
    main()
