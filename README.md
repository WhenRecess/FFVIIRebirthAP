# Final Fantasy VII: Rebirth - Archipelago Randomizer

A randomizer for Final Fantasy VII: Rebirth using [Archipelago](https://archipelago.gg) for seed generation and logic.

## Current Status: Single-World Randomizer

**Phase 1** focuses on a **single-world local randomizer** using pre-randomization (pak patching). All item placements are baked into modified game files before launch.

**Multiworld support** is a future goal but is currently blocked by the inability to grant items at runtime (no game API functions found for adding items to inventory).

## How It Works

### Pre-Randomization Approach

1. **Generate seed** with Archipelago (handles logic, item placement)
2. **Pre-randomize game files** using Python tools
   - Shop prices, equipment stats, chest contents, enemy drops
   - Deterministic results from AP seed
3. **Deploy as pak mod** to game folder
4. **Play!** All randomized content is already in the game files

### Why Pre-Randomization?

- FF7R uses Unreal Engine with complex encrypted assets
- Prices, stats, and loot tables are stored in DataTable assets
- Can be modified deterministically with a seed
- Stable, verifiable, no runtime overhead
- **Tool**: `tools/smart_price_randomizer.py` (working now!)

## Repository Structure

```
FFVIIRebirthAP/
├── tools/                        # Pre-randomization tools ⭐
│   ├── smart_price_randomizer.py # Working shop price randomizer
│   ├── bin/                      # Bundled tools (retoc, UAssetGUI)
│   ├── data/                     # Extracted game data (502 items mapped)
│   ├── config.ini                # User path configuration
│   └── AP_DEVELOPMENT_GUIDE.md   # Complete development guide
│
├── ue4ss_mod_lua/                # UE4SS Lua mod (runtime) ⭐
│   └── Scripts/
│       ├── main.lua              # Entry point
│       ├── APClient.lua          # Archipelago WebSocket client
│       ├── GameState.lua         # Game state monitoring
│       └── ItemHandler.lua       # Item give implementation
│
├── ue4ss_mod/                    # C++ alternative (optional)
│   └── [C++ DLL project]
│
└── worlds/finalfantasy_rebirth/  # AP world module
    ├── __init__.py               # World definition
    ├── items.py                  # 276 unique items
    ├── locations.py              # 506 locations
    └── options.py                # World options
```

## Architecture (Single-World)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SEED GENERATION & SETUP                              │
├─────────────────────────────────────────────────────────────────────────┤
│  [Archipelago] → generates seed + item placements                       │
│       ↓                                                                 │
│  [Pre-Randomizers] → modify game files based on placements              │
│      ├── smart_price_randomizer.py → ShopItem.uexp                      │
│      ├── (planned) reward_randomizer.py → Chest contents                │
│      └── (planned) equipment_randomizer.py → Equipment stats            │
│       ↓                                                                 │
│  [retoc] → repack to .pak/.ucas/.utoc                                   │
│       ↓                                                                 │
│  [Deploy] → copy to ~mods/ folder                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                         GAMEPLAY                                        │
├─────────────────────────────────────────────────────────────────────────┤
│  [FF7R] → loads pre-randomized paks automatically                       │
│       ↓                                                                 │
│  [Player] → plays with randomized shops, chests, equipment              │
│       ↓                                                                 │
│  [Tracker] → (optional) manual or auto-tracking via Lua mod             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Pre-Randomization (Working Now!)

Randomize shop prices and deploy to game:

```bash
cd tools
# Edit config.ini with your game paths first!
python smart_price_randomizer.py "C:\...\ShopItem.uexp" --auto-deploy 12345 100 5000
```

This will:

1. Randomize all shop prices (seed 12345, range 100-5000 gil)
2. Repack with retoc
3. Deploy to your game's ~mods folder
4. Ready to play!

See `tools/AP_DEVELOPMENT_GUIDE.md` for full documentation.

### 2. APWorld (For Seed Generation)

1. Copy `worlds/finalfantasy_rebirth/` to Archipelago's `lib/worlds/`
2. Generate seeds with Archipelago
3. See `worlds/finalfantasy_rebirth/README_WORLD.md`

## Current Status

### ✅ Working

| Component                | Status        | Details                                 |
| ------------------------ | ------------- | --------------------------------------- |
| Shop Price Randomization | ✅ Complete   | 252-455 arrays, 280-540 prices modified |
| Item ID Extraction       | ✅ Complete   | 502 items mapped to game IDs            |
| File Patching Workflow   | ✅ Complete   | Verified in-game (Equipment, ShopItem)  |
| APWorld Structure        | ✅ Scaffolded | World module, items, locations defined  |

### 🔄 In Progress

| Component               | Status             | Next Step                            |
| ----------------------- | ------------------ | ------------------------------------ |
| Chest/Reward Randomizer | 🔄 Not Started     | Apply same pattern as shop prices    |
| Equipment Randomization | 🔄 Algorithm ready | Apply same pattern detection         |
| Location Database       | 🔄 Partial (~60)   | Need 500+ locations mapped           |
| Seed-to-Pak Pipeline    | 🔄 Not Started     | Connect AP output to pre-randomizers |

### ⬜ Future (Multiworld)

| Feature | Blocker |
| ------- | ------- |
| Runtime item grants | No game API for adding items |
| Multiworld sync | Depends on item grants |
| DeathLink | Depends on runtime mod |

## Safety & Backup

⚠️ **IMPORTANT**: Always backup your save files before using this mod!

- The mod modifies game behavior and save data
- Create backups of your `%LOCALAPPDATA%\FF7R\Saved\SaveGames\` directory
- Be aware of potential anti-cheat systems (though FFVII: Rebirth is primarily single-player)
- This is experimental software - use at your own risk

## Development Roadmap

See [TASKS.md](TASKS.md) for detailed task breakdown.

### Phase 1: Expand Pre-Randomization
- [ ] Chest/reward content randomization
- [ ] Equipment stat randomization
- [ ] Enemy drop randomization

### Phase 2: Complete AP World Data
- [ ] Map all 500+ locations
- [ ] Define all items with game IDs
- [ ] Implement progression logic

### Phase 3: Unified Pipeline
- [ ] AP seed → pre-randomizers → deployable pak
- [ ] Wire options to affect generation
- [ ] Spoiler log generation

### Phase 4: Polish
- [ ] Full playtest
- [ ] User documentation
- [ ] Optional tracker integration

### Future: Multiworld
- Requires solving runtime item grant problem
- May need external companion tool or wait for UE4SS improvements

## Contributing

This is a community project. Contributions are welcome! Please:

- Follow the existing code style
- Add TODO comments for incomplete functionality
- Document any game-specific discoveries
- Test thoroughly before submitting PRs

## License

TBD - To be determined by repository owner

## Credits

- [Archipelago](https://archipelago.gg) - Multiworld randomizer framework
- [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) - Unreal Engine scripting system
- Community contributors and testers

## Resources

- [Archipelago Documentation](https://archipelago.gg/tutorial/)
- [UE4SS Documentation](https://docs.ue4ss.com/)
- [UAssetAPI](https://github.com/atenfyr/UAssetAPI) - For extracting game data
