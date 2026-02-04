"""
Archipelago Python Client → File Bridge
=========================================

This script connects to an Archipelago server and writes received
items to a file that the UE4SS Lua mod can read.

Communication Flow:
    AP Server → This Script → ap_received_items.txt → Lua Mod → Memory Bridge

Usage:
    python ap_file_bridge.py --server SERVER:PORT --slot SLOTNAME --password PASSWORD
"""

import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    from CommonClient import CommonContext, server_loop, ClientCommandProcessor, logger, gui_enabled
    from NetUtils import ClientStatus
except ImportError:
    print("ERROR: Archipelago libraries not found!")
    print("Install with: pip install archipelago-client")
    exit(1)

from item_mappings import get_memory_id, get_all_item_names

# File paths
RECEIVED_ITEMS_FILE = Path("ap_received_items.txt")
CHECKED_LOCATIONS_FILE = Path("ap_checked_locations.txt")
CONNECTION_STATUS_FILE = Path("ap_status.txt")


class FFVIIRebirthContext(CommonContext):
    """Archipelago context for FF7 Rebirth."""
    
    game = "Final Fantasy VII Rebirth"
    items_handling = 0b111  # Receive items from other players
    
    def __init__(self, server_address, password):
        super().__init__(server_address, password)
        self.received_items_index = 0
        
    def on_package(self, cmd: str, args: dict):
        """Handle packets from AP server."""
        if cmd == "ReceivedItems":
            # Process new items
            start_index = args["index"]
            items = args["items"]
            
            for item in items[self.received_items_index:]:
                self.handle_received_item(item)
            
            self.received_items_index = start_index + len(items)
            
        elif cmd == "Connected":
            logger.info(f"Connected to Archipelago server!")
            self.update_status_file("connected")
            
        elif cmd == "ConnectionRefused":
            logger.error(f"Connection refused: {args}")
            self.update_status_file("refused")
            
    def handle_received_item(self, item):
        """Write received item to file for Lua mod to process."""
        item_id = item.item
        player_name = self.player_names.get(item.player, "Unknown")
        
        # Convert AP item ID to item name
        # Note: You'll need to map AP IDs to CE IDs in your world definition
        item_name = f"Item_{item_id}"  # Placeholder
        
        # Write to file
        data = {
            "item": item_name,
            "qty": 1,
            "from": player_name,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(RECEIVED_ITEMS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        
        logger.info(f"Received {item_name} from {player_name}")
    
    def update_status_file(self, status: str):
        """Write connection status for monitoring."""
        data = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        with open(CONNECTION_STATUS_FILE, "w", encoding="utf-8") as f:
            json.dumps(data, f, indent=2)


class FFVIIRebirthCommandProcessor(ClientCommandProcessor):
    """Command processor for the text client."""
    
    def _cmd_check(self):
        """Mark a location as checked."""
        # TODO: Read from checked_locations.txt and send to server
        pass


async def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="FF7 Rebirth Archipelago File Bridge")
    parser.add_argument("--server", help="AP server address (host:port)", required=True)
    parser.add_argument("--slot", help="Your slot name", required=True)
    parser.add_argument("--password", help="Server password (optional)", default="")
    
    args = parser.parse_args()
    
    # Clear files
    RECEIVED_ITEMS_FILE.write_text("", encoding="utf-8")
    CONNECTION_STATUS_FILE.write_text('{"status":"connecting"}', encoding="utf-8")
    
    # Create context
    ctx = FFVIIRebirthContext(args.server, args.password)
    ctx.auth = args.slot
    
    # Run client
    logger.info(f"Connecting to {args.server} as {args.slot}...")
    await server_loop(ctx)


if __name__ == "__main__":
    asyncio.run(main())
