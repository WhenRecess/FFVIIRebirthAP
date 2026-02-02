#pragma once

#include <string>
#include <cstdint>

/**
 * Client namespace
 * 
 * Provides an interface to the Archipelago client library.
 * This is a wrapper around the APClient C++ library.
 * 
 * TODO: Link against apclient library and implement these methods.
 * Required apclient library functions:
 * - APClient constructor/destructor
 * - APClient::set_items_received_handler()
 * - APClient::set_print_json_handler()
 * - APClient::ConnectSlot()
 * - APClient::LocationChecks()
 * - APClient::Bounce()
 * - APClient::StatusUpdate()
 * - APClient::get_server_time()
 * - APClient::get_slot()
 */
namespace Client {

    /**
     * Connect to an Archipelago server
     * @param serverUrl Server URL (e.g., "archipelago.gg:38281")
     * @param slotName Player slot name
     * @param password Optional server password
     * @return true if connection initiated successfully
     */
    bool Connect(const std::string& serverUrl, const std::string& slotName, const std::string& password = "");

    /**
     * Check if currently connected to a server
     * @return true if connected
     */
    bool Connected();

    /**
     * Poll the server for updates (items, messages, etc.)
     * Should be called regularly (e.g., every frame or on a timer)
     */
    void PollServer();

    /**
     * Disconnect from the current server
     */
    void Disconnect();

    /**
     * Send a location check to the server
     * @param locationId The location ID that was checked
     */
    void SendCheck(int64_t locationId);

    /**
     * Send a goal completion to the server
     */
    void SendGoal();

    /**
     * Send a death notification (for DeathLink)
     */
    void SendDeath();

    /**
     * Toggle DeathLink on/off
     * @param enabled true to enable DeathLink, false to disable
     */
    void ToggleDeathLink(bool enabled);

    /**
     * Toggle RingLink on/off (custom feature for item sharing)
     * @param enabled true to enable RingLink, false to disable
     */
    void ToggleRingLink(bool enabled);

} // namespace Client
