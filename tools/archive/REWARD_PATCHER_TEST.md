# Option 2: Reward Patcher Testing (In-Game Validation)

## How It Works

1. **Patch** a reward location with a test item ID
2. **Load game** and complete that specific reward
3. **Check inventory** - did the right item appear?
4. **Restore** and repeat with next test ID

## Prerequisites

- FF7R game and save file
- Access to game files or UE4SS mod loader
- reward_patcher.py (included)
- Reward.uexp file (extracted)

## Step-by-Step Guide

### Step 1: Find Your Reward.uexp File

Location depends on installation:
- **Steam**: `C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY VII REBIRTH\FF7R\Content\DataObjects\Resident\Reward.uexp`
- **Or extracted from PAK**: Your extraction folder

Note the full path for next step.

### Step 2: Run Patcher Commands

Open PowerShell in the workspace and run these commands:

#### Test 1: ID 100 (Potion - Consumable Baseline)
```powershell
python tools/reward_patcher.py `
  --input "PATH_TO_YOUR_REWARD.uexp" `
  --reward "rwdCOL15_TutorialBtl_01" `
  --new-id 100 `
  --quantity 1
```

#### Test 2: ID 9001 (Equipment - Power Wristguards)
```powershell
python tools/reward_patcher.py `
  --input "PATH_TO_YOUR_REWARD.uexp" `
  --reward "rwdCOL15_TutorialBtl_01" `
  --new-id 9001 `
  --quantity 1
```

#### Test 3: ID 3000 (Minigame Card)
```powershell
python tools/reward_patcher.py `
  --input "PATH_TO_YOUR_REWARD.uexp" `
  --reward "rwdCOL15_TutorialBtl_01" `
  --new-id 3000 `
  --quantity 1
```

#### Test 4: ID 6100 (Chadly Data - Gongaga)
```powershell
python tools/reward_patcher.py `
  --input "PATH_TO_YOUR_REWARD.uexp" `
  --reward "rwdCOL15_TutorialBtl_01" `
  --new-id 6100 `
  --quantity 1
```

#### Test 5: ID 10102 (Crystal: Kjata2)
```powershell
python tools/reward_patcher.py `
  --input "PATH_TO_YOUR_REWARD.uexp" `
  --reward "rwdCOL15_TutorialBtl_01" `
  --new-id 10102 `
  --quantity 1
```

### Step 3: Load Patched File in Game

**Option A - PAK Mod:**
1. Replace original Reward.uexp with patched version in game directory
2. Start FF7R
3. Navigate to that reward location

**Option B - UE4SS:**
1. Place patched Reward.uexp in UE4SS mod folder
2. Load with UE4SS injector
3. Navigate to reward in-game

### Step 4: Collect the Reward

1. **Travel to the reward location** in FF7R
2. **Complete the action** to get the reward
3. **Open inventory** and check what item you got
4. **Record result**: Y (correct item) or N (wrong item)

### Step 5: Restore & Repeat

1. **Restore backup**: `copy Reward.uexp.backup Reward.uexp`
2. Go to Step 2 with next test ID
3. Repeat for all 5 tests

## Test Summary

| Test | ID | Reward Location | Expected Item | Got | Result |
|---|---|---|---|---|---|
| 1 | 100 | rwdCOL15_TutorialBtl_01 | Potion | ? | Y/N |
| 2 | 9001 | rwdCOL15_TutorialBtl_01 | Power Wristguards | ? | Y/N |
| 3 | 3000 | rwdCOL15_TutorialBtl_01 | Queen's Blood Card | ? | Y/N |
| 4 | 6100 | rwdCOL15_TutorialBtl_01 | Chadley Data - Gongaga | ? | Y/N |
| 5 | 10102 | rwdCOL15_TutorialBtl_01 | Crystal: Kjata2 | ? | Y/N |

## Results Interpretation

**4-5 Correct** ✅ → Patterns are trustworthy, use all 244 mappings  
**2-3 Correct** ⚠️ → Some patterns wrong, needs refinement  
**0-1 Correct** ❌ → ID ranges completely wrong, different approach needed

## Troubleshooting

**"Reward not found"?**
- Check reward name spelling
- Run `python tools/reward_enhanced_parser.py` to list all available rewards

**"File not found"?**
- Update `--input` path with full path to your Reward.uexp
- Use `C:\Program Files\...` format (full absolute path)

**Changes don't show in-game?**
- Make sure patched file is in correct game/mod directory
- Restart game completely
- Check backup wasn't used instead

**Item still wrong after patching?**
- ID mapping is incorrect for that range
- Move to next test ID
- Patterns need adjustment
