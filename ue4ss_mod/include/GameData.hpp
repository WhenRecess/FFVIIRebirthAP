#pragma once

#include <string>
#include <unordered_map>
#include <vector>

namespace FFVIIRebirthAP {

/**
 * @brief GameData manages item and location mappings for Archipelago integration.
 * 
 * Loads CSV files containing item names, location names, and their IDs.
 * Provides methods to query and validate game data.
 */
class GameData {
public:
    GameData() = default;
    ~GameData() = default;

    /**
     * @brief Load item mappings from a CSV file.
     * 
     * CSV format:
     *   ItemName,ItemID
     *   Buster Sword,1000
     *   Bronze Bangle,2000
     * 
     * @param filepath Path to items CSV file
     * @return true if loaded successfully, false otherwise
     */
    bool LoadItemsCSV(const std::string& filepath);

    /**
     * @brief Load location mappings from a CSV file.
     * 
     * CSV format:
     *   LocationName,LocationID
     *   Boss: Scorpion Sentinel,1
     *   Chest: Sector 7 Slums,2
     * 
     * @param filepath Path to locations CSV file
     * @return true if loaded successfully, false otherwise
     */
    bool LoadLocationsCSV(const std::string& filepath);

    /**
     * @brief Get item ID by name.
     * 
     * @param name Item name
     * @return Item ID, or -1 if not found
     */
    int64_t GetItemID(const std::string& name) const;

    /**
     * @brief Get location ID by name.
     * 
     * @param name Location name
     * @return Location ID, or -1 if not found
     */
    int64_t GetLocationID(const std::string& name) const;

    /**
     * @brief Get item name by ID.
     * 
     * @param id Item ID
     * @return Item name, or empty string if not found
     */
    std::string GetItemName(int64_t id) const;

    /**
     * @brief Get location name by ID.
     * 
     * @param id Location ID
     * @return Location name, or empty string if not found
     */
    std::string GetLocationName(int64_t id) const;

    /**
     * @brief Get all item names.
     * 
     * @return Vector of item names
     */
    std::vector<std::string> GetAllItemNames() const;

    /**
     * @brief Get all location names.
     * 
     * @return Vector of location names
     */
    std::vector<std::string> GetAllLocationNames() const;

    /**
     * @brief Clear all loaded data.
     */
    void Clear();

    /**
     * @brief Check if data is loaded.
     * 
     * @return true if both items and locations are loaded, false otherwise
     */
    bool IsLoaded() const;

private:
    // Map: item name -> item ID
    std::unordered_map<std::string, int64_t> item_name_to_id_;
    // Map: item ID -> item name
    std::unordered_map<int64_t, std::string> item_id_to_name_;
    
    // Map: location name -> location ID
    std::unordered_map<std::string, int64_t> location_name_to_id_;
    // Map: location ID -> location name
    std::unordered_map<int64_t, std::string> location_id_to_name_;

    bool items_loaded_ = false;
    bool locations_loaded_ = false;
};

} // namespace FFVIIRebirthAP
