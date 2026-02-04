#!/usr/bin/env python3
"""
Smart reward parser that examines binary structure more carefully.

Pattern observed:
- Rewards are separated by name references
- Between rewards: [00 00 00 00] [item_id] [quantity_or_flag] [name_index] ...
- Item IDs in range 100-50000
- Need to identify which int32 values are item IDs vs other data
"""

import json
import struct
import sys

def parse_rewards_smart(json_path, uasset_path):
    """Parse rewards with detailed binary analysis."""
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    name_refs = data['exports'][0]['extrasData']['nameReferences']
    
    # Load binary
    uexp_path = uasset_path.replace('.uasset', '.uexp')
    with open(uexp_path, 'rb') as f:
        binary_data = f.read()
    
    print(f"Binary size: {len(binary_data):,} bytes")
    print(f"Name refs: {len(name_refs)}\n")
    
    # Find all reward name references
    reward_refs = [ref for ref in name_refs if ref['name'].startswith(('rwr', 'rwd'))]
    print(f"Found {len(reward_refs)} reward entries\n")
    
    # Analyze first few rewards in detail
    for i in range(min(10, len(reward_refs))):
        reward_ref = reward_refs[i]
        reward_name = reward_ref['name']
        start = reward_ref['index']
        
        # Get end (next reward or EOF)
        if i + 1 < len(reward_refs):
            end = reward_refs[i + 1]['index']
        else:
            end = len(binary_data)
        
        size = end - start
        
        print(f"\n{i+1}. {reward_name}")
        print(f"   Offset: {start:6d}, Size: {size:4d} bytes")
        
        # Show hex dump
        hex_data = binary_data[start:start+min(80, size)]
        hex_str = ' '.join(f'{b:02X}' for b in hex_data[:80])
        print(f"   Hex: {hex_str}")
        
        # Try to parse int32 values
        print(f"   Int32 values:")
        for offset in range(0, min(80, size), 4):
            if start + offset + 4 <= len(binary_data):
                value = struct.unpack('<I', binary_data[start+offset:start+offset+4])[0]
                
                # Identify what this might be
                if value == 0:
                    desc = "(zero/padding)"
                elif value == 0xFFFFFFFF:
                    desc = "(separator -1)"
                elif 100 <= value < 1000:
                    desc = "(ITEM ID? - consumable range)"
                elif 2000 <= value < 3000:
                    desc = "(ITEM ID? - armor range)"
                elif 9000 <= value < 10000:
                    desc = "(ITEM ID? - accessory range)"
                elif 10000 <= value < 50000:
                    desc = "(ITEM ID? - materia range)"
                elif 1 <= value <= 99:
                    desc = "(quantity?)"
                elif value < 2000:
                    desc = "(name index or other)"
                else:
                    desc = ""
                
                if desc or (100 <= value < 50000):
                    print(f"      +{offset:3d}: {value:8d} {desc}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python reward_smart_parser.py <reward_json> <Reward.uasset>")
        sys.exit(1)
    
    parse_rewards_smart(sys.argv[1], sys.argv[2])
