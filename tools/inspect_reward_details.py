#!/usr/bin/env python3
"""
Detailed Reward Structure Inspector
====================================

Takes a closer look at specific reward entries to understand the exact structure.
"""

import struct
import json
from pathlib import Path


def inspect_reward_entry(data, entry_name, items):
    """Inspect a specific reward entry in detail"""
    print(f"\n{'='*70}")
    print(f"REWARD ENTRY: {entry_name}")
    print(f"{'='*70}")
    print(f"Number of items: {len(items)}")
    
    # Get offsets
    offsets = [item['byte_offset'] for item in items]
    item_names = [item['name'] for item in items]
    
    print(f"\nItem list:")
    for i, (offset, name) in enumerate(zip(offsets, item_names)):
        print(f"  {i+1}. {name:40} @ offset {offset}")
    
    # Look at the data around the first offset
    if offsets:
        first_offset = min(offsets)
        last_offset = max(offsets)
        
        print(f"\nData range: {first_offset} to {last_offset} ({last_offset - first_offset + 20} bytes)")
        
        # Show structure around first few items
        print(f"\nDetailed hex dump (offsets {first_offset}-{first_offset+100}):")
        start = first_offset
        for i in range(0, 100, 20):
            offset = start + i
            if offset + 20 > len(data):
                break
            chunk = data[offset:offset+20]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            
            # Try to interpret as integers
            ints = []
            for j in range(0, min(20, len(chunk)), 4):
                if j + 4 <= len(chunk):
                    val = struct.unpack('<I', chunk[j:j+4])[0]
                    ints.append(f"{val:8}")
            
            print(f"  {offset:6}: {hex_str:59} | {' '.join(ints)}")
        
        # Check pattern between items
        if len(offsets) >= 2:
            print(f"\nPattern between items:")
            for i in range(min(3, len(offsets) - 1)):
                off1 = offsets[i]
                off2 = offsets[i + 1]
                gap = off2 - off1
                
                print(f"\n  Item {i+1} → Item {i+2} (gap: {gap} bytes):")
                chunk = data[off1:off2+4]
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                print(f"    {hex_str}")
                
                # Try to parse as structured data
                if len(chunk) >= 20:
                    # Common pattern seems to be: [index?][0xFF 0xFF 0xFF 0xFF][value][padding][index+1][...]
                    idx = struct.unpack('<I', chunk[0:4])[0]
                    marker = struct.unpack('<I', chunk[4:8])[0]
                    value = struct.unpack('<I', chunk[8:12])[0]
                    pad1 = struct.unpack('<I', chunk[12:16])[0]
                    
                    print(f"    Parsed: idx={idx}, marker=0x{marker:08x}, value={value}, pad={pad1}")


def main():
    # Load binary
    uexp_path = Path(r"C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\Reward.uexp")
    with open(uexp_path, 'rb') as f:
        data = f.read()
    
    # Load parsed data
    json_path = Path(__file__).parent / "data" / "_reward_parsed.json"
    with open(json_path, 'r') as f:
        parsed = json.load(f)
    
    print("="*70)
    print("Detailed Reward Structure Inspector")
    print("="*70)
    
    # Inspect a few interesting entries
    entries_to_inspect = [
        "rwdCARD_Normal_005",  # Has 6 items
        "rwr2110_Yuffie_Join",  # Has 9 items
        "rwr1360_treasure005_00",  # Treasure chest with 4 items
    ]
    
    for entry_name in entries_to_inspect:
        if entry_name in parsed and 'items' in parsed[entry_name]:
            inspect_reward_entry(data, entry_name, parsed[entry_name]['items'])
    
    print("\n" + "="*70)
    print("KEY OBSERVATIONS")
    print("="*70)
    print("""
Look for patterns in the hex dumps:
1. Are there repeating markers (like 0xFFFFFFFF)?
2. What's the consistent structure between items?
3. Can we identify: [ItemID][ItemCount][ItemType]?
4. What are the gaps between items (12, 20, 8 bytes)?
""")


if __name__ == '__main__':
    main()
