import re
import json
import os

def extract_all_dropdowns(ce_txt_path):
    """Extract all CE ID dropdowns from ce.txt"""
    
    with open(ce_txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all dropdown sections
    dropdown_pattern = r'<DropDownList[^>]*>(.*?)</DropDownList>'
    dropdowns = re.findall(dropdown_pattern, content, re.DOTALL)
    
    all_ids = {}
    
    for i, dropdown in enumerate(dropdowns):
        # Parse each line in the dropdown
        lines = dropdown.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and ':' in line:
                try:
                    parts = line.split(':', 1)
                    ce_id = int(parts[0].strip())
                    item_name = parts[1].strip()
                    
                    # Skip duplicates
                    if ce_id not in all_ids:
                        all_ids[ce_id] = item_name
                except (ValueError, IndexError):
                    continue
    
    return all_ids

if __name__ == "__main__":
    # Try both relative and parent directory
    ce_path = "ce.txt"
    if not os.path.exists(ce_path):
        ce_path = "../ce.txt"
    if not os.path.exists(ce_path):
        print(f"Error: ce.txt not found")
        exit(1)
    
    all_ids = extract_all_dropdowns(ce_path)
    
    print(f"Found {len(all_ids)} CE item ID mappings from all dropdowns\n")
    print("Sample CE IDs (first 50):")
    for i, (ce_id, name) in enumerate(sorted(all_ids.items())[:50]):
        print(f"  {ce_id}: {name}")
    
    # Save to JSON
    output_path = "tools/_ce_all_real_ids.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_ids, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(all_ids)} mappings to {output_path}")
    
    # Print stats by ID range
    ranges = {
        "Consumables (100-199)": range(100, 200),
        "Materials (300-399)": range(300, 400),
        "Armor (2000-2199)": range(2000, 2200),
        "Accessories (9000-9199)": range(9000, 9200),
    }
    
    print("\nIDs by category:")
    for category, id_range in ranges.items():
        count = sum(1 for ce_id in all_ids if ce_id in id_range)
        if count > 0:
            print(f"  {category}: {count} items")
