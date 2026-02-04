#!/usr/bin/env python3
"""
FF7 Rebirth Reward Randomizer (Binary Mode)
============================================

Randomizes chest and quest rewards by finding and replacing item name indices
in the binary .uexp file.

APPROACH:
Similar to smart_price_randomizer.py, this scans the binary for ItemID_Array
structures using intelligent pattern detection:
  [4-byte count] [count × 4-byte index values]

The index values point to names in the .uasset name table. We randomize these
indices to swap which items appear in each reward.

USAGE:
  python reward_randomizer.py <input.uexp> <output.uexp> <seed>

EXAMPLE:
  python reward_randomizer.py Reward.uexp Reward_randomized.uexp 12345

DEPENDENCIES:
  Requires both Reward.uasset and Reward.uexp in same directory
"""

import struct
import random
import sys
import json
import os
import shutil
import subprocess
import configparser
from pathlib import Path
from typing import List, Tuple


def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    
    defaults = {
        'game_dir': r'G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH',
        'unpack_dir': r'C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End',
        'unpack_rewards_dir': r'C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\unpack\UnpackFresh_Rewards\End'
    }
    
    if config_path.exists():
        config.read(config_path)
        if 'Paths' in config:
            for key in defaults:
                if key in config['Paths']:
                    defaults[key] = config['Paths'][key]
    
    return defaults


def load_item_pool():
    """Load valid item names that appear in rewards"""
    data_dir = Path(__file__).parent / "data"
    reward_file = data_dir / "_reward_parsed.json"
    
    # Extract all unique item names from parsed reward data
    item_names = set()
    with open(reward_file, 'r') as f:
        rewards = json.load(f)
        for reward_entry in rewards.values():
            if 'items' in reward_entry:
                for item in reward_entry['items']:
                    if 'name' in item:
                        item_names.add(item['name'])
    
    item_names = sorted(list(item_names))
    print(f"Loaded {len(item_names)} valid reward item names")
    return item_names


def find_itemid_arrays(data, min_count=1, max_count=50):
    """
    Find ItemID_Array structures in binary data.
    
    Pattern: [4-byte count] [count × 4-byte index values]
    
    Similar to how smart_price_randomizer finds price arrays.
    Uses intelligent filtering: validates that at least 50% of indices are non-zero
    (similar to the 50% non-zero price validation)
    
    Returns list of (offset, count, indices) tuples
    """
    arrays = []
    i = 0
    
    while i < len(data) - 8:  # Need at least count + 1 index
        try:
            potential_count = struct.unpack('<I', data[i:i+4])[0]
            
            # Check if this could be an array count
            if min_count <= potential_count <= max_count:
                array_size = 4 + potential_count * 4
                
                # Check if we have enough data
                if i + array_size <= len(data):
                    indices = []
                    valid = True
                    
                    # Try to read all indices
                    for j in range(potential_count):
                        idx_offset = i + 4 + j * 4
                        idx = struct.unpack('<I', data[idx_offset:idx_offset+4])[0]
                        
                        # Index should be reasonable (< 100,000 for name table)
                        if idx < 100000:
                            indices.append(idx)
                        else:
                            valid = False
                            break
                    
                    # If valid array found, validate it has meaningful content
                    # (at least 50% non-zero, like smart_price_randomizer)
                    if valid and len(indices) == potential_count:
                        non_zero_indices = [idx for idx in indices if idx > 0]
                        if len(non_zero_indices) >= len(indices) * 0.5:  # At least 50% non-zero
                            arrays.append((i, potential_count, indices))
                            i += array_size
                            continue
        except:
            pass
        
        i += 1
    
    return arrays


def randomize_rewards_binary(input_path, output_path, seed):
    """Randomize reward item indices in binary .uexp file"""
    
    print(f"=== FF7 Rebirth Reward Randomizer (Binary) ===")
    print(f"Input: {Path(input_path).name}")
    print(f"Seed: {seed}\n")
    
    # Load item pool
    item_pool = load_item_pool()
    rng = random.Random(seed)
    
    # Load parsed reward data with known offsets
    data_dir = Path(__file__).parent / "data"
    reward_file = data_dir / "_reward_parsed.json"
    
    print(f"Loading parsed reward data...")
    with open(reward_file, 'r') as f:
        parsed_rewards = json.load(f)
    
    # Collect all item offsets
    target_offsets = []
    for reward_name, reward_data in parsed_rewards.items():
        if 'items' in reward_data:
            for item in reward_data['items']:
                if 'byte_offset' in item:
                    target_offsets.append(item['byte_offset'])
    
    print(f"Found {len(target_offsets)} item indices to randomize (from {len(parsed_rewards)} rewards)")
    
    # Load binary
    print(f"Loading binary data...")
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    print(f"File size: {len(data):,} bytes")
    
    # Randomize at known offsets only
    print(f"\nRandomizing items at known offsets...")
    total_modified = 0
    
    for offset in sorted(target_offsets)[:20]:  # Show first 20
        old_idx = struct.unpack('<I', data[offset:offset+4])[0]
        
        # Pick a random index from the found indices
        new_idx = rng.choice(target_offsets) if target_offsets else rng.randint(0, 1000)
        
        data[offset:offset+4] = struct.pack('<I', new_idx)
        total_modified += 1
        
        if total_modified <= 10:
            print(f"  0x{offset:08X}: {old_idx:5} → {new_idx:5}")
    
    # Randomize the rest
    for offset in sorted(target_offsets)[20:]:
        old_idx = struct.unpack('<I', data[offset:offset+4])[0]
        new_idx = rng.choice(target_offsets) if target_offsets else rng.randint(0, 1000)
        data[offset:offset+4] = struct.pack('<I', new_idx)
        total_modified += 1
    
    if len(target_offsets) > 10:
        print(f"  ... and {len(target_offsets) - 10} more")
    
    print(f"\nTotal indices modified: {total_modified}")
    
    # Save output
    print(f"Saving to {Path(output_path).name}...")
    with open(output_path, 'wb') as f:
        f.write(data)
    
    print(f"\n✓ Done!")
    return True


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return
    
    input_path = sys.argv[1]
    
    # Check for --auto-deploy flag
    auto_deploy = '--auto-deploy' in sys.argv
    
    if auto_deploy:
        # Auto mode: randomize in place and deploy
        output_path = input_path + ".tmp"
        argv_offset = sys.argv.index('--auto-deploy')
        seed = int(sys.argv[argv_offset + 1]) if len(sys.argv) > argv_offset + 1 else 12345
    else:
        # Manual mode: specify output path
        output_path = sys.argv[2] if len(sys.argv) > 2 else Path(input_path).stem + "_randomized.uexp"
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
    
    # Validate input
    if not Path(input_path).exists():
        print(f"ERROR: Input file not found: {input_path}")
        return
    
    # Run randomization
    success = randomize_rewards_binary(input_path, output_path, seed)
    
    if not success:
        return
    
    if auto_deploy:
        print("\n" + "="*70)
        print("AUTOMATED DEPLOYMENT STARTING")
        print("="*70)
        
        # Load configuration
        config = load_config()
        script_dir = Path(__file__).parent
        
        # Use separate unpack directory for rewards
        unpack_dir = config.get('unpack_rewards_dir', config['unpack_dir'])
        retoc_exe = script_dir / "bin" / "retoc.exe"
        game_mods_dir = Path(config['game_dir']) / "End" / "Content" / "Paks" / "~mods"
        
        # Verify retoc exists
        if not retoc_exe.exists():
            print(f"ERROR: retoc.exe not found at {retoc_exe}")
            print("Please ensure retoc.exe is in tools/bin/ directory")
            return
        
        # Step 1: Replace in UnpackFresh_Rewards
        dest_file = os.path.join(unpack_dir, "Content", "DataObject", "Resident", "Reward.uexp")
        print(f"\n[1/4] Replacing Reward.uexp in {Path(unpack_dir).parent.name}...")
        print(f"      Source: {output_path}")
        print(f"      Dest:   {dest_file}")
        
        # Backup original if it exists
        if os.path.exists(dest_file) and not os.path.exists(dest_file + ".bak"):
            shutil.copy2(dest_file, dest_file + ".bak")
            print(f"      ✓ Backed up original to .bak")
        
        shutil.copy2(output_path, dest_file)
        print(f"      ✓ Replaced")
        
        # Step 2: Repack with retoc
        pak_basename = f"RandomizedRewards_Seed{seed}"
        pak_output = os.path.join(os.path.dirname(output_path), pak_basename)
        
        print(f"\n[2/4] Repacking with retoc...")
        print(f"      Input:  {unpack_dir}")
        print(f"      Output: {pak_output}.utoc/.pak/.ucas")
        print(f"      Note: Using separate rewards-only directory to avoid conflicts")
        
        # Get parent directory (UnpackFresh_Rewards/End -> UnpackFresh_Rewards)
        repack_input = str(Path(unpack_dir).parent)
        
        retoc_cmd = [
            str(retoc_exe),
            "to-zen",
            "--version", "UE4_26",
            repack_input,
            pak_output
        ]
        
        result = subprocess.run(retoc_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"      ✗ ERROR: retoc failed")
            print(f"      {result.stderr}")
            return
        
        print(f"      ✓ Repacked successfully")
        
        # Step 3: Deploy to game mods folder
        print(f"\n[3/4] Deploying to game mods folder...")
        print(f"      Target: {game_mods_dir}")
        
        if not game_mods_dir.exists():
            game_mods_dir.mkdir(parents=True, exist_ok=True)
            print(f"      ✓ Created mods directory")
        
        # Copy all three files: .pak, .ucas, and .utoc
        files_to_copy = [
            (pak_output + '.pak', pak_basename + '.pak'),
            (pak_output + '.ucas', pak_basename + '.ucas'),
            (pak_output, pak_basename + '.utoc')
        ]
        
        for src, dst_name in files_to_copy:
            dst = game_mods_dir / dst_name
            
            if os.path.exists(src):
                shutil.copy2(src, dst)
                file_size = os.path.getsize(dst)
                print(f"      ✓ {dst_name} ({file_size:,} bytes)")
            else:
                print(f"      ✗ WARNING: {os.path.basename(src)} not found at {src}")
        
        # Step 4: Cleanup
        print(f"\n[4/4] Cleaning up temporary files...")
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"      ✓ Removed {output_path}")
        
        print("\n" + "="*70)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*70)
        print(f"\nMod deployed to: {game_mods_dir}")
        print(f"Seed: {seed}")
        print("\n🎮 Ready to test in-game!")
    else:
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print(f"Output file: {output_path}")
        print("\nTo deploy automatically with repacking:")
        print(f"  python reward_randomizer.py {Path(input_path).name} --auto-deploy {seed}")


if __name__ == '__main__':
    main()
