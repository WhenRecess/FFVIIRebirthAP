-- ============================================================================
-- MemoryItem.lua - Direct Memory Item Manipulation
-- ============================================================================
-- Uses UE4SS memory functions to directly write to item inventory in memory
-- Based on Cheat Engine table reverse-engineering from FF7R
-- ============================================================================

-- Local log function
local function Log(msg)
    print(string.format("[MemoryItem] %s", msg))
end

local MemoryItem = {
    ItemDatabase = {
        -- Consumables (based on CE table IDs)
        POTION = 100,
        HI_POTION = 101,
        MEGA_POTION = 102,
        ELIXIR = 110,
        PHOENIX_DOWN = 120,
        REMEDY = 130,
        
        -- Key items/Currency
        MOOGLE_MEDALS = 2,
        GOLDEN_PLUMS = 3,
        GP = 1,  -- Gil?
        
        -- Equipment IDs (from CE table)
        METAL_BRACER = 2000,
        COPPER_BRACER = 2004,
    },
    
    -- Pointers from Cheat Engine
    InventoryBasePtr = nil,
    LastItemUpdate = 0,
}

---Initialize memory item system
---@return boolean success
function MemoryItem.Initialize()
    Log("[MemoryItem] Initializing memory access system...")
    
    -- Check if UE4SS memory functions are available
    if not readByte then
        Log("[MemoryItem] ERROR: UE4SS memory functions not available (readByte missing)")
        Log("[MemoryItem] Required: readByte, writeByte, readInteger, writeInteger functions")
        return false
    end
    
    Log("[MemoryItem] Memory functions available: readByte, writeInteger detected")
    return true
end

---Read an integer (4 bytes) from memory address
---@param address integer Memory address to read from
---@param default integer Default value if read fails
---@return integer value
local function ReadMemInt(address, default)
    default = default or 0
    local success, value = pcall(function()
        return readInteger(address)
    end)
    if not success or value == nil then
        return default
    end
    return value
end

---Write an integer (4 bytes) to memory address
---@param address integer Memory address to write to
---@param value integer Value to write
---@return boolean success
local function WriteMemInt(address, value)
    if not address or address == 0 then
        Log("[MemoryItem] ERROR: Attempted write to null address")
        return false
    end
    
    local success, err = pcall(function()
        writeInteger(address, value)
    end)
    
    if not success then
        Log(string.format("[MemoryItem] Write failed at 0x%X: %s", address, tostring(err)))
        return false
    end
    
    return true
end

---Find the inventory base pointer by scanning for the pattern
---This mimics what the CE table does with AOBscan
---@return integer|nil pointer
function MemoryItem.FindInventoryPointer()
    Log("[MemoryItem] Searching for inventory base pointer...")
    
    -- The CE table uses this pattern:
    -- aobscanmodule(inventorycontrol,ff7rebirth_.exe,458B????442B????4489)
    -- This is a signature scan - we'll try to find it using Lua's capabilities
    
    -- For now, we'll note that this requires signature scanning capabilities
    -- which UE4SS Lua may not have directly exposed
    
    Log("[MemoryItem] NOTE: Inventory pointer finding requires AOBscan (CE feature)")
    Log("[MemoryItem] Current approach: Find through game object reflection")
    
    return nil
end

---Get the current inventory base pointer (caches it)
---@return integer|nil pointer
function MemoryItem.GetInventoryPtr()
    -- If we already found it, return cached value
    if MemoryItem.InventoryBasePtr and MemoryItem.InventoryBasePtr ~= 0 then
        return MemoryItem.InventoryBasePtr
    end
    
    -- Try to find it
    local ptr = MemoryItem.FindInventoryPointer()
    if ptr then
        MemoryItem.InventoryBasePtr = ptr
        Log(string.format("[MemoryItem] Inventory pointer found: 0x%X", ptr))
    else
        Log("[MemoryItem] Could not locate inventory pointer")
    end
    
    return ptr
end

---Try to give item using direct memory manipulation
---@param itemId integer Item ID from item database
---@param quantity integer How many to give (default 1)
---@return boolean success, string message
function MemoryItem.GiveItem(itemId, quantity)
    quantity = quantity or 1
    
    Log(string.format("[MemoryItem] Attempting to give item ID %d x%d via memory", itemId, quantity))
    
    local inventoryPtr = MemoryItem.GetInventoryPtr()
    if not inventoryPtr or inventoryPtr == 0 then
        return false, "Inventory pointer not found - memory address unknown"
    end
    
    -- According to CE table:
    -- binven_ptr + 0x8 = Item ID
    -- binven_ptr + 0xC = Item Quantity
    
    local itemIdAddr = inventoryPtr + 0x8
    local itemQtyAddr = inventoryPtr + 0xC
    
    Log(string.format("[MemoryItem] Item ID address: 0x%X", itemIdAddr))
    Log(string.format("[MemoryItem] Item Qty address: 0x%X", itemQtyAddr))
    
    -- Read current item ID
    local currentItemId = ReadMemInt(itemIdAddr)
    Log(string.format("[MemoryItem] Current item ID at pointer: %d", currentItemId))
    
    -- If it's a different item, write the new ID
    if currentItemId ~= itemId then
        if not WriteMemInt(itemIdAddr, itemId) then
            return false, "Failed to write item ID to memory"
        end
        Log(string.format("[MemoryItem] Wrote item ID %d to memory", itemId))
    end
    
    -- Read current quantity
    local currentQty = ReadMemInt(itemQtyAddr)
    Log(string.format("[MemoryItem] Current quantity: %d", currentQty))
    
    -- Write new quantity (add to existing)
    local newQty = currentQty + quantity
    if not WriteMemInt(itemQtyAddr, newQty) then
        return false, "Failed to write item quantity to memory"
    end
    
    Log(string.format("[MemoryItem] Wrote quantity %d to memory (was %d)", newQty, currentQty))
    
    MemoryItem.LastItemUpdate = os.clock()
    return true, string.format("Item ID %d x%d written to memory", itemId, newQty)
end

---Scan for item in inventory by iterating potential memory ranges
---This is experimental and may not work without proper pointer chain
---@return table|nil items found
function MemoryItem.ScanForItems()
    Log("[MemoryItem] Scanning for items in memory...")
    Log("[MemoryItem] NOTE: Scan requires known memory base address")
    
    -- This would require:
    -- 1. Base game module address (ff7rebirth_.exe)
    -- 2. Signature scanning capability
    -- 3. Pointer arithmetic and dereferencing
    
    Log("[MemoryItem] Scan requires low-level memory access not directly available in Lua")
    return nil
end

---Test memory reading capability
---@return boolean success
function MemoryItem.TestMemoryAccess()
    Log("[MemoryItem] Testing basic memory access...")
    
    local success, result = pcall(function()
        -- Try to read a known safe address (usually game code base)
        local testAddr = 0x140000000  -- Typical Unreal Engine base
        local byte = readByte(testAddr)
        return byte
    end)
    
    if success then
        Log(string.format("[MemoryItem] Memory read successful (got: 0x%02X)", result or 0))
        return true
    else
        Log(string.format("[MemoryItem] Memory read failed: %s", tostring(result)))
        return false
    end
end

---Manual pointer entry (user can find via CE and enter)
---@param address integer The inventory base address
function MemoryItem.SetInventoryPointer(address)
    MemoryItem.InventoryBasePtr = address
    Log(string.format("[MemoryItem] Inventory pointer manually set to: 0x%X", address))
end

return MemoryItem
