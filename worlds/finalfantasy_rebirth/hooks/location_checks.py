"""
Location Check Definitions for Final Fantasy VII: Rebirth
================================================================

Defines how in-game events map to Archipelago location checks.
When the Lua mod detects a triggering event, it uses this mapping
to report the correct location to the AP server.

Game IDs are loaded from the data tables which were extracted from
the game's UAsset files (Colosseum.json, EnemyTerritory.json, etc.)

Check Types:
    - BOSS: Defeating a boss
    - COLOSSEUM: Completing a colosseum battle
    - SUMMON: Completing a summon battle (VR)
    - CHEST: Opening a chest (future)
    - QUEST: Completing a side quest
    - MINIGAME: Completing a minigame
    - TERRITORY: Clearing a territory battle
    - STORY: Story progression point

Each check defines:
    - The AP location name it corresponds to
    - What game event triggers it
    - How to detect it in the Lua mod

Usage (Lua side):
    -- When boss defeated:
    local trigger = "boss_defeated:midgardsormr"
    local locationName = GetLocationByTrigger(trigger)
    if locationName then
        SendLocationCheck(locationName)
    end
"""
from enum import IntEnum, auto
from typing import Dict, List, NamedTuple, Optional, Set

from ..data.location_tables import (
    STORY_LOCATIONS,
    VR_SUMMON_BATTLES,
    QUEST_LOCATIONS,
    MINIGAME_LOCATIONS,
    FFVIIRLocationData,
)
from ..data.game_loader import get_game_data


class CheckType(IntEnum):
    """Categories of location checks."""
    BOSS = 1
    COLOSSEUM = 2
    SUMMON = 3
    CHEST = 4
    QUEST = 5
    MINIGAME = 6
    TERRITORY = 7
    STORY = 8
    VR_BATTLE = 9


class LocationCheck(NamedTuple):
    """Definition of a location check trigger."""
    location_name: str      # AP location name (must match location_tables.py)
    check_type: CheckType   # Category of check
    trigger_id: str         # Unique trigger identifier
    game_id: str = ""       # Internal game ID (from data exports)
    
    # Trigger detection info
    hook_type: str = ""         # Type of hook: "function", "flag", "event"
    hook_target: str = ""       # What to hook/monitor
    hook_condition: str = ""    # Condition to evaluate
    
    # Game data references
    game_object: str = ""       # UE4 object path if relevant


def _infer_check_type(location_type: str) -> CheckType:
    """Infer CheckType from location_type string."""
    return {
        "story": CheckType.STORY,
        "boss": CheckType.BOSS,
        "colosseum": CheckType.COLOSSEUM,
        "summon_battle": CheckType.SUMMON,
        "vr_battle": CheckType.VR_BATTLE,
        "quest": CheckType.QUEST,
        "minigame": CheckType.MINIGAME,
        "territory": CheckType.TERRITORY,
        "chest": CheckType.CHEST,
    }.get(location_type, CheckType.STORY)


def _build_checks_from_location_tables() -> Dict[str, LocationCheck]:
    """Build location checks from the data tables."""
    checks = {}
    
    # Process story locations
    for name, loc_data in STORY_LOCATIONS.items():
        check_type = _infer_check_type(loc_data.location_type)
        trigger_id = name.lower().replace(" ", "_").replace(":", "")
        
        # Determine hook based on type
        if loc_data.location_type == "boss":
            hook_type = "event"
            hook_target = "OnBossDefeated"
        else:
            hook_type = "flag"
            hook_target = "OnStoryProgress"
        
        checks[trigger_id] = LocationCheck(
            location_name=name,
            check_type=check_type,
            trigger_id=trigger_id,
            game_id=loc_data.game_id,
            hook_type=hook_type,
            hook_target=hook_target,
        )
    
    # Process VR summon battles
    for name, loc_data in VR_SUMMON_BATTLES.items():
        trigger_id = name.lower().replace(" ", "_").replace(":", "").replace("-", "_")
        checks[trigger_id] = LocationCheck(
            location_name=name,
            check_type=CheckType.SUMMON,
            trigger_id=trigger_id,
            game_id=loc_data.game_id,
            hook_type="event",
            hook_target="OnVRBattleComplete",
        )
    
    # Process quest locations
    for name, loc_data in QUEST_LOCATIONS.items():
        trigger_id = name.lower().replace(" ", "_").replace(":", "")
        checks[trigger_id] = LocationCheck(
            location_name=name,
            check_type=CheckType.QUEST,
            trigger_id=trigger_id,
            game_id=loc_data.game_id,
            hook_type="event",
            hook_target="OnQuestComplete",
        )
    
    # Process minigame locations
    for name, loc_data in MINIGAME_LOCATIONS.items():
        trigger_id = name.lower().replace(" ", "_").replace(":", "").replace("'", "")
        checks[trigger_id] = LocationCheck(
            location_name=name,
            check_type=CheckType.MINIGAME,
            trigger_id=trigger_id,
            game_id=loc_data.game_id,
            hook_type="event",
            hook_target="OnMinigameComplete",
        )
    
    return checks


def _build_colosseum_checks() -> Dict[str, LocationCheck]:
    """Build colosseum checks from game data."""
    checks = {}
    game_data = get_game_data()
    
    for battle_id, battle in game_data.colosseum_battles.items():
        # Create AP-style location name
        location_name = f"Colosseum: {battle.display_name}"
        trigger_id = battle_id.lower()
        
        checks[trigger_id] = LocationCheck(
            location_name=location_name,
            check_type=CheckType.COLOSSEUM,
            trigger_id=trigger_id,
            game_id=battle_id,
            hook_type="event",
            hook_target="OnColosseumBattleComplete",
            hook_condition=f"battle_id == '{battle_id}'",
        )
    
    return checks


def _build_territory_checks() -> Dict[str, LocationCheck]:
    """Build territory checks from game data."""
    checks = {}
    game_data = get_game_data()
    
    for ter_id, territory in game_data.territories.items():
        location_name = f"Territory: {territory.display_name}"
        trigger_id = ter_id.lower()
        
        checks[trigger_id] = LocationCheck(
            location_name=location_name,
            check_type=CheckType.TERRITORY,
            trigger_id=trigger_id,
            game_id=ter_id,
            hook_type="event",
            hook_target="OnTerritoryCleared",
            hook_condition=f"territory_id == '{ter_id}'",
        )
    
    return checks


# =============================================================================
# Combined Check Registry (built lazily)
# =============================================================================

_LOCATION_CHECKS: Optional[Dict[str, LocationCheck]] = None
_TRIGGER_TO_LOCATION: Optional[Dict[str, LocationCheck]] = None


def _get_all_checks() -> Dict[str, LocationCheck]:
    """Get or build the complete checks dictionary."""
    global _LOCATION_CHECKS, _TRIGGER_TO_LOCATION
    if _LOCATION_CHECKS is None:
        _LOCATION_CHECKS = _build_checks_from_location_tables()
        _LOCATION_CHECKS.update(_build_colosseum_checks())
        _LOCATION_CHECKS.update(_build_territory_checks())
        
        # Build reverse lookup
        _TRIGGER_TO_LOCATION = {
            check.trigger_id: check 
            for check in _LOCATION_CHECKS.values()
        }
    return _LOCATION_CHECKS


def _get_trigger_lookup() -> Dict[str, LocationCheck]:
    """Get the trigger -> location lookup dict."""
    global _TRIGGER_TO_LOCATION
    if _TRIGGER_TO_LOCATION is None:
        _get_all_checks()  # This builds both dicts
    return _TRIGGER_TO_LOCATION or {}


# Public alias
LOCATION_CHECKS = property(lambda self: _get_all_checks())


# =============================================================================
# Lookup Functions
# =============================================================================

def get_check_trigger(location_name: str) -> Optional[str]:
    """Get the trigger ID for a location name."""
    for check in _get_all_checks().values():
        if check.location_name == location_name:
            return check.trigger_id
    return None


def get_location_by_trigger(trigger_id: str) -> Optional[LocationCheck]:
    """Get location check data by its trigger ID."""
    return _get_trigger_lookup().get(trigger_id)


def get_location_name_by_trigger(trigger_id: str) -> Optional[str]:
    """Get AP location name from a trigger ID."""
    check = _get_trigger_lookup().get(trigger_id)
    return check.location_name if check else None


def get_game_id_for_location(location_name: str) -> Optional[str]:
    """Get the game ID for a location name."""
    trigger = get_check_trigger(location_name)
    if trigger:
        check = get_location_by_trigger(trigger)
        if check:
            return check.game_id
    return None


def get_checks_by_type(check_type: CheckType) -> List[LocationCheck]:
    """Get all checks of a specific type."""
    return [c for c in _get_all_checks().values() if c.check_type == check_type]


def get_checks_by_hook(hook_target: str) -> List[LocationCheck]:
    """Get all checks that use a specific hook target."""
    return [c for c in _get_all_checks().values() if c.hook_target == hook_target]


def get_all_triggers() -> Set[str]:
    """Get all registered trigger IDs."""
    return set(_get_trigger_lookup().keys())


def get_all_game_ids() -> Dict[str, str]:
    """Get mapping of location names to game IDs."""
    return {check.location_name: check.game_id for check in _get_all_checks().values() if check.game_id}


def validate_location_exists(location_name: str, location_table: dict) -> bool:
    """Check if a location name exists in the AP location table."""
    return location_name in location_table
