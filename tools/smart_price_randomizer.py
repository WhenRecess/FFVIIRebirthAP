#!/usr/bin/env python3
"""
FF7 Rebirth Shop Price Randomizer
==================================

Intelligent binary randomizer that detects and modifies shop prices in ShopItem.uexp.

Part of the FF7 Rebirth Archipelago pre-randomization system. This tool modifies
game files BEFORE launch, generating deterministic results based on a seed value.
For runtime functionality (item gives, location checks), see the ue4ss_mod.

WHAT IT DOES:
- Scans ShopItem.uexp for price array structures
- Uses intelligent pattern detection (not naive byte matching)
- Randomizes prices within a specified range using a seed
- Can automatically repack and deploy to game

HOW IT WORKS:
The tool detects OverridePrice_Array structures by looking for:
  [4-byte count (0-100)] [count x 4-byte prices in valid range]
This intelligent approach finds 250-450 real price arrays vs 6000+ false positives
from naive byte matching.

USAGE:
  Manual mode (just randomize a file):
    python smart_price_randomizer.py <input.uexp> <output.uexp> <seed> <min> <max>
    
  Auto-deploy mode (randomize, repack, and install):
    python smart_price_randomizer.py <input.uexp> --auto-deploy <seed> <min> <max>

EXAMPLES:
  # Manual: Create a randomized copy
  python smart_price_randomizer.py ShopItem.uexp ShopItem_mod.uexp 12345 100 5000
  
  # Auto: Full pipeline - randomize, repack with retoc, deploy to game
  python smart_price_randomizer.py "C:\\...\\ShopItem.uexp" --auto-deploy 54321 100 9000

CONFIGURATION:
  Edit config.ini to set:
  - game_dir: Your FF7 Rebirth installation path
  - unpack_dir: Where your unpacked game files are (for repacking)

DEPENDENCIES:
  - Python 3.10+ (standard library only)
  - bin/retoc.exe (for --auto-deploy, included in repository)
  - config.ini (for --auto-deploy paths)

SEE ALSO:
  - AP_DEVELOPMENT_GUIDE.md: Full development documentation
  - BINARY_STRUCTURE_BREAKTHROUGH.md: Technical details on detection algorithm
  - EQUIPMENT_RANDOMIZATION_PLAN.md: Similar approach for equipment stats
"""

import struct
import random
import sys
import os
import shutil
import subprocess
import configparser
import argparse
from pathlib import Path


def load_config():
    """Load configuration from config.ini or use defaults"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    
    # Defaults
    defaults = {
        'game_dir': r'G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH',
        'unpack_dir': r'C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End',
        'unpack_shop_dir': r'C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\unpack\UnpackFresh_Shop\End'
    }
    
    if config_path.exists():
        config.read(config_path)
        if 'Paths' in config:
            for key in defaults:
                if key in config['Paths']:
                    defaults[key] = config['Paths'][key]
    
    return defaults


def find_price_arrays(data, min_price=1, max_price=9999):
    """
    Find OverridePrice_Array structures in the binary data
    Returns list of (offset, count, prices) tuples
    """
    arrays = []
    i = 0
    
    # Look for FF7ArrayProperty markers followed by price data
    # Pattern: Look for sequences of 4-byte integers in price range
    while i < len(data) - 4:
        # Try to read as little-endian 4-byte integer
        value = struct.unpack('<I', data[i:i+4])[0]
        
        # Check if this could be an array count (small positive number)
        if 0 < value < 100 and i + value * 4 < len(data):
            # This might be an array count! Check if following values are prices
            potential_count = value
            prices = []
            valid = True
            
            for j in range(potential_count):
                price_offset = i + 4 + j * 4
                if price_offset + 4 <= len(data):
                    price = struct.unpack('<I', data[price_offset:price_offset+4])[0]
                    
                    # Check if it's in price range
                    if min_price <= price <= max_price:
                        prices.append(price)
                    elif price == 0:
                        # Zero prices are OK (not yet priced)
                        prices.append(price)
                    else:
                        valid = False
                        break
                else:
                    valid = False
                    break
            
            # If we found a valid array
            if valid and len(prices) >= 1 and len(prices) <= 100:
                # Check if this looks like a real price array
                # (at least some prices should be non-zero)
                non_zero_prices = [p for p in prices if p > 0]
                if len(non_zero_prices) >= len(prices) * 0.5:  # At least 50% non-zero
                    arrays.append((i, potential_count, prices))
                    i += 4 + potential_count * 4  # Skip past this array
                    continue
        
        i += 1
    
    return arrays


def randomize_prices_binary(input_path, output_path, seed, min_price=1, max_price=9999):
    """Randomize prices in ShopItem.uexp using intelligent binary scanning"""
    
    print(f"=== ShopItem Binary Price Randomizer (Intelligent) ===")
    print(f"Input: {Path(input_path).name}")
    print(f"Seed: {seed}")
    print(f"Price range: {min_price}-{max_price}\n")
    
    # Read the file
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())
    
    print(f"File size: {len(data)} bytes")
    
    # Find price arrays
    arrays = find_price_arrays(data, min_price, max_price)
    print(f"Found {len(arrays)} potential price arrays\n")
    
    if len(arrays) == 0:
        print("ERROR: No price arrays found")
        return False
    
    # Show first few arrays
    print("First 5 arrays found:")
    for idx, (offset, count, prices) in enumerate(arrays[:5]):
        non_zero = len([p for p in prices if p > 0])
        print(f"  {idx+1}. Offset 0x{offset:08X}: {count} items ({non_zero} prices)")
    
    if len(arrays) > 5:
        print(f"  ... and {len(arrays) - 5} more")
    
    # Randomize
    print(f"\nRandomizing prices...")
    rng = random.Random(seed)
    total_modified = 0
    
    for offset, count, prices in arrays:
        for j in range(count):
            price_offset = offset + 4 + j * 4
            old_price = struct.unpack('<I', data[price_offset:price_offset+4])[0]
            
            # Only randomize non-zero prices (zero means not yet available)
            if old_price > 0:
                new_price = rng.randint(min_price, max_price)
                data[price_offset:price_offset+4] = struct.pack('<I', new_price)
                total_modified += 1
    
    print(f"Modified {total_modified} price values")
    
    # Write output
    with open(output_path, 'wb') as f:
        f.write(data)
    
    print(f"\n✓ Saved to: {Path(output_path).name}")
    return True


def print_help():
    """Print detailed help information"""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    FF7 REBIRTH SHOP PRICE RANDOMIZER                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
  Intelligently detects and randomizes shop prices in ShopItem.uexp.
  Part of the FF7 Rebirth Archipelago pre-randomization system.

USAGE:
  python smart_price_randomizer.py <input_file> [options]

MODES:
  Manual Mode (default):
    python smart_price_randomizer.py <input.uexp> [output.uexp] [seed] [min] [max]
    
    Creates a randomized copy of the input file without deploying.
    
  Auto-Deploy Mode:
    python smart_price_randomizer.py <input.uexp> --auto-deploy <seed> <min> <max>
    
    Full pipeline: randomize → repack with retoc → deploy to game mods folder.
    Requires config.ini to be set up with your paths.

ARGUMENTS:
  input_file     Path to ShopItem.uexp (required)
  output_file    Output path (manual mode, default: <name>_randomized.uexp)
  seed           Random seed for reproducible results (default: 12345)
  min_price      Minimum price in gil (default: 1)
  max_price      Maximum price in gil (default: 9999)

FLAGS:
  --auto-deploy  Enable automatic repacking and deployment
  --help, -h     Show this help message

EXAMPLES:
  # Just randomize a file (no deployment)
  python smart_price_randomizer.py ShopItem.uexp

  # Randomize with specific seed and price range
  python smart_price_randomizer.py ShopItem.uexp output.uexp 42 500 3000

  # Full auto-deploy pipeline
  python smart_price_randomizer.py "C:\\Path\\To\\ShopItem.uexp" --auto-deploy 12345 100 5000

CONFIGURATION (config.ini):
  [Paths]
  game_dir = G:\\SteamLibrary\\steamapps\\common\\FINAL FANTASY VII REBIRTH
  unpack_dir = C:\\Users\\YourName\\Documents\\UnpackFresh\\End

WHAT AUTO-DEPLOY DOES:
  1. Randomizes prices in a temporary copy
  2. Replaces original in unpack_dir
  3. Runs retoc to repack to Zen format (.pak/.ucas/.utoc)
  4. Copies result to {game_dir}\\End\\Content\\Paks\\~mods\\
  5. Cleans up temporary files

OUTPUT:
  The randomizer reports:
  - Number of price arrays detected
  - Number of prices modified
  - Deployment status (if --auto-deploy)
  
TECHNICAL NOTES:
  - Detection algorithm: [4-byte count][count × 4-byte prices]
  - Validates: count 0-100, prices in range, >50% non-zero
  - Typical result: 250-450 arrays, 280-540 prices
  - Zero prices (locked items) are not modified

FILES:
  - bin/retoc.exe: Pak repacker (required for --auto-deploy)
  - config.ini: User path configuration

SEE ALSO:
  - AP_DEVELOPMENT_GUIDE.md: Complete development guide
  - BINARY_STRUCTURE_BREAKTHROUGH.md: Algorithm details
"""
    print(help_text)


def main():
    # Handle help flags first
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help', '/?']:
        print_help()
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    # Check for --auto-deploy flag
    auto_deploy = '--auto-deploy' in sys.argv
    
    if auto_deploy:
        # Auto mode: randomize in place and deploy
        output_path = input_path + ".tmp"
        argv_offset = sys.argv.index('--auto-deploy')
        seed = int(sys.argv[argv_offset + 1]) if len(sys.argv) > argv_offset + 1 else 12345
        min_price = int(sys.argv[argv_offset + 2]) if len(sys.argv) > argv_offset + 2 else 1
        max_price = int(sys.argv[argv_offset + 3]) if len(sys.argv) > argv_offset + 3 else 9999
    else:
        # Manual mode: specify output path
        output_path = sys.argv[2] if len(sys.argv) > 2 else Path(input_path).stem + "_randomized.uexp"
        seed = int(sys.argv[3]) if len(sys.argv) > 3 else 12345
        min_price = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        max_price = int(sys.argv[5]) if len(sys.argv) > 5 else 9999
    
    if not Path(input_path).exists():
        print(f"ERROR: {input_path} not found")
        sys.exit(1)
    
    success = randomize_prices_binary(input_path, output_path, seed, min_price, max_price)
    
    if not success:
        sys.exit(1)
    
    if auto_deploy:
        print("\n" + "="*60)
        print("AUTOMATED DEPLOYMENT STARTING")
        print("="*60)
        
        # Load configuration
        config = load_config()
        script_dir = Path(__file__).parent
        
        # Use separate unpack directory for shop
        unpack_dir = config.get('unpack_shop_dir', config['unpack_dir'])
        retoc_exe = script_dir / "bin" / "retoc.exe"
        game_mods_dir = Path(config['game_dir']) / "End" / "Content" / "Paks" / "~mods"
        
        # Verify retoc exists
        if not retoc_exe.exists():
            print(f"ERROR: retoc.exe not found at {retoc_exe}")
            print("Please ensure retoc.exe is in tools/bin/ directory")
            sys.exit(1)
        
        # Step 1: Replace in UnpackFresh_Shop
        dest_file = os.path.join(unpack_dir, "Content", "DataObject", "Resident", "ShopItem.uexp")
        print(f"\n[1/4] Replacing ShopItem.uexp in {Path(unpack_dir).parent.name}...")
        print(f"      Source: {output_path}")
        print(f"      Dest:   {dest_file}")
        
        # Backup original if it exists
        if os.path.exists(dest_file) and not os.path.exists(dest_file + ".bak"):
            shutil.copy2(dest_file, dest_file + ".bak")
            print(f"      ✓ Backed up original to .bak")
        
        shutil.copy2(output_path, dest_file)
        print(f"      ✓ Replaced")
        
        # Step 2: Repack with retoc
        pak_basename = f"RandomizedShop_Seed{seed}"
        pak_output = os.path.join(os.path.dirname(output_path), pak_basename)
        
        print(f"\n[2/4] Repacking with retoc...")
        print(f"      Input:  {unpack_dir}")
        print(f"      Output: {pak_output}.utoc/.pak/.ucas")
        print(f"      Note: Using separate shop-only directory to avoid conflicts")
        
        # Get parent directory (UnpackFresh_Shop/End -> UnpackFresh_Shop)
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
            sys.exit(1)
        
        print(f"      ✓ Repacked successfully")
        
        # Step 3: Deploy to game mods folder
        print(f"\n[3/4] Deploying to game mods folder...")
        print(f"      Target: {game_mods_dir}")
        
        if not game_mods_dir.exists():
            game_mods_dir.mkdir(parents=True, exist_ok=True)
            print(f"      ✓ Created mods directory")
        
        # Copy all three files: .pak, .ucas, and the no-extension .utoc file
        files_to_copy = [
            (pak_output + '.pak', pak_basename + '.pak'),
            (pak_output + '.ucas', pak_basename + '.ucas'),
            (pak_output, pak_basename + '.utoc')  # No extension = .utoc data
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
        
        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        print(f"\nMod deployed to: {game_mods_dir}")
        print(f"Seed: {seed}")
        print(f"Price range: {min_price}-{max_price} gil")
        print("\n🎮 Ready to test in-game!")
    
    sys.exit(0)


if __name__ == '__main__':
    main()
