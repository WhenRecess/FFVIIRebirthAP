"""
Item Grant Definitions for Final Fantasy VII: Rebirth
================================================================

Defines how Archipelago items map to in-game items and how they
should be granted to the player. This is the bridge between AP
item names and the actual game implementation.

Grant Types:
    - INVENTORY: Add to player inventory (consumables, equipment)
    - MATERIA: Add to materia inventory
    - KEY_ITEM: Add to key items
    - GIL: Add currency
    - STAT: Modify player stats
    - UNLOCK: Unlock game feature/area
    - PARTY: Add party member
    - TRAP: Apply negative effect

Game IDs are loaded from the data/exports/item_names.json which
contains the mapping from internal game IDs to display names.

Usage (Lua side):
    local grantData = GetGrantData(itemName)
    if grantData.type == GrantType.MATERIA then
        AddMateria(grantData.game_id, grantData.quantity)
    elseif grantData.type == GrantType.GIL then
        AddGil(grantData.quantity)
    end

Usage (Python side):
    grant_data = get_grant_data("Fire Materia")
    # Serialize to JSON for mod communication
"""
from enum import IntEnum, auto
from typing import Dict, List, NamedTuple, Optional, Any

from ..data.game_loader import get_item_display_name, _ITEM_NAMES, ItemType


class GrantType(IntEnum):
    """How an item should be granted in-game."""
    INVENTORY = 1       # Standard inventory item
    MATERIA = 2         # Materia orb
    KEY_ITEM = 3        # Key item (quest/progression)
    GIL = 4             # Currency
    STAT_BOOST = 5      # Permanent stat increase
    UNLOCK = 6          # Unlock feature/chapter/area
    PARTY_MEMBER = 7    # Unlock party member
    SUMMON = 8          # Summon materia (special materia)
    TRAP = 9            # Negative effect


class ItemGrant(NamedTuple):
    """Definition of how to grant an AP item in-game."""
    ap_item_name: str       # AP item name (must match item_tables.py)
    grant_type: GrantType   # How to grant this item
    game_id: str            # In-game item ID (e.g., "E_ACC_0001")
    quantity: int = 1       # Amount to grant
    display_name: str = ""  # In-game display name (if different)
    
    # Lua hook info
    grant_function: str = ""    # Lua function to call
    grant_params: str = ""      # Additional parameters


def _infer_grant_type(game_id: str) -> GrantType:
    """Infer grant type from game ID prefix."""
    if game_id.startswith("E_ACC") or game_id.startswith("E_ARM"):
        return GrantType.INVENTORY
    elif game_id.startswith("IT_") or game_id.startswith("it_"):
        return GrantType.INVENTORY
    elif game_id.startswith("M_"):
        return GrantType.MATERIA
    elif game_id.startswith("W_"):
        return GrantType.INVENTORY
    elif game_id.startswith("key_"):
        return GrantType.KEY_ITEM
    elif game_id.startswith("mat_"):
        return GrantType.INVENTORY
    return GrantType.INVENTORY


def _get_grant_function(grant_type: GrantType) -> str:
    """Get the Lua function name for a grant type."""
    return {
        GrantType.INVENTORY: "GrantItem",
        GrantType.MATERIA: "GrantMateria",
        GrantType.KEY_ITEM: "GrantKeyItem",
        GrantType.GIL: "GrantGil",
        GrantType.STAT_BOOST: "GrantStatBoost",
        GrantType.UNLOCK: "UnlockFeature",
        GrantType.PARTY_MEMBER: "UnlockPartyMember",
        GrantType.SUMMON: "GrantSummonMateria",
        GrantType.TRAP: "ApplyTrap",
    }.get(grant_type, "GrantItem")


# =============================================================================
# Build grants from game data (item_names.json)
# =============================================================================

def _build_grants_from_game_data() -> Dict[str, ItemGrant]:
    """Build item grants from the loaded game data."""
    grants = {}
    
    for game_id, display_name in _ITEM_NAMES.items():
        # Skip category headers (like "E_ACC" -> "Accessory")
        if "_" not in game_id or game_id.count("_") < 2:
            # Could be a category header, skip if no number suffix
            if not any(c.isdigit() for c in game_id):
                continue
        
        grant_type = _infer_grant_type(game_id)
        grant_func = _get_grant_function(grant_type)
        
        grant = ItemGrant(
            ap_item_name=display_name,
            grant_type=grant_type,
            game_id=game_id,
            quantity=1,
            display_name=display_name,
            grant_function=grant_func,
        )
        grants[display_name] = grant
    
    return grants


# =============================================================================
# Static Grants (non-item grants like unlocks, party members, gil)
# =============================================================================

STATIC_GRANTS: Dict[str, ItemGrant] = {
    # Chapter Unlocks
    "Chapter 1 Complete": ItemGrant(
        ap_item_name="Chapter 1 Complete",
        grant_type=GrantType.UNLOCK,
        game_id="chapter_1",
        grant_function="UnlockChapter",
        grant_params="2",
    ),
    "Chapter 2 Complete": ItemGrant(
        ap_item_name="Chapter 2 Complete",
        grant_type=GrantType.UNLOCK,
        game_id="chapter_2",
        grant_function="UnlockChapter",
        grant_params="3",
    ),
    # ... chapters 3-13 follow same pattern
    
    # Party Members
    "Party: Barret": ItemGrant(
        ap_item_name="Party: Barret",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_barret",
        display_name="Barret Wallace",
        grant_function="UnlockPartyMember",
        grant_params="barret",
    ),
    "Party: Tifa": ItemGrant(
        ap_item_name="Party: Tifa",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_tifa",
        display_name="Tifa Lockhart",
        grant_function="UnlockPartyMember",
        grant_params="tifa",
    ),
    "Party: Aerith": ItemGrant(
        ap_item_name="Party: Aerith",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_aerith",
        display_name="Aerith Gainsborough",
        grant_function="UnlockPartyMember",
        grant_params="aerith",
    ),
    "Party: Red XIII": ItemGrant(
        ap_item_name="Party: Red XIII",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_redxiii",
        display_name="Red XIII",
        grant_function="UnlockPartyMember",
        grant_params="redxiii",
    ),
    "Party: Yuffie": ItemGrant(
        ap_item_name="Party: Yuffie",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_yuffie",
        display_name="Yuffie Kisaragi",
        grant_function="UnlockPartyMember",
        grant_params="yuffie",
    ),
    "Party: Cait Sith": ItemGrant(
        ap_item_name="Party: Cait Sith",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_caitsith",
        display_name="Cait Sith",
        grant_function="UnlockPartyMember",
        grant_params="caitsith",
    ),
    "Party: Vincent": ItemGrant(
        ap_item_name="Party: Vincent",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_vincent",
        display_name="Vincent Valentine",
        grant_function="UnlockPartyMember",
        grant_params="vincent",
    ),
    "Party: Cid": ItemGrant(
        ap_item_name="Party: Cid",
        grant_type=GrantType.PARTY_MEMBER,
        game_id="party_cid",
        display_name="Cid Highwind",
        grant_function="UnlockPartyMember",
        grant_params="cid",
    ),
    
    # Key Progression Items
    "Chocobo License": ItemGrant(
        ap_item_name="Chocobo License",
        grant_type=GrantType.UNLOCK,
        game_id="unlock_chocobo",
        grant_function="UnlockFeature",
        grant_params="chocobo_riding",
    ),
    "Grappling Hook": ItemGrant(
        ap_item_name="Grappling Hook",
        grant_type=GrantType.UNLOCK,
        game_id="unlock_grapple",
        grant_function="UnlockFeature",
        grant_params="grapple_points",
    ),
    "Climbing Gear": ItemGrant(
        ap_item_name="Climbing Gear",
        grant_type=GrantType.UNLOCK,
        game_id="unlock_climb",
        grant_function="UnlockFeature",
        grant_params="rock_climbing",
    ),
    "Colosseum Pass": ItemGrant(
        ap_item_name="Colosseum Pass",
        grant_type=GrantType.UNLOCK,
        game_id="unlock_colosseum",
        grant_function="UnlockFeature",
        grant_params="colosseum",
    ),
    "VR Simulator Access": ItemGrant(
        ap_item_name="VR Simulator Access",
        grant_type=GrantType.UNLOCK,
        game_id="unlock_vr",
        grant_function="UnlockFeature",
        grant_params="vr_simulator",
    ),
    
    # Gil Bundles
    "Gil Bundle (500)": ItemGrant(
        ap_item_name="Gil Bundle (500)",
        grant_type=GrantType.GIL,
        game_id="gil_500",
        quantity=500,
        grant_function="GrantGil",
    ),
    "Gil Bundle (1000)": ItemGrant(
        ap_item_name="Gil Bundle (1000)",
        grant_type=GrantType.GIL,
        game_id="gil_1000",
        quantity=1000,
        grant_function="GrantGil",
    ),
    "Gil Bundle (5000)": ItemGrant(
        ap_item_name="Gil Bundle (5000)",
        grant_type=GrantType.GIL,
        game_id="gil_5000",
        quantity=5000,
        grant_function="GrantGil",
    ),
    
    # Traps
    "Poison Trap": ItemGrant(
        ap_item_name="Poison Trap",
        grant_type=GrantType.TRAP,
        game_id="trap_poison",
        grant_function="ApplyTrap",
        grant_params="poison",
    ),
    "Confusion Trap": ItemGrant(
        ap_item_name="Confusion Trap",
        grant_type=GrantType.TRAP,
        game_id="trap_confuse",
        grant_function="ApplyTrap",
        grant_params="confuse",
    ),
    "Gil Loss Trap": ItemGrant(
        ap_item_name="Gil Loss Trap",
        grant_type=GrantType.TRAP,
        game_id="trap_gil_loss",
        quantity=-1000,
        grant_function="ApplyTrap",
        grant_params="gil_loss",
    ),
}


# =============================================================================
# Summon Materia Grants (with game IDs from data)
# =============================================================================

SUMMON_GRANTS: Dict[str, ItemGrant] = {
    "Summon: Ifrit": ItemGrant(
        ap_item_name="Summon: Ifrit",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Ifrit",
        display_name="Ifrit",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Shiva": ItemGrant(
        ap_item_name="Summon: Shiva",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Shiva",
        display_name="Shiva",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Ramuh": ItemGrant(
        ap_item_name="Summon: Ramuh",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Ramuh",
        display_name="Ramuh",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Titan": ItemGrant(
        ap_item_name="Summon: Titan",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Taitan",
        display_name="Titan",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Odin": ItemGrant(
        ap_item_name="Summon: Odin",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Odin",
        display_name="Odin",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Phoenix": ItemGrant(
        ap_item_name="Summon: Phoenix",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Phoenix",
        display_name="Phoenix",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Alexander": ItemGrant(
        ap_item_name="Summon: Alexander",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Alexander",
        display_name="Alexander",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Kujata": ItemGrant(
        ap_item_name="Summon: Kujata",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Kjata",
        display_name="Kujata",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Bahamut": ItemGrant(
        ap_item_name="Summon: Bahamut",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_Bahamut",
        display_name="Bahamut",
        grant_function="GrantSummonMateria",
    ),
    "Summon: Neo Bahamut": ItemGrant(
        ap_item_name="Summon: Neo Bahamut",
        grant_type=GrantType.SUMMON,
        game_id="M_SUM_NeoBahamut",
        display_name="Neo Bahamut",
        grant_function="GrantSummonMateria",
    ),
}


# =============================================================================
# Combined Grant Registry (built lazily)
# =============================================================================

_ITEM_GRANTS: Optional[Dict[str, ItemGrant]] = None


def _get_all_grants() -> Dict[str, ItemGrant]:
    """Get or build the complete grants dictionary."""
    global _ITEM_GRANTS
    if _ITEM_GRANTS is None:
        # Start with game data grants
        _ITEM_GRANTS = _build_grants_from_game_data()
        # Add static grants (overwrites any conflicts)
        _ITEM_GRANTS.update(STATIC_GRANTS)
        # Add summon grants
        _ITEM_GRANTS.update(SUMMON_GRANTS)
    return _ITEM_GRANTS


# Public alias
ITEM_GRANTS = property(lambda self: _get_all_grants())


# =============================================================================
# Lookup Functions
# =============================================================================

def get_grant_data(ap_item_name: str) -> Optional[ItemGrant]:
    """Get grant data for an AP item name."""
    return _get_all_grants().get(ap_item_name)


def get_game_item_id(ap_item_name: str) -> str:
    """Get the in-game item ID for an AP item."""
    grant = _get_all_grants().get(ap_item_name)
    return grant.game_id if grant else ""


def get_grants_by_type(grant_type: GrantType) -> List[ItemGrant]:
    """Get all grants of a specific type."""
    return [g for g in _get_all_grants().values() if g.grant_type == grant_type]


def get_grant_function(ap_item_name: str) -> str:
    """Get the Lua function to call for granting this item."""
    grant = _get_all_grants().get(ap_item_name)
    return grant.grant_function if grant else "GrantItem"


def to_lua_table(grant: ItemGrant) -> Dict[str, Any]:
    """Convert grant data to a Lua-compatible dictionary."""
    return {
        "name": grant.ap_item_name,
        "type": int(grant.grant_type),
        "game_id": grant.game_id,
        "quantity": grant.quantity,
        "display_name": grant.display_name or grant.ap_item_name,
        "function": grant.grant_function,
        "params": grant.grant_params,
    }


def get_all_game_ids() -> Dict[str, str]:
    """Get mapping of AP item names to game IDs for all grants."""
    return {name: grant.game_id for name, grant in _get_all_grants().items()}
