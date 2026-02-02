#include "Client.hpp"
#include "GameData.hpp"

// TODO: Include actual apclient headers
// #include <apclient.hpp>

namespace FFVIIRebirthAP {

Client::Client(std::shared_ptr<GameData> game_data)
    : game_data_(game_data) {
    // TODO: Initialize apclient instance
    // ap_client_ = std::make_unique<apclient::APClient>("Final Fantasy VII: Rebirth");
}

Client::~Client() {
    Disconnect();
}

bool Client::Connect(const std::string& server_address,
                     const std::string& slot_name,
                     const std::string& password) {
    if (is_connected_) {
        return true;
    }

    server_address_ = server_address;
    slot_name_ = slot_name;

    // TODO: Implement actual connection using apclient
    // Example pseudocode:
    // 
    // ap_client_->set_socket_connected_handler([this]() { OnConnected(); });
    // ap_client_->set_socket_disconnected_handler([this]() { OnDisconnected(); });
    // ap_client_->set_items_received_handler([this](const std::list<NetworkItem>& items) {
    //     for (const auto& item : items) {
    //         OnItemReceived(&item);
    //     }
    // });
    // 
    // bool success = ap_client_->connect(server_address, slot_name, password);
    // if (success) {
    //     is_connected_ = true;
    // }
    // return success;

    // Placeholder:
    is_connected_ = false;
    return false;
}

void Client::Disconnect() {
    if (!is_connected_) {
        return;
    }

    // TODO: Implement disconnection
    // ap_client_->disconnect();

    is_connected_ = false;
}

bool Client::IsConnected() const {
    return is_connected_;
}

void Client::SendLocationCheck(int64_t location_id) {
    if (!is_connected_) {
        return;
    }

    // TODO: Send location check to server
    // ap_client_->LocationChecks({location_id});
}

void Client::RegisterItemReceivedCallback(std::function<void(int64_t, const std::string&)> callback) {
    item_received_callback_ = callback;
}

void Client::Poll() {
    if (!is_connected_) {
        return;
    }

    // TODO: Poll for network events
    // ap_client_->poll();
}

std::string Client::GetStatusMessage() const {
    if (is_connected_) {
        return "Connected to " + server_address_ + " as " + slot_name_;
    } else {
        return "Not connected";
    }
}

void Client::OnItemReceived(const void* item_data) {
    // TODO: Parse item data from apclient NetworkItem
    // Example:
    // const auto* item = static_cast<const apclient::NetworkItem*>(item_data);
    // int64_t item_id = item->item;
    // std::string item_name = game_data_->GetItemName(item_id);
    //
    // if (item_received_callback_) {
    //     item_received_callback_(item_id, item_name);
    // }
}

void Client::OnConnected() {
    is_connected_ = true;
    // TODO: Handle connection success (e.g., log message)
}

void Client::OnDisconnected() {
    is_connected_ = false;
    // TODO: Handle disconnection (e.g., log message)
}

} // namespace FFVIIRebirthAP
