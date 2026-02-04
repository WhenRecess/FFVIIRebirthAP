# Final Fantasy VII: Rebirth - Code Architecture

## Overview

This document describes the code organization for the FFVII Rebirth Archipelago world.
The codebase follows a modular architecture with clear separation of concerns.

## Directory Structure

```
worlds/finalfantasy_rebirth/
│
├── __init__.py              # Main world class (FFVIIRebirthWorld)
│
├── core/                    # Public interface modules
│   ├── __init__.py          # Package exports
│   ├── items.py             # Item facade API
│   ├── locations.py         # Location facade API
│   ├── options.py           # Randomizer options
│   └── regions.py           # Region builder
│
├── data/                    # Static data definitions
│   ├── __init__.py          # Package exports
│   ├── game_loader.py       # Game data manager
│   ├── item_tables.py       # Item definitions by category
│   ├── location_tables.py   # Location definitions by type
│   ├── region_tables.py     # Region definitions
│   └── exports/             # Raw game data (JSON/text)
│       ├── _consolidated_data.json
│       ├── Colosseum.json
│       ├── EnemyTerritory.json
│       ├── item_names.json
│       └── ... (other exports)
│
├── randomization/           # Randomization logic
│   ├── __init__.py          # Package exports
│   ├── item_pool.py         # Item pool builder
│   ├── location_generator.py # Location generator
│   └── rules.py             # Access rules factory
│
├── hooks/                   # Lua mod interface
│   ├── __init__.py          # Package exports
│   ├── events.py            # Game event definitions
│   ├── item_grants.py       # Item grant mappings
│   ├── location_checks.py   # Location check triggers
│   ├── game_state.py        # State queries and commands
│   └── protocol.py          # Message format for mod communication
│
├── test/                    # Unit tests
│   └── README.md
│
├── ARCHITECTURE.md          # This file
├── README_WORLD.md          # Setup instructions
├── archipelago.json         # World metadata
└── requirements.txt         # Python dependencies
```

## Module Descriptions

### Main Entry Point

| Module        | Purpose                                                                               |
| ------------- | ------------------------------------------------------------------------------------- |
| `__init__.py` | Main entry point. Defines `FFVIIRebirthWorld` class that integrates with Archipelago. |

### Core Package (`core/`)

Public interface modules providing clean APIs for the main world class.

| Module         | Purpose                                                                              |
| -------------- | ------------------------------------------------------------------------------------ |
| `items.py`     | Public API for item data. Thin wrapper over randomization/item_pool.py.              |
| `locations.py` | Public API for location data. Thin wrapper over randomization/location_generator.py. |
| `options.py`   | All configurable options (chapter progression, content toggles, difficulty, etc.).   |
| `regions.py`   | `RegionBuilder` class for creating the Archipelago world graph.                      |

### Data Package (`data/`)

Contains all static data definitions and the game data loader.

| Module               | Purpose                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| `game_loader.py`     | `GameDataManager` class that loads JSON exports from `exports/` subdirectory.                                 |
| `item_tables.py`     | Static item definitions: `PROGRESSION_ITEMS`, `USEFUL_ITEMS`, `FILLER_ITEMS`, `TRAP_ITEMS`, `SUMMON_MATERIA`. |
| `location_tables.py` | Static location definitions: `STORY_LOCATIONS`, `VR_SUMMON_BATTLES`, `QUEST_LOCATIONS`, `MINIGAME_LOCATIONS`. |
| `region_tables.py`   | Region data: `REGIONS` list, `REGION_REQUIREMENTS` dict, `CHAPTER_REGIONS` mapping.                           |

#### Exports Subdirectory (`data/exports/`)

Contains raw JSON data extracted from the game's UAsset files using the tools in `/tools`.

| File                      | Contents                               |
| ------------------------- | -------------------------------------- |
| `_consolidated_data.json` | Combined summary of all extracted data |
| `Colosseum.json`          | Colosseum battle definitions           |
| `EnemyTerritory.json`     | World map territory/encounter data     |
| `item_names.json`         | Game ID to display name mapping        |
| `Reward.json`             | Battle reward definitions              |
| `ShopItem.json`           | Shop inventory data                    |

### Randomization Package (`randomization/`)

Contains all logic for generating randomized content.

| Module                  | Purpose                                                                                       |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| `item_pool.py`          | `ItemPoolBuilder` - Combines static items with generated equipment from game data.            |
| `location_generator.py` | `LocationGenerator` - Combines static locations with generated colosseum/territory locations. |
| `rules.py`              | `RuleFactory` - Creates access rules for regions and locations.                               |

### Hooks Package (`hooks/`)

Defines the interface between the Archipelago client and the in-game Lua mod.
This is the "contract" that both sides must follow for communication.

| Module               | Purpose                                                                                |
| -------------------- | -------------------------------------------------------------------------------------- |
| `events.py`          | Game event definitions - what the mod can detect (boss kills, quest completions, etc.) |
| `item_grants.py`     | Item grant mappings - how AP items map to in-game items and actions                    |
| `location_checks.py` | Location check triggers - what game events trigger AP location checks                  |
| `game_state.py`      | State queries and commands - reading game state and executing actions                  |
| `protocol.py`        | Message format for JSON communication between client and mod                           |

## Design Patterns

### Builder Pattern

Both `ItemPoolBuilder` and `LocationGenerator` use the builder pattern for flexible configuration:

```python
# Item pool with custom configuration
items = (ItemPoolBuilder()
    .with_progression_items()
    .with_useful_items()
    .with_filler_items()
    .with_traps()  # Optional
    .with_equipment_from_game_data()
    .build())

# Location table with custom configuration
locations = (LocationGenerator()
    .with_story_locations()
    .with_vr_summon_battles()
    .with_quest_locations()  # Optional
    .with_minigame_locations()  # Optional
    .with_colosseum_from_game_data()
    .with_territories_from_game_data()
    .build())
```

### Factory Pattern

`RuleFactory` creates rule lambdas for the Archipelago rule system:

```python
factory = RuleFactory(player)

# Create individual rules
has_chapter_1 = factory.has_chapter_complete(1)
has_tifa = factory.has_party_member("Tifa")
has_vr = factory.has_vr_access()

# Use with Archipelago's rule system
set_rule(location, has_chapter_1)
add_rule(entrance, has_vr)
```

### Facade Pattern

`items.py` and `locations.py` act as facades, providing simple public APIs:

```python
# Simple API for consumers
from .items import item_table, get_progression_items
from .locations import location_table, get_locations_by_region

# Internal complexity hidden
items = get_progression_items()  # Returns list of item names
gold_saucer = get_locations_by_region("Gold Saucer")  # Returns location names
```

## Data Flow

```
Game Data (UAsset files)
         │
         ▼ (tools/uasset_to_json.py)
    JSON Exports
         │
         ▼ (data/game_loader.py)
   GameDataManager
         │
    ┌────┴────┐
    ▼         ▼
Static    Dynamic
Tables    Generation
    │         │
    └────┬────┘
         ▼
   ItemPoolBuilder / LocationGenerator
         │
         ▼
   item_table / location_table
         │
         ▼
   FFVIIRebirthWorld
         │
         ▼
   Archipelago Multiworld
```

## Adding New Content

### Adding a New Item

1. **Choose the appropriate category** in `data/item_tables.py`:

   - `PROGRESSION_ITEMS` - Required for progress
   - `USEFUL_ITEMS` - Helpful but optional
   - `FILLER_ITEMS` - Common pool items
   - `TRAP_ITEMS` - Negative effects

2. **Add the entry**:

```python
"Item Name": FFVIIRItemData(
    "Item Name",                    # display_name
    ItemClassification.progression, # classification
    "GAME_ID",                      # game_id (optional)
    1,                              # count
    "Description"                   # description
),
```

### Adding a New Location

1. **Choose the appropriate category** in `data/location_tables.py`:

   - `STORY_LOCATIONS` - Main story
   - `VR_SUMMON_BATTLES` - VR summons
   - `QUEST_LOCATIONS` - Side quests
   - `MINIGAME_LOCATIONS` - Minigames

2. **Add the entry**:

```python
"Location Name": FFVIIRLocationData(
    "Location Name",  # display_name
    "Region Name",    # region
    "location_type",  # type (story, boss, quest, etc.)
    "GAME_ID",        # game_id (optional)
    "Description"     # description
),
```

### Adding a New Region

1. Add to `REGIONS` list in `data/region_tables.py`
2. Add requirements to `REGION_REQUIREMENTS`
3. Add chapter mapping to `CHAPTER_REGIONS`
4. Update `randomization/rules.py` if custom logic needed

### Adding a New Option

1. Define the option class in `options.py`
2. Add to `FFVIIRebirthOptions` dataclass
3. Use in world class via `self.options.<option_name>`

## Testing

Run tests from the workspace root:

```bash
python -m pytest worlds/finalfantasy_rebirth/test/
```

## Lua Mod Integration

The `hooks/` package defines the contract between the APWorld and the Lua mod.

### Communication Flow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   AP Server      │◄───►│   AP Client      │◄───►│   Lua Mod        │
│                  │     │   (Python)       │     │   (UE4SS)        │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                │
                                │ uses
                                ▼
                         ┌──────────────────┐
                         │   hooks/         │
                         │   - events       │
                         │   - item_grants  │
                         │   - location_checks
                         │   - game_state   │
                         │   - protocol     │
                         └──────────────────┘
```

### Event Flow: Location Check

```
Game Event (boss defeated)
        │
        ▼ (Lua detects via hook)
   GameState.lua
        │
        ▼ (lookup trigger)
   hooks/location_checks.py
        │
        ▼ (create message)
   hooks/protocol.py
        │
        ▼ (send to AP)
   APClient.lua → AP Server
```

### Event Flow: Item Received

```
AP Server sends item
        │
        ▼ (received by client)
   APClient.lua
        │
        ▼ (lookup grant data)
   hooks/item_grants.py
        │
        ▼ (create message)
   hooks/protocol.py
        │
        ▼ (grant in game)
   ItemHandler.lua
```

### Implementing a New Hook

1. **Define the event** in `hooks/events.py`:

```python
"boss_new_boss": GameEvent(
    event_id="boss_new_boss",
    event_type=EventType.BOSS,
    display_name="New Boss Defeated",
    description="Defeated the new boss",
    hook_function="OnBossDefeated",
    hook_condition="boss_id == 'new_boss'",
)
```

2. **Add location check** in `hooks/location_checks.py`:

```python
"boss_new_boss": LocationCheck(
    location_name="New Boss Defeated",
    check_type=CheckType.BOSS,
    trigger_id="boss_new_boss",
    hook_type="event",
    hook_target="OnBossDefeated",
)
```

3. **Implement in Lua** (`GameState.lua`):

```lua
RegisterHook("/Script/Game.BossActor:OnDefeated", function(self)
    local bossId = GetBossId(self)
    if bossId == "new_boss" then
        ReportLocationCheck("boss_new_boss")
    end
end)
```

## Dependencies

- **Archipelago**: Core multiworld framework
- **BaseClasses**: Region, Location, Item, ItemClassification
- **worlds.generic.Rules**: set_rule, add_rule

## Version History

| Version | Changes                                   |
| ------- | ----------------------------------------- |
| 0.1.0   | Initial release with basic structure      |
| 0.2.0   | Added hooks package for Lua mod interface |
