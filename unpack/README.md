# Separate Unpack Directories

These directories are used for repacking individual randomized assets to avoid conflicts.

## Structure

- `UnpackFresh_Shop/End/` - Contains only ShopItem files
  - Used by: `smart_price_randomizer.py --auto-deploy`
  - Creates: `RandomizedShop_Seed*.pak`

- `UnpackFresh_Rewards/End/` - Contains only Reward files
  - Used by: `reward_randomizer.py --auto-deploy`
  - Creates: `RandomizedRewards_Seed*.pak`

## Setup

You'll need to populate these with the unpacked game files:

```bash
# From your UnpackFresh\End directory, copy:

# For shop randomization
cp UnpackFresh/End/Content/DataObject/Resident/ShopItem.* \
   unpack/UnpackFresh_Shop/End/Content/DataObject/Resident/

# For rewards randomization
cp UnpackFresh/End/Content/DataObject/Resident/Reward.* \
   unpack/UnpackFresh_Rewards/End/Content/DataObject/Resident/
```

## Paths in config.ini

```ini
[Paths]
game_dir = G:\SteamLibrary\steamapps\common\FINAL FANTASY VII REBIRTH
unpack_shop_dir = C:\Users\YourName\Documents\GitHub\FFVIIRebirthAP\unpack\UnpackFresh_Shop\End
unpack_rewards_dir = C:\Users\YourName\Documents\GitHub\FFVIIRebirthAP\unpack\UnpackFresh_Rewards\End
```

## Why Separate Directories?

When repacking multiple randomizers, each pak contains the full directory structure. If they share files (like if both repacked the entire End directory), the later pak would overwrite the earlier one's modifications.

By using separate directories with only the specific files:
- Shop pak contains only ShopItem files
- Rewards pak contains only Reward files
- Equipment pak (future) contains only Equipment files

**No conflicts!** Each pak can load independently.
