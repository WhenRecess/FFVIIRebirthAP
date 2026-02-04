#!/usr/bin/env python3
"""
Setup script for separate unpack directories.

This script copies the necessary files from your main UnpackFresh directory
into the separate shop and rewards unpack directories for no-conflict repacking.

USAGE:
  python setup_unpack_dirs.py

REQUIREMENTS:
  - Your main UnpackFresh directory is set up in config.ini
  - Files will be copied from UnpackFresh/End/Content/DataObject/Resident/
"""

import shutil
import sys
from pathlib import Path
import configparser


def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / "config.ini"
    
    if not config_path.exists():
        print(f"ERROR: config.ini not found at {config_path}")
        print("Please create config.ini with your UnpackFresh path")
        return None
    
    config.read(config_path)
    
    if 'Paths' not in config:
        print("ERROR: [Paths] section not found in config.ini")
        return None
    
    return config['Paths']


def main():
    print("="*70)
    print("Setting up separate unpack directories")
    print("="*70)
    
    # Load config
    config = load_config()
    if not config:
        sys.exit(1)
    
    unpack_base = config.get('unpack_dir', r'C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End')
    source_dir = Path(unpack_base) / "Content" / "DataObject" / "Resident"
    
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("Make sure UnpackFresh is set up correctly in config.ini")
        sys.exit(1)
    
    script_dir = Path(__file__).parent.parent
    
    # Setup directories
    setups = [
        {
            "name": "Shop",
            "target": script_dir / "unpack" / "UnpackFresh_Shop" / "End" / "Content" / "DataObject" / "Resident",
            "files": ["ShopItem.uasset", "ShopItem.uexp"]
        },
        {
            "name": "Rewards",
            "target": script_dir / "unpack" / "UnpackFresh_Rewards" / "End" / "Content" / "DataObject" / "Resident",
            "files": ["Reward.uasset", "Reward.uexp"]
        }
    ]
    
    for setup in setups:
        print(f"\n[{setup['name']}]")
        target_dir = setup['target']
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for filename in setup['files']:
            src = source_dir / filename
            dst = target_dir / filename
            
            if not src.exists():
                print(f"  ⚠ WARNING: {filename} not found in source")
                continue
            
            print(f"  Copying {filename}...")
            shutil.copy2(src, dst)
            file_size = dst.stat().st_size
            print(f"    ✓ {filename} ({file_size:,} bytes)")
    
    print("\n" + "="*70)
    print("✅ Setup complete!")
    print("="*70)
    print("\nYou can now use:")
    print("  python smart_price_randomizer.py ShopItem.uexp --auto-deploy 12345")
    print("  python reward_randomizer.py Reward.uexp --auto-deploy 12345")
    print("\nBoth randomizers will create separate pak files with no conflicts!")


if __name__ == '__main__':
    main()
