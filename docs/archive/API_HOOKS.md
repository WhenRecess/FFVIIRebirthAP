# FFVII Rebirth API Hooks for Archipelago

This document details the game APIs discovered through UE4SS Live View analysis and how they're used in the Archipelago mod.

## Core API Classes

### EndDataBaseDataBaseAPI
**Location:** `/Script/EndDataBase.EndDataBaseDataBaseAPI`  
**Purpose:** Core data access for items, flags, work variables, and game state.

| Function | Purpose | Status |
|----------|---------|--------|
| `GetItemNumBP(itemId)` | Get count of item in inventory | ✅ Integrated |
| `IsStoryFlag(flagName)` | Check if story flag is set | ✅ Integrated |
| `SetStoryFlagBP(flagName, value)` | Set story flag | ✅ Integrated |
| `GetResidentWorkInteger(workId)` | Get persistent save variable | ✅ Integrated |
| `SetResidentWorkInteger(workId, value)` | Set persistent save variable | ✅ Integrated |
| `GetResidentWorkFloat(workId)` | Get persistent float variable | 🔧 Available |
| `SetResidentWorkFloat(workId, value)` | Set persistent float variable | 🔧 Available |
| `GetLocationWorkInteger(workId)` | Get area-specific variable | ✅ Integrated |
| `SetLocationWorkInteger(workId, value)` | Set area-specific variable | 🔧 Available |
| `GetChapterProgress()` | Get current chapter number | ✅ Integrated |
| `GetPlayerPosition()` | Get player world position | ✅ Integrated |
| `GetPlayerRotation()` | Get player rotation | 🔧 Available |
| `EnemyBook_IncrementKillCount_BP(enemyId)` | Called when enemy killed | 🔧 Hook candidate |
| `SetDefaultBattleLeaderTypeBP(type)` | Set default party leader | 🔧 Available |
| `SetDefaultPartyLeaderTypeBP(type)` | Set default party leader | 🔧 Available |

### EndMenuBPAPI
**Location:** `/Script/EndGame.EndMenuBPAPI`  
**Purpose:** Player stats access and modification.

| Function | Purpose | Status |
|----------|---------|--------|
| `BPGetPlayerHP(playerType)` | Get character HP | ✅ Integrated |
| `BPGetPlayerHPMax(playerType)` | Get character max HP | ✅ Integrated |
| `BPSetPlayerHP(playerType, hp)` | Set character HP | ✅ Integrated (DeathLink) |
| `BPGetPlayerMP(playerType)` | Get character MP | 🔧 Available |
| `BPSetPlayerMP(playerType, mp)` | Set character MP | 🔧 Available |
| `BPGetPlayerLevel(playerType)` | Get character level | ✅ Integrated |
| `BPSetPlayerLevel(playerType, level)` | Set character level | 🔧 Available |
| `BPGetPlayerExperience(playerType)` | Get character EXP | 🔧 Available |
| `BPSetPlayerExperience(playerType, exp)` | Set character EXP | 🔧 Available |

**Player Types:**
- 0 = Cloud
- 1 = Barret
- 2 = Tifa
- 3 = Aerith
- 4 = Red XIII
- 5 = Yuffie
- 6 = Cait Sith
- 7 = Cid
- 8 = Vincent

### EndBattleAPI
**Location:** `/Script/EndGame.EndBattleAPI`  
**Purpose:** Battle system control and events.

| Function | Purpose | Status |
|----------|---------|--------|
| `GetStoryFlagConditionNum(...)` | Check story flags in battle | 🔧 Available |
| `SetStoryFlagCondition(...)` | Set story flags from battle | 🔧 Available |
| `GetPartyLeader()` | Get current battle leader | 🔧 Available |
| `SetPartyLeader(...)` | Change battle leader | 🔧 Available |
| `IsInBattle()` | Check if in battle | 🔧 Hook candidate |
| `GameOverForce()` | Force game over | 🔧 DeathLink alternative |

### EndPartyAPI
**Location:** `/Script/EndGame.EndPartyAPI`  
**Purpose:** Party management.

| Function | Purpose | Status |
|----------|---------|--------|
| `GetAliveBattleMemberCount()` | Count living party members | ✅ Integrated (Death detect) |
| `GetAllPartyMemberCount()` | Get total party size | 🔧 Available |
| `GetBattleMemberCount()` | Get active battle party size | 🔧 Available |
| `GetPartyLeaderType()` | Get current leader | 🔧 Available |

### EndFieldAPI
**Location:** `/Script/EndGame.EndFieldAPI`  
**Purpose:** Field/map events and triggers.

| Function | Purpose | Status |
|----------|---------|--------|
| `ChangeChapter(...)` | Change game chapter | 🔧 Available |
| `IsDuringBattle()` | Check battle state | 🔧 Available |
| `SendStateTrigger(...)` | Trigger game events | 🔧 Potential use |

---

## Item System (Updated from Raw Dump Analysis)

### Key Discovery: Items Use NameProperty Strings

Based on analysis of the UE4SS raw dump (412K+ lines), items are stored using **NameProperty strings**, NOT integer IDs.

#### EndDataTableItem Structure
```
EndDataTableItem:UniqueId (NameProperty)     // Item identifier string
EndDataTableItem:ItemCategory (Int8Property)  // Category enum
EndDataTableItem:MaxCount (Int16Property)     // Max stack size
```

#### EndDataTableInventoryList Structure
```
EndDataTableInventoryList:Type (EnumProperty)     // Item type enum
EndDataTableInventoryList:TableID (NameProperty)  // Links to DataTable item
EndDataTableInventoryList:IsStack (BoolProperty)  // Can stack?
```

#### EndDataTableMateria Structure
```
EndDataTableMateria:UniqueId (NameProperty)
EndDataTableMateria:Level (Int8Property)
EndDataTableMateria:AP (Int32Property)
EndDataTableMateria:Attack (Int16Property)
EndDataTableMateria:Magic (Int16Property)
// ... additional stats
```

### Item Name Patterns (NEEDS VERIFICATION)

The exact format needs in-game testing, but likely follows:
- Consumables: `ITEM_POTION`, `ITEM_HI_POTION`, `ITEM_ETHER`, etc.
- Materia: `MAT_FIRE`, `MAT_BLIZZARD`, `MAT_CURE`, etc.
- Equipment: `WEAPON_BUSTER_SWORD`, `ARMOR_BRONZE_BANGLE`, etc.
- Key Items: Controlled via StoryFlags

### Treasure Chests

From the dump analysis:
```
EndObjectTreasure:StoryFlagName (NameProperty)  // Flag that tracks if chest opened
```

This means chest states are controlled by StoryFlags, which we can read/write via:
- `IsStoryFlag(flagName)` - Check if chest was opened
- `SetStoryFlagBP(flagName, true)` - Mark chest as opened

### Quest Completion

From EndDataTableQuest structure:
```
EndDataTableQuest:CompleteStoryFlag (NameProperty)  // Flag set on completion
EndDataTableQuest:AcceptedStoryFlag (NameProperty)  // Flag set on acceptance
```

### Debug Commands

Use these in-game via UE4SS console to determine actual formats:
```
/ap testapi        -- Tests all API functions with various name formats
/ap testitem Potion  -- Test granting an item by name
/ap dumpmappings   -- Show current item name mappings
```

---

## Research Still Needed

### Variable Name Verification
The exact naming convention needs in-game testing:
1. Run `/ap testapi` with game loaded
2. Check which `GetItemNumBP()` calls succeed
3. Check which `GetResidentWorkInteger()` calls return valid values

### Gil Variable Name
Need to find the correct work variable name for Gil:
- Try: `GIL`, `Gil`, `MONEY`, `Money`, `PLAYER_GIL`, `PlayerGil`
- The `/ap testapi` command tests all these

### Key Item Flag Names
Need to capture actual flag names from:
- EndDataTableQuest entries
- EndObjectTreasure entries
- Story progression flags

---

## UE4SS Hook Registration

For real-time event detection, use:

```lua
RegisterHook("/Script/Module.Class:FunctionName", function(Context, ...)
    -- Called when function is invoked
end)
```

### Recommended Hooks

```lua
-- Battle end (for enemy defeat checks)
RegisterHook("/Script/EndGame.EndBattleAPI:OnExitBattleScene", function(Context)
    -- Check for location completions
end)

-- Enemy kill tracking
RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:EnemyBook_IncrementKillCount_BP", function(Context, EnemyId)
    -- Track enemy defeats
end)

-- Item pickup (if found)
-- RegisterHook("/Script/EndGame.???:OnItemPickup", function(Context, ItemId)
--     -- Track item acquisitions
-- end)
```

---

## Status Legend
- ✅ Integrated - Implemented in mod code
- 🔧 Available - Found and ready to use
- ❓ Unknown - Needs research
- ⚠️ Risky - May cause issues

## Files
- [GameState.lua](../ue4ss_mod_lua/Scripts/GameState.lua) - Game state reading/writing
- [ItemHandler.lua](../ue4ss_mod_lua/Scripts/ItemHandler.lua) - Item granting
- [filtered_output.txt](../filtered_output.txt) - Full filtered API list
