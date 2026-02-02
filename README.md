# Final Fantasy VII: Rebirth Archipelago Integration

This repository contains the scaffold for integrating Final Fantasy VII: Rebirth with [Archipelago](https://archipelago.gg/), a randomizer framework that enables multi-world, multi-game item randomization.

## Architecture Overview

The integration consists of three main components:

1. **UE4SS Mod (C++)** (`ue4ss_mod/`) - An in-process DLL mod that hooks into the game using UE4SS
   - Provides an Archipelago client wrapper
   - Implements game data access stubs (items, locations, save data)
   - Handles communication between the game and AP server

2. **Archipelago World Package (Python)** (`worlds/finalfantasy_rebirth/`) - APWorld package for server-side generation
   - Defines items, locations, and rules for Final Fantasy VII: Rebirth
   - Generates randomized seeds
   - Interfaces with the Archipelago core system

3. **Communication Flow**
   ```
   FF7 Rebirth Game <-> UE4SS Mod <-> AP Client Library <-> Archipelago Server
                                                              ^
                                                              |
                                                        APWorld Generation
   ```

## Quick Start

### Building the UE4SS Mod

1. Install [xmake](https://xmake.io/)
2. Navigate to `ue4ss_mod/`
3. Run `xmake` to build the DLL
4. See `ue4ss_mod/README_MOD.md` for detailed build and installation instructions

### Installing the APWorld Package

1. Copy the `worlds/finalfantasy_rebirth/` directory to your Archipelago installation's `custom_worlds/` folder
2. Prepare CSV data files from game assets (see `worlds/finalfantasy_rebirth/README_WORLD.md`)
3. Run `ArchipelagoGenerate` to create a seed
4. See `worlds/finalfantasy_rebirth/README_WORLD.md` for detailed instructions

## Safety and Backups

⚠️ **IMPORTANT**: Always back up your save files before using this mod. The mod modifies game behavior and can potentially corrupt saves if used improperly.

- Back up saves located in the game's save directory
- Test with a new save file first
- Be aware of potential anti-cheat systems

## Current Status

This scaffold provides the initial structure with:
- ✅ Build system configuration (xmake)
- ✅ C++ headers and skeleton implementations
- ✅ Python APWorld package structure
- ✅ Example tooling for asset extraction
- ⚠️ Game-specific logic marked with TODO
- ⚠️ AP client library integration required
- ⚠️ CSV data files need to be generated from game assets

## Next Steps

1. **Extract Game Data**: Use `tools/exporter_example.cs` as a guide to extract item/location data from game assets
2. **Implement Game Hooks**: Fill in the TODO sections in `GameData.cpp` to read/write actual game state
3. **Integrate AP Client**: Link against the apclient library and implement the client wrapper methods
4. **Populate World Data**: Create CSV files with actual items and locations from the game
5. **Define Logic Rules**: Implement progression logic in the APWorld's `set_rules()` method
6. **Test Integration**: Verify the mod loads, connects to AP server, and can send/receive items

## Contributing

Contributions are welcome! This is a community project to bring Archipelago support to Final Fantasy VII: Rebirth.

## License

See LICENSE file for details.

## Acknowledgements

- [Archipelago](https://archipelago.gg/) - Multi-world randomizer framework
- [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) - Unreal Engine 4/5 scripting system
- [UAssetAPI](https://github.com/atenfyr/UAssetAPI) - Unreal Engine asset parsing library
