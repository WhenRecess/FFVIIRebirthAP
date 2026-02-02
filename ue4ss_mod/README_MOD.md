# FFVIIRebirthAP UE4SS Mod - Build Instructions

This directory contains the C++ source code for the **FFVIIRebirthAP** UE4SS mod, which provides Archipelago integration for Final Fantasy VII: Rebirth.

## Prerequisites

### Required Tools

1. **xmake** - Cross-platform build system
   - Install from [xmake.io](https://xmake.io/)
   - Windows: `scoop install xmake` or download installer
   - Linux: `bash <(curl -fsSL https://xmake.io/shget.text)`

2. **C++ Compiler**
   - Windows: Visual Studio 2019+ with C++ workload
   - Linux: GCC 11+ or Clang 14+
   - Ensure C++20 support is available

3. **UE4SS SDK**
   - Download from [UE4SS releases](https://github.com/UE4SS-RE/RE-UE4SS/releases)
   - Extract and set `UE4SS_SDK_PATH` environment variable to the SDK directory
   - The SDK should contain `include/` and `lib/` subdirectories

4. **apclient C++ Library**
   - Clone from [Archipelago apclient](https://github.com/ArchipelagoMW/apclient)
   - Build following the apclient documentation (typically `cmake` and `make`)
   - Set `APCLIENT_PATH` environment variable to the installation directory
   - The path should contain `include/` and `lib/` subdirectories with apclient headers/libraries

### Setting Environment Variables

**Windows (PowerShell):**
```powershell
$env:UE4SS_SDK_PATH = "C:\path\to\ue4ss_sdk"
$env:APCLIENT_PATH = "C:\path\to\apclient"
```

**Linux/macOS:**
```bash
export UE4SS_SDK_PATH="/path/to/ue4ss_sdk"
export APCLIENT_PATH="/path/to/apclient"
```

Alternatively, edit `xmake.lua` and hardcode the paths if environment variables are not desired.

## Building the Mod

1. **Configure the project:**
   ```bash
   cd ue4ss_mod
   xmake f -p windows -a x64 -m release
   ```
   
   Options:
   - `-p windows`: Target platform (windows, linux, macosx)
   - `-a x64`: Architecture (x64, x86)
   - `-m release`: Build mode (release, debug)

2. **Build the DLL:**
   ```bash
   xmake
   ```

3. **Output location:**
   - The compiled DLL will be in `bin/release/windows/x64/FFVIIRebirthAP.dll`

## Installing the Mod

1. **Locate your game directory:**
   - Example: `C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY VII REBIRTH`

2. **Install UE4SS** (if not already installed):
   - Copy UE4SS files (`UE4SS.dll`, `dwmapi.dll`, etc.) to `<GameDir>/Binaries/Win64/`
   - Create `<GameDir>/Binaries/Win64/Mods/` directory if it doesn't exist

3. **Install FFVIIRebirthAP mod:**
   ```
   <GameDir>/Binaries/Win64/Mods/
   └── FFVIIRebirthAP/
       ├── enabled.txt          (empty file to enable the mod)
       ├── FFVIIRebirthAP.dll   (your compiled DLL)
       ├── items.csv            (item mappings, see below)
       └── locations.csv        (location mappings, see below)
   ```

4. **Create `enabled.txt`:**
   - This is an empty file that tells UE4SS to load the mod
   - Windows: `type nul > enabled.txt`
   - Linux: `touch enabled.txt`

## CSV File Format

### items.csv
```csv
ItemName,ItemID
Buster Sword,1000
Bronze Bangle,2000
Potion,3000
```

### locations.csv
```csv
LocationName,LocationID
Boss: Scorpion Sentinel,1
Chest: Sector 7 Slums,2
Materia: Kalm,3
```

**Important:** You must populate these CSVs with actual game data. Use the `tools/exporter_example.cs` utility to extract DataTable rows from `.uasset` files.

## Using the Mod

1. **Launch the game** with UE4SS installed.

2. **Open the console** (usually `~` or `F10` depending on UE4SS configuration).

3. **Load data files:**
   ```
   /loaditems C:\Path\To\items.csv
   /loadlocations C:\Path\To\locations.csv
   ```

4. **Connect to Archipelago server:**
   ```
   /connect archipelago.gg:38281 YourSlotName
   ```
   
   With password:
   ```
   /connect archipelago.gg:38281 YourSlotName your_password
   ```

5. **Check status:**
   ```
   /status
   ```

6. **View help:**
   ```
   /aphelp
   ```

## Development Notes

### TODO: Implement Game Hooks

The current scaffold provides console commands and data structures, but **game-specific hooks are not implemented**. You need to:

1. **Hook item collection events:**
   - Intercept calls to game functions that add items to inventory
   - Map game item IDs to Archipelago item names using `GameData`
   - Call `client_->SendLocationCheck(location_id)` when a location is collected

2. **Hook received items:**
   - Register a callback with `client_->RegisterItemReceivedCallback(...)`
   - When an item is received from Archipelago, add it to the player's inventory
   - Use UE4SS APIs to call game functions (e.g., `GiveItemToPlayer(item_id)`)

3. **Save/load integration:**
   - Persist checked locations across game sessions
   - Restore Archipelago connection state on game load

### Debugging

- UE4SS logs are written to `<GameDir>/Binaries/Win64/UE4SS.log`
- Your mod can use `Output::send(STR("message"))` to log to the UE4SS console

### Common Issues

**"Failed to load UE4SS.dll":**
- Ensure UE4SS is installed correctly in `Binaries/Win64/`
- Check that your game is supported by UE4SS (Unreal Engine 4.x)

**"Mod not loading":**
- Verify `enabled.txt` exists in the mod folder
- Check UE4SS logs for error messages
- Ensure the DLL is compiled for the correct architecture (x64 for most games)

**"apclient not found":**
- Verify `APCLIENT_PATH` environment variable is set
- Ensure apclient library files are in `$APCLIENT_PATH/lib/`
- You may need to copy apclient DLLs to the game's `Binaries/Win64/` directory

## Additional Resources

- [UE4SS Documentation](https://docs.ue4ss.com/)
- [UE4SS GitHub](https://github.com/UE4SS-RE/RE-UE4SS)
- [Archipelago Development Docs](https://archipelago.gg/tutorial/)
- [xmake Documentation](https://xmake.io/#/guide/quickstart)
