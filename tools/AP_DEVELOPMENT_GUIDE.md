# FF7 Rebirth Archipelago Development Guide

**Status**: Active Development  
**Last Updated**: February 3, 2026  
**Current Phase**: Single-World Randomizer (Pre-randomization)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Current Status](#current-status)
3. [Architecture](#architecture)
4. [Working Tools](#working-tools)
5. [Development Workflow](#development-workflow)
6. [Next Steps](#next-steps)
7. [Technical Reference](#technical-reference)

---

## Project Overview

### Goal

Create a **single-world randomizer** for Final Fantasy VII: Rebirth using Archipelago for seed generation and logic. Multiworld support is a future goal once runtime item granting is solved.

### Approach

**Pre-randomization system**: Modify game files before launch using seed-based deterministic randomization, deployed via UE4 pak mods. All item placements are baked into the game files.

**Why pre-randomization (and why single-world first)?**

- FF7R uses Unreal Engine with encrypted assets
- **No game API functions found** for granting items at runtime
- Memory modification works but is too fragile for distribution
- File patching is deterministic, verifiable, and stable
- Can leverage existing UE4 modding tools (retoc, UAssetGUI)
- Delivers a playable randomizer without solving the item grant problem

### Key Components

1. **Randomizer Tools** (Python) - Modify game asset files
2. **UE4SS Mod** (Lua/C++) - Runtime client for item gives
3. **AP World** (Python) - Archipelago integration
4. **Game File Patching** - Deploy modified paks to game

---

## Current Status

### ✅ Completed (Working & Tested)

#### Shop Price Randomization

- **Tool**: `smart_price_randomizer.py`
- **Method**: Intelligent binary pattern detection
- **Detection**: 252-455 price arrays (depending on seed)
- **Automation**: Full --auto-deploy pipeline
  1. Randomize prices in .uexp file
  2. Replace in unpacked directory
  3. Repack with retoc (UE4_26 Zen format)
  4. Deploy to game mods folder
- **Testing**: Verified in-game with multiple seeds
- **Performance**: ~535 prices modified in seconds

#### Item ID Extraction

- **Completed**: 502 item IDs extracted and verified
- **Method**: Cheat Engine scanning + binary analysis
- **Data**: `data/_ce_all_real_ids.json`
- **Coverage**: All consumables, equipment, key items, materials

#### File Patching Workflow

- **Verified**: Equipment.uasset modifications work in-game
- **Verified**: ShopItem.uasset modifications work in-game
- **Method**: Modify .uexp → repack → deploy to ~mods folder
- **Format**: UE4_26 Zen pak format via retoc

#### Repository Self-Containment

- **External tools internalized**: retoc.exe, UAssetGUI.exe in `bin/`
- **Configuration system**: `config.ini` for user paths
- **No external dependencies**: Fully portable

### 🟡 In Progress

#### Equipment Randomization

- **Status**: Algorithm proven (same approach as shop prices)
- **Expected**: 100-300 stat arrays in Equipment.uasset
- **Next**: Apply smart detection to equipment stats
- **Plan**: See EQUIPMENT_RANDOMIZATION_PLAN.md

#### Location Mapping

- **Partial**: Some treasure chests mapped (Kalm, Midgar)
- **Need**: Complete treasure, enemy drops, quest rewards
- **Format**: Location ID → Item ID mappings

#### Reward System Understanding

- **Status**: Multiple parsers created, structure partially understood
- **Need**: Consolidate parser, map all reward types

### ❌ Not Started

- AP world module integration
- UE4SS runtime client connection
- Logic system (item requirements, progression)
- Save file detection/validation
- Multiworld synchronization

---

## Architecture

### Two-Phase System

The FF7R Archipelago uses a **hybrid approach** combining:

1. **Pre-Randomization (File Patching)** - Modify game files BEFORE launch
2. **Runtime Hooks (UE4SS Mod)** - Handle dynamic events DURING gameplay

This hybrid is necessary because:

- FF7R uses Unreal Engine with complex encrypted assets
- Some things (shop prices, equipment stats, loot tables) can be pre-baked
- Other things (item gives, location checks, AP sync) MUST be runtime

### What Pre-Randomization Handles

| Feature             | Tool                      | When          |
| ------------------- | ------------------------- | ------------- |
| Shop prices         | smart_price_randomizer.py | Before launch |
| Equipment stats     | (planned)                 | Before launch |
| Loot table contents | (planned)                 | Before launch |
| Enemy drops         | (planned)                 | Before launch |
| Chest contents      | (planned)                 | Before launch |

**Why pre-patching works for these:**

- Values are stored in DataTable assets (.uasset/.uexp)
- Can be modified deterministically with a seed
- Changes persist across saves
- No runtime overhead

### What UE4SS Runtime Would Handle (Future Multiworld)

| Feature                 | Component       | Status                                |
| ----------------------- | --------------- | ------------------------------------- |
| AP server connection    | APClient.lua    | ✅ Scaffolded                         |
| Sending location checks | GameState.lua   | 🔄 Partial (needs game hooks)         |
| Receiving items from AP | ItemHandler.lua | ❌ **BLOCKED** - No item grant API    |
| DeathLink               | main.lua        | ❌ Blocked by runtime mod             |
| Multiworld sync         | APClient.lua    | ❌ Blocked by item grants             |

**Why multiworld is blocked:**

- **No game API functions** for adding items to player inventory
- Memory modification works (Cheat Engine) but UE4SS Lua can't do signature scanning
- External trainer approach is too fragile (breaks with game updates)
- Single-world avoids this by pre-placing all items in game files

### System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BEFORE GAME LAUNCH                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [AP World Module] → generates seed + settings                          │
│          ↓                                                              │
│  [Pre-Randomizer Tools]                                                 │
│      ├── smart_price_randomizer.py → ShopItem.uexp                      │
│      ├── (planned) equipment_randomizer.py → Equipment.uasset           │
│      └── (planned) loot_randomizer.py → Reward tables                   │
│          ↓                                                              │
│  [retoc repack] → .pak/.ucas/.utoc                                      │
│          ↓                                                              │
│  [Deploy to ~mods/] ← Game will auto-load these                         │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                         DURING GAMEPLAY                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  [Game Launches] → loads pre-randomized assets                          │
│          ↓                                                              │
│  [UE4SS Mod] ← ue4ss_mod_lua/                                           │
│      ├── APClient.lua     → WebSocket connection to AP server           │
│      ├── GameState.lua    → Monitors player actions (chests, kills)     │
│      ├── ItemHandler.lua  → Gives items when received from AP           │
│      └── main.lua         → Coordinates everything                      │
│          ↓                    ↑                                         │
│  [Archipelago Server] ←───────┘                                         │
│      ├── Receives: Location checks from this player                     │
│      └── Sends: Items from other players                                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **AP generates seed** → Includes FF7R-specific settings
2. **Pre-randomizer runs** → Modifies game files deterministically
3. **Player starts game** → Loads modded pak files
4. **UE4SS tracks progress** → Sends location checks to AP
5. **AP gives items** → UE4SS injects via game functions
6. **Player continues** → Synced with multiworld

---

## Working Tools

### Primary Tools (Keep These!)

#### `smart_price_randomizer.py` ⭐

**Purpose**: Automated shop price randomization with deployment

**Usage**:

```bash
cd tools
python smart_price_randomizer.py <file.uexp> --auto-deploy <seed> <min> <max>

# Example: Randomize 100-9000 gil with seed 54321
python smart_price_randomizer.py \
    "C:\...\UnpackFresh\End\Content\DataObject\Resident\ShopItem.uexp" \
    --auto-deploy 54321 100 9000
```

**What it does**:

1. Scans binary for price array patterns: `[4-byte count][count × 4-byte prices]`
2. Validates arrays (reasonable size, price range, non-zero percentage)
3. Randomizes prices with seed
4. Replaces file in unpacked directory
5. Repacks with retoc to Zen format
6. Deploys .pak/.ucas/.utoc to game ~mods folder
7. Cleans up temporary files

**Output**: Ready-to-use pak mod in game directory

#### `uassetgui_price_randomizer.py`

**Purpose**: Alternative JSON-based approach (experimental)

**Status**: Has known bugs (JSON serialization issue)
**Usage**: Reference only, binary approach preferred
**Note**: Useful for manual debugging with UAssetGUI

#### `config.ini`

**Purpose**: User configuration

**Required settings**:

```ini
[Paths]
game_dir = G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH
unpack_dir = C:\Users\username\Documents\UnpackFresh\End
```

**Edit this** to match your system paths.

### Data Extraction Tools

#### `extract_all_ce_ids.py`

**Purpose**: Extract all item IDs from Item.uexp
**Output**: `data/_ce_all_real_ids.json` (502 items)
**Usage**: Rerun if game updates

#### `build_item_name_map.py`

**Purpose**: Generate item name → ID mappings
**Output**: Various mapping files in `data/`
**Usage**: For AP item definitions

#### `generate_item_mappings.py`

**Purpose**: Create comprehensive item database
**Output**: `data/_complete_item_mappings.json`

#### `generate_location_mappings.py`

**Purpose**: Map game locations to AP location IDs
**Status**: In development

### Supporting Tools

#### `filter_ue4ss_functions.py`

**Purpose**: Filter UE4SS function dumps for useful game functions
**Usage**: When researching game internals

#### `reward_smart_parser.py`

**Purpose**: Parse reward system data
**Status**: Working parser (others consolidated/removed)

#### `exporter_example.cs` / `UAssetExporter/`

**Purpose**: C# UAssetAPI-based exporter
**Usage**: Export .uasset to JSON for analysis

---

## Development Workflow

### Prerequisites

1. **Game Installation**: FF7 Rebirth on PC (Steam/Epic)
2. **Python 3.10+**: With standard library
3. **Repository Tools**: All included in `tools/bin/`
   - retoc.exe (pak repacker)
   - UAssetGUI.exe (asset viewer)

### Setup Steps

1. **Clone Repository**

   ```bash
   git clone https://github.com/your-org/FFVIIRebirthAP
   cd FFVIIRebirthAP
   ```

2. **Configure Paths**

   ```bash
   cd tools
   # Edit config.ini with your game directory and unpack location
   notepad config.ini
   ```

3. **Unpack Game Files** (One-time)

   ```bash
   # Use QuickBMS or similar to unpack End-Windows.pak
   # Extract to: C:\Users\YourName\Documents\UnpackFresh\End\
   ```

4. **Test Randomizer**

   ```bash
   python smart_price_randomizer.py \
       "C:\...\UnpackFresh\End\Content\DataObject\Resident\ShopItem.uexp" \
       --auto-deploy 12345 100 5000
   ```

5. **Launch Game**
   - Mod will be in: `{GameDir}\End\Content\Paks\~mods\`
   - Game auto-loads all .pak files in ~mods
   - Check shops to verify randomized prices

### Development Cycle

For adding new randomization features:

1. **Research**: Use UAssetGUI to understand asset structure
2. **Analyze**: Examine binary patterns (hex editor, Python)
3. **Detect**: Create intelligent pattern detection algorithm
4. **Randomize**: Implement seed-based modifications
5. **Test**: Deploy and verify in-game
6. **Integrate**: Add to automation pipeline

### Git Workflow

```bash
# Before making changes
git status
git add .
git commit -m "Snapshot before cleanup/changes"

# After testing
git add <modified_files>
git commit -m "Descriptive message"
git push
```

---

## Next Steps

### Immediate (Next 1-2 weeks)

1. **Equipment Randomization**

   - Apply smart algorithm to Equipment.uasset
   - Detect stat arrays (Attack, Defense, Magic, etc.)
   - Create `smart_equipment_randomizer.py`
   - Test in-game

2. **Unified Randomizer**
   - Combine shop + equipment into single tool
   - Accept AP seed as input
   - Generate all mods in one run

### Short Term (Next month)

3. **Complete Location Mapping**

   - Map all treasure chests
   - Map all enemy drops
   - Map all quest rewards
   - Map all shop acquisitions
   - Create `locations.py` for AP world

4. **UE4SS Mod Development**

   - Create item-give function hooks
   - Implement location check detection
   - Add AP client communication

5. **AP World Module**
   - Implement `worlds/finalfantasy_rebirth/`
   - Define items.py (502+ items)
   - Define locations.py (hundreds of checks)
   - Implement rules.py (progression logic)

### Medium Term (Next 2-3 months)

6. **Logic System**

   - Define progression items (Key Items, Story Flags)
   - Implement region access rules
   - Add equipment requirements (if applicable)

7. **Save Detection**

   - Hook save game creation
   - Validate AP seed matches save
   - Warn on mismatch

8. **Testing & Balancing**
   - Playtest full runs
   - Balance price ranges
   - Tune stat randomization
   - Fix progression issues

### Long Term

9. **Advanced Features**

   - Multiple randomization options
   - Difficulty modes
   - Optional cosmetic randomization
   - Quality of life improvements

10. **Community Release**
    - Documentation for end users
    - Installation guide
    - Troubleshooting guide
    - Video tutorials

---

## Technical Reference

### File Format: ShopItem.uexp

**Structure**:

```
UE4 Asset Header
├── Export Table
├── Import Table
└── Export Data
    └── DataTable Rows
        └── OverridePrice_Array
            ├── [4-byte count]
            └── [count × 4-byte int32 prices]
```

**Price Array Pattern**:

```
Offset: Variable
Pattern: [Count: 4 bytes] [Price1: 4 bytes] [Price2: 4 bytes] ...
Example: 05 00 00 00 | 64 00 00 00 | C8 00 00 00 | ...
         ↑ Count=5    ↑ Price1=100  ↑ Price2=200
```

**Detection Heuristics**:

- Count must be 0-100 (reasonable array size)
- Following values must be in price range (1-9999)
- At least 50% of values must be non-zero
- Entire array must fit within file bounds

### File Format: Equipment.uasset

**Target Properties**:

- Attack, MagicAttack, Defense, MagicDefense
- HP, MP, Luck, Speed
- Element affinities
- Materia slots (special handling)

**Approach**: Same pattern detection as ShopItem

### UE4 Pak Format

**Zen Format (UE4.26+)**:

- `.pak` - Metadata (small, ~347 bytes)
- `.ucas` - Compressed asset data (~49 MB)
- `.utoc` - Table of contents (~226 KB)

**Conversion**: Use retoc.exe

```bash
retoc.exe to-zen --version UE4_26 <input_dir> <output_name>
```

### Deployment

**Game Mod Folder**:

```
{GameDir}\End\Content\Paks\~mods\
├── RandomizedShop_Seed12345.pak
├── RandomizedShop_Seed12345.ucas
└── RandomizedShop_Seed12345.utoc
```

**Load Order**: Alphabetical, mods override base files

**Naming**: Prefix with tilde `~` ensures late load

---

## Research Notes

### Discoveries

1. **Binary Randomization Works**: Direct modification of .uexp files is stable
2. **UAssetGUI JSON Export Broken**: Has serialization bugs, not reliable
3. **Intelligent Detection Critical**: Naive pattern matching produces 6,000+ false positives
4. **retoc is Essential**: Only working tool for UE4_26 Zen repacking
5. **~mods folder**: Game auto-loads, no manual patching needed

### Lessons Learned

- Start with binary analysis, not high-level tools
- Test in-game early and often
- Keep historical documentation (archive/)
- Automation is key for reproducibility
- Seed-based randomization enables AP integration

### Key Files Modified

**For Shop Randomization**:

- `End/Content/DataObject/Resident/ShopItem.uexp` (124,724 bytes)

**For Equipment Randomization** (planned):

- `End/Content/DataObject/Resident/Equipment.uasset` (149,508 bytes)

**For Rewards** (researching):

- Various Reward/Treasure tables in DataObject/

---

## Troubleshooting

### Randomizer doesn't find any arrays

- Check file path is correct
- Ensure using .uexp file (not .uasset)
- Verify file is not corrupted
- Try different min/max price ranges

### Mod doesn't load in game

- Check ~mods folder path correct
- Ensure all three files present (.pak, .ucas, .utoc)
- Verify file permissions (not read-only)
- Check game version matches (UE4_26)

### Prices not randomized in-game

- Verify you deployed to correct game directory
- Check seed generates non-zero prices
- Ensure game loaded mod (check file timestamps)
- Try deleting cache: `{GameDir}\End\Saved\`

### retoc fails to repack

- Ensure input directory structure correct
- Check no files are locked/in-use
- Verify retoc.exe is in `tools/bin/`
- Check disk space available

---

## Contributing

### Coding Standards

- **Python**: PEP 8 style
- **Comments**: Explain WHY, not WHAT
- **Functions**: Single responsibility
- **Error handling**: Always include context

### Testing

- Test with multiple seeds
- Verify in-game before committing
- Document any edge cases
- Update documentation with findings

### Pull Requests

- Descriptive commit messages
- Reference issue numbers
- Include test results
- Update relevant docs

---

## Resources

### External Tools

- **retoc**: https://github.com/GhostyPool/retoc
- **UAssetGUI**: https://github.com/atenfyr/UAssetGUI
- **UE4SS**: https://github.com/UE4SS-RE/RE-UE4SS
- **Archipelago**: https://archipelago.gg/

### Documentation

- **This guide**: Primary reference
- **BINARY_STRUCTURE_BREAKTHROUGH.md**: Technical deep-dive
- **EQUIPMENT_RANDOMIZATION_PLAN.md**: Next phase planning
- **FILE_AUDIT.md**: Repository cleanup decisions
- **archive/**: Historical documents

### Community

- **Archipelago Discord**: #future-games channel
- **FF7R Modding Discord**: General modding help

---

## License

This project is licensed under [LICENSE TYPE] - see LICENSE file for details.

Game assets remain property of Square Enix.

---

## Credits

- **FF7R Modding Community**: For UE4 research and tools
- **Archipelago Team**: For the multiworld framework
- **UE4SS Team**: For the scripting system
- **retoc Developer**: For the pak conversion tool

---

_This is a living document. Update as the project evolves._
