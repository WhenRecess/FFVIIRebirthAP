#pragma once

#include <string>
#include <vector>
#include <cstdint>

/**
 * GameData namespace provides an interface to FFVII: Rebirth's game state
 * All functions are stubs/skeletons and require game-specific implementation
 */
namespace GameData {

    /**
     * Check if game data is loaded and accessible
     * @return true if game is loaded and ready for data access
     */
    bool IsLoaded();

    /**
     * Get the current map/territory identifier
     * @return Current map name or ID (e.g., "Grasslands", "Junon", etc.)
     */
    std::string GetCurrentMap();

    /**
     * Get the current save file name/slot
     * @return Save file identifier
     */
    std::string GetSaveName();

    /**
     * Set/select a save file slot
     * @param saveName Save file identifier to load
     */
    void SetSaveName(const std::string& saveName);

    /**
     * Trigger a game save operation
     * @return true if save was successful
     */
    bool SaveGame();

    /**
     * Check for newly completed encounters/battles
     * Called periodically to detect location checks
     * @return Vector of location IDs that were completed since last check
     */
    std::vector<uint64_t> CheckEncounterSpots();

    /**
     * Check if player has died (for DeathLink)
     * @return true if player death detected since last check
     */
    bool CheckDeath();

    /**
     * Receive an item from Archipelago
     * Called when the AP server sends an item to this player
     * @param itemCode Archipelago item code
     * @param itemName Human-readable item name
     * @param playerName Name of player who sent the item
     */
    void ReceiveItem(uint64_t itemCode, const std::string& itemName, const std::string& playerName);

    /**
     * Give an item to the player by AP item code
     * Translates AP item code to game item ID and adds to inventory
     * @param itemCode Archipelago item code
     * @return true if item was successfully given
     */
    bool GiveItemByCode(uint64_t itemCode);

    /**
     * Replace an enemy template in a territory
     * Used for enemy randomization
     * @param territoryIndex Territory/map index
     * @param slotIndex Enemy slot index within territory
     * @param newEnemyId New enemy template ID to use
     * @return true if replacement was successful
     */
    bool ReplaceEnemyTemplate(uint32_t territoryIndex, uint32_t slotIndex, uint32_t newEnemyId);

    /**
     * Print a message to the game's console/log
     * @param message Message to display
     */
    void PrintToConsole(const std::string& message);

    /**
     * Print a formatted message to console
     * @param format Format string (printf-style)
     * @param args Variadic arguments for formatting
     */
    template<typename... Args>
    void PrintToConsole(const char* format, Args... args) {
        char buffer[512];
        snprintf(buffer, sizeof(buffer), format, args...);
        PrintToConsole(std::string(buffer));
    }

    // Internal helper structures (TODO: define based on game data)
    
    /**
     * Territory/map data structure
     * TODO: Define based on actual game DataTable structure
     */
    struct TerritoryData {
        uint32_t uniqueIndex;
        std::string territoryName;
        std::vector<uint32_t> mobTemplateList;
        std::vector<uint32_t> waveMobTemplateList;
    };

    /**
     * Item data structure
     * TODO: Define based on actual game item structure
     */
    struct ItemData {
        uint32_t itemId;
        std::string itemName;
        uint32_t itemType;
        uint32_t quantity;
    };

    /**
     * Find territory data by index
     * TODO: Implement by scanning game memory or reading from exports
     * @param territoryIndex Territory unique index
     * @return Territory data if found, nullptr otherwise
     */
    TerritoryData* FindTerritoryByIndex(uint32_t territoryIndex);

    /**
     * Find array containing mob template lists
     * Heuristic search for arrays named "MobTemplateList" or "WaveMobTemplateList"
     * TODO: Implement based on UE4 reflection or memory scanning
     * @return true if arrays were located
     */
    bool FindMobTemplateLists();

} // namespace GameData
