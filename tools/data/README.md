# Data Files

Static game data used by active randomizers.

## Files

### `_reward_parsed.json`

- **Used by**: `reward_randomizer.py`, `shop_inventory_randomizer.py`
- **Contents**: Parsed reward pool data (item IDs and types from game reward tables)
- **Purpose**: Provides the valid item pool for reward shuffling and shop inventory randomization

## Notes

All other data files have been removed — they were outputs of legacy extraction scripts.
Active randomizers now extract fresh data directly from game paks via retoc + UAssetGUI JSON pipeline at runtime.
