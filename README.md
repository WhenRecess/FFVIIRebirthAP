# Final Fantasy VII: Rebirth - Archipelago Integration

An integration project for connecting Final Fantasy VII: Rebirth with [Archipelago](https://archipelago.gg), enabling multiworld randomizer functionality.

## Project Overview

This project provides the infrastructure to integrate FFVII: Rebirth with the Archipelago multiworld randomizer system. It consists of:

1. **UE4SS In-Process Mod** (`ue4ss_mod/`) - A C++ DLL mod that hooks into the game via UE4SS to:
   - Connect to an Archipelago server as a client
   - Track location checks (encounters, story events, chests, etc.)
   - Receive and grant items from other players
   - Implement optional DeathLink functionality
   
2. **APWorld Package** (`worlds/finalfantasy_rebirth/`) - A Python Archipelago world definition that:
   - Defines the item and location pools for FFVII: Rebirth
   - Generates randomized game data
   - Handles multiworld generation logic

3. **Tooling** (`tools/`) - Helper utilities for extracting game data from UAsset files

## Architecture

```
┌─────────────────────┐
│  FFVII: Rebirth     │
│  (Unreal Engine)    │
└──────────┬──────────┘
           │
           │ UE4SS Lua Hook
           ▼
┌─────────────────────┐
│  ue4ss_mod DLL      │
│  (C++ Mod)          │
│  - GameData hooks   │
│  - APClient wrapper │
└──────────┬──────────┘
           │
           │ Archipelago Protocol
           ▼
┌─────────────────────┐
│  Archipelago Server │
│  (Python)           │
└──────────┬──────────┘
           │
           │ Generation
           ▼
┌─────────────────────┐
│  APWorld Package    │
│  (Python)           │
│  - Item/Location    │
│    definitions      │
│  - Logic rules      │
└─────────────────────┘
```

## Quick Start

### Building the UE4SS Mod

1. Install [xmake](https://xmake.io)
2. Navigate to `ue4ss_mod/`
3. Run `xmake build`
4. Copy the resulting DLL to your UE4SS mods directory
5. See `ue4ss_mod/README_MOD.md` for detailed instructions

### Installing the APWorld Package

1. Copy `worlds/finalfantasy_rebirth/` to your Archipelago installation's `custom_worlds/` directory
2. Prepare data CSVs from game files (see `tools/exporter_example.cs`)
3. Run `ArchipelagoGenerate` with your YAML configuration
4. See `worlds/finalfantasy_rebirth/README_WORLD.md` for detailed instructions

## Current Status

⚠️ **This is a scaffold/template project** ⚠️

The current code provides the basic structure and API definitions but does **not** include:
- Game-specific memory addresses or save file parsing
- Complete item/location definitions
- Actual AP client library integration (requires linking apclient)
- SSL certificates for server connection

All game-specific logic is marked with `TODO` comments. Developers will need to:
1. Reverse engineer FFVII: Rebirth's memory structures
2. Implement save file reading/writing
3. Map game events to AP locations
4. Link against the apclient C++ library
5. Export comprehensive item/location data from game files

## Safety & Backup

⚠️ **IMPORTANT**: Always backup your save files before using this mod!

- The mod modifies game behavior and save data
- Create backups of your `%LOCALAPPDATA%\FF7R\Saved\SaveGames\` directory
- Be aware of potential anti-cheat systems (though FFVII: Rebirth is primarily single-player)
- This is experimental software - use at your own risk

## Next Steps

1. **Game Research**: Reverse engineer the game's:
   - Save file format and structures
   - Item IDs and inventory system
   - Event/encounter tracking systems
   - Territory/map structures

2. **Data Export**: Use `tools/exporter_example.cs` to:
   - Extract DataTables from game PAK files
   - Generate CSV files with item/location data
   - Document game data structures

3. **Mod Implementation**: Complete the C++ mod:
   - Implement `GameData` functions for save reading/writing
   - Add memory scanning for runtime game state
   - Integrate apclient library for server communication
   - Test location checks and item receiving

4. **World Definition**: Complete the APWorld:
   - Define complete item and location pools
   - Implement progression logic and rules
   - Add world-specific options and settings
   - Write comprehensive tests

5. **Testing**: Verify the integration:
   - Test single-player AP generation
   - Test multiworld synchronization
   - Validate save file integrity
   - Document known issues

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
