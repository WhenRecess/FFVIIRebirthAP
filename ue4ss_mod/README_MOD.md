# FFVIIRebirthAP UE4SS Mod - Build and Installation Guide

This directory contains the UE4SS mod for Final Fantasy VII: Rebirth Archipelago integration.

## Prerequisites

### Required Tools
- [xmake](https://xmake.io/) - Build system
- C++20 compatible compiler (MSVC 2019+, GCC 10+, or Clang 11+)
- [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) - Unreal Engine scripting system

### Required Libraries (To Be Obtained Separately)
- **UE4SS SDK**: Headers and libraries from UE4SS project
- **APClient Library**: C++ Archipelago client library ([apcpp](https://github.com/black-sliver/apcpp) or similar)
- **cacert.pem**: SSL certificate file for HTTPS connections

## Building the Mod

### 1. Set Up Dependencies

Before building, you need to:

1. Download and install UE4SS from https://github.com/UE4SS-RE/RE-UE4SS
2. Obtain the apclient C++ library (e.g., from https://github.com/black-sliver/apcpp)
3. Download `cacert.pem` from https://curl.se/docs/caextract.html

### 2. Configure Build Paths

Edit `xmake.lua` to add the correct paths for:
- UE4SS SDK include directories
- APClient library include directories  
- APClient library link directories

Example modifications to `xmake.lua`:
```lua
-- Add UE4SS SDK includes
add_includedirs("C:/path/to/UE4SS/SDK/include")

-- Add APClient includes and libs
add_includedirs("C:/path/to/apclient/include")
add_linkdirs("C:/path/to/apclient/lib")
add_links("apclient")
```

### 3. Build with xmake

```bash
# Navigate to the ue4ss_mod directory
cd ue4ss_mod

# Build in release mode (recommended)
xmake f -m release
xmake

# Or build in debug mode for development
xmake f -m debug
xmake
```

The compiled DLL will be in `build/bin/FFVIIRebirthAP.dll`

## Installation

### 1. Install UE4SS

1. Download the latest UE4SS release for your game version
2. Extract UE4SS to your game directory (where the .exe is located)
3. Verify UE4SS works by launching the game - you should see a console window

### 2. Install the Mod

1. Copy `build/bin/FFVIIRebirthAP.dll` to `<GameDirectory>/Mods/FFVIIRebirthAP/`
2. Create a `enabled.txt` file in the same directory
3. Copy `cacert.pem` to `<GameDirectory>/Mods/FFVIIRebirthAP/`

Your mod directory structure should look like:
```
GameDirectory/
├── FF7Rebirth.exe (or similar)
├── UE4SS.dll
├── Mods/
│   └── FFVIIRebirthAP/
│       ├── FFVIIRebirthAP.dll
│       ├── enabled.txt
│       └── cacert.pem
```

### 3. Verify Installation

1. Launch the game
2. Open the UE4SS console (usually by pressing `)
3. You should see log messages from `[FFVIIRebirthAP]` indicating the mod loaded
4. Available console commands should be listed

## Usage

### Connecting to Archipelago

In the game console, use the `/connect` command:
```
/connect archipelago.gg:38281 YourSlotName [password]
```

Example:
```
/connect archipelago.gg:38281 Player1
/connect myserver.com:38281 Player1 mypassword
```

### Console Commands

- `/connect <server> <slot> [password]` - Connect to an Archipelago server
- `/deathlink [on|off]` - Enable or disable DeathLink
- `/ap-replace <territory> <slot> <template>` - Replace an enemy template (for testing)

### Tips

- The mod automatically checks for location clears and sends them to the server
- Items received from the server will be added to your inventory
- Connection status is displayed in the console

## Important Warnings

⚠️ **Back Up Your Saves**: Always back up your save files before using mods. Mods can potentially corrupt saves.

⚠️ **Anti-Cheat**: Some games have anti-cheat systems that may detect mods. Use at your own risk. This mod is intended for single-player randomizer purposes.

⚠️ **Game Updates**: Game updates may break the mod. Check for mod updates after game patches.

⚠️ **Work in Progress**: This is scaffold code. Many features are marked TODO and require implementation.

## Troubleshooting

### Mod doesn't load
- Check that UE4SS is installed correctly
- Verify `enabled.txt` exists in the mod directory
- Check UE4SS console for error messages

### Connection fails
- Verify `cacert.pem` is in the mod directory
- Check that the server address is correct
- Ensure your firewall allows the connection

### Items not received
- Verify you're connected to the server (`/connect` command)
- Check the console for error messages
- Make sure the APClient library is properly linked

## Development

### Implementing Game-Specific Logic

The following areas need implementation:

1. **GameData.cpp**: 
   - `IsLoaded()`: Detect when game is ready
   - `GetCurrentMap()`: Read current level
   - `CheckEncounterSpots()`: Detect location checks
   - `ReceiveItem()`: Add items to inventory
   - `ReplaceEnemyTemplate()`: Modify enemy spawns

2. **Client.cpp**:
   - Link against actual APClient library
   - Implement all TODO sections
   - Handle connection callbacks

3. **dllmain.cpp**:
   - Integrate with UE4SS CppUserModBase
   - Register proper console command handlers
   - Hook game events (BeginPlay, etc.)

### Adding UE4SS Integration

Once UE4SS SDK is available:

1. Include UE4SS headers in `xmake.lua`
2. Inherit from `RC::CppUserModBase` in `dllmain.cpp`
3. Use UE4SS logging: `RC::Output::send<RC::LogLevel::Verbose>(STR("message"))`
4. Register hooks with `register_hook<UObject>()`

### Debugging

Build in debug mode for better debugging:
```bash
xmake f -m debug
xmake
```

Use console output for debugging:
```cpp
GameData::PrintToConsole("Debug: %s", value.c_str());
```

## Resources

- [UE4SS Documentation](https://docs.ue4ss.com/)
- [Archipelago Documentation](https://archipelago.gg/tutorial/)
- [APClient Library](https://github.com/black-sliver/apcpp)
- [xmake Documentation](https://xmake.io/#/guide/installation)

## Contributing

Contributions are welcome! Focus areas:
- Implementing game-specific hooks
- Testing with actual game data
- Performance optimization
- Error handling improvements
