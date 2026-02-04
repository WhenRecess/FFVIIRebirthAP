/**
 * FFVII Rebirth Archipelago - UE4SS C++ Mod Entry Point
 * 
 * This is the main entry point for the UE4SS C++ mod.
 * Based on LiesOfAP's proven pattern for UE4 game item granting.
 * 
 * HOTKEYS:
 *   F1 - Show status
 *   F2 - Run item grant tests  
 *   F3 - Enumerate player functions
 *   F4 - Enumerate API functions
 *   F5 - Test give potion
 *   F6 - Test give item ID 1
 *   F7 - Find all EndDataBaseAPI objects
 *   F8 - Find all player characters
 */

#include <Mod/CppUserModBase.hpp>
#include <Unreal/UObjectGlobals.hpp>
#include <Unreal/UObject.hpp>
#include <Unreal/UFunction.hpp>
#include <Unreal/UClass.hpp>
#include <Unreal/Hooks.hpp>
#include <Unreal/UnrealInitializer.hpp>
#include <DynamicOutput/DynamicOutput.hpp>
#include <Input/Handler.hpp>

#include "GameData.hpp"

#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>

using namespace RC;
using namespace RC::Unreal;

// Log file for output (since no console access)
static std::wofstream g_LogFile;

static void WriteLog(const std::wstring& text)
{
    // Write to UE4SS output
    Output::send<LogLevel::Normal>(text + L"\n");
    
    // Also write to log file
    if (g_LogFile.is_open())
    {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
        std::tm tm_buf;
        localtime_s(&tm_buf, &time);
        
        g_LogFile << L"[" << std::put_time(&tm_buf, L"%H:%M:%S") << L"] " << text << std::endl;
        g_LogFile.flush();
    }
}

/**
 * FFVIIRebirthAPMod - Main mod class
 */
class FFVIIRebirthAPMod : public CppUserModBase
{
public:
    FFVIIRebirthAPMod()
    {
        ModName = STR("FFVIIRebirthAP");
        ModVersion = STR("1.0.0");
        ModDescription = STR("Archipelago multiworld randomizer support for FFVII Rebirth");
        ModAuthors = STR("FFVIIRebirthAP Team");
        
        // Open log file in mod directory
        g_LogFile.open("Mods/FFVIIRebirthAP/ap_log.txt", std::ios::out | std::ios::app);
        
        WriteLog(L"=== FFVIIRebirthAP Mod Loaded ===");
        WriteLog(L"Hotkeys:");
        WriteLog(L"  F1 - Show status");
        WriteLog(L"  F2 - Run item grant tests");
        WriteLog(L"  F3 - Enumerate player functions");
        WriteLog(L"  F4 - Enumerate API functions");
        WriteLog(L"  F5 - Test give potion");
        WriteLog(L"  F6 - Test give item ID 1");
        WriteLog(L"  F7 - Find all API objects");
        WriteLog(L"  F8 - Find all player characters");
    }

    ~FFVIIRebirthAPMod() override
    {
        WriteLog(L"=== FFVIIRebirthAP Mod Unloaded ===");
        if (g_LogFile.is_open())
        {
            g_LogFile.close();
        }
    }

    /**
     * Called when Unreal Engine has finished initializing
     * This is the main initialization point
     */
    auto on_unreal_init() -> void override
    {
        WriteLog(L"on_unreal_init called - Unreal Engine ready");
        
        // Register hotkeys for testing
        RegisterHotkeys();
        
        WriteLog(L"Initialization complete - hotkeys registered");
    }

    /**
     * Called every game tick (use sparingly!)
     */
    auto on_update() -> void override
    {
        // Don't do heavy work here - this is called every frame
    }

    /**
     * Register hotkeys for testing and debugging
     */
    void RegisterHotkeys()
    {
        // F1 - Show status
        register_keydown_event(Input::Key::F1, [this]() {
            WriteLog(L"--- Status Check ---");
            bool loaded = GameData::IsLoaded();
            std::wstring map = GameData::GetCurrentMap();
            WriteLog(L"Game Loaded: " + std::wstring(loaded ? L"Yes" : L"No"));
            WriteLog(L"Current Map: " + map);
            return false; // Don't consume the key
        });

        // F2 - Run item grant tests
        register_keydown_event(Input::Key::F2, [this]() {
            WriteLog(L"--- Running Item Grant Tests ---");
            GameData::TestItemGrant();
            return false;
        });

        // F3 - Enumerate player functions
        register_keydown_event(Input::Key::F3, [this]() {
            WriteLog(L"--- Enumerating Player Functions ---");
            GameData::EnumeratePlayerFunctions();
            return false;
        });

        // F4 - Enumerate API functions
        register_keydown_event(Input::Key::F4, [this]() {
            WriteLog(L"--- Enumerating API Functions ---");
            GameData::EnumerateAllAPIFunctions();
            return false;
        });

        // F5 - Test give potion
        register_keydown_event(Input::Key::F5, [this]() {
            WriteLog(L"--- Testing Give Potion ---");
            GameData::GiveItem(L"IT_Potion");
            GameData::GiveItem(L"Potion");
            return false;
        });

        // F6 - Test give item ID 1
        register_keydown_event(Input::Key::F6, [this]() {
            WriteLog(L"--- Testing Give Item ID 1 ---");
            GameData::GiveItemById(1, 1);
            GameData::GiveItemById(4000001, 1); // Consumable range
            return false;
        });

        // F7 - Find all API objects
        register_keydown_event(Input::Key::F7, [this]() {
            WriteLog(L"--- Finding API Objects ---");
            FindAllOfClass(L"EndDataBaseDataBaseAPI");
            FindAllOfClass(L"EndDataBaseAPI");
            FindAllOfClass(L"EndFieldAPI");
            FindAllOfClass(L"EndMenuAPI");
            return false;
        });

        // F8 - Find all player characters
        register_keydown_event(Input::Key::F8, [this]() {
            WriteLog(L"--- Finding Player Characters ---");
            FindAllOfClass(L"EndPlayerCharacter");
            FindAllOfClass(L"EndCharacter");
            FindAllOfClass(L"PlayerController");
            return false;
        });

        WriteLog(L"Hotkeys registered (F1-F8)");
    }

    void FindAllOfClass(const wchar_t* className)
    {
        std::vector<UObject*> objects;
        UObjectGlobals::FindAllOf(className, objects);
        
        WriteLog(std::wstring(L"FindAllOf(") + className + L"): " + std::to_wstring(objects.size()) + L" found");
        
        for (auto* obj : objects)
        {
            if (obj && obj->IsValid())
            {
                std::wstring name = obj->GetName();
                if (!name.contains(L"Default__"))
                {
                    WriteLog(L"  -> " + name);
                }
            }
        }
    }
};

// ============================================================================
// DLL Entry Points
// ============================================================================

#define FFVIIREBIRTH_AP_API __declspec(dllexport)

extern "C"
{
    FFVIIREBIRTH_AP_API CppUserModBase* start_mod()
    {
        return new FFVIIRebirthAPMod();
    }

    FFVIIREBIRTH_AP_API void uninstall_mod(CppUserModBase* mod)
    {
        delete mod;
    }
}
