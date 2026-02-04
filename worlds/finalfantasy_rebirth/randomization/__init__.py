"""
Randomization Package for Final Fantasy VII: Rebirth
================================================================

This package contains all randomization logic for generating item pools,
location tables, and access rules. These modules combine static data
from the data/ package with dynamically generated content from game exports.

Modules:
    item_pool.py
        ItemPoolBuilder class for constructing item pools.
        Combines static definitions with generated equipment items.
        Provides build_item_table() convenience function.
    
    location_generator.py
        LocationGenerator class for constructing location tables.
        Generates colosseum and territory locations from game data.
        Provides build_location_table() convenience function.
    
    rules.py
        RuleFactory class for creating access rules.
        Defines region, location, and completion condition logic.
        Integrates with Archipelago's rule system.

Builder Pattern:
    Both ItemPoolBuilder and LocationGenerator use the builder pattern
    for flexible, chainable configuration:
    
        items = (ItemPoolBuilder()
            .with_progression_items()
            .with_useful_items()
            .with_filler_items()
            .build())
        
        locations = (LocationGenerator()
            .with_story_locations()
            .with_colosseum_from_game_data()
            .build())
"""
from .item_pool import ItemPoolBuilder, build_item_table
from .location_generator import LocationGenerator, build_location_table
from .rules import RuleFactory, set_region_rules, set_location_rules

__all__ = [
    # Item pool
    "ItemPoolBuilder",
    "build_item_table",
    # Location generation
    "LocationGenerator",
    "build_location_table",
    # Rules
    "RuleFactory",
    "set_region_rules",
    "set_location_rules",
]
