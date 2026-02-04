"""
Generate complete item_mappings.py from ce.txt
===============================================

This script parses ce.txt and generates a complete Python mapping
file with all items organized by category.

Usage:
    python generate_item_mappings.py
"""

import re
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
CE_FILE = REPO_ROOT / "ce.txt"
OUTPUT_FILE = REPO_ROOT / "worlds" / "finalfantasy_rebirth" / "item_mappings.py"

def extract_item_dropdown(ce_content: str) -> list:
    """Extract items from all dropdown lists in ce.txt."""
    items = []
    in_dropdown = False
    
    for line in ce_content.splitlines():
        # Found any dropdown
        if "<DropDownList" in line:
            in_dropdown = True
            continue
        
        # End of dropdown
        if in_dropdown and "</DropDownList>" in line:
            in_dropdown = False
            continue
        
        # Parse dropdown entries: "100:Potion" or "2001:Leather Bangle"
        if in_dropdown:
            match = re.match(r'^(\d+)\s*:\s*(.+)$', line.strip())
            if match and match.group(2).lower() not in ['blank', 'default']:
                item_id = int(match.group(1))
                item_name = match.group(2).strip()
                # Avoid duplicates
                if (item_id, item_name) not in items:
                    items.append((item_id, item_name))
    
    return items

def categorize_items(items: list) -> dict:
    """Categorize items by ID range."""
    categories = {
        "consumables": [],    # 100-999
        "armor": [],          # 2000-2999
        "accessories": [],    # 9000-9999
        "materia": [],        # 10000+
        "other": []
    }
    
    for item_id, name in items:
        if 100 <= item_id < 1000:
            categories["consumables"].append((item_id, name))
        elif 2000 <= item_id < 3000:
            categories["armor"].append((item_id, name))
        elif 9000 <= item_id < 10000:
            categories["accessories"].append((item_id, name))
        elif item_id >= 10000:
            categories["materia"].append((item_id, name))
        else:
            categories["other"].append((item_id, name))
    
    return categories

def generate_python_dict(items: list, indent: int = 4) -> str:
    """Generate Python dictionary entries."""
    lines = []
    for item_id, name in sorted(items):
        # Escape quotes in item names
        safe_name = name.replace('"', '\\"')
        lines.append(f'{" " * indent}"{safe_name}": {item_id},')
    return '\n'.join(lines)

def main():
    print(f"Reading {CE_FILE}...")
    ce_content = CE_FILE.read_text(encoding='utf-8')
    
    print("Extracting items from all dropdowns...")
    items = extract_item_dropdown(ce_content)
    print(f"Found {len(items)} items")
    
    print("Categorizing items...")
    categories = categorize_items(items)
    
    print("\nGenerating item_mappings.py...")
    
    output = '''"""
Item Mappings: Archipelago Item Names → CE Memory IDs
========================================================

AUTO-GENERATED from ce.txt - DO NOT EDIT MANUALLY
Run tools/generate_item_mappings.py to regenerate

This file maps Archipelago item names to the memory IDs used by
the game's inventory system (from Cheat Engine table).

Memory ID Ranges:
- 100-999: Consumables (Potions, Ethers, Phoenix Downs, etc.)
- 2000-2999: Armor (Bangles, Bracers, Armlets)
- 9000-9999: Accessories (Rings, Earrings, Amulets, etc.)
- 10000+: Materia
"""

'''
    
    # Consumables
    if categories["consumables"]:
        output += f"# Consumables ({len(categories['consumables'])} items)\n"
        output += "CONSUMABLES = {\n"
        output += generate_python_dict(categories["consumables"])
        output += "\n}\n\n"
    
    # Armor
    if categories["armor"]:
        output += f"# Armor ({len(categories['armor'])} items)\n"
        output += "ARMOR = {\n"
        output += generate_python_dict(categories["armor"])
        output += "\n}\n\n"
    
    # Accessories
    if categories["accessories"]:
        output += f"# Accessories ({len(categories['accessories'])} items)\n"
        output += "ACCESSORIES = {\n"
        output += generate_python_dict(categories["accessories"])
        output += "\n}\n\n"
    
    # Materia
    if categories["materia"]:
        output += f"# Materia ({len(categories['materia'])} items)\n"
        output += "MATERIA = {\n"
        output += generate_python_dict(categories["materia"])
        output += "\n}\n\n"
    
    # Other
    if categories["other"]:
        output += f"# Other Items ({len(categories['other'])} items)\n"
        output += "OTHER = {\n"
        output += generate_python_dict(categories["other"])
        output += "\n}\n\n"
    
    # Combined mapping
    dict_names = [k.upper() for k in categories if categories[k]]
    output += "# Combined mapping for easy lookup\n"
    output += "ALL_ITEMS = {" + ", ".join(f"**{name}" for name in dict_names) + "}\n\n"
    
    # Helper function
    output += '''# Helper function to validate item names
def get_memory_id(item_name: str) -> int:
    """Get CE memory ID for an Archipelago item name."""
    if item_name in ALL_ITEMS:
        return ALL_ITEMS[item_name]
    raise ValueError(f"Unknown item: {item_name}")

def get_all_item_names() -> list:
    """Get list of all available item names."""
    return list(ALL_ITEMS.keys())
'''
    
    OUTPUT_FILE.write_text(output, encoding='utf-8')
    print(f"\n✓ Generated {OUTPUT_FILE}")
    print(f"\nSummary:")
    for category, items in categories.items():
        if items:
            print(f"  - {category.capitalize()}: {len(items)} items")
    print(f"\n  Total: {len(items)} items")

if __name__ == "__main__":
    main()
