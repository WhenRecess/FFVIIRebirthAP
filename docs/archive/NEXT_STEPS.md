# Next Steps: Determine Best Randomization Approach

## What You Need To Do Now

### Step 1: Run The Test (5 minutes)

1. **Deploy the updated Lua files:**
   ```powershell
   Copy-Item "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\ue4ss_mod_lua\Scripts\*.lua" `
             -Destination "G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH\End\Binaries\Win64\Mods\FFVIIRebirthAP\Scripts\" `
             -Force
   ```

2. **Start the game with CE script running:**
   - Enable "Inventory/Item Control" in CE
   - Run `ce_pointer_writer.lua` in CE Lua Engine
   - Hover over an item once to populate pointer

3. **In-game, press F7**
   - This runs the complete API test suite
   - Results will print to UE4SS console

4. **Check your inventory before and after:**
   - Count your Potions before test
   - After F7, close/reopen inventory
   - Did Potion count change?

### Step 2: Read The Results

The test will tell you:

**✓ If this prints "YES":**
- `Add Items (AddItemBP): ✓ YES` → We can grant items via game API
- `Remove Items (negative qty): ✓ YES` → We can remove items via game API
- `RegisterHook supported: ✓ YES` → We can hook functions

**Then this approach is possible:**
- **BEST:** Hook AddItemBP, replace items cleanly (no glitches)
- **GOOD:** Use API to grant/remove, watch memory for detection
- **FALLBACK:** Current Memory Bridge approach

---

## The Three Options Explained

### Option 1: Memory Watching (Current Working Method)

**What it is:**
- Watch game memory for changes (inventory, flags, battles)
- When change detected, determine what location was checked
- Remove vanilla item via Memory Bridge
- Grant randomized item via Memory Bridge

**Pros:**
- ✅ Already partially working (Memory Bridge functional)
- ✅ No dependency on game APIs
- ✅ Can handle any event type

**Cons:**
- ❌ Player sees wrong item briefly (then it disappears)
- ❌ Complex detection logic needed
- ❌ Must track player position, story flags, battle state
- ❌ CE script must be running (for pointer)

**When to use:** If API tests fail

---

### Option 2: Function Hooking (If Tests Pass)

**What it is:**
- Hook the game's `AddItemBP` function
- When game tries to give item, intercept the call
- Replace item ID before it's granted
- Player only sees correct item

**Pros:**
- ✅ Perfect player experience (no glitches)
- ✅ Works for ALL item sources (chests, shops, battles, rewards)
- ✅ Automatic detection (we know context from hook)
- ✅ No Memory Bridge needed

**Cons:**
- ❓ Unknown if UE4SS supports this
- ❌ Still need location context (which chest?)
- ❌ May break on game updates

**When to use:** If F7 test shows "Hooking supported: ✓ YES"

---

### Option 3: Save File Editing (Research Project)

**What it is:**
- Pre-randomize: Know Chest #5 should contain Ether
- Modify save file to place Ether in Chest #5
- Game naturally gives correct item

**Pros:**
- ✅ Perfect experience
- ✅ No runtime code needed
- ✅ Works offline

**Cons:**
- ❌ Requires reverse engineering save format (weeks/months)
- ❌ Won't work for shops (dynamic)
- ❌ Breaks every game update
- ❌ Can't sync with other players in real-time

**When to use:** Never (unless you want a research project)

---

## Decision Tree

```
Run F7 Test
│
├─ "RegisterHook supported: YES" & "Modify parameters: YES"
│  └─> OPTION 2: Function Hooking ⭐ BEST
│
├─ "AddItemBP: YES" & "Negative quantity: YES"
│  └─> HYBRID: Memory Watching + API Calls ⭐ GOOD
│     (Watch for changes, use API to grant/remove)
│
├─ "AddItemBP: YES" but "Negative quantity: NO"
│  └─> OPTION 1 + API: Memory Bridge for removal, API for granting
│
└─ Everything fails
   └─> OPTION 1: Pure Memory Bridge approach (current working method)
```

---

## What The Test Actually Does

**Test 1:** Find the game's database API
- Success → We can access game systems

**Test 2:** Read inventory count
- Success → We can detect changes

**Test 3:** Grant an item via API
- Success → We don't need Memory Bridge for granting!

**Test 4:** Remove an item (negative quantity)
- Success → We don't need Memory Bridge for removal either!

**Test 5:** Register a function hook
- Success → We can intercept item grants before they happen

**Test 6:** Modify hook parameters
- Success → We can replace items cleanly! ⭐

---

## After Running The Test

1. **Copy the console output** (important for debugging)

2. **If hooking works:**
   - I'll help you implement full function hooking
   - This is the cleanest solution

3. **If API works but not hooking:**
   - Hybrid approach: detect via memory, manipulate via API
   - Still better than pure memory manipulation

4. **If nothing works:**
   - Stick with Memory Bridge approach
   - Add item removal capability
   - Accept brief visual glitches

---

## Files Created For Testing

- ✅ [APITest.lua](ue4ss_mod_lua/Scripts/APITest.lua) - Complete test suite
- ✅ [TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md) - Detailed analysis
- ✅ Updated [main.lua](ue4ss_mod_lua/Scripts/main.lua) - Added F7 keybind

---

## Important Notes

- **The test is non-destructive** - it only adds/removes 1 Potion
- **You need inventory open** to see changes (menu must refresh)
- **F7 can be pressed multiple times** to verify results
- **Console output is saved** - you can share it for analysis

---

## What Happens Next

**Based on test results, we will:**

1. **Choose the best architecture** (hooking vs watching)
2. **Implement location detection** (mapping chests/bosses/shops to AP locations)
3. **Connect to Archipelago server** (receive randomized items)
4. **Test end-to-end flow** (check location → AP responds → item granted)

But first: **Run that F7 test!** It determines everything.
