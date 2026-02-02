#pragma once

#include <string>
#include <vector>
#include <cstdint>

/**
 * GameData namespace
 * 
 * Provides functions to interact with Final Fantasy VII: Rebirth game state.
 * All functions are skeleton implementations with TODO markers for game-specific logic.
 */
namespace GameData {

    /**
     * Check if game data is loaded and ready for access
     * @return true if game data structures are accessible
     */
    bool IsLoaded();

    /**
     * Get the current map/zone identifier
     * @return Map name or identifier as a string
     */
    std::string GetCurrentMap();

    /**
     * Get the current save file name
     * @return Save file name or identifier
     */
    std::string GetSaveName();

    /**
     * Set the current save file name (for tracking AP slot)
     * @param saveName The save file name to set
     */
    void SetSaveName(const std::string& saveName);

    /**
     * Trigger a game save operation
     * @return true if save was successful
     */
    bool SaveGame();

    /**
     * Check if any encounter spots (locations) have been triggered
     * Should be called periodically to detect location checks
     * @return Vector of location IDs that were triggered this frame
     */
    std::vector<int64_t> CheckEncounterSpots();

    /**
     * Check if the player has died (for DeathLink)
     * @return true if player death was detected this frame
     */
    bool CheckDeath();

    /**
     * Called when an item is received from the AP server
     * Should add the item to the player's inventory
     * @param itemCode The AP item code to receive
     * @param playerName The name of the player who sent the item
     */
    void ReceiveItem(int64_t itemCode, const std::string& playerName);

    /**
     * Give an item to the player by its internal game code
     * @param itemCode The game's internal item identifier
     * @param count Number of items to give
     * @return true if item was successfully given
     */
    bool GiveItemByCode(int32_t itemCode, int32_t count = 1);

    /**
     * Replace an enemy template in a territory with a different one
     * Used for enemy randomization
     * @param territoryIndex The territory/zone index
     * @param slotIndex The enemy slot to replace
     * @param newTemplateId The new enemy template ID to use
     * @return true if replacement was successful
     */
    bool ReplaceEnemyTemplate(int32_t territoryIndex, int32_t slotIndex, int32_t newTemplateId);

    /**
     * Print a message to the game console
     * @param message The message to print
     */
    void PrintToConsole(const std::string& message);

    /**
     * Print a formatted message to the game console
     * @param format Format string (printf-style)
     * @param ... Format arguments
     */
    void PrintToConsole(const char* format, ...);

} // namespace GameData
