#include "GameData.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>

namespace FFVIIRebirthAP {

bool GameData::LoadItemsCSV(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        return false;
    }

    item_name_to_id_.clear();
    item_id_to_name_.clear();

    std::string line;
    // Skip header line
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) continue;

        std::stringstream ss(line);
        std::string name;
        std::string id_str;

        // Parse CSV: ItemName,ItemID
        std::getline(ss, name, ',');
        std::getline(ss, id_str, ',');

        // Trim whitespace
        name.erase(0, name.find_first_not_of(" \t\r\n"));
        name.erase(name.find_last_not_of(" \t\r\n") + 1);
        id_str.erase(0, id_str.find_first_not_of(" \t\r\n"));
        id_str.erase(id_str.find_last_not_of(" \t\r\n") + 1);

        if (name.empty() || id_str.empty()) continue;

        try {
            int64_t id = std::stoll(id_str);
            item_name_to_id_[name] = id;
            item_id_to_name_[id] = name;
        } catch (...) {
            // Skip invalid lines
            continue;
        }
    }

    items_loaded_ = true;
    return true;
}

bool GameData::LoadLocationsCSV(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        return false;
    }

    location_name_to_id_.clear();
    location_id_to_name_.clear();

    std::string line;
    // Skip header line
    std::getline(file, line);

    while (std::getline(file, line)) {
        if (line.empty()) continue;

        std::stringstream ss(line);
        std::string name;
        std::string id_str;

        // Parse CSV: LocationName,LocationID
        std::getline(ss, name, ',');
        std::getline(ss, id_str, ',');

        // Trim whitespace
        name.erase(0, name.find_first_not_of(" \t\r\n"));
        name.erase(name.find_last_not_of(" \t\r\n") + 1);
        id_str.erase(0, id_str.find_first_not_of(" \t\r\n"));
        id_str.erase(id_str.find_last_not_of(" \t\r\n") + 1);

        if (name.empty() || id_str.empty()) continue;

        try {
            int64_t id = std::stoll(id_str);
            location_name_to_id_[name] = id;
            location_id_to_name_[id] = name;
        } catch (...) {
            // Skip invalid lines
            continue;
        }
    }

    locations_loaded_ = true;
    return true;
}

int64_t GameData::GetItemID(const std::string& name) const {
    auto it = item_name_to_id_.find(name);
    return (it != item_name_to_id_.end()) ? it->second : -1;
}

int64_t GameData::GetLocationID(const std::string& name) const {
    auto it = location_name_to_id_.find(name);
    return (it != location_name_to_id_.end()) ? it->second : -1;
}

std::string GameData::GetItemName(int64_t id) const {
    auto it = item_id_to_name_.find(id);
    return (it != item_id_to_name_.end()) ? it->second : "";
}

std::string GameData::GetLocationName(int64_t id) const {
    auto it = location_id_to_name_.find(id);
    return (it != location_id_to_name_.end()) ? it->second : "";
}

std::vector<std::string> GameData::GetAllItemNames() const {
    std::vector<std::string> names;
    names.reserve(item_name_to_id_.size());
    for (const auto& pair : item_name_to_id_) {
        names.push_back(pair.first);
    }
    return names;
}

std::vector<std::string> GameData::GetAllLocationNames() const {
    std::vector<std::string> names;
    names.reserve(location_name_to_id_.size());
    for (const auto& pair : location_name_to_id_) {
        names.push_back(pair.first);
    }
    return names;
}

void GameData::Clear() {
    item_name_to_id_.clear();
    item_id_to_name_.clear();
    location_name_to_id_.clear();
    location_id_to_name_.clear();
    items_loaded_ = false;
    locations_loaded_ = false;
}

bool GameData::IsLoaded() const {
    return items_loaded_ && locations_loaded_;
}

} // namespace FFVIIRebirthAP
