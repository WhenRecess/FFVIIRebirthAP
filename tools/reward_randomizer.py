#!/usr/bin/env python3
"""
FF7 Rebirth Reward Randomizer
Randomizes ItemID_Array values in Reward.uasset (chest/quest rewards)
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
UNPACK_FRESH_DIR = "UnpackFresh_Rewards"
REWARD_ASSET_PATH = "DataObject/Resident/Reward"
REWARD_POOL_JSON = r"tools\data\_reward_parsed.json"


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


def load_item_pool():
    """Load valid reward item names from parsed reward data"""
    pool_path = Path(__file__).parent / "data" / "_reward_parsed.json"
    if not pool_path.exists():
        log(f"✗ Reward pool not found: {pool_path}", "red")
        return [], {}

    with open(pool_path, 'r', encoding='utf-8') as f:
        parsed = json.load(f)

    item_names = set()
    for reward in parsed.values():
        for item in reward.get('items', []):
            name = item.get('name')
            if name:
                item_names.add(name)

    item_names = sorted(item_names)

    # Group by prefix for better category matching
    by_prefix = {}
    for name in item_names:
        prefix = name.split('_')[0] if '_' in name else 'OTHER'
        by_prefix.setdefault(prefix, []).append(name)

    log(f"✓ Loaded {len(item_names)} reward item names", "green")
    return item_names, by_prefix


def extract_from_game_paks(output_dir):
    """Extract fresh Reward.uasset from game paks using retoc to-legacy"""
    log("\n=== STEP 0: EXTRACTING FRESH FILES FROM GAME PAKS ===", "cyan")

    if not os.path.exists(GAME_PAKS_DIR):
        log(f"✗ Game paks directory not found: {GAME_PAKS_DIR}", "red")
        return False

    if not os.path.exists(RETOC_EXE):
        log(f"✗ retoc_filtered.exe not found: {RETOC_EXE}", "red")
        return False

    # Extract Reward from game paks (Zen to Legacy conversion)
    extract_dir = os.path.join(output_dir, "extracted_from_game_rewards")
    os.makedirs(extract_dir, exist_ok=True)

    cmd = f'"{RETOC_EXE}" to-legacy "{GAME_PAKS_DIR}" "{extract_dir}" --filter "Reward" --version UE4_26'

    if not run_command(cmd, "Extracting Reward from game paks (Zen to Legacy)"):
        log("✗ Failed to extract from game paks", "red")
        return False

    # Find the specific Reward.uasset we need
    expected = Path(extract_dir) / "End" / "Content" / "DataObject" / "Resident" / "Reward.uasset"
    if expected.exists():
        target_file = expected
    else:
        candidates = list(Path(extract_dir).rglob("Reward.uasset"))
        if not candidates:
            log("✗ Reward.uasset not found after extraction", "red")
            return False
        target_file = candidates[0]

    log(f"✓ Found Reward.uasset ({target_file.stat().st_size:,} bytes)", "green")

    # Copy to UnpackFresh directory
    reward_dir = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident")
    os.makedirs(reward_dir, exist_ok=True)

    for ext in ['.uasset', '.uexp']:
        src = target_file.with_suffix(ext)
        if src.exists():
            dest = os.path.join(reward_dir, f"Reward{ext}")
            shutil.copy2(src, dest)
            log(f"  ✓ Copied Reward{ext}", "green")

    return True


def export_to_json(output_dir):
    """Export Reward.uasset to JSON"""
    log("\n=== STEP 1: EXPORTING TO JSON ===", "cyan")

    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Reward.uasset")
    json_path = os.path.join(output_dir, "temp", "Reward.json")

    if not os.path.exists(uasset_path):
        log(f"✗ Reward.uasset not found at: {uasset_path}", "red")
        return False

    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    cmd = f'"{UASSETGUI_EXE}" tojson "{uasset_path}" "{json_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Exporting Reward to JSON"):
        log("✗ JSON export failed", "red")
        return False

    if not os.path.exists(json_path):
        log("✗ JSON file was not created", "red")
        return False

    size = os.path.getsize(json_path)
    log(f"✓ JSON exported successfully ({size:,} bytes)", "green")
    return True


def _randomize_itemid_array(value_list, item_pool, items_by_prefix, rng, stats, exclude_prefixes):
    """Randomize ItemID_Array list entries in-place"""
    for entry in value_list:
        if not isinstance(entry, dict):
            continue
        old_item = entry.get("Value")
        if not isinstance(old_item, str) or not old_item:
            continue

        prefix = old_item.split('_')[0] if '_' in old_item else 'OTHER'
        if prefix in exclude_prefixes:
            continue

        candidates = items_by_prefix.get(prefix, item_pool)
        if not candidates:
            continue

        new_item = rng.choice(candidates)
        entry["Value"] = new_item
        stats["modified"] += 1
        if len(stats["examples"]) < 10:
            stats["examples"].append(f"{old_item} → {new_item}")


def _walk_json(obj, item_pool, items_by_prefix, rng, stats, exclude_prefixes):
    if isinstance(obj, dict):
        # Look for ItemID_Array
        if obj.get("Name") == "ItemID_Array" and isinstance(obj.get("Value"), list):
            _randomize_itemid_array(obj["Value"], item_pool, items_by_prefix, rng, stats, exclude_prefixes)

        # Recurse into values
        for value in obj.values():
            _walk_json(value, item_pool, items_by_prefix, rng, stats, exclude_prefixes)

    elif isinstance(obj, list):
        for item in obj:
            _walk_json(item, item_pool, items_by_prefix, rng, stats, exclude_prefixes)


def randomize_rewards(output_dir, seed, exclude_prefixes=None):
    """Randomize ItemID_Array values in Reward.json"""
    log(f"\n=== STEP 2: RANDOMIZING REWARDS (seed: {seed}) ===", "cyan")

    json_path = os.path.join(output_dir, "temp", "Reward.json")

    if not os.path.exists(json_path):
        log(f"✗ JSON file not found: {json_path}", "red")
        return False

    item_pool, items_by_prefix = load_item_pool()
    if not item_pool:
        return False

    rng = random.Random(seed)
    exclude_prefixes = set(exclude_prefixes or [])

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = {"modified": 0, "examples": []}
    _walk_json(data, item_pool, items_by_prefix, rng, stats, exclude_prefixes)

    if stats["modified"] == 0:
        log("✗ No ItemID_Array entries were modified", "red")
        return False

    log(f"✓ Randomized {stats['modified']} reward item IDs", "green")
    if stats["examples"]:
        log("Examples:", "yellow")
        for example in stats["examples"]:
            print(f"  {example}")

    randomized_path = os.path.join(output_dir, "temp", "Reward_randomized.json")
    with open(randomized_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    log(f"✓ Randomized JSON saved to {randomized_path}", "green")
    return True


def import_from_json(output_dir):
    """Import randomized JSON back to Reward.uasset"""
    log("\n=== STEP 3: IMPORTING FROM JSON TO UASSET ===", "cyan")

    json_path = os.path.join(output_dir, "temp", "Reward_randomized.json")
    uasset_path = os.path.join(output_dir, UNPACK_FRESH_DIR, "End", "Content", "DataObject", "Resident", "Reward.uasset")

    if not os.path.exists(json_path):
        log(f"✗ Randomized JSON not found: {json_path}", "red")
        return False

    cmd = f'"{UASSETGUI_EXE}" fromjson "{json_path}" "{uasset_path}" 26 "4.26.1-0+++UE4+Release-4.26-End"'

    if not run_command(cmd, "Importing JSON to Reward.uasset"):
        log("✗ JSON import failed", "red")
        return False

    log("✓ Successfully imported JSON back to uasset", "green")
    return True


def repack_to_zen(output_dir, mod_name="RandomizedRewards"):
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


def deploy_mod(output_dir, mod_name="RandomizedRewards"):
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
    parser = argparse.ArgumentParser(description='Randomize FF7 Rebirth Rewards')
    parser.add_argument('seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--auto-deploy', action='store_true', help='Automatically deploy to game mods folder')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--exclude-prefix', action='append', default=[], help='Exclude item prefixes (repeatable)')

    args = parser.parse_args()

    log("=" * 60, "cyan")
    log("FF7 REBIRTH REWARD RANDOMIZER", "cyan")
    log("=" * 60, "cyan")

    if not extract_from_game_paks(args.output_dir):
        return 1

    if not export_to_json(args.output_dir):
        return 1

    if not randomize_rewards(args.output_dir, args.seed, args.exclude_prefix):
        return 1

    if not import_from_json(args.output_dir):
        return 1

    if not repack_to_zen(args.output_dir):
        return 1

    if args.auto_deploy:
        if not deploy_mod(args.output_dir):
            return 1

    log("\n" + "=" * 60, "green")
    log("REWARD RANDOMIZATION COMPLETE!", "green")
    log("=" * 60, "green")
    return 0


if __name__ == '__main__':
    exit(main())
