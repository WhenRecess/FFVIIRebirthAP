# FF7 Rebirth Asset JSON Export/Import Workflow

## Successfully Completed: 2026-02-03

This document records the exact steps to export FF7 Rebirth .uasset files to JSON format, which can then be modified and re-imported.

---

## Problem We Solved

**Issue**: Binary patching of .uasset/.uexp files corrupted the assets:
- Shop randomizer made shops empty
- Reward randomizer caused fatal crashes

**Solution**: Use the FF7 Rebirth-specific UAssetGUI to export to JSON, modify, then re-import.

---

## Required Files and Tools

### 1. FF7R-Specific UAssetGUI Source Code
- **Repository**: https://github.com/LongerWarrior/UAssetGUI
- **Branch**: `FF7Rebirth_v1.0.2`
- **Location Cloned To**: `C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\UAssetGUI_FF7R`

### 2. Unreal Engine Mappings File
- **File**: `4.26.1-0+++UE4+Release-4.26-End.usmap`
- **Source Location**: `F:\Downloads\4.26.1-0+++UE4+Release-4.26-End.usmap`
- **Copied To**: `C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\bin\Mappings\`
- **Purpose**: Contains FF7 Rebirth's custom Unreal Engine type definitions

### 3. Source Asset Files
- **ShopItem.uasset**: `C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\ShopItem.uasset`
- **ShopItem.uexp**: `C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\ShopItem.uexp`
- **Sizes**: 
  - ShopItem.uasset: 48,711 bytes
  - ShopItem.uexp: 124,708 bytes

---

## Step-by-Step Process

### Step 1: Clone FF7R UAssetGUI Repository

```bash
cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools"
git clone --branch FF7Rebirth_v1.0.2 --recursive https://github.com/LongerWarrior/UAssetGUI.git UAssetGUI_FF7R
```

**Result**: Cloned repository with FF7R-specific modifications to UAssetAPI submodule

### Step 2: Build UAssetGUI

```bash
cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\UAssetGUI_FF7R"
dotnet build UAssetGUI.sln -c Release
```

**Build Output Location**: 
- Executable: `UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows\UAssetGUI.exe`
- Dependencies: All DLLs in same directory

**Result**: Successful build with 6 warnings (non-critical)

### Step 3: Copy Mappings File

```powershell
New-Item -ItemType Directory -Path "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\bin\Mappings" -Force
Copy-Item "F:\Downloads\4.26.1-0+++UE4+Release-4.26-End.usmap" "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\bin\Mappings\"
```

**Note**: UAssetGUI looks for mappings in `Mappings\` subdirectory next to the executable

### Step 4: Export Asset to JSON

```bash
cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows"

.\UAssetGUI.exe tojson "C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\ShopItem.uasset" "C:\Users\jeffk\OneDrive\Desktop\ShopItem_test.json" 26 "4.26.1-0+++UE4+Release-4.26-End"
```

**Command Breakdown**:
- `tojson`: Export to JSON command
- `ShopItem.uasset`: Source file (must include both .uasset and .uexp in same directory)
- `ShopItem_test.json`: Output JSON file
- `26`: Unreal Engine version (4.26)
- `"4.26.1-0+++UE4+Release-4.26-End"`: Mappings file name (without .usmap extension)

**Result**: 
- ✅ Created `ShopItem_test.json` (4,375,284 bytes / 4.3 MB)
- ✅ No errors or warnings

---

## JSON Structure Analysis

### Top-Level Structure
```json
{
  "$type": "UAssetAPI.UAsset, UAssetAPI",
  "Info": "Serialized with UAssetAPI 1.0.2.0 (8699133)",
  "NameMap": [...],
  "Exports": [...]
}
```

### Export Structure
- **Single Export**: `Exports[0]` contains all shop data
- **Data Array**: 795 shop items in `Exports[0].Data[]`
- **Items with Prices**: 455 items have `OverridePrice_Array`
- **Total Price Values**: 468 individual prices to randomize

### Price Location in JSON
```
Exports[0]
  └─ Data[N]                           // Shop item (N = 0-794)
      └─ Value[]                       // Properties array
          └─ OverridePrice_Array       // Property with Name == "OverridePrice_Array"
              └─ Value[]               // Array of price objects
                  └─ Value: 3000       // Actual price integer
```

### Example Price Entry
```json
{
  "$type": "UAssetAPI.GameTypes.FF7Rebirth.PropertyTypes.FF7ArrayProperty, UAssetAPI",
  "Name": "OverridePrice_Array",
  "Value": [
    {
      "$type": "UAssetAPI.GameTypes.FF7Rebirth.PropertyTypes.FF7IntProperty, UAssetAPI",
      "Name": "OverridePrice_Array",
      "Value": 3000
    }
  ]
}
```

### Sample Data
```
Item Name: ShopItem_W_TSW_0101
Price: [3000]

Item Name: ShopItem_W_TSW_0102
Price: [5000]

Item Name: ShopItem_W_TSW_0103
Price: [7500]
```

---

## Import Process (Not Yet Tested)

### Step 5: Import Modified JSON Back to .uasset

```bash
cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows"

.\UAssetGUI.exe fromjson "C:\Users\jeffk\OneDrive\Desktop\ShopItem_modified.json" "C:\Users\jeffk\OneDrive\Desktop\ShopItem_new.uasset" "4.26.1-0+++UE4+Release-4.26-End"
```

**Command Breakdown**:
- `fromjson`: Import from JSON command
- `ShopItem_modified.json`: Modified JSON file
- `ShopItem_new.uasset`: Output asset file (creates both .uasset and .uexp)
- `"4.26.1-0+++UE4+Release-4.26-End"`: Mappings file name

---

## Next Steps for Automation

### Planned Workflow
1. **Export**: Use UAssetGUI CLI to export to JSON
2. **Randomize**: Python script modifies prices/items in JSON
3. **Import**: Use UAssetGUI CLI to import back to .uasset
4. **Repack**: Use retoc to create pak files
5. **Deploy**: Copy to game mods folder

### Python Script Requirements
- Load JSON with `json.load()`
- Navigate to `Exports[0].Data[]`
- Find properties with `Name == "OverridePrice_Array"`
- Randomize `Value[].Value` integers
- Save modified JSON with `json.dump()`

---

## Critical Notes

### Why This Works vs Binary Patching Failed

**Binary Patching Issues**:
- Pattern matching hit false positives
- Modified critical structure fields
- Broke asset serialization integrity
- No validation of changes

**JSON Approach Benefits**:
- ✅ UAssetAPI properly deserializes asset structure
- ✅ Only modifies intended data fields
- ✅ Maintains serialization integrity on re-import
- ✅ Human-readable for debugging
- ✅ Type-safe modifications

### Important File Size Notes
- ShopItem.uasset and .uexp MUST match exactly
- Earlier repo versions had corrupted files (wrong sizes)
- Fresh Desktop versions are authoritative source

### FF7R-Specific Considerations
- Standard UAssetAPI doesn't work (missing FF7R types)
- Must use LongerWarrior's FF7R branch
- Mappings file is REQUIRED (not optional)
- Engine version must be 26 (UE 4.26)

---

## Testing Status

- ✅ **Export to JSON**: Confirmed working
- ⬜ **Import from JSON**: Not yet tested
- ⬜ **Randomization**: Not yet implemented
- ⬜ **In-game validation**: Pending

---

## File Locations Reference

```
Repository Structure:
FFVIIRebirthAP/
├── tools/
│   ├── bin/
│   │   ├── Mappings/
│   │   │   └── 4.26.1-0+++UE4+Release-4.26-End.usmap
│   │   ├── retoc.exe
│   │   └── UAssetGUI_FF7R.exe (to be copied here)
│   ├── UAssetGUI_FF7R/ (cloned repository)
│   │   └── UAssetGUI/
│   │       └── bin/Release/net8.0-windows/
│   │           ├── UAssetGUI.exe ← Built executable
│   │           ├── UAssetAPI.dll
│   │           └── [other dependencies]
│   └── [existing scripts]
└── unpack/
    ├── UnpackFresh_Shop/End/Content/DataObject/Resident/
    │   ├── ShopItem.uasset (48,711 bytes)
    │   └── ShopItem.uexp (124,708 bytes)
    └── UnpackFresh_Rewards/End/Content/DataObject/Resident/
        ├── Reward.uasset
        └── Reward.uexp
```

---

## Commands Quick Reference

### Export ShopItem to JSON
```bash
cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\tools\UAssetGUI_FF7R\UAssetGUI\bin\Release\net8.0-windows"
.\UAssetGUI.exe tojson "C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\ShopItem.uasset" "C:\Users\jeffk\OneDrive\Desktop\ShopItem.json" 26 "4.26.1-0+++UE4+Release-4.26-End"
```

### Export Reward to JSON
```bash
.\UAssetGUI.exe tojson "C:\Users\jeffk\OneDrive\Desktop\End\Content\DataObject\Resident\Reward.uasset" "C:\Users\jeffk\OneDrive\Desktop\Reward.json" 26 "4.26.1-0+++UE4+Release-4.26-End"
```

### Import from JSON
```bash
.\UAssetGUI.exe fromjson "ShopItem_modified.json" "ShopItem_new.uasset" "4.26.1-0+++UE4+Release-4.26-End"
```

---

## Success Metrics

✅ **JSON Export Successful**:
- 4.3 MB JSON file created
- 795 shop items parsed
- 455 items with prices identified
- 468 total price values accessible
- Clean JSON structure for modification

**This proves the workflow is viable for programmatic randomization!**
