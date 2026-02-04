# Validation Assessment - Skip In-Game Testing

## What We Know For Certain

**80 Consumables (ID 100-499)**: ✅ VERIFIED
- These exist in pre-extracted `_item_name_to_id.json`
- Source: Direct extraction from reward data
- Confidence: HIGH (already in working repository)

Example verified items:
- 100 = Potion
- 101 = Hi-Potion
- 116 = Phoenix Down
- etc.

## What We're Uncertain About (164 items)

**Equipment (112 items)**: 
- Pattern: E_ACC_000X → ID 9000+X
- Example: E_ACC_0001 = 9001, E_ACC_0022 = 9022
- Confidence: MEDIUM (pattern is logical but untested)
- Risk: If wrong, AP items won't match equipment

**Special Items (52 items)**:
- Minigame cards (3000-3099)
- Chocobo gear (5000-5999)
- Chadly points (6100-6499)
- Crystals (10000-14999)
- Confidence: LOW (pure pattern guesses)
- Risk: If wrong, AP can't randomize these item types

## Recommendation

**Option A - Conservative (Safe)**
- Use ONLY 80 verified consumables for AP
- Limited but guaranteed to work
- Player gets only potions/ethers/etc randomized

**Option B - Moderate Risk (Likely Works)**
- Use 80 consumables + 112 equipment (192 total)
- Equipment pattern seems solid
- Test 1-2 equipment IDs in-game if needed

**Option C - Full Risk (Many unknowns)**
- Use all 244 items
- Patterns likely 60-70% correct
- Special items are guesses

## Decision

For AP randomization, I'd recommend **Option B** - include the 80 verified + 112 equipment pattern. The equipment pattern (E_ACC_000X → 900X) is mathematically logical and consistent.

For the 52 special items - those should be tested or excluded until verified.

**What would you prefer?**
