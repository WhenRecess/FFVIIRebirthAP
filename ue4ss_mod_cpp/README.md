# FFVII Rebirth Archipelago - UE4SS C++ Mod

A C++ mod for UE4SS that enables item granting in Final Fantasy VII Rebirth for the Archipelago multiworld randomizer.

## Why C++ Instead of Lua?

Through extensive testing, we discovered that the Lua APIs available in UE4SS for FF7R (like `GetItemNumBP`, `SetResidentWorkInteger`) are:

- **Read-only** or disconnected from the live game state
- Unable to actually grant items to the player

The [LiesOfAP](https://github.com/Coookei/LiesOfAP) project (Lies of P Archipelago mod) demonstrated that using C++ with UE4SS allows:

- **Direct ProcessEvent calls** to game functions
- **Runtime function enumeration** on game objects
- **Discovery of Blueprint functions** not exposed through simple APIs

This mod follows that proven pattern.

## Prerequisites

1. **UE4SS Source (RE-UE4SS)**

   ```bash
   cd ..
   git clone https://github.com/UE4SS-RE/RE-UE4SS.git
   cd RE-UE4SS
   git submodule update --init --recursive
   ```

2. **xmake** (build system)

   ```
   winget install xmake
   ```

   Or download from https://xmake.io/

3. **Visual Studio 2022** (for C++ compiler)

## Building

```bash
cd ue4ss_mod_cpp
xmake build
```

The DLL will be built to `build/windows/x64/release/FFVIIRebirthAP.dll`

## Installation

1. Ensure UE4SS is installed in your FF7R installation
2. Create folder: `<FF7R Install>/End/Binaries/Win64/Mods/FFVIIRebirthAP/dlls/`
3. Copy `FFVIIRebirthAP.dll` to the `dlls/` folder
4. Create `enabled.txt` in `Mods/FFVIIRebirthAP/`

## Usage

Once loaded, open the UE4SS console (default: F10) and use these commands:

| Command              | Description                            |
| -------------------- | -------------------------------------- |
| `ap_help`            | Show available commands                |
| `ap_status`          | Check if game is loaded                |
| `ap_test`            | Run item grant tests                   |
| `ap_enum_player`     | List all functions on player character |
| `ap_enum_api`        | List all functions on API objects      |
| `ap_give <name>`     | Try to give item by name               |
| `ap_give_id <id>`    | Try to give item by numeric ID         |
| `ap_findall <class>` | Find all objects of a class            |

## Development Workflow

### Step 1: Discovery

Run `ap_enum_player` and `ap_enum_api` to find available functions in the game.
Look for functions containing: `Item`, `Gain`, `Give`, `Add`, `Receive`, `Reward`

### Step 2: Testing

Use `ap_give` and `ap_give_id` to test calling discovered functions.

### Step 3: Implementation

Once a working function is found, update `GameData.cpp` to use it properly.

## Architecture

```
ue4ss_mod_cpp/
├── dllmain.cpp           # UE4SS mod entry point, console commands
├── include/
│   └── GameData.hpp      # Game interaction interface
├── src/
│   └── GameData.cpp      # Item granting implementation
└── xmake.lua             # Build configuration
```

### Key Classes/Functions

- `UObjectGlobals::FindAllOf()` - Find all instances of a class
- `UObject::GetFunctionByNameInChain()` - Get a UFunction by name
- `UObject::ProcessEvent()` - Call a UFunction on an object
- `UClass::ForEachFunctionInChain()` - Iterate all functions on a class

## Target API Objects

Based on CXX header analysis, these are likely useful:

- `EndDataBaseDataBaseAPI` - Item database access
- `EndFieldAPI` - Field/overworld interactions
- `EndMenuAPI` / `EndMenuBPAPI` - Menu system
- `EndPartyAPI` - Party management
- `EndBattleAPI` - Battle system

## Item Categories (from game data)

| Category    | ID Range         | Examples        |
| ----------- | ---------------- | --------------- |
| Consumables | 4000001-40999999 | Potions, Ethers |
| Weapons     | 1000001-1999999  | Swords, Staffs  |
| Armor       | 2000001-2999999  | Armlets         |
| Accessories | 3000001-3999999  | Rings, Earrings |
| Materia     | 5000001-5999999  | Magic, Support  |

## Resources

- [UE4SS Documentation](https://docs.ue4ss.com/)
- [RE-UE4SS GitHub](https://github.com/UE4SS-RE/RE-UE4SS)
- [LiesOfAP (reference implementation)](https://github.com/Coookei/LiesOfAP)
- [Archipelago](https://archipelago.gg/)

## License

See main project LICENSE file.
