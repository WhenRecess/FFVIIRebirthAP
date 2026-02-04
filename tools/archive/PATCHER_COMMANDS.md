# Ready-to-Run Reward Patcher Test Commands

Copy and run these commands one at a time in PowerShell.

## Test 1: ID 100 (Potion - Consumable Baseline)
```powershell
python tools/reward_patcher.py --input "F:\Downloads\DataObjects\Resident\Reward.uexp" --reward "rwdCOL15_TutorialBtl_01" --new-id 100 --quantity 1
```
**After running:**
1. Replace game Reward.uexp with patched version
2. Load FF7R and get the reward
3. Check: Did you get a **Potion**?
4. Record: **Y** or **N**

---

## Test 2: ID 9001 (Equipment - Power Wristguards)
```powershell
python tools/reward_patcher.py --input "F:\Downloads\DataObjects\Resident\Reward.uexp" --reward "rwdCOL15_TutorialBtl_01" --new-id 9001 --quantity 1
```
**After running:**
1. Replace game Reward.uexp with patched version
2. Load FF7R and get the reward
3. Check: Did you get **Power Wristguards**?
4. Record: **Y** or **N**

---

## Test 3: ID 3000 (Minigame Card - Queen's Blood Card)
```powershell
python tools/reward_patcher.py --input "F:\Downloads\DataObjects\Resident\Reward.uexp" --reward "rwdCOL15_TutorialBtl_01" --new-id 3000 --quantity 1
```
**After running:**
1. Replace game Reward.uexp with patched version
2. Load FF7R and get the reward
3. Check: Did you get **Queen's Blood Card**?
4. Record: **Y** or **N**

---

## Test 4: ID 6100 (Chadly Points - Chadley Data - Gongaga)
```powershell
python tools/reward_patcher.py --input "F:\Downloads\DataObjects\Resident\Reward.uexp" --reward "rwdCOL15_TutorialBtl_01" --new-id 6100 --quantity 1
```
**After running:**
1. Replace game Reward.uexp with patched version
2. Load FF7R and get the reward
3. Check: Did you get **Chadley Data - Gongaga**?
4. Record: **Y** or **N**

---

## Test 5: ID 10102 (Crystal - Crystal: Kjata2)
```powershell
python tools/reward_patcher.py --input "F:\Downloads\DataObjects\Resident\Reward.uexp" --reward "rwdCOL15_TutorialBtl_01" --new-id 10102 --quantity 1
```
**After running:**
1. Replace game Reward.uexp with patched version
2. Load FF7R and get the reward
3. Check: Did you get **Crystal: Kjata2**?
4. Record: **Y** or **N**

---

## How to Replace File Each Time

The patcher creates backups automatically, but you need to copy the patched file to your game:

1. After each `python reward_patcher.py` command:
   - Find the patched file in `F:\Downloads\DataObjects\Resident\Reward.uexp`
   - Copy it to your game location
   
2. After testing, restore:
   ```powershell
   copy "F:\Downloads\DataObjects\Resident\Reward.uexp.backup" "F:\Downloads\DataObjects\Resident\Reward.uexp"
   ```

---

## Quick Summary

| Test | Command | Expected Item |
|---|---|---|
| 1 | ID 100 | Potion |
| 2 | ID 9001 | Power Wristguards |
| 3 | ID 3000 | Queen's Blood Card |
| 4 | ID 6100 | Chadley Data - Gongaga |
| 5 | ID 10102 | Crystal: Kjata2 |

**After all 5 tests**, reply with your results:
```
100: Y (Potion)
9001: Y (Power Wristguards)
3000: N (got wrong item)
6100: Y (Chadley Data)
10102: Y (Crystal)
```
