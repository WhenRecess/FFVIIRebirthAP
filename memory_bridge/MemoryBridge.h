#pragma once

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <windows.h>
#include <string>
#include <vector>
#include <cstdint>

class MemoryBridge {
public:
    MemoryBridge();
    ~MemoryBridge();

    // Process management
    bool AttachToGame();
    bool IsGameRunning() const;
    DWORD GetProcessId() const { return processId; }

    // Memory operations
    bool FindInventoryPointer();
    bool SetInventoryPointer(uintptr_t basePtr);
    bool SetInventoryPointerFromItemId(uintptr_t itemIdAddr);
    uintptr_t GetInventoryPointer() const { return inventoryBasePtr; }
    bool GiveItem(int itemId, int quantity);

    // Server
    bool StartServer(int port);
    void StopServer();
    bool StartFileListener(const std::string& path);

private:
    // Process
    DWORD processId;
    HANDLE processHandle;
    uintptr_t baseAddress;

    // Memory
    uintptr_t inventoryBasePtr;

    // Server
    SOCKET serverSocket;
    bool serverRunning;
    bool fileListenerRunning;
    std::string commandFilePath;
    void HandleClient(SOCKET clientSocket);
    static void ClientThread(MemoryBridge* bridge, SOCKET clientSocket);
    void FileListenerThread();
    void ProcessCommandLine(const std::string& line);

    // Memory helpers
    bool ReadMemory(uintptr_t address, void* buffer, size_t size);
    bool WriteMemory(uintptr_t address, const void* data, size_t size);
    uintptr_t FindPattern(const std::vector<uint8_t>& pattern, const std::string& mask);
    uintptr_t GetModuleBase(const std::wstring& moduleName);
    bool ValidateInventoryPointer(uintptr_t basePtr);
};
