"""
Game Event Definitions for Final Fantasy VII: Rebirth
================================================================

Defines all game events that the Lua mod can detect and report.
Events are categorized by type and mapped to unique IDs that both
the Python APWorld and Lua mod use for communication.

Event Types:
    - STORY: Main story progression events
    - BOSS: Boss defeat events
    - COLOSSEUM: Colosseum battle completions
    - SUMMON: Summon acquisition/battle events
    - QUEST: Side quest completions
    - MINIGAME: Minigame completions
    - DISCOVERY: World exploration events
    - DEATH: Player death events (for DeathLink)

Usage (Lua side):
    -- When event detected:
    ReportEvent(EventType.BOSS, "jenova_birth")
    
Usage (Python side):
    event = get_event_by_id(event_id)
    if event.type == EventType.BOSS:
        # Handle boss defeat
"""
from enum import IntEnum, auto
from typing import Dict, List, NamedTuple, Optional


class EventType(IntEnum):
    """Categories of game events."""
    STORY = 1
    BOSS = 2
    COLOSSEUM = 3
    SUMMON = 4
    QUEST = 5
    MINIGAME = 6
    DISCOVERY = 7
    TERRITORY = 8
    DEATH = 9
    CHAPTER = 10
    GOAL = 11


class GameEvent(NamedTuple):
    """Definition of a game event the mod can detect."""
    event_id: str           # Unique string identifier
    event_type: EventType   # Category of event
    display_name: str       # Human-readable name
    description: str        # What triggers this event
    chapter: int = 0        # Chapter where event can occur (0 = any)
    
    # Lua hook information
    hook_function: str = ""      # UE4SS function to hook
    hook_object: str = ""        # UE4 object path to monitor
    hook_condition: str = ""     # Condition to check


# =============================================================================
# Story Events - Main story progression points
# =============================================================================

STORY_EVENTS: Dict[str, GameEvent] = {
    "story_chapter_1_complete": GameEvent(
        event_id="story_chapter_1_complete",
        event_type=EventType.STORY,
        display_name="Chapter 1 Complete",
        description="Completed Chapter 1 - Fall of a Hero",
        chapter=1,
        hook_function="OnChapterComplete",
        hook_condition="chapter_id == 1",
    ),
    "story_chapter_2_complete": GameEvent(
        event_id="story_chapter_2_complete",
        event_type=EventType.STORY,
        display_name="Chapter 2 Complete",
        description="Completed Chapter 2 - A New Journey Begins",
        chapter=2,
    ),
    # TODO: Add remaining chapters 3-14
}


# =============================================================================
# Boss Events - Major boss defeats
# =============================================================================

BOSS_EVENTS: Dict[str, GameEvent] = {
    "boss_midgardsormr": GameEvent(
        event_id="boss_midgardsormr",
        event_type=EventType.BOSS,
        display_name="Midgardsormr Defeated",
        description="Defeated Midgardsormr in the Grasslands",
        chapter=2,
        hook_function="OnEnemyDefeated",
        hook_object="/Game/Battle/Enemy/Midgardsormr",
    ),
    "boss_jenova_birth": GameEvent(
        event_id="boss_jenova_birth",
        event_type=EventType.BOSS,
        display_name="Jenova Birth Defeated",
        description="Defeated Jenova Birth on the cargo ship",
        chapter=4,
    ),
    "boss_dyne": GameEvent(
        event_id="boss_dyne",
        event_type=EventType.BOSS,
        display_name="Dyne Defeated",
        description="Defeated Dyne in Corel Prison",
        chapter=8,
    ),
    "boss_gi_nattak": GameEvent(
        event_id="boss_gi_nattak",
        event_type=EventType.BOSS,
        display_name="Gi Nattak Defeated",
        description="Defeated Gi Nattak in the Cave of the Gi",
        chapter=10,
    ),
    "boss_lost_number": GameEvent(
        event_id="boss_lost_number",
        event_type=EventType.BOSS,
        display_name="Lost Number Defeated",
        description="Defeated Lost Number in Shinra Manor",
        chapter=11,
    ),
    # TODO: Add remaining bosses
}


# =============================================================================
# Colosseum Events - Battle arena completions
# =============================================================================

COLOSSEUM_EVENTS: Dict[str, GameEvent] = {
    # These will be populated from game data
    # Format: "colosseum_{battle_id}"
}


# =============================================================================
# Summon Events - Summon materia acquisition
# =============================================================================

SUMMON_EVENTS: Dict[str, GameEvent] = {
    "summon_ifrit": GameEvent(
        event_id="summon_ifrit",
        event_type=EventType.SUMMON,
        display_name="Ifrit Obtained",
        description="Obtained Ifrit Summon Materia",
        hook_function="OnItemObtained",
        hook_condition="item_type == SUMMON_MATERIA",
    ),
    "summon_shiva": GameEvent(
        event_id="summon_shiva",
        event_type=EventType.SUMMON,
        display_name="Shiva Obtained", 
        description="Obtained Shiva Summon Materia",
    ),
    "summon_ramuh": GameEvent(
        event_id="summon_ramuh",
        event_type=EventType.SUMMON,
        display_name="Ramuh Obtained",
        description="Obtained Ramuh Summon Materia",
    ),
    "summon_titan": GameEvent(
        event_id="summon_titan",
        event_type=EventType.SUMMON,
        display_name="Titan Obtained",
        description="Obtained Titan Summon Materia",
    ),
    "summon_odin": GameEvent(
        event_id="summon_odin",
        event_type=EventType.SUMMON,
        display_name="Odin Obtained",
        description="Obtained Odin Summon Materia",
    ),
    "summon_bahamut": GameEvent(
        event_id="summon_bahamut",
        event_type=EventType.SUMMON,
        display_name="Bahamut Obtained",
        description="Obtained Bahamut Summon Materia",
    ),
    "summon_alexander": GameEvent(
        event_id="summon_alexander",
        event_type=EventType.SUMMON,
        display_name="Alexander Obtained",
        description="Obtained Alexander Summon Materia",
    ),
    "summon_kujata": GameEvent(
        event_id="summon_kujata",
        event_type=EventType.SUMMON,
        display_name="Kujata Obtained",
        description="Obtained Kujata Summon Materia",
    ),
    "summon_phoenix": GameEvent(
        event_id="summon_phoenix",
        event_type=EventType.SUMMON,
        display_name="Phoenix Obtained",
        description="Obtained Phoenix Summon Materia",
    ),
}


# =============================================================================
# Quest Events - Side quest completions
# =============================================================================

QUEST_EVENTS: Dict[str, GameEvent] = {
    # TODO: Populate from game data
    # Format: "quest_{quest_id}"
}


# =============================================================================
# Minigame Events - Minigame completions
# =============================================================================

MINIGAME_EVENTS: Dict[str, GameEvent] = {
    "minigame_qb_grasslands": GameEvent(
        event_id="minigame_qb_grasslands",
        event_type=EventType.MINIGAME,
        display_name="Queen's Blood - Grasslands Champion",
        description="Won all Queen's Blood matches in Grasslands region",
        chapter=2,
    ),
    "minigame_chocobo_race_1": GameEvent(
        event_id="minigame_chocobo_race_1",
        event_type=EventType.MINIGAME,
        display_name="Chocobo Race - First Victory",
        description="Won first Chocobo race",
        chapter=6,
    ),
    # TODO: Add more minigame events
}


# =============================================================================
# Territory Events - World map encounters
# =============================================================================

TERRITORY_EVENTS: Dict[str, GameEvent] = {
    # TODO: Populate from EnemyTerritory game data
    # Format: "territory_{territory_id}"
}


# =============================================================================
# Death Event - For DeathLink
# =============================================================================

DEATH_EVENTS: Dict[str, GameEvent] = {
    "player_death": GameEvent(
        event_id="player_death",
        event_type=EventType.DEATH,
        display_name="Player Death",
        description="Player party was defeated",
        hook_function="OnGameOver",
    ),
}


# =============================================================================
# Goal Events - Game completion conditions
# =============================================================================

GOAL_EVENTS: Dict[str, GameEvent] = {
    "goal_story_complete": GameEvent(
        event_id="goal_story_complete",
        event_type=EventType.GOAL,
        display_name="Story Complete",
        description="Completed the main story",
    ),
    "goal_all_bosses": GameEvent(
        event_id="goal_all_bosses",
        event_type=EventType.GOAL,
        display_name="All Bosses Defeated",
        description="Defeated all required bosses",
    ),
    "goal_colosseum_champion": GameEvent(
        event_id="goal_colosseum_champion",
        event_type=EventType.GOAL,
        display_name="Colosseum Champion",
        description="Completed all Colosseum tiers",
    ),
}


# =============================================================================
# Combined Event Registry
# =============================================================================

GAME_EVENTS: Dict[str, GameEvent] = {
    **STORY_EVENTS,
    **BOSS_EVENTS,
    **COLOSSEUM_EVENTS,
    **SUMMON_EVENTS,
    **QUEST_EVENTS,
    **MINIGAME_EVENTS,
    **TERRITORY_EVENTS,
    **DEATH_EVENTS,
    **GOAL_EVENTS,
}


# =============================================================================
# Lookup Functions
# =============================================================================

def get_event_id(event_id: str) -> Optional[GameEvent]:
    """Get event by its string ID."""
    return GAME_EVENTS.get(event_id)


def get_event_by_id(event_id: str) -> Optional[GameEvent]:
    """Alias for get_event_id."""
    return get_event_id(event_id)


def get_events_by_type(event_type: EventType) -> List[GameEvent]:
    """Get all events of a specific type."""
    return [e for e in GAME_EVENTS.values() if e.event_type == event_type]


def get_events_by_chapter(chapter: int) -> List[GameEvent]:
    """Get all events that occur in a specific chapter."""
    return [e for e in GAME_EVENTS.values() if e.chapter == chapter or e.chapter == 0]


def get_hookable_events() -> List[GameEvent]:
    """Get all events that have Lua hook information defined."""
    return [e for e in GAME_EVENTS.values() if e.hook_function]
