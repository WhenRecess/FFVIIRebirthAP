#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <tlhelp32.h>
#include <iostream>
#include <sstream>
#include <thread>
#include <fstream>
#include <chrono>
#include "MemoryBridge.h"

#pragma comment(lib, "ws2_32.lib")

MemoryBridge::MemoryBridge() 
        : processId(0), processHandle(nullptr), baseAddress(0), 
            inventoryBasePtr(0), serverSocket(INVALID_SOCKET), serverRunning(false),
            fileListenerRunning(false) {
    
    // Initialize Winsock
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
}

MemoryBridge::~MemoryBridge() {
    StopServer();
    fileListenerRunning = false;
    if (processHandle) {
        CloseHandle(processHandle);
    }
    WSACleanup();
}

bool MemoryBridge::AttachToGame() {
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snapshot == INVALID_HANDLE_VALUE) {
        return false;
    }

    PROCESSENTRY32W pe32;
    pe32.dwSize = sizeof(pe32);

    if (Process32FirstW(snapshot, &pe32)) {
        do {
            // Look for ff7rebirth_.exe
            if (wcsstr(pe32.szExeFile, L"ff7rebirth_") != nullptr) {
                processId = pe32.th32ProcessID;
                CloseHandle(snapshot);

                // Open process with all access
                processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, processId);
                if (processHandle) {
                    baseAddress = GetModuleBase(L"ff7rebirth_.exe");
                    return true;
                }
                return false;
            }
        } while (Process32NextW(snapshot, &pe32));
    }

    CloseHandle(snapshot);
    return false;
}

bool MemoryBridge::IsGameRunning() const {
    if (!processHandle) return false;
    
    DWORD exitCode;
    if (GetExitCodeProcess(processHandle, &exitCode)) {
        return exitCode == STILL_ACTIVE;
    }
    return false;
}

uintptr_t MemoryBridge::GetModuleBase(const std::wstring& moduleName) {
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, processId);
    if (snapshot == INVALID_HANDLE_VALUE) {
        return 0;
    }

    MODULEENTRY32W me32;
    me32.dwSize = sizeof(me32);

    if (Module32FirstW(snapshot, &me32)) {
        do {
            if (_wcsicmp(me32.szModule, moduleName.c_str()) == 0) {
                CloseHandle(snapshot);
                return (uintptr_t)me32.modBaseAddr;
            }
        } while (Module32NextW(snapshot, &me32));
    }

    CloseHandle(snapshot);
    return 0;
}

bool MemoryBridge::ReadMemory(uintptr_t address, void* buffer, size_t size) {
    SIZE_T bytesRead;
    return ReadProcessMemory(processHandle, (LPCVOID)address, buffer, size, &bytesRead) && bytesRead == size;
}

bool MemoryBridge::WriteMemory(uintptr_t address, const void* data, size_t size) {
    SIZE_T bytesWritten;
    return WriteProcessMemory(processHandle, (LPVOID)address, data, size, &bytesWritten) && bytesWritten == size;
}

bool MemoryBridge::FindInventoryPointer() {
    // NOTE: The CE table captures binven_ptr via an injected hook (r14).
    // This external tool does not yet implement that hook, so automatic
    // discovery is currently not available.
    return false;
}

bool MemoryBridge::ValidateInventoryPointer(uintptr_t basePtr) {
    if (basePtr == 0) {
        return false;
    }

    const uintptr_t itemIdAddr = basePtr + 0x8;
    const uintptr_t itemQtyAddr = basePtr + 0xC;

    std::cout << "[INFO] Item ID address: 0x" << std::hex << itemIdAddr << std::dec << "\n";
    std::cout << "[INFO] Item Qty address: 0x" << std::hex << itemQtyAddr << std::dec << "\n";

    int testValue = 0;
    if (!ReadMemory(itemIdAddr, &testValue, sizeof(testValue))) {
        std::cerr << "[ERROR] Could not read from Item ID address\n";
        return false;
    }

    std::cout << "[SUCCESS] Verified Item ID at 0x" << std::hex << itemIdAddr
              << ": " << std::dec << testValue << "\n";
    return true;
}

bool MemoryBridge::SetInventoryPointer(uintptr_t basePtr) {
    std::cout << "[INFO] Using inventory base pointer: 0x" << std::hex << basePtr << std::dec << "\n";
    if (!ValidateInventoryPointer(basePtr)) {
        std::cerr << "[ERROR] Inventory pointer validation failed\n";
        return false;
    }

    inventoryBasePtr = basePtr;
    return true;
}

bool MemoryBridge::SetInventoryPointerFromItemId(uintptr_t itemIdAddr) {
    if (itemIdAddr < 0x8) {
        return false;
    }

    const uintptr_t basePtr = itemIdAddr - 0x8;
    std::cout << "[INFO] Calculated base pointer from Item ID address\n";
    return SetInventoryPointer(basePtr);
}

uintptr_t MemoryBridge::FindPattern(const std::vector<uint8_t>& pattern, const std::string& mask) {
    MEMORY_BASIC_INFORMATION mbi;
    uintptr_t address = (uintptr_t)baseAddress;
    uintptr_t maxAddress = address + 0x10000000; // Search 256MB

    std::vector<uint8_t> buffer(0x10000); // 64KB chunks

    while (address < maxAddress) {
        if (VirtualQueryEx(processHandle, (LPCVOID)address, &mbi, sizeof(mbi)) == 0) {
            break;
        }

        if (mbi.State == MEM_COMMIT && (mbi.Protect & PAGE_GUARD) == 0 && 
            (mbi.Protect & PAGE_NOACCESS) == 0) {
            
            SIZE_T bytesToRead = min(buffer.size(), mbi.RegionSize);
            SIZE_T bytesRead;
            
            if (ReadProcessMemory(processHandle, (LPCVOID)address, buffer.data(), bytesToRead, &bytesRead)) {
                for (size_t i = 0; i < bytesRead - pattern.size(); i++) {
                    bool found = true;
                    for (size_t j = 0; j < pattern.size(); j++) {
                        if (mask[j] == 'x' && buffer[i + j] != pattern[j]) {
                            found = false;
                            break;
                        }
                    }
                    if (found) {
                        return address + i;
                    }
                }
            }
        }

        address += mbi.RegionSize;
    }

    return 0;
}

bool MemoryBridge::GiveItem(int itemId, int quantity) {
    if (inventoryBasePtr == 0) {
        std::cerr << "[ERROR] Inventory pointer not initialized\n";
        return false;
    }

    // Write item ID at offset +0x8
    uintptr_t itemIdAddr = inventoryBasePtr + 0x8;
    if (!WriteMemory(itemIdAddr, &itemId, sizeof(itemId))) {
        std::cerr << "[ERROR] Failed to write item ID\n";
        return false;
    }

    // Read current quantity
    uintptr_t quantityAddr = inventoryBasePtr + 0xC;
    int currentQty = 0;
    ReadMemory(quantityAddr, &currentQty, sizeof(currentQty));

    // Write new quantity
    int newQty = currentQty + quantity;
    if (!WriteMemory(quantityAddr, &newQty, sizeof(newQty))) {
        std::cerr << "[ERROR] Failed to write quantity\n";
        return false;
    }

    std::cout << "[SUCCESS] Gave item " << itemId << " x" << quantity 
              << " (total: " << newQty << ")\n";
    return true;
}

bool MemoryBridge::StartServer(int port) {
    serverSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (serverSocket == INVALID_SOCKET) {
        return false;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    serverAddr.sin_port = htons(port);

    if (bind(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        closesocket(serverSocket);
        return false;
    }

    if (listen(serverSocket, 5) == SOCKET_ERROR) {
        closesocket(serverSocket);
        return false;
    }

    serverRunning = true;

    // Accept connections in separate thread
    std::thread([this]() {
        while (serverRunning) {
            SOCKET clientSocket = accept(serverSocket, nullptr, nullptr);
            if (clientSocket != INVALID_SOCKET) {
                std::thread(ClientThread, this, clientSocket).detach();
            }
        }
    }).detach();

    return true;
}

bool MemoryBridge::StartFileListener(const std::string& path) {
    commandFilePath = path;
    fileListenerRunning = true;

    std::thread(&MemoryBridge::FileListenerThread, this).detach();
    return true;
}

void MemoryBridge::FileListenerThread() {
    std::cout << "[INFO] File listener active: " << commandFilePath << "\n";

    while (fileListenerRunning) {
        std::ifstream inFile(commandFilePath);
        if (inFile.good()) {
            std::string line;
            bool hadData = false;
            while (std::getline(inFile, line)) {
                if (!line.empty()) {
                    hadData = true;
                    ProcessCommandLine(line);
                }
            }
            inFile.close();

            if (hadData) {
                std::ofstream outFile(commandFilePath, std::ios::trunc);
                outFile.close();
            }
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

void MemoryBridge::ProcessCommandLine(const std::string& line) {
    int itemId = 0;
    int quantity = 0;

    size_t idPos = line.find("\"id\":");
    size_t qtyPos = line.find("\"qty\":");

    try {
        if (idPos != std::string::npos && qtyPos != std::string::npos) {
            itemId = std::stoi(line.substr(idPos + 5));
            quantity = std::stoi(line.substr(qtyPos + 6));
        } else {
            std::stringstream ss(line);
            char sep = 0;
            ss >> itemId;
            if (ss.peek() == ',' || ss.peek() == ' ') {
                ss >> sep;
            }
            ss >> quantity;
        }
    } catch (...) {
        std::cerr << "[FILE] Invalid command: " << line << "\n";
        return;
    }

    if (itemId > 0 && quantity != 0) {
        std::cout << "[FILE] Request: item=" << itemId << " qty=" << quantity << "\n";
        GiveItem(itemId, quantity);
    }
}

void MemoryBridge::StopServer() {
    serverRunning = false;
    if (serverSocket != INVALID_SOCKET) {
        closesocket(serverSocket);
        serverSocket = INVALID_SOCKET;
    }
}

void MemoryBridge::ClientThread(MemoryBridge* bridge, SOCKET clientSocket) {
    bridge->HandleClient(clientSocket);
}

void MemoryBridge::HandleClient(SOCKET clientSocket) {
    char buffer[4096];
    int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
    
    if (bytesReceived > 0) {
        buffer[bytesReceived] = '\0';
        std::string request(buffer);

        // Parse HTTP request
        if (request.find("POST /give_item") == 0) {
            // Find JSON body (after \r\n\r\n)
            size_t bodyPos = request.find("\r\n\r\n");
            if (bodyPos != std::string::npos) {
                std::string body = request.substr(bodyPos + 4);
                
                // Simple JSON parsing (expecting: {"id":100,"qty":5})
                int itemId = 0, quantity = 0;
                size_t idPos = body.find("\"id\":");
                size_t qtyPos = body.find("\"qty\":");
                
                if (idPos != std::string::npos && qtyPos != std::string::npos) {
                    itemId = std::stoi(body.substr(idPos + 5));
                    quantity = std::stoi(body.substr(qtyPos + 6));
                    
                    std::cout << "[HTTP] Received request: item=" << itemId 
                              << " qty=" << quantity << "\n";
                    
                    bool success = GiveItem(itemId, quantity);
                    
                    // Send response
                    std::string response;
                    if (success) {
                        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
                                   "{\"success\":true,\"message\":\"Item granted\"}";
                    } else {
                        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\n\r\n"
                                   "{\"success\":false,\"message\":\"Failed to grant item\"}";
                    }
                    
                    send(clientSocket, response.c_str(), response.length(), 0);
                }
            }
        } else if (request.find("GET /status") == 0) {
            // Status endpoint
            std::stringstream ss;
            ss << "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n"
               << "{\"running\":true,\"pid\":" << processId 
               << ",\"inventoryPtr\":\"0x" << std::hex << inventoryBasePtr << std::dec << "\"}";
            
            std::string response = ss.str();
            send(clientSocket, response.c_str(), response.length(), 0);
        }
    }

    closesocket(clientSocket);
}
