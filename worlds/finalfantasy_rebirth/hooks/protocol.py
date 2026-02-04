"""
Communication Protocol for Final Fantasy VII: Rebirth
================================================================

Defines the message format for communication between the Archipelago
client (or APWorld output) and the Lua mod. Messages are serialized
as JSON for easy parsing on both sides.

Message Types:
    - ITEM_RECEIVED: AP server sent an item to grant
    - LOCATION_CHECKED: Mod reports a location was checked  
    - STATE_QUERY: Request game state information
    - STATE_RESPONSE: Response to state query
    - COMMAND: Execute a game command
    - COMMAND_RESULT: Result of command execution
    - SYNC: Synchronization message
    - ERROR: Error message

Protocol Flow:
    AP Server -> Client -> Mod: ITEM_RECEIVED
    Mod -> Client -> AP Server: LOCATION_CHECKED
    Client <-> Mod: STATE_QUERY/RESPONSE, COMMAND/RESULT

Message Format (JSON):
    {
        "type": "item_received",
        "id": 12345,
        "timestamp": 1234567890,
        "data": { ... type-specific data ... }
    }
"""
from enum import IntEnum, auto
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import json
import time


class MessageType(IntEnum):
    """Types of protocol messages."""
    # Core AP messages
    ITEM_RECEIVED = 1
    LOCATION_CHECKED = 2
    
    # State messages
    STATE_QUERY = 10
    STATE_RESPONSE = 11
    
    # Command messages
    COMMAND = 20
    COMMAND_RESULT = 21
    
    # Sync messages
    SYNC_REQUEST = 30
    SYNC_RESPONSE = 31
    
    # DeathLink
    DEATH_LINK = 40
    
    # Utility
    HEARTBEAT = 50
    ERROR = 99


@dataclass
class ModMessage:
    """
    Base message structure for mod communication.
    
    All messages between the client and mod use this format.
    """
    type: MessageType
    data: Dict[str, Any] = field(default_factory=dict)
    id: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            "type": self.type.name.lower(),
            "type_id": int(self.type),
            "id": self.id,
            "timestamp": self.timestamp,
            "data": self.data,
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.name.lower(),
            "type_id": int(self.type),
            "id": self.id,
            "timestamp": self.timestamp,
            "data": self.data,
        }
    
    @classmethod
    def from_json(cls, json_str: str) -> "ModMessage":
        """Deserialize message from JSON string."""
        obj = json.loads(json_str)
        return cls(
            type=MessageType(obj.get("type_id", 99)),
            data=obj.get("data", {}),
            id=obj.get("id", 0),
            timestamp=obj.get("timestamp", time.time()),
        )


# =============================================================================
# Message Builders
# =============================================================================

_message_counter = 0


def _next_id() -> int:
    """Get next message ID."""
    global _message_counter
    _message_counter += 1
    return _message_counter


def create_item_message(
    item_name: str,
    item_id: int,
    sender_name: str,
    sender_slot: int,
    item_index: int,
    grant_data: Optional[Dict[str, Any]] = None,
) -> ModMessage:
    """
    Create an item received message.
    
    Args:
        item_name: AP item name
        item_id: AP item ID
        sender_name: Name of player who sent item
        sender_slot: Slot number of sender
        item_index: Index in received items list
        grant_data: Optional grant data from item_grants module
    
    Returns:
        ModMessage ready to send to Lua mod
    """
    data = {
        "item_name": item_name,
        "item_id": item_id,
        "sender_name": sender_name,
        "sender_slot": sender_slot,
        "item_index": item_index,
    }
    
    if grant_data:
        data["grant"] = grant_data
    
    return ModMessage(
        type=MessageType.ITEM_RECEIVED,
        data=data,
        id=_next_id(),
    )


def create_location_message(
    location_name: str,
    location_id: int,
    trigger_id: str = "",
) -> ModMessage:
    """
    Create a location checked message.
    
    Args:
        location_name: AP location name
        location_id: AP location ID
        trigger_id: Internal trigger ID that caused the check
    
    Returns:
        ModMessage from Lua mod to client
    """
    return ModMessage(
        type=MessageType.LOCATION_CHECKED,
        data={
            "location_name": location_name,
            "location_id": location_id,
            "trigger_id": trigger_id,
        },
        id=_next_id(),
    )


def create_state_message(
    query_type: int,
    response_data: Any,
) -> ModMessage:
    """
    Create a state response message.
    
    Args:
        query_type: The QueryType that was requested
        response_data: The response data
    
    Returns:
        ModMessage with state response
    """
    return ModMessage(
        type=MessageType.STATE_RESPONSE,
        data={
            "query_type": query_type,
            "result": response_data,
        },
        id=_next_id(),
    )


def create_command_message(
    command_type: int,
    command_function: str,
    params: Dict[str, Any],
) -> ModMessage:
    """
    Create a command message to send to the mod.
    
    Args:
        command_type: The CommandType to execute
        command_function: Lua function name to call
        params: Parameters for the command
    
    Returns:
        ModMessage with command
    """
    return ModMessage(
        type=MessageType.COMMAND,
        data={
            "command_type": command_type,
            "function": command_function,
            "params": params,
        },
        id=_next_id(),
    )


def create_death_link_message(
    source: str,
    cause: str = "",
) -> ModMessage:
    """
    Create a DeathLink message.
    
    Args:
        source: Player/world that triggered the death
        cause: Optional cause of death
    
    Returns:
        ModMessage for DeathLink
    """
    return ModMessage(
        type=MessageType.DEATH_LINK,
        data={
            "source": source,
            "cause": cause,
        },
        id=_next_id(),
    )


def create_sync_request() -> ModMessage:
    """Create a sync request message to get current game state."""
    return ModMessage(
        type=MessageType.SYNC_REQUEST,
        data={
            "request_locations": True,
            "request_inventory": True,
            "request_progress": True,
        },
        id=_next_id(),
    )


def create_sync_response(
    checked_locations: List[int],
    received_items: int,
    current_chapter: int,
    additional_data: Optional[Dict[str, Any]] = None,
) -> ModMessage:
    """
    Create a sync response message with current game state.
    
    Args:
        checked_locations: List of checked location IDs
        received_items: Index of last received item
        current_chapter: Current story chapter
        additional_data: Any additional state data
    
    Returns:
        ModMessage with sync data
    """
    data = {
        "checked_locations": checked_locations,
        "received_item_index": received_items,
        "current_chapter": current_chapter,
    }
    
    if additional_data:
        data.update(additional_data)
    
    return ModMessage(
        type=MessageType.SYNC_RESPONSE,
        data=data,
        id=_next_id(),
    )


def create_error_message(
    error_code: int,
    error_message: str,
    details: Optional[Dict[str, Any]] = None,
) -> ModMessage:
    """Create an error message."""
    return ModMessage(
        type=MessageType.ERROR,
        data={
            "code": error_code,
            "message": error_message,
            "details": details or {},
        },
        id=_next_id(),
    )


def create_heartbeat() -> ModMessage:
    """Create a heartbeat message for connection keepalive."""
    return ModMessage(
        type=MessageType.HEARTBEAT,
        data={},
        id=_next_id(),
    )


# =============================================================================
# Message Parsing
# =============================================================================

def parse_mod_message(json_str: str) -> Optional[ModMessage]:
    """
    Parse a message from the Lua mod.
    
    Args:
        json_str: JSON string from mod
    
    Returns:
        ModMessage or None if parsing failed
    """
    try:
        return ModMessage.from_json(json_str)
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def parse_location_check(msg: ModMessage) -> Optional[Dict[str, Any]]:
    """
    Parse location check data from a message.
    
    Returns:
        Dict with location_name, location_id, trigger_id
        or None if not a location check message
    """
    if msg.type != MessageType.LOCATION_CHECKED:
        return None
    
    return {
        "location_name": msg.data.get("location_name", ""),
        "location_id": msg.data.get("location_id", 0),
        "trigger_id": msg.data.get("trigger_id", ""),
    }


def parse_sync_response(msg: ModMessage) -> Optional[Dict[str, Any]]:
    """
    Parse sync response data from a message.
    
    Returns:
        Dict with sync data or None if not a sync response
    """
    if msg.type != MessageType.SYNC_RESPONSE:
        return None
    
    return {
        "checked_locations": msg.data.get("checked_locations", []),
        "received_item_index": msg.data.get("received_item_index", 0),
        "current_chapter": msg.data.get("current_chapter", 1),
    }
