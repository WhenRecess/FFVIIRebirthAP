"""
Final Fantasy VII: Rebirth Archipelago World Definition
"""
from typing import Dict, List, Set, Any
import os
import csv

from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from .items import item_table, load_items_from_csv
from .locations import location_table, load_locations_from_csv

# Game identifier
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
    # Base range: 6000-6999 for items, 6000-6999 for locations
    base_id = 6000
    
    # Item and location name to ID mappings
    item_name_to_id = {}
    location_name_to_id = {}
    
    # TODO: Define world options (difficulty, randomization settings, etc.)
    # options_dataclass = FFVIIRebirthOptions
    # options: FFVIIRebirthOptions
    
    def __init__(self, world, player):
        super().__init__(world, player)
        
        # Load item and location data
        self._load_data()
    
    def _load_data(self):
        """Load item and location definitions from CSV files or hardcoded data"""
        
        # Try to load from CSV files in data/ directory
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        
        # Load items
        items_csv = os.path.join(data_dir, "items.csv")
        if os.path.exists(items_csv):
            self.item_name_to_id = load_items_from_csv(items_csv, self.base_id)
        else:
            # Fall back to hardcoded item_table
            self.item_name_to_id = {name: self.base_id + idx 
                                   for idx, name in enumerate(item_table.keys())}
        
        # Load locations
        locations_csv = os.path.join(data_dir, "locations.csv")
        if os.path.exists(locations_csv):
            self.location_name_to_id = load_locations_from_csv(locations_csv, self.base_id)
        else:
            # Fall back to hardcoded location_table
            self.location_name_to_id = {name: self.base_id + idx 
                                       for idx, name in enumerate(location_table.keys())}
    
    @classmethod
    def stage_assert_generate(cls, multiworld):
        """Called before world generation to validate settings"""
        # TODO: Add validation logic
        pass
    
    def create_regions(self):
        """
        Create regions (maps/areas) and their connections.
        Each region contains locations (checks) that the player can complete.
        """
        
        # Create menu region (standard starting point)
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        
        # TODO: Create regions based on game areas
        # Example regions:
        # - Grasslands
        # - Junon
        # - Corel
        # - Gongaga
        # - Cosmo Canyon
        # - Nibel
        # - etc.
        
        # Example: Create a basic region structure
        regions = {
            "Grasslands": [],  # List of location names in this region
            "Junon": [],
            "Corel": [],
        }
        
        for region_name, location_names in regions.items():
            region = Region(region_name, self.player, self.multiworld)
            
            # Add locations to region
            for loc_name in location_names:
                if loc_name in self.location_name_to_id:
                    location = self.create_location(loc_name)
                    region.locations.append(location)
            
            self.multiworld.regions.append(region)
            
            # Connect from menu (TODO: implement proper region connections)
            entrance = Entrance(self.player, f"To {region_name}", menu)
            entrance.connect(region)
            menu.exits.append(entrance)
        
        # Set starting region
        self.multiworld.get_region("Menu", self.player).connect(
            self.multiworld.get_region("Grasslands", self.player)
        )
    
    def create_items(self):
        """
        Create items and add them to the item pool.
        Items are what players receive when they complete locations.
        """
        
        # TODO: Implement item pool creation based on world options
        # Consider:
        # - Progression items (key items, abilities, story flags)
        # - Useful items (materia, equipment, consumables)
        # - Filler items (gil, exp, common items)
        
        # Example: Create items from item_table
        item_pool = []
        
        for item_name, item_data in item_table.items():
            classification = item_data.get("classification", ItemClassification.filler)
            count = item_data.get("count", 1)
            
            for _ in range(count):
                item = self.create_item(item_name)
                item_pool.append(item)
        
        # Add items to multiworld
        self.multiworld.itempool += item_pool
    
    def create_item(self, name: str) -> Item:
        """Create an item by name"""
        item_id = self.item_name_to_id.get(name)
        
        if item_id is None:
            raise ValueError(f"Unknown item: {name}")
        
        # Get item classification (progression, useful, filler, trap)
        classification = item_table.get(name, {}).get("classification", ItemClassification.filler)
        
        return Item(name, classification, item_id, self.player)
    
    def create_location(self, name: str):
        """Create a location by name"""
        from BaseClasses import Location
        
        location_id = self.location_name_to_id.get(name)
        
        if location_id is None:
            raise ValueError(f"Unknown location: {name}")
        
        return Location(self.player, name, location_id)
    
    def set_rules(self):
        """
        Define logic rules for accessing locations and regions.
        This determines what items are required to reach certain locations.
        """
        
        # TODO: Implement access rules
        # Example:
        # set_rule(
        #     self.multiworld.get_location("Boss: Midgardsormr", self.player),
        #     lambda state: state.has("Chocobo Lure", self.player)
        # )
        
        pass
    
    def generate_early(self):
        """
        Called early in generation process.
        Use this to set up any world-specific generation logic.
        """
        
        # TODO: Implement early generation logic
        # Examples:
        # - Validate world options
        # - Generate random enemy/item placements
        # - Set up region connections based on options
        
        pass
    
    def pre_fill(self):
        """Called before items are distributed to locations"""
        # TODO: Pre-place any required items
        pass
    
    def fill_slot_data(self) -> Dict[str, Any]:
        """
        Return slot data that will be sent to the client.
        This can include world-specific settings, seed info, etc.
        """
        
        slot_data = {
            "world_version": "0.1.0",
            # TODO: Add game-specific configuration
            # "enemy_randomization": self.options.enemy_randomization.value,
            # "starting_materia": self.options.starting_materia.value,
            # etc.
        }
        
        return slot_data
    
    def generate_output(self, output_directory: str):
        """
        Generate mod files/patches for the game.
        For FFVII Rebirth, this might generate configuration files
        for the UE4SS mod to read.
        """
        
        # TODO: Generate output files
        # Examples:
        # - item_locations.json: mapping of location IDs to items
        # - enemy_randomization.json: enemy replacements
        # - starting_inventory.json: items to give at start
        
        # Example output generation:
        output_file = os.path.join(output_directory, f"AP_{self.player}_{self.multiworld.seed_name}.json")
        
        data = {
            "slot_name": self.multiworld.player_name[self.player],
            "seed": self.multiworld.seed_name,
            "locations": {
                # TODO: Add location -> item mappings
            },
            "slot_data": self.fill_slot_data()
        }
        
        # Uncomment to actually write file:
        # import json
        # with open(output_file, 'w') as f:
        #     json.dump(data, f, indent=2)
