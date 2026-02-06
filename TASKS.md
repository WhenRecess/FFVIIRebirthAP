# FF7 Rebirth Randomizer - Development Tasks

**Current Phase**: Single-World Local Randomizer  
**Goal**: Complete, playable randomizer using pre-randomization (pak patching)  
**Future**: Multiworld support (requires solving runtime item grants)

---

## Overview

We're building a **single-world randomizer** first. All item placement is handled via pre-randomization (modifying game files before launch). This approach is stable, deterministic, and doesn't require solving the unsolved runtime item grant problem.

**Why single-world first?**

- Runtime item granting not feasible (no API functions found, memory approach too fragile)
- Pre-randomization is proven working (shop prices verified in-game)
- Many great randomizers started single-world and added multiworld later
- Delivers a playable experience sooner

---

## Phase 1: Expand Pre-Randomization Coverage

### 1.1 - Chest/Reward Content Randomization

**Status**: Not Started  
**Priority**: HIGH  
**Depends on**: None

Randomize what items appear in treasure chests and quest rewards.

- [ ] Analyze Reward.uasset binary structure (similar to ShopItem analysis)
- [ ] Identify item ID fields in reward tables
- [ ] Create `reward_randomizer.py` using same pattern as `smart_price_randomizer.py`
- [ ] Test with a few known chest locations
- [ ] Verify items appear correctly in-game

**Data sources**:

- `tools/data/Reward_parsed.json` - Extracted reward table data
- `tools/data/EnemyTerritory_parsed.json` - Enemy drop locations

### 1.2 - Equipment Stat Randomization

**Status**: Algorithm Ready  
**Priority**: MEDIUM  
**Depends on**: None

Randomize weapon/armor stats (Attack, Defense, Magic, etc.)

- [ ] Apply `smart_price_randomizer.py` pattern to Equipment.uasset
- [ ] Identify stat value arrays (similar to price arrays)
- [ ] Define reasonable stat ranges per equipment tier
- [ ] Test stat modifications in-game
- [ ] Add to unified randomizer pipeline

**Reference**: `tools/archive/EQUIPMENT_RANDOMIZATION_PLAN.md`

### 1.3 - Enemy Drop Randomization

**Status**: Not Started  
**Priority**: MEDIUM  
**Depends on**: 1.1 (same table structure likely)

- [ ] Identify drop table structure in game files
- [ ] Create drop table randomizer
- [ ] Balance drop rates (don't make key items too rare/common)

---

## Phase 2: Complete AP World Data

### 2.1 - Expand Location Database

**Status**: Partial (~60 locations defined)  
**Priority**: HIGH  
**Depends on**: 1.1 (need to know what's randomizable)

Define all locations where items can be found.

- [ ] Map all story chest locations (Chapters 1-14)
- [ ] Map all side quest reward locations
- [ ] Map all Colosseum reward locations
- [ ] Map all VR Battle rewards
- [ ] Map all enemy territory completion rewards
- [ ] Assign unique IDs matching game's internal structure

**Target**: 500+ locations  
**File**: `worlds/finalfantasy_rebirth/data/location_tables.py`

### 2.2 - Complete Item Definitions

**Status**: Partial (35 progression, 30 filler defined)  
**Priority**: HIGH  
**Depends on**: None

- [ ] Define all key/progression items
- [ ] Define all equipment as items (weapons, armor, accessories)
- [ ] Define all materia
- [ ] Define all summons
- [ ] Map AP item IDs to game item IDs (use `tools/data/_ce_all_real_ids.json`)

**File**: `worlds/finalfantasy_rebirth/data/item_tables.py`

### 2.3 - Logic Rules

**Status**: Basic structure exists  
**Priority**: MEDIUM  
**Depends on**: 2.1, 2.2

- [ ] Define progression requirements (what items unlock what areas)
- [ ] Define chapter unlock logic
- [ ] Test logic doesn't create impossible seeds
- [ ] Add glitch/sequence break options if applicable

**File**: `worlds/finalfantasy_rebirth/randomization/rules.py`

---

## Phase 3: Unified Generation Pipeline

### 3.1 - Seed-to-Pak Pipeline

**Status**: Not Started  
**Priority**: HIGH  
**Depends on**: Phase 1, Phase 2

Create end-to-end flow from AP seed to playable game.

- [ ] AP world generates item placements as JSON/YAML
- [ ] Pre-randomizer tools read placement data
- [ ] Tools modify appropriate .uexp files based on placements
- [ ] Automatic retoc repacking
- [ ] Deploy to game mods folder
- [ ] Generate spoiler log

**Deliverable**: Single command that takes a seed and produces a ready-to-play pak

### 3.2 - Wire Options to Generation

**Status**: Options defined but not connected  
**Priority**: MEDIUM  
**Depends on**: 3.1

- [ ] `ChapterProgression` affects location requirements
- [ ] `ColosseumIncluded` adds/removes Colosseum locations
- [ ] `TrapItems` enables trap item pool
- [ ] `GoalType` sets win condition

**File**: `worlds/finalfantasy_rebirth/core/options.py`

---

## Phase 4: Polish & Testing

### 4.1 - Playtesting

**Status**: Not Started  
**Priority**: HIGH  
**Depends on**: Phase 3

- [ ] Complete playthrough with randomized seed
- [ ] Verify all randomized items work correctly
- [ ] Check for soft-locks or impossible situations
- [ ] Test multiple seeds for variety

### 4.2 - Documentation

**Status**: Partial  
**Priority**: MEDIUM

- [ ] User guide for generating and playing randomized games
- [ ] Troubleshooting guide
- [ ] Known issues list

### 4.3 - Tracker Integration (Optional)

**Status**: Not Started  
**Priority**: LOW

- [ ] Location check detection in Lua mod (for auto-tracking)
- [ ] Integration with PopTracker or similar
- [ ] Manual tracking checklist as fallback

---

## Future: Multiworld Support

**Status**: Blocked  
**Blocker**: No working method to grant items at runtime

Multiworld requires giving players items they receive from other players during gameplay. Our research found:

- No game API functions for adding items to inventory
- Memory modification works (Cheat Engine) but requires signature scanning UE4SS can't do
- External trainer approach is fragile (breaks with game updates)

**Potential paths forward**:

1. **External companion tool** - Separate process with Cheat Engine-style memory access
2. **"Mailbox" system** - Queue items at pre-placed collection points
3. **Wait for UE4SS improvements** - Future versions may add memory scanning

For now, single-world provides a complete, enjoyable randomizer experience.

---

## Quick Reference

### Working Tools

| Tool                        | Purpose                  | Status     |
| --------------------------- | ------------------------ | ---------- |
| `smart_price_randomizer.py` | Shop price randomization | ✅ Working |
| `retoc.exe`                 | Pak repacking            | ✅ Bundled |
| `config.ini`                | Path configuration       | ✅ Working |

### Key Data Files

| File                                | Contents                |
| ----------------------------------- | ----------------------- |
| `tools/data/_ce_all_real_ids.json`  | 502 item IDs from game  |
| `tools/data/Reward_parsed.json`     | Chest/reward table data |
| `worlds/finalfantasy_rebirth/data/` | AP world definitions    |

### Commands

```bash
# Randomize shop prices (working now)
cd tools
python smart_price_randomizer.py "ShopItem.uexp" --auto-deploy 12345 100 5000
```

---

_Last Updated: February 3, 2026_
