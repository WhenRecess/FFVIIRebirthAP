# FF7 Rebirth Randomization: Detailed Technical Analysis

## What We Know About The Game

### Memory Architecture
```
CE AOB Pattern: 458B????442B????4489
Injection Point: mov [binven_ptr],r14

Runtime pointer structure (changes per launch):
  binven_ptr → Base Pointer (e.g., 0x7FF7F8940AB8)
    Base + 0x8  → Item ID (4 bytes)
    Base + 0xC  → Item Quantity (4 bytes)
```

**Key Discovery:** The CE script uses **code injection** to capture the pointer when the game accesses inventory. Our external tool (MemoryBridge.exe) **cannot** replicate this - we need the CE script running or manual pointer entry.

### Game APIs Available (from GameState.lua)
```lua
EndDataBaseDataBaseAPI:
  - GetItemNumBP(itemId) → Read item count
  - AddItemBP(itemId, quantity) → Grant item (if available)
  - IsStoryFlag(flagId) → Check story progression
  - SetStoryFlagBP(flagId, value) → Set flags
  - GetResidentWorkInteger(varId) → Read game variables

EndBattleAPI:
  - Battle state tracking (if accessible)

EndMenuBPAPI:
  - Player stats (HP, MP, level, etc.)
```

**Critical Limitation:** We haven't confirmed if `AddItemBP` is actually callable from UE4SS Lua. If it is, this changes everything.

### UE4SS Limitations
- ❌ No socket library → Can't do HTTP directly
- ✅ File I/O works → File-based IPC functional
- ✅ Can call game APIs via `StaticFindObject`
- ❌ Cannot inject ASM code (like CE does)
- ❓ Unknown if we can hook functions with `RegisterHook`

---

## Option 1: Memory Watching + Compensation

### How It Actually Works
```
1. Player opens chest in-game
2. Game's code executes: AddItemBP(100, 1)  // Gives Potion
3. Potion appears in inventory (count increases)
4. LocationTracker.lua polls every 500ms:
   - Detects inventory count changed for item 100
   - Cross-references with player position/story state
   - Identifies: "This was Grasslands_Chest_05"
5. Writes to ap_checked_locations.txt: "770002005"
6. AP bridge reads file, tells server "checked 770002005"
7. Server responds: "You get Ether from Player2's world"
8. Lua mod writes to requests.txt: {"id":111,"qty":1}
9. Memory Bridge grants Ether
10. Memory Bridge REMOVES the Potion: WriteMemory(qty_addr, 0)
```

### Technical Requirements

**✅ What We Have:**
- Read inventory counts: `GameState.GetItemCount(itemId)`
- Grant items: Memory Bridge working
- File IPC: Proven functional

**❌ What We Need:**
- **Item removal capability** in Memory Bridge
- **Position tracking** to identify which chest was opened
- **Timing logic** to correlate inventory changes with locations
- **State tracking** for shops, battles, story events

### Code Example (Item Removal)
```cpp
// In MemoryBridge.cpp
bool MemoryBridge::RemoveItem(int itemId, int quantity) {
    // Find item slot with matching ID
    for (int slot = 0; slot < MAX_INVENTORY_SLOTS; slot++) {
        uintptr_t slotAddr = GetInventorySlotAddress(slot);
        int currentId = ReadInt(slotAddr + 0x8);
        
        if (currentId == itemId) {
            int currentQty = ReadInt(slotAddr + 0xC);
            int newQty = max(0, currentQty - quantity);
            WriteInt(slotAddr + 0xC, newQty);
            return true;
        }
    }
    return false;
}
```

### Problems

**1. Multiple Inventory Slots**
The current pointer only tracks ONE slot (wherever you hover). To remove items, we need to:
- Scan entire inventory array
- Find all slots
- Modify the correct one

**2. Timing Window**
```
T+0ms:   Chest opens, Potion granted (count: 62→63)
T+250ms: LocationTracker polls, sees change
T+300ms: Sends to AP
T+500ms: AP responds with Ether
T+550ms: Grant Ether (count: 10→11)
T+600ms: Remove Potion (count: 63→62)
```
Player sees Potion for 600ms, then it disappears. **Immersion-breaking.**

**3. Location Detection Complexity**
```lua
-- How do we know which chest was just opened?
function DetermineChestLocation()
    local pos = GetPlayerPosition()
    
    -- Check all known chest coordinates
    for chest_key, chest_data in pairs(ChestDatabase) do
        if Distance(pos, chest_data.position) < 100 then
            -- But which chest at this position?
            -- Multiple chests can be nearby!
            -- Need to check which one's flag was just set
        end
    end
end
```

### Verdict on Option 1
**Feasibility: 6/10**
- ✅ Pro: No code injection needed
- ✅ Pro: We have all the pieces
- ❌ Con: Player sees wrong item briefly
- ❌ Con: Complex location detection
- ❌ Con: Need to track EVERYTHING (shops, battles, chests, story)
- ❌ Con: May miss fast events

---

## Option 2: Function Hooking (If Possible)

### How It Would Work
```lua
-- In UE4SS Lua
RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:AddItemBP", function(Context, ItemId, Quantity)
    print(string.format("[Hook] Game wants to give: %d x%d", ItemId, Quantity))
    
    -- Determine what location this is
    local location_key = DetermineLocationContext()
    
    if location_key and RandomizedItems[location_key] then
        local randomized = RandomizedItems[location_key]
        
        -- REPLACE the item ID before game processes it
        Context:SetItemId(randomized.item_id)
        
        print(string.format("[Hook] Replaced with: %s", randomized.item_name))
        
        -- Mark location checked
        CheckAPLocation(location_key)
    end
    
    -- Let the call proceed (with modified or original item)
    return true
end)
```

### Technical Requirements

**? Unknown if UE4SS Supports:**
- Can we use `RegisterHook` on Blueprint functions?
- Can we modify function parameters in the hook?
- Does hooking work reliably without crashing?

### Testing Approach
```lua
-- Simple test in main.lua
local success = pcall(function()
    RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:AddItemBP", function(...)
        print("[TEST] Hook triggered!")
        return true
    end)
end)

if success then
    print("Hooking is supported!")
else
    print("Hooking NOT supported")
end
```

### If Hooking Works

**Best Case Scenario:**
```
1. Chest opens
2. Game calls AddItemBP(100, 1)
3. Hook intercepts BEFORE item granted
4. Hook determines: "This is Grasslands_Chest_05"
5. Hook replaces: AddItemBP(111, 1) // Ether instead
6. Game grants Ether
7. Player only ever sees Ether - perfect!
```

**Challenges:**
- Still need to determine location context
- What if we can't tell which chest was opened?
- Shop purchases might be multiple calls in sequence

### Alternative: Use Game's Own AddItemBP

What if we don't hook, but use the API directly?
```lua
-- When location checked
local api = StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
if api and api.AddItemBP then
    -- Try calling the game's function
    api:AddItemBP(111, 1)  -- Give Ether
end
```

**If this works,** we can:
1. Let vanilla item be granted
2. Immediately call API to remove it: `api:AddItemBP(100, -1)`
3. Grant randomized item: `api:AddItemBP(111, 1)`

Much cleaner than memory manipulation!

### Verdict on Option 2
**Feasibility: ?/10 (NEEDS TESTING)**
- ❓ Unknown: Does RegisterHook work?
- ❓ Unknown: Can we call AddItemBP with negative quantity?
- ✅ Pro: If it works, cleanest solution
- ✅ Pro: No external Memory Bridge needed
- ❌ Con: If it doesn't work, wasted effort

**RECOMMENDATION: Test this FIRST before committing to Option 1**

---

## Option 3: Pre-Randomization via Save Editing

### How It Would Work
```
1. Player generates AP seed
2. Seed determines: "Grasslands_Chest_05 contains Ether"
3. Python script modifies save file:
   - Find chest_05 item entry
   - Change from item_id=100 to item_id=111
4. Player loads save
5. Game naturally gives Ether when chest opened
```

### Technical Requirements

**Need to Reverse Engineer:**
- Save file format (.sav or similar)
- Where chest contents are stored
- Checksum/validation (if any)
- Shop inventory structure
- Battle rewards table

### Research Approach
```python
# 1. Make clean save at start of game
save1 = read_binary("save_slot1.sav")

# 2. Open one chest in-game, save again
save2 = read_binary("save_slot1.sav")

# 3. Diff the saves
diff = find_differences(save1, save2)
# Look for: item count changes, flag bits

# 4. Hex edit save2 to change item
save2_modified = modify_at_offset(save2, diff_offset, new_item_id)

# 5. Load modified save, verify item changed
```

### Problems

**1. Item Placement Might Be Server-Side**
Some games store loot tables in game files, not saves:
- Chests might reference: `loot_table_id = 42`
- Loot table 42 is hardcoded in `.pak` files
- Modifying `.pak` files = complex, version-dependent

**2. Shops Are Probably Dynamic**
Shop inventory might be procedurally generated, not saved:
```cpp
// Game code (hypothetical)
void PopulateShop(int shop_id) {
    for (int slot = 0; slot < 10; slot++) {
        shop_items[slot] = ShopDatabase[shop_id][slot];
    }
}
```
Can't randomize what isn't in the save.

**3. Maintenance Nightmare**
Every game update could change:
- Save format
- Item IDs
- Memory offsets
- File structure

### Verdict on Option 3
**Feasibility: 3/10**
- ❌ Con: Requires extensive reverse engineering
- ❌ Con: Won't work for shops/dynamic content
- ❌ Con: Breaks on every game update
- ✅ Pro: Perfect player experience (if it works)
- ⏰ Con: Weeks/months of research

**RECOMMENDATION: Skip unless Options 1 & 2 fail**

---

## Recommended Path Forward

### Phase 1: CRITICAL TEST (30 minutes)
**Test if we can use game's AddItemBP function:**

```lua
-- Add to main.lua
local function TestGameAPI()
    local api = StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
    if not api then
        print("[TEST] API not found!")
        return
    end
    
    print("[TEST] Found API:", api:GetFullName())
    
    -- Test 1: Can we call AddItemBP?
    local success1 = pcall(function()
        api:AddItemBP(100, 1)  -- Give 1 Potion
    end)
    print("[TEST] AddItemBP callable:", success1)
    
    -- Test 2: Can we remove items with negative qty?
    local success2 = pcall(function()
        api:AddItemBP(100, -1)  -- Remove 1 Potion
    end)
    print("[TEST] Negative quantity:", success2)
    
    -- Test 3: Can we hook functions?
    local success3 = pcall(function()
        RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:AddItemBP", function(...)
            print("[TEST] Hook triggered!")
            return true
        end)
    end)
    print("[TEST] Hooking supported:", success3)
end

RegisterKeyBind(Key.F7, TestGameAPI)
```

### Phase 2: Choose Path Based on Results

**If AddItemBP + negative qty work:**
→ **Hybrid Approach:** Memory watching + API calls
- Watch for inventory changes (Option 1 detection)
- Remove vanilla item via API
- Grant randomized item via API
- NO Memory Bridge needed for granting!

**If Hooking works:**
→ **Option 2:** Full function hooking
- Intercept and replace items
- Cleanest solution

**If Neither work:**
→ **Option 1:** Memory watching + Memory Bridge
- Keep current system
- Add item removal to Memory Bridge
- Accept brief visual glitches

### Phase 3: Location Detection Strategy

**For Any Option, We Need:**
```lua
LocationDatabase = {
    -- Story flags
    story_flags = {
        [1003] = "Story_Chapter_3_Complete",
    },
    
    -- Chest positions
    chests = {
        {map="Grasslands", pos={x=1234, y=5678, z=100}, 
         flag=2001, id="Grasslands_Chest_05"},
    },
    
    -- Boss battles
    bosses = {
        ["BattleID_Midgardsormr"] = "Boss_Midgardsormr",
    },
    
    -- Shop purchases (track by transaction)
    shops = {
        -- Mark slot as "checked" on purchase
    },
}
```

**Detection Methods:**
1. **Story:** Poll ResidentWork variables
2. **Chests:** Player position + flag changes
3. **Bosses:** Battle completion hooks
4. **Shops:** Transaction count changes

---

## My Recommendation

**Start with Phase 1 API test.** This 30-minute test will determine everything:

- If API calls work → Simplest path (no Memory Bridge for items)
- If hooking works → Best quality path
- If neither → Stick with current Memory Bridge approach

**Do NOT invest time in save editing** until you've exhausted runtime options.

The test will answer: **"Can we use the game's own systems?"**

That's the key question.
