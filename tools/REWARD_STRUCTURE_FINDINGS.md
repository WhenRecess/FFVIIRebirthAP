# Reward Structure Analysis - Findings

**Date**: February 3, 2026  
**Issue**: #5 - Analyze Reward.uasset structure  
**Status**: Major breakthrough - structure identified

## Key Discovery

Reward entries use **string name references** to items, not integer IDs stored directly in binary.

## Reward Entry Structure

From UAssetGUI JSON export of `rwr2250_treasure008_00`:

```json
{
  "$type": "FF7StructProperty",
  "Name": "rwr2250_treasure008_00",
  "Value": [
    {
      "$type": "FF7ArrayProperty",
      "ArrayType": "FF7NameProperty",
      "Name": "ItemID_Array",
      "Value": [
        {
          "$type": "FF7NameProperty",
          "Value": "M_MAG_107"  // ← Item referenced by STRING name
        }
      ]
    },
    {
      "$type": "FF7ArrayProperty",
      "ArrayType": "FF7IntProperty",
      "Name": "ItemCount_Array",
      "Value": [
        {
          "$type": "FF7IntProperty",
          "Value": 1  // ← Count is integer
        }
      ]
    },
    {
      "$type": "FF7ArrayProperty",
      "ArrayType": "FF7ByteProperty",
      "Name": "ItemAddType_Array",
      "Value": []  // ← Can be empty
    },
    {
      "$type": "FF7IntProperty",
      "Name": "UniqueIndex",
      "Value": 2321  // ← Unique identifier for this reward
    }
  ]
}
```

## Structure Breakdown

Each reward entry is a `FF7StructProperty` containing:

1. **ItemID_Array** (FF7NameProperty[])
   - Item identifiers as **string names** (e.g., "M_MAG_107", "M_ACC_023")
   - References items from the game's item name table
   - NOT integer IDs - this is why binary analysis couldn't find direct matches

2. **ItemCount_Array** (FF7IntProperty[])
   - Integer counts for each item (typically 1, but can be higher)
   - Array length matches ItemID_Array

3. **ItemAddType_Array** (FF7ByteProperty[])
   - Byte values indicating how item is added
   - Can be empty (default behavior)

4. **StateCondision_Array** (FF7NameProperty[])
   - Conditional states (often empty)

5. **IntegerArgument_Array** (FF7IntProperty[])
   - Additional integer arguments (often empty)

6. **UniqueIndex** (FF7IntProperty)
   - Unique identifier for the reward entry
   - Should NOT be randomized

## Implications for Randomization

### What This Means

1. **Cannot use simple binary patching** like shop prices
   - Shop prices are arrays of integers we can directly replace
   - Rewards use UE4 name references (indices into name table)

2. **Must use UAssetAPI** for proper modification
   - UAssetAPI can properly parse UE4 asset structure
   - Can read/modify name references correctly
   - Handles serialization back to .uasset/.uexp format

3. **Name table considerations**
   - Item names are stored in the .uasset file's name table
   - .uexp file contains indices into that table
   - Must ensure all item names we want to use are in the name table

### Randomization Strategy

**Workflow** (same as shop price randomizer):

```
1. Export Reward.uasset → JSON using UAssetGUI
2. Modify JSON with reward_randomizer.py
   - Randomize ItemID_Array values (item name strings)
   - Preserve ItemCount_Array (quantities)
   - Preserve ItemAddType_Array, UniqueIndex
3. Convert JSON → .uasset/.uexp using ReUE4SS/Retoc
4. Deploy to game mods folder
```

**Python script** (`reward_randomizer.py`):
```python
# Load exported JSON from UAssetGUI
# Find all ItemID_Array properties recursively
# Replace item name strings with random valid items
# Save modified JSON for reconversion
```

## Comparison with Shop Prices

| Feature | Shop Prices | Rewards |
|---------|------------|---------|
| Data type | Integer arrays | Name reference arrays |
| Modification | Direct binary patching | JSON export → modify → reconvert |
| Workflow | Binary scanning | UAssetGUI → Python → ReUE4SS |
| Complexity | Simple (found patterns) | Moderate (JSON parsing) |
| Status | ✅ Working | ✅ Script created |

## Implementation Complete ✅

**Status**: reward_randomizer.py working and tested

**Approach**: 
- Load parsed reward data (_reward_parsed.json) with 289 known item indices
- Randomize values at those specific offsets in binary Reward.uexp
- Repack with retoc and deploy to game mods folder

**Results**:
- Successfully identifies 88 reward entries with 289 item references
- Safely modifies ONLY known locations (no false positives)
- Auto-deploys with full retoc repacking pipeline
- Creates seed-based pak files in game mods folder

**Usage**:
```bash
# Manual randomization
python reward_randomizer.py Reward.uexp Reward_randomized.uexp 12345

# Auto-deploy with repacking
python reward_randomizer.py Reward.uexp --auto-deploy 12345
```

**Next Steps**:
1. Test randomized rewards in-game
2. Verify items appear correctly and game doesn't crash
3. If working: repeat for Equipment randomization (Issue #15)
4. Create seed pipeline (Issue #11)
