"""
Region Builder for Final Fantasy VII: Rebirth
================================================================

This module handles the creation of regions and their connections
for the Archipelago world graph. Regions represent distinct areas
of the game world that contain locations (checks).

Key Concepts:
    - Region: A named area containing zero or more locations
    - Entrance: A connection between two regions
    - Location: A check within a region where items can be placed

Region Structure:
    Menu (start) -> All game regions
    
    Game regions include:
    - Kalm, Grasslands, Junon, Costa del Sol, Corel
    - Gold Saucer, Gongaga, Cosmo Canyon, Nibelheim, Mt. Nibel
    - Temple of the Ancients, Forgotten Capital, VR Simulator

Classes:
    - RegionBuilder: Builder pattern class for creating regions

Functions:
    - build_regions(): Convenience function to build all regions

Example:
    from .regions import build_regions
    
    # In FFVIIRebirthWorld.create_regions():
    build_regions(self.player, self.multiworld, self.location_name_to_id)
"""
from typing import Dict, List, TYPE_CHECKING

from BaseClasses import Region, Entrance, Location

from ..data import REGIONS, REGION_REQUIREMENTS
from ..randomization import build_location_table

if TYPE_CHECKING:
    from BaseClasses import MultiWorld


class RegionBuilder:
    """Builder class for creating and connecting regions."""
    
    def __init__(self, player: int, multiworld: "MultiWorld"):
        self.player = player
        self.multiworld = multiworld
        self._regions: Dict[str, Region] = {}
        self._location_table = build_location_table()
    
    def create_regions(self, location_name_to_id: Dict[str, int]) -> Dict[str, Region]:
        """
        Create all game regions and their locations.
        
        Args:
            location_name_to_id: Mapping of location names to AP IDs
        
        Returns:
            Dictionary of created regions
        """
        # Create Menu region (starting point)
        menu = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu)
        self._regions["Menu"] = menu
        
        # Create game regions
        for region_name in REGIONS:
            if region_name == "Menu":
                continue
            
            region = Region(region_name, self.player, self.multiworld)
            self._regions[region_name] = region
            self.multiworld.regions.append(region)
            
            # Add locations to this region
            self._add_locations_to_region(region, location_name_to_id)
        
        return self._regions
    
    def connect_regions(self) -> None:
        """
        Connect regions with entrances.
        
        For initial implementation, all regions connect directly to Menu.
        This can be expanded for more realistic region connections.
        """
        menu = self._regions.get("Menu")
        if not menu:
            return
        
        for region_name, region in self._regions.items():
            if region_name == "Menu":
                continue
            
            entrance = Entrance(self.player, f"Enter {region_name}", menu)
            entrance.connect(region)
            menu.exits.append(entrance)
    
    def _add_locations_to_region(
        self,
        region: Region,
        location_name_to_id: Dict[str, int]
    ) -> None:
        """Add all locations belonging to a region."""
        for loc_name, loc_data in self._location_table.items():
            if loc_data.region != region.name:
                continue
            
            if loc_name not in location_name_to_id:
                continue
            
            location = Location(
                self.player,
                loc_name,
                location_name_to_id[loc_name],
                region
            )
            region.locations.append(location)
    
    def get_locations_for_region(self, region_name: str) -> List[str]:
        """Get all location names for a specific region."""
        return [
            name for name, data in self._location_table.items()
            if data.region == region_name
        ]


def build_regions(
    player: int,
    multiworld: "MultiWorld",
    location_name_to_id: Dict[str, int]
) -> Dict[str, Region]:
    """
    Build all regions and their connections.
    
    Args:
        player: The player ID
        multiworld: The Archipelago multiworld
        location_name_to_id: Mapping of location names to AP IDs
    
    Returns:
        Dictionary of created regions
    """
    builder = RegionBuilder(player, multiworld)
    regions = builder.create_regions(location_name_to_id)
    builder.connect_regions()
    return regions
