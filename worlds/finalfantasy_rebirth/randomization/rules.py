"""
Rules Factory for Final Fantasy VII: Rebirth
================================================================

This module provides the rule system for determining when regions
and locations become accessible during randomization. It integrates
with Archipelago's generic rule system.

Key Components:
    RuleFactory
        Factory class for creating rule lambda functions.
        Provides methods for common rule patterns:
        - has_item(): Check for a single item
        - has_all_items(): Check for all items in a list (AND)
        - has_any_item(): Check for any item in a list (OR)
        - has_chapter_complete(): Check for chapter completion
        - has_party_member(): Check for party member unlock
        - has_colosseum_access(): Check for colosseum pass
        - has_vr_access(): Check for VR simulator access

Module Functions:
    set_region_rules(multiworld, player)
        Apply access rules to all regions based on REGION_REQUIREMENTS.
        Called during world generation in set_rules().
    
    set_location_rules(multiworld, player, location_table)
        Apply access rules to specific locations based on their type.
        For example, colosseum locations require colosseum pass.
    
    set_completion_condition(multiworld, player, goal_type)
        Define what's required to complete the game.
        Supports: story_complete, all_bosses, colosseum_champion.

Rule System:
    Rules are lambda functions that take a CollectionState and return
    True if the requirement is met. Rules are applied to entrances
    (for regions) and locations using Archipelago's set_rule/add_rule.
"""
from typing import Dict, List, Callable, Any, TYPE_CHECKING
from worlds.generic.Rules import set_rule, add_rule

from ..data import REGION_REQUIREMENTS, FFVIIRLocationData

if TYPE_CHECKING:
    from BaseClasses import CollectionState, MultiWorld


class RuleFactory:
    """Factory for creating access rules."""
    
    def __init__(self, player: int):
        self.player = player
    
    def has_item(self, item_name: str) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for a specific item."""
        return lambda state: state.has(item_name, self.player)
    
    def has_all_items(self, item_names: List[str]) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for all items in a list."""
        return lambda state: all(state.has(item, self.player) for item in item_names)
    
    def has_any_item(self, item_names: List[str]) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for any item in a list."""
        return lambda state: any(state.has(item, self.player) for item in item_names)
    
    def has_chapter_complete(self, chapter: int) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for chapter completion."""
        return self.has_item(f"Chapter {chapter} Complete")
    
    def has_party_member(self, member: str) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for a party member."""
        return self.has_item(f"Party: {member}")
    
    def has_colosseum_access(self) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for colosseum access."""
        return self.has_item("Colosseum Pass")
    
    def has_vr_access(self) -> Callable[["CollectionState"], bool]:
        """Create a rule that checks for VR simulator access."""
        return self.has_item("VR Simulator Access")


def set_region_rules(multiworld: "MultiWorld", player: int) -> None:
    """
    Set access rules for all regions based on requirements.
    
    Args:
        multiworld: The Archipelago multiworld
        player: The player ID
    """
    factory = RuleFactory(player)
    
    for region_name, requirements in REGION_REQUIREMENTS.items():
        if region_name == "Menu" or not requirements:
            continue
        
        region = multiworld.get_region(region_name, player)
        if not region:
            continue
        
        # Apply rules to all entrances to this region
        for entrance in region.entrances:
            for req in requirements:
                add_rule(entrance, factory.has_item(req))


def set_location_rules(
    multiworld: "MultiWorld",
    player: int,
    location_table: Dict[str, FFVIIRLocationData]
) -> None:
    """
    Set access rules for specific locations.
    
    Args:
        multiworld: The Archipelago multiworld
        player: The player ID
        location_table: The location table with location data
    """
    factory = RuleFactory(player)
    
    # Example location-specific rules
    # These can be expanded based on game knowledge
    
    location_rules = {
        # Colosseum requires pass
        "colosseum": factory.has_colosseum_access(),
        # VR battles require VR access
        "vr_battle": factory.has_vr_access(),
        "summon_battle": factory.has_vr_access(),
    }
    
    for loc_name, loc_data in location_table.items():
        location = multiworld.get_location(loc_name, player)
        if not location:
            continue
        
        # Apply type-based rules
        if loc_data.location_type in location_rules:
            set_rule(location, location_rules[loc_data.location_type])


def set_completion_condition(
    multiworld: "MultiWorld",
    player: int,
    goal_type: str = "story_complete"
) -> None:
    """
    Set the completion condition for the game.
    
    Args:
        multiworld: The Archipelago multiworld
        player: The player ID
        goal_type: Type of goal (story_complete, all_bosses, etc.)
    """
    factory = RuleFactory(player)
    
    if goal_type == "story_complete":
        # Beat the main story
        multiworld.completion_condition[player] = factory.has_chapter_complete(13)
    
    elif goal_type == "all_bosses":
        # Defeat all major bosses
        boss_items = [
            "Boss: Midgardsormr Defeated",
            "Boss: Bottomswell Defeated",
            "Boss: Dyne Defeated",
            "Boss: Gi Nattak Defeated",
            "Boss: Lost Number Defeated",
            "Boss: Red Dragon Defeated",
            "Boss: Demon Wall Defeated",
        ]
        multiworld.completion_condition[player] = factory.has_all_items(boss_items)
    
    elif goal_type == "colosseum_champion":
        # Complete all colosseum tiers
        multiworld.completion_condition[player] = factory.has_item("Colosseum Champion")
    
    else:
        # Default to story complete
        multiworld.completion_condition[player] = factory.has_chapter_complete(13)
