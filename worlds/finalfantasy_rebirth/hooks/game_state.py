"""
Game State Queries and Commands for Final Fantasy VII: Rebirth
================================================================

Defines the interface for querying game state and sending commands
to the game. The Lua mod implements these queries/commands and
reports results back to the AP client.

Query Types:
    - Player state (HP, MP, level, etc.)
    - Inventory state (items, materia, equipment)
    - Progress state (chapter, locations checked)
    - Party state (members, formation)

Command Types:
    - Grant item
    - Apply effect (trap)
    - Trigger death (DeathLink)
    - Set game flag
    - Unlock feature

Usage (Lua side):
    -- Respond to query:
    function HandleQuery(queryType)
        if queryType == QueryType.PLAYER_HP then
            return GetPlayerHP()
        end
    end
    
    -- Execute command:
    function HandleCommand(cmd)
        if cmd.type == CommandType.GRANT_ITEM then
            GrantItemToPlayer(cmd.item_id, cmd.quantity)
        end
    end
"""
from enum import IntEnum, auto
from typing import Dict, List, NamedTuple, Optional, Any


class QueryType(IntEnum):
    """Types of game state queries."""
    # Player State
    PLAYER_HP = 1
    PLAYER_MP = 2
    PLAYER_LEVEL = 3
    PLAYER_GIL = 4
    PLAYER_LOCATION = 5
    
    # Progress State
    CURRENT_CHAPTER = 10
    CHECKED_LOCATIONS = 11
    UNLOCKED_CHAPTERS = 12
    DEFEATED_BOSSES = 13
    
    # Party State
    PARTY_MEMBERS = 20
    ACTIVE_PARTY = 21
    
    # Inventory State
    ITEM_COUNT = 30
    HAS_ITEM = 31
    MATERIA_LIST = 32
    KEY_ITEMS = 33
    
    # Game State
    IS_IN_BATTLE = 40
    IS_IN_MENU = 41
    IS_CUTSCENE = 42
    CAN_RECEIVE_ITEMS = 43


class CommandType(IntEnum):
    """Types of game commands."""
    # Item Commands
    GRANT_ITEM = 1
    GRANT_MATERIA = 2
    GRANT_GIL = 3
    GRANT_KEY_ITEM = 4
    
    # Effect Commands
    APPLY_TRAP = 10
    HEAL_PARTY = 11
    DAMAGE_PARTY = 12
    
    # State Commands
    SET_FLAG = 20
    UNLOCK_CHAPTER = 21
    UNLOCK_PARTY_MEMBER = 22
    
    # DeathLink Commands
    TRIGGER_DEATH = 30
    
    # UI Commands
    SHOW_MESSAGE = 40
    SHOW_NOTIFICATION = 41


class GameStateQuery(NamedTuple):
    """Definition of a game state query."""
    query_type: QueryType
    name: str
    description: str
    return_type: str        # "int", "bool", "string", "list", "dict"
    lua_function: str       # Lua function to call


class GameCommand(NamedTuple):
    """Definition of a game command."""
    command_type: CommandType
    name: str
    description: str
    parameters: List[str]   # Required parameters
    lua_function: str       # Lua function to call


# =============================================================================
# State Query Definitions
# =============================================================================

STATE_QUERIES: Dict[QueryType, GameStateQuery] = {
    # Player State
    QueryType.PLAYER_HP: GameStateQuery(
        query_type=QueryType.PLAYER_HP,
        name="Player HP",
        description="Get current HP of party leader",
        return_type="int",
        lua_function="GetPlayerHP",
    ),
    QueryType.PLAYER_MP: GameStateQuery(
        query_type=QueryType.PLAYER_MP,
        name="Player MP",
        description="Get current MP of party leader",
        return_type="int",
        lua_function="GetPlayerMP",
    ),
    QueryType.PLAYER_LEVEL: GameStateQuery(
        query_type=QueryType.PLAYER_LEVEL,
        name="Player Level",
        description="Get level of party leader (Cloud)",
        return_type="int",
        lua_function="GetPlayerLevel",
    ),
    QueryType.PLAYER_GIL: GameStateQuery(
        query_type=QueryType.PLAYER_GIL,
        name="Gil",
        description="Get current Gil amount",
        return_type="int",
        lua_function="GetGil",
    ),
    QueryType.PLAYER_LOCATION: GameStateQuery(
        query_type=QueryType.PLAYER_LOCATION,
        name="Player Location",
        description="Get current map/area name",
        return_type="string",
        lua_function="GetCurrentMap",
    ),
    
    # Progress State
    QueryType.CURRENT_CHAPTER: GameStateQuery(
        query_type=QueryType.CURRENT_CHAPTER,
        name="Current Chapter",
        description="Get current story chapter number",
        return_type="int",
        lua_function="GetCurrentChapter",
    ),
    QueryType.CHECKED_LOCATIONS: GameStateQuery(
        query_type=QueryType.CHECKED_LOCATIONS,
        name="Checked Locations",
        description="Get list of checked AP location IDs",
        return_type="list",
        lua_function="GetCheckedLocations",
    ),
    QueryType.UNLOCKED_CHAPTERS: GameStateQuery(
        query_type=QueryType.UNLOCKED_CHAPTERS,
        name="Unlocked Chapters",
        description="Get list of unlocked chapter numbers",
        return_type="list",
        lua_function="GetUnlockedChapters",
    ),
    QueryType.DEFEATED_BOSSES: GameStateQuery(
        query_type=QueryType.DEFEATED_BOSSES,
        name="Defeated Bosses",
        description="Get list of defeated boss IDs",
        return_type="list",
        lua_function="GetDefeatedBosses",
    ),
    
    # Party State
    QueryType.PARTY_MEMBERS: GameStateQuery(
        query_type=QueryType.PARTY_MEMBERS,
        name="Party Members",
        description="Get list of unlocked party members",
        return_type="list",
        lua_function="GetPartyMembers",
    ),
    QueryType.ACTIVE_PARTY: GameStateQuery(
        query_type=QueryType.ACTIVE_PARTY,
        name="Active Party",
        description="Get current active party formation",
        return_type="list",
        lua_function="GetActiveParty",
    ),
    
    # Inventory State
    QueryType.ITEM_COUNT: GameStateQuery(
        query_type=QueryType.ITEM_COUNT,
        name="Item Count",
        description="Get count of specific item (requires item_id param)",
        return_type="int",
        lua_function="GetItemCount",
    ),
    QueryType.HAS_ITEM: GameStateQuery(
        query_type=QueryType.HAS_ITEM,
        name="Has Item",
        description="Check if player has specific item",
        return_type="bool",
        lua_function="HasItem",
    ),
    QueryType.MATERIA_LIST: GameStateQuery(
        query_type=QueryType.MATERIA_LIST,
        name="Materia List",
        description="Get list of owned materia IDs",
        return_type="list",
        lua_function="GetMateriaList",
    ),
    QueryType.KEY_ITEMS: GameStateQuery(
        query_type=QueryType.KEY_ITEMS,
        name="Key Items",
        description="Get list of owned key item IDs",
        return_type="list",
        lua_function="GetKeyItems",
    ),
    
    # Game State
    QueryType.IS_IN_BATTLE: GameStateQuery(
        query_type=QueryType.IS_IN_BATTLE,
        name="In Battle",
        description="Check if currently in battle",
        return_type="bool",
        lua_function="IsInBattle",
    ),
    QueryType.IS_IN_MENU: GameStateQuery(
        query_type=QueryType.IS_IN_MENU,
        name="In Menu",
        description="Check if menu is open",
        return_type="bool",
        lua_function="IsInMenu",
    ),
    QueryType.IS_CUTSCENE: GameStateQuery(
        query_type=QueryType.IS_CUTSCENE,
        name="In Cutscene",
        description="Check if cutscene is playing",
        return_type="bool",
        lua_function="IsInCutscene",
    ),
    QueryType.CAN_RECEIVE_ITEMS: GameStateQuery(
        query_type=QueryType.CAN_RECEIVE_ITEMS,
        name="Can Receive Items",
        description="Check if safe to grant items (not in battle/cutscene)",
        return_type="bool",
        lua_function="CanReceiveItems",
    ),
}


# =============================================================================
# Command Definitions
# =============================================================================

GAME_COMMANDS: Dict[CommandType, GameCommand] = {
    # Item Commands
    CommandType.GRANT_ITEM: GameCommand(
        command_type=CommandType.GRANT_ITEM,
        name="Grant Item",
        description="Add item to player inventory",
        parameters=["item_id", "quantity"],
        lua_function="GrantItem",
    ),
    CommandType.GRANT_MATERIA: GameCommand(
        command_type=CommandType.GRANT_MATERIA,
        name="Grant Materia",
        description="Add materia to player inventory",
        parameters=["materia_id"],
        lua_function="GrantMateria",
    ),
    CommandType.GRANT_GIL: GameCommand(
        command_type=CommandType.GRANT_GIL,
        name="Grant Gil",
        description="Add Gil to player",
        parameters=["amount"],
        lua_function="GrantGil",
    ),
    CommandType.GRANT_KEY_ITEM: GameCommand(
        command_type=CommandType.GRANT_KEY_ITEM,
        name="Grant Key Item",
        description="Add key item to player",
        parameters=["key_item_id"],
        lua_function="GrantKeyItem",
    ),
    
    # Effect Commands
    CommandType.APPLY_TRAP: GameCommand(
        command_type=CommandType.APPLY_TRAP,
        name="Apply Trap",
        description="Apply trap effect to player",
        parameters=["trap_type"],
        lua_function="ApplyTrap",
    ),
    CommandType.HEAL_PARTY: GameCommand(
        command_type=CommandType.HEAL_PARTY,
        name="Heal Party",
        description="Heal entire party (for testing)",
        parameters=[],
        lua_function="HealParty",
    ),
    CommandType.DAMAGE_PARTY: GameCommand(
        command_type=CommandType.DAMAGE_PARTY,
        name="Damage Party",
        description="Damage party (for traps)",
        parameters=["damage_percent"],
        lua_function="DamageParty",
    ),
    
    # State Commands
    CommandType.SET_FLAG: GameCommand(
        command_type=CommandType.SET_FLAG,
        name="Set Flag",
        description="Set a game flag",
        parameters=["flag_name", "value"],
        lua_function="SetGameFlag",
    ),
    CommandType.UNLOCK_CHAPTER: GameCommand(
        command_type=CommandType.UNLOCK_CHAPTER,
        name="Unlock Chapter",
        description="Unlock access to a chapter",
        parameters=["chapter_number"],
        lua_function="UnlockChapter",
    ),
    CommandType.UNLOCK_PARTY_MEMBER: GameCommand(
        command_type=CommandType.UNLOCK_PARTY_MEMBER,
        name="Unlock Party Member",
        description="Make a party member available",
        parameters=["member_id"],
        lua_function="UnlockPartyMember",
    ),
    
    # DeathLink
    CommandType.TRIGGER_DEATH: GameCommand(
        command_type=CommandType.TRIGGER_DEATH,
        name="Trigger Death",
        description="Kill the player (DeathLink)",
        parameters=["source", "cause"],
        lua_function="TriggerDeath",
    ),
    
    # UI Commands
    CommandType.SHOW_MESSAGE: GameCommand(
        command_type=CommandType.SHOW_MESSAGE,
        name="Show Message",
        description="Display a message to the player",
        parameters=["message", "duration"],
        lua_function="ShowMessage",
    ),
    CommandType.SHOW_NOTIFICATION: GameCommand(
        command_type=CommandType.SHOW_NOTIFICATION,
        name="Show Notification",
        description="Show item received notification",
        parameters=["item_name", "sender_name"],
        lua_function="ShowItemNotification",
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_query(query_type: QueryType) -> Optional[GameStateQuery]:
    """Get query definition by type."""
    return STATE_QUERIES.get(query_type)


def get_command(command_type: CommandType) -> Optional[GameCommand]:
    """Get command definition by type."""
    return GAME_COMMANDS.get(command_type)


def get_query_lua_function(query_type: QueryType) -> str:
    """Get the Lua function name for a query type."""
    query = STATE_QUERIES.get(query_type)
    return query.lua_function if query else ""


def get_command_lua_function(command_type: CommandType) -> str:
    """Get the Lua function name for a command type."""
    command = GAME_COMMANDS.get(command_type)
    return command.lua_function if command else ""


def build_command_message(
    command_type: CommandType, 
    **params
) -> Dict[str, Any]:
    """Build a command message to send to the Lua mod."""
    command = GAME_COMMANDS.get(command_type)
    if not command:
        return {}
    
    return {
        "type": "command",
        "command": int(command_type),
        "function": command.lua_function,
        "params": params,
    }


def build_query_message(
    query_type: QueryType,
    **params
) -> Dict[str, Any]:
    """Build a query message to send to the Lua mod."""
    query = STATE_QUERIES.get(query_type)
    if not query:
        return {}
    
    return {
        "type": "query",
        "query": int(query_type),
        "function": query.lua_function,
        "params": params,
    }
