"""
Final Fantasy VII: Rebirth Archipelago World Implementation

This module defines the FFVIIRebirthWorld class, which integrates Final Fantasy VII: Rebirth
with the Archipelago multi-game randomizer platform.
"""

from typing import Dict, List, Any
from BaseClasses import Region, Entrance, Item, Tutorial, ItemClassification
from worlds.AutoWorld import World, WebWorld
from .items import item_name_to_id, FFVIIRebirthItem
from .locations import location_name_to_id, FFVIIRebirthLocation


class FFVIIRebirthWeb(WebWorld):
    """Web configuration for Final Fantasy VII: Rebirth."""
    
    theme = "partyTime"
    
    tutorials = [
        Tutorial(
            "Multiworld Setup Guide",
            "A guide to setting up Final Fantasy VII: Rebirth for Archipelago multiworld.",
            "English",
            "setup_en.md",
            "setup/en",
            ["WhenRecess"]
        )
    ]


class FFVIIRebirthWorld(World):
    """
    Final Fantasy VII: Rebirth is an action RPG developed by Square Enix.
    This world implementation provides Archipelago integration for the game.
    """
    
    game = "Final Fantasy VII: Rebirth"
    web = FFVIIRebirthWeb()
    
    # Data package information
    data_version = 1
    required_client_version = (0, 4, 4)
    
    # Item and location mappings
    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id
    
    # TODO: Define game-specific options
    # Example:
    # from Options import Toggle, Range, Choice
    # 
    # class StartingMateria(Choice):
    #     """Which materia to start with"""
    #     display_name = "Starting Materia"
    #     option_fire = 0
    #     option_ice = 1
    #     option_lightning = 2
    #     default = 0
    # 
    # options_dataclass = make_dataclass("FFVIIRebirthOptions", [
    #     ("starting_materia", StartingMateria),
    # ])
    # options: options_dataclass

    def create_item(self, name: str) -> Item:
        """
        Create an Archipelago item.
        
        Args:
            name: Name of the item to create
            
        Returns:
            FFVIIRebirthItem instance
        """
        item_id = self.item_name_to_id.get(name)
        if item_id is None:
            raise ValueError(f"Item '{name}' not found in item_name_to_id")
        
        # TODO: Classify items properly
        # Example classification:
        # - ItemClassification.progression: Required for game completion
        # - ItemClassification.useful: Helpful but not required
        # - ItemClassification.filler: Common/less useful items
        # - ItemClassification.trap: Negative effects
        
        classification = ItemClassification.filler
        
        # Example: Mark key items as progression
        # if "Key Item" in name or "Summon" in name:
        #     classification = ItemClassification.progression
        
        return FFVIIRebirthItem(name, classification, item_id, self.player)

    def create_event(self, name: str) -> Item:
        """
        Create an event item (no ID, local to this world).
        
        Args:
            name: Name of the event
            
        Returns:
            Event item instance
        """
        return FFVIIRebirthItem(name, ItemClassification.progression, None, self.player)

    def create_regions(self) -> None:
        """
        Create regions and connect them with entrances.
        
        Regions represent logical areas in the game world. Locations are placed
        within regions, and entrances connect regions together.
        """
        
        # Create menu region (starting point)
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        
        # TODO: Create game regions based on the game's structure
        # Example:
        # 
        # midgar = Region("Midgar", self.player, self.multiworld)
        # kalm = Region("Kalm", self.player, self.multiworld)
        # junon = Region("Junon", self.player, self.multiworld)
        # 
        # self.multiworld.regions.extend([midgar, kalm, junon])
        # 
        # # Connect regions with entrances
        # menu.connect(midgar, "Start Game")
        # midgar.connect(kalm, "Leave Midgar")
        # kalm.connect(junon, "Travel to Junon")
        # 
        # # Add locations to regions
        # midgar.locations.append(FFVIIRebirthLocation(
        #     self.player, "Boss: Scorpion Sentinel", 
        #     self.location_name_to_id["Boss: Scorpion Sentinel"], midgar
        # ))
        
        # Placeholder: Single region with all locations
        main_region = Region("Main Game", self.player, self.multiworld)
        self.multiworld.regions.append(main_region)
        menu.connect(main_region, "Start Game")
        
        # TODO: Add locations to regions
        # for location_name, location_id in self.location_name_to_id.items():
        #     location = FFVIIRebirthLocation(
        #         self.player, location_name, location_id, main_region
        #     )
        #     main_region.locations.append(location)

    def create_items(self) -> None:
        """
        Create items and add them to the multiworld item pool.
        
        This method is called during world generation to populate the item pool
        with all items that should be placed in the multiworld.
        """
        
        # TODO: Create items for the item pool
        # Example:
        # 
        # item_pool = []
        # 
        # for item_name, item_id in self.item_name_to_id.items():
        #     # Skip victory/event items
        #     if item_name == "Victory":
        #         continue
        #     
        #     # Create item
        #     item = self.create_item(item_name)
        #     item_pool.append(item)
        # 
        # self.multiworld.itempool += item_pool
        
        # Placeholder: No items created yet
        pass

    def set_rules(self) -> None:
        """
        Set access rules for locations and entrances.
        
        Rules define which items are required to access specific locations or regions.
        Use `set_rule()` and `add_rule()` from `worlds.generic.Rules`.
        """
        
        # TODO: Define access rules
        # Example:
        # 
        # from worlds.generic.Rules import set_rule, add_rule
        # 
        # # Require a specific item to access a location
        # set_rule(
        #     self.multiworld.get_location("Boss: Jenova BIRTH", self.player),
        #     lambda state: state.has("Cargo Ship Access", self.player)
        # )
        # 
        # # Require multiple items for a region entrance
        # set_rule(
        #     self.multiworld.get_entrance("Enter Northern Crater", self.player),
        #     lambda state: (
        #         state.has("Highwind", self.player) and
        #         state.has("Key to Ancients", self.player)
        #     )
        # )
        
        # Set completion condition (victory)
        # self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)
        
        pass

    def generate_early(self) -> None:
        """
        Called early in the generation process, before item placement.
        
        Use this to set up world-specific logic or validate options.
        """
        
        # TODO: Early generation logic
        # Example:
        # - Validate player options
        # - Pre-place certain items in specific locations
        # - Adjust item pool based on settings
        
        pass

    def generate_output(self, output_directory: str) -> None:
        """
        Generate output files for this world.
        
        Args:
            output_directory: Path to the output directory for generated files
        """
        
        # TODO: Generate output files for the game client
        # Example: Create a JSON file with item/location mappings
        # 
        # import json
        # import os
        # 
        # output_data = {
        #     "player_name": self.multiworld.get_player_name(self.player),
        #     "seed": self.multiworld.seed,
        #     "locations": {
        #         location.name: location.item.name if location.item else None
        #         for location in self.multiworld.get_locations(self.player)
        #     }
        # }
        # 
        # output_path = os.path.join(output_directory, f"AP_{self.multiworld.seed}_{self.player}.json")
        # with open(output_path, "w") as f:
        #     json.dump(output_data, f, indent=2)
        
        pass

    def fill_slot_data(self) -> Dict[str, Any]:
        """
        Generate slot data for this world.
        
        Slot data is sent to the client and can contain player-specific information
        like options, seed, or generated randomization data.
        
        Returns:
            Dictionary of slot data
        """
        
        # TODO: Add slot data
        # Example:
        # return {
        #     "death_link": self.options.death_link.value,
        #     "starting_materia": self.options.starting_materia.value,
        #     "seed": self.multiworld.seed,
        # }
        
        return {}
