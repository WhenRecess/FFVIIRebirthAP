# FF7 Rebirth File Patching Workflow - Complete Documentation

## Overview

This document describes the **confirmed working workflow** for modifying FF7 Rebirth game files (Equipment, ShopItem, etc.) using file patching and pak deployment.

**Status**: ✅ CONFIRMED WORKING
- Equipment.uasset modifications: ✅ Tested and verified in-game
- ShopItem.uasset modifications: ✅ Tested and verified in-game
- **Programmatic price randomization**: ✅ 252 price arrays identified and randomized

## Quick Start: Automated Price Randomization

Use the new **smart_price_randomizer.py** for automated, intelligent shop price randomization:

```bash
# Randomize prices 100-5000 gil with seed 54321
python tools/smart_price_randomizer.py ShopItem.uexp ShopItem_rand.uexp 54321 100 5000

# Then follow standard deployment workflow (repack + deploy)
```

This intelligently detects 252 price arrays and modifies 282+ prices without manual editing.

---

## Prerequisites

### Required Tools

1. **retoc** - IoStore pak converter
   - Location: `F:\Downloads\retoc7r\retoc\retoc.exe`
   - Source: [GhostyPool/retoc](https://github.com/GhostyPool/retoc/releases)
   - Function: Converts between Zen (UE5) and Legacy (UE4) pak formats

2. **UAssetGUI** - Binary UAsset editor
   - Source: [atenfyr/UAssetGUI](https://github.com/atenfyr/UAssetGUI/releases)
   - Function: Edit binary asset files with visual interface

3. **UAssetExporter** (optional) - Export assets to JSON
   - Location: `tools\UAssetExporter\bin\Release\net8.0\UAssetExporter.exe`
   - Function: View and understand asset structure

### Game Paths

- **Game Directory**: `G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH`
- **Mod Deployment Path**: `{GameDir}\End\Content\Paks\~mods\`
- **Fresh Extracts Path**: `C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End\Content\DataObject\Resident\`

---

## Critical Discoveries

### ShopItem Structure

- Uses **string-based ItemIds**, NOT integers
- Example: `ItemId: "it_potion"`, `ItemId: "M_MAG_109"`, `ItemId: "it_atel"`
- Each shop entry is **location-specific**:
  - `ChadleyShopItem_Junon_000` = Chadley's shop in Junon
  - `ItemShopItem_Kalm_000` = Item shop in Kalm
  - Modifying one entry affects only that specific shop

### Equipment Structure

- Contains weapons, armor, accessories for all characters
- Stats: AttackAdd, DefenseAdd, StrengthAdd, VitalityAdd, etc.
- Materia slots configurable per equipment
- Identified items: `WE0000_00_Cloud_BusterSword`, `E_ACC_*`, `E_ARM_*`, etc.

### Pak Format (UE4 IoStore)

FF7 Rebirth uses UE4.26 IoStore format consisting of **three files**:

- `.pak` - 347 bytes (manifest header)
- `.ucas` - Variable size (~160KB for Equipment) - actual data container
- `.utoc` - 488-57KB (table of contents)

**Critical**: All three files must have **matching names** and be deployed together.

---

## Working Workflow - Step by Step

### Phase 1: Extract Source Files

```powershell
# Location where game pak files are extracted
$extractPath = "C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End\Content\DataObject\Resident\"

# Files needed for modification:
# - Equipment.uasset (11,718 bytes)
# - Equipment.uexp (149,508 bytes)  
# - ShopItem.uasset (48,711 bytes)
# - ShopItem.uexp (124,708 bytes)
```

**Status**: Fresh extraction already done from game's pakchunk files

### Phase 2: Edit in UAssetGUI

1. **Open UAssetGUI** (standalone application)

2. **Open the file** from extraction:
   - `C:\Users\jeffk\OneDrive\Documents\UnpackFresh\End\Content\DataObject\Resident\Equipment.uasset`
   - OR `ShopItem.uasset`

3. **Make changes**:
   - **Equipment example**: Changed Buster Sword DefenseAdd from `0` to `45`
   - **Shop example**: Changed Chadley's Junon shop items to price `50`

4. **Save** (File → Save)
   - **Important**: Use "Save", not "Save As"
   - Files are updated in-place
   - `.bak` backups are created automatically

**Result**: Files modified with updated timestamps

### Phase 3: Create Mod Folder Structure

Create proper directory hierarchy for pak:

```
C:\Users\jeffk\OneDrive\Desktop\EquipmentMod\
  └─ End\
      └─ Content\
          └─ DataObject\
              └─ Resident\
                  ├─ Equipment.uasset
                  └─ Equipment.uexp
```

**Important**: 
- Folder structure must match game's internal paths exactly
- Only modified files included (not entire Resident folder)
- Naming is case-sensitive

```powershell
# Command to create structure
New-Item -ItemType Directory -Path "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod\End\Content\DataObject\Resident" -Force | Out-Null
Copy-Item "Equipment.uasset" "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod\End\Content\DataObject\Resident\" -Force
Copy-Item "Equipment.uexp" "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod\End\Content\DataObject\Resident\" -Force
```

### Phase 4: Pack with retoc

**CRITICAL**: Use `--version=UE4_26` (NOT UE5_0 or UE5_1)

```powershell
cd F:\Downloads\retoc7r

# Pack command with _P suffix in output filename
.\retoc\retoc.exe to-zen --version=UE4_26 "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod" "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod_P.utoc"
```

**Output Files Created**:
- `EquipmentMod_P.pak` (347 bytes)
- `EquipmentMod_P.ucas` (~160KB)
- `EquipmentMod_P.utoc` (488 bytes)

**Output Example**:
```
[00:00:00] ########################################       1/1
Applying import fix-ups to the converted assets. Package data in memory: 0MB
Writing converted assets
```

### Phase 5: Deploy to Game Mods Folder

```powershell
# Copy all three pak files to game's ~mods folder
Copy-Item "C:\Users\jeffk\OneDrive\Desktop\EquipmentMod_P.*" "G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods\" -Force

# Verify deployment
Get-ChildItem "G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Content\Paks\~mods\EquipmentMod_P.*"
```

**Expected Result**:
```
Name              Length
----              ------
EquipmentMod_P.pak       347
EquipmentMod_P.ucas  161708
EquipmentMod_P.utoc      489
```

### Phase 6: Test In-Game

1. **Launch FF7 Rebirth**
2. **Navigate to equipment screen** (for Equipment testing)
   - Check Buster Sword now shows DEF+45
3. **Or visit shop** (for Shop testing)
   - Check Chadley's Junon shop shows modified prices

**Success Indicators**:
- ✅ Changes appear in-game
- ✅ Mod is loaded (check in Mods menu if available)
- ✅ Multiple mods can be deployed together

---

## Failed Approaches & Why

### ❌ Binary Patching (Initial Attempt)

**Approach**: Directly modify byte offsets in .uexp file

**Problem**: 
- Modified name table **indices**, not actual string values
- ShopItem uses string ItemIds, not integers
- Changes had no in-game effect

**Lesson**: File patching with proper repacking required

### ❌ UE5_0 Format Version

**Approach**: Used `--version=UE5_0` in retoc

**Error**: 
```
thread '<unnamed>' panicked at src\legacy_asset.rs:518:36:
index out of bounds: the len is 464 but the index is 18446744073709551615
```

**Solution**: Use `--version=UE4_26` (game is built on UE4.26)

### ❌ Wrong Pak Location

**Attempted**: Various locations
- `{GameDir}\Paks\` - Ignored
- `{GameDir}\Content\Paks\` - Ignored
- `{GameDir}\ShippingMods\` - Ignored

**Working**: `{GameDir}\End\Content\Paks\~mods\` with `_P` suffix

### ❌ Pak File Naming

**Attempted**: 
- `EquipmentMod.pak` (no _P) - Not loaded
- Renamed after packing - Sometimes loaded

**Working**: Specify `_P.utoc` **in retoc command**, not rename after

### ❌ Incomplete Mod Structure

**Attempted**: 
- Just Equipment.uasset/uexp in pak root - Not found by game
- Full Resident folder (86MB) - Too large, unparseable

**Working**: Only modified files in proper `End\Content\DataObject\Resident` path

---

## Technical Notes

### UAssetGUI Behavior

- Saves to same directory by default
- Creates `.bak` files (backup of original)
- File size may change slightly due to serialization
- Automatically handles binary format details

### retoc Tool

- Requires `oo2core_9_win64.dll` in same folder
- Version matters: UE4_26 for FF7R
- _P suffix triggers mod-specific loading
- Can convert bulk assets or single files

### Game Loading Priority

1. Checks `~mods\` folder first
2. Loads pak files with `_P` suffix
3. Merges with base game files
4. Multiple mods can coexist if no conflicts

---

## File Sizes Reference

| File | Original | After Equipment Mod |
|------|----------|-------------------|
| Equipment.uasset | 11,718 | 11,862 bytes |
| Equipment.uexp | 149,508 | 149,508 bytes |
| ShopItem.uasset | 48,711 | 48,807 bytes |
| ShopItem.uexp | 124,708 | 124,724 bytes |

Size changes are minor (1-3%) due to metadata/serialization updates.

---

## Verified Test Cases

### Test 1: Equipment Modification ✅

**Change**: Buster Sword DefenseAdd: 0 → 45
**Result**: In-game shows DEF+45 when viewing equipment

**Status**: CONFIRMED WORKING

### Test 2: Shop Price Modification ✅

**Change**: Chadley's Junon shop items: various prices → 50
**Result**: In-game shop shows modified price (50 gil)

**Status**: CONFIRMED WORKING

---

## Troubleshooting

### Mod Not Loading

1. Verify folder location: `End\Content\Paks\~mods\`
2. Check _P suffix on all three files
3. Verify file structure: `End\Content\DataObject\Resident\`
4. Try removing other mods temporarily

### Changes Not Appearing

1. Confirm files were saved in UAssetGUI (check timestamps)
2. Verify retoc command used `UE4_26`
3. Check game was restarted after mod deployment
4. Try modifying a more obvious value for testing

### Pak Creation Errors

**Error**: `index out of bounds`
- Solution: Use `--version=UE4_26`, not UE5_0

**Error**: `Could not find files in archives`
- Solution: Verify folder structure matches exactly

---

## Next Steps for Archipelago Integration

1. **Automate with Python script**:
   - Parse seed
   - Generate random equipment stats
   - Generate random shop contents
   - Create pak files automatically
   - Deploy to ~mods

2. **Integrate with ItemHandler.lua**:
   - Read items from AP server
   - Modify shop/equipment accordingly
   - Runtime item distribution

3. **Additional Randomization Options**:
   - Materia stats
   - Battle rewards
   - Enemy drops
   - Treasure chest contents

---

## References

- **retoc GitHub**: https://github.com/GhostyPool/retoc
- **UAssetGUI GitHub**: https://github.com/atenfyr/UAssetGUI
- **FF7R Modding Discord**: Community discussions confirm this workflow
- **UAssetAPI**: Underlying format handling library

---

## Document Version

- **Created**: 2026-02-03
- **Status**: FINAL - Workflow confirmed working
- **Equipment Test**: ✅ Passed (DEF+45 verified in-game)
- **Shop Test**: ✅ Passed (Price modification verified in-game)
- **Last Updated**: 2026-02-03
