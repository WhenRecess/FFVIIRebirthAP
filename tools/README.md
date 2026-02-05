# FF7 Rebirth Archipelago - Tools

Development tools and utilities for the FF7 Rebirth Archipelago randomizer.

## 📖 Documentation

**Start Here**: [AP_DEVELOPMENT_GUIDE.md](AP_DEVELOPMENT_GUIDE.md) - Complete development guide

**Other Docs**:

- [BINARY_STRUCTURE_BREAKTHROUGH.md](BINARY_STRUCTURE_BREAKTHROUGH.md) - Technical deep-dive on price array detection
- [EQUIPMENT_RANDOMIZATION_PLAN.md](EQUIPMENT_RANDOMIZATION_PLAN.md) - Next phase roadmap
- [MODDING_WORKFLOW.md](MODDING_WORKFLOW.md) - File patching workflow details
- [data/README.md](data/README.md) - Data files documentation
- [bin/README.md](bin/README.md) - External tools documentation
- [archive/](archive/) - Historical documents

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- FF7 Rebirth (PC)
- Unpacked game files (use QuickBMS)

### Configuration

Edit `config.ini` with your paths:

```ini
[Paths]
game_dir = G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH
unpack_dir = C:\Users\YourName\Documents\UnpackFresh\End
```

### Run Shop Randomizer

```bash
cd tools
python smart_price_randomizer.py ShopItem.uexp --auto-deploy 12345 100 5000
```

### Run Item Price Randomizer

```bash
cd tools
python item_price_randomizer.py 12345 --auto-deploy
```

### Run Materia Price Randomizer

```bash
cd tools
python materia_price_randomizer.py 12345 --auto-deploy
```

These will randomize prices, repack, and deploy to your game automatically! All three randomizers use the same seed for reproducible results.

## 📁 Directory Structure

```
tools/
├── bin/                              # External binaries (retoc, UAssetGUI)
├── data/                             # Extracted game data (JSON files)
├── archive/                          # Historical documentation
├── UAssetAPI_Source/                 # UAssetAPI library source
├── UAssetExporter/                   # C# export tool
├── config.ini                        # User configuration ⚙️
├── smart_price_randomizer.py        # Shop price randomizer ⭐
├── item_price_randomizer.py         # Item/consumable price randomizer ⭐
├── materia_price_randomizer.py      # Materia sell price randomizer ⭐
├── reward_randomizer.py             # Reward/chest randomizer (experimental)
├── extract_all_ce_ids.py            # Extract item IDs
├── build_item_name_map.py           # Generate item mappings
├── build_equipment_mappings.py      # Generate equipment data
├── generate_item_mappings.py        # Comprehensive item database
├── generate_location_mappings.py    # Location → AP ID mapping
├── reward_smart_parser.py           # Parse reward system
├── filter_ue4ss_functions.py        # Filter UE4SS dumps
├── ff7r_randomizer.py               # Early randomizer (legacy)
├── exporter_example.cs              # UAssetAPI C# example
└── [other extraction/parsing tools]
```

## 🔧 Primary Tools

### smart_price_randomizer.py ⭐

**Automated shop price randomization with full deployment**

**Features**:

- Intelligent binary pattern detection (finds 252-455 price arrays)
- Seed-based deterministic randomization
- Full automation: randomize → repack → deploy
- Self-contained (uses repository tools)

**Usage**:

```bash
python smart_price_randomizer.py <file.uexp> --auto-deploy <seed> <min_price> <max_price>

# Example
python smart_price_randomizer.py ShopItem.uexp --auto-deploy 54321 100 5000
```

**Algorithm**: See BINARY_STRUCTURE_BREAKTHROUGH.md for technical details

### item_price_randomizer.py ⭐

**Randomize consumable and weapon/armor purchase/sell prices**

**Why it works**: Item.uasset contains BuyValue and SaleValue for ALL purchasable items including:

- Consumables (Potions, Hi-Potions, Ethers, etc.)
- Weapons and Armor
- Materia (though their sell prices are overridden by Materia.uasset)

**Features**:

- Extracts fresh Item.uasset from game paks
- Randomizes all BuyValue and SaleValue fields
- Full workflow: extract → export → randomize → import → repack → deploy
- Seed-based deterministic randomization with configurable multiplier range

**Usage**:

```bash
python item_price_randomizer.py <seed> [--min-mult <float>] [--max-mult <float>] [--auto-deploy]

# Example: Randomize with 0.5x to 2.0x multiplier, seed 12345
python item_price_randomizer.py 12345 --auto-deploy

# Custom range: 0.7x to 1.5x
python item_price_randomizer.py 12345 --min-mult 0.7 --max-mult 1.5 --auto-deploy
```

**Output**: Deploys `RandomizedItemPrices_P.ucas/.utoc/.pak` to game mods folder

### materia_price_randomizer.py ⭐

**Randomize materia sell prices by level**

**Why it works**: Materia.uasset contains materia-specific data including `SaleValueLv_Array` fields which define sell prices for each materia at each experience level (1-5). These arrays were empty in the original asset, so we populate them with randomized values.

**Features**:

- Extracts fresh Materia.uasset from game paks
- Populates empty `SaleValueLv_Array` for all sellable materia
- Generates level-scaled sell prices (increases with materia level)
- Full workflow: extract → export → randomize → import → repack → deploy
- Seed-based deterministic randomization with configurable multiplier range

**Usage**:

```bash
python materia_price_randomizer.py <seed> [--min-mult <float>] [--max-mult <float>] [--auto-deploy]

# Example: Randomize with 0.5x to 2.0x multiplier, seed 12345
python materia_price_randomizer.py 12345 --auto-deploy

# Custom range: 0.8x to 1.8x
python materia_price_randomizer.py 12345 --min-mult 0.8 --max-mult 1.8 --auto-deploy
```

**Output**: Deploys `RandomizedMateriaPrices_P.ucas/.utoc/.pak` to game mods folder

**Materia Pricing**: Each materia has 1-5 levels. Sell price increases with level:

- Level 1: 1.0x base price
- Level 2: 1.5x base price
- Level 3: 2.0x base price
- Level 4: 2.5x base price
- Level 5: 3.0x base price

Base prices are defined in the script and can be customized.

### reward_randomizer.py (experimental)

**Randomize chest/quest reward items**

**Why it works**: Reward.uasset contains `ItemID_Array` entries that define which item is granted for each reward entry. This script replaces those item IDs while preserving quantities and other metadata.

**Features**:

- Extracts fresh Reward.uasset from game paks
- Randomizes all `ItemID_Array` entries (name-based item IDs)
- Prefix-aware randomization (keeps item categories when possible)
- Full workflow: extract → export → randomize → import → repack → deploy

**Usage**:

```bash
python reward_randomizer.py <seed> [--auto-deploy] [--exclude-prefix <prefix>]

# Example
python reward_randomizer.py 12345 --auto-deploy

# Exclude key items
python reward_randomizer.py 12345 --exclude-prefix it_key --auto-deploy
```

**Output**: Deploys `RandomizedRewards_P.ucas/.utoc/.pak` to game mods folder

### Data Extraction Tools

#### extract_all_ce_ids.py

Extract all 502 item IDs from game files

```bash
python extract_all_ce_ids.py
# Output: data/_ce_all_real_ids.json
```

#### build_item_name_map.py

Generate item name → ID mappings for AP integration

```bash
python build_item_name_map.py
# Output: Various mapping files in data/
```

#### generate_item_mappings.py / generate_location_mappings.py

Create comprehensive databases for AP world module

```bash
python generate_item_mappings.py
python generate_location_mappings.py
```

## 🔨 C# Tools

### UAssetExporter

Custom C# tool for exporting UAssets to JSON using UAssetAPI

**Build**:

```bash
cd UAssetExporter
dotnet build
```

**Usage**:

```bash
dotnet run -- <uasset_path> <output_json>
```

### exporter_example.cs

Example code demonstrating UAssetAPI usage for DataTable extraction

See file comments for setup instructions and customization.

## 📊 Data Files

All extracted data is in the `data/` directory. See [data/README.md](data/README.md) for detailed documentation.

**Key files**:

- `_ce_all_real_ids.json` - 502 item IDs (verified)
- `_complete_item_mappings.json` - Comprehensive item database
- `_equipment_master.json` - Equipment data
- `_reward_master.json` - Reward system data
- `_treasure_*.json` - Location treasure data

## 🎯 Current Development Status

✅ **Complete**:

- Shop price randomization (working, tested) - `smart_price_randomizer.py`
- Item price randomization (buy/sell prices) - `item_price_randomizer.py`
- Materia price randomization (sell prices by level) - `materia_price_randomizer.py`
- Item ID extraction (502 items)
- File patching workflow (verified in-game)
- Repository self-containment
- All 3 price randomizer mods integrated and tested

🟡 **In Progress**:

- Equipment randomization
- Location mapping
- Reward system consolidation
- Reward randomizer (experimental)

❌ **Not Started**:

- AP world module integration
- UE4SS client connection
- Full multiworld support

## 🚦 Next Steps

1. Apply equipment randomization (Weapon.uasset, Armor.uasset)
2. Complete location mapping (all treasures, drops, rewards)
3. Implement AP world module
4. Create UE4SS runtime client
5. Full integration testing

See [AP_DEVELOPMENT_GUIDE.md](AP_DEVELOPMENT_GUIDE.md) for detailed roadmap.

## 📝 Price Randomization Summary

Three separate mod files handle different price sources:

| Mod Name                    | File            | Affects                                   |
| --------------------------- | --------------- | ----------------------------------------- |
| `RandomizedShop_P`          | ShopItem.uasset | Shop item buy prices (Shelke, Chadley)    |
| `RandomizedItemPrices_P`    | Item.uasset     | Consumable & weapon/armor buy/sell prices |
| `RandomizedMateriaPrices_P` | Materia.uasset  | Materia sell prices (by level)            |

Each mod is **independent** and can be used separately. All three work together for comprehensive price randomization.

**Load Order**: All three mods can be loaded simultaneously with no conflicts.

## 📜 Historical Documents

See [archive/](archive/) for:

- Old status reports
- Testing documentation
- Research notes
- Development logs

These are kept for reference but not actively maintained.

## 🤝 Contributing

1. Read [AP_DEVELOPMENT_GUIDE.md](AP_DEVELOPMENT_GUIDE.md)
2. Check current issues/TODOs
3. Test changes in-game before committing
4. Update documentation with findings

## 📄 License

[To be determined]

Game assets remain property of Square Enix.

- FFVII Rebirth may use a specific Unreal Engine version

## 🔗 Resources

- [Archipelago Documentation](https://archipelago.gg/)
- [UAssetAPI GitHub](https://github.com/atenfyr/UAssetAPI)
- [retoc GitHub](https://github.com/GhostyPool/retoc)
- [UE4SS GitHub](https://github.com/UE4SS-RE/RE-UE4SS)
- [FF7R Modding Community](https://discord.gg/ff7modding)

## 💬 Support

- Check [AP_DEVELOPMENT_GUIDE.md](AP_DEVELOPMENT_GUIDE.md) troubleshooting section
- Review [archive/](archive/) for historical solutions
- Join FF7R modding Discord for community help

---

_Last updated: February 4, 2026_
