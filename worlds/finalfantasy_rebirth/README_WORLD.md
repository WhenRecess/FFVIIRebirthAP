# Final Fantasy VII: Rebirth APWorld - Installation and Usage Guide

This directory contains the Archipelago World package for Final Fantasy VII: Rebirth.

## What is an APWorld?

An APWorld is a Python package that defines how a game integrates with Archipelago. It specifies:
- What items exist in the game
- What locations (checks) exist in the game
- How items and locations are connected (progression logic)
- How to generate randomized seeds

## Installation

### 1. Install Archipelago

Download and install Archipelago from https://github.com/ArchipelagoMW/Archipelago/releases

### 2. Install the World Package

Copy the entire `finalfantasy_rebirth` directory to your Archipelago installation:

**Windows:**
```
C:\ProgramData\Archipelago\custom_worlds\finalfantasy_rebirth\
```

**Linux/Mac:**
```
~/Library/Application Support/Archipelago/custom_worlds/finalfantasy_rebirth/
```

Your directory structure should look like:
```
custom_worlds/
└── finalfantasy_rebirth/
    ├── __init__.py
    ├── items.py
    ├── locations.py
    ├── archipelago.json
    ├── requirements.txt
    ├── data/
    │   ├── items.csv (you need to create this)
    │   └── territories.csv (you need to create this)
    └── test/
```

### 3. Verify Installation

Launch the Archipelago Launcher and check that "Final Fantasy VII: Rebirth" appears in the game list.

## Preparing Game Data

Before you can generate seeds, you need to extract data from the game assets.

### Required CSV Files

Create these CSV files in the `data/` directory:

#### 1. `items.csv`

Format:
```csv
Name,ID,Classification,Count
Potion,1,filler,10
Phoenix Down,2,useful,5
Mythril Saber,3,progression,1
Summon Materia: Ifrit,100,progression,1
```

Classifications:
- `progression`: Required to complete the game
- `useful`: Helpful but not required
- `filler`: Common items
- `trap`: Negative effects

#### 2. `territories.csv`

Format:
```csv
TerritoryName,UniqueIndex,MobTemplateList,Region
Grasslands_Territory_01,0,MobTemplate_Goblin,Grasslands
Grasslands_Territory_02,1,MobTemplate_Cactuar,Grasslands
Junon_Boss_Arena,100,MobTemplate_BossTurks,Junon
```

### Extracting Data with UAssetGUI/UAssetAPI

Use the example tool in `tools/exporter_example.cs` to extract data from game assets:

1. Locate the game's asset files (`.uasset`, `.pak`)
2. Use UAssetAPI or UAssetGUI to open DataTable assets
3. Export relevant tables to CSV format:
   - Item tables (weapons, materia, consumables, key items)
   - Territory/encounter tables
   - Enemy template tables

See `tools/exporter_example.cs` for a code example of automated extraction.

## Generating a Seed

### 1. Create a YAML Configuration

Create a file named `FFVIIRebirth_YourName.yaml`:

```yaml
name: YourName
game: Final Fantasy VII: Rebirth
requires:
  version: 0.4.5

Final Fantasy VII: Rebirth:
  progression_balancing: 50
  accessibility: items
  
  # TODO: Add game-specific options here
  # death_link: true
  # enemy_randomization: true
```

### 2. Generate the Seed

Run ArchipelagoGenerate:
```bash
# Navigate to your Archipelago directory
cd /path/to/Archipelago

# Generate with your YAML
python ArchipelagoGenerate.py FFVIIRebirth_YourName.yaml
```

Or use the GUI launcher and click "Generate".

### 3. Output Files

The generator will create files in the `output/` directory:
- `AP_XXXXX.zip`: Distribution zip for all players
- `AP_XXXXX_P1_YourName.json`: Player-specific data file (if `generate_output` is implemented)

## Configuration Options

TODO: Document game-specific options once implemented in `__init__.py`

Example options that could be added:
- `death_link`: Enable/disable DeathLink
- `enemy_randomization`: Randomize enemy templates
- `starting_materia`: Choose starting materia
- `difficulty`: Adjust item balance
- `goal`: Set victory condition (defeat Sephiroth, collect X items, etc.)

## Using with the Mod

1. Generate a seed with this APWorld
2. Host or connect to an Archipelago server
3. Start the game with the UE4SS mod installed
4. Use `/connect <server> <slot>` in the game console
5. Play the game - items will be randomized and synced with other players!

## Development

### Adding Items

1. Extract item data from game assets
2. Add to `data/items.csv`
3. Update `items.py` with item classifications
4. Implement item giving logic in the mod (`GameData::ReceiveItem`)

### Adding Locations

1. Extract territory/encounter data from game assets
2. Add to `data/territories.csv`
3. Update `locations.py` with location definitions
4. Implement location checking in the mod (`GameData::CheckEncounterSpots`)

### Adding Progression Logic

Edit `__init__.py` and implement the `set_rules()` method:

```python
def set_rules(self):
    from worlds.generic.Rules import set_rule
    
    # Example: Can't reach Junon without defeating Grasslands boss
    set_rule(
        self.multiworld.get_entrance("Grasslands -> Junon", self.player),
        lambda state: state.has("Grasslands Boss Key", self.player)
    )
```

### Testing

Add tests in the `test/` directory using Archipelago's `WorldTestBase`:

```python
from test.bases import WorldTestBase

class FFVIIRebirthTestBase(WorldTestBase):
    game = "Final Fantasy VII: Rebirth"

class TestBasicGeneration(FFVIIRebirthTestBase):
    def test_game_completes(self):
        self.assertBeatable(True)
```

Run tests:
```bash
python -m pytest worlds/finalfantasy_rebirth/test/
```

## Troubleshooting

### "Game not found" error
- Verify the `finalfantasy_rebirth` directory is in `custom_worlds/`
- Check that `__init__.py` and `archipelago.json` exist
- Restart the Archipelago launcher

### Generation fails
- Check that CSV files exist in `data/` directory
- Verify CSV format matches expected columns
- Check for error messages in the generator output

### Items not spawning in game
- Verify the mod is connected to the server
- Check console output for errors
- Ensure `ReceiveItem` is implemented in the mod

## Resources

- [Archipelago World Development Guide](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md)
- [UAssetAPI Documentation](https://github.com/atenfyr/UAssetAPI)
- [UE4SS Documentation](https://docs.ue4ss.com/)

## Contributing

Contributions are welcome! Priority areas:
- Extracting comprehensive item/location data
- Implementing progression logic
- Adding game-specific options
- Testing and balancing

## Version History

- 0.1.0: Initial scaffold release
  - Basic World structure
  - CSV loading placeholders
  - Example item/location definitions
