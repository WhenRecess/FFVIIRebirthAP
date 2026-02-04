#!/usr/bin/env python3
"""
ShopItem Price Randomizer using UAssetGUI JSON export/import
Properly handles FF7R property structures via JSON
"""

import json
import subprocess
import random
import sys
import os
import shutil
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent


def run_command(cmd, description=""):
    """Run a command and return success status"""
    print(f"[*] {description}")
    print(f"    Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"    ✗ FAILED (exit code {result.returncode})")
        if result.stderr:
            print(f"    stderr: {result.stderr}")
        return False
    else:
        print(f"    ✓ Success")
        return True


def export_uasset_to_json(uasset_path, json_path, engine_version="VER_UE4_26", mappings_name="4.26.1-0+++UE4+Release-4.26-End", uassetgui_path=None):
    """Export uasset to JSON using UAssetGUI"""
    if uassetgui_path is None:
        uassetgui_path = str(script_dir / "bin" / "UAssetGUI.exe")
    
    if not os.path.exists(uassetgui_path):
        print(f"ERROR: UAssetGUI not found at {uassetgui_path}")
        return False
    
    cmd = [uassetgui_path, "tojson", uasset_path, json_path, engine_version, mappings_name]
    return run_command(cmd, f"Exporting {Path(uasset_path).name} to JSON (with FF7R mappings)")


def import_json_to_uasset(json_path, uasset_path, mappings_name="4.26.1-0+++UE4+Release-4.26-End", uassetgui_path=None):
    """Import JSON back to uasset using UAssetGUI"""
    if uassetgui_path is None:
        uassetgui_path = str(script_dir / "bin" / "UAssetGUI.exe")
    
    if not os.path.exists(uassetgui_path):
        print(f"ERROR: UAssetGUI not found at {uassetgui_path}")
        return False
    
    cmd = [uassetgui_path, "fromjson", json_path, uasset_path, mappings_name]
    return run_command(cmd, f"Importing JSON back to {Path(uasset_path).name} (with FF7R mappings)")


def randomize_prices_in_json(json_path, seed, min_price=1, max_price=9999):
    """Randomize all OverridePrice_Array values in the JSON"""
    print(f"[*] Loading JSON: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    random.seed(seed)
    modification_count = 0
    
    # Navigate to exports
    if 'exports' not in data:
        print("  ERROR: No 'exports' key in JSON")
        return 0
    
    exports = data['exports']
    print(f"  Found {len(exports)} exports")
    
    # Iterate through each export
    for export_idx, export in enumerate(exports):
        if not isinstance(export, dict) or 'Value' not in export:
            continue
        
        value_data = export['Value']
        if not isinstance(value_data, list):
            continue
        
        # Look for OverridePrice_Array in this export's properties
        for prop_idx, prop in enumerate(value_data):
            if not isinstance(prop, dict):
                continue
            
            if prop.get('Name') == 'OverridePrice_Array':
                # This is an FF7ArrayProperty with FF7IntProperty items
                if 'Value' in prop and isinstance(prop['Value'], list):
                    original_count = len(prop['Value'])
                    
                    # Randomize each price in the array
                    for i, price_entry in enumerate(prop['Value']):
                        if isinstance(price_entry, dict) and 'Value' in price_entry:
                            old_price = price_entry.get('Value', 0)
                            new_price = random.randint(min_price, max_price)
                            price_entry['Value'] = new_price
                            modification_count += 1
                    
                    if original_count > 0:
                        print(f"  Export {export_idx}: Randomized {original_count} prices in OverridePrice_Array")
    
    print(f"\n[*] Saving modified JSON: {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"  ✓ Modified {modification_count} total price values")
    return modification_count


def main():
    if len(sys.argv) < 2:
        print("Usage: uassetgui_price_randomizer.py <uasset_path> [seed] [min_price] [max_price]")
        print("Example: uassetgui_price_randomizer.py ShopItem.uasset 54321 100 5000")
        sys.exit(1)
    
    uasset_path = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
    min_price = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_price = int(sys.argv[4]) if len(sys.argv) > 4 else 9999
    
    # UAssetGUI path - uses repository-local version, can be overridden with environment variable
    default_path = str(script_dir / "bin" / "UAssetGUI.exe")
    uassetgui_path = os.environ.get('UASSETGUI_PATH', default_path)
    
    if not os.path.exists(uasset_path):
        print(f"ERROR: {uasset_path} not found")
        sys.exit(1)
    
    # Create temporary JSON file
    json_temp = Path(uasset_path).stem + "_temp.json"
    
    try:
        print(f"=== ShopItem Price Randomizer (UAssetGUI Edition) ===")
        print(f"Input: {uasset_path}")
        print(f"Seed: {seed}")
        print(f"Price range: {min_price}-{max_price}\n")
        
        # Step 1: Export to JSON
        if not export_uasset_to_json(uasset_path, json_temp, uassetgui_path=uassetgui_path):
            sys.exit(1)
        
        # Step 2: Randomize prices in JSON
        mod_count = randomize_prices_in_json(json_temp, seed, min_price, max_price)
        print(f"\n[*] Total modifications: {mod_count} prices")
        
        if mod_count == 0:
            print("WARNING: No prices were modified. Check the JSON structure.")
        
        # Step 3: Import back to uasset
        if not import_json_to_uasset(json_temp, uasset_path, uassetgui_path=uassetgui_path):
            print(f"WARNING: Import may have failed, but {json_temp} contains the modifications")
            sys.exit(1)
        
        print(f"\n✓ SUCCESS! Randomized {mod_count} prices in {uasset_path}")
        
    finally:
        # Clean up temp JSON
        if os.path.exists(json_temp):
            print(f"\n[*] Cleaning up temporary file: {json_temp}")
            os.remove(json_temp)


if __name__ == '__main__':
    main()
