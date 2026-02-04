# Data Files

This directory contains extracted and processed game data used by the FF7R Archipelago randomizer.

## Essential Mapping Files

### Item Mappings

#### `_ce_all_real_ids.json`

- **Source**: Extracted from Item.uexp via Cheat Engine scanning
- **Contents**: 502 confirmed item IDs
- **Format**: `{ "ItemName": CE_ID, ... }`
- **Usage**: Primary item ID reference for game modifications
- **Status**: ✅ Complete and verified

#### `_complete_item_mappings.json`

- **Source**: Consolidated from multiple extraction methods
- **Contents**: Comprehensive item database with names, IDs, types
- **Usage**: Main reference for AP item definitions
- **Status**: ✅ Complete

#### `_complete_item_mappings_detailed.json`

- **Source**: Enhanced version with additional metadata
- **Contents**: Detailed item information including categories, descriptions
- **Usage**: Extended item data for advanced features
- **Status**: ✅ Complete

#### `_item_master.json`

- **Source**: Master item database from game files
- **Contents**: All game items with properties
- **Usage**: Reference for item properties and relationships

#### `_item_name_to_id.json`

- **Source**: Generated from item extractions
- **Contents**: Simple name → ID lookup table
- **Format**: `{ "Item Name": ID, ... }`
- **Usage**: Quick item ID lookups

### Equipment Mappings

#### `_equipment_master.json`

- **Source**: Extracted from Equipment.uasset
- **Contents**: All equipment items with stats and properties
- **Usage**: Equipment randomization reference

#### `_equipment_enum_mappings.json`

- **Source**: Enum value mappings from game assets
- **Contents**: Equipment type enums and IDs
- **Usage**: Equipment type identification

#### `_e_acc_mappings.json` / `_e_acc_to_id.json` / `_e_acc_to_id_extracted.json`

- **Source**: Accessory-specific mappings
- **Contents**: Accessory item mappings
- **Usage**: Accessory randomization
- **Status**: Intermediate files, may consolidate later

### Reward System

#### `_reward_master.json`

- **Source**: Extracted from game reward tables
- **Contents**: All reward definitions and drop tables
- **Usage**: Location randomization, reward tracking

#### `_reward_parsed.json` / `_reward_structure_analysis.json`

- **Source**: Parsed reward data
- **Contents**: Structured reward information
- **Usage**: Understanding reward system structure

#### `_reward_test*.json` (multiple files)

- **Source**: Test outputs during reward parser development
- **Contents**: Various reward parsing attempts
- **Status**: Historical, may be removed in future cleanup

### Shop Data

#### `_shopitem.json`

- **Source**: Exported from ShopItem.uasset
- **Contents**: All shop item definitions and prices
- **Usage**: Reference for shop randomization
- **Note**: Smart price randomizer works directly on binary, doesn't require this

### Location/Treasure Data

#### `_treasure_kalmt.json` / `_treasure_kalmt_uassetapi.json`

- **Source**: Extracted from Kalm treasure data tables
- **Contents**: Treasure chest locations and contents for Kalm area
- **Usage**: Location mapping for AP

#### `_treasure_midga_mapped.json`

- **Source**: Extracted from Midgar treasure data
- **Contents**: Treasure chest locations and contents for Midgar area
- **Usage**: Location mapping for AP

#### `_itemdrop_midga_uassetapi.json`

- **Source**: Item drop tables for Midgar
- **Contents**: Enemy drop information
- **Usage**: Understanding item drop system

### Special Items

#### `_special_items_mappings.json`

- **Source**: Extracted special/key items
- **Contents**: Story items, key items, unique items
- **Usage**: Identifying items that shouldn't be randomized or need special handling

#### `_unmapped_items.json`

- **Source**: Items without complete mappings
- **Contents**: Items that need additional research
- **Status**: Historical, most items now mapped

### Intermediate Files

#### `_all_item_mappings.json`

- **Status**: Intermediate, superseded by \_complete_item_mappings.json

#### `_ce_real_item_ids.json`

- **Status**: Intermediate, superseded by \_ce_all_real_ids.json

#### `_mappings_stats.json`

- **Source**: Statistics about mapping completeness
- **Contents**: Counts of mapped vs unmapped items

### Export Files

#### `Equipment_export.json`

- **Source**: UAssetGUI export of Equipment.uasset
- **Contents**: Full Equipment asset structure
- **Usage**: Reference for understanding Equipment structure
- **Note**: Can be regenerated from game files

#### `ShopItem_export.json`

- **Source**: UAssetGUI export of ShopItem.uasset
- **Contents**: Full ShopItem asset structure
- **Usage**: Reference for understanding ShopItem structure
- **Note**: Can be regenerated from game files

### Text Reports

#### `_final_parse_output.txt`

- **Source**: Final parsing run output
- **Contents**: Human-readable parse results

#### `_reward_report.txt`

- **Source**: Reward system analysis report
- **Contents**: Analysis of reward structures

---

## File Naming Convention

- **Underscore prefix** (`_`): Indicates generated/extracted data file
- **`master`**: Comprehensive data from primary source
- **`mappings`**: Lookup tables for ID/name conversions
- **`parsed`/`test`**: Processing outputs, may be intermediate
- **`export`**: Direct exports from UAssetGUI or other tools

---

## Usage in AP Development

### For Item Randomization

```python
# Load item mappings
with open('data/_ce_all_real_ids.json') as f:
    item_ids = json.load(f)

# Get item ID for giving items via UE4SS
item_id = item_ids["Elixir"]
```

### For Location Definition

```python
# Load treasure mappings
with open('data/_treasure_kalmt.json') as f:
    locations = json.load(f)
```

### For Shop Randomization

- Use `smart_price_randomizer.py` directly on binary files
- ShopItem_export.json available for reference only

---

## Maintenance Notes

- **Do not manually edit**: These are generated files
- **To regenerate**: Use the extraction scripts in parent directory
- **Source truth**: Game files (`.uasset`/`.uexp` in unpacked paks)
- **Version tracking**: Files may need regeneration after game updates

---

## Data Quality Status

| Category       | Completeness     | Verified       |
| -------------- | ---------------- | -------------- |
| Item IDs       | 100% (502 items) | ✅ Yes         |
| Equipment Data | ~80%             | 🟡 Partial     |
| Reward System  | ~70%             | 🟡 Partial     |
| Location Data  | ~30%             | ❌ In Progress |
| Shop Data      | 100%             | ✅ Yes         |

---

## Next Steps for Data Collection

1. **Complete location mappings** - All treasure chests, enemy drops
2. **Enemy drop tables** - Comprehensive enemy loot data
3. **Quest rewards** - Map all quest completion rewards
4. **Missables tracking** - Identify time-limited items
5. **Progressive items** - Define item chains for AP logic
