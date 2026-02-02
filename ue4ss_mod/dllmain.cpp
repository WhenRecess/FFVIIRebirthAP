#include <UE4SSProgram.hpp>
#include <Mod/CppUserModBase.hpp>
#include <DynamicOutput/DynamicOutput.hpp>
#include <Unreal/UObject.hpp>
#include <Unreal/UObjectGlobals.hpp>

#include "GameData.hpp"
#include "Client.hpp"

#include <memory>
#include <string>
#include <sstream>

using namespace RC;
using namespace RC::Unreal;

/**
 * @brief FFVIIRebirthAP: Archipelago integration mod for Final Fantasy VII: Rebirth.
 * 
 * This UE4SS mod provides console commands to connect to an Archipelago server
 * and synchronize item/location data with the game.
 */
class FFVIIRebirthAP : public CppUserModBase {
public:
    FFVIIRebirthAP() {
        ModName = STR("FFVIIRebirthAP");
        ModVersion = STR("0.1.0");
        ModDescription = STR("Archipelago integration for Final Fantasy VII: Rebirth");
        ModAuthors = STR("WhenRecess");
        
        game_data_ = std::make_shared<FFVIIRebirthAP::GameData>();
        client_ = std::make_unique<FFVIIRebirthAP::Client>(game_data_);
    }

    ~FFVIIRebirthAP() override = default;

    auto on_update() -> void override {
        // Poll for Archipelago network events every frame
        if (client_ && client_->IsConnected()) {
            client_->Poll();
        }
    }

    auto on_unreal_init() -> void override {
        // Hook BeginPlay for game initialization
        Hook::RegisterBeginPlayPostCallback([this](AGameModeBase* GameMode) {
            OnBeginPlay(GameMode);
        });

        // Hook console command processing
        Hook::RegisterProcessConsoleExecPreCallback([this](UObject* Context, const TCHAR* Cmd, FOutputDevice& Ar, UObject* Executor) -> bool {
            return OnProcessConsoleExec(Context, Cmd, Ar, Executor);
        });

        Output::send(STR("FFVIIRebirthAP mod loaded successfully\n"));
        Output::send(STR("Type '/aphelp' for available commands\n"));
    }

private:
    std::shared_ptr<FFVIIRebirthAP::GameData> game_data_;
    std::unique_ptr<FFVIIRebirthAP::Client> client_;

    /**
     * @brief Called when the game starts (BeginPlay).
     */
    void OnBeginPlay(AGameModeBase* GameMode) {
        Output::send(STR("FFVIIRebirthAP: Game started\n"));
        
        // TODO: Hook game events here
        // Example: Hook item collection, location checks, boss defeats, etc.
        // 
        // RegisterItemCollectedHook([this](int64_t item_id) {
        //     std::string item_name = game_data_->GetItemName(item_id);
        //     Output::send(STR("Item collected: ") + to_wstring(item_name) + STR("\n"));
        //     
        //     // If this is an Archipelago location, send check
        //     int64_t location_id = game_data_->GetLocationID(item_name);
        //     if (location_id != -1) {
        //         client_->SendLocationCheck(location_id);
        //     }
        // });
    }

    /**
     * @brief Process console commands.
     * 
     * @return true if command was handled, false to pass to game
     */
    bool OnProcessConsoleExec(UObject* Context, const TCHAR* Cmd, FOutputDevice& Ar, UObject* Executor) {
        std::wstring cmd_str(Cmd);
        
        // Convert to lowercase for case-insensitive matching
        std::wstring cmd_lower = cmd_str;
        std::transform(cmd_lower.begin(), cmd_lower.end(), cmd_lower.begin(), ::tolower);

        // /aphelp - Show help
        if (cmd_lower.find(L"/aphelp") == 0) {
            ShowHelp();
            return true;
        }

        // /connect <server:port> <slot_name> [password]
        if (cmd_lower.find(L"/connect ") == 0) {
            HandleConnectCommand(cmd_str.substr(9)); // Skip "/connect "
            return true;
        }

        // /disconnect
        if (cmd_lower.find(L"/disconnect") == 0) {
            HandleDisconnectCommand();
            return true;
        }

        // /status
        if (cmd_lower.find(L"/status") == 0) {
            HandleStatusCommand();
            return true;
        }

        // /loaditems <filepath>
        if (cmd_lower.find(L"/loaditems ") == 0) {
            HandleLoadItemsCommand(cmd_str.substr(11)); // Skip "/loaditems "
            return true;
        }

        // /loadlocations <filepath>
        if (cmd_lower.find(L"/loadlocations ") == 0) {
            HandleLoadLocationsCommand(cmd_str.substr(15)); // Skip "/loadlocations "
            return true;
        }

        // Command not handled, pass to game
        return false;
    }

    void ShowHelp() {
        Output::send(STR("=== FFVIIRebirthAP Commands ===\n"));
        Output::send(STR("/aphelp - Show this help\n"));
        Output::send(STR("/connect <server:port> <slot_name> [password] - Connect to Archipelago server\n"));
        Output::send(STR("/disconnect - Disconnect from server\n"));
        Output::send(STR("/status - Show connection status\n"));
        Output::send(STR("/loaditems <filepath> - Load items from CSV\n"));
        Output::send(STR("/loadlocations <filepath> - Load locations from CSV\n"));
        Output::send(STR("Example: /loaditems C:\\Mods\\FFVIIRebirthAP\\items.csv\n"));
        Output::send(STR("Example: /connect archipelago.gg:38281 Player1\n"));
    }

    void HandleConnectCommand(const std::wstring& args) {
        // Parse arguments: <server:port> <slot_name> [password]
        std::wistringstream iss(args);
        std::wstring server, slot, password;
        iss >> server >> slot;
        std::getline(iss, password); // Rest is password (may be empty)
        
        // Trim password
        password.erase(0, password.find_first_not_of(L" \t"));
        password.erase(password.find_last_not_of(L" \t") + 1);

        if (server.empty() || slot.empty()) {
            Output::send(STR("Error: Usage: /connect <server:port> <slot_name> [password]\n"));
            return;
        }

        // Convert wide string to narrow string
        std::string server_str(server.begin(), server.end());
        std::string slot_str(slot.begin(), slot.end());
        std::string password_str(password.begin(), password.end());

        Output::send(STR("Connecting to ") + server + STR(" as ") + slot + STR("...\n"));
        
        if (client_->Connect(server_str, slot_str, password_str)) {
            Output::send(STR("Connected successfully!\n"));
        } else {
            Output::send(STR("Connection failed. Check server address and slot name.\n"));
        }
    }

    void HandleDisconnectCommand() {
        if (!client_->IsConnected()) {
            Output::send(STR("Not connected to any server.\n"));
            return;
        }

        client_->Disconnect();
        Output::send(STR("Disconnected from server.\n"));
    }

    void HandleStatusCommand() {
        std::string status = client_->GetStatusMessage();
        Output::send(STR("Status: ") + std::wstring(status.begin(), status.end()) + STR("\n"));
        
        if (game_data_->IsLoaded()) {
            auto items = game_data_->GetAllItemNames();
            auto locations = game_data_->GetAllLocationNames();
            Output::send(STR("Loaded ") + std::to_wstring(items.size()) + STR(" items, ") +
                        std::to_wstring(locations.size()) + STR(" locations\n"));
        } else {
            Output::send(STR("No game data loaded. Use /loaditems and /loadlocations.\n"));
        }
    }

    void HandleLoadItemsCommand(const std::wstring& filepath) {
        std::string filepath_str(filepath.begin(), filepath.end());
        
        Output::send(STR("Loading items from ") + filepath + STR("...\n"));
        
        if (game_data_->LoadItemsCSV(filepath_str)) {
            auto items = game_data_->GetAllItemNames();
            Output::send(STR("Loaded ") + std::to_wstring(items.size()) + STR(" items successfully.\n"));
        } else {
            Output::send(STR("Failed to load items. Check file path.\n"));
        }
    }

    void HandleLoadLocationsCommand(const std::wstring& filepath) {
        std::string filepath_str(filepath.begin(), filepath.end());
        
        Output::send(STR("Loading locations from ") + filepath + STR("...\n"));
        
        if (game_data_->LoadLocationsCSV(filepath_str)) {
            auto locations = game_data_->GetAllLocationNames();
            Output::send(STR("Loaded ") + std::to_wstring(locations.size()) + STR(" locations successfully.\n"));
        } else {
            Output::send(STR("Failed to load locations. Check file path.\n"));
        }
    }
};

// Register the mod with UE4SS
extern "C" __declspec(dllexport) CppUserModBase* start_mod() {
    return new FFVIIRebirthAP();
}

extern "C" __declspec(dllexport) void uninstall_mod(CppUserModBase* mod) {
    delete mod;
}
