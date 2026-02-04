# Quick Testing Options - Pick One

## Option 1: Cheat Engine (5-15 min) ⚡ FASTEST
**What:** Use CE to directly modify game memory to spawn items
**Pros:** No modding, instant feedback, test 10+ IDs quickly
**Cons:** Requires finding inventory array address in CE
**Steps:**
1. Open ce.txt in Cheat Engine
2. Find player inventory address (likely pre-populated in CE table)
3. Modify memory to add item with ID 3000
4. Check if Queen's Blood Card appears
5. Repeat with other IDs

**Test these IDs first:**
- 100 (Potion) - baseline/known good
- 9001 (Power Wristguards) - equipment
- 3000 (Queen's Blood Card) - minigame
- 6100 (Chadly Data) - key item
- 10102 (Crystal Kjata2) - materia

**If 4/5 match expected → mappings are probably correct**

---

## Option 2: Reward Patcher (15-30 min) 🎮 RELIABLE
**What:** Patch specific reward locations, test in-game
**Pros:** Definitive (actual in-game item), uses existing tools
**Cons:** Slower, requires reloading game for each test
**Steps:**
```bash
# Patch a reward to test ID
python tools/reward_patcher.py \
  --input "F:\Downloads\DataObjects\Resident\Reward.uexp" \
  --output "reward_test.uexp" \
  --location "rwdCOL15_TutorialBtl_01" \
  --new-id 3000 \
  --quantity 1

# Replace game's Reward.uexp with reward_test.uexp
# Complete the reward in-game
# Check inventory for Queen's Blood Card
# If correct → ID 3000 works!
```

**Suggested test rewards:**
- rwdCard_GOLDS_012_00 → Test ID 100 (known good)
- rwdCOL15_TutorialBtl_01 → Test ID 3000 (minigame)
- rwdCOL30_GOLDA_08 → Test ID 9001 (equipment)
- rwdCOL30_GOLDA_14 → Test ID 6100 (chadly)

---

## Option 3: Memory Inspection (30-60 min) 🔬 DEFINITIVE
**What:** Dump game memory to extract full item ID table
**Pros:** Gets ALL IDs at once, ultimate truth
**Cons:** Most complex, requires reverse engineering
**Steps:**
1. Find item enumeration in game memory
2. Dump memory region containing item data
3. Parse for ID patterns
4. Compare against our mappings

**Would answer:** Are the ID ranges even close?

---

## 🎯 RECOMMENDED: Start with Option 1

**Why?**
- Fastest feedback (5 min vs 15-30 min)
- Test multiple IDs quickly
- If 4/5 pass → confidence to use all mappings
- If 2/5 pass → know patterns need adjustment
- If 0/5 pass → mappings are all wrong

**How to decide if patterns are right:**
```
5/5 correct = 100% trust all mappings
4/5 correct = Trust 80% (offset needed?)
3/5 correct = Mixed - some ranges off
2/5 correct = Patterns wrong, need verification
1/5 correct = IDs probably wrong
0/5 correct = All ID ranges incorrect
```

---

## Quick Status

**Currently know:**
- ✅ 80 consumables: VERIFIED (from existing mapping)
- ✅ 96 equipment (E_ACC_*): PROBABLY OK (pattern seems logical)
- ❓ 52 special items: NO CLUE (pure guesses)

**After testing Option 1 with 5 IDs, you'll know if the pattern holds for all 244 items.**

---

## Files Ready for Testing

- `TESTING_GUIDE.md` - Detailed instructions
- `ITEM_TEST_TEMPLATE.txt` - Record sheet
- `generate_ce_tester.py` - CE Lua script generator
- `reward_patcher.py` - Already working patcher
- `_complete_item_mappings.json` - Test values here
