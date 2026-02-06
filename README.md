# Final Fantasy VII: Rebirth - Archipelago Randomizer

A randomizer for Final Fantasy VII: Rebirth using [Archipelago](https://archipelago.gg) for seed generation and logic.

## Current Status: Single-World Randomizer

**Phase 1** focuses on a **single-world local randomizer** using pre-randomization (pak patching). All changes are baked into modified game files before launch.

**Multiworld support** is a future goal, currently blocked by the inability to grant items at runtime.

## How It Works

1. **Extract** game assets from paks using retoc
2. **Convert** binary assets to JSON using UAssetGUI (FF7R fork)
3. **Randomize** values in JSON using Python scripts
4. **Repack** modified JSON back to binary, then to pak format
5. **Deploy** to `~mods/` folder — game loads modified paks automatically

## Working Randomizers

| Randomizer      | What It Changes                                       | Status     |
| --------------- | ----------------------------------------------------- | ---------- |
| Enemy Stats     | HP, attack, defense, elemental resistances            | ✅ Working |
| Equipment Stats | Weapon/armor stats, skill core slots, materia layouts | ✅ Working |
| Shop Prices     | Per-shop item prices (all 6 shop types)               | ✅ Working |
| Item Prices     | Base buy/sell values for consumables and gear         | ✅ Working |
| Materia Prices  | Materia sell prices and AP growth rates               | ✅ Working |
| Rewards         | Chest and quest reward item shuffling                 | ✅ Working |
| Shop Inventory  | Which items appear in each shop                       | ✅ Working |

All 7 randomizers support `--seed`, `--auto-deploy`, and `--test-mode`. See [tools/README.md](tools/README.md) for usage.

## Repository Structure

```
FFVIIRebirthAP/
├── tools/                        # Randomizer scripts and supporting tools
│   ├── *_randomizer.py           # 7 active randomizers
│   ├── bin/                      # Compiled tools (retoc, UAssetGUI)
│   ├── data/                     # Static game data
│   └── UAssetGUI_FF7R/           # FF7R-specific UAssetGUI (built)
│
├── ue4ss_mod/                    # UE4SS C++ mod (runtime hooks)
│
├── ue4ss_mod_lua/                # UE4SS Lua mod (AP client, tracking)
│   └── Scripts/
│       ├── main.lua              # Entry point
│       ├── APClient.lua          # Archipelago WebSocket client
│       ├── GameState.lua         # Game state monitoring
│       └── ItemHandler.lua       # Item grant implementation
│
├── worlds/finalfantasy_rebirth/  # AP world module
│   ├── __init__.py               # World definition
│   ├── items.py                  # Item definitions
│   ├── locations.py              # Location definitions
│   └── options.py                # World options
│
└── POTENTIAL_RANDOMIZERS.md      # Ideas and roadmap for new randomizers
```

## Quick Start

```bash
cd tools

# Randomize enemy stats with a seed and deploy
python enemy_stats_randomizer.py --seed 12345 --auto-deploy

# Test mode (extreme values for easy in-game verification)
python equipment_stats_randomizer.py --test-mode --auto-deploy
```

## Safety & Backup

⚠️ Always backup your save files before using this mod!

- Backup `%LOCALAPPDATA%\FF7R\Saved\SaveGames\`
- Mods are deployed to `~mods/` and can be removed by deleting that folder
- This is experimental software — use at your own risk

## Credits

- [Archipelago](https://archipelago.gg) - Multiworld randomizer framework
- [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) - Unreal Engine scripting system
- [UAssetGUI (FF7R fork)](https://github.com/LongerWarrior/UAssetGUI) - Asset JSON export/import
- [retoc](https://github.com/trumank/retoc) - Unreal pak extract/repack
