"""
Randomizer Options for Final Fantasy VII: Rebirth
================================================================

This module defines all configurable options for the FFVII Rebirth
randomizer. Options control how the game is randomized and what
content is included in the multiworld.

Option Categories:
    Progression Options:
        - ChapterProgression: How chapter unlocks work
        - PartyMemberRandomization: How party members are obtained
    
    Content Options:
        - ColosseumIncluded: Include colosseum battles as checks
        - VRSimulatorIncluded: Include VR battles as checks
        - QuestsIncluded: Include side quests as checks
        - MinigamesIncluded: Include minigames as checks
    
    Randomization Depth:
        - SummonRandomization: How summons are distributed
        - MateriaRandomization: How materia is distributed
        - EquipmentRandomization: How equipment is distributed
    
    Difficulty/Balance:
        - TrapItems: Include negative effect items
        - TrapPercentage: How many traps to include
        - StartingGil: Starting currency amount
        - StartingLevel: Starting character level
    
    Goal Settings:
        - GoalType: What's required to complete the game
        - RequiredBossCount: Number of bosses for boss goal
    
    Multiplayer:
        - DeathLink: Shared death between players

The FFVIIRebirthOptions dataclass at the end aggregates all options
for use by the main world class.
"""
from dataclasses import dataclass
from Options import (
    Toggle, Choice, Range, OptionSet, PerGameCommonOptions,
    DefaultOnToggle, StartInventoryPool
)


class ChapterProgression(Choice):
    """
    How chapter progression items are distributed.
    
    - Vanilla: Chapter unlocks happen automatically through story
    - Randomized: Chapter unlocks are randomized items
    - Open World: All chapters accessible from start (except final)
    """
    display_name = "Chapter Progression"
    option_vanilla = 0
    option_randomized = 1
    option_open_world = 2
    default = 1


class PartyMemberRandomization(Choice):
    """
    How party members are obtained.
    
    - Vanilla: Party members join at story points
    - Randomized: Party members are randomized items
    - All Available: All party members from start
    """
    display_name = "Party Member Randomization"
    option_vanilla = 0
    option_randomized = 1
    option_all_available = 2
    default = 0


class ColosseumIncluded(DefaultOnToggle):
    """
    Include Colosseum battles as locations.
    
    When enabled, each Colosseum battle is a check that awards an item.
    """
    display_name = "Include Colosseum"


class VRSimulatorIncluded(DefaultOnToggle):
    """
    Include VR Simulator battles as locations.
    
    When enabled, VR Summon battles and combat simulations are checks.
    """
    display_name = "Include VR Simulator"


class SummonRandomization(Choice):
    """
    How Summon Materia is obtained.
    
    - Vanilla: Summons obtained at normal locations
    - Randomized: Summons are in the item pool
    - Starting: Start with all summons
    """
    display_name = "Summon Randomization"
    option_vanilla = 0
    option_randomized = 1
    option_starting = 2
    default = 1


class MateriaRandomization(Choice):
    """
    How Materia is handled in randomization.
    
    - Vanilla: Materia found at normal locations
    - Shuffled: Materia locations contain other materia
    - Full Random: Materia mixed into full item pool
    """
    display_name = "Materia Randomization"
    option_vanilla = 0
    option_shuffled = 1
    option_full_random = 2
    default = 1


class EquipmentRandomization(Choice):
    """
    How equipment (weapons, armor, accessories) is handled.
    
    - Vanilla: Equipment at normal locations
    - Shuffled: Equipment shuffled within equipment pool
    - Full Random: Equipment mixed into full item pool
    """
    display_name = "Equipment Randomization"
    option_vanilla = 0
    option_shuffled = 1
    option_full_random = 2
    default = 1


class QuestsIncluded(DefaultOnToggle):
    """
    Include side quest completions as locations.
    """
    display_name = "Include Side Quests"


class MinigamesIncluded(DefaultOnToggle):
    """
    Include minigame completions as locations (Queen's Blood, Chocobo Racing, etc.)
    """
    display_name = "Include Minigames"


class TrapItems(Toggle):
    """
    Include trap items in the item pool.
    
    Traps can cause negative effects like poison, confusion, or gil loss.
    """
    display_name = "Include Trap Items"


class TrapPercentage(Range):
    """
    Percentage of filler items to replace with traps (if enabled).
    """
    display_name = "Trap Percentage"
    range_start = 0
    range_end = 50
    default = 10


class StartingGil(Range):
    """
    Amount of Gil to start with.
    """
    display_name = "Starting Gil"
    range_start = 0
    range_end = 99999
    default = 500


class StartingLevel(Range):
    """
    Starting level for Cloud (other party members scale accordingly).
    """
    display_name = "Starting Level"
    range_start = 1
    range_end = 50
    default = 1


class DeathLink(Toggle):
    """
    When you die, everyone who enabled death link dies.
    When anyone dies, you die.
    """
    display_name = "Death Link"


class GoalType(Choice):
    """
    What is required to complete the game.
    
    - Story Complete: Beat the main story
    - All Bosses: Defeat all major bosses
    - Colosseum Champion: Complete all Colosseum tiers
    - Full Completion: All of the above
    """
    display_name = "Goal Type"
    option_story_complete = 0
    option_all_bosses = 1
    option_colosseum_champion = 2
    option_full_completion = 3
    default = 0


class RequiredBossCount(Range):
    """
    Number of major bosses required (for All Bosses goal).
    """
    display_name = "Required Boss Count"
    range_start = 1
    range_end = 20
    default = 10


@dataclass
class FFVIIRebirthOptions(PerGameCommonOptions):
    """Options dataclass for FFVII Rebirth."""
    
    # Progression options
    chapter_progression: ChapterProgression
    party_member_randomization: PartyMemberRandomization
    
    # Content options
    colosseum_included: ColosseumIncluded
    vr_simulator_included: VRSimulatorIncluded
    quests_included: QuestsIncluded
    minigames_included: MinigamesIncluded
    
    # Randomization depth
    summon_randomization: SummonRandomization
    materia_randomization: MateriaRandomization
    equipment_randomization: EquipmentRandomization
    
    # Traps
    trap_items: TrapItems
    trap_percentage: TrapPercentage
    
    # Starting conditions
    starting_gil: StartingGil
    starting_level: StartingLevel
    start_inventory_from_pool: StartInventoryPool
    
    # Goal
    goal_type: GoalType
    required_boss_count: RequiredBossCount
    
    # Multiplayer
    death_link: DeathLink
