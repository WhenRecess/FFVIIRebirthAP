#pragma once

#include <string>
#include <functional>
#include <memory>

// Forward declare apclient types (adjust based on actual apclient API)
// This is a placeholder - implementers will need to include actual apclient headers
namespace apclient {
    class APClient;
    struct NetworkItem;
}

namespace FFVIIRebirthAP {

class GameData;

/**
 * @brief Client wraps the Archipelago C++ client (apclient) library.
 * 
 * Handles connection to the Archipelago server, sending location checks,
 * and receiving items from other players.
 */
class Client {
public:
    /**
     * @brief Construct a new Client object.
     * 
     * @param game_data Shared GameData instance for item/location lookups
     */
    explicit Client(std::shared_ptr<GameData> game_data);
    ~Client();

    /**
     * @brief Connect to an Archipelago server.
     * 
     * @param server_address Server address (e.g., "archipelago.gg:38281")
     * @param slot_name Player's slot name
     * @param password Optional password for the slot
     * @return true if connection succeeded, false otherwise
     */
    bool Connect(const std::string& server_address, 
                 const std::string& slot_name, 
                 const std::string& password = "");

    /**
     * @brief Disconnect from the server.
     */
    void Disconnect();

    /**
     * @brief Check if connected to the server.
     * 
     * @return true if connected, false otherwise
     */
    bool IsConnected() const;

    /**
     * @brief Send a location check to the server.
     * 
     * Call this when the player collects an item or completes a location.
     * 
     * @param location_id Archipelago location ID
     */
    void SendLocationCheck(int64_t location_id);

    /**
     * @brief Register a callback for receiving items.
     * 
     * The callback is invoked when an item is received from the server.
     * 
     * @param callback Function to call with received item info
     */
    void RegisterItemReceivedCallback(std::function<void(int64_t item_id, const std::string& item_name)> callback);

    /**
     * @brief Poll for network events.
     * 
     * Call this regularly (e.g., in a tick function) to process incoming messages.
     */
    void Poll();

    /**
     * @brief Get connection status message.
     * 
     * @return Status string (e.g., "Connected to archipelago.gg:38281 as Player1")
     */
    std::string GetStatusMessage() const;

private:
    std::shared_ptr<GameData> game_data_;
    
    // TODO: Add apclient::APClient instance
    // std::unique_ptr<apclient::APClient> ap_client_;
    
    bool is_connected_ = false;
    std::string server_address_;
    std::string slot_name_;
    
    std::function<void(int64_t, const std::string&)> item_received_callback_;

    // Internal callback handlers for apclient events
    void OnItemReceived(const void* item_data);
    void OnConnected();
    void OnDisconnected();
};

} // namespace FFVIIRebirthAP
