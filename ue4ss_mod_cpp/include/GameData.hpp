#pragma once

#include <string>
#include <functional>
#include <cstdint>

namespace GameData
{
    // Core state checks
    bool IsLoaded();
    std::wstring GetCurrentMap();
    
    // Item system - the main goal
    bool ReceiveItem(int64_t itemId);
    bool GiveItem(const std::wstring& codename);
    bool GiveItemById(int32_t uniqueId, int32_t quantity = 1);
    bool AddGil(int32_t amount);
    
    // Materia system
    bool GiveMateria(const std::wstring& materiaId);
    
    // Weapon system  
    bool GiveWeapon(const std::wstring& weaponId);
    
    // Accessory/Equipment
    bool GiveEquipment(const std::wstring& equipId);
    
    // Debug/Discovery functions
    void EnumeratePlayerFunctions();
    void EnumerateAllAPIFunctions();
    void TestItemGrant();
    
    // Output
    void PrintToConsole(const std::wstring& text);
    void PrintToConsole(const std::wstring& format, ...);
}
