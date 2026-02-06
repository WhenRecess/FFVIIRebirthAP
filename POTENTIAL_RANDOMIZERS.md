# FF7 Rebirth Potential Randomizers - Analysis & Roadmap

**Last Updated:** February 5, 2026

This document analyzes potential randomizer features for FF7 Rebirth, organized by difficulty, implementation approach, and gameplay value.

---

## 🟢 Tier 1 — Easy (DataTable exists, fields are clear, low risk)

These follow the exact same pattern as existing randomizers: Extract a DataTable, modify JSON values, reimport.

### Enemy Stats

- **How:** `BattleCharaSpec` DataTable is already extracted with `HP`, `PhysicsAttack`, `PhysicsDefense`, `MagicAttack`, `MagicDefense`, `Shield`. Filter to `EN*` IDs and randomize within ranges.
- **Value:** ⭐⭐⭐⭐⭐ **Huge** — Every fight feels different
- **Notes:** 975 entries already parsed. Can scale by ±% to keep balanced. Same randomizer can handle both regular enemies and bosses.

### Boss Stats

- **How:** Same `BattleCharaSpec` table, filter to `EB*` entries. Randomize separately with tighter bounds.
- **Value:** ⭐⭐⭐⭐⭐ **Huge** — Boss fights become unpredictable
- **Notes:** Same DataTable as enemy stats, just different ID prefix. Could share a randomizer.

### Enemy Weakness

- **How:** `AttributeResist_Array` and `PropertyResist0`/`PropertyResist1` in `BattleCharaSpec`. Shuffle or randomize resistance values.
- **Value:** ⭐⭐⭐⭐ **High** — Forces you to experiment with materia
- **Notes:** Already extracted. Swap/shuffle resist arrays between enemies.

### Boss Weakness

- **How:** Same as Enemy Weakness, `EB*` prefix.
- **Value:** ⭐⭐⭐⭐ **High** — No more memorizing boss weaknesses
- **Notes:** Could be a flag on the enemy stats randomizer.

### Materia MP Cost

- **How:** Extract `BattleAbility` or `BattleAbilityResource` DataTable. MP costs should be simple int fields.
- **Value:** ⭐⭐⭐ **Medium** — Changes resource management
- **Notes:** DataTable exists in ResidentPack but hasn't been extracted yet. One retoc + export away.

### Materia Power

- **How:** Same `BattleAbility` table likely has damage/potency values.
- **Value:** ⭐⭐⭐ **Medium** — Fire might hit harder than Firaga
- **Notes:** Pairs naturally with MP cost randomizer.

### Materia Duration

- **How:** Buff duration fields in `BattleAbility` or `Materia` tables.
- **Value:** ⭐⭐⭐ **Medium** — Barrier lasting 3 seconds or 5 minutes
- **Notes:** Likely same DataTable as power/MP cost.

### Materia Cast Time

- **How:** Cast time / charge time fields in `BattleAbility`.
- **Value:** ⭐⭐⭐ **Medium** — Changes combat flow
- **Notes:** Bundle all materia combat stat randomization together.

### Chocobo Race Stats

- **How:** `ChocoboRace*` (12 DataTables) exist in ResidentPack. Likely has speed, stamina, acceleration fields.
- **Value:** ⭐⭐ **Low-Medium** — Fun for Gold Saucer segment
- **Notes:** Niche but easy. Extract and randomize numeric fields.

### Chocobo Colors

- **How:** `ChocoboCapture*` (6 DataTables) likely define which colors spawn where.
- **Value:** ⭐⭐ **Low** — Cosmetic mostly
- **Notes:** Very easy if it's just enum swaps.

---

## 🟡 Tier 2 — Medium (DataTable exists but needs new extraction, some complexity)

### Equipment Stats

- **How:** `Equipment` DataTable (149KB, unextracted). Will need retoc extraction + UAssetGUI export. Fields likely include ATK, MAG, DEF, MDEF, HP bonuses.
- **Value:** ⭐⭐⭐⭐ **High** — Gear becomes a gamble
- **Notes:** DataTable confirmed to exist. Same pipeline as existing randomizers.

### Equipment Materia Slots

- **How:** Likely in `Equipment` or `WeaponUpgrade` DataTable. Slot count/layout per weapon.
- **Value:** ⭐⭐⭐⭐ **High** — Build diversity
- **Notes:** May be linked to weapon upgrade tree. Need to extract and investigate the schema first.

### Party Member Stats

- **How:** `PlayerParameter`, `InitPlayerParameter`, `BattlePlayerParameter` DataTables. Base stats per character per level.
- **Value:** ⭐⭐⭐⭐ **High** — Aerith might be a tank
- **Notes:** Multiple tables to coordinate. Need to understand which one the game actually reads at runtime.

### Equipment Skills

- **How:** `AutoWeaponAbility` DataTable maps equipment → passive abilities.
- **Value:** ⭐⭐⭐ **High** — Different builds per playthrough
- **Notes:** Shuffle ability IDs between equipment entries. Need to ensure ability IDs are valid.

### Equipment Abilities

- **How:** Same area — weapon abilities (Braver, Focused Thrust, etc.) are assigned somewhere in Equipment or a linked table.
- **Value:** ⭐⭐⭐⭐ **High** — Cloud with Aerith's abilities
- **Notes:** May require `BattleAbility` cross-reference. Need to figure out where weapon→ability mapping lives.

### Weapon Skills

- **How:** The SP-unlocked abilities on weapons. Likely in `WeaponUpgrade` or `WeaponUpgradeTreeLevel`.
- **Value:** ⭐⭐⭐ **Medium** — Changes upgrade priorities
- **Notes:** Tree structure makes this trickier than flat table randomization.

### Music Field

- **How:** `BGMField` DataTable — maps areas to background music. Shuffle the BGM IDs.
- **Value:** ⭐⭐⭐ **Medium** — Fun vibes, low gameplay impact
- **Notes:** Easy technically, high fun factor. People love music randomizers.

### Music Battle

- **How:** `BGMList` or battle-specific BGM assignments.
- **Value:** ⭐⭐⭐ **Medium** — One-Winged Angel plays against a Shinra grunt
- **Notes:** Same approach as field music.

### Music Minigame

- **How:** Minigame-specific BGM references in `Piano*`, `ChocoboRace*`, etc.
- **Value:** ⭐⭐ **Low-Medium** — Niche fun
- **Notes:** Scattered across many tables. More effort per payoff.

### Enemy Types (IDs)

- **How:** `EnemyTerritoryMob` already extracted with `BattleCharaSpecID`. Swap enemy IDs between territories.
- **Value:** ⭐⭐⭐⭐ **High** — Tonberries in Kalm
- **Notes:** Data extracted. Risk: some enemies may require specific arena sizes or scripting. Need to exclude scripted encounters.

---

## 🔴 Tier 3 — Hard (Non-DataTable assets, complex interdependencies, high risk)

### Key Items

- **How:** `Reward.uasset` has `it_key*` entries. You'd shuffle which key items are given where.
- **Value:** ⭐⭐⭐⭐⭐ **Massive** for Archipelago
- **Notes:** **Extremely dangerous** — key items gate story progression. Needs full logic validation to prevent softlocks. This is essentially the core of an Archipelago world. The existing `reward_randomizer.py` already excludes `it_key` for good reason.

### Boss Types

- **How:** Swap `BattleCharaSpecID` for boss encounters. Would need to find boss encounter definitions (likely in level blueprint/scripting, not a DataTable).
- **Value:** ⭐⭐⭐⭐ **High** — Fight Sephiroth in Chapter 2
- **Notes:** Boss encounters are likely hardcoded in level blueprints, not simple DataTable swaps. May cause crashes if arena/camera/scripting doesn't match.

### Folio Tree Layout

- **How:** `SkillTree_*.uasset` files are **UI widget assets**, not DataTables. Folio node positions and connections may be in binary widget data or a separate `PlayerParameter`-adjacent table.
- **Value:** ⭐⭐⭐ **Medium** — Different progression paths
- **Notes:** Need significant reverse engineering. Widget assets have a completely different structure than DataTables.

### Equipment Appearance

- **How:** Visual mesh references are in character blueprint/skeletal mesh assets, not DataTables.
- **Value:** ⭐⭐ **Low** — Pure cosmetic
- **Notes:** Requires modifying blueprint or material assets. Completely different from the current pipeline.

### Party Appearances

- **How:** Character model/mesh swaps across the entire game. Cutscenes, battles, field.
- **Value:** ⭐ **Low** — Cosmetic, breaks cutscenes
- **Notes:** Massive undertaking. Every cutscene references specific character meshes. Would cause visual chaos.

---

## ⛔ Tier 4 — Extreme / Likely Infeasible (Level scripting, game flow)

### Party Member Join Time

- **How:** Controlled by story scripts/blueprints and `InitPartySetData`/`PartyEntry`. Party composition is deeply tied to cutscenes and chapter scripting.
- **Value:** ⭐⭐⭐⭐ **High in theory**
- **Notes:** Would need to modify level blueprints and story flags. Cutscenes assume specific party members. Very high crash/softlock risk.

### Locations

- **How:** Map connections, world layout. This is baked into level streaming and world partition data.
- **Value:** ⭐⭐⭐⭐⭐ **Massive in theory**
- **Notes:** Essentially requires rebuilding the game's world graph. Not feasible with DataTable modding alone.

### Gating

- **How:** `StoryProgress`, `StoryFlag`, `Chapter` tables exist, but gating is enforced by level blueprints, invisible walls, and NPC scripting.
- **Value:** ⭐⭐⭐⭐ **High for AP**
- **Notes:** DataTables might control _some_ flags, but physical barriers are in level assets. Partial implementation possible through story flag manipulation via UE4SS runtime hooks.

---

## 📋 Recommended Priority Order

| Priority | Randomizer(s)                                           | Why                                                                                                             |
| -------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **1**    | **Enemy Stats + Boss Stats + Weakness**                 | Already-extracted data, massive gameplay impact, one DataTable                                                  |
| **2**    | **Equipment Stats + Materia Slots**                     | New extraction needed but same pipeline, high impact                                                            |
| **3**    | **All Materia Combat** (MP, Power, Duration, Cast Time) | Likely one `BattleAbility` table, bundle together                                                               |
| **4**    | **Music (Field + Battle)**                              | Easy, fun, crowd-pleaser                                                                                        |
| **5**    | **Enemy Types**                                         | Data extracted, high impact, but needs crash testing                                                            |
| **6**    | **Equipment Abilities/Skills**                          | Medium effort, high replay value                                                                                |
| **7**    | **Key Items**                                           | Core to Archipelago but needs full logic — this is really the **AP world logic** problem, not just a randomizer |
| **8**    | **Chocobo stuff**                                       | Easy but niche                                                                                                  |

---

## 🛠️ Implementation Notes

### Current Pipeline (Proven)

1. **Extract:** `retoc_filtered.exe` → unpacked `.uasset`/`.uexp` from game `.pak` files
2. **Export:** `UAssetGUI` (C# + UAssetAPI) → `.json` with structured data
3. **Randomize:** Python script modifies JSON values
4. **Import:** `UAssetGUI` → modified `.uasset`
5. **Repack:** `retoc.exe` → `_P.ucas/.utoc/.pak` mod files (Zen format)
6. **Deploy:** Copy to `~mods` folder in game directory

### Existing Randomizers

- ✅ **Smart Price Randomizer** — Shop buy prices (binary pattern matching)
- ✅ **Item Price Randomizer** — Item buy/sell values (`Item.uasset`)
- ✅ **Materia Price Randomizer** — Materia sell prices by level (`Materia.uasset`)
- ✅ **Enemy Stats Randomizer** — Enemy/boss HP, ATK, DEF, MAG, MDEF, Shield (`BattleCharaSpec.uasset`) — **TIER 1 PRIORITY 1** ⭐
- 🟡 **Reward Randomizer** — Chest/quest rewards (`Reward.uasset`) — excludes key items
- 🟡 **Shop Inventory Randomizer** — Shop inventory items/materia (`ShopItem.uasset`)

### Already Extracted DataTables (12 total)

- `BattleCharaSpec` (975 entries) — Enemy/boss stats, resistances, abilities
- `EnemyTerritory` (852 entries) — World territory definitions
- `EnemyTerritoryMob` (587 entries) — Enemy spawn templates
- `Reward` (2,375 entries) — Reward definitions
- `ShopItem` (1,568 entries) — Shop inventory
- `Colosseum` + related (1,919 entries) — Colosseum battles
- Others: `ItemCraftRecipe`, `RewardRandom`, `ShopList`, `ResidentPack`

### Key Unextracted DataTables (Need `retoc` extraction)

- `Equipment` — Equipment stats (149KB)
- `BattleAbility` / `BattleAbilityResource` — Ability stats, MP costs
- `BGMField` / `BGMList` — Music assignments
- `PlayerParameter` / `BattlePlayerParameter` — Player stats
- `WeaponUpgrade` / `WeaponUpgradeTreeLevel` — Weapon upgrade trees
- ~200+ more in `ResidentPack` manifest

---

## 💡 Sweet Spot: Tier 1 + Top of Tier 2

Focus on **10 randomizers** using the proven pipeline with minimal new reverse engineering:

1. Enemy/Boss Stats + Weakness (one randomizer, `BattleCharaSpec`)
2. Equipment Stats + Materia Slots (one extraction, `Equipment`)
3. Materia Combat Bundle (MP, Power, Duration, Cast Time from `BattleAbility`)
4. Music Field/Battle (BGM tables)
5. Enemy Type Swaps (`EnemyTerritoryMob`)

This gives maximum gameplay variety with minimal technical risk.
