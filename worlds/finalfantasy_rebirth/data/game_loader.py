"""
Game Data Loader for Final Fantasy VII: Rebirth
================================================================

This module provides the GameDataManager class which handles loading and 
accessing extracted game data from JSON files. The raw game data is stored
in the `exports/` subdirectory.

Key Components:
    - GameDataManager: Main class for loading and querying game data
    - GameItem: Data class representing in-game items
    - ColosseumBattle: Data class for colosseum battle definitions
    - Territory: Data class for world territory/encounter areas
    - ItemType/LocationType: Enums for categorizing game content

Usage:
    from .game_loader import get_game_data, ItemType
    
    game_data = get_game_data()
    accessories = game_data.get_items_by_type(ItemType.ACCESSORY)

Note:
    This module expects JSON files exported from the game's UAsset files
    using the tools in the /tools directory of this repository.
"""
import json
import os
import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum, auto


# =============================================================================
# Path Configuration
# =============================================================================

# Base directory for this module
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory containing exported game data JSON files
EXPORTS_DIR = os.path.join(_MODULE_DIR, "exports")

# Legacy alias for backwards compatibility
DATA_DIR = EXPORTS_DIR


# =============================================================================
# Item Name Mapping (loaded at module init)
# =============================================================================

_ITEM_NAMES: Dict[str, str] = {}
_item_names_path = os.path.join(EXPORTS_DIR, "item_names.json")
if os.path.exists(_item_names_path):
    with open(_item_names_path, "r", encoding="utf-8") as f:
        _ITEM_NAMES = json.load(f)


def get_item_display_name(game_id: str) -> str:
    """Get the human-readable display name for an item ID."""
    return _ITEM_NAMES.get(game_id, game_id)


class ItemType(Enum):
    """Types of items in the game."""
    ACCESSORY = auto()      # E_ACC_*
    ARMOR = auto()          # E_ARM_*
    CONSUMABLE = auto()     # IT_*
    WEAPON = auto()         # W_*
    MATERIA = auto()        # M_*
    KEY_ITEM = auto()       # key_*
    MATERIAL = auto()       # mat_*
    UNKNOWN = auto()


class LocationType(Enum):
    """Types of locations/checks in the game."""
    COLOSSEUM_BATTLE = auto()
    COLOSSEUM_REWARD = auto()
    TERRITORY_ENCOUNTER = auto()
    BOSS_FIGHT = auto()
    CHEST = auto()
    QUEST_REWARD = auto()
    SHOP_UNLOCK = auto()
    CRAFTING_RECIPE = auto()


@dataclass
class GameItem:
    """Represents an in-game item."""
    game_id: str           # Original game ID (e.g., "E_ACC_0001")
    item_type: ItemType
    display_name: str      # Human-readable name
    description: str = ""
    
    @classmethod
    def from_game_id(cls, game_id: str) -> "GameItem":
        """Create a GameItem from a game ID, inferring type and display name."""
        item_type = cls._infer_type(game_id)
        display_name = cls._generate_display_name(game_id, item_type)
        return cls(game_id=game_id, item_type=item_type, display_name=display_name)
    
    @staticmethod
    def _infer_type(game_id: str) -> ItemType:
        """Infer item type from game ID prefix."""
        if game_id.startswith("E_ACC"):
            return ItemType.ACCESSORY
        elif game_id.startswith("E_ARM"):
            return ItemType.ARMOR
        elif game_id.startswith("IT_") or game_id.startswith("it_"):
            return ItemType.CONSUMABLE
        elif game_id.startswith("W_"):
            return ItemType.WEAPON
        elif game_id.startswith("M_"):
            return ItemType.MATERIA
        elif game_id.startswith("key_"):
            return ItemType.KEY_ITEM
        elif game_id.startswith("mat_"):
            return ItemType.MATERIAL
        return ItemType.UNKNOWN
    
    @staticmethod
    def _generate_display_name(game_id: str, item_type: ItemType) -> str:
        """Generate a human-readable display name from game ID."""
        # First, check if we have a mapped name
        if game_id in _ITEM_NAMES:
            return _ITEM_NAMES[game_id]
        
        # Fallback: generate name from ID
        name = game_id
        
        # Handle specific prefixes
        prefix_map = {
            "E_ACC_": "Accessory ",
            "E_ARM_": "Armor ",
            "IT_": "",
            "it_": "",
            "W_": "Weapon ",
            "M_": "Materia ",
            "key_": "Key Item: ",
            "mat_": "Material ",
        }
        
        for prefix, replacement in prefix_map.items():
            if name.startswith(prefix):
                name = replacement + name[len(prefix):]
                break
        
        # Convert underscores to spaces and title case
        name = name.replace("_", " ")
        
        # Handle camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        return name.title()


@dataclass
class ColosseumBattle:
    """Represents a Colosseum battle."""
    battle_id: str         # e.g., "COL30_GOLDA_01_Free_Col"
    colosseum: str         # e.g., "COL30"
    tier: str              # e.g., "GOLDA" (Gold A), "UNDRS" (Under), etc.
    round_number: int
    battle_type: str       # "Free", "Tutorial", etc.
    display_name: str
    reward_id: Optional[str] = None
    
    @classmethod
    def from_battle_id(cls, battle_id: str) -> Optional["ColosseumBattle"]:
        """Parse a battle ID into a ColosseumBattle object."""
        parts = battle_id.split("_")
        if len(parts) < 3:
            return None
        
        colosseum = parts[0]  # COL30, COL11, etc.
        
        # Handle tutorial battles differently
        if "Tutorial" in battle_id:
            tier = "Tutorial"
            round_num = 0
            battle_type = "Tutorial"
            character = parts[-2] if len(parts) > 3 else ""
            display_name = f"{colosseum} Tutorial: {character}"
        else:
            tier = parts[1]  # GOLDA, UNDRS, SUMMON, etc.
            
            # Try to extract round number
            round_num = 0
            for part in parts[2:]:
                if part.isdigit():
                    round_num = int(part)
                    break
            
            # Determine battle type
            battle_type = "Free" if "Free" in battle_id else "Standard"
            
            # Generate display name
            tier_names = {
                "GOLDA": "Gold Saucer A",
                "UNDRS": "Under",
                "CORLA": "Corel A",
                "CSMOA": "Costa del Sol A",
                "GONGA": "Gongaga A",
                "GRASA": "Grasslands A",
                "JUNOA": "Junon A",
                "NIBLA": "Nibelheim A",
                "NIBLS": "Nibelheim Special",
                "SUMMON": "Summon Challenge",
            }
            tier_display = tier_names.get(tier, tier)
            display_name = f"Colosseum: {tier_display} Round {round_num}"
            
            if "SUMMON" in tier:
                # Extract summon name
                summon = parts[-2] if len(parts) > 2 else ""
                display_name = f"Summon Battle: {summon}"
        
        return cls(
            battle_id=battle_id,
            colosseum=colosseum,
            tier=tier,
            round_number=round_num,
            battle_type=battle_type,
            display_name=display_name,
            reward_id=f"rwrd{battle_id.replace('_Free_Col', '').replace('_Free_vr', '').replace('_Free_Colvr', '')}"
        )


@dataclass 
class Territory:
    """Represents a territory/encounter area."""
    territory_id: str
    region: str
    subregion: Optional[str] = None
    display_name: str = ""
    
    @classmethod
    def from_territory_id(cls, territory_id: str) -> "Territory":
        """Parse territory ID into a Territory object."""
        if territory_id.startswith("terVR_"):
            # VR Colosseum territory
            parts = territory_id.replace("terVR_", "").split("_")
            region = "VR_Colosseum"
            subregion = "_".join(parts)
            display_name = f"VR: {subregion}"
        else:
            match = re.match(r"ter(\d+)_?(\d+)?", territory_id)
            if match:
                region = f"Region_{match.group(1)}"
                subregion = match.group(2)
                display_name = f"Territory {match.group(1)}"
                if subregion:
                    display_name += f"-{subregion}"
            else:
                region = territory_id
                subregion = None
                display_name = territory_id
        
        return cls(
            territory_id=territory_id,
            region=region,
            subregion=subregion,
            display_name=display_name
        )


class GameDataManager:
    """
    Manages loading and accessing extracted game data.
    
    This class provides a unified interface for accessing all game data
    that has been extracted from the game's UAsset files. Data is loaded
    lazily on first access.
    
    Attributes:
        data_dir: Path to the directory containing JSON export files
        items: Dictionary of GameItem objects keyed by game ID
        colosseum_battles: Dictionary of ColosseumBattle objects
        territories: Dictionary of Territory objects
        enemies: Set of enemy IDs found in the game data
        summons: Set of summon IDs found in the game data
        reward_ids: Set of reward IDs for battle completions
    
    Example:
        manager = GameDataManager()
        manager.load()
        
        # Get all accessories
        accessories = manager.get_items_by_type(ItemType.ACCESSORY)
        
        # Get colosseum battles for a specific tier
        gold_battles = manager.get_colosseum_battles_by_tier("GOLDA")
    """
    
    def __init__(self, data_dir: str = EXPORTS_DIR):
        """Initialize the GameDataManager.
        
        Args:
            data_dir: Path to directory containing exported JSON files.
                      Defaults to the 'exports/' subdirectory.
        """
        self.data_dir = data_dir
        self._consolidated: Optional[Dict] = None
        self._items: Dict[str, GameItem] = {}
        self._colosseum_battles: Dict[str, ColosseumBattle] = {}
        self._territories: Dict[str, Territory] = {}
        self._enemies: Set[str] = set()
        self._summons: Set[str] = set()
        self._reward_ids: Set[str] = set()
        self._shop_entries: Set[str] = set()
        
    def load(self) -> bool:
        """
        Load all game data from the consolidated JSON file.
        
        Returns:
            True if data was loaded successfully, False otherwise.
        """
        consolidated_path = os.path.join(self.data_dir, "_consolidated_data.json")
        
        if not os.path.exists(consolidated_path):
            print(f"Warning: Consolidated data not found at {consolidated_path}")
            return False
        
        try:
            with open(consolidated_path, 'r', encoding='utf-8') as f:
                self._consolidated = json.load(f)
            
            # Process items
            for item_id in self._consolidated.get("items", []):
                self._items[item_id] = GameItem.from_game_id(item_id)
            
            # Process colosseum battles  
            for battle_id in self._consolidated.get("colosseum_battles", []):
                battle = ColosseumBattle.from_battle_id(battle_id)
                if battle:
                    self._colosseum_battles[battle_id] = battle
            
            # Process territories
            for ter_id in self._consolidated.get("territories", []):
                self._territories[ter_id] = Territory.from_territory_id(ter_id)
            
            # Store sets
            self._enemies = set(self._consolidated.get("enemies", []))
            self._summons = set(self._consolidated.get("summons", []))
            self._reward_ids = set(self._consolidated.get("reward_ids", []))
            self._shop_entries = set(self._consolidated.get("shop_entries", []))
            
            return True
            
        except Exception as e:
            print(f"Error loading game data: {e}")
            return False
    
    @property
    def items(self) -> Dict[str, GameItem]:
        """Get all game items."""
        if not self._items:
            self.load()
        return self._items
    
    @property
    def colosseum_battles(self) -> Dict[str, ColosseumBattle]:
        """Get all colosseum battles."""
        if not self._colosseum_battles:
            self.load()
        return self._colosseum_battles
    
    @property
    def territories(self) -> Dict[str, Territory]:
        """Get all territories."""
        if not self._territories:
            self.load()
        return self._territories
    
    @property
    def enemies(self) -> Set[str]:
        """Get all enemy IDs."""
        if not self._enemies:
            self.load()
        return self._enemies
    
    @property
    def summons(self) -> Set[str]:
        """Get all summon IDs."""
        if not self._summons:
            self.load()
        return self._summons
    
    @property
    def reward_ids(self) -> Set[str]:
        """Get all reward IDs."""
        if not self._reward_ids:
            self.load()
        return self._reward_ids
    
    def get_items_by_type(self, item_type: ItemType) -> List[GameItem]:
        """Get all items of a specific type."""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def get_colosseum_battles_by_tier(self, tier: str) -> List[ColosseumBattle]:
        """Get all colosseum battles for a specific tier."""
        return [b for b in self.colosseum_battles.values() if b.tier == tier]
    
    def get_colosseum_tiers(self) -> Set[str]:
        """Get all unique colosseum tiers."""
        return {b.tier for b in self.colosseum_battles.values()}


# Global instance
_game_data: Optional[GameDataManager] = None


def get_game_data() -> GameDataManager:
    """Get the global GameDataManager instance."""
    global _game_data
    if _game_data is None:
        _game_data = GameDataManager()
        _game_data.load()
    return _game_data


# Item name mappings (can be populated with actual names later)
ITEM_NAME_OVERRIDES: Dict[str, str] = {
    # Consumables
    "IT_potion": "Potion",
    "IT_hpotion": "Hi-Potion",
    "IT_gpotion": "Giga-Potion",
    "IT_mpotion": "Mega-Potion",
    "IT_phenxtal": "Phoenix Down",
    "IT_echo": "Echo Mist",
    "IT_soft": "Soft",
    "IT_maidenOfKiss": "Maiden's Kiss",
    "IT_poisona": "Antidote",
    "IT_grenade": "Grenade",
    "IT_supergrenade": "Mega Grenade",
    "IT_molotov": "Molotov",
    "IT_gravity": "Gravity Ball",
    "IT_slow": "Mr. Slowpoke",
    "IT_speed": "Speed Drink",
    "IT_stimulant": "Stimulant",
    "IT_sedative": "Sedative",
    "IT_toxic": "Toxic Frog",
    "IT_universal": "Universal Medicine",
}
