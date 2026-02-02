#include <Windows.h>
#include <string>
#include <thread>
#include <chrono>

#include "GameData.hpp"
#include "Client.hpp"

// TODO: Include UE4SS SDK headers when available
// #include <DynamicOutput/DynamicOutput.hpp>
// #include <Mod/CppUserModBase.hpp>

// For now, create minimal placeholder structures to allow compilation
namespace RC::Unreal {
    class UObject {};
    class FOutputDevice {};
}

namespace RC {
    // Minimal CppUserModBase interface placeholder
    class CppUserModBase {
    public:
        virtual ~CppUserModBase() = default;
        virtual void on_update() {}
        virtual void on_unreal_init() {}
    };
}

/**
 * FFVIIRebirthAP Mod Class
 * Implements the UE4SS mod interface for Archipelago integration
 */
class FFVIIRebirthAP : public RC::CppUserModBase {
private:
    bool m_initialized = false;
    bool m_updateRegistered = false;
    std::chrono::steady_clock::time_point m_lastPollTime;
    const std::chrono::milliseconds m_pollInterval{100}; // Poll AP server every 100ms

public:
    FFVIIRebirthAP() {
        GameData::PrintToConsole("FFVIIRebirthAP mod constructed");
    }

    ~FFVIIRebirthAP() override {
        if (m_initialized) {
            Shutdown();
        }
    }

    /**
     * Called when UE4 is initialized and ready
     */
    void on_unreal_init() override {
        GameData::PrintToConsole("=== FFVII Rebirth Archipelago Mod ===");
        GameData::PrintToConsole("Version: 0.1.0 (Scaffold)");
        GameData::PrintToConsole("Initializing...");
        
        // Initialize subsystems
        Client::Initialize();
        
        // Set up callbacks
        Client::SetItemReceivedCallback([](uint64_t itemCode, const std::string& itemName, const std::string& playerName) {
            GameData::PrintToConsole("Received %s (%llu) from %s", itemName.c_str(), itemCode, playerName.c_str());
            GameData::ReceiveItem(itemCode, itemName, playerName);
        });
        
        Client::SetPrintMessageCallback([](const std::string& message) {
            GameData::PrintToConsole("AP: %s", message.c_str());
        });
        
        Client::SetDeathLinkCallback([](const std::string& source) {
            GameData::PrintToConsole("DeathLink received from %s!", source.c_str());
            // TODO: Implement player death when DeathLink received
        });
        
        m_initialized = true;
        m_lastPollTime = std::chrono::steady_clock::now();
        
        GameData::PrintToConsole("Mod initialized successfully!");
        GameData::PrintToConsole("Use /connect <server> <slot> [password] to connect");
    }

    /**
     * Called every frame/tick
     */
    void on_update() override {
        if (!m_initialized) {
            return;
        }
        
        auto now = std::chrono::steady_clock::now();
        if (now - m_lastPollTime >= m_pollInterval) {
            m_lastPollTime = now;
            
            // Poll AP server for updates
            if (Client::Connected()) {
                Client::PollServer();
                
                // Check for new location completions
                auto newChecks = GameData::CheckEncounterSpots();
                if (!newChecks.empty()) {
                    Client::SendChecks(newChecks);
                }
                
                // Check for death (if DeathLink enabled)
                if (GameData::CheckDeath()) {
                    Client::SendDeath("Died in combat");
                }
            }
        }
    }

    /**
     * Handle console commands
     * @param Command The command string entered
     * @return true if command was handled
     */
    bool on_console_command(const std::wstring& Command) {
        std::string cmd = WideToString(Command);
        
        // Parse command
        if (cmd.find("/connect") == 0) {
            return HandleConnectCommand(cmd);
        }
        else if (cmd.find("/disconnect") == 0) {
            Client::Disconnect();
            GameData::PrintToConsole("Disconnected from AP server");
            return true;
        }
        else if (cmd.find("/deathlink") == 0) {
            // Toggle DeathLink
            static bool deathLinkEnabled = false;
            deathLinkEnabled = !deathLinkEnabled;
            Client::ToggleDeathLink(deathLinkEnabled);
            return true;
        }
        else if (cmd.find("/ap-replace") == 0) {
            // Example command: /ap-replace 10 5 42
            // Replace territory 10, slot 5 with enemy 42
            uint32_t territory, slot, enemy;
            if (sscanf(cmd.c_str(), "/ap-replace %u %u %u", &territory, &slot, &enemy) == 3) {
                GameData::ReplaceEnemyTemplate(territory, slot, enemy);
                return true;
            }
            else {
                GameData::PrintToConsole("Usage: /ap-replace <territory> <slot> <enemy>");
                return true;
            }
        }
        else if (cmd.find("/ap-status") == 0) {
            // Print status information
            if (Client::Connected()) {
                GameData::PrintToConsole("Status: Connected to AP server");
                // TODO: Print more status info
            }
            else {
                GameData::PrintToConsole("Status: Not connected");
            }
            return true;
        }
        
        return false; // Command not handled
    }

private:
    /**
     * Handle /connect command
     * Format: /connect <server:port> <slot> [password]
     */
    bool HandleConnectCommand(const std::string& cmd) {
        // Parse command arguments
        char server[256] = {0};
        char slot[256] = {0};
        char password[256] = {0};
        
        int parsed = sscanf(cmd.c_str(), "/connect %255s %255s %255s", server, slot, password);
        
        if (parsed < 2) {
            GameData::PrintToConsole("Usage: /connect <server:port> <slot> [password]");
            GameData::PrintToConsole("Example: /connect archipelago.gg:38281 Player1");
            return true;
        }
        
        // Create connection info
        Client::ConnectionInfo info;
        info.serverUrl = server;
        info.slotName = slot;
        info.password = (parsed >= 3) ? password : "";
        info.game = 0; // TODO: Set proper game ID
        info.uuid = "FFVII-Rebirth-Client"; // TODO: Generate or load persistent UUID
        
        // Attempt connection
        if (Client::Connect(info)) {
            GameData::PrintToConsole("Connected successfully!");
        }
        else {
            GameData::PrintToConsole("Connection failed!");
        }
        
        return true;
    }

    void Shutdown() {
        GameData::PrintToConsole("Shutting down FFVIIRebirthAP mod...");
        Client::Shutdown();
        m_initialized = false;
    }

    /**
     * Helper to convert wide string to regular string
     */
    static std::string WideToString(const std::wstring& wide) {
        if (wide.empty()) return "";
        int size = WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), -1, nullptr, 0, nullptr, nullptr);
        std::string result(size - 1, 0);
        WideCharToMultiByte(CP_UTF8, 0, wide.c_str(), -1, &result[0], size, nullptr, nullptr);
        return result;
    }
};

// Global mod instance
static FFVIIRebirthAP* g_ModInstance = nullptr;

/**
 * DLL entry point
 */
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // Disable thread library calls for performance
            DisableThreadLibraryCalls(hModule);
            break;
        case DLL_PROCESS_DETACH:
            break;
    }
    return TRUE;
}

/**
 * UE4SS mod entry point
 * Called by UE4SS to start the mod
 */
extern "C" __declspec(dllexport) RC::CppUserModBase* start_mod() {
    if (!g_ModInstance) {
        g_ModInstance = new FFVIIRebirthAP();
    }
    return g_ModInstance;
}

/**
 * UE4SS mod uninstall
 * Called by UE4SS to unload the mod
 */
extern "C" __declspec(dllexport) void uninstall_mod() {
    if (g_ModInstance) {
        delete g_ModInstance;
        g_ModInstance = nullptr;
    }
}
