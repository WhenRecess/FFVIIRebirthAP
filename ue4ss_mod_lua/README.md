# FFVII Rebirth Archipelago - Lua Mod

A UE4SS Lua mod that connects Final Fantasy VII: Rebirth to Archipelago multiworld randomizer.

## Overview

This mod provides:
- **Archipelago Client**: Connects to AP servers via WebSocket
- **Item Handling**: Receives items from other players and grants them in-game
- **Location Tracking**: Detects completed locations and sends checks to server
- **DeathLink**: Optional shared death functionality
- **Console Commands**: In-game commands for connection management

## Requirements

- **UE4SS** v3.0.0 or later with Lua support
- **Final Fantasy VII: Rebirth** (PC/Steam version)
- An **Archipelago** server with FFVII:R world

## Installation

### 1. Install UE4SS

1. Download UE4SS from [GitHub Releases](https://github.com/UE4SS-RE/RE-UE4SS/releases)
2. Extract to your game directory:
   ```
   <Steam>/steamapps/common/FINAL FANTASY VII REBIRTH/Binaries/Win64/
   ```
3. Launch the game once to verify UE4SS console appears

### 2. Install This Mod

1. Copy the `FFVIIRebirthAP` folder to UE4SS mods directory:
   ```
   <Game>/Binaries/Win64/Mods/FFVIIRebirthAP/
   ```

2. Your folder structure should look like:
   ```
   Mods/
   └── FFVIIRebirthAP/
       ├── enabled.txt
       └── Scripts/
           ├── main.lua
           ├── APClient.lua
           ├── GameState.lua
           ├── ItemHandler.lua
           └── json.lua
   ```

3. The `enabled.txt` file tells UE4SS to load this mod

### 3. Generate a Multiworld

1. Install the FFVII:R APWorld in Archipelago
2. Create a YAML config file
3. Generate a multiworld seed
4. Host or connect to a server

## Usage

### Console Commands

Open the UE4SS console (usually `~` key) and use these commands:

| Command | Description |
|---------|-------------|
| `/ap help` | Show all commands |
| `/ap connect <server> <slot> [pass]` | Connect to AP server |
| `/ap disconnect` | Disconnect from server |
| `/ap status` | Show connection status |
| `/ap deathlink [on\|off]` | Toggle DeathLink |
| `/ap items` | List received items |
| `/ap locations` | List checked locations |
| `/ap debug [on\|off]` | Toggle debug logging |
| `/ap test` | Run diagnostics |

### Example Connection

```
/ap connect archipelago.gg:38281 MySlotName
```

Or for a local server:
```
/ap connect localhost:38281 Player1 password123
```

## Development Status

⚠️ **This mod is a work in progress!** ⚠️

### Implemented
- [x] Archipelago protocol client
- [x] WebSocket communication
- [x] Item receiving framework
- [x] Location check framework
- [x] DeathLink support
- [x] Console commands

### TODO (Needs Game Research)
- [ ] Actual item granting (inventory modification)
- [ ] Location detection (quest/chest/battle hooks)
- [ ] Death detection
- [ ] Goal completion detection
- [ ] Save file integration

## Architecture

```
main.lua          - Entry point, tick loop, commands
├── APClient.lua  - Archipelago server communication
├── GameState.lua - Game state detection and hooks
├── ItemHandler.lua - Item mapping and granting
└── json.lua      - JSON encode/decode
```

### Flow

1. `main.lua` initializes all modules on mod load
2. Every tick, it polls the AP client for messages
3. When items are received, `ItemHandler` grants them
4. `GameState` scans for completed locations
5. New locations are sent to server via `APClient`

## Customization

### Item Mapping

Edit `ItemHandler.lua` to map AP item names to game item IDs:

```lua
local ItemNameToGameId = {
    ["Fire Materia"] = 1001,  -- Game's internal ID for Fire
    ["Potion"] = 4001,
    -- Add more mappings...
}
```

### Location Hooks

Edit `GameState.lua` to add hooks for location detection:

```lua
-- Hook quest completion
RegisterHook("/Script/FFVII.QuestManager:OnQuestComplete", function(Context, QuestId)
    GameState.MarkLocationChecked(QuestId:get())
end)
```

## Testing the Mod Loads

### Step 1: Verify UE4SS Installation

1. Navigate to your game directory:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY VII REBIRTH\End\Binaries\Win64\
   ```
   (Path may vary based on your Steam library location)

2. Verify these UE4SS files exist:
   ```
   Win64/
   ├── dwmapi.dll              (or xinput1_3.dll - the UE4SS loader)
   ├── UE4SS.dll
   ├── UE4SS-settings.ini
   └── Mods/
       └── shared/
           └── Types.lua
   ```

3. Edit `UE4SS-settings.ini` to enable the console:
   ```ini
   [General]
   GuiConsoleEnabled = 1
   GuiConsoleVisible = 1
   
   [Debug]
   ConsoleEnabled = 1
   GuiConsoleEnabled = 1
   ```

### Step 2: Install the Archipelago Mod

1. Create the mod folder:
   ```
   Win64/Mods/FFVIIRebirthAP/
   ```

2. Copy files from this repo:
   ```
   FFVIIRebirthAP/
   ├── enabled.txt
   └── Scripts/
       ├── main.lua
       ├── APClient.lua
       ├── GameState.lua
       ├── ItemHandler.lua
       └── json.lua
   ```

### Step 3: Launch and Verify

1. Launch FFVII Rebirth through Steam

2. The UE4SS console window should appear (separate window or overlay)

3. Look for these messages in the console:
   ```
   [FFVIIRebirthAP] ===========================================
   [FFVIIRebirthAP]   FFVIIRebirthAP v0.1.0
   [FFVIIRebirthAP]   Final Fantasy VII: Rebirth x Archipelago
   [FFVIIRebirthAP] ===========================================
   [FFVIIRebirthAP] Mod initialized! Use /ap help for commands.
   ```

4. Test the commands work:
   ```
   /ap help
   /ap test
   ```

### Step 4: Check for Errors

If the mod doesn't load, check:

1. **UE4SS.log** in the Win64 folder:
   ```
   Look for: "Starting Lua mod 'FFVIIRebirthAP'"
   Errors will show: "Error loading mod" or Lua syntax errors
   ```

2. **Common Issues**:
   - Missing `enabled.txt` → Mod won't load
   - Lua syntax error → Check console for line numbers
   - Wrong folder structure → Must be `Mods/FFVIIRebirthAP/Scripts/main.lua`

---

## Researching Game Hooks with UE4SS

UE4SS provides powerful tools for reverse engineering Unreal Engine games. Here's how to find the hooks we need.

### Step 1: Generate Object Dump

1. In the UE4SS console, run:
   ```
   dumpallobjects
   ```
   This creates `Win64/UE4SS_ObjectDump.txt` (can be 100MB+)

2. Alternative - dump only specific types:
   ```
   dumpinstances UObject
   dumpinstances AActor
   ```

### Step 2: Find Game-Specific Classes

Open `UE4SS_ObjectDump.txt` and search for keywords:

**For Inventory/Items:**
```
Search for: Inventory, Item, Equipment, Materia, Weapon, Armor
Look for classes like:
- UInventoryComponent
- AItemActor
- UMateriaData
- UEquipmentManager
```

**For Quests:**
```
Search for: Quest, Mission, Objective, Task, Story
Look for classes like:
- UQuestManager
- AQuestActor
- UMissionData
```

**For Battle/Combat:**
```
Search for: Battle, Combat, Enemy, Damage, Health, Death
Look for classes like:
- UBattleManager
- UCombatComponent
- UHealthComponent
```

### Step 3: Use Live View (GUI)

1. Enable GUI in `UE4SS-settings.ini`:
   ```ini
   [General]
   EnableHotReloadSystem = 1
   
   [LiveView]
   LiveViewEnabled = 1
   ```

2. Press the UE4SS GUI hotkey (default: F10) in-game

3. Use **Live View** tab to:
   - Browse all loaded objects in real-time
   - Search for specific class names
   - Inspect object properties
   - Watch values change during gameplay

### Step 4: Find Function Signatures

1. Generate CXX headers:
   ```
   generatecxxheaders
   ```
   Creates `Win64/CXXHeaderDump/` with C++ headers for all classes

2. Open relevant headers and look for:
   - Virtual functions (can be hooked)
   - Blueprint-callable functions (UFUNCTION)
   - Delegate/event properties

3. Example - finding quest completion:
   ```cpp
   // In QuestManager.hpp, look for:
   UFUNCTION(BlueprintCallable)
   void CompleteQuest(FName QuestID);
   
   // Or delegate:
   UPROPERTY(BlueprintAssignable)
   FOnQuestCompleted OnQuestCompleted;
   ```

### Step 5: Hook Functions in Lua

Once you find a function, hook it in `GameState.lua`:

```lua
-- Hook a function by path
RegisterHook("/Script/FFVII.QuestManager:CompleteQuest", function(Context, QuestID)
    local questName = QuestID:get():ToString()
    print("[GameState] Quest completed: " .. questName)
    GameState.MarkLocationChecked(questName)
end)

-- Hook with pre/post execution
RegisterHook("/Script/FFVII.ItemManager:AddItem", function(Context, ItemID, Quantity)
    print(string.format("[GameState] Item added: %d x%d", ItemID:get(), Quantity:get()))
end)
```

### Step 6: Key Objects to Find

For the Archipelago mod, search for these patterns:

| What We Need | Search Terms | Likely Class Names |
|--------------|--------------|-------------------|
| Item pickup | `AddItem`, `PickupItem`, `GiveItem` | `UInventoryComponent`, `APickupActor` |
| Quest complete | `CompleteQuest`, `QuestFinish` | `UQuestManager`, `UMissionManager` |
| Chest opened | `OpenChest`, `TreasureBox`, `Loot` | `ATreasureBoxActor` |
| Battle won | `BattleEnd`, `Victory`, `EnemyDefeated` | `UBattleManager` |
| Player death | `PlayerDeath`, `GameOver`, `PartyWipe` | `UGameOverManager` |
| Map/Area | `LevelChange`, `AreaEnter`, `WorldMap` | `ULevelStreamingManager` |

### Step 7: Example Research Session

```
1. Launch game, load a save
2. Open UE4SS GUI (F10)
3. Go to Live View tab
4. Search: "Quest"
5. Find: UQuestManager object
6. Expand properties, find: ActiveQuests array
7. Complete a quest in-game
8. Watch the array change in Live View
9. Note the function that was called
10. Add hook in Lua mod
```

### Step 8: Save Your Research

Create a file `ue4ss_mod_lua/RESEARCH.md` to document:
- Class names you found
- Function signatures
- Memory offsets (if any)
- Working hooks

---

## Troubleshooting

### Mod Not Loading
- Check that `enabled.txt` exists in the mod folder
- Verify UE4SS is loading (console should appear)
- Check UE4SS.log for errors

### Can't Connect to Server
- Verify server address and port
- Check if WebSocket is available (`/ap test`)
- Try `ws://` prefix for local, `wss://` for archipelago.gg

### Items Not Being Granted
- Item mapping may be incomplete
- Check console for error messages
- Use `/ap debug on` for detailed logging

### UE4SS GUI Not Opening
- Try different hotkeys: F10, Insert, or check settings
- Make sure `GuiConsoleEnabled = 1` in settings
- Some games block overlays - try windowed mode

---

## Contributing

This mod needs help with:
1. Reverse engineering FFVII:R's memory structures
2. Finding function hooks for events
3. Mapping item IDs to AP items
4. Testing and bug reports

## License

MIT License - See repository root for details.

## Credits

- [Archipelago](https://archipelago.gg) - Multiworld framework
- [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) - Unreal modding
- [rxi/json.lua](https://github.com/rxi/json.lua) - JSON library
