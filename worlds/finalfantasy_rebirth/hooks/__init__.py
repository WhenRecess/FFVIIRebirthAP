"""
Game Hooks Package for Final Fantasy VII: Rebirth
================================================================

This package defines the interface between the Archipelago world
and the in-game Lua mod (UE4SS). It provides:

1. Event definitions that the Lua mod can trigger
2. Item grant mappings for received items (using real game IDs)
3. Location check mappings for game events (using real game IDs)
4. Game state synchronization data

The hooks package serves as the "contract" between the Python
APWorld (server-side generation) and the Lua mod (client-side
runtime). Both sides must agree on IDs and formats.

Game IDs are loaded from the data tables which were extracted from
the game's UAsset files using the tools in /tools.

Modules:
    - events: Game event definitions and IDs
    - item_grants: How AP items map to game items (with real game IDs)
    - location_checks: What game events trigger AP checks (with real game IDs)
    - game_state: Game state queries and commands
    - protocol: Data format for mod communication

Usage:
    # In Lua mod, when player defeats a boss:
    # CheckLocation("boss_jenova_birth")
    
    # This maps to the AP location via location_checks.py
    
    # When AP sends "Power Wristguards":
    # grant_data = get_grant_data("Power Wristguards")
    # grant_data.game_id == "E_ACC_0001"
"""

from .events import (
    GameEvent,
    EventType,
    GAME_EVENTS,
    get_event_id,
    get_event_by_id,
    get_events_by_type,
    get_events_by_chapter,
)

from .item_grants import (
    ItemGrant,
    GrantType,
    get_grant_data,
    get_game_item_id,
    get_grants_by_type,
    get_grant_function,
    to_lua_table,
    get_all_game_ids as get_all_item_game_ids,
)

from .location_checks import (
    LocationCheck,
    CheckType,
    get_check_trigger,
    get_location_by_trigger,
    get_location_name_by_trigger,
    get_game_id_for_location,
    get_checks_by_type,
    get_checks_by_hook,
    get_all_triggers,
    get_all_game_ids as get_all_location_game_ids,
)

from .game_state import (
    GameStateQuery,
    GameCommand,
    QueryType,
    CommandType,
    STATE_QUERIES,
    GAME_COMMANDS,
    get_query,
    get_command,
    build_command_message,
    build_query_message,
)

from .protocol import (
    ModMessage,
    MessageType,
    create_item_message,
    create_location_message,
    create_state_message,
    create_command_message,
    create_death_link_message,
    create_sync_request,
    create_sync_response,
    parse_mod_message,
)

__all__ = [
    # Events
    "GameEvent",
    "EventType", 
    "GAME_EVENTS",
    "get_event_id",
    "get_event_by_id",
    "get_events_by_type",
    "get_events_by_chapter",
    # Item Grants
    "ItemGrant",
    "GrantType",
    "get_grant_data",
    "get_game_item_id",
    "get_grants_by_type",
    "get_grant_function",
    "to_lua_table",
    "get_all_item_game_ids",
    # Location Checks
    "LocationCheck",
    "CheckType",
    "get_check_trigger",
    "get_location_by_trigger",
    "get_location_name_by_trigger",
    "get_game_id_for_location",
    "get_checks_by_type",
    "get_checks_by_hook",
    "get_all_triggers",
    "get_all_location_game_ids",
    # Game State
    "GameStateQuery",
    "GameCommand",
    "QueryType",
    "CommandType",
    "STATE_QUERIES",
    "GAME_COMMANDS",
    "get_query",
    "get_command",
    "build_command_message",
    "build_query_message",
    # Protocol
    "ModMessage",
    "MessageType",
    "create_item_message",
    "create_location_message",
    "create_state_message",
    "create_command_message",
    "create_death_link_message",
    "create_sync_request",
    "create_sync_response",
    "parse_mod_message",
]
