# FF7 Rebirth Archipelago - Tools

Randomizers and supporting tools for the FF7 Rebirth Archipelago project.

## Randomizers

All randomizers follow the same pipeline: **retoc extract → UAssetGUI tojson → Python modify JSON → UAssetGUI fromjson → retoc repack → deploy to ~mods**.

| Randomizer                      | Target Asset           | What It Randomizes                                         |
| ------------------------------- | ---------------------- | ---------------------------------------------------------- |
| `enemy_stats_randomizer.py`     | BattleCharaSpec.uasset | Enemy HP, attack, defense, etc. (bosses scaled separately) |
| `equipment_stats_randomizer.py` | Equipment.uasset       | Weapon/armor stats, skill core slots, materia slot layouts |
| `shop_price_randomizer.py`      | ShopItem.uasset        | Per-shop override prices (all 6 shop types)                |
| `item_price_randomizer.py`      | Item.uasset            | Base buy/sell values for consumables, weapons, armor       |
| `materia_price_randomizer.py`   | Materia.uasset         | Materia sell prices and AP growth rates                    |
| `reward_randomizer.py`          | Reward.uasset          | Chest/quest reward item shuffling                          |
| `shop_inventory_randomizer.py`  | ShopItem.uasset        | Which items appear in each shop                            |

### Usage

All randomizers support `--seed`, `--auto-deploy`, and `--test-mode`:

```bash
cd tools

# Randomize with seed
python enemy_stats_randomizer.py --seed 12345 --auto-deploy

# Test mode (extreme values for easy verification)
python equipment_stats_randomizer.py --test-mode --auto-deploy
```

## Directory Structure

```
tools/
├── bin/                    # Compiled tools (retoc, UAssetGUI)
│   ├── retoc_filtered.exe  # Pak extract/repack tool
│   ├── UAssetGUI.exe       # Asset JSON export (generic UE)
│   ├── UAssetGUI_FF7R.exe  # Asset JSON export (FF7R-specific)
│   └── Mappings/           # .usmap type definitions
├── data/                   # Static data files (see data/README.md)
├── UAssetGUI_FF7R/         # FF7R-specific UAssetGUI source (built)
├── *_randomizer.py         # Active randomizers (7 total)
└── JSON_EXPORT_WORKFLOW.md # Documents the JSON pipeline
```

## Prerequisites

- Python 3.10+
- FF7 Rebirth (PC) with game paks at the default Steam location
- .NET 8.0 Runtime (for UAssetGUI)
- Compiled tools in `bin/` (retoc_filtered.exe, UAssetGUI_FF7R.exe)

## How the Pipeline Works

1. **retoc to-legacy** extracts `.uasset`/`.uexp` from game paks
2. **UAssetGUI tojson** converts binary asset to editable JSON
3. **Python randomizer** modifies values in the JSON
4. **UAssetGUI fromjson** converts JSON back to binary
5. **retoc to-zen** repacks into `.pak`/`.ucas`/`.utoc`
6. Files are deployed to `~mods/` folder for the game to load
