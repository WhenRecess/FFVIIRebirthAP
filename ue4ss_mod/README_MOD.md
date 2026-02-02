# FFVII Rebirth Archipelago Mod - Build & Installation Guide

This directory contains the UE4SS in-process DLL mod for integrating Final Fantasy VII: Rebirth with Archipelago.

## Overview

The mod provides:
- **AP Client Integration**: Connects to Archipelago servers and synchronizes game state
- **GameData Interface**: Hooks for reading/writing game data (saves, inventory, events)
- **Console Commands**: In-game commands for connecting and managing the AP session
- **Runtime Enemy Randomization**: Placeholder for replacing enemy templates

## Prerequisites

### Building

- **xmake** (v2.8.0 or later): [Install xmake](https://xmake.io/#/getting_started)
- **Visual Studio 2022** or **MSVC Build Tools** with C++20 support
- **Windows SDK** (10.0.19041.0 or later recommended)

### Runtime

- **UE4SS** (v3.0.0 or later): [UE4SS Releases](https://github.com/UE4SS-RE/RE-UE4SS/releases)
- **Final Fantasy VII: Rebirth** (PC version)
- **apclient library** (C++ Archipelago client) - Not included, must be built separately
- **cacert.pem** - SSL certificate bundle for HTTPS connections

## Building the Mod

### Step 1: Install Dependencies

```powershell
# Install xmake if not already installed
powershell -c "irm https://xmake.io/psget.txt | iex"
```

### Step 2: Configure Build (Optional)

The `xmake.lua` file contains TODO comments for paths that need to be configured:

```lua
-- TODO: Add UE4SS SDK include paths when available
-- add_includedirs("path/to/UE4SS/include")

-- TODO: Add apclient library when available
-- add_includedirs("path/to/apclient/include")
-- add_linkdirs("path/to/apclient/lib")
-- add_links("apclient")
```

**Note**: The current scaffold builds without these dependencies, but full functionality requires:
1. UE4SS SDK headers for proper mod integration
2. apclient library for actual server communication

### Step 3: Build

```powershell
cd ue4ss_mod
xmake config -m release -a x64
xmake build
```

For debug builds (with more logging):
```powershell
xmake config -m debug -a x64
xmake build
```

The compiled DLL will be in: `build/windows/x64/release/FFVIIRebirthAP.dll`

## Installation

### Step 1: Install UE4SS

1. Download UE4SS from [GitHub Releases](https://github.com/UE4SS-RE/RE-UE4SS/releases)
2. Extract to your FFVII Rebirth game directory (where the .exe is located)
3. Launch the game once to verify UE4SS is working (console should appear)

### Step 2: Install the Mod

1. Create the mod directory:
   ```
   <Game Directory>/Binaries/Win64/Mods/FFVIIRebirthAP/
   ```

2. Create a `dlls` subdirectory:
   ```
   <Game Directory>/Binaries/Win64/Mods/FFVIIRebirthAP/dlls/
   ```

3. Copy `FFVIIRebirthAP.dll` to:
   ```
   <Game Directory>/Binaries/Win64/Mods/FFVIIRebirthAP/dlls/main.dll
   ```
   **Important**: Rename the DLL to `main.dll`!

4. Create an `enabled.txt` file in the mod directory:
   ```
   <Game Directory>/Binaries/Win64/Mods/FFVIIRebirthAP/enabled.txt
   ```
   (The file can be empty)

### Step 3: Install SSL Certificate

For HTTPS/WSS connections to Archipelago servers:

1. Download `cacert.pem` from [curl.se](https://curl.se/ca/cacert.pem)
2. Place it in the game directory or specify its path in code

**Note**: The current scaffold does not implement SSL, but this will be needed for production use.

### Final Directory Structure

```
FFVII-Rebirth/
├── Binaries/
│   └── Win64/
│       ├── Mods/
│       │   └── FFVIIRebirthAP/
│       │       ├── enabled.txt
│       │       └── dlls/
│       │           └── main.dll (your built mod)
│       ├── ue4ss.dll
│       ├── ue4ss-settings.ini
│       └── FF7Rebirth.exe
└── cacert.pem (optional, for SSL)
```

## Usage

### Launching

1. Start Final Fantasy VII: Rebirth
2. Open the UE4SS console (typically `~` or `F10`)
3. You should see initialization messages:
   ```
   === FFVII Rebirth Archipelago Mod ===
   Version: 0.1.0 (Scaffold)
   Initializing...
   Mod initialized successfully!
   Use /connect <server> <slot> [password] to connect
   ```

### Console Commands

#### Connect to AP Server
```
/connect archipelago.gg:38281 YourSlotName
```
With password:
```
/connect archipelago.gg:38281 YourSlotName roomPassword123
```

#### Disconnect
```
/disconnect
```

#### Toggle DeathLink
```
/deathlink
```

#### Check Status
```
/ap-status
```

#### Replace Enemy (Example/Testing)
```
/ap-replace <territoryIndex> <slotIndex> <newEnemyId>
```
Example: `/ap-replace 10 5 42` - Replace territory 10, slot 5 with enemy template 42

## Troubleshooting

### Mod doesn't load
- Check that `enabled.txt` exists in the mod directory
- Verify the DLL is named `main.dll` (not `FFVIIRebirthAP.dll`)
- Check UE4SS logs in `Binaries/Win64/ue4ss.log`
- Ensure game is not using anti-cheat that blocks DLL injection

### Connection fails
- Verify server address and port are correct
- Check firewall settings
- Ensure slot name matches the generated game
- If using SSL, verify `cacert.pem` is present and accessible

### Game crashes
- Try debug build for more information
- Check if game updated (may need UE4SS update)
- Backup saves before testing!

### Commands don't work
- Verify you're typing in the UE4SS console (not game chat)
- Check console for error messages
- Ensure mod initialized successfully (check for init messages)

## Development Notes

### Current Status

⚠️ **This is a scaffold/template** - Most functionality is stubbed out with TODOs.

What works:
- ✅ Mod loads and initializes
- ✅ Console commands register
- ✅ Basic structure for AP client

What needs implementation:
- ❌ Actual game memory reading/writing
- ❌ Save file parsing and modification
- ❌ Real AP client library integration
- ❌ Item ID mapping (AP ↔ Game)
- ❌ Location tracking (encounters, events, chests)
- ❌ Enemy randomization (runtime modification)

### Implementing Game Hooks

To add real functionality:

1. **Find Game Objects**: Use UE4SS to enumerate UObjects and find:
   - Save game objects
   - Player inventory structures
   - World/territory managers
   - Event tracking systems

2. **Implement GameData Functions**:
   - `GetCurrentMap()`: Read from world state
   - `SaveGame()`: Call game's save method
   - `GiveItemByCode()`: Add items to inventory
   - `CheckEncounterSpots()`: Compare current vs. saved encounter flags

3. **Link apclient**: 
   - Build or obtain the C++ apclient library
   - Update `xmake.lua` with proper include/lib paths
   - Uncomment and implement client code in `src/Client.cpp`

4. **Test Incrementally**:
   - Start with read-only operations (GetCurrentMap, etc.)
   - Add console logging for all operations
   - Test save/load functionality thoroughly before deploying

## Safety Warnings

⚠️ **IMPORTANT SAFETY INFORMATION** ⚠️

- **Backup your saves**: Always maintain backups of your save files
- **Use at your own risk**: This mod modifies game behavior and data
- **Anti-cheat**: Some games have anti-cheat systems - be cautious
- **Save corruption**: Bugs in the mod could corrupt save files
- **Online features**: Don't use with games that have online anti-cheat

**Recommended**: Test on a separate save file/profile first!

## Contributing

When contributing to the mod:

1. Follow the existing code style (see `.clang-format` if available)
2. Add detailed comments for game-specific discoveries
3. Mark incomplete code with `// TODO:`
4. Test thoroughly before submitting PRs
5. Document any new console commands
6. Update this README with new information

## Resources

- [UE4SS Documentation](https://docs.ue4ss.com/)
- [UE4SS Modding Guide](https://docs.ue4ss.com/guides/creating-a-c++-mod.html)
- [Archipelago Protocol Docs](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md)
- [apclient C++ Library](https://github.com/black-sliver/apclientpp)

## License

TBD - To be determined by repository owner
