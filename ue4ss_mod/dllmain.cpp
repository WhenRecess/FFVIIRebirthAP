#include "Client.hpp"
#include "GameData.hpp"
#include <string>
#include <memory>

// TODO: Include UE4SS mod base headers
// #include <DynamicOutput/DynamicOutput.hpp>
// #include <Mod/CppUserModBase.hpp>

// Placeholder for UE4SS mod base class
// Once UE4SS SDK is integrated, this should inherit from RC::CppUserModBase
class FFVIIRebirthAP {
private:
    bool m_IsInitialized = false;
    int m_UpdateCounter = 0;

public:
    FFVIIRebirthAP() {
        GameData::PrintToConsole("[FFVIIRebirthAP] Mod instance created");
    }

    ~FFVIIRebirthAP() {
        if (Client::Connected()) {
            Client::Disconnect();
        }
        GameData::PrintToConsole("[FFVIIRebirthAP] Mod instance destroyed");
    }

    void on_update() {
        // Called every frame or on a timer
        m_UpdateCounter++;

        // Poll AP server periodically (every ~60 frames if at 60 FPS = ~1 second)
        if (m_UpdateCounter % 60 == 0 && Client::Connected()) {
            Client::PollServer();
        }

        // Check for encounter spots if game is loaded
        if (GameData::IsLoaded()) {
            auto checks = GameData::CheckEncounterSpots();
            for (auto locationId : checks) {
                Client::SendCheck(locationId);
            }
        }
    }

    void on_unreal_init() {
        // Called when Unreal Engine is initialized
        m_IsInitialized = true;
        GameData::PrintToConsole("[FFVIIRebirthAP] Unreal Engine initialized, mod ready");
    }

    void register_console_commands() {
        // TODO: Register console commands with UE4SS
        // Example registration would look like:
        // register_console_command("connect", &FFVIIRebirthAP::cmd_connect);
        // register_console_command("deathlink", &FFVIIRebirthAP::cmd_deathlink);
        // register_console_command("ap-replace", &FFVIIRebirthAP::cmd_replace_enemy);
        
        GameData::PrintToConsole("[FFVIIRebirthAP] Console commands registered (TODO: UE4SS integration)");
        GameData::PrintToConsole("  /connect <server> <slot> [password] - Connect to AP server");
        GameData::PrintToConsole("  /deathlink [on|off] - Toggle DeathLink");
        GameData::PrintToConsole("  /ap-replace <territory> <slot> <template> - Replace enemy template");
    }

    // Console command handlers
    bool cmd_connect(const std::vector<std::string>& args) {
        if (args.size() < 2) {
            GameData::PrintToConsole("[AP] Usage: /connect <server> <slot> [password]");
            return false;
        }

        std::string server = args[0];
        std::string slot = args[1];
        std::string password = args.size() > 2 ? args[2] : "";

        bool success = Client::Connect(server, slot, password);
        if (success) {
            GameData::PrintToConsole("[AP] Connection initiated to %s as %s", 
                                    server.c_str(), slot.c_str());
        } else {
            GameData::PrintToConsole("[AP] Failed to connect to %s", server.c_str());
        }
        return success;
    }

    bool cmd_deathlink(const std::vector<std::string>& args) {
        bool enable = true;
        if (!args.empty()) {
            std::string arg = args[0];
            if (arg == "off" || arg == "0" || arg == "false") {
                enable = false;
            }
        }

        Client::ToggleDeathLink(enable);
        return true;
    }

    bool cmd_replace_enemy(const std::vector<std::string>& args) {
        if (args.size() < 3) {
            GameData::PrintToConsole("[AP] Usage: /ap-replace <territory> <slot> <template>");
            return false;
        }

        try {
            int32_t territory = std::stoi(args[0]);
            int32_t slot = std::stoi(args[1]);
            int32_t templateId = std::stoi(args[2]);

            bool success = GameData::ReplaceEnemyTemplate(territory, slot, templateId);
            if (success) {
                GameData::PrintToConsole("[AP] Replaced enemy in territory %d slot %d with template %d",
                                        territory, slot, templateId);
            } else {
                GameData::PrintToConsole("[AP] Failed to replace enemy template");
            }
            return success;
        } catch (...) {
            GameData::PrintToConsole("[AP] Invalid arguments for /ap-replace");
            return false;
        }
    }
};

// Global mod instance
static std::unique_ptr<FFVIIRebirthAP> g_ModInstance;

// DLL entry point
#ifdef _WIN32
#include <windows.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // DLL is being loaded
            break;
        case DLL_PROCESS_DETACH:
            // DLL is being unloaded
            if (g_ModInstance) {
                g_ModInstance.reset();
            }
            break;
    }
    return TRUE;
}
#endif

// UE4SS mod interface functions
// These are the entry points that UE4SS will call

extern "C" {
    // Called when the mod is loaded by UE4SS
    __declspec(dllexport) void start_mod() {
        if (!g_ModInstance) {
            g_ModInstance = std::make_unique<FFVIIRebirthAP>();
            g_ModInstance->on_unreal_init();
            g_ModInstance->register_console_commands();
        }
    }

    // Called when the mod is unloaded by UE4SS
    __declspec(dllexport) void uninstall_mod() {
        if (g_ModInstance) {
            g_ModInstance.reset();
        }
    }

    // Called every frame by UE4SS (if registered)
    __declspec(dllexport) void on_update() {
        if (g_ModInstance) {
            g_ModInstance->on_update();
        }
    }
}

// TODO: Integrate with UE4SS CppUserModBase
// When UE4SS SDK is available, refactor to properly inherit from CppUserModBase
// and use its callback system (on_unreal_init, register_hook, etc.)
//
// Example integration:
// class FFVIIRebirthAP : public RC::CppUserModBase {
// public:
//     FFVIIRebirthAP() : CppUserModBase() {
//         ModName = STR("FFVIIRebirthAP");
//         ModVersion = STR("0.1.0");
//     }
//
//     void on_unreal_init() override {
//         // Hook game functions, register callbacks
//     }
//
//     void on_update() override {
//         // Per-frame logic
//     }
// };
