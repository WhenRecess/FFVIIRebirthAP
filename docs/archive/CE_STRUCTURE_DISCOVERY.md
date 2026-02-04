# Finding Game Data Structures in Cheat Engine
# Complete guide for all randomizable content

## 1. Finding Chest Data

### Method 0: Minimal-Results (Unique Item + Pattern)
**Use this if scans return too many values**

1. **Pick a chest with a unique item**
   - Prefer Materia or rare items that are unlikely elsewhere.
   - Note the item ID from your mapping table.

2. **Before opening the chest:**
   - New Scan → Value Type: 4 Bytes
   - Search for the item ID
   - Enable **Fast Scan** and **Aligned** (4-byte aligned)
   - Optional: set Scan Region to **Writable** only

3. **Use a pattern search to narrow results**
   - Open Memory View → Search → **Array of Bytes**
   - Search for a packed pattern like:
     ```
     [item_id] [quantity] [opened_flag]
     ```
   - Example for Potion (100), quantity 1, unopened:
     ```
     64 00 00 00  01 00 00 00  00 00 00 00
     ```

4. **Open the chest**
   - Repeat the Array of Bytes search with opened flag = 1:
     ```
     64 00 00 00  01 00 00 00  01 00 00 00
     ```
   - This should narrow to a handful of candidates.

5. **Verify the structure**
   - Inspect nearby memory for a consistent structure size
   - Change `item_id` to a different known ID and re-open a prior save to confirm

### Method 1: Known Item Search
**Use this if you know what item a chest contains**

1. **Before opening chest:**
   - New Scan → Value Type: 4 Bytes
   - Search for the item ID (e.g., 100 for Potion)
   - You'll get many results

2. **Open the chest** and note what you received

3. **Next Scan:**
   - Search for the item you ACTUALLY want to find (the chest's item)
   - This narrows results

4. **Find the structure:**
   - Look for addresses with similar patterns
   - Check nearby memory for chest ID, quantity, opened flag

### Method 2: Unknown Value + Change Detection
**Use when you don't know chest contents**

1. **Stand near chest (don't open):**
   - New Scan → Unknown initial value
   - First Scan

2. **Move around** (don't open chest):
   - Scan Type: Unchanged value
   - Next Scan (repeat 2-3 times)

3. **Open chest:**
   - Scan Type: Changed value
   - Next Scan

4. **Browse memory region:**
   - Find the "opened" flag (changed from 0→1)
   - Look at surrounding memory for item ID pattern

### If You Still Get Too Many Results

- **Use a rare item** (Materia, key items) to reduce hits.
- **Use a 12-byte Array of Bytes pattern** (item_id + quantity + opened flag).
- **Scan only writable memory** and enable **aligned 4-byte** scans.
- **Save/Reload** and compare which candidates stay stable after reload.
- Use **Find out what writes to this address** on the opened flag candidate to confirm a chest open event.

---

## 2. Finding Shop Inventory

### Shop Structure Discovery

1. **Enter a shop** (note what items are for sale)

2. **Search for the first item in stock:**
   - New Scan → 4 Bytes
   - Search for item ID (e.g., 100 for Potion)

3. **Look for sequential items:**
   ```
   Shop stock: [Potion, Hi-Potion, Ether]
   Memory pattern:
   Address        Value
   0x...000       100    (Potion)
   0x...004       101    (Hi-Potion) 
   0x...008       111    (Ether)
   ```

4. **Verify by changing:**
   - Change the first item ID from 100 → 116 (Phoenix Down)
   - Talk to shop NPC again
   - Check if first item changed

### Shop Data Structure (typical)
```cpp
struct ShopSlot {
    int item_id;       // +0x0
    int price;         // +0x4
    int stock;         // +0x8  (-1 = infinite)
};

ShopSlot inventory[10];  // 10 slots per shop
```

### Finding Multiple Shops

1. **Note current shop ID** (Kalm, Junon, etc.)
2. **Exit and enter different shop**
3. **Search for new shop's items**
4. **Calculate offset between shops:**
   ```
   Shop_Kalm_base = 0x7FF7F8950000
   Shop_Junon_base = 0x7FF7F8951000
   Offset = 0x1000 (4096 bytes)
   ```

---

## 3. Finding Battle Rewards

### Method: Pre/Post Battle Comparison

1. **Save before battle** (quicksave or manual)

2. **Scan for the reward item:**
   - If boss should give "Mythril Ore" (ID 330)
   - Search for value: 330

3. **Fight and win the battle**

4. **Check battle results screen:**
   - Note what reward was shown

5. **Search changed values:**
   - The reward item count should have increased
   - Find addresses that changed

### Battle Reward Structure (hypothetical)
```cpp
struct BattleReward {
    int battle_id;        // Unique battle identifier
    int item_id;          // Reward item
    int quantity;         // Amount given
    int exp_reward;       // EXP given
    int gil_reward;       // Gil given
};
```

### Finding Boss-Specific Rewards

Boss rewards might be in a separate table from regular encounters:

1. **Search for boss battle ID** in CE Lua:
   ```lua
   -- After defeating Midgardsormr
   -- Search memory for "Midgardsormr" string or battle ID
   ```

2. **Pointer scan** from reward item to boss data:
   - Right-click reward address
   - "Pointer scan for this address"
   - Find static pointer

---

## 4. Finding Simulator/VR Challenge Rewards

### Chadley's Simulator Challenges

These might be stored differently than chests:

1. **Before starting challenge:**
   - Talk to Chadley
   - Note which challenge and its reward

2. **Search for challenge ID:**
   - Challenges might be numbered (1, 2, 3...)
   - Or have specific IDs

3. **Complete challenge:**
   - Watch for memory changes
   - Reward might be granted instantly or on menu close

### VR Summon Battle Structure
```cpp
struct VRBattle {
    int challenge_id;      // VR_Bahamut = 1, etc.
    int completion_flag;   // 0=not started, 1=completed
    int reward_item_id;    // Materia or item
    int difficulty;        // Normal, Hard, etc.
};
```

### Finding the Challenge List

1. **Open Chadley's menu**
2. **Scan for challenge names** (if visible)
3. **Or scan for sequential IDs:**
   ```
   Challenge 1: ID = 1001
   Challenge 2: ID = 1002
   Challenge 3: ID = 1003
   ```

4. **Verify by changing reward:**
   - Change VR_Bahamut reward from Bahamut Materia → Phoenix Down
   - Complete challenge
   - Check if you got Phoenix Down instead

---

## 5. Finding Colosseum Battle Rewards

### Colosseum Battle Structure

You already have `Colosseum_parsed.json` data! Use it:

1. **Load the JSON** to know battle IDs
2. **Search for battle number** in memory
3. **Find reward field** next to battle data

### Using Existing Data
```python
# From Colosseum_parsed.json
battle_data = {
    "battle_num": 1,
    "reward_item_id": 100,
    "difficulty": "Normal"
}
```

Search memory for this pattern:
```
01 00 00 00  (battle 1)
64 00 00 00  (item 100 = Potion)
...
```

### Verification

1. **Change battle 1 reward** from Potion → Ether
2. **Complete battle 1**
3. **Check rewards screen** - should show Ether

---

## General Tips

### Pattern Recognition
Game data often follows patterns:
```
[ID] [Item] [Quantity] [Flag/Status] [Padding]
 4b    4b      4b          4b          ...
```

### Pointer Scanning
For dynamic structures, use pointer scans:
1. Find the data address
2. Right-click → "Pointer scan for this address"
3. Save pointer results
4. Restart game, reload scan
5. Find persistent pointers

### Using CE Lua for Automation
```lua
-- Test script to verify shop patching
function patchShop(shop_base, slot, new_item_id)
    local slot_address = shop_base + (slot * 0x10)  -- 0x10 = slot size
    writeInteger(slot_address, new_item_id)
    print(string.format("Patched shop slot %d to item %d", slot, new_item_id))
end

-- Usage
kalm_shop_base = readPointer("ff7rebirth_.exe+SHOPBASE")
patchShop(kalm_shop_base, 0, 111)  -- Change first slot to Ether
```

---

## Priority Order for Discovery

**Start with these (easiest to hardest):**

1. ✅ **Chests** - Static, well-defined, many examples
2. ✅ **Shops** - Clear inventory display, easy to verify
3. ⚠️ **Colosseum** - Have JSON data, structured battles
4. ⚠️ **Boss Rewards** - One-time events, need save scumming
5. ❌ **Simulator** - May be server-validated, complex

---

## Documenting Your Findings

When you find a structure, document it:

```cpp
// Chest Structure (verified 2026-02-03)
// Base: ff7rebirth_.exe+0xABC12340 (points to array)
// Array size: 500 chests
// Stride: 0x20 (32 bytes)
struct ChestData {
    uint32_t chest_id;      // +0x00
    uint32_t item_id;       // +0x04  ← PATCH THIS
    uint32_t quantity;      // +0x08
    uint32_t opened_flag;   // +0x0C
    float pos_x;            // +0x10
    float pos_y;            // +0x14
    float pos_z;            // +0x18
    uint32_t padding;       // +0x1C
};
```

Save this to a file so Memory Bridge can use it!
