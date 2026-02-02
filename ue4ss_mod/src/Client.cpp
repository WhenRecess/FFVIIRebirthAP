#include "Client.hpp"
#include "GameData.hpp"
#include <cstdio>

// TODO: Include apclient library headers
// #include <apclient.hpp>

namespace Client {

    // TODO: Create global APClient instance
    // static APClient* g_APClient = nullptr;
    static bool g_Connected = false;
    static bool g_DeathLinkEnabled = false;
    static bool g_RingLinkEnabled = false;

    // Callback handlers for AP client events
    static void OnItemsReceived(const std::vector<int64_t>& items) {
        // TODO: Implement item received handler
        // This gets called when the AP server sends items to the player
        for (size_t i = 0; i < items.size(); i++) {
            GameData::ReceiveItem(items[i], "AP Server");
            GameData::PrintToConsole("[AP] Received item code: %lld", items[i]);
        }
    }

    static void OnPrintJson(const std::string& message) {
        // TODO: Implement message handler
        // Parse and display messages from the AP server
        GameData::PrintToConsole("[AP] %s", message.c_str());
    }

    bool Connect(const std::string& serverUrl, const std::string& slotName, const std::string& password) {
        // TODO: Implement connection logic using APClient library
        // Example:
        // if (g_APClient) {
        //     delete g_APClient;
        // }
        // 
        // g_APClient = new APClient("FF7Rebirth", serverUrl);
        // 
        // // Set up handlers
        // g_APClient->set_items_received_handler(OnItemsReceived);
        // g_APClient->set_print_json_handler(OnPrintJson);
        // 
        // // Attempt connection
        // bool success = g_APClient->ConnectSlot(slotName, password);
        // if (success) {
        //     g_Connected = true;
        //     GameData::PrintToConsole("[AP] Connected to %s as %s", 
        //                             serverUrl.c_str(), slotName.c_str());
        // }
        // return success;

        printf("[Client] Connect called: server=%s, slot=%s (TODO: Implement APClient)\n",
               serverUrl.c_str(), slotName.c_str());
        
        // Stub: Simulate connection for testing
        g_Connected = true;
        GameData::PrintToConsole("[AP] STUB: Simulated connection to %s", serverUrl.c_str());
        return true;
    }

    bool Connected() {
        // TODO: Check actual APClient connection state
        // return g_APClient && g_APClient->is_connected();
        return g_Connected;
    }

    void PollServer() {
        if (!Connected()) return;

        // TODO: Poll the APClient for updates
        // g_APClient->poll();
        
        // Check for location clears
        auto newChecks = GameData::CheckEncounterSpots();
        for (auto locationId : newChecks) {
            SendCheck(locationId);
        }

        // Check for death (if DeathLink enabled)
        if (g_DeathLinkEnabled && GameData::CheckDeath()) {
            SendDeath();
        }
    }

    void Disconnect() {
        // TODO: Disconnect from APClient
        // if (g_APClient) {
        //     g_APClient->disconnect();
        //     delete g_APClient;
        //     g_APClient = nullptr;
        // }
        
        g_Connected = false;
        GameData::PrintToConsole("[AP] Disconnected from server");
    }

    void SendCheck(int64_t locationId) {
        if (!Connected()) return;

        // TODO: Send location check to AP server
        // g_APClient->LocationChecks({locationId});
        
        printf("[Client] SendCheck: locationId=%lld (TODO: Implement)\n", locationId);
        GameData::PrintToConsole("[AP] Checked location: %lld", locationId);
    }

    void SendGoal() {
        if (!Connected()) return;

        // TODO: Send goal completion to AP server
        // g_APClient->StatusUpdate(AP_CLIENT_STATUS_GOAL);
        
        printf("[Client] SendGoal called (TODO: Implement)\n");
        GameData::PrintToConsole("[AP] Goal completed!");
    }

    void SendDeath() {
        if (!Connected() || !g_DeathLinkEnabled) return;

        // TODO: Send death notification via Bounce packet
        // Example:
        // json deathData = {
        //     {"time", g_APClient->get_server_time()},
        //     {"source", g_APClient->get_slot()},
        //     {"cause", "Player died in FF7 Rebirth"}
        // };
        // g_APClient->Bounce(deathData, {}, {}, {"DeathLink"});
        
        printf("[Client] SendDeath called (TODO: Implement)\n");
        GameData::PrintToConsole("[AP] Death sent to DeathLink");
    }

    void ToggleDeathLink(bool enabled) {
        g_DeathLinkEnabled = enabled;
        
        // TODO: Subscribe/unsubscribe from DeathLink tag
        // if (g_APClient) {
        //     if (enabled) {
        //         g_APClient->ConnectUpdate({"DeathLink"});
        //     } else {
        //         g_APClient->ConnectUpdate({});
        //     }
        // }
        
        GameData::PrintToConsole("[AP] DeathLink %s", enabled ? "enabled" : "disabled");
    }

    void ToggleRingLink(bool enabled) {
        g_RingLinkEnabled = enabled;
        GameData::PrintToConsole("[AP] RingLink %s (TODO: Implement)", enabled ? "enabled" : "disabled");
    }

} // namespace Client
