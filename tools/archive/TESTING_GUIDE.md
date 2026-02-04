# Quick Testing Guide - Verify Item IDs

## Option 1: Cheat Engine Item Spawning (FASTEST - 10 minutes)

### Prerequisites
- CE table (ce.txt)
- FF7R running with save loaded
- Inventory open

### Steps

1. **Find Item Pointer in CE**
   - Open Cheat Engine
   - Load ce.txt table
   - Find/hook to "player inventory" or "item array" address
   - (CE table likely has this predefined)

2. **Test Individual IDs**
   - For each test ID, modify memory to add item
   - Check if correct item appears in inventory
   - Format: Modify item array entry to set ID and quantity

3. **Test Batch**
   Test these representative IDs:
   - **3000** (should be: Queen's Blood Card/minigamecard)
   - **5005** (should be: Chocobo Gear #005)
   - **6100** (should be: Chadley Data - Gongaga)
   - **10102** (should be: Crystal Kjata2)
   - **6200** (should be: Chadley Data - Grasslands)

4. **Record Results**
   ```
   ID | Item Name | Expected | Got | ✓/✗
   3000 | Minigamecard | Queen's Blood Card | ? | 
   5005 | Chocobo Custom | Chocobo Gear #005 | ?
   6100 | Chadly Gongaga | Chadley Data - Gongaga | ?
   10102 | Crystal Kjata2 | Crystal: Kjata2 | ?
   6200 | Chadly Grass | Chadley Data - Grasslands | ?
   ```

---

## Option 2: Reward Patcher Test (RELIABLE - 30 minutes)

### Prerequisites
- reward_patcher.py (working)
- UE4SS mod environment or ability to load PAK mods
- Game/save to test in

### Steps

1. **Pick a Test Reward Location**
   - Choose a simple reward (e.g., rwdCOL15_TutorialBtl_01)
   - Current item: E_ACC_0026 (ID 9026)

2. **Patch to Test ID**
   ```bash
   python tools/reward_patcher.py \
     --input "F:\Downloads\DataObjects\Resident\Reward.uexp" \
     --output "test_reward.uexp" \
     --location "rwdCOL15_TutorialBtl_01" \
     --new-id 3000 \
     --quantity 1
   ```

3. **Create Test PAK**
   - Replace Reward.uexp in game directory with patched version
   - Or use UE4SS to hot-patch

4. **Test in Game**
   - Complete that specific reward location
   - Check if correct item appears
   - If wrong item, ID mapping is incorrect

5. **Repeat for Different IDs**
   - Change new-id to test different categories
   - Document which IDs work/fail

---

## Option 3: Memory Extraction (DEFINITIVE - 1 hour)

If CE has item enumeration data, we can extract the full table:

1. **Find Item Enum in Game Memory**
   ```
   Search for known item ID (100 = potion)
   Look for pointer/table that contains all IDs
   Dump the region (likely contiguous array)
   ```

2. **Parse Dumped Memory**
   ```python
   # Extract sequential IDs
   import struct
   with open('item_memory_dump.bin', 'rb') as f:
       data = f.read()
       for i in range(0, len(data), 4):
           item_id = struct.unpack('<I', data[i:i+4])[0]
           if 1 < item_id < 50000:
               print(f"Offset {i}: ID {item_id}")
   ```

3. **Cross-reference with Our Mappings**
   - Compare dumped IDs against our predictions
   - See which patterns are correct

---

## Quick Verification Script

Once you've tested 5-10 IDs, you'll know:
- ✓ If sequential pattern (E_ACC_000X → 9000+X) is correct
- ✓ If minigame card range (3000+) is valid
- ✓ If Chadly points (6100-6400) match
- ✓ If crystal range (10000+) is close

```python
# tools/test_results.py - track findings
test_results = {
    3000: {"expected": "minigamecard", "actual": "???", "correct": None},
    5005: {"expected": "chocobo_005", "actual": "???", "correct": None},
    6100: {"expected": "chadly_gongaga", "actual": "???", "correct": None},
    10102: {"expected": "crystal_kjata2", "actual": "???", "correct": None},
}
```

---

## What We're Solving

- ✓ Consumables (80): ALREADY VERIFIED (in existing mapping)
- ✓ Equipment E_ACC (96): PROBABLY CORRECT (pattern seems solid)
- ? Special items (52): COMPLETELY UNVERIFIED (guesses only)

**Testing these 5 IDs will tell us if the special items mapping is worth using.**

---

## Recommended Testing Order

1. **Test 1 equipment ID** (e.g., E_ACC_0001 = 9001) → should give "Power Wristguards"
2. **Test 1 minigame card** (3000) → should give "Queen's Blood Card"
3. **Test 1 Chadly point** (6100) → should give Chadley Data item
4. **Test 1 crystal** (10102) → should give "Crystal: Kjata2"
5. **Test 1 chocobo** (5005) → should give "Chocobo Gear #005"

If 4/5 match expected = mappings are probably right
If 2/5 match = pattern is wrong, need real data
If 0/5 match = ID ranges are all incorrect
