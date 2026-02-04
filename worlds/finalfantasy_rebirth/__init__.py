"""
Final Fantasy VII: Rebirth - Archipelago World Definition
================================================================

This is the main entry point for the FFVII Rebirth Archipelago world.
It defines the FFVIIRebirthWorld class which integrates with the
Archipelago multiworld randomizer framework.

Module Structure:
    worlds/finalfantasy_rebirth/
    ├── __init__.py          # This file - main world class
    ├── core/                # Public interface modules
    │   ├── items.py         # Item facade
    │   ├── locations.py     # Location facade  
    │   ├── options.py       # Randomizer options
    │   └── regions.py       # Region builder
    ├── data/                # Static data tables
    │   ├── item_tables.py   # Item definitions
    │   ├── location_tables.py # Location definitions
    │   ├── region_tables.py # Region definitions
    │   ├── game_loader.py   # Game data loader
    │   └── exports/         # Raw JSON game data
    └── randomization/       # Randomization logic
        ├── item_pool.py     # Item pool builder
        ├── location_generator.py # Location generator
        └── rules.py         # Access rules

Usage:
    This module is loaded by Archipelago's world system.
    The FFVIIRebirthWorld class is automatically discovered and
    made available for multiworld generation.

See Also:
    - ARCHITECTURE.md for detailed documentation
    - README_WORLD.md for setup instructions
"""
from typing import Dict, List, Set, Any, ClassVar
import os
import json
import logging

from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification, Location
from worlds.AutoWorld import World, WebWorld

# Import from modular structure
from .data import get_game_data, REGIONS, REGION_REQUIREMENTS
from .data.item_tables import FFVIIRItemData
from .data.location_tables import FFVIIRLocationData
from .randomization import build_item_table, build_location_table
from .randomization.rules import set_region_rules, set_location_rules, set_completion_condition
from .core.regions import build_regions

logger = logging.getLogger("FFVIIRebirth")

# Build tables at module load time
_item_table = build_item_table(include_traps=False, include_game_data=True)
_location_table = build_location_table()


class FFVIIRebirthWeb(WebWorld):
    """Web interface configuration for FFVII Rebirth"""
    theme = "stone"
    
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Final Fantasy VII: Rebirth for Archipelago",
            "English",
            "setup_en.md",
            "setup/en",
            ["WhenRecess"]
        )
    ]


class FFVIIRebirthWorld(World):
    """
    Final Fantasy VII: Rebirth is an action RPG by Square Enix.
    Join Cloud and friends as they explore a vast open world, battle fierce enemies,
    and uncover the mysteries of the Planet in this multiworld randomizer adaptation.
    """
    
    # World metadata
    game = "Final Fantasy VII: Rebirth"
    web = FFVIIRebirthWeb()
    
    # World configuration
    topology_present = True
    
    # Base ID for items/locations (must be unique across all AP worlds)
    base_id = 770000  # Using 770xxx range for FF7R
    
    # Item and location name to ID mappings (built at class definition time)
    item_name_to_id: ClassVar[Dict[str, int]] = {
        name: 770000 + idx 
        for idx, name in enumerate(_item_table.keys())
    }
    
    location_name_to_id: ClassVar[Dict[str, int]] = {
        name: 770000 + len(_item_table) + 1000 + idx 
        for idx, name in enumerate(_location_table.keys())
    }
    
    # Store tables for instance access
    item_table = _item_table
    location_table = _location_table
    
    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)
    
    @classmethod
    def stage_assert_generate(cls, multiworld):
        """Called before world generation to validate settings"""
        pass  # ID mappings are built at class definition time
    
    def create_regions(self):
        """
        Create regions (maps/areas) and their connections.
        Each region contains locations (checks) that the player can complete.
        """
        build_regions(self.player, self.multiworld, self.location_name_to_id)
    
    def create_items(self):
        """
        Create items and add them to the item pool.
        Items are what players receive when they complete locations.
        """
        total_locations = len(self.location_name_to_id)
        
        # Separate items into non-filler and filler
        non_filler_items = []
        filler_items = []
        
        for item_name, item_data in self.item_table.items():
            for _ in range(item_data.count):
                item = self.create_item(item_name)
                if item_data.classification == ItemClassification.filler:
                    filler_items.append(item)
                else:
                    non_filler_items.append(item)
        
        # Start with all non-filler items
        item_pool = non_filler_items.copy()
        
        # Calculate how much room we have for filler
        filler_slots = total_locations - len(non_filler_items)
        
        # Add only as much filler as we have room for
        if filler_slots > 0:
            while len(filler_items) < filler_slots:
                filler_items.append(self.create_filler())
            item_pool.extend(filler_items[:filler_slots])
        
        self.multiworld.itempool += item_pool
    
    def get_filler_item_name(self) -> str:
        """Return a filler item name for balancing."""
        filler_options = ["Gil Bundle (500)", "Gil Bundle (1000)", "Potion", "Ether"]
        return self.random.choice(filler_options)
    
    def create_item(self, name: str) -> Item:
        """Create an item by name"""
        item_id = self.item_name_to_id.get(name)
        
        if item_id is None:
            item_id = self.base_id
        
        item_data = self.item_table.get(name)
        if item_data:
            classification = item_data.classification
        else:
            classification = ItemClassification.filler
        
        return Item(name, classification, item_id, self.player)
    
    def set_rules(self):
        """
        Define logic rules for accessing locations and regions.
        """
        set_region_rules(self.multiworld, self.player)
        set_location_rules(self.multiworld, self.player, self.location_table)
        set_completion_condition(self.multiworld, self.player, "story_complete")
    
    def generate_early(self):
        """Called early in generation process."""
        game_data = get_game_data()
        if not game_data.items:
            logger.warning(f"No game data loaded for {self.game}")
    
    def pre_fill(self):
        """Called before items are distributed to locations"""
        pass
    
    def fill_slot_data(self) -> Dict[str, Any]:
        """Return slot data that will be sent to the client."""
        return {
            "world_version": "0.1.0",
            "base_id": self.base_id,
            "total_items": len(self.item_name_to_id),
            "total_locations": len(self.location_name_to_id),
        }
    
    def generate_output(self, output_directory: str):
        """Generate mod files for the game client (UE4SS mod)."""
        location_item_map = {}
        for location in self.multiworld.get_filled_locations(self.player):
            loc_data = self.location_table.get(location.name)
            if loc_data:
                location_item_map[location.name] = {
                    "item_name": location.item.name if location.item else "Nothing",
                    "item_player": location.item.player if location.item else self.player,
                    "game_id": loc_data.game_id,
                    "region": loc_data.region,
                    "type": loc_data.location_type,
                }
        
        output_file = os.path.join(
            output_directory, 
            f"AP_{self.multiworld.get_file_safe_player_name(self.player)}_{self.multiworld.seed_name}.json"
        )
        
        data = {
            "slot_name": self.multiworld.player_name[self.player],
            "seed": self.multiworld.seed_name,
            "player": self.player,
            "locations": location_item_map,
            "slot_data": self.fill_slot_data()
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
