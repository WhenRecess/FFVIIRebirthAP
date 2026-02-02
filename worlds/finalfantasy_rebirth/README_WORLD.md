# Final Fantasy VII: Rebirth - Archipelago World Package

This directory contains the Archipelago World implementation for **Final Fantasy VII: Rebirth**.

## Installation

### Option 1: Copy to Archipelago Installation

Copy this entire folder to your Archipelago `worlds/` directory:

```bash
# Windows example
copy /E worlds\finalfantasy_rebirth "C:\ProgramData\Archipelago\worlds\finalfantasy_rebirth"

# Linux/macOS example
cp -r worlds/finalfantasy_rebirth ~/Archipelago/worlds/
```

### Option 2: Create .apworld Package

Package this world as a `.apworld` file (which is just a ZIP file):

```bash
# From the repository root
cd worlds
zip -r finalfantasy_rebirth.apworld finalfantasy_rebirth/

# Then place the .apworld file in Archipelago's custom_worlds/ or lib/worlds/ directory
```

## Data Files

This World package requires CSV files containing item and location data extracted from the game. Place these files in the `data/` subdirectory:

```
worlds/finalfantasy_rebirth/
├── data/
│   ├── items.csv        # Item name-to-ID mappings
│   └── locations.csv    # Location name-to-ID mappings
├── __init__.py
├── items.py
├── locations.py
└── ...
```

**Note:** Git does not track empty directories, so you may need to create the `data/` folder manually:

```bash
mkdir worlds/finalfantasy_rebirth/data
```

### CSV Format

#### items.csv

```csv
ItemName,ItemID
Buster Sword,16707584
Bronze Bangle,16711936
Fire Materia,16715008
Potion,16719104
```

- `ItemName`: In-game item name (string)
- `ItemID`: Unique item ID (integer, decimal or hex with `0x` prefix)

#### locations.csv

**Standard format:**

```csv
LocationName,LocationID,Region
Boss: Scorpion Sentinel,16707584,Midgar
Chest: Sector 7 Slums,16711936,Midgar
Materia: Kalm,16715008,Kalm
```

- `LocationName`: In-game location name (string)
- `LocationID`: Unique location ID (integer, decimal or hex)
- `Region`: (Optional) Region name for logical grouping

**Territory format (alternative):**

```csv
RowName,UniqueIndex,MobTemplateList,MobLevels
Territory_Midgar_01,1,Scorpion;Guard,5;7
Territory_Kalm_01,2,Flan,10
```

- `RowName`: Territory identifier from game data
- `UniqueIndex`: Unique ID for this territory
- `MobTemplateList`: Semicolon-separated list of enemy names
- `MobLevels`: Semicolon-separated list of enemy levels

The territory format is automatically converted to location names like "Midgar 01: Defeat Scorpion".

### Extracting Data from Game Files

Use the C# exporter tool in `tools/exporter_example.cs` to extract DataTable rows from `.uasset` files:

```bash
cd tools
dotnet run -- "C:\Path\To\Game\Content\DataTables\ItemTable.uasset"
```

This will generate CSV files that can be copied to the `data/` directory.

## Generating Seeds

Once installed, you can generate Archipelago seeds that include Final Fantasy VII: Rebirth.

1. **Create a YAML configuration file** (e.g., `ff7r_player.yaml`):

```yaml
name: YourPlayerName

game: Final Fantasy VII: Rebirth

Final Fantasy VII: Rebirth:
  progression_balancing: 50
  accessibility: items
  
  # TODO: Add game-specific options here
  # starting_materia: fire
  # randomize_bosses: true
```

2. **Generate the seed:**

```bash
python ArchipelagoGenerate.py --player_files_path . --weights ff7r_player.yaml
```

This creates a `.archipelago` file in the `output/` directory.

3. **Host or join a multiworld:**
   - Use `ArchipelagoServer.py` to host a server
   - Use the in-game mod to connect (see `ue4ss_mod/README_MOD.md`)

## Development

### TODO: Implement Game Logic

The current implementation is a **scaffold**. The following must be implemented:

1. **Populate `item_table` and `location_table`** in `items.py` and `locations.py` with real game data.

2. **Define regions** in `__init__.py` (`create_regions()` method):
   - Create regions for major game areas (Midgar, Kalm, Junon, etc.)
   - Connect regions with entrances
   - Assign locations to regions

3. **Create items** in `__init__.py` (`create_items()` method):
   - Add all items to the multiworld item pool
   - Classify items as progression, useful, filler, or trap

4. **Set access rules** in `__init__.py` (`set_rules()` method):
   - Define which items are required to access locations
   - Set the victory condition

5. **Generate output** in `__init__.py` (`generate_output()` method):
   - Create output files for the game client (e.g., JSON with item placements)

6. **Add game options** in `__init__.py`:
   - Define player-configurable options (starting items, difficulty, etc.)

### Loading CSV Data Dynamically

The `items.py` and `locations.py` modules provide CSV loader functions (`load_items_from_csv`, `load_locations_from_csv`). To use them:

```python
import os
from .items import load_items_from_csv, item_table, ItemData
from .locations import load_locations_from_csv, location_table, LocationData

# In __init__.py or at module level
data_dir = os.path.join(os.path.dirname(__file__), "data")

# Load items
items_csv = os.path.join(data_dir, "items.csv")
if os.path.exists(items_csv):
    csv_items = load_items_from_csv(items_csv)
    for name, item_id in csv_items.items():
        item_table[name] = ItemData(item_id, ItemClassification.filler)

# Load locations
locations_csv = os.path.join(data_dir, "locations.csv")
if os.path.exists(locations_csv):
    csv_locations = load_locations_from_csv(locations_csv)
    for name, location_id in csv_locations.items():
        location_table[name] = LocationData(location_id, "Main Game")
```

## Testing

See `test/README.md` for information on writing and running tests for this World.

## Resources

- [Archipelago World Development Guide](https://archipelago.gg/tutorial/Archipelago/world_api/)
- [Archipelago Discord](https://discord.gg/archipelago)
- [Final Fantasy VII: Rebirth Modding Community](https://www.nexusmods.com/finalfantasy7rebirth)

## License

This World package is provided as-is for community use. Respect the intellectual property of Square Enix and the Archipelago project.
