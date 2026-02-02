#pragma once

#include <string>
#include <vector>
#include <functional>
#include <cstdint>

/**
 * Client namespace provides wrapper functions for Archipelago client functionality
 * This is a minimal interface to the apclient library
 * All functions are stubs and require linking against apclient
 */
namespace Client {

    /**
     * Connection parameters
     */
    struct ConnectionInfo {
        std::string serverUrl;      // e.g., "archipelago.gg:38281"
        std::string slotName;       // Player's slot name
        std::string password;       // Optional room password
        int game;                   // Game ID (should be "Final Fantasy VII: Rebirth")
        std::string uuid;           // Client UUID for identification
    };

    /**
     * Connect to an Archipelago server
     * @param info Connection parameters
     * @return true if connection initiated successfully
     */
    bool Connect(const ConnectionInfo& info);

    /**
     * Check if currently connected to AP server
     * @return true if connected
     */
    bool Connected();

    /**
     * Poll the server for updates
     * Should be called regularly (e.g., every frame or every 100ms)
     * Processes incoming messages and triggers callbacks
     */
    void PollServer();

    /**
     * Disconnect from the AP server
     */
    void Disconnect();

    /**
     * Send a location check to the server
     * Called when player completes a location
     * @param locationId AP location ID that was checked
     */
    void SendCheck(uint64_t locationId);

    /**
     * Send multiple location checks
     * @param locationIds Vector of location IDs to check
     */
    void SendChecks(const std::vector<uint64_t>& locationIds);

    /**
     * Send goal completion
     * Called when player completes the game/goal
     */
    void SendGoal();

    /**
     * Send death notification (for DeathLink)
     * @param deathText Optional message describing the death
     */
    void SendDeath(const std::string& deathText = "");

    /**
     * Toggle DeathLink on/off
     * @param enabled true to enable DeathLink
     */
    void ToggleDeathLink(bool enabled);

    /**
     * Toggle RingLink on/off (if applicable)
     * @param enabled true to enable RingLink
     */
    void ToggleRingLink(bool enabled);

    /**
     * Get current slot data
     * @return JSON string of slot data (game-specific settings)
     */
    std::string GetSlotData();

    /**
     * Get items received from server
     * @return Vector of item codes received
     */
    std::vector<uint64_t> GetReceivedItems();

    /**
     * Get current hint points
     * @return Number of hint points available
     */
    int GetHintPoints();

    /**
     * Callbacks for AP events
     */
    using ItemReceivedCallback = std::function<void(uint64_t itemCode, const std::string& itemName, const std::string& playerName)>;
    using PrintMessageCallback = std::function<void(const std::string& message)>;
    using DeathLinkCallback = std::function<void(const std::string& source)>;

    /**
     * Set callback for when items are received
     * @param callback Function to call when items are received
     */
    void SetItemReceivedCallback(ItemReceivedCallback callback);

    /**
     * Set callback for server messages
     * @param callback Function to call for server messages
     */
    void SetPrintMessageCallback(PrintMessageCallback callback);

    /**
     * Set callback for DeathLink events
     * @param callback Function to call when another player dies
     */
    void SetDeathLinkCallback(DeathLinkCallback callback);

    /**
     * Initialize the client system
     * Should be called once at mod startup
     */
    void Initialize();

    /**
     * Shutdown the client system
     * Should be called at mod unload
     */
    void Shutdown();

} // namespace Client
