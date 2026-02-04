#!/usr/bin/env python3
"""
Filter UE4SS Live View function dumps to find useful hooks for Archipelago.

Usage:
    python filter_ue4ss_functions.py input_file.txt [output_file.txt]
    python filter_ue4ss_functions.py input_file.txt --categorize
    
If no output file is specified, prints to stdout.
Use --categorize to organize output by category.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Set
from collections import defaultdict


# =============================================================================
# EXCLUSION PATTERNS - Things we definitely don't care about
# =============================================================================

EXCLUDE_PATTERNS = [
    # Delegate signatures (not actual callable functions)
    r"DelegateFunction",
    r"__DelegateSignature",
    
    # VFX/Particles/Effects (visual only, no gameplay)
    r"NiagaraDataInterfaceFunctionLibrary",
    r"VFXNiagaraDataInterfaceFunctionLibrary",
    r"EndNiagaraDataInterfaceFunctionLibrary",
    r"/Game/Effect/",
    r"FX_R_Item_",
    r"FX_Menu_",
    r"Particle/",
    r"/Script/Niagara\.",
    
    # UI Animation sequences (MovieScene = Unreal's UI animation system)
    # These are DATA not hookable functions
    r"MovieScene",
    r"_INST\.",              # Animation instance properties
    r"_INST$",               # Animation instance names ending lines
    r"CompiledData",
    r"WidgetTree",           # Widget tree structure (not functions)
    r"\.EndCanvasPanelSlot",
    r"Icon_Complete",        # UI icons
    r"Txt_Complete",         # UI text labels
    r"Deco_Complete",        # UI decorations
    r"Pnl_Deco_",            # Panel decorations
    r"/Icon_Currency",       # Currency icon assets
    r"\.Icon_[A-Z]",         # Icon assets in general
    
    # UI setup/measurement functions (not interactions)
    r":OnSetupItem\b",
    r":OnMeasureItem\b",
    r":SetupItem\b",
    r":MeasureItem\b",
    r":OnCleanupItem\b",
    r":RefreshItem\b",
    r":RefreshItems\b",
    r":SetItemCount\b",
    r":SetItems\b",
    
    # Widget construction (UI building, not gameplay)
    r":Construct\b",
    r":ExecuteUbergraph_",
    r"BndEvt__.*_K2Node_",
    
    # Generic engine/module functions
    r"/Script/Engine\.",
    r"/Script/AIModule\.",
    r"/Script/UMG\.",
    r"/Script/ControlRig\.",
    r"/Script/EngineSettings\.",
    r"/Script/AudioMixer\.",
    r"/Script/SQEXSEAD\.",
    r"/Script/OnlineSubsystem",
    r"/Script/Paper2D\.",
    r"/Script/ImageWriteQueue\.",
    r"/Script/GameplayTasks\.",
    r"/Script/MeshModelingTools\.",
    r"EnvQuery",
    r"BlueprintSetLibrary",
    r"KismetArrayLibrary",
    r"PrimitiveComponent:",
    
    # Asset paths (textures, materials, physics assets - not code)
    r"/Game/Environment/",
    r"/Game/Sound/",
    r"/Game/Character/",           # Character model/texture assets
    r"/Game/Motion/",              # Animation assets
    r"/Game/DataAsset/",           # Data assets
    r"/Texture/",                  # Texture subfolders
    r"/Model/",                    # Model subfolders
    r"/Material/",                 # Material subfolders
    r"/Emissive/",                 # Emissive texture subfolders
    
    # Blueprint/mesh component internals (not hookable)
    r"_Skeleton\b",
    r"_PhysicsAsset",
    r"PhysicsConstraintTemplate",
    r"SkeletalBodySetup",
    r"SkeletalMeshSocket",
    r"SimpleConstructionScript",
    r"DefaultSceneRoot",
    r"InheritableComponentHandler",
    r"EndBodyCollisionPrimitive",
    r"_GEN_VARIABLE",
    r"EndEmissiveColorUserData",
    r"EndAnimNotify",
    r"/Texture/T_",
    r"/Game/BluePrint/Character/Property/",  # Character property blueprints (assets)
    
    # Light/visual settings
    r"_Light\.",
    r"_Light_C:",
    r"_LightSetting",
    r"_LightCraft",
    r"Cell_Light",
    
    # Generic list operations (too low-level)
    r"ListView:",
    r"TreeView:",
    r"UserListEntry",
    r"UserObjectListEntry",
    
    # Scroll box internals
    r"EndVirtualScrollBox:",
    r"EndListBox:",
    r"EndStringListBox:",
    r"EndStringScrollBox:",
    
    # Texture/asset references (not code)
    r"/Game/Menu/Resident/Texture/",
    r"\.BodySetup_",
    
    # Data structure definitions (not hookable functions)
    r"Default__",                    # Default object instances
    r"Accessor\b",                   # Accessor class definitions
    r"_Array\b",                     # Array property definitions  
    r"/Game/DataObject/",            # Data object assets (not functions)
    
    # Class/type definitions without actual function calls
    # Pattern: ends with .ClassName or .ClassName_C without :FunctionName
    r"\.[A-Z][a-zA-Z0-9_]*$",        # Ends in .ClassName (asset reference)
    r"\.[A-Z][a-zA-Z0-9_]*_C$",      # Ends in .ClassName_C (blueprint class)
    
    # Enum definitions (must start with E then another uppercase, like EItemType)
    # Use (?-i:...) to disable case-insensitivity for this pattern
    r"(?-i:\.E[A-Z][a-zA-Z]+)\b",    # Enum types (EEnumName pattern)
    
    # DataTable/DataObject property definitions (not functions)
    # These are field/property definitions, not callable functions
    # Pattern: EndDataTable<Name>:<PropertyName> where PropertyName is not On*/Get*/Set*
    r"EndDataTable\w+:[A-Z](?!n[A-Z])",   # DataTable:Property (but not :On*)
    r"EndDataObject\w+:[A-Z](?!n[A-Z])",  # DataObject:Property (but not :On*)
    
    # Specific property patterns that are never functions
    r":[A-Z][a-z]+[A-Z].*(?:ID|Flag|Name|Type|Offset|Index|Count|Size|Array|List|Percent|Coefficient|Distance|Gauge|Trigger|Camera|Pic|Text|Hint|Unit|Digit)$",
    
    # Class definitions without function calls (no :FunctionName after class)
    r"EndDataObject[A-Z]\w+$",       # EndDataObjectClassName (no function)
    r"EndDataTable[A-Z]\w+$",        # EndDataTableClassName (no function)
]

# Compile patterns for efficiency
EXCLUDE_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in EXCLUDE_PATTERNS]


# =============================================================================
# INCLUSION PATTERNS - Things we definitely want to keep
# =============================================================================

# High priority keywords that should always be kept
# These look for FUNCTION patterns (with : before them) not just any occurrence
HIGH_PRIORITY_KEYWORDS = [
    # Item system (actual functions)
    r":AddItem", r":GiveItem", r":ReceiveItem", r":AcquireItem",
    r":GetItemNum", r":HasItem", r":RemoveItem", r":UseItem",
    r":SetItem\b",  # Not SetItems (list operation)
    
    # Currency
    r":AddGil", r":SetGil", r":GetGil",
    r"Gil\b", r"Money", r"Currency",
    
    # Rewards/Completion (function calls)
    r":OnReward", r":GiveReward", r":AddReward",
    r"BattleReward", r"QuestReward",
    r":OnComplete\b", r":SetComplete", r":IsComplete",
    r":OnFinish", r":Finish\b",
    r":OnClear", r":Clear\b",
    r":OnExit", r":OnEnd\b",
    
    # Progress/Save (function calls)
    r":SaveData", r":LoadData", r":OnSave", r":OnLoad",
    r":SetFlag", r":GetFlag", r":CheckFlag", r":IsStoryFlag", r":SetStoryFlag",
    r":Unlock\b", r":SetUnlock",
    
    # Battle (function calls)
    r":OnBattleEnd", r":OnBattleComplete", r":BattleResult",
    r":OnVictory", r":OnDefeat",
    r"ExitBattleScene", r"EnterBattleScene",
    
    # Pickup/Treasure (function calls)
    r":OnPickup", r":Pickup\b",
    r":OpenChest", r":OpenBox", r":OpenTreasure",
    r"TreasureBox",
    
    # Database API functions (very useful) - THE CORE GAME APIs
    r"EndDataBaseDataBaseAPI:",
    r"EndBattleAPI:",
    r"EndBattleCountAPI:",
    
    # Chapter/Progress
    r":GetChapterProgress", r":SetChapter",
    r":GetLocationWork", r":SetLocationWork",
    r":GetResidentWork", r":SetResidentWork",
]

HIGH_PRIORITY_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in HIGH_PRIORITY_KEYWORDS]


# =============================================================================
# CATEGORY DEFINITIONS
# =============================================================================

CATEGORIES = {
    "BATTLE": [
        r"Battle", r"Combat", r"Fight", r"Enemy",
        r"btsc_", r"BattleScene",
    ],
    "ITEM_INVENTORY": [
        r"Item", r"Inventory", r"GetItemNum",
        r"EndMainItemMenu", r"EndItemWindow", r"EndItemCraft",
    ],
    "EQUIPMENT_MATERIA": [
        r"Equip", r"Materia", r"Weapon", r"Armor", r"Accessory",
        r"WeaponCore", r"SummonMateria",
    ],
    "COLOSSEUM_VR": [
        r"Colosseum", r"COL30", r"Summon.*Level", r"VR",
    ],
    "SHOP": [
        r"Shop", r"Buy", r"Sell", r"Purchase", r"Vendor",
    ],
    "QUEST_STORY": [
        r"Quest", r"Story", r"Chapter", r"Mission", r"Objective",
    ],
    "SAVE_LOAD": [
        r"Save", r"Load", r"DataSlot",
    ],
    "MINIGAME": [
        r"Card", r"Queen.*Blood", r"Chocobo", r"Boxing", r"Piano",
        r"Race", r"Condor", r"Fort",
    ],
    "PARTY_CHARACTER": [
        r"Member", r"Party", r"Character", r"Costume",
        r"Cloud", r"Tifa", r"Aerith", r"Barret", r"Yuffie", r"RedXIII",
    ],
    "MENU_UI": [
        r"Menu", r"Window", r"Pause",
    ],
}

CATEGORY_REGEX = {
    cat: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for cat, patterns in CATEGORIES.items()
}


# =============================================================================
# FILTERING LOGIC
# =============================================================================

def should_exclude(line: str) -> bool:
    """Check if a line should be excluded."""
    for pattern in EXCLUDE_REGEX:
        if pattern.search(line):
            return True
    return False


def is_high_priority(line: str) -> bool:
    """Check if a line matches high-priority keywords."""
    for pattern in HIGH_PRIORITY_REGEX:
        if pattern.search(line):
            return True
    return False


def is_useful_interaction(line: str) -> bool:
    """Check if line represents a useful user interaction."""
    # PressedItem functions are user interactions
    if "PressedItem" in line:
        return True
    # SelectedIndexChanged can indicate selection
    if "SelectedIndexChanged" in line:
        return True
    # OnPressed, OnClicked indicate button interactions
    if re.search(r"On(Pressed|Clicked|Selected)\b", line):
        return True
    return False


def is_game_specific(line: str) -> bool:
    """Check if line is from game-specific code (not generic engine)."""
    game_namespaces = [
        "/Script/EndGame.",
        "/Script/EndDataBase.",
        "/Game/Menu/",
        "/Game/BluePrint/",
    ]
    return any(ns in line for ns in game_namespaces)


def categorize_line(line: str) -> str:
    """Determine the category for a line."""
    for category, patterns in CATEGORY_REGEX.items():
        for pattern in patterns:
            if pattern.search(line):
                return category
    return "OTHER"


def extract_function_name(line: str) -> str:
    """Extract the function path from a raw line."""
    # Try to find the function path pattern
    # Format: Function /Script/Module.Class:FunctionName or /Game/Path.Class_C:FunctionName
    match = re.search(r"(Function\s+)?(/(?:Script|Game)/[^\s\[]+)", line)
    if match:
        return match.group(2)
    return line.strip()


def filter_functions(lines: List[str]) -> List[Tuple[str, str, bool]]:
    """
    Filter function lines and return (function_name, category, is_high_priority) tuples.
    """
    results = []
    seen = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Must be a Function line (not just any text)
        if "Function " not in line and "/Script/" not in line and "/Game/" not in line:
            continue
        
        # Extract clean function name FIRST
        func_name = extract_function_name(line)
        
        # Deduplicate early
        if func_name in seen:
            continue
            
        # Skip if matches exclusion patterns (check extracted name, not raw line)
        if should_exclude(func_name):
            continue
        
        # Check if it's useful
        high_priority = is_high_priority(func_name)
        useful_interaction = is_useful_interaction(func_name)
        game_specific = is_game_specific(func_name)
        
        # Keep if: high priority OR (useful interaction AND game-specific)
        if not (high_priority or (useful_interaction and game_specific)):
            continue
        
        seen.add(func_name)
        
        # Categorize
        category = categorize_line(func_name)
        
        results.append((func_name, category, high_priority))
    
    return results


# =============================================================================
# OUTPUT FORMATTING
# =============================================================================

def format_output_flat(results: List[Tuple[str, str, bool]]) -> str:
    """Format results as a flat list."""
    lines = []
    lines.append("# Filtered UE4SS Functions for Archipelago Hooks")
    lines.append("# High priority items marked with [!]")
    lines.append("")
    
    for func_name, category, high_priority in sorted(results, key=lambda x: (x[1], x[0])):
        marker = "[!] " if high_priority else "    "
        lines.append(f"{marker}{func_name}")
    
    return "\n".join(lines)


def format_output_categorized(results: List[Tuple[str, str, bool]]) -> str:
    """Format results organized by category."""
    by_category = defaultdict(list)
    for func_name, category, high_priority in results:
        by_category[category].append((func_name, high_priority))
    
    lines = []
    lines.append("# Filtered UE4SS Functions for Archipelago Hooks")
    lines.append("# Organized by category, high priority marked with [!]")
    lines.append("")
    
    # Define category order
    category_order = [
        "BATTLE",
        "ITEM_INVENTORY", 
        "EQUIPMENT_MATERIA",
        "COLOSSEUM_VR",
        "SHOP",
        "QUEST_STORY",
        "SAVE_LOAD",
        "MINIGAME",
        "PARTY_CHARACTER",
        "MENU_UI",
        "OTHER",
    ]
    
    for category in category_order:
        if category not in by_category:
            continue
        
        funcs = sorted(by_category[category], key=lambda x: x[0])
        
        lines.append("=" * 80)
        lines.append(f"## {category.replace('_', ' ')}")
        lines.append("=" * 80)
        lines.append("")
        
        for func_name, high_priority in funcs:
            marker = "[!] " if high_priority else "    "
            lines.append(f"{marker}{func_name}")
        
        lines.append("")
    
    return "\n".join(lines)


def print_stats(results: List[Tuple[str, str, bool]], original_count: int):
    """Print filtering statistics."""
    high_priority_count = sum(1 for _, _, hp in results if hp)
    by_category = defaultdict(int)
    for _, cat, _ in results:
        by_category[cat] += 1
    
    print(f"\n--- Filtering Statistics ---", file=sys.stderr)
    print(f"Original lines: {original_count}", file=sys.stderr)
    print(f"Filtered results: {len(results)}", file=sys.stderr)
    print(f"Reduction: {100 * (1 - len(results)/max(original_count, 1)):.1f}%", file=sys.stderr)
    print(f"High priority: {high_priority_count}", file=sys.stderr)
    print(f"\nBy category:", file=sys.stderr)
    for cat in sorted(by_category.keys()):
        print(f"  {cat}: {by_category[cat]}", file=sys.stderr)


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: Input file '{input_file}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Parse arguments
    categorize = "--categorize" in sys.argv or "-c" in sys.argv
    output_file = None
    for arg in sys.argv[2:]:
        if not arg.startswith("-"):
            output_file = Path(arg)
            break
    
    # Read input
    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    original_count = len(lines)
    
    # Load existing results if output file exists (for deduplication)
    existing_funcs = set()
    if output_file:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Extract function path from formatted lines (with or without [!] prefix)
                    if line.startswith("[!] /"):
                        existing_funcs.add(line[4:])
                    elif line.startswith("/"):
                        existing_funcs.add(line)
        except FileNotFoundError:
            pass  # File doesn't exist yet, that's fine
    
    # Filter
    results = filter_functions(lines)
    
    # Remove duplicates that already exist in output file
    new_results = [(func, cat, hp) for func, cat, hp in results if func not in existing_funcs]
    new_count = len(new_results)
    dup_count = len(results) - new_count
    
    # Decide what to output
    if existing_funcs:
        # Output file exists - only write if we have new results
        if new_results:
            # Re-read existing file to preserve formatting, then append new
            with open(output_file, "r", encoding="utf-8") as f:
                existing_content = f.read().rstrip()
            
            # Format only new results
            if categorize:
                new_output = format_output_categorized(new_results)
            else:
                new_output = format_output_flat(new_results)
            
            # Remove header from new output and append
            new_lines = new_output.split('\n')
            # Find where actual content starts (after header comments)
            content_start = 0
            for i, line in enumerate(new_lines):
                if line.startswith("==") or line.startswith("/") or line.startswith("[!] /"):
                    content_start = i
                    break
            output = existing_content + "\n\n# --- New entries from this run ---\n" + '\n'.join(new_lines[content_start:])
        else:
            # No new results, don't modify file
            print(f"No new entries found (skipped {dup_count} duplicates)", file=sys.stderr)
            print_stats(results, original_count)
            return
    else:
        # No existing file - write fresh
        if categorize:
            output = format_output_categorized(results)
        else:
            output = format_output_flat(results)
        new_count = len(results)
        dup_count = 0
    
    # Write output
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {output_file}", file=sys.stderr)
        if existing_funcs:
            print(f"  (Added {len(new_results)} new, skipped {len(results) - len(new_results)} duplicates)", file=sys.stderr)
    else:
        print(output)
    
    # Stats
    print_stats(new_results if existing_funcs else results, original_count)


if __name__ == "__main__":
    main()
