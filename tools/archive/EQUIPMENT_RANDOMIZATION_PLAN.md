# Next: Equipment.uasset Programmatic Modification

## Overview

Now that we've successfully created smart_price_randomizer.py for ShopItem prices, the same approach should work for Equipment.uasset to randomize weapon/armor stats.

## Equipment Structure (Hypothesis)

Based on ShopItem analysis, Equipment.uasset likely contains:

```
[Structure Header]
[Equipment 1] → [Stat 1] [Stat 2] [Stat 3] ... [Stat N]
[Equipment 2] → [Stat 1] [Stat 2] [Stat 3] ... [Stat N]
...
```

Stat values are likely 4-byte integers similar to prices:
- AttackAdd: 0-50 range typically
- DefenseAdd: 0-50 range typically
- MagicAdd: 0-30 range typically
- Vitality: 0-20 range typically

## Known Structure

From UAssetGUI inspection (as shown in equipment example):
```json
{
  "Name": "Equipment_Buster_Sword_000",
  "Value": [
    {"Name": "AttackAdd", "Value": 45},
    {"Name": "DefenseAdd", "Value": 0},
    ...
  ]
}
```

Binary equivalent: 4-byte integers for each stat

## Implementation Plan

### Step 1: Analyze Equipment Binary Structure

```bash
# Create similar analyzer for Equipment
python DetailedStructureAnalyzer.exe Equipment.uexp
```

Expected output:
- Number of structures (weapons/armor/accessories)
- Stat field offsets
- Stat value ranges

### Step 2: Create smart_equipment_randomizer.py

```bash
# Duplicate and adapt smart_price_randomizer.py
python smart_equipment_randomizer.py Equipment.uexp Equipment_rand.uexp 54321 min_atk max_atk min_def max_def ...
```

### Step 3: Repack and Deploy

```bash
retoc.exe to-zen --version UE4_26 UnpackFresh/End EquipmentModName_Zen
cp EquipmentModName_Zen.* "%LOCALAPPDATA%\FF7Rebirth\Saved\Paks\~mods\"
```

### Step 4: Test In-Game

Verify stats changed correctly for weapons/armor/accessories

## Detection Strategy

Similar to ShopItem:

1. **Stat ranges**: AttackAdd (0-50), DefenseAdd (0-50), MagicAdd (0-30), etc.
2. **Regular spacing**: Stats likely at fixed offsets (0x00, 0x04, 0x08, etc.)
3. **Equipment count**: ~100-200 equipment items expected
4. **Stat count**: 5-10 stats per item

## Known Stats (from Equipment.json)

Look for these stat names in UAssetGUI:
- `AttackAdd`
- `DefenseAdd`
- `MagicAdd`
- `MagicDefenseAdd`
- `Vitality`
- `Spirit`
- `Dexterity`
- `Luck`
- `FireResist`
- `IceResist`
- `ElectricResist`
- `WindResist`
- `HolyResist`
- `DarkResist`
- `StatusResist`

## File Locations

| File | Path |
|------|------|
| Equipment.uasset | `C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End\Content\DataObject\Resident\Equipment.uasset` |
| Equipment.uexp | `C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End\Content\DataObject\Resident\Equipment.uexp` |
| Exported JSON | `tools\Equipment_export.json` |

## Success Criteria

✅ Smart equipment randomizer created
✅ Stat ranges properly detected
✅ All equipment stats randomized
✅ Randomization reproducible with seed
✅ In-game verification passes
✅ No binary corruption

## Integration with AP

Once both ShopItem and Equipment randomization work:

1. **Create ApRandomizer wrapper**:
   ```python
   ap_seed = get_ap_seed()
   randomize_shop_items(seed=ap_seed, min_price=..., max_price=...)
   randomize_equipment_stats(seed=ap_seed, stat_ranges=...)
   ```

2. **Generate seed-based location items**:
   - Connect randomized prices to AP item location system
   - Connect randomized equipment to AP progression

3. **Full workflow**:
   ```
   AP Seed → Python randomizers → Modified uassets → 
   retoc packaging → Mod deployment → Game loads with randomization
   ```

---

## References

- ShopItem randomizer: [smart_price_randomizer.py](./smart_price_randomizer.py)
- Binary analysis tool: [DetailedStructureAnalyzer](./DetailedStructureAnalyzer/Program.cs)
- Workflow docs: [MODDING_WORKFLOW.md](./MODDING_WORKFLOW.md)
- Structure breakthrough: [BINARY_STRUCTURE_BREAKTHROUGH.md](./BINARY_STRUCTURE_BREAKTHROUGH.md)

