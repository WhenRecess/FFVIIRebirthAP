# FFVII Rebirth APWorld Package - Installation & Usage Guide

This directory contains the Archipelago World definition for Final Fantasy VII: Rebirth.

## Overview

The APWorld package defines:
- **Items**: Materia, equipment, key items, consumables, etc.
- **Locations**: Encounters, bosses, chests, quests, mini-games
- **Logic**: Rules for what items are needed to access locations
- **Generation**: Creates randomized multiworld seeds

## Installation

### Step 1: Install Archipelago

1. Download Archipelago from [archipelago.gg](https://archipelago.gg/downloads)
2. Install or extract to a folder (e.g., `C:\Archipelago\`)
3. Launch once to verify installation

### Step 2: Install FFVII Rebirth World

1. Locate your Archipelago installation's `custom_worlds` or `worlds` directory:
   - **Custom install**: `<Archipelago>/custom_worlds/`
   - **Pip install**: `<Python>/Lib/site-packages/worlds/`

2. Copy the `finalfantasy_rebirth` folder:
   ```
   <Archipelago>/custom_worlds/finalfantasy_rebirth/
   ```

3. Verify installation by running:
   ```bash
   python -m worlds.finalfantasy_rebirth
   ```

### Step 3: Prepare Game Data

The world definition needs CSV files containing game data (items, locations, encounters).

#### Option A: Use Provided Templates

Run the item/location scripts to generate template CSVs:

```bash
cd worlds/finalfantasy_rebirth
python items.py     # Generates data/items_template.csv
python locations.py # Generates data/locations_template.csv
```

Edit these CSVs to add your complete item/location lists.

#### Option B: Export from Game Files

Use the `tools/exporter_example.cs` tool to extract data from game PAK files:

1. Extract FFVII Rebirth PAK files using UEAssetExplorer or similar
2. Build and run the exporter tool (see `tools/` directory)
3. Export DataTables (items, territories, encounters, etc.) to CSV
4. Place CSVs in `worlds/finalfantasy_rebirth/data/`:
   - `data/items.csv` - Item definitions
   - `data/locations.csv` - Location definitions
   - `data/territories.csv` - Territory/encounter data (optional)

#### CSV Formats

**items.csv**:
```csv
ItemName,Classification,Count,Description
"Chocobo Lure",progression,1,"Allows catching chocobos"
"Fire Materia",useful,3,"Fire elemental attack"
"Potion",filler,20,"Restores 500 HP"
```

**locations.csv**:
```csv
LocationName,Region,Type,Description
"Boss: Midgardsormr",Grasslands,boss,"Defeat Midgardsormr"
"Grasslands: Encounter 1",Grasslands,encounter,"Random encounter"
```

**territories.csv** (from game DataTable):
```csv
UniqueIndex,TerritoryName,MobTemplateList,WaveMobTemplateList
100,"Grasslands_01","[1,2,3]","[4,5]"
101,"Junon_Harbor","[10,11]","[]"
```

## Creating a Multiworld Seed

### Step 1: Create a YAML Configuration

Create a YAML file (e.g., `ffvii_rebirth.yaml`) in your Archipelago Players directory:

```yaml
name: YourSlotName
game: Final Fantasy VII: Rebirth

# TODO: Add world-specific options when implemented
# enemy_randomization: 50  # percentage
# starting_materia: 3      # number of random materia
# death_link: false
```

### Step 2: Generate the Seed

Run Archipelago's generator:

```bash
python ArchipelagoGenerate.py
```

Or use the GUI launcher and select your YAML file.

This will create:
- `AP_<seed_name>.archipelago` - Multiworld data file
- `AP_<player>_<seed>.json` - FFVII Rebirth-specific data (in output directory)

### Step 3: Host or Join a Multiworld

1. **Hosting**: Use ArchipelagoServer to host the generated `.archipelago` file
2. **Joining**: Use the in-game mod to connect (see `ue4ss_mod/README_MOD.md`)

## World Options

⚠️ **TODO**: World options are not yet implemented in the scaffold.

Planned options:
- `enemy_randomization`: Randomize enemy encounters (0-100%)
- `boss_randomization`: Randomize boss encounters
- `starting_inventory`: Items to start with
- `death_link`: Enable DeathLink
- `materia_randomization`: Randomize materia locations
- `equipment_randomization`: Randomize equipment locations
- `quest_randomization`: Randomize quest availability

## Development

### Adding Items

1. Export item data from game files (see `tools/exporter_example.cs`)
2. Add to `data/items.csv` or edit `items.py`
3. Classify items:
   - `progression`: Required to complete the game
   - `useful`: Helpful but not required
   - `filler`: Common items, gil, consumables
   - `trap`: Negative effects (optional)

### Adding Locations

1. Export territory/encounter data from game files
2. Add to `data/locations.csv` or edit `locations.py`
3. Organize by region/area
4. Include metadata (territory index, encounter index, etc.)

### Implementing Logic

Edit `__init__.py` and add access rules in `set_rules()`:

```python
from worlds.generic.Rules import set_rule

# Example: Require Chocobo Lure to access Grasslands encounters
set_rule(
    self.multiworld.get_location("Grasslands: Encounter 5", self.player),
    lambda state: state.has("Chocobo Lure", self.player)
)
```

### Testing

Create test cases in `test/` directory using Archipelago's test framework:

```python
from test.bases import WorldTestBase

class FFVIIRebirthTestBase(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"

class TestAccess(FFVIIRebirthTestBase):
    def test_chocobo_access(self):
        """Test that Chocobo Lure is required for certain locations"""
        locations = ["Grasslands: Encounter 5"]
        items = [["Chocobo Lure"]]
        self.assertAccessDependency(locations, items)
```

Run tests:
```bash
python -m pytest test/
```

## Troubleshooting

### World doesn't appear in generator
- Verify `archipelago.json` exists and is valid
- Check that `__init__.py` defines `FFVIIRebirthWorld` class
- Ensure `game` attribute matches the JSON file

### Generation fails
- Check that CSV files are valid UTF-8
- Verify item/location counts are reasonable
- Check for duplicate item/location IDs
- Review Archipelago logs for errors

### Items/locations not loading
- Verify CSV files are in `data/` directory
- Check CSV format matches expected structure
- Ensure file paths are correct (case-sensitive on Linux)

## Resources

- [Archipelago Setup Guide](https://archipelago.gg/tutorial/Archipelago/setup/en)
- [World Development Guide](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md)
- [Logic Documentation](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md#access-rules)
- [UAssetAPI Documentation](https://github.com/atenfyr/UAssetAPI)

## Contributing

When adding features to the world:

1. Keep CSV formats consistent and documented
2. Add comprehensive logic rules
3. Write tests for new functionality
4. Update this README with new options/features
5. Follow Archipelago's world API conventions

## License

TBD - To be determined by repository owner
