--[[
    LocationTracker.lua
    Tracks in-game events and maps them to Archipelago locations
    
    This module watches game memory for:
    - Item pickups (chests, field items, shop purchases)
    - Story flags (chapter completion, boss defeats)
    - Battle victories (colosseum, territory battles)
    - Quest completions
    
    When a location is detected, it:
    1. Writes the location ID to ap_checked_locations.txt
    2. Prevents the vanilla item from being granted
    3. Waits for AP to send the randomized item
]]

local LocationTracker = {}

-- ============================================================================
-- Configuration
-- ============================================================================

local LOCATIONS_FILE = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\memory_bridge\\ap_locations.json"
local CHECKED_FILE = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\memory_bridge\\ap_checked_locations.txt"

-- Poll interval (ms)
local POLL_INTERVAL = 500

-- ============================================================================
-- Location Database
-- ============================================================================

-- Maps in-game triggers to AP location IDs
-- Structure: [trigger_type][trigger_id] = {location_id, name}
local LocationDatabase = {
    -- Story flags (ResidentWork variables)
    story_flags = {
        [1001] = {location_id = 770001001, name = "Story: Kalm Flashback Complete"},
        [1002] = {location_id = 770001002, name = "Story: Reach Chocobo Ranch"},
        -- ... more story flags
    },
    
    -- Item pickups (field items by map + item ID)
    field_items = {
        ["Grasslands_01_Chest_001"] = {location_id = 770002001, name = "Grasslands: Chocobo Ranch Chest"},
        ["Grasslands_02_Chest_005"] = {location_id = 770002002, name = "Grasslands: Cliff Side Chest"},
        -- ... more field items
    },
    
    -- Shop purchases (by shop ID + item slot)
    shop_items = {
        ["Shop_Kalm_Slot_1"] = {location_id = 770003001, name = "Kalm Shop: Item Slot 1"},
        -- ... more shop slots
    },
    
    -- Boss defeats (battle IDs)
    bosses = {
        ["Boss_Midgardsormr"] = {location_id = 770004001, name = "Boss: Midgardsormr"},
        ["Boss_Bottomswell"] = {location_id = 770004002, name = "Boss: Bottomswell"},
        -- ... more bosses
    },
    
    -- Colosseum battles
    colosseum = {
        [1] = {location_id = 770005001, name = "Colosseum: Battle 1"},
        [2] = {location_id = 770005002, name = "Colosseum: Battle 2"},
        -- ... more battles
    },
}

-- ============================================================================
-- State Tracking
-- ============================================================================

local State = {
    Initialized = false,
    CheckedLocations = {},  -- Set of checked location IDs
    LastStoryFlags = {},    -- Track previous state
    LastBattleId = nil,
    LastShopState = {},
}

-- ============================================================================
-- Location Detection
-- ============================================================================

---Check if a story flag was just set
---@param flag_id number
---@return boolean
local function CheckStoryFlag(flag_id)
    -- TODO: Use GameState.lua API to read ResidentWork/StoryFlags
    -- For now, placeholder
    return false
end

---Detect field item pickup by watching inventory changes
---@return string|nil item_key if an item was picked up
local function DetectFieldItemPickup()
    -- TODO: Hook into game's item pickup system
    -- Watch for inventory changes and cross-reference with map position
    return nil
end

---Detect shop purchase
---@return string|nil shop_key if something was purchased
local function DetectShopPurchase()
    -- TODO: Hook shop purchase events
    -- Track which shop slot was purchased
    return nil
end

---Detect battle completion
---@return string|nil battle_key if a battle was won
local function DetectBattleWin()
    -- TODO: Watch battle state changes
    -- Check if boss/colosseum battle completed
    return nil
end

-- ============================================================================
-- Location Checking
-- ============================================================================

---Mark a location as checked and write to file
---@param location_id number Archipelago location ID
---@param location_name string Human-readable name
local function CheckLocation(location_id, location_name)
    if State.CheckedLocations[location_id] then
        return  -- Already checked
    end
    
    print(string.format("[LocationTracker] Checked: %s (ID: %d)", location_name, location_id))
    
    State.CheckedLocations[location_id] = true
    
    -- Write to file for AP bridge to process
    local file = io.open(CHECKED_FILE, "a")
    if file then
        file:write(string.format("%d\n", location_id))
        file:close()
    else
        print("[LocationTracker] ERROR: Could not write to checked_locations.txt")
    end
end

-- ============================================================================
-- Main Polling Loop
-- ============================================================================

local function PollLocations()
    -- Check story flags
    for flag_id, location_data in pairs(LocationDatabase.story_flags) do
        if CheckStoryFlag(flag_id) then
            CheckLocation(location_data.location_id, location_data.name)
        end
    end
    
    -- Check field items
    local picked_item = DetectFieldItemPickup()
    if picked_item and LocationDatabase.field_items[picked_item] then
        local loc = LocationDatabase.field_items[picked_item]
        CheckLocation(loc.location_id, loc.name)
    end
    
    -- Check shop purchases
    local shop_purchase = DetectShopPurchase()
    if shop_purchase and LocationDatabase.shop_items[shop_purchase] then
        local loc = LocationDatabase.shop_items[shop_purchase]
        CheckLocation(loc.location_id, loc.name)
    end
    
    -- Check battles
    local battle_won = DetectBattleWin()
    if battle_won then
        local loc = LocationDatabase.bosses[battle_won] or LocationDatabase.colosseum[battle_won]
        if loc then
            CheckLocation(loc.location_id, loc.name)
        end
    end
end

-- ============================================================================
-- Public API
-- ============================================================================

function LocationTracker.Initialize()
    if State.Initialized then return end
    
    print("[LocationTracker] Initializing...")
    
    -- Load location database from file
    -- TODO: Load from ap_locations.json
    
    -- Clear checked file
    local file = io.open(CHECKED_FILE, "w")
    if file then
        file:close()
    end
    
    State.Initialized = true
    print("[LocationTracker] Ready!")
end

function LocationTracker.Update()
    if not State.Initialized then return end
    PollLocations()
end

function LocationTracker.GetCheckedCount()
    local count = 0
    for _ in pairs(State.CheckedLocations) do
        count = count + 1
    end
    return count
end

return LocationTracker
