#!/usr/bin/env python3
"""
FF7 Rebirth Reward Structure Analyzer
=====================================

Analyzes the binary structure of Reward.uexp to understand how chest and quest
reward item IDs are stored. This is the research phase for implementing reward
randomization.

Part of Issue #5: https://github.com/WhenRecess/FFVIIRebirthAP/issues/5

GOAL:
Understand the binary layout of reward entries so we can programmatically
modify item IDs (similar to how smart_price_randomizer.py modifies prices).

WHAT WE KNOW:
- Reward.uexp contains reward entries (chests, quests, etc.)
- Each entry has ItemID_Array, ItemCount_Array, ItemAddType_Array
- Items are likely stored as 4-byte integers
- From _reward_parsed.json: We have item names with byte offsets

WHAT WE NEED TO FIND:
1. How are ItemID arrays structured?
2. Where are the item ID values in the binary?
3. Are they sequential or scattered?
4. Can we identify patterns for automated detection?
5. What are the count/type arrays and how do they relate?

USAGE:
  python analyze_reward_structure.py <Reward.uexp>
  
EXAMPLE:
  python analyze_reward_structure.py "C:\\...\\Reward.uexp"
"""

import struct
import json
import sys
from pathlib import Path
from collections import defaultdict


def load_parsed_json():
    """Load the previously parsed reward data with item offsets"""
    json_path = Path(__file__).parent / "data" / "_reward_parsed.json"
    if not json_path.exists():
        print(f"Warning: {json_path} not found")
        return {}
    
    with open(json_path, 'r') as f:
        return json.load(f)


def analyze_offsets(parsed_data):
    """Analyze the byte offsets to find patterns"""
    print("=" * 70)
    print("OFFSET ANALYSIS")
    print("=" * 70)
    
    all_offsets = []
    offset_gaps = []
    
    for reward_name, reward_data in parsed_data.items():
        if 'items' not in reward_data:
            continue
            
        items = reward_data['items']
        offsets = [item['byte_offset'] for item in items]
        all_offsets.extend(offsets)
        
        # Calculate gaps between consecutive offsets in this reward
        sorted_offsets = sorted(offsets)
        for i in range(len(sorted_offsets) - 1):
            gap = sorted_offsets[i+1] - sorted_offsets[i]
            offset_gaps.append(gap)
    
    print(f"\nTotal item entries found: {len(all_offsets)}")
    print(f"Offset range: {min(all_offsets)} - {max(all_offsets)}")
    
    # Analyze gaps
    if offset_gaps:
        print(f"\nGap analysis (distance between consecutive item offsets):")
        print(f"  Min gap: {min(offset_gaps)}")
        print(f"  Max gap: {max(offset_gaps)}")
        print(f"  Average gap: {sum(offset_gaps) / len(offset_gaps):.2f}")
        
        # Common gaps
        gap_counts = defaultdict(int)
        for gap in offset_gaps:
            gap_counts[gap] += 1
        
        print(f"\nMost common gaps:")
        for gap, count in sorted(gap_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {gap} bytes: {count} occurrences")
    
    return all_offsets


def inspect_binary_at_offsets(data, offsets_sample, parsed_data):
    """Look at actual binary data at known item offset positions"""
    print("\n" + "=" * 70)
    print("BINARY DATA INSPECTION")
    print("=" * 70)
    
    # Take a sample of offsets to inspect
    sample_offsets = sorted(offsets_sample)[:20]
    
    print("\nInspecting first 20 item offsets:")
    print(f"{'Offset':>8} | {'Value (int32)':>12} | {'Value (hex)':>10} | Surrounding bytes")
    print("-" * 70)
    
    for offset in sample_offsets:
        if offset + 4 > len(data):
            continue
            
        # Read as 4-byte integer (little-endian)
        value_int = struct.unpack('<I', data[offset:offset+4])[0]
        value_hex = data[offset:offset+4].hex()
        
        # Get surrounding context (16 bytes before and after)
        start = max(0, offset - 16)
        end = min(len(data), offset + 20)
        context = data[start:end].hex(' ')
        
        print(f"{offset:8} | {value_int:12} | 0x{value_hex:>8} | {context}")
    
    # Try to find item IDs
    print("\n" + "=" * 70)
    print("SEARCHING FOR ITEM ID PATTERNS")
    print("=" * 70)
    
    # Load known item IDs
    item_ids_path = Path(__file__).parent / "data" / "_ce_all_real_ids.json"
    if item_ids_path.exists():
        with open(item_ids_path, 'r') as f:
            known_ids = json.load(f)
        
        print(f"\nLoaded {len(known_ids)} known item IDs")
        print(f"ID range: {min(known_ids.values())} - {max(known_ids.values())}")
        
        # Check if values at offsets match known item IDs
        matches = 0
        for offset in sample_offsets:
            if offset + 4 > len(data):
                continue
            value_int = struct.unpack('<I', data[offset:offset+4])[0]
            
            # Check if this matches any known item ID
            for item_name, item_id in known_ids.items():
                if value_int == item_id:
                    print(f"  Offset {offset}: {value_int} matches {item_name}")
                    matches += 1
                    break
        
        print(f"\nMatches found: {matches}/{len(sample_offsets)}")
    else:
        print("\n_ce_all_real_ids.json not found, skipping ID matching")


def find_array_structures(data):
    """Try to find array-like structures (count followed by values)"""
    print("\n" + "=" * 70)
    print("ARRAY STRUCTURE DETECTION")
    print("=" * 70)
    
    print("\nSearching for [count][values...] patterns...")
    print("(Similar to price array detection)")
    
    potential_arrays = []
    i = 0
    
    while i < len(data) - 8:
        # Read potential count (small number, 0-50)
        count = struct.unpack('<I', data[i:i+4])[0]
        
        if 1 <= count <= 50:
            # Check if next 'count' values look like item IDs
            values = []
            valid = True
            
            for j in range(count):
                offset = i + 4 + (j * 4)
                if offset + 4 > len(data):
                    valid = False
                    break
                    
                value = struct.unpack('<I', data[offset:offset+4])[0]
                # Item IDs are typically 0-10000
                if value > 100000:
                    valid = False
                    break
                values.append(value)
            
            if valid and len(values) > 0:
                potential_arrays.append({
                    'offset': i,
                    'count': count,
                    'values': values
                })
        
        i += 4
    
    print(f"\nFound {len(potential_arrays)} potential arrays")
    
    if potential_arrays:
        print("\nFirst 10 potential arrays:")
        for arr in potential_arrays[:10]:
            print(f"  Offset {arr['offset']:6}: count={arr['count']}, values={arr['values'][:5]}...")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Please provide path to Reward.uexp")
        sys.exit(1)
    
    uexp_path = Path(sys.argv[1])
    
    if not uexp_path.exists():
        print(f"Error: File not found: {uexp_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("FF7 Rebirth Reward Structure Analyzer")
    print("=" * 70)
    print(f"\nAnalyzing: {uexp_path}")
    print(f"File size: {uexp_path.stat().st_size:,} bytes")
    
    # Load binary data
    with open(uexp_path, 'rb') as f:
        data = f.read()
    
    # Load parsed JSON
    parsed_data = load_parsed_json()
    print(f"Loaded parsed data: {len(parsed_data)} reward entries")
    
    # Analyze offsets
    all_offsets = analyze_offsets(parsed_data)
    
    # Inspect binary at known offsets
    if all_offsets:
        inspect_binary_at_offsets(data, all_offsets, parsed_data)
    
    # Try to find array structures
    find_array_structures(data)
    
    print("\n" + "=" * 70)
    print("SUMMARY & NEXT STEPS")
    print("=" * 70)
    print("""
Based on this analysis, we should be able to determine:
1. Are item IDs stored sequentially or in arrays?
2. What's the relationship between offsets in _reward_parsed.json and actual IDs?
3. Can we detect ItemID_Array structures programmatically?
4. Are there count/type arrays that need to be preserved?

Next: Review the output above and document findings for reward_randomizer.py
""")


if __name__ == '__main__':
    main()
