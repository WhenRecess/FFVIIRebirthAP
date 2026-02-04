# Game Data Exports

This directory contains raw JSON data extracted from Final Fantasy VII: Rebirth's UAsset files.

## File Descriptions

| File                         | Description                                       |
| ---------------------------- | ------------------------------------------------- |
| `_consolidated_data.json`    | Combined summary of items, enemies, battles, etc. |
| `_export_summary.json`       | Summary of what was exported                      |
| `_parse_summary.json`        | Summary of parsing results                        |
| `BattleCharaSpec.json`       | Battle character specifications                   |
| `Colosseum.json`             | Colosseum battle definitions                      |
| `ColosseumPositionData.json` | Colosseum position/layout data                    |
| `EnemyTerritory.json`        | World map territory definitions                   |
| `EnemyTerritoryLevel.json`   | Territory level data                              |
| `EnemyTerritoryMob.json`     | Territory enemy spawn data                        |
| `ItemCraftRecipe.json`       | Crafting recipe definitions                       |
| `Item_export.json`           | Item export data                                  |
| `item_names.json`            | Mapping of game IDs to display names              |
| `ResidentPack.json`          | Resident pack data                                |
| `Reward.json`                | Battle/quest reward definitions                   |
| `RewardRandom.json`          | Random reward pool data                           |
| `ShopItem.json`              | Shop inventory definitions                        |
| `ShopList.json`              | Shop list data                                    |
| `WorldItemSpec.json`         | World item specifications                         |

## Parsed Files

Files ending in `_parsed.json` are processed versions of the raw exports with additional metadata extracted.

## How to Update

These files are generated using the tools in `/tools`:

1. Extract UAsset files from the game
2. Run `uasset_to_json.py` to convert to JSON
3. Run `parse_exported_json.py` to create parsed versions
4. The `game_loader.py` module loads these files at runtime

## Note

Do not manually edit these files. They should be regenerated from game data when the game updates.
