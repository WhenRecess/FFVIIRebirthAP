--[[
    ItemHandler.lua
    Handles receiving items from Archipelago and granting them in-game
    
    FFVII Rebirth Item System (from UE4SS dump analysis):
    
    Data Structures:
    - EndDataTableItem: Item definitions (UniqueId, ItemCategory, MaxCount)
    - EndDataTableInventoryList: Inventory entries (Type, TableID, IsStack)
    - EndDataTableMateria: Materia definitions (MateriaType, stats)
    - EndDataTableReward: Reward definitions (ItemID_Array, ItemCount_Array)
    
    Key Findings:
    - Items use NameProperty strings (e.g., "ITEM_POTION") not integer IDs
    - GetItemNumBP takes a NameProperty item identifier
    - Story flags control key items and unlocks
    - ResidentWork variables store persistent item counts
    
    APIs:
    - EndDataBaseDataBaseAPI:GetItemNumBP(itemName) - Check item counts  
    - EndDataBaseDataBaseAPI:SetResidentWorkInteger(workName, value) - Set variables
    - EndDataBaseDataBaseAPI:SetStoryFlagBP(flagName, value) - Set flags
]]

local ItemHandler = {}
local HttpClient = require("HttpClient")

-- Item ID base (must match APWorld)
local BASE_ID = 770000

-- Memory Bridge configuration
local MEMORY_BRIDGE_URL = "http://localhost:8080"
local MEMORY_BRIDGE_FILE = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\memory_bridge\\requests.txt"
local MEMORY_BRIDGE_CE_PATH = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\ce.txt"
local USE_MEMORY_BRIDGE = true  -- Set to false to use old API method

-- Configure HttpClient fallback
HttpClient.SetFallbackFilePath(MEMORY_BRIDGE_FILE)

-- Internal state
local State = {
    ReceivedItems = {},
    PendingItems = {},
    ItemQueue = {},
    APIAvailable = false,
}

-- ============================================================================
-- Item Name Mapping Tables
-- Maps AP item names to FFVII Rebirth internal NameProperty identifiers
-- Format discovered: Items use string identifiers like "ITEM_<NAME>" 
-- ============================================================================

-- AP item name -> Memory Item ID (for Memory Bridge)
-- From CE table analysis: 100=Potion, 101=Hi-Potion, etc.
local APItemToMemoryId = {
    -- Consumables
    ["Potion"] = 100,
    ["Hi-Potion"] = 101,
    ["Mega Potion"] = 102,
    ["Elixir"] = 110,
    ["Phoenix Down"] = 120,
    ["Remedy"] = 130,
    ["Moogle Medals"] = 2,
    ["Golden Plums"] = 3,
    -- TODO: Add more mappings from CE list or exports
}

local function NormalizeItemName(name)
    if not name then return "" end
    local s = name:lower()
    s = s:gsub("[-_]", " ")
    s = s:gsub("%s+", " ")
    s = s:gsub("^%s+", "")
    s = s:gsub("%s+$", "")
    return s
end

local APItemToMemoryIdNormalized = {}
for k, v in pairs(APItemToMemoryId) do
    APItemToMemoryIdNormalized[NormalizeItemName(k)] = v
end

local function LoadMemoryIdMapFromCE()
    local file = io.open(MEMORY_BRIDGE_CE_PATH, "r")
    if not file then
        LogDebug("CE table not found for memory ID mapping: " .. MEMORY_BRIDGE_CE_PATH)
        return
    end

    local inDropDown = false
    local inItemIdBlock = false
    local added = 0

    for line in file:lines() do
        if line:find("<Description>\"Item ID\"</Description>") then
            inItemIdBlock = true
        end

        if inItemIdBlock and line:find("<DropDownList") then
            inDropDown = true
        elseif inDropDown and line:find("</DropDownList>") then
            inDropDown = false
            inItemIdBlock = false
        elseif inDropDown then
            local id, name = line:match("^(%d+)%s*:%s*(.+)$")
            if id and name and name ~= "blank" then
                local numId = tonumber(id)
                if numId then
                    APItemToMemoryId[name] = numId
                    APItemToMemoryIdNormalized[NormalizeItemName(name)] = numId
                    added = added + 1
                end
            end
        end
    end

    file:close()
    print(string.format("[ItemHandler] Loaded %d memory item IDs from CE table", added))
end

LoadMemoryIdMapFromCE()

local function ResolveMemoryItemId(itemName)
    if not itemName then return nil end
    local direct = APItemToMemoryId[itemName]
    if direct then return direct end
    return APItemToMemoryIdNormalized[NormalizeItemName(itemName)]
end

-- AP item name -> Game item NameProperty ID (for old API method)
-- These need to be verified against actual game data
local APItemToGameName = {
    -- Consumables (Category from EndDataTableItem)
    ["Potion"] = "ITEM_POTION",
    ["Hi-Potion"] = "ITEM_HI_POTION", 
    ["Mega-Potion"] = "ITEM_MEGA_POTION",
    ["Ether"] = "ITEM_ETHER",
    ["Turbo Ether"] = "ITEM_TURBO_ETHER",
    ["Phoenix Down"] = "ITEM_PHOENIX_DOWN",
    ["Elixir"] = "ITEM_ELIXIR",
    ["Megalixir"] = "ITEM_MEGALIXIR",
    ["Antidote"] = "ITEM_ANTIDOTE",
    ["Echo Mist"] = "ITEM_ECHO_MIST",
    ["Maiden's Kiss"] = "ITEM_MAIDENS_KISS",
    ["Remedy"] = "ITEM_REMEDY",
    
    -- Materia (uses different system - MateriaType from EndDataTableMateria)
    ["Fire Materia"] = "MAT_FIRE",
    ["Fira Materia"] = "MAT_FIRA",
    ["Firaga Materia"] = "MAT_FIRAGA",
    ["Ice Materia"] = "MAT_BLIZZARD",
    ["Blizzara Materia"] = "MAT_BLIZZARA",
    ["Blizzaga Materia"] = "MAT_BLIZZAGA",
    ["Lightning Materia"] = "MAT_THUNDER",
    ["Thundara Materia"] = "MAT_THUNDARA",
    ["Thundaga Materia"] = "MAT_THUNDAGA",
    ["Healing Materia"] = "MAT_CURE",
    ["Cura Materia"] = "MAT_CURA",
    ["Curaga Materia"] = "MAT_CURAGA",
    ["Revival Materia"] = "MAT_RAISE",
    ["Barrier Materia"] = "MAT_BARRIER",
    
    -- Key Items (use StoryFlags instead of inventory)
    ["Chocobo Lure"] = "FLAG_ITEM_CHOCOBO_LURE",
    ["Grappling Gun"] = "FLAG_ITEM_GRAPPLING_GUN",
    
    -- Gil bundles (handled specially)
    ["Gil Bundle (100)"] = "GIL_100",
    ["Gil Bundle (500)"] = "GIL_500",
    ["Gil Bundle (1000)"] = "GIL_1000",
    ["Gil Bundle (5000)"] = "GIL_5000",
}

-- Item types for special handling
local ItemType = {
    CONSUMABLE = "consumable",
    MATERIA = "materia",
    EQUIPMENT = "equipment",
    KEY_ITEM = "key_item",
    GIL = "gil",
    UNKNOWN = "unknown",
}

-- Determine item type from game name prefix
local function GetItemType(gameName)
    if not gameName then return ItemType.UNKNOWN end
    
    if gameName:match("^ITEM_") then
        return ItemType.CONSUMABLE
    elseif gameName:match("^MAT_") then
        return ItemType.MATERIA
    elseif gameName:match("^EQUIP_") or gameName:match("^WEAPON_") or gameName:match("^ARMOR_") then
        return ItemType.EQUIPMENT
    elseif gameName:match("^FLAG_") then
        return ItemType.KEY_ITEM
    elseif gameName:match("^GIL_") then
        return ItemType.GIL
    end
    
    return ItemType.UNKNOWN
end

-- ============================================================================
-- Utility Functions
-- ============================================================================

local function Log(msg)
    print(string.format("[ItemHandler] %s", msg))
end

local function LogDebug(msg)
    print(string.format("[ItemHandler][DEBUG] %s", msg))
end

-- ============================================================================
-- Game Inventory Interface
-- Using discovered FFVII Rebirth APIs with NameProperty strings
-- Based on EndDataTableItem, EndDataTableMateria, etc. structures
-- ============================================================================

-- Cache for API reference
local DataBaseAPI = nil

---Get the EndDataBaseDataBaseAPI singleton
---@return userdata|nil
local function GetDataBaseAPI()
    if DataBaseAPI then
        return DataBaseAPI
    end
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
    end)
    
    if success and api then
        DataBaseAPI = api
        LogDebug("Found EndDataBaseDataBaseAPI")
        return api
    end
    
    return nil
end

---Add an item to the player's inventory using NameProperty string
---Items use EndDataTableInventoryList with Type + TableID (NameProperty)
---@param gameItemName string The game's internal item name (e.g. "ITEM_POTION")
---@param quantity number Number to add
---@return boolean success
local function AddToInventory(gameItemName, quantity)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("AddToInventory: API not available")
        return false
    end
    
    -- Try GetItemNumBP with NameProperty string
    -- Based on discovered API: GetItemNumBP likely takes item name string
    local success, currentCount = pcall(function()
        return api:GetItemNumBP(gameItemName)
    end)
    
    if success then
        local newCount = (currentCount or 0) + quantity
        
        -- Items stored in ResidentWork - variable name likely matches item name
        -- or uses a pattern like the item's TableID from EndDataTableInventoryList
        local setSuccess = pcall(function()
            api:SetResidentWorkInteger(gameItemName, newCount)
        end)
        
        if setSuccess then
            Log(string.format("Set item %s count to %d", gameItemName, newCount))
            return true
        end
        
        -- Alternative: Try without ITEM_ prefix if that fails
        if gameItemName:match("^ITEM_") then
            local shortName = gameItemName:gsub("^ITEM_", "")
            setSuccess = pcall(function()
                api:SetResidentWorkInteger(shortName, newCount)
            end)
            if setSuccess then
                Log(string.format("Set item %s count to %d (short name)", shortName, newCount))
                return true
            end
        end
    end
    
    LogDebug(string.format("AddToInventory(%s, %d) - could not set item count", gameItemName, quantity))
    return false
end

---Add Gil to the player
---Gil stored in ResidentWork variable
---@param amount number Amount of Gil to add
---@return boolean success
local function AddGil(amount)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("AddGil: API not available")
        return false
    end
    
    -- Try known work variable names for Gil
    -- ResidentWork naming convention from dump analysis
    local gilWorkIds = {"GIL", "MONEY", "Gil", "Money", "PLAYER_GIL", "PlayerGil"}
    
    for _, workId in ipairs(gilWorkIds) do
        local success, currentGil = pcall(function()
            return api:GetResidentWorkInteger(workId)
        end)
        
        if success and currentGil and currentGil >= 0 then
            local newGil = currentGil + amount
            
            local setSuccess = pcall(function()
                api:SetResidentWorkInteger(workId, newGil)
            end)
            
            if setSuccess then
                Log(string.format("Added %d Gil (total: %d) via %s", amount, newGil, workId))
                return true
            end
        end
    end
    
    LogDebug(string.format("AddGil(%d) - could not find Gil variable", amount))
    return false
end

---Add a key item via story flag
---Key items controlled by StoryFlag system (see EndObjectTreasure:StoryFlagName)
---@param flagName string Story flag name (e.g. "FLAG_ITEM_CHOCOBO_LURE")
---@return boolean success
local function AddKeyItem(flagName)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("AddKeyItem: API not available")
        return false
    end
    
    -- Key items use story flags
    -- Format from EndDataTableQuest: CompleteStoryFlag, AcceptedStoryFlag patterns
    local success = pcall(function()
        api:SetStoryFlagBP(flagName, true)
    end)
    
    if success then
        Log(string.format("Set key item flag: %s", flagName))
        return true
    end
    
    -- Try alternate flag name formats
    local alternates = {}
    if flagName:match("^FLAG_") then
        table.insert(alternates, flagName:gsub("^FLAG_", ""))
    else
        table.insert(alternates, "FLAG_" .. flagName)
    end
    
    for _, altFlag in ipairs(alternates) do
        success = pcall(function()
            api:SetStoryFlagBP(altFlag, true)
        end)
        if success then
            Log(string.format("Set key item flag: %s (alternate)", altFlag))
            return true
        end
    end
    
    LogDebug(string.format("AddKeyItem(%s) - could not set flag", flagName))
    return false
end

---Add Materia to the player
---Based on EndDataTableMateria structure with UniqueId as NameProperty
---@param materiaName string Materia name (e.g. "MAT_FIRE")
---@return boolean success
local function AddMateria(materiaName)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("AddMateria: API not available")
        return false
    end
    
    -- Materia may use different system than regular items
    -- EndDataTableMateria has: UniqueId, Level, AP, Attack, Magic, etc.
    -- Try ResidentWork first
    local success = pcall(function()
        -- Materia might use a "has materia" flag or count
        api:SetResidentWorkInteger(materiaName, 1)
    end)
    
    if success then
        Log(string.format("Added materia: %s", materiaName))
        return true
    end
    
    -- Try without MAT_ prefix
    if materiaName:match("^MAT_") then
        local shortName = materiaName:gsub("^MAT_", "")
        success = pcall(function()
            api:SetResidentWorkInteger(shortName, 1)
        end)
        if success then
            Log(string.format("Added materia: %s (short name)", shortName))
            return true
        end
    end
    
    LogDebug(string.format("AddMateria(%s) - implementation may need adjustment", materiaName))
    return false
end

-- ============================================================================
-- Item Processing
-- ============================================================================

---Grant an item to the player based on AP item name
---Uses string-based NameProperty system discovered from game data
---@param apItemId number Archipelago item ID
---@param itemName string Item name for display/lookup
---@return boolean success
function ItemHandler.GrantItem(apItemId, itemName)
    -- Try Memory Bridge first (direct memory write)
    if USE_MEMORY_BRIDGE then
        -- Convert AP item name to game item ID
        local gameItemId = ResolveMemoryItemId(itemName)
        
        if gameItemId then
            print(string.format("[ItemHandler] Granting '%s' (Memory ID: %d) via Memory Bridge", itemName, gameItemId))
            
            local success, response = HttpClient.Post(
                MEMORY_BRIDGE_URL .. "/give_item",
                {id = gameItemId, qty = 1}
            )
            
            if success then
                Log(string.format("Granted '%s' via Memory Bridge", itemName))
                return true
            else
                Log(string.format("Memory Bridge failed for '%s': %s", itemName, tostring(response)))
                Log("Falling back to API method...")
            end
        else
            Log(string.format("Item '%s' has no memory ID mapping, falling back to API", itemName))
        end
    end
    
    -- Fallback: Old API method (doesn't work but kept for testing)
    -- Look up game item name (NameProperty string)
    local gameName = APItemToGameName[itemName]
    
    if not gameName then
        -- Unknown item - log and fail gracefully
        Log(string.format("Unknown item '%s' (AP ID: %d) - no mapping found", itemName, apItemId))
        return false
    end
    
    local itemType = GetItemType(gameName)
    local success = false
    
    if itemType == ItemType.GIL then
        -- Gil bundles - parse amount from name (e.g. "GIL_500", "GIL_2000")
        local amount = tonumber(gameName:match("GIL_(%d+)")) or 1000
        success = AddGil(amount)
        
    elseif itemType == ItemType.MATERIA then
        success = AddMateria(gameName)
        
    elseif itemType == ItemType.KEY_ITEM then
        -- Key items use story flags
        success = AddKeyItem(gameName)
        
    elseif itemType == ItemType.EQUIPMENT then
        -- Equipment items - handled like regular inventory
        success = AddToInventory(gameName, 1)
        
    elseif itemType == ItemType.CONSUMABLE then
        -- Regular consumable items
        success = AddToInventory(gameName, 1)
        
    else
        -- Unknown type - try as inventory item
        Log(string.format("Unknown item type for '%s', trying as inventory", gameName))
        success = AddToInventory(gameName, 1)
    end
    
    return success
end

---Process an item received from AP
---@param itemId number AP item ID
---@param itemName string Item name
---@param senderName string Name of sending player
function ItemHandler.ReceiveItem(itemId, itemName, senderName)
    -- Record the received item
    table.insert(State.ReceivedItems, {
        id = itemId,
        name = itemName,
        sender = senderName,
        time = os.time(),
        granted = false,
    })
    
    -- Queue for granting
    table.insert(State.ItemQueue, {
        id = itemId,
        name = itemName,
        sender = senderName,
    })
    
    -- Try to grant immediately
    ItemHandler.ProcessQueue()
end

---Process queued items
function ItemHandler.ProcessQueue()
    local remaining = {}
    
    for _, item in ipairs(State.ItemQueue) do
        local success = ItemHandler.GrantItem(item.id, item.name)
        
        if success then
            Log(string.format("Granted: %s", item.name))
            -- Mark as granted in received list
            for _, recv in ipairs(State.ReceivedItems) do
                if recv.id == item.id and not recv.granted then
                    recv.granted = true
                    break
                end
            end
        else
            -- Keep in queue for retry
            table.insert(remaining, item)
        end
    end
    
    State.ItemQueue = remaining
end

-- ============================================================================
-- Query Functions
-- ============================================================================

---Get list of received items
---@return table
function ItemHandler.GetReceivedItems()
    return State.ReceivedItems
end

---Get count of received items
---@return number
function ItemHandler.GetReceivedCount()
    return #State.ReceivedItems
end

---Get pending item count
---@return number
function ItemHandler.GetPendingCount()
    return #State.ItemQueue
end

-- ============================================================================
-- Initialization
-- ============================================================================

function ItemHandler.Initialize()
    Log("Initializing item handler...")
    
    -- Try to find the DataBase API
    local api = GetDataBaseAPI()
    if api then
        Log("DataBaseAPI found - item handling available")
        -- Don't test API calls here - game world may not be loaded yet
    else
        Log("Warning: DataBaseAPI not found - item granting will fail")
        Log("API will be retried when items are received")
    end
    
    -- Item mapping is defined in APItemToGameName table above
    -- TODO: Consider loading additional mappings from external JSON file
    -- This would allow updating item mappings without code changes:
    --[[
    local mappingFile = io.open("Mods/FFVIIRebirthAP/data/item_mapping.json", "r")
    if mappingFile then
        local content = mappingFile:read("*all")
        mappingFile:close()
        
        local mapping = json.decode(content)
        if mapping then
            for apName, gameName in pairs(mapping) do
                APItemToGameName[apName] = gameName
            end
            Log(string.format("Loaded %d item mappings from file", #mapping))
        end
    end
    ]]
    
    Log(string.format("Item handler initialized with %d item mappings", 0))  -- TODO: count table entries
end

---Debug function to dump current item mappings
function ItemHandler.DumpMappings()
    Log("=== Item Mappings ===")
    for apName, gameName in pairs(APItemToGameName) do
        local itemType = GetItemType(gameName)
        Log(string.format("  %s -> %s (type: %d)", apName, gameName, itemType))
    end
    Log("=====================")
end

---Debug function to test API access
function ItemHandler.TestAPI()
    Log("=== API Test ===")
    local api = GetDataBaseAPI()
    if not api then
        Log("ERROR: DataBaseAPI not available")
        return
    end
    
    -- Test GetItemNumBP with a common item
    local testItems = {"ITEM_POTION", "POTION", "Potion"}
    for _, itemName in ipairs(testItems) do
        local success, count = pcall(function()
            return api:GetItemNumBP(itemName)
        end)
        Log(string.format("  GetItemNumBP('%s'): success=%s, count=%s", 
            itemName, tostring(success), tostring(count)))
    end
    
    -- Test GetResidentWorkInteger
    local testVars = {"GIL", "Gil", "MONEY", "Money"}
    for _, varName in ipairs(testVars) do
        local success, value = pcall(function()
            return api:GetResidentWorkInteger(varName)
        end)
        Log(string.format("  GetResidentWorkInteger('%s'): success=%s, value=%s", 
            varName, tostring(success), tostring(value)))
    end
    
    Log("================")
end

return ItemHandler
