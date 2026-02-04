#!/usr/bin/env python3
"""
Generate comprehensive E_ACC, E_ARM, E_WEP, E_MAT enum → ID mappings.

For now, use sequential mapping as a foundation:
- E_ACC_000X → 9000 + X (accessories)
- E_ARM_000XX → 2000 + XX (armor)
- E_WEP_000XX → 7000 + XX (weapons)
- E_MAT_000X → 10000 + X (materia)

This will be refined once we can verify the actual mappings through CE or in-game testing.
"""

import json
import re

def build_enum_mappings():
    """Build enum → ID mappings from equipment names."""
    
    # All E_ACC enums found in Equipment.uasset
    e_acc_enums = [
        'E_ACC_0001', 'E_ACC_0002', 'E_ACC_0003', 'E_ACC_0004', 'E_ACC_0005',
        'E_ACC_0006', 'E_ACC_0007', 'E_ACC_0008', 'E_ACC_0009', 'E_ACC_0010',
        'E_ACC_0011', 'E_ACC_0013', 'E_ACC_0014', 'E_ACC_0015', 'E_ACC_0016',
        'E_ACC_0017', 'E_ACC_0018', 'E_ACC_0019', 'E_ACC_0020', 'E_ACC_0021',
        'E_ACC_0022', 'E_ACC_0023', 'E_ACC_0024', 'E_ACC_0025', 'E_ACC_0026',
        'E_ACC_0027', 'E_ACC_0028', 'E_ACC_0029', 'E_ACC_0201', 'E_ACC_0202',
        'E_ACC_0203', 'E_ACC_0204', 'E_ACC_0205', 'E_ACC_0206', 'E_ACC_0207',
        'E_ACC_0208', 'E_ACC_0209', 'E_ACC_0210', 'E_ACC_0211', 'E_ACC_0212',
        'E_ACC_0213', 'E_ACC_0214', 'E_ACC_0215', 'E_ACC_0216', 'E_ACC_0217',
        'E_ACC_0218', 'E_ACC_0219', 'E_ACC_0220', 'E_ACC_0221', 'E_ACC_0222',
        'E_ACC_0223', 'E_ACC_0224', 'E_ACC_0225', 'E_ACC_0226', 'E_ACC_0227',
        'E_ACC_0228', 'E_ACC_0229', 'E_ACC_0230', 'E_ACC_0231', 'E_ACC_0232',
        'E_ACC_0233', 'E_ACC_0234', 'E_ACC_0235', 'E_ACC_0236', 'E_ACC_0237',
        'E_ACC_0238', 'E_ACC_0245', 'E_ACC_0246', 'E_ACC_0247', 'E_ACC_0248',
        'E_ACC_0249', 'E_ACC_0250', 'E_ACC_0251', 'E_ACC_0252', 'E_ACC_0253',
        'E_ACC_0254', 'E_ACC_0255', 'E_ACC_0256', 'E_ACC_0257', 'E_ACC_0258',
        'E_ACC_0259', 'E_ACC_0260', 'E_ACC_0261', 'E_ACC_0262', 'E_ACC_0263',
        'E_ACC_0264', 'E_ACC_0265', 'E_ACC_0266', 'E_ACC_0267', 'E_ACC_0268',
        'E_ACC_0269', 'E_ACC_0270', 'E_ACC_0271', 'E_ACC_0272', 'E_ACC_0273',
        'E_ACC_0274',
    ]
    
    # All E_ARM enums found in Equipment.uasset
    e_arm_enums = [
        'E_ARM', 'E_ARM_00000', 'E_ARM_00010', 'E_ARM_00011', 'E_ARM_00030',
        'E_ARM_00031', 'E_ARM_00050', 'E_ARM_00051', 'E_ARM_00070', 'E_ARM_00071',
        'E_ARM_00080', 'E_ARM_00090', 'E_ARM_00091', 'E_ARM_00110', 'E_ARM_00111',
        'E_ARM_00130', 'E_ARM_00131', 'E_ARM_DEMO_0000',
    ]
    
    mappings = {}
    
    # E_ACC mappings (9000+)
    for i, enum in enumerate(e_acc_enums, start=1):
        # Extract numeric suffix
        match = re.search(r'E_ACC_(\d+)', enum)
        if match:
            num = int(match.group(1))
            # Map based on the actual number, not sequential index
            ce_id = 9000 + num if num < 100 else 9100 + (num - 200)
            mappings[enum] = ce_id
    
    # E_ARM mappings (2000+)
    armor_base_ids = [2001, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013,
                      2014, 2020, 2021]  # First few from item_mappings.py
    
    for enum in e_arm_enums:
        if enum == 'E_ARM':
            continue  # Skip base
        match = re.search(r'E_ARM_(\d+)', enum)
        if match:
            num = int(match.group(1))
            # Need better mapping here - for now use sequential
            ce_id = 2000 + num
            mappings[enum] = ce_id
    
    return mappings

def main():
    mappings = build_enum_mappings()
    
    print(f"Generated {len(mappings)} equipment enum → CE ID mappings\n")
    
    # Group by type
    acc_mappings = {k: v for k, v in mappings.items() if k.startswith('E_ACC')}
    arm_mappings = {k: v for k, v in mappings.items() if k.startswith('E_ARM')}
    
    print(f"Accessories (E_ACC): {len(acc_mappings)}")
    print(f"Armor (E_ARM): {len(arm_mappings)}\n")
    
    print("Sample E_ACC mappings:")
    for enum in sorted(acc_mappings.keys())[:15]:
        print(f"  {enum:20s} → {acc_mappings[enum]:5d}")
    
    print("\nSample E_ARM mappings:")
    for enum in sorted(arm_mappings.keys())[:10]:
        print(f"  {enum:20s} → {arm_mappings[enum]:5d}")
    
    # Save all mappings
    with open('tools/_equipment_enum_mappings.json', 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2, sort_keys=True)
    
    print(f"\n\nSaved all mappings to tools/_equipment_enum_mappings.json")
    
    # Also save just E_ACC for quick access
    with open('tools/_e_acc_mappings.json', 'w', encoding='utf-8') as f:
        json.dump(acc_mappings, f, indent=2, sort_keys=True)
    
    print(f"Saved {len(acc_mappings)} E_ACC mappings to tools/_e_acc_mappings.json")
    
    return mappings

if __name__ == '__main__':
    mappings = main()
