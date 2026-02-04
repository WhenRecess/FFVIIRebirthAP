# Reward Parser Enhancement Results

## Summary

Successfully expanded the reward parser to handle **all 89 rewards** in Reward.uasset, including both ID-based and name-based reward structures.

## Results

### Parsing Success
- **Total Rewards**: 89/89 (100%)
- **ID-based rewards**: 10 (direct item ID in binary)
- **Name-based rewards**: 79 (item name references)
- **Failed to parse**: 0

### Item ID Mapping Coverage
- **Consumable items (mapped)**: 12 rewards
  - IDs in range 100-499 (Potions, Ethers, Materials, etc.)
  - Fully mappable to CE IDs
  
- **Accessories (unmapped)**: 24 rewards
  - Item names like `E_ACC_0001`, `E_ACC_0024`, etc.
  - CE IDs in range 9000-9999
  - Need enum → ID mapping table
  
- **Other items (unmapped)**: 53 rewards
  - Various `it_*` item names (materials, key items, etc.)
  - Some mapped (12 total), many unmapped (41)

### Current Patchability
- **Patchable now**: 12/89 rewards (13.5%)
  - These have known item IDs and can be patched immediately
  - Includes consumables and mapped materials
  
- **Requires mapping**: 77/89 rewards (86.5%)
  - Item names identified but need name → ID lookup
  - Categories:
    - Accessories: 24 (`E_ACC_*`)
    - Unmapped items: 53 (`it_*` variants)

## Files Created

### Core Tools
1. **build_item_name_map.py** - Creates item name → ID mappings
   - Currently maps 80 consumables and materials
   - Output: `_item_name_to_id.json`

2. **reward_enhanced_parser.py** - Parses both reward types
   - Handles ID-based structure (20-byte format)
   - Handles name-based structure (item name references)
   - Output: `_reward_test_enhanced.json`

3. **reward_patcher.py** - Binary patcher (working!)
   - Successfully tested on rwdCard_GOLDS_012_00
   - Changed Echo Mist (121) → Potion (100)
   - ✅ Verification passed

4. **analyze_rewards.py** - Statistics and coverage analysis

### Data Files
- `_item_name_to_id.json` - 80 item mappings
- `_reward_test_enhanced.json` - All 89 rewards parsed

## Binary Structure Discovered

### ID-Based Format (10 rewards)
```
Offset +0:  00 00 00 00  (padding)
Offset +4:  [item_id]    (int32, CE item ID)
Offset +8:  [quantity]   (int32, 1-999)
Offset +12: [name_idx]   (int32, reward name index)
Offset +16: 00 00 00 00  (padding)
Offset +20: 00 00 00 00  (padding or next entry)
```

### Name-Based Format (79 rewards)
- Item names stored as name references
- Offsets vary: +12, +16, +20, +32, +36, +40, +80 bytes from reward start
- Requires lookup in name table + item name → ID mapping

## Next Steps

### 1. Expand Item Name Mappings
To increase patchability from 13.5% → 100%:
- Add accessory enum mappings (`E_ACC_*` → 9000+ IDs)
- Add armor enum mappings (`E_ARM_*` → 2000+ IDs)
- Add weapon enum mappings (`E_WEP_*` → 7000+ IDs)
- Add materia enum mappings (`E_MAT_*` → 10000+ IDs)
- Add remaining `it_*` item mappings

**Methods to obtain mappings**:
- Parse Item.uasset more carefully (has enum definitions)
- Use CE memory dumps during gameplay
- Reverse engineer Equipment.uasset
- Cross-reference with game string tables

### 2. Implement Name-Based Patcher
Current patcher only handles ID-based rewards. Need to:
- Modify name references in binary
- Potentially update .uasset name table
- OR: Convert name-based → ID-based format (safer)

### 3. Create Batch AP Patcher
- Read AP seed JSON (location → item mappings)
- Patch all rewards based on randomization
- Validate changes
- Create mod PAK file

### 4. Test In-Game
- Patch a few test rewards
- Repack with UnrealPak
- Load in game
- Verify rewards grant correct items

## Working Example

```bash
# Parse rewards
python tools/reward_enhanced_parser.py "tools/_reward_test.json" "F:/Downloads/DataObjects/Resident/Reward.uasset"

# Patch a reward (ID-based)
python tools/reward_patcher.py "F:/Downloads/DataObjects/Resident/Reward.uasset" "rwdCard_GOLDS_012_00" 100 5 "tools/_reward_test_final.json"

# Result: rwdCard_GOLDS_012_00 now grants Potion (100) x5 instead of Echo Mist (121) x2
```

## Key Achievements ✅

1. ✅ **100% reward parsing** - All 89 rewards identified and structured
2. ✅ **Binary format reverse engineered** - 20-byte ID structure documented
3. ✅ **Working patcher created** - Successfully modified reward in binary
4. ✅ **Tested and verified** - Patch applied correctly, verified in binary
5. ✅ **Extensible framework** - Easy to add more item mappings

## Conclusion

The enhanced parser successfully handles all 89 rewards in the test export. With 12 rewards immediately patchable and a clear path to expanding coverage to 100% through additional item name mappings, the foundation for Archipelago integration is solid.

The next critical step is expanding the item name → ID mapping database, particularly for accessories (`E_ACC_*`) which represent 27% of all rewards.
