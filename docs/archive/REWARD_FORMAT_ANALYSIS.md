# Reward.uasset Binary Format - Reverse Engineering Progress

## Discovered Structure

**File:** `Resident/Reward.uasset` + `Reward.uexp`
**Format:** EndDataObjectReward (custom UE4 class)
**Total Size:** 248,116 bytes (bulk data in .uexp)

## Pattern Analysis

### Entry Structure (20-byte pattern most common)
```
Reward Entry {
    // Header (12-20 bytes - varies by type)
    uint32 reward_name_index;  // Index into name table
    uint32 unknown_1;          // Possibly reward type/flags
    uint32 unknown_2;          // Possibly count or ID
    // ... more header fields
    
    // Item Data (starts at +12 or +20 from reward start)
    uint32 item_name_index;    // Index into name table for item name
    uint32 quantity;           // Item quantity
    // Possibly more fields per item
}
```

### Observed Patterns
- **First item offsets:** +12, +16, +20, +32, +36, +40, +80 bytes
- **Item spacing:** Typically 20 bytes apart
- **89 reward entries** total, 73 with parseable item data

## Sample Entries

```
rwrShootingGame_Main_Gold:
  - it_material_enemy_002 at +20

rwr2110_Yuffie_Join:
  - it_key_chocobo_custom_031 at +20
  - it_material_rock_011 at +80

rwr1360_treasure005_00:
  - it_key_chocobo_custom_028 at +12
  - it_crystal_Titan3 at +16
  - it_key_oceanTreasureMemo at +20
```

## Next Steps to Complete Patcher

### 1. Binary Structure Parser (70% complete)
- ✅ Identified reward entry offsets
- ✅ Found item name indices
- ⬜ Need to determine exact structure fields
- ⬜ Find quantity field offset
- ⬜ Understand header variations

### 2. Item ID Mapping
**Problem:** Name indices reference item NAMES (it_potion), not IDs (100)
**Solution needed:** Find item name → ID mapping
- Check for another data file (ItemMaster.uasset?)
- Or build mapping from Memory Bridge's working item table

### 3. Write-Back Implementation
Once structure is understood:
```python
def patch_reward(reward_name, new_item_name, quantity):
    # Find reward entry offset
    # Calculate item field offset
    # Write new item name index
    # Write quantity
    # Rebuild .uasset/.uexp
```

### 4. UAssetAPI Write Support
Extend UAssetExporter to:
- Modify NormalExport.Extras bytes
- Recalculate offsets/sizes
- Write valid .uasset/.uexp pair

## Alternative: Find Item Master Data

Search for:
```
ItemMaster.uasset
ItemData.uasset
ItemDatabase.uasset
```

These likely contain `item_name → item_id` mappings we need.

## Current Blockers

1. **Name vs ID:** We can find item names (it_potion) but need numeric IDs (100) for actual patching
2. **Structure ambiguity:** Variable offsets suggest multiple reward types
3. **Write-back:** Need UAssetAPI Write() with proper Extras handling

## Recommendation

**Next immediate action:** Search for Item master data file to get name→ID mappings, then complete the binary patcher.
