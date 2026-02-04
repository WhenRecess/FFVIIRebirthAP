# FF7 Rebirth Archipelago - Randomization Guide

## How Randomization Works

In Archipelago, **locations** contain randomized **items**. When you pick up an item in FF7 Rebirth, the game gives you a different item than what normally appears there.

### Example Flow

1. **Normal game**: Open chest in Grasslands → Get Potion
2. **Archipelago**: Open chest in Grasslands → Check "Grasslands Chest 01" location → Receive "Ether" (from someone else's world)

---

## Implementation Approaches

### Approach 1: Memory Watching (Current - In Progress)

**How it works:**
1. Lua mod watches game memory for events (item pickups, story flags, battles)
2. When event detected, write location ID to `ap_checked_locations.txt`
3. AP bridge reads file, tells server "checked location X"
4. Server responds with randomized item
5. Memory Bridge grants that item

**Pros:**
- No code injection needed
- Works with existing Memory Bridge

**Cons:**
- Player might briefly see/receive vanilla item
- Need to detect all types of events
- May require "item removal" feature

**Status:** ✅ Framework created ([LocationTracker.lua](ue4ss_mod_lua/Scripts/LocationTracker.lua))

---

### Approach 2: Function Hooking (Better Quality)

**How it works:**
1. Hook the game's internal `GiveItem()` function
2. When game tries to give item, intercept the call
3. Look up what AP randomized for this location
4. Give that item instead of vanilla

**Pros:**
- Clean, no visual glitches
- Item replacement happens instantly
- Works for all item sources (chests, shops, rewards)

**Cons:**
- Requires finding and hooking game functions
- More complex UE4SS scripting
- May break on game updates

**Implementation:**
```lua
-- In UE4SS Lua:
RegisterHook("/Script/End.EndDataBaseDataBaseAPI:AddItemBP", function(Context, ItemId, Quantity)
    local location_key = GetCurrentLocationContext()
    local randomized_item = LookupRandomizedItem(location_key)
    
    if randomized_item then
        -- Replace with randomized item
        Context:SetItemId(randomized_item)
        CheckAPLocation(location_key)
    end
end)
```

**Status:** ⏳ Not yet implemented

---

### Approach 3: Pre-Randomization (Cleanest)

**How it works:**
1. Generate AP seed, know all location→item mappings upfront
2. Modify game files or save data to place correct items
3. Game naturally gives correct items

**Pros:**
- Zero runtime overhead
- Perfect player experience
- No hooks or memory watching needed

**Cons:**
- Requires understanding save format
- May need to rebuild game data tables
- Complex to implement

**Status:** ❌ Requires reverse engineering

---

## Location Types to Track

### 1. Field Items (Chests, Pickups)

**Detection Method:**
- Watch inventory count changes
- Cross-reference with player position/map
- Hook `AddItemBP` function

**Example:**
```lua
-- Detect chest opened at specific coordinates
if player_position == "X:1234 Y:5678" and inventory_changed then
    CheckLocation("Grasslands_Chest_05")
end
```

---

### 2. Shop Purchases

**Detection Method:**
- Hook shop purchase UI
- Track gil spent + item received
- Mark shop slot as "checked"

**Challenge:** Each shop visit is randomized, so buying same item twice = 2 different checks

**Example:**
```lua
-- When buying from Kalm Shop
CheckLocation("Shop_Kalm_Slot_3")  -- 3rd item in stock
```

---

### 3. Battle Rewards (Boss Defeats, Colosseum)

**Detection Method:**
- Watch battle result screen
- Check battle ID from game memory
- Mark boss/battle as checked

**Example:**
```lua
-- After defeating Midgardsormr
if battle_id == "Boss_Midgardsormr" and battle_result == "Victory" then
    CheckLocation("Boss_Midgardsormr")
end
```

---

### 4. Story Progression

**Detection Method:**
- Watch story flags (ResidentWork variables)
- Trigger on chapter completion
- Trigger on specific cutscenes

**Example:**
```lua
-- Chapter 3 complete
if GetResidentWork(1003) == 1 then
    CheckLocation("Story_Chapter_3_Complete")
end
```

---

### 5. Quest Completions

**Detection Method:**
- Watch quest flags
- Trigger when quest marked complete
- May have multiple rewards per quest

**Example:**
```lua
if IsQuestComplete("Quest_Chocobo_Farm_01") then
    CheckLocation("Quest_Chocobo_Farm_01_Reward")
end
```

---

## Implementation Roadmap

### Phase 1: Manual Testing (Current)
- ✅ Memory Bridge grants items by ID
- ✅ Item mapping from CE table (578 items)
- ⏳ LocationTracker framework
- ⏳ AP bridge for server communication

### Phase 2: Basic Location Tracking
- ⏳ Story flag detection
- ⏳ Boss defeat detection
- ⏳ Manual location checking (press button to check)

### Phase 3: Automated Detection
- ⏳ Field item pickup detection
- ⏳ Shop purchase tracking
- ⏳ Battle reward tracking

### Phase 4: Function Hooking (Optional)
- ⏳ Hook `AddItemBP` function
- ⏳ Intercept and replace items
- ⏳ Remove vanilla items before granting

### Phase 5: Polish
- ⏳ UI notifications ("You found Ether from Player2!")
- ⏳ Save/load state persistence
- ⏳ Multi-world sync testing

---

## Key Files

### Location Definition
- **Python:** [location_tables.py](worlds/finalfantasy_rebirth/data/location_tables.py)
  - Defines all AP location names and IDs
  
### Location Detection
- **Lua:** [LocationTracker.lua](ue4ss_mod_lua/Scripts/LocationTracker.lua)
  - Watches game for location checks
  
- **Lua:** [GameState.lua](ue4ss_mod_lua/Scripts/GameState.lua)
  - Provides game memory reading APIs

### Item Granting
- **Python:** [item_mappings.py](worlds/finalfantasy_rebirth/item_mappings.py)
  - Maps item names → CE memory IDs
  
- **Lua:** [ItemHandler.lua](ue4ss_mod_lua/Scripts/ItemHandler.lua)
  - Resolves item names and grants via Memory Bridge

---

## Next Steps

1. **Map locations to game triggers**
   - Identify story flags for chapters
   - Find battle IDs for bosses
   - Map chest positions to location IDs

2. **Implement detection in LocationTracker.lua**
   - Use GameState.lua APIs to read flags
   - Watch for inventory changes
   - Test with manual checks

3. **Connect to AP server**
   - Complete [ap_file_bridge.py](worlds/finalfantasy_rebirth/ap_file_bridge.py)
   - Send checked locations to server
   - Receive randomized items

4. **Test end-to-end**
   - Generate AP seed
   - Check location in game
   - Verify correct item granted
