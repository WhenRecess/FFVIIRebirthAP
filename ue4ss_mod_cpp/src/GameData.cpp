/**
 * FFVII Rebirth Archipelago - GameData Implementation
 * 
 * Core game interaction layer using UE4SS C++ API
 * Based on LiesOfAP's approach of finding and calling game functions via ProcessEvent
 */

#include "GameData.hpp"

#include <Mod/CppUserModBase.hpp>
#include <Unreal/UObjectGlobals.hpp>
#include <Unreal/UObject.hpp>
#include <Unreal/UFunction.hpp>
#include <Unreal/UClass.hpp>
#include <Unreal/FName.hpp>
#include <Unreal/FString.hpp>
#include <Unreal/World.hpp>
#include <DynamicOutput/DynamicOutput.hpp>

#include <vector>
#include <string>
#include <map>

using namespace RC;
using namespace RC::Unreal;

namespace GameData
{
    // =========================================================================
    // Helper: Print to UE4SS console
    // =========================================================================
    void PrintToConsole(const std::wstring& text)
    {
        Output::send<LogLevel::Default>(text);
    }

    // =========================================================================
    // Helper: Find the EndDataBaseDataBaseAPI singleton
    // =========================================================================
    static UObject* GetDatabaseAPI()
    {
        static UObject* cachedAPI = nullptr;
        if (cachedAPI && cachedAPI->IsValid())
        {
            return cachedAPI;
        }

        // Try to find the API object
        std::vector<UObject*> apis;
        UObjectGlobals::FindAllOf(STR("EndDataBaseDataBaseAPI"), apis);
        
        if (!apis.empty())
        {
            cachedAPI = apis[0];
            return cachedAPI;
        }

        // Try alternate class name
        UObjectGlobals::FindAllOf(STR("EndDataBaseAPI"), apis);
        if (!apis.empty())
        {
            cachedAPI = apis[0];
            return cachedAPI;
        }

        return nullptr;
    }

    // =========================================================================
    // Helper: Find any player character
    // =========================================================================
    static UObject* GetPlayerCharacter()
    {
        // Try common FF7R player class names
        static const wchar_t* playerClassNames[] = {
            L"EndPlayerCharacter",
            L"BP_EndPlayerCharacter_C",
            L"EndCharacter",
            L"BP_Cloud_C",
            L"BP_PlayerCharacter_C"
        };

        for (const auto* className : playerClassNames)
        {
            std::vector<UObject*> players;
            UObjectGlobals::FindAllOf(className, players);
            
            for (auto* player : players)
            {
                if (player && player->IsValid())
                {
                    // Filter out CDO (Class Default Object)
                    if (!player->GetName().contains(STR("Default__")))
                    {
                        return player;
                    }
                }
            }
        }

        return nullptr;
    }

    // =========================================================================
    // Helper: Find the player controller
    // =========================================================================
    static UObject* GetPlayerController()
    {
        std::vector<UObject*> controllers;
        UObjectGlobals::FindAllOf(STR("EndPlayerController"), controllers);
        
        for (auto* controller : controllers)
        {
            if (controller && controller->IsValid())
            {
                if (!controller->GetName().contains(STR("Default__")))
                {
                    return controller;
                }
            }
        }
        return nullptr;
    }

    // =========================================================================
    // Helper: Find game instance/game mode
    // =========================================================================
    static UObject* GetGameInstance()
    {
        std::vector<UObject*> instances;
        
        // Try to find game instance
        UObjectGlobals::FindAllOf(STR("EndGameInstance"), instances);
        if (!instances.empty())
        {
            for (auto* inst : instances)
            {
                if (inst && inst->IsValid() && !inst->GetName().contains(STR("Default__")))
                {
                    return inst;
                }
            }
        }

        // Try game mode
        UObjectGlobals::FindAllOf(STR("EndGameMode"), instances);
        for (auto* inst : instances)
        {
            if (inst && inst->IsValid() && !inst->GetName().contains(STR("Default__")))
            {
                return inst;
            }
        }

        return nullptr;
    }

    // =========================================================================
    // IsLoaded: Check if game is ready
    // =========================================================================
    bool IsLoaded()
    {
        UObject* dbApi = GetDatabaseAPI();
        return (dbApi != nullptr);
    }

    // =========================================================================
    // GetCurrentMap: Get the current map/level name
    // =========================================================================
    std::wstring GetCurrentMap()
    {
        // Try to get world
        UWorld* world = UWorld::GetWorld();
        if (world)
        {
            return world->GetName();
        }
        return L"Unknown";
    }

    // =========================================================================
    // GiveItemById: Try to give item using database API
    // =========================================================================
    bool GiveItemById(int32_t uniqueId, int32_t quantity)
    {
        UObject* dbApi = GetDatabaseAPI();
        if (!dbApi)
        {
            PrintToConsole(L"[GameData] Database API not found!");
            return false;
        }

        // Try to find a function that adds items
        // Search through the class hierarchy for any "Add" or "Give" or "Set" item functions
        UClass* apiClass = dbApi->GetClassPrivate();
        if (!apiClass)
        {
            PrintToConsole(L"[GameData] Could not get API class!");
            return false;
        }

        // List all functions to find candidates
        PrintToConsole(L"[GameData] Searching for item-granting functions on API class...");
        
        for (UFunction* func : apiClass->ForEachFunctionInChain())
        {
            FName funcName = func->GetNamePrivate();
            std::wstring nameStr = funcName.ToString();
            
            // Look for functions with Item, Add, Give, Set in the name
            if (nameStr.find(L"Item") != std::wstring::npos ||
                nameStr.find(L"Add") != std::wstring::npos ||
                nameStr.find(L"Give") != std::wstring::npos)
            {
                PrintToConsole(L"[GameData] Found candidate function: " + nameStr);
            }
        }

        // For now, try SetResidentWorkInteger with different work IDs
        // Items might be stored as work variables with specific IDs
        UFunction* setWorkFunc = dbApi->GetFunctionByNameInChain(L"SetResidentWorkInteger");
        if (setWorkFunc)
        {
            // Try setting item count directly via work variable
            // Format: ITEM_{uniqueId}_COUNT or similar
            struct SetWorkParams
            {
                FName workId;
                int32 value;
            };

            // Try different naming conventions
            std::wstring workIdStr = L"ITEM_" + std::to_wstring(uniqueId);
            SetWorkParams params{ FName(workIdStr.c_str()), quantity };
            
            dbApi->ProcessEvent(setWorkFunc, &params);
            PrintToConsole(L"[GameData] Tried SetResidentWorkInteger with " + workIdStr);
            
            return true; // We tried, can't verify if it worked
        }

        return false;
    }

    // =========================================================================
    // GiveItem: Give item by codename
    // =========================================================================
    bool GiveItem(const std::wstring& codename)
    {
        PrintToConsole(L"[GameData] GiveItem: " + codename);

        // First, try to find a player with an OnGainItem-like function (like LiesOfP)
        UObject* player = GetPlayerCharacter();
        if (player)
        {
            // Search for item-receiving functions on player
            UClass* playerClass = player->GetClassPrivate();
            if (playerClass)
            {
                // Try common function names
                static const wchar_t* funcNames[] = {
                    L"OnGainItem",
                    L"GainItem", 
                    L"AddItem",
                    L"ReceiveItem",
                    L"OnReceiveItem",
                    L"GiveItem",
                    L"AddToInventory",
                    L"OnObtainItem"
                };

                for (const auto* funcName : funcNames)
                {
                    UFunction* func = player->GetFunctionByNameInChain(funcName);
                    if (func)
                    {
                        PrintToConsole(std::wstring(L"[GameData] Found function: ") + funcName);
                        
                        // Try calling it with codename
                        struct GainItemParams
                        {
                            FName itemCodename;
                            int32 quantity;
                        } params{ FName(codename.c_str()), 1 };

                        player->ProcessEvent(func, &params);
                        PrintToConsole(L"[GameData] Called " + std::wstring(funcName) + L" with " + codename);
                        return true;
                    }
                }
            }
        }

        // Fallback: try database API approach
        return GiveItemById(0, 1); // Placeholder
    }

    // =========================================================================
    // AddGil: Add currency
    // =========================================================================
    bool AddGil(int32_t amount)
    {
        UObject* dbApi = GetDatabaseAPI();
        if (!dbApi)
        {
            return false;
        }

        UFunction* setWorkFunc = dbApi->GetFunctionByNameInChain(L"SetResidentWorkInteger");
        if (setWorkFunc)
        {
            // Try common gil work variable names
            static const wchar_t* gilNames[] = {
                L"GIL",
                L"MONEY",
                L"Gil",
                L"Money",
                L"PLAYER_GIL",
                L"PlayerGil",
                L"CurrentGil"
            };

            struct SetWorkParams
            {
                FName workId;
                int32 value;
            };

            for (const auto* gilName : gilNames)
            {
                // First try to get current value
                UFunction* getWorkFunc = dbApi->GetFunctionByNameInChain(L"GetResidentWorkInteger");
                if (getWorkFunc)
                {
                    struct GetWorkParams
                    {
                        FName workId;
                    } getParams{ FName(gilName) };

                    int32 currentGil = 0;
                    // Note: Return value handling may need adjustment
                    dbApi->ProcessEvent(getWorkFunc, &getParams);
                    
                    // Set new value (current + amount)
                    SetWorkParams setParams{ FName(gilName), currentGil + amount };
                    dbApi->ProcessEvent(setWorkFunc, &setParams);
                    
                    PrintToConsole(std::wstring(L"[GameData] Tried adding gil via ") + gilName);
                }
            }
        }

        return false;
    }

    // =========================================================================
    // GiveMateria: Give materia by ID
    // =========================================================================
    bool GiveMateria(const std::wstring& materiaId)
    {
        PrintToConsole(L"[GameData] GiveMateria: " + materiaId + L" (not implemented)");
        // Similar to GiveItem, find materia-specific functions
        return false;
    }

    // =========================================================================
    // GiveWeapon: Give weapon by ID
    // =========================================================================
    bool GiveWeapon(const std::wstring& weaponId)
    {
        PrintToConsole(L"[GameData] GiveWeapon: " + weaponId + L" (not implemented)");
        
        // Look for weapon grant function on player
        UObject* player = GetPlayerCharacter();
        if (player)
        {
            UFunction* func = player->GetFunctionByNameInChain(L"OnGainWeapon");
            if (!func) func = player->GetFunctionByNameInChain(L"AddWeapon");
            if (!func) func = player->GetFunctionByNameInChain(L"GiveWeapon");
            
            if (func)
            {
                struct WeaponParams
                {
                    FName weaponCodename;
                } params{ FName(weaponId.c_str()) };

                player->ProcessEvent(func, &params);
                PrintToConsole(L"[GameData] Called weapon function with " + weaponId);
                return true;
            }
        }

        return false;
    }

    // =========================================================================
    // GiveEquipment: Give accessory/equipment by ID
    // =========================================================================
    bool GiveEquipment(const std::wstring& equipId)
    {
        PrintToConsole(L"[GameData] GiveEquipment: " + equipId + L" (not implemented)");
        return false;
    }

    // =========================================================================
    // ReceiveItem: Main entry point for AP item receives
    // =========================================================================
    bool ReceiveItem(int64_t itemId)
    {
        PrintToConsole(L"[GameData] ReceiveItem: " + std::to_wstring(itemId));

        // Map itemId to game item type and grant
        // For now, try generic approach
        return GiveItemById(static_cast<int32_t>(itemId), 1);
    }

    // =========================================================================
    // Debug: Enumerate all functions on player object
    // =========================================================================
    void EnumeratePlayerFunctions()
    {
        PrintToConsole(L"=== Enumerating Player Functions ===");
        
        UObject* player = GetPlayerCharacter();
        if (!player)
        {
            PrintToConsole(L"[Debug] No player character found!");
            return;
        }

        PrintToConsole(L"[Debug] Player: " + player->GetName());
        
        UClass* playerClass = player->GetClassPrivate();
        if (!playerClass)
        {
            PrintToConsole(L"[Debug] Could not get player class!");
            return;
        }

        PrintToConsole(L"[Debug] Class: " + playerClass->GetName());

        int funcCount = 0;
        for (UFunction* func : playerClass->ForEachFunctionInChain())
        {
            FName funcName = func->GetNamePrivate();
            std::wstring nameStr = funcName.ToString();
            
            // Filter to interesting functions
            if (nameStr.find(L"Item") != std::wstring::npos ||
                nameStr.find(L"Gain") != std::wstring::npos ||
                nameStr.find(L"Give") != std::wstring::npos ||
                nameStr.find(L"Add") != std::wstring::npos ||
                nameStr.find(L"Receive") != std::wstring::npos ||
                nameStr.find(L"Equip") != std::wstring::npos ||
                nameStr.find(L"Weapon") != std::wstring::npos ||
                nameStr.find(L"Materia") != std::wstring::npos ||
                nameStr.find(L"Gil") != std::wstring::npos ||
                nameStr.find(L"Money") != std::wstring::npos)
            {
                PrintToConsole(L"  [INTERESTING] " + nameStr);
            }
            funcCount++;
        }
        
        PrintToConsole(L"[Debug] Total functions: " + std::to_wstring(funcCount));
    }

    // =========================================================================
    // Debug: Enumerate all API object functions
    // =========================================================================
    void EnumerateAllAPIFunctions()
    {
        PrintToConsole(L"=== Enumerating API Functions ===");

        // List of API class names to search
        static const wchar_t* apiClassNames[] = {
            L"EndDataBaseDataBaseAPI",
            L"EndDataBaseAPI",
            L"EndFieldAPI",
            L"EndMenuAPI",
            L"EndMenuBPAPI",
            L"EndBattleAPI",
            L"EndPartyAPI",
            L"EndCommonAPI",
            L"EndDebugAPI"
        };

        for (const auto* apiClassName : apiClassNames)
        {
            std::vector<UObject*> apis;
            UObjectGlobals::FindAllOf(apiClassName, apis);
            
            for (auto* api : apis)
            {
                if (!api || !api->IsValid()) continue;
                if (api->GetName().contains(STR("Default__"))) continue;

                PrintToConsole(std::wstring(L"\n--- ") + apiClassName + L" ---");
                PrintToConsole(L"Object: " + api->GetName());

                UClass* apiClass = api->GetClassPrivate();
                if (!apiClass) continue;

                for (UFunction* func : apiClass->ForEachFunctionInChain())
                {
                    FName funcName = func->GetNamePrivate();
                    std::wstring nameStr = funcName.ToString();
                    
                    // Filter to potentially useful functions
                    if (nameStr.find(L"Item") != std::wstring::npos ||
                        nameStr.find(L"Give") != std::wstring::npos ||
                        nameStr.find(L"Add") != std::wstring::npos ||
                        nameStr.find(L"Set") != std::wstring::npos ||
                        nameStr.find(L"Grant") != std::wstring::npos ||
                        nameStr.find(L"Receive") != std::wstring::npos ||
                        nameStr.find(L"Reward") != std::wstring::npos)
                    {
                        PrintToConsole(L"  " + nameStr);
                    }
                }
            }
        }
    }

    // =========================================================================
    // Debug: Test various item grant approaches
    // =========================================================================
    void TestItemGrant()
    {
        PrintToConsole(L"=== Testing Item Grant ===");

        // Test 1: Try to find and call any item-adding function
        EnumeratePlayerFunctions();
        EnumerateAllAPIFunctions();

        // Test 2: Try giving a potion (common test item)
        PrintToConsole(L"\n--- Attempting to give Potion ---");
        GiveItem(L"IT_Potion");
        GiveItem(L"Potion");
        GiveItem(L"ITEM_POTION");
        
        // Test 3: Try numeric IDs
        PrintToConsole(L"\n--- Attempting numeric item IDs ---");
        GiveItemById(1, 1);
        GiveItemById(100, 1);
        GiveItemById(4000001, 1);

        PrintToConsole(L"=== Test Complete ===");
    }

} // namespace GameData
