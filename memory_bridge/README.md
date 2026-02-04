# FF7 Rebirth Memory Bridge

External memory manipulation tool for FFVIIRebirthAP Archipelago mod.

## Purpose

This standalone C++ application provides item granting capabilities to the UE4SS Lua mod by:

1. Attaching to the FF7 Rebirth game process
2. Finding the inventory memory structure via signature scanning
3. Hosting an HTTP server for the Lua mod to communicate with
4. Writing items directly to game memory

## Features

- **Auto-attach**: Waits for FF7 Rebirth to launch and auto-attaches
- **Signature scanning**: Dynamically finds inventory pointer (no hardcoded addresses)
- **HTTP API**: Simple REST API for Lua mod integration
- **Safe memory operations**: Validates writes and provides error handling

## Building

### Option 1: Visual Studio

1. Open Developer Command Prompt for VS 2022
2. Navigate to memory_bridge directory:
   ```cmd
   cd "C:\Users\jeffk\OneDrive\Documents\GitHub\FFVIIRebirthAP\memory_bridge"
   ```
3. Create build directory and compile:
   ```cmd
   mkdir build
   cd build
   cmake ..
   cmake --build . --config Release
   ```
4. Executable will be in: `build\bin\Release\MemoryBridge.exe`

### Option 2: MinGW

1. Install MinGW-w64
2. Navigate to memory_bridge directory
3. Build:
   ```cmd
   mkdir build
   cd build
   cmake -G "MinGW Makefiles" ..
   cmake --build .
   ```

### Option 3: Direct Compilation (no CMake)

```cmd
cl /EHsc /std:c++17 /O2 main.cpp MemoryBridge.cpp /link ws2_32.lib /out:MemoryBridge.exe
```

Or with g++:

```cmd
g++ -std=c++17 -O2 main.cpp MemoryBridge.cpp -o MemoryBridge.exe -lws2_32
```

## Usage

1. **Start Memory Bridge first**:

   ```cmd
   MemoryBridge.exe
   ```

   It will wait for FF7 Rebirth to launch.

2. **Launch FF7 Rebirth**

   - Memory Bridge will auto-detect and attach
   - It will scan for the inventory pointer
   - HTTP server will start on `localhost:8080`

3. **Lua mod integration**:
   The Lua mod sends HTTP POST requests to grant items:
   ```lua
   POST http://localhost:8080/give_item
   Body: {"id":100,"qty":5}
   ```

## API Endpoints

### POST /give_item

Grant an item to the player.

**Request:**

```json
{
  "id": 100, // Item ID (100 = Potion, 101 = Hi-Potion, etc.)
  "qty": 5 // Quantity to add
}
```

**Response (success):**

```json
{
  "success": true,
  "message": "Item granted"
}
```

### GET /status

Check if bridge is running and attached.

**Response:**

```json
{
  "running": true,
  "pid": 12345,
  "inventoryPtr": "0x7FF12ABC3000"
}
```

## Item IDs

From CE table analysis:

- **100** = Potion
- **101** = Hi-Potion
- **102** = Mega Potion
- **110** = Elixir
- **120** = Phoenix Down
- **130** = Remedy
- **2** = Moogle Medals
- **3** = Golden Plums
- **2000+** = Equipment/Armor
- **10001+** = Materia

Full mappings in `../worlds/finalfantasy_rebirth/data/_consolidated_data.json`

## Memory Structure

Based on CE table `ff7rebirth_- sharing.CT`:

```
Base Pointer: binven_ptr (found via AOBscan)
Pattern: 45 8B ?? ?? 44 2B ?? ?? 44 89
Injection: ff7rebirth_.exe + 0xF40A2F

Structure:
  binven_ptr + 0x8  = Item ID (4 bytes, int32)
  binven_ptr + 0xC  = Item Quantity (4 bytes, int32)
```

## Troubleshooting

### "Pattern not found"

- CE table may be outdated for your game version
- Check for game updates
- Compare with latest CE table from FearlessRevolution

### "Failed to attach"

- Run as Administrator
- Check if game is running
- Verify game process name is `ff7rebirth_.exe`

### HTTP connection refused

- Check Windows Firewall
- Verify port 8080 is not in use: `netstat -an | findstr :8080`

### Items not appearing in-game

- Pointer offset may need adjustment (+0x8, +0xC)
- Memory structure may have changed with game updates
- Verify with CE table

## Development

### Adding new features:

1. **Multiple item slots**: Modify `GiveItem()` to write to different inventory slots
2. **Equipment granting**: Add separate endpoint for equipment IDs (2000+)
3. **Materia granting**: Add endpoint for materia IDs (10001+)
4. **Gil granting**: Find gil pointer and add `/give_gil` endpoint

### Testing:

Test with curl:

```cmd
curl -X POST http://localhost:8080/give_item -H "Content-Type: application/json" -d "{\"id\":100,\"qty\":5}"
```

## Credits

- Memory structure from BigBear743's CE table
- WeMod/FLiNG trainers for proof of concept
- FearlessRevolution community
