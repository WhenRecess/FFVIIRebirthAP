# Final Fantasy VII: Rebirth - Archipelago Integration

This repository provides a scaffold for integrating **Final Fantasy VII: Rebirth** with [Archipelago](https://archipelago.gg/), a multi-game, multi-world randomizer platform.

## ⚠️ Work in Progress

This is a **WIP scaffold**. Game-specific logic (item checks, location handling, world generation) is marked with `TODO` comments and must be implemented by developers familiar with the game's internals.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Final Fantasy VII: Rebirth                 │
│                      (Unreal Engine 4)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (in-process DLL injection via UE4SS)
                     │
┌────────────────────▼────────────────────────────────────────┐
│              FFVIIRebirthAP UE4SS Mod (C++)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  dllmain.cpp:                                        │   │
│  │  - Hooks BeginPlay, ProcessConsoleExec               │   │
│  │  - Console commands: /connect, /status               │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Client.hpp/cpp:                                     │   │
│  │  - APClient wrapper (apclient C++ library)           │   │
│  │  - Connect to Archipelago server                     │   │
│  │  - Send LocationChecks, receive NetworkItem          │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  GameData.hpp/cpp:                                   │   │
│  │  - Load item/location mappings from CSV              │   │
│  │  - Hook game events (collect item, defeat enemy)     │   │
│  │  - TODO: Implement game-specific hooks               │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (Archipelago network protocol)
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Archipelago Server & Client                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ (World generation, item placement)
                     │
┌────────────────────▼────────────────────────────────────────┐
│      worlds/finalfantasy_rebirth/ (Python APWorld)           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  __init__.py: FFVIIRebirthWorld class                │   │
│  │  - generate_early(), create_regions()                │   │
│  │  - create_items(), set_rules()                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  items.py: Item definitions, CSV loader              │   │
│  │  locations.py: Location definitions, CSV loader      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Quickstart

### Prerequisites

- **UE4SS**: [UE4SS releases](https://github.com/UE4SS-RE/RE-UE4SS/releases) (for DLL injection into Unreal Engine games)
- **xmake**: [xmake.io](https://xmake.io/) (build system for C++ mod)
- **apclient C++ library**: See [Archipelago apclient documentation](https://github.com/ArchipelagoMW/apclient)
- **Archipelago**: [archipelago.gg/downloads](https://archipelago.gg/downloads) (Python 3.10+)
- **UAssetAPI** (optional): For exporting game data to CSV

### Building the UE4SS Mod

1. Navigate to `ue4ss_mod/` and follow the instructions in `README_MOD.md`.
2. Ensure you have `apclient` library available (vendor it or build from source).
3. Build with xmake:
   ```bash
   cd ue4ss_mod
   xmake
   ```
4. Copy the compiled DLL to `<GameDir>/Binaries/Win64/Mods/FFVIIRebirthAP/`.

See `ue4ss_mod/README_MOD.md` for detailed build instructions.

### Installing the Archipelago World

1. Navigate to `worlds/finalfantasy_rebirth/` and follow `README_WORLD.md`.
2. Copy the folder to your Archipelago installation:
   ```bash
   cp -r worlds/finalfantasy_rebirth <ArchipelagoInstall>/worlds/
   ```
3. Place item and location CSVs in `worlds/finalfantasy_rebirth/data/`.
4. Generate a seed using Archipelago's YAML configuration:
   ```bash
   python ArchipelagoGenerate.py
   ```

See `worlds/finalfantasy_rebirth/README_WORLD.md` for detailed instructions.

### Exporting Game Data

Use the C# exporter example in `tools/exporter_example.cs` to extract DataTable rows from `.uasset` files:

```bash
cd tools
dotnet run -- <path_to_uasset_file>
```

This outputs CSV files suitable for the World package.

## Important Notes

### Save Backups

**Always back up your save files before using mods or randomizers.** Modifying game behavior can corrupt saves.

### Anti-Cheat

If the game uses anti-cheat software (e.g., Easy Anti-Cheat), you may need to:
- Launch the game in offline mode
- Disable anti-cheat via launch parameters (game-specific)
- Use a separate, non-online profile for randomizer play

Consult the game's modding community for guidance.

## Next Steps (TODO)

1. **Implement game-specific hooks in `GameData.cpp`**:
   - Hook item collection events
   - Hook location checks (boss defeats, chests opened, etc.)
   - Map game item/location IDs to Archipelago names

2. **Populate item and location CSVs**:
   - Export DataTables from `.uasset` files using UAssetAPI
   - Create `items.csv` and `locations.csv` in `worlds/finalfantasy_rebirth/data/`

3. **Implement World logic in `__init__.py`**:
   - Define regions and connections in `create_regions()`
   - Implement item placement rules in `set_rules()`
   - Generate output files in `generate_output()`

4. **Test the integration**:
   - Generate a seed with Archipelago
   - Launch the game with UE4SS and the mod
   - Use `/connect <slot_name>` in the in-game console
   - Verify items are sent/received correctly

5. **Write tests**:
   - Add `WorldTestBase` tests in `worlds/finalfantasy_rebirth/test/`

## Contributing

This is a community-driven project. Contributions are welcome! Please open an issue or PR if you have:
- Improvements to the scaffold
- Game-specific data exports
- Implemented hooks or logic
- Bug fixes or documentation updates

## Resources

- [Archipelago Documentation](https://archipelago.gg/tutorial/)
- [UE4SS Documentation](https://docs.ue4ss.com/)
- [apclient C++ Library](https://github.com/ArchipelagoMW/apclient)
- [UAssetAPI Documentation](https://github.com/atenfyr/UAssetAPI)

## License

This project is provided as-is for educational and community use. Respect the intellectual property of Square Enix and the Archipelago project.
