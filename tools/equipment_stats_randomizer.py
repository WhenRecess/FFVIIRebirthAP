#!/usr/bin/env python3
"""
FF7 Rebirth Equipment Stats Randomizer
Randomizes ATK, MATK, DEF, MDEF, HP, MP, materia slots, skill core slots, and bonus stats for all equipment
Also handles array-based weapon properties (SkillCoreSlotMax progression, MateriaSlotModify layout)
Uses filtered retoc extraction from game paks to ensure fresh assets
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
UNPACK_FRESH_DIR = "UnpackFresh_Equipment"
MOD_DEPLOY_DIR = r"G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods"

# Equipment type prefixes
WEAPON_PREFIXES = ['W_TSW', 'W_GUN', 'W_GLV', 'W_ROD', 'W_SHR', 'W_CLR', 'W_MGP', 'W_FLG', 'W_SWD']
ARMOR_PREFIX = 'E_ARM'
ACCESSORY_PREFIX = 'E_ACC'

# Stats to randomize - grouped by category
# Core combat stats (always present, high impact)
CORE_STATS = ['AttackAdd', 'MagicAttackAdd', 'DefenseAdd', 'MagicDefenseAdd']

# Resource stats
RESOURCE_STATS = ['HPMaxAdd', 'MPMaxAdd']

# Scale stats (percentage-based bonuses)
SCALE_STATS = ['HPMaxScale', 'MPMaxScale', 'MagicScale', 'StrengthScale', 'VitalityScale', 'SpiritScale', 'DexterityScale', 'LuckScale']

# Flat bonus stats
BONUS_STATS = ['VitalityAdd', 'SpiritAdd', 'DexterityAdd', 'LuckAdd', 'StrengthAdd', 'SpiritAdd']

# Materia slots (scalar totals)
MATERIA_STATS = ['MateriaSlotSingle', 'MateriaSlotDouble']

# Float stats
FLOAT_STATS = ['MateriaGrowScale']

# Scalar weapon stats (not in the original list)
WEAPON_SCALAR_STATS = ['SkillCoreSlotNum']

# Array-based weapon fields (need special handling)
# SkillCoreSlotMax_Array: [1,1,1,2,2,3,3,4,4] = skill slots at each weapon level (must stay non-decreasing)
# MateriaSlotModify_Array: [1,1,2,1,1,2] = materia slot layout (1=single, 2=linked pair)
WEAPON_ARRAY_FIELDS = ['SkillCoreSlotMax_Array', 'MateriaSlotModify_Array']

# All randomizable scalar stats combined
ALL_STAT_FIELDS = CORE_STATS + RESOURCE_STATS + SCALE_STATS + BONUS_STATS + MATERIA_STATS + FLOAT_STATS + WEAPON_SCALAR_STATS


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
    """
    Extract the base name for FName entries, matching UAssetAPI's FName parsing.
    Names ending with _NNN (where first digit isn't 0) are split into base + number.
    e.g. 'E_ACC_0101' -> 'E_ACC' (base), because '0101' starts with '0' -> kept as-is
    Actually '0101' starts with '0' so it's kept. But 'E_ACC_101' -> 'E_ACC' base.
    """
    match = re.match(r'^(.+)_([0-9]+)$', name)
    if match:
        base = match.group(1)
        num_str = match.group(2)
        if len(num_str) > 0 and num_str[0] != '0':
            return base
    return None


def extract_from_game_paks(output_dir):
    """Extract fresh Equipment.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")

    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    extract_dir = os.path.join(output_dir, "extracted_from_game")
    os.makedirs(extract_dir, exist_ok=True)

    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "Equipment" --version UE4_26'

    if not run_command(cmd, "Extracting Equipment from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False

    target_file = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "Equipment.uasset"
    if not target_file.exists():
        log(f"✗ Equipment.uasset not found at expected path: {target_file}", "red")
        return False

    log(f"✓ Found Equipment.uasset ({target_file.stat().st_size:,} bytes)", "green")

    equip_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(equip_dir, exist_ok=True)

    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(equip_dir, f"Equipment{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied Equipment{ext}", "green")

    return True


def export_to_json(output_dir):
    """Export Equipment.uasset to JSON using UAssetGUI"""
    log("\n=== STEP 1: EXPORTING EQUIPMENT TO JSON ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Equipment.uasset")
    if not os.path.exists(uasset_path):
        log(f"✗ Equipment.uasset not found at: {uasset_path}", "red")
        return False

    json_path = os.path.join(output_dir, "temp", "Equipment.json")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Exporting Equipment.uasset to JSON"):
        log("✗ Failed to export JSON", "red")
        return False

    if not os.path.exists(json_path):
        log("✗ JSON export failed", "red")
        return False

    size = os.path.getsize(json_path)
    log(f"✓ Exported to {json_path} ({size:,} bytes)", "green")
    return True


def get_equipment_type(name):
    """Determine equipment type from its ID prefix"""
    if not name:
        return "unknown"
    for prefix in WEAPON_PREFIXES:
        if name.startswith(prefix):
            return "weapon"
    if name.startswith(ARMOR_PREFIX):
        return "armor"
    if name.startswith(ACCESSORY_PREFIX):
        return "accessory"
    return "unknown"


def collect_stat_ranges(data_rows):
    """Collect value ranges for each stat across all equipment, grouped by type"""
    from collections import defaultdict
    ranges = defaultdict(lambda: defaultdict(list))

    for row in data_rows:
        if 'Value' not in row:
            continue
        equip_name = row.get('Name', '')
        equip_type = get_equipment_type(equip_name)

        for prop in row['Value']:
            name = prop.get('Name', '')
            if name not in ALL_STAT_FIELDS:
                continue
            value = prop.get('Value')
            if value is not None and (isinstance(value, (int, float))):
                ranges[equip_type][name].append(value)

    return ranges


def randomize_equipment(output_dir, seed=None, stat_variance=0.5, test_mode=False, randomize_materia_slots=True):
    """Load Equipment JSON, randomize stats, save modified JSON"""
    log("\n=== STEP 2: RANDOMIZING EQUIPMENT STATS ===", "cyan")

    if test_mode:
        log("⚠️ TEST MODE: Setting all stats to extreme values for testing", "yellow")
    elif seed is not None:
        random.seed(seed)
        log(f"Using seed: {seed}", "yellow")

    json_path = os.path.join(output_dir, "temp", "Equipment.json")

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

    # Collect stat ranges per equipment type for smart randomization
    stat_ranges = collect_stat_ranges(export['Data'])

    # Count equipment by type
    weapons = []
    armor = []
    accessories = []
    for i, row in enumerate(export['Data']):
        name = row.get('Name', '')
        etype = get_equipment_type(name)
        if etype == "weapon":
            weapons.append(i)
        elif etype == "armor":
            armor.append(i)
        elif etype == "accessory":
            accessories.append(i)

    log(f"Found {len(weapons)} weapons, {len(armor)} armor, {len(accessories)} accessories", "yellow")

    randomized_count = 0
    all_indices = weapons + armor + accessories

    for row_idx in all_indices:
        row = export['Data'][row_idx]
        equip_name = row.get('Name', '')
        equip_type = get_equipment_type(equip_name)

        if 'Value' not in row:
            continue

        for prop in row['Value']:
            field_name = prop.get('Name', '')
            if field_name not in ALL_STAT_FIELDS:
                continue

            value = prop.get('Value')
            if value is None:
                continue

            if test_mode:
                # Test mode: set combat stats high, materia slots to max
                if field_name in CORE_STATS:
                    prop['Value'] = 999
                    randomized_count += 1
                elif field_name in RESOURCE_STATS:
                    if field_name == 'HPMaxAdd':
                        prop['Value'] = 9999
                    elif field_name == 'MPMaxAdd':
                        prop['Value'] = 99
                    randomized_count += 1
                elif field_name == 'MateriaSlotDouble':
                    prop['Value'] = 4
                    randomized_count += 1
                elif field_name == 'MateriaSlotSingle':
                    prop['Value'] = 0
                    randomized_count += 1
                elif field_name == 'MateriaGrowScale':
                    prop['Value'] = 3.0
                    randomized_count += 1
                elif field_name == 'SkillCoreSlotNum':
                    prop['Value'] = 6
                    randomized_count += 1
                continue

            # Normal randomization
            try:
                old_value = value
                if isinstance(old_value, float):
                    # Float stats (MateriaGrowScale)
                    if old_value > 0:
                        min_val = max(0.5, old_value * (1 - stat_variance))
                        max_val = old_value * (1 + stat_variance)
                        new_value = round(random.uniform(min_val, max_val), 1)
                        # Clamp MateriaGrowScale to reasonable range
                        if field_name == 'MateriaGrowScale':
                            new_value = max(0.5, min(3.0, new_value))
                        prop['Value'] = new_value
                        randomized_count += 1

                elif isinstance(old_value, int):
                    if field_name in MATERIA_STATS and randomize_materia_slots:
                        # Materia slots: randomize within type-appropriate ranges
                        type_values = stat_ranges.get(equip_type, {}).get(field_name, [])
                        non_zero = [v for v in type_values if v > 0]
                        if non_zero:
                            new_value = random.choice(non_zero)
                        elif old_value > 0:
                            new_value = random.randint(0, max(old_value, 2))
                        else:
                            new_value = old_value
                        prop['Value'] = new_value
                        randomized_count += 1
                    elif old_value > 0:
                        # Standard int stats with variance
                        min_val = max(0, int(old_value * (1 - stat_variance)))
                        max_val = int(old_value * (1 + stat_variance))
                        new_value = random.randint(min_val, max_val)
                        prop['Value'] = new_value
                        randomized_count += 1
                    elif old_value == 0 and field_name in BONUS_STATS + SCALE_STATS:
                        # Small chance to add a bonus where there was none
                        if random.random() < 0.15:  # 15% chance
                            type_values = stat_ranges.get(equip_type, {}).get(field_name, [])
                            non_zero = [v for v in type_values if v > 0]
                            if non_zero:
                                prop['Value'] = random.choice(non_zero)
                                randomized_count += 1

            except (ValueError, TypeError):
                continue

        # Handle array-based weapon properties
        if equip_type == 'weapon':
            for prop in row['Value']:
                field_name = prop.get('Name', '')
                if field_name not in WEAPON_ARRAY_FIELDS:
                    continue
                arr = prop.get('Value', [])
                if not arr or not isinstance(arr, list):
                    continue

                if field_name == 'SkillCoreSlotMax_Array':
                    # Skill core slot progression per weapon level (e.g. [1,1,1,2,2,3,3,4,4])
                    # Must maintain non-decreasing order
                    int_vals = [elem.get('Value', 1) for elem in arr if isinstance(elem, dict)]
                    if not int_vals:
                        continue

                    if test_mode:
                        # Test mode: max slots at every level
                        for elem in arr:
                            if isinstance(elem, dict):
                                elem['Value'] = 6
                                randomized_count += 1
                    else:
                        # Randomize: pick a random max (2-6), generate non-decreasing progression
                        n = len(int_vals)
                        orig_max = max(int_vals)
                        new_max = random.randint(
                            max(1, int(orig_max * (1 - stat_variance))),
                            min(6, int(orig_max * (1 + stat_variance)))
                        )
                        new_max = max(1, new_max)
                        # Generate sorted random values that ramp up to new_max
                        new_vals = sorted(random.randint(1, new_max) for _ in range(n))
                        # Ensure last value hits the max
                        new_vals[-1] = new_max
                        for i_elem, elem in enumerate(arr):
                            if isinstance(elem, dict) and i_elem < len(new_vals):
                                elem['Value'] = new_vals[i_elem]
                                randomized_count += 1

                elif field_name == 'MateriaSlotModify_Array' and randomize_materia_slots:
                    # Materia slot layout (1=single, 2=linked pair start)
                    int_vals = [elem.get('Value', 1) for elem in arr if isinstance(elem, dict)]
                    if not int_vals:
                        continue

                    if test_mode:
                        # Test mode: make all slots linked pairs (2,2,2...)
                        for elem in arr:
                            if isinstance(elem, dict):
                                elem['Value'] = 2
                                randomized_count += 1
                    else:
                        # Shuffle the existing 1s and 2s randomly
                        # This preserves the total slot count but changes which are linked
                        random.shuffle(int_vals)
                        for i_elem, elem in enumerate(arr):
                            if isinstance(elem, dict) and i_elem < len(int_vals):
                                elem['Value'] = int_vals[i_elem]
                                randomized_count += 1

    log(f"✓ Randomized {randomized_count} stat entries across {len(all_indices)} equipment pieces", "green")

    # Add any new names to NameMap for FName safety
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
    """Ensure all equipment names and their FName bases are in the NameMap"""
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

        # Also add FName base names
        base = get_fname_base(name)
        if base and base not in existing:
            data['NameMap'].append(base)
            existing.add(base)
            added.add(base)

    if added:
        log(f"  Added {len(added)} names to NameMap", "yellow")


def import_from_json(output_dir):
    """Import modified JSON back to Equipment.uasset using UAssetGUI"""
    log("\n=== STEP 3: IMPORTING JSON BACK TO EQUIPMENT ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Equipment.uasset")
    json_path = os.path.join(output_dir, "temp", "Equipment.json")

    if not os.path.exists(uasset_path):
        log(f"✗ Equipment.uasset not found at: {uasset_path}", "red")
        return False

    if not os.path.exists(json_path):
        log(f"✗ Modified JSON not found at: {json_path}", "red")
        return False

    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Importing JSON to Equipment.uasset"):
        log("✗ Failed to import JSON", "red")
        return False

    log(f"✓ Successfully imported randomized equipment stats", "green")
    return True


def repack_to_mod(output_dir):
    """Repack Equipment into Zen format .pak file using retoc"""
    log("\n=== STEP 4: REPACKING TO MOD FILE ===", "cyan")

    unpack_dir = os.path.join(output_dir, UNPACK_FRESH_DIR)

    if not os.path.exists(unpack_dir):
        log(f"✗ Unpack directory not found: {unpack_dir}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    mod_base = ensure_p_suffix('RandomizedEquipmentStats')
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
        log(f"✗ Mod deployment directory not found: {MOD_DEPLOY_DIR}", "red")
        return False

    mod_files = list(Path(output_dir).glob("RandomizedEquipmentStats_P.*"))

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
    parser = argparse.ArgumentParser(description="FF7 Rebirth Equipment Stats Randomizer")
    parser.add_argument('--seed', type=int, help='Random seed for reproducible randomization')
    parser.add_argument('--variance', type=float, default=0.5, help='Stat variance (default: 0.5 = ±50%%)')
    parser.add_argument('--no-materia-slots', action='store_true', help='Do not randomize materia slot counts')
    parser.add_argument('--test-mode', action='store_true', help='Set all stats to extreme values for testing')
    parser.add_argument('--extract', action='store_true', help='Extract fresh assets from game paks')
    parser.add_argument('--export', action='store_true', help='Export to JSON')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import from JSON')
    parser.add_argument('--repack', action='store_true', help='Repack to mod file')
    parser.add_argument('--deploy', action='store_true', help='Deploy mod to game')
    parser.add_argument('--auto-deploy', action='store_true', help='Run full pipeline: extract → export → randomize → import → repack → deploy')

    args = parser.parse_args()
    output_dir = "."

    if args.auto_deploy:
        args.extract = True
        args.export = True
        args.do_import = True
        args.repack = True
        args.deploy = True

    if not (args.extract or args.export or args.do_import or args.repack or args.deploy):
        parser.print_help()
        return

    if args.extract:
        if not extract_from_game_paks(output_dir):
            return

    if args.export:
        if not export_to_json(output_dir):
            return

    if args.export:
        randomize_slots = not args.no_materia_slots
        if not randomize_equipment(output_dir, args.seed, args.variance, args.test_mode, randomize_slots):
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

    log("\n" + "=" * 60, "green")
    log("✓ EQUIPMENT RANDOMIZATION COMPLETE", "green")
    log("=" * 60, "green")


if __name__ == "__main__":
    main()
