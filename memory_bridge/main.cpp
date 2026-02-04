#include "MemoryBridge.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <fstream>

int main() {
    std::cout << "===========================================\n";
    std::cout << "  FF7 Rebirth Memory Bridge v1.0\n";
    std::cout << "  Archipelago Item Granting Service\n";
    std::cout << "===========================================\n\n";

    MemoryBridge bridge;

    // Wait for FF7 Rebirth to launch
    std::cout << "[INFO] Waiting for FINAL FANTASY VII REBIRTH...\n";
    while (!bridge.AttachToGame()) {
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }

    std::cout << "[SUCCESS] Attached to FF7 Rebirth (PID: " << bridge.GetProcessId() << ")\n";

    // Find inventory pointer
    std::cout << "[INFO] Scanning for inventory pointer...\n";
    if (bridge.FindInventoryPointer()) {
        std::cout << "[SUCCESS] Inventory pointer found: 0x" 
                  << std::hex << bridge.GetInventoryPointer() << std::dec << "\n";
    } else {
        std::cerr << "[WARN] Automatic inventory pointer discovery not available\n";
        std::cerr << "[WARN] Checking pointer.txt...\n";

        std::string input;
        {
            std::ifstream inFile("pointer.txt");
            if (inFile.good()) {
                std::getline(inFile, input);
                inFile.close();
                if (!input.empty()) {
                    std::cout << "[INFO] Loaded pointer from pointer.txt: " << input << "\n";
                }
            }
        }

        if (input.empty()) {
            std::cerr << "[WARN] pointer.txt not found or empty\n";
            std::cerr << "[WARN] Please enter pointer manually (from CE binven_ptr)\n";

            std::cout << "\nEnter inventory base pointer (hex) or item ID address with prefix 'id:'\n";
            std::cout << "Examples: 0x7FF6ABCDEF00   or   id:0x7FF6ABCDEFF8\n";
            std::cout << "> ";
            std::getline(std::cin, input);
        }

        auto parseHex = [](const std::string& text, uintptr_t& out) -> bool {
            std::string s = text;
            if (s.rfind("0x", 0) == 0 || s.rfind("0X", 0) == 0) {
                s = s.substr(2);
            }
            if (s.empty()) return false;
            try {
                out = static_cast<uintptr_t>(std::stoull(s, nullptr, 16));
                return true;
            } catch (...) {
                return false;
            }
        };

        bool setOk = false;
        if (input.rfind("id:", 0) == 0 || input.rfind("ID:", 0) == 0) {
            uintptr_t itemIdAddr = 0;
            if (parseHex(input.substr(3), itemIdAddr)) {
                setOk = bridge.SetInventoryPointerFromItemId(itemIdAddr);
            }
        } else {
            uintptr_t basePtr = 0;
            if (parseHex(input, basePtr)) {
                setOk = bridge.SetInventoryPointer(basePtr);
            }
        }

        if (!setOk) {
            std::cerr << "[ERROR] Invalid or unreadable pointer - aborting\n";
            std::cout << "\nPress Enter to exit...";
            std::cin.get();
            return 1;
        }
    }

    // Start HTTP server
    std::cout << "[INFO] Starting HTTP server on localhost:8080...\n";
    if (bridge.StartServer(8080)) {
        std::cout << "[SUCCESS] Server running - ready to receive item requests\n";
        bridge.StartFileListener("requests.txt");
        std::cout << "\n===========================================\n";
        std::cout << "  Memory Bridge Active\n";
        std::cout << "  Lua mod can now grant items via HTTP\n";
        std::cout << "  Press Ctrl+C to stop\n";
        std::cout << "===========================================\n\n";

        // Keep running until process exits or Ctrl+C
        while (bridge.IsGameRunning()) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }

        std::cout << "\n[INFO] Game closed - shutting down\n";
    } else {
        std::cerr << "[ERROR] Failed to start HTTP server\n";
        std::cout << "\nPress Enter to exit...";
        std::cin.get();
        return 1;
    }

    return 0;
}
