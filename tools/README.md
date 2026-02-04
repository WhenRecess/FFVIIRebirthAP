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
python smart_price_randomizer.py \
    "C:\...\UnpackFresh\End\Content\DataObject\Resident\ShopItem.uexp" \
    --auto-deploy 12345 100 5000
```

This will randomize shop prices, repack, and deploy to your game automatically!

## 📁 Directory Structure

```
tools/
├── bin/                              # External binaries (retoc, UAssetGUI)
├── data/                             # Extracted game data (JSON files)
├── archive/                          # Historical documentation
├── UAssetAPI_Source/                 # UAssetAPI library source
├── UAssetExporter/                   # C# export tool
├── config.ini                        # User configuration ⚙️
├── smart_price_randomizer.py        # Primary randomizer tool ⭐
├── uassetgui_price_randomizer.py    # Alternative approach (experimental)
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

### uassetgui_price_randomizer.py

**JSON-based alternative approach**

**Status**: Experimental (has serialization bugs)  
**Purpose**: Reference implementation, useful for debugging  
**Note**: Binary approach (above) is recommended

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

- Shop price randomization (working, tested)
- Item ID extraction (502 items)
- File patching workflow (verified in-game)
- Repository self-containment

🟡 **In Progress**:

- Equipment randomization
- Location mapping
- Reward system consolidation

❌ **Not Started**:

- AP world module integration
- UE4SS client connection
- Full multiworld support

## 🚦 Next Steps

1. Apply smart algorithm to Equipment.uasset
2. Complete location mapping (all treasures, drops, rewards)
3. Implement AP world module
4. Create UE4SS runtime client
5. Full integration testing

See [AP_DEVELOPMENT_GUIDE.md](AP_DEVELOPMENT_GUIDE.md) for detailed roadmap.

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

_Last updated: February 3, 2026_
