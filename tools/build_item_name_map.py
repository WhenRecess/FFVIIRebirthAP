#!/usr/bin/env python3
"""
Build item name → ID mapping from CE item_mappings.py

Maps internal item names (it_potion, it_hipotion) to CE IDs (100, 101, etc.)
"""

import json
import re

def normalize_name(display_name):
    """Convert display name to internal name format."""
    # Remove special characters and convert to lowercase
    name = display_name.lower()
    
    # Common conversions
    name = name.replace('-', '')
    name = name.replace(' ', '')
    name = name.replace("'", '')
    
    # Specific mappings
    mappings = {
        'potion': 'it_potion',
        'hipotion': 'it_hipotion',
        'megapotion': 'it_megapotion',
        'gigapotion': 'it_gigapotion',
        'xpotion': 'it_xpotion',
        'mixedpotion': 'it_mixpotion',
        'mixedhipotion': 'it_mixhpotion',
        'mistpotion': 'it_mistpotion',
        'misthipotion': 'it_misthpotion',
        'mistmegapotion': 'it_mistmegapotion',
        'mistgigapotion': 'it_mistgigapotion',
        'ether': 'it_ether',
        'hiether': 'it_hiether',
        'dryether': 'it_dryether',
        'turboether': 'it_turboether',
        'elilxir': 'it_elixir',  # Typo in original
        'phoenixdown': 'it_phoenixdown',
        'phoenixdraft': 'it_phoenixdraft',
        'maidenskiss': 'it_maidenskiss',
        'antidote': 'it_antidote',
        'smellingsalts': 'it_smellingsalts',
        'echomist': 'it_echomist',
        'goldneedle': 'it_goldneedle',
        'adrenaline': 'it_adrenaline',
        'sedative': 'it_sedative',
        'remedy': 'it_remedy',
        'celeris': 'it_celeris',
        'grenade': 'it_grenade',
        'armorpiercinggrenade': 'it_grenade_ap',
        'hazardousmaterial': 'it_hazardous',
        'spiderweb': 'it_spiderweb',
        'molotovcocktail': 'it_molotov',
        'orbofgravity': 'it_gravity',
        'cushion': 'it_cushion',
        # Materials
        'ironore': 'it_material_iron',
        # Add more as needed
    }
    
    return mappings.get(name, None)

def build_name_to_id_map():
    """Build comprehensive item name → ID mapping."""
    
    # Manual mappings based on CE table structure
    # Format: internal_name → CE_ID
    name_to_id = {
        # Consumables
        'it_potion': 100,
        'it_hipotion': 101,
        'it_megapotion': 102,
        'it_gigapotion': 103,
        'it_xpotion': 104,
        'it_mixpotion': 105,
        'it_mixhpotion': 106,
        'it_mistpotion': 107,
        'it_misthpotion': 108,
        'it_mistmegapotion': 109,
        'it_mistgigapotion': 110,
        'it_ether': 111,
        'it_hiether': 112,
        'it_dryether': 113,
        'it_turboether': 114,
        'it_elixir': 115,
        'it_phoenixdown': 116,
        'it_phoenixdraft': 117,
        'it_maidenskiss': 118,
        'it_antidote': 119,
        'it_smellingsalts': 120,
        'it_echomist': 121,
        'it_goldneedle': 122,
        'it_adrenaline': 123,
        'it_sedative': 124,
        'it_remedy': 125,
        'it_celeris': 126,
        'it_grenade': 127,
        'it_grenade_ap': 128,
        'it_hazardous': 129,
        'it_spiderweb': 130,
        'it_molotov': 132,
        'it_gravity': 133,
        'it_cushion': 137,
        
        # Materials (crafting)
        'it_material_herb_001': 300,  # Sage
        'it_material_herb_002': 301,  # Oregano
        'it_material_herb_003': 302,  # Saint Luche Leaf
        'it_material_herb_004': 303,  # Pearl Ginger Root
        'it_material_herb_005': 304,  # Marjoram
        
        'it_material_ore_001': 321,   # Iron Ore
        'it_material_ore_002': 322,   # Zinc Ore
        'it_material_ore_003': 323,   # Chromite Ore
        'it_material_ore_004': 324,   # Lea Titanium
        'it_material_ore_005': 325,   # Tourmaline
        'it_material_ore_006': 326,   # Amethyst
        'it_material_ore_007': 327,   # Moss Agate
        'it_material_ore_008': 328,   # Crimsonite Crystal
        'it_material_ore_009': 329,   # Moonstone
        'it_material_ore_010': 330,   # Mythril Ore
        'it_material_ore_011': 331,   # Numinous Ashes
        'it_material_ore_012': 332,   # Cosmotite Ore
        'it_material_ore_013': 333,   # Gold Dust
        
        'it_material_wood_001': 342,  # Ancient Bark
        'it_material_wood_002': 343,  # Divine Heartwood
        'it_material_wood_003': 344,  # Mellow Oak
        'it_material_wood_004': 345,  # Condor Cedar
        'it_material_wood_005': 346,  # Sycamore Wood
        'it_material_wood_006': 347,  # Gongaga Pine
        'it_material_wood_007': 348,  # Baobab Wood
        'it_material_wood_008': 349,  # Ash Wood
        'it_material_wood_009': 350,  # Laurel
        'it_material_wood_010': 351,  # Mist Seeds
        
        'it_material_hide_001': 361,  # Beast Pelt
        'it_material_hide_002': 362,  # Exquisite Beast Hide
        
        'it_material_bone_001': 381,  # Beast Bone
        'it_material_bone_002': 382,  # Exquisite Beast Spine
        
        # Planet items
        'it_material_planet_001': 401,  # Planet's Blessing
        'it_material_planet_002': 402,  # Planet's Favor
        'it_material_planet_003': 403,  # Planet's Benison
        'it_material_planet_004': 404,  # Planet's Splendor
        'it_material_planet_005': 405,  # Ether Onion
        'it_material_planet_006': 406,  # Planet's Mercy
        'it_material_planet_007': 407,  # Planet's Spirit
        
        # Gems
        'it_material_gem_001': 421,  # Ruby
        'it_material_gem_002': 422,  # Emerald
        'it_material_gem_003': 423,  # Sapphire
        
        # Enemy materials
        'it_material_enemy_001': 431,  # Beast Talon
        'it_material_enemy_002': 432,  # Astral Remnant
        'it_material_senemy_001': 433,  # Slimy Malboro Tendril
        'it_material_senemy_002': 434,  # Heavy Jabberwock Horn
    }
    
    return name_to_id

def save_mapping(output_path='tools/_item_name_to_id.json'):
    """Save the mapping to JSON file."""
    mapping = build_name_to_id_map()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    
    print(f"Saved {len(mapping)} item name → ID mappings to {output_path}")
    
    # Show samples
    print("\nSample mappings:")
    for i, (name, item_id) in enumerate(sorted(mapping.items())[:20]):
        print(f"  {name:30s} → {item_id}")
    
    return mapping

if __name__ == '__main__':
    mapping = save_mapping()
