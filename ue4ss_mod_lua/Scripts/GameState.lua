--[[
    GameState.lua
    Interface to FFVII Rebirth's game state
    
    Handles reading game memory, detecting events, and triggering game actions.
    
    Key Game APIs discovered from UE4SS Live View:
    - EndDataBaseDataBaseAPI: Core data access (items, flags, work variables)
    - EndBattleAPI: Battle system hooks
    - EndMenuBPAPI: Player stats access
    - EndFieldAPI: Field/map events
    - EndPartyAPI: Party management
]]

local GameState = {}

-- Location ID base (must match APWorld)
local BASE_ID = 770000
local LOCATION_OFFSET = 1000  -- Locations start at BASE_ID + 1000

-- Internal state
local State = {
    Initialized = false,
    GameLoaded = false,
    CurrentMap = "Unknown",
    CurrentChapter = 0,
    APITestsRun = false,  -- Track if we've run API tests
    PlayerSpawnTime = nil,  -- Track when player spawned for delayed tests
    
    -- Location tracking
    CheckedLocations = {},
    PendingChecks = {},
    
    -- Work variable caching (to detect changes)
    CachedResidentWork = {},
    CachedLocationWork = {},
    CachedStoryFlags = {},
    
    -- Death tracking
    LastDeathCheck = false,
    PlayerDead = false,
    
    -- Goal tracking
    GoalComplete = false,
    
    -- Slot data settings
    SlotData = {},
    
    -- API References (cached after first lookup)
    APIs = {
        DataBaseAPI = nil,
        DataObjectAPI = nil,
        BattleAPI = nil,
        MenuBPAPI = nil,
        FieldAPI = nil,
        PartyAPI = nil,
    },
}

-- ============================================================================
-- Utility Functions
-- ============================================================================

local function Log(msg)
    print(string.format("[GameState] %s", msg))
end

local function LogDebug(msg)
    print(string.format("[GameState][DEBUG] %s", msg))
end

-- ============================================================================
-- FFVII Rebirth API Access
-- ============================================================================

---Get the EndDataBaseDataBaseAPI singleton
---Key functions: GetItemNumBP, IsStoryFlag, SetStoryFlagBP, Get/SetResidentWorkInteger, etc.
---@return userdata|nil
local function GetDataBaseAPI()
    if State.APIs.DataBaseAPI then
        return State.APIs.DataBaseAPI
    end
    
    -- Try to find the API class default object
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
    end)
    
    if success and api then
        State.APIs.DataBaseAPI = api
        LogDebug("Found EndDataBaseDataBaseAPI")
        return api
    end
    
    return nil
end

---Get the EndMenuBPAPI for player stat access
---Key functions: BPGetPlayerHP, BPSetPlayerHP, BPGetPlayerLevel, etc.
---@return userdata|nil
local function GetMenuBPAPI()
    if State.APIs.MenuBPAPI then
        return State.APIs.MenuBPAPI
    end
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndGame.Default__EndMenuBPAPI")
    end)
    
    if success and api then
        State.APIs.MenuBPAPI = api
        LogDebug("Found EndMenuBPAPI")
        return api
    end
    
    return nil
end

---Get the EndBattleAPI for battle hooks
---@return userdata|nil
local function GetBattleAPI()
    if State.APIs.BattleAPI then
        return State.APIs.BattleAPI
    end
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndGame.Default__EndBattleAPI")
    end)
    
    if success and api then
        State.APIs.BattleAPI = api
        LogDebug("Found EndBattleAPI")
        return api
    end
    
    return nil
end

---Get the EndPartyAPI for party management
---@return userdata|nil
local function GetPartyAPI()
    if State.APIs.PartyAPI then
        return State.APIs.PartyAPI
    end
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndGame.Default__EndPartyAPI")
    end)
    
    if success and api then
        State.APIs.PartyAPI = api
        LogDebug("Found EndPartyAPI")
        return api
    end
    
    return nil
end

---Get the EndFieldAPI for field/trigger access
---@return userdata|nil
local function GetFieldAPI()
    if State.APIs.FieldAPI then
        return State.APIs.FieldAPI
    end
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndGame.Default__EndFieldAPI")
    end)
    
    if success and api then
        State.APIs.FieldAPI = api
        LogDebug("Found EndFieldAPI")
        return api
    end
    
    return nil
end

-- ============================================================================
-- Game Data Access Functions
-- ============================================================================

---Get the count of a specific item in inventory
---@param itemId string|number Item identifier (DataTable ID or name)
---@return number Item count, or -1 if failed
function GameState.GetItemCount(itemId)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("GetItemCount: API not available")
        return -1
    end
    
    local success, count = pcall(function()
        return api:GetItemNumBP(itemId)
    end)
    
    if success then
        return count or 0
    end
    
    LogDebug(string.format("GetItemCount(%s) failed", tostring(itemId)))
    return -1
end

---Check if a story flag is set
---@param flagName string Story flag identifier
---@return boolean|nil True if set, false if not, nil if failed
function GameState.IsStoryFlag(flagName)
    local api = GetDataBaseAPI()
    if not api then
        return nil
    end
    
    local success, result = pcall(function()
        local fname = FName(flagName)
        return api:IsStoryFlag(fname)
    end)
    
    if success then
        return result
    end
    
    return nil
end

---Set a story flag
---@param flagName string Story flag identifier
---@param value boolean Value to set
---@return boolean Success
function GameState.SetStoryFlag(flagName, value)
    local api = GetDataBaseAPI()
    if not api then
        LogDebug("SetStoryFlag: API not available")
        return false
    end
    
    local success = pcall(function()
        local fname = FName(flagName)
        api:SetStoryFlagBP(fname, value)
    end)
    
    if success then
        Log(string.format("Set story flag %s = %s", flagName, tostring(value)))
    end
    
    return success
end

---Get a persistent work variable (integer)
---These are saved with the game and persist across sessions
---@param workId string Work variable identifier
---@return number|nil Value, or nil if failed
function GameState.GetResidentWorkInteger(workId)
    local api = GetDataBaseAPI()
    if not api then
        return nil
    end
    
    local success, value = pcall(function()
        local fname = FName(workId)
        return api:GetResidentWorkInteger(fname)
    end)
    
    if success then
        return value
    end
    
    return nil
end

---Set a persistent work variable (integer)
---@param workId string Work variable identifier
---@param value number Value to set
---@return boolean Success
function GameState.SetResidentWorkInteger(workId, value)
    local api = GetDataBaseAPI()
    if not api then
        return false
    end
    
    local success = pcall(function()
        local fname = FName(workId)
        api:SetResidentWorkInteger(fname, value)
    end)
    
    if success then
        Log(string.format("Set work variable %s = %d", workId, value))
    end
    
    return success
end

---Get a location-specific work variable (integer)
---These reset when leaving the area
---@param workId string|number Work variable identifier
---@return number|nil Value, or nil if failed
function GameState.GetLocationWorkInteger(workId)
    local api = GetDataBaseAPI()
    if not api then
        return nil
    end
    
    local success, value = pcall(function()
        return api:GetLocationWorkInteger(workId)
    end)
    
    if success then
        return value
    end
    
    return nil
end

---Get current chapter progress
---@return number Chapter number (1-based), or 0 if failed
function GameState.GetChapterProgress()
    local api = GetDataBaseAPI()
    if not api then
        return 0
    end
    
    local success, chapter = pcall(function()
        return api:GetChapterProgress()
    end)
    
    if success then
        State.CurrentChapter = chapter or 0
        return State.CurrentChapter
    end
    
    return 0
end

---Get player position in world
---@return table|nil {x, y, z} or nil if failed
function GameState.GetPlayerPosition()
    local api = GetDataBaseAPI()
    if not api then
        return nil
    end
    
    local success, pos = pcall(function()
        return api:GetPlayerPosition()
    end)
    
    if success and pos then
        return {x = pos.X, y = pos.Y, z = pos.Z}
    end
    
    return nil
end

-- ============================================================================
-- Player Stats Access (via EndMenuBPAPI)
-- ============================================================================

---Get player HP
---@param playerType number Player type/index (0 = Cloud, etc.)
---@return number|nil Current HP, or nil if failed
function GameState.GetPlayerHP(playerType)
    local api = GetMenuBPAPI()
    if not api then
        return nil
    end
    
    local success, hp = pcall(function()
        return api:BPGetPlayerHP(playerType)
    end)
    
    if success then
        return hp
    end
    
    return nil
end

---Get player max HP
---@param playerType number Player type/index
---@return number|nil Max HP, or nil if failed
function GameState.GetPlayerMaxHP(playerType)
    local api = GetMenuBPAPI()
    if not api then
        return nil
    end
    
    local success, hp = pcall(function()
        return api:BPGetPlayerHPMax(playerType)
    end)
    
    if success then
        return hp
    end
    
    return nil
end

---Set player HP
---@param playerType number Player type/index
---@param hp number HP value to set
---@return boolean Success
function GameState.SetPlayerHP(playerType, hp)
    local api = GetMenuBPAPI()
    if not api then
        return false
    end
    
    local success = pcall(function()
        api:BPSetPlayerHP(playerType, hp)
    end)
    
    return success
end

---Get player level
---@param playerType number Player type/index
---@return number|nil Level, or nil if failed
function GameState.GetPlayerLevel(playerType)
    local api = GetMenuBPAPI()
    if not api then
        return nil
    end
    
    local success, level = pcall(function()
        return api:BPGetPlayerLevel(playerType)
    end)
    
    if success then
        return level
    end
    
    return nil
end

-- ============================================================================
-- Game State Detection
-- ============================================================================

---Check if the game world is loaded and playable
---@return boolean
function GameState.IsGameLoaded()
    -- Check if we can access the DataBase API and get chapter progress
    local chapter = GameState.GetChapterProgress()
    if chapter and chapter > 0 then
        State.GameLoaded = true
        return true
    end
    
    -- Fallback: try to get player position
    local pos = GameState.GetPlayerPosition()
    if pos then
        State.GameLoaded = true
        return true
    end
    
    State.GameLoaded = false
    return false
end

---Get the current map/area name
---@return string
function GameState.GetCurrentMap()
    -- Try to get from DataObject API
    local api = GetDataBaseAPI()
    if api then
        local success, name = pcall(function()
            -- GetLocationNameDetails or similar
            return "Unknown"  -- TODO: Find correct function
        end)
    end
    
    return State.CurrentMap
end

---Called when player spawns/respawns
function GameState.OnPlayerSpawn()
    LogDebug("Player spawned")
    State.PlayerDead = false
    State.LastDeathCheck = false
end

-- ============================================================================
-- Location Check Detection
-- Work variables and story flags are the primary way to detect completion
-- ============================================================================

-- Location type mappings - these need to be filled in based on game research
-- Format: {workVariableId = apLocationId, ...}
local LocationWorkMappings = {
    -- Example: Quest completion flags stored in ResidentWork
    -- ["QUEST_001_COMPLETE"] = 1001,
    -- ["CHEST_SECTOR5_01"] = 2001,
}

-- Story flag mappings for key events
local StoryFlagMappings = {
    -- Example: Story progression flags
    -- ["CHAPTER_1_COMPLETE"] = 3001,
    -- ["BOSS_SCORPION_DEFEATED"] = 4001,
}

-- ============================================================================
-- Location Checking
-- ============================================================================

---Register that a location was checked (by game ID)
---@param gameLocationId number The in-game identifier
function GameState.MarkLocationChecked(gameLocationId)
    -- Convert game ID to AP location ID
    local apLocationId = BASE_ID + LOCATION_OFFSET + gameLocationId
    
    if not State.CheckedLocations[apLocationId] then
        State.CheckedLocations[apLocationId] = true
        table.insert(State.PendingChecks, apLocationId)
        Log(string.format("Location checked: %d (AP: %d)", gameLocationId, apLocationId))
    end
end

---Get new location checks since last call
---@return table Array of AP location IDs
function GameState.GetNewLocationChecks()
    local checks = State.PendingChecks
    State.PendingChecks = {}
    return checks
end

---Get all checked locations
---@return table
function GameState.GetCheckedLocations()
    local result = {}
    for id, _ in pairs(State.CheckedLocations) do
        table.insert(result, {id = id, name = string.format("Location_%d", id)})
    end
    return result
end

---Get count of checked locations
---@return number
function GameState.GetCheckedCount()
    local count = 0
    for _ in pairs(State.CheckedLocations) do
        count = count + 1
    end
    return count
end

---Scan for newly completed locations
---Checks work variables and story flags for changes
---@return table Array of new location checks
function GameState.ScanForLocationChecks()
    if not GameState.IsGameLoaded() then
        return {}
    end
    
    -- Scan story flags for changes
    for flagName, apLocationId in pairs(StoryFlagMappings) do
        local currentValue = GameState.IsStoryFlag(flagName)
        local cachedValue = State.CachedStoryFlags[flagName]
        
        -- Detect flag becoming true
        if currentValue == true and cachedValue ~= true then
            if not State.CheckedLocations[apLocationId] then
                Log(string.format("Story flag triggered: %s -> Location %d", flagName, apLocationId))
                GameState.MarkLocationChecked(apLocationId - BASE_ID - LOCATION_OFFSET)
            end
        end
        
        State.CachedStoryFlags[flagName] = currentValue
    end
    
    -- Scan resident work variables for changes
    for workId, apLocationId in pairs(LocationWorkMappings) do
        local currentValue = GameState.GetResidentWorkInteger(workId)
        local cachedValue = State.CachedResidentWork[workId]
        
        -- Detect value becoming non-zero (completed)
        if currentValue and currentValue > 0 and (not cachedValue or cachedValue == 0) then
            if not State.CheckedLocations[apLocationId] then
                Log(string.format("Work variable triggered: %s=%d -> Location %d", workId, currentValue, apLocationId))
                GameState.MarkLocationChecked(apLocationId - BASE_ID - LOCATION_OFFSET)
            end
        end
        
        State.CachedResidentWork[workId] = currentValue
    end
    
    -- Check for chapter progress (special handling)
    local chapter = GameState.GetChapterProgress()
    if chapter > State.CurrentChapter then
        Log(string.format("Chapter progress: %d -> %d", State.CurrentChapter, chapter))
        -- Could trigger chapter completion locations here
        State.CurrentChapter = chapter
    end
    
    return GameState.GetNewLocationChecks()
end

-- ============================================================================
-- Death Detection (for DeathLink)
-- ============================================================================

---Check if player has died since last check
---Uses party HP checks to detect game over state
---@return boolean True if new death detected
function GameState.CheckPlayerDeath()
    -- Check if all party members are dead (HP = 0)
    local partyApi = GetPartyAPI()
    if partyApi then
        local success, count = pcall(function()
            return partyApi:GetAliveBattleMemberCount()
        end)
        
        if success and count == 0 then
            -- All party members dead = game over
            if not State.LastDeathCheck then
                State.LastDeathCheck = true
                State.PlayerDead = true
                return true
            end
        else
            State.LastDeathCheck = false
            State.PlayerDead = false
        end
    end
    
    return false
end

---Trigger player death (called when receiving DeathLink)
---Sets all party member HP to 0
function GameState.TriggerDeath()
    Log("DeathLink received - triggering game over")
    
    -- Try to set all party members HP to 0
    local menuApi = GetMenuBPAPI()
    if menuApi then
        -- Player types: 0=Cloud, 1=Barret, 2=Tifa, 3=Aerith, 4=Red XIII, 5=Yuffie, 6=Cait Sith, 7=Cid, 8=Vincent
        for playerType = 0, 8 do
            local success = pcall(function()
                menuApi:BPSetPlayerHP(playerType, 0)
            end)
            if success then
                LogDebug(string.format("Set player %d HP to 0", playerType))
            end
        end
    else
        Log("Warning: Could not trigger death - MenuBPAPI not available")
    end
end

-- ============================================================================
-- Goal Completion
-- ============================================================================

---Check if the game goal is complete
---@return boolean
function GameState.CheckGoalComplete()
    -- TODO: Implement goal detection
    -- For FFVII Rebirth, this might be:
    -- - Defeating the final boss
    -- - Reaching a certain chapter
    -- - Completing specific objectives
    
    return State.GoalComplete
end

---Mark goal as complete
function GameState.SetGoalComplete()
    State.GoalComplete = true
    Log("Goal marked as complete!")
end

-- ============================================================================
-- Debug / Testing Functions
-- ============================================================================

-- ============================================================================
-- Debug / Testing Functions
-- ============================================================================

---Test all API functions to determine which are working
---Useful for in-game debugging and API discovery
function GameState.TestAllAPIs()
    Log("=== FFVII Rebirth API Test ===")
    
    -- Test DataBase API
    Log("--- DataBase API ---")
    local dbApi = GetDataBaseAPI()
    if dbApi then
        Log("  DataBase API object found")
        
        -- Test 1: GetItemNumBP
        Log("  [TEST 1] Calling GetItemNumBP('ITEM_POTION')...")
        local success, result = pcall(function() 
            return dbApi:GetItemNumBP("ITEM_POTION") 
        end)
        Log(string.format("  [TEST 1] Result: success=%s, value=%s", tostring(success), tostring(result)))
        
        -- Test 2: IsStoryFlag - try with FName
        Log("  [TEST 2] Testing IsStoryFlag with FName...")
        if dbApi.IsStoryFlag then
            local flags = {"STORY_001", "CHAPTER_1", "BOSS_DEFEATED"}
            for _, flagName in ipairs(flags) do
                success, result = pcall(function()
                    local fname = FName(flagName)
                    return dbApi:IsStoryFlag(fname)
                end)
                Log(string.format("  [TEST 2] IsStoryFlag(FName('%s')): success=%s, value=%s", 
                    flagName, tostring(success), tostring(result)))
            end
        else
            Log("  [TEST 2] IsStoryFlag method does not exist")
        end
        
        -- Test 3: GetResidentWorkInteger - SUCCESS with FName!
        Log("  [TEST 3] Testing GetResidentWorkInteger with FName...")
        if dbApi.GetResidentWorkInteger then
            -- Test multiple work variables with FName
            local workVars = {"GIL", "CHAPTER", "PLAYTIME"}
            for _, varName in ipairs(workVars) do
                success, result = pcall(function()
                    local fname = FName(varName)
                    return dbApi:GetResidentWorkInteger(fname)
                end)
                Log(string.format("  [TEST 3] GetResidentWorkInteger(FName('%s')): success=%s, value=%s", 
                    varName, tostring(success), tostring(result)))
            end
        else
            Log("  [TEST 3] GetResidentWorkInteger method does not exist")
        end
        
        -- Test 4: GetChapterProgress - check if method exists first
        Log("  [TEST 4] Checking if GetChapterProgress exists...")
        if dbApi.GetChapterProgress then
            Log("  [TEST 4] Method exists, calling GetChapterProgress()...")
            success, result = pcall(function() 
                return dbApi:GetChapterProgress()
            end)
            Log(string.format("  [TEST 4] Result: success=%s, value=%s", tostring(success), tostring(result)))
        else
            Log("  [TEST 4] GetChapterProgress method does not exist on API object")
        end
        
    else
        Log("  DataBase API not available!")
    end
    
    -- Test Menu BP API  
    Log("--- Menu BP API ---")
    local menuApi = GetMenuBPAPI()
    if menuApi then
        Log("  Menu BP API object found")
        
        -- Test 5: BPGetPlayerHP - check if method exists first
        Log("  [TEST 5] Checking if BPGetPlayerHP exists...")
        if menuApi.BPGetPlayerHP then
            Log("  [TEST 5] Method exists, calling BPGetPlayerHP(0)...")
            local success, result = pcall(function() 
                return menuApi:BPGetPlayerHP(0)
            end)
            Log(string.format("  [TEST 5] Result: success=%s, value=%s", tostring(success), tostring(result)))
        else
            Log("  [TEST 5] BPGetPlayerHP method does not exist on API object")
        end
    else
        Log("  Menu BP API not available!")
    end
    
    -- Test Party API
    Log("--- Party API ---")
    local partyApi = GetPartyAPI()
    if partyApi then
        Log("  Party API object found")
        
        -- Test 6: GetAliveBattleMemberCount - check if method exists first
        Log("  [TEST 6] Checking if GetAliveBattleMemberCount exists...")
        if partyApi.GetAliveBattleMemberCount then
            Log("  [TEST 6] Method exists, calling GetAliveBattleMemberCount()...")
            local success, result = pcall(function()
                -- Check if object is valid before calling
                if partyApi:IsValid() then
                    return partyApi:GetAliveBattleMemberCount()
                else
                    return "PartyAPI object is not valid (nullptr)"
                end
            end)
            Log(string.format("  [TEST 6] Result: success=%s, value=%s", tostring(success), tostring(result)))
        else
            Log("  [TEST 6] GetAliveBattleMemberCount method does not exist on API object")
        end
    else
        Log("  Party API not available!")
    end
    
    -- Test SET functions
    Log("--- Testing SET Functions ---")
    local dbApi = GetDataBaseAPI()
    if dbApi then
        -- Test 7: SetResidentWorkInteger - create a test variable
        Log("  [TEST 7] Testing SetResidentWorkInteger...")
        local testVarName = "AP_TEST_VAR"
        local testValue = 12345
        local success = pcall(function()
            local fname = FName(testVarName)
            dbApi:SetResidentWorkInteger(fname, testValue)
        end)
        Log(string.format("  [TEST 7] SetResidentWorkInteger(FName('%s'), %d): success=%s", 
            testVarName, testValue, tostring(success)))
        
        -- Read it back to verify
        if success then
            local readSuccess, readValue = pcall(function()
                local fname = FName(testVarName)
                return dbApi:GetResidentWorkInteger(fname)
            end)
            Log(string.format("  [TEST 7] Read back: success=%s, value=%s (expected %d)", 
                tostring(readSuccess), tostring(readValue), testValue))
        end
        
        -- Test 8: SetStoryFlagBP
        Log("  [TEST 8] Testing SetStoryFlagBP...")
        local testFlagName = "AP_TEST_FLAG"
        success = pcall(function()
            local fname = FName(testFlagName)
            dbApi:SetStoryFlagBP(fname, true)
        end)
        Log(string.format("  [TEST 8] SetStoryFlagBP(FName('%s'), true): success=%s", 
            testFlagName, tostring(success)))
        
        -- Read it back to verify
        if success then
            local readSuccess, readValue = pcall(function()
                local fname = FName(testFlagName)
                return dbApi:IsStoryFlag(fname)
            end)
            Log(string.format("  [TEST 8] Read back: success=%s, value=%s (expected true)", 
                tostring(readSuccess), tostring(readValue)))
        end
    end
    
    Log("=== End API Test ===")
end

---Advanced test: Explore save data structure and test item manipulation
---This function attempts to find where item data is stored and manipulate it
function GameState.TestItemManipulation()
    Log("=== Item Manipulation Test ===")
    
    -- First, let's get current item count for reference
    local dbApi = GetDataBaseAPI()
    if not dbApi then
        Log("ERROR: DataBase API not available")
        return
    end
    
    -- Test getting item count for a known item (Potion = ID 4000001 or similar)
    -- The actual IDs need to be discovered from game data
    local testItemIds = {4000001, 4000002, 4000003, 1, 2, 100, 1000}
    Log("--- Reading item counts for various IDs ---")
    for _, itemId in ipairs(testItemIds) do
        local success, count = pcall(function()
            return dbApi:GetItemNumBP(itemId)
        end)
        if success and count and count > 0 then
            Log(string.format("  ItemID %d: count = %d", itemId, count))
        end
    end

    -- Snapshot and diff a range of numeric IDs to detect changes across runs
    Log("--- Snapshotting numeric item ID range (1..200) ---")
    local function SnapshotItemCounts(maxId)
        local counts = {}
        for i = 1, maxId do
            local ok, count = pcall(function()
                return dbApi:GetItemNumBP(i)
            end)
            if ok then
                counts[i] = count
            end
        end
        return counts
    end

    if not GameState.ItemCountBaseline then
        GameState.ItemCountBaseline = SnapshotItemCounts(200)
        Log("  Baseline stored (run F9 again after picking up an item to see diffs)")
    else
        local newCounts = SnapshotItemCounts(200)
        local diffs = 0
        for i = 1, 200 do
            local oldVal = GameState.ItemCountBaseline[i]
            local newVal = newCounts[i]
            if oldVal ~= newVal then
                Log(string.format("  ID %d changed: %s -> %s", i, tostring(oldVal), tostring(newVal)))
                diffs = diffs + 1
            end
        end
        if diffs == 0 then
            Log("  No changes detected in IDs 1..200")
        else
            Log(string.format("  Total changes detected: %d", diffs))
        end
        GameState.ItemCountBaseline = newCounts
    end

    -- Scan item_names.json for any nonzero counts to discover valid item IDs
    Log("--- Scanning item_names.json for nonzero counts ---")
    local function LoadJsonFile(path)
        local ok, jsonModule = pcall(function()
            return require("json")
        end)
        if not ok or not jsonModule then
            Log("  json module not available")
            return nil
        end
        local file = io.open(path, "r")
        if not file then
            Log("  Could not open item_names.json at: " .. path)
            return nil
        end
        local content = file:read("*a")
        file:close()
        local okParse, data = pcall(function()
            return jsonModule.decode(content)
        end)
        if not okParse then
            Log("  Failed to parse item_names.json")
            return nil
        end
        return data
    end

    local itemNamesPath = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\worlds\\finalfantasy_rebirth\\data\\exports\\item_names.json"
    local itemNameMap = LoadJsonFile(itemNamesPath)
    if itemNameMap then
        local checked = 0
        local found = 0
        for itemName, _ in pairs(itemNameMap) do
            checked = checked + 1
            local okCount, count = pcall(function()
                return dbApi:GetItemNumBP(itemName)
            end)
            if okCount and count and count > 0 then
                Log(string.format("  %s: count = %d", itemName, count))
                found = found + 1
                if found >= 10 then
                    Log("  ...found 10 items, stopping scan")
                    break
                end
            end
            if checked >= 300 then
                Log("  ...scanned 300 items, stopping scan")
                break
            end
        end
        if found == 0 then
            Log("  No nonzero counts found in first 300 item names")
        end
    end
    
    -- Try to find save data objects
    Log("--- Searching for save data objects ---")
    
    -- Try EndSaveGame
    local saveGame = nil
    local success, result = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndSaveGame")
    end)
    if success and result and result:IsValid() then
        saveGame = result
        Log("  Found EndSaveGame default object")
        Log(string.format("    Address: 0x%X", saveGame:GetAddress()))
    else
        Log("  EndSaveGame default object not found or invalid")
    end
    
    -- Try to find EndOneSaveDataManager instance
    local saveManager = nil
    success, result = pcall(function()
        return FindFirstOf("EndOneSaveDataManager")
    end)
    if success and result and result:IsValid() then
        saveManager = result
        Log("  Found EndOneSaveDataManager instance!")
        Log(string.format("    Address: 0x%X", saveManager:GetAddress()))
        Log(string.format("    FullName: %s", saveManager:GetFullName()))
        
        -- Try to explore its properties
        local reflection = saveManager:Reflection()
        if reflection then
            Log("    Got reflection object")
        end
    else
        Log("  EndOneSaveDataManager instance not found")
    end
    
    -- Try to find EndItemAPI
    local itemApi = nil
    success, result = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndItemAPI")
    end)
    if success and result and result:IsValid() then
        itemApi = result
        Log("  Found EndItemAPI default object")
        Log(string.format("    Address: 0x%X", itemApi:GetAddress()))
    else
        Log("  EndItemAPI not found")
    end
    
    -- Try KismetSystemLibrary:SetIntPropertyByName
    Log("--- Testing SetIntPropertyByName ---")
    local kismetLib = nil
    success, result = pcall(function()
        return StaticFindObject("/Script/Engine.Default__KismetSystemLibrary")
    end)
    if success and result and result:IsValid() then
        kismetLib = result
        Log("  Found KismetSystemLibrary")
        
        -- Try to call SetIntPropertyByName on a test object
        -- This needs an object with an int property to modify
    else
        Log("  KismetSystemLibrary not found")
    end
    
    -- Try SendStateTriggerByName via EndFieldAPI
    Log("--- Testing SendStateTriggerByName ---")
    local fieldApi = GetFieldAPI()
    if fieldApi and fieldApi:IsValid() then
        Log("  Found EndFieldAPI")
        
        -- Try sending a test trigger
        local testTrigger = "AP_TEST_TRIGGER"
        success = pcall(function()
            local fname = FName(testTrigger)
            fieldApi:SendStateTriggerByName(fname)
        end)
        Log(string.format("  SendStateTriggerByName('%s'): %s", testTrigger, tostring(success)))
    else
        Log("  EndFieldAPI not available or invalid")
    end
    
    -- Try ExecuteConsoleCommand via KismetSystemLibrary
    Log("--- Testing ExecuteConsoleCommand ---")
    if kismetLib and kismetLib:IsValid() then
        -- Get world context
        local world = nil
        local pc = FindFirstOf("PlayerController")
        if pc and pc:IsValid() then
            world = pc:GetWorld()
        end
        
        if world and world:IsValid() then
            -- Common debug commands that might work
            local testCommands = {
                "stat fps",
                "showflag.volumes 1",
                -- Try item commands (these are guesses based on common UE patterns)
                "giveitem 1 10",
                "additem 1 10",
                "item.add 1 10",
                "player.additem 1 10",
                -- Try gil/money commands
                "givegil 1000",
                "addgil 1000",
                "gil.add 1000",
                "player.addgil 1000"
            }
            for _, cmd in ipairs(testCommands) do
                success = pcall(function()
                    kismetLib:ExecuteConsoleCommand(world, cmd, nil)
                end)
                Log(string.format("  ExecuteConsoleCommand('%s'): %s", cmd, tostring(success)))
            end
            
            -- After trying commands, check if item count changed
            Log("  Checking if item counts changed...")
            local afterCount = dbApi:GetItemNumBP(1)
            Log(string.format("  ItemID 1 after console commands: %d", afterCount))
        else
            Log("  Could not get world context")
        end
    end
    
    -- Try direct property modification on save manager
    Log("--- Testing Direct Property Modification ---")
    if saveManager and saveManager:IsValid() then
        Log("  Save manager is valid, attempting property access...")

        local function DumpMetatableKeys(label, obj)
            pcall(function()
                local mt = getmetatable(obj)
                if not mt then
                    Log(string.format("    %s: no metatable", label))
                    return
                end
                Log(string.format("    %s: metatable keys:", label))
                local count = 0
                for k, _ in pairs(mt) do
                    Log(string.format("      %s", tostring(k)))
                    count = count + 1
                    if count >= 20 then
                        Log("      ... (truncated)")
                        break
                    end
                end
            end)
        end
        
        -- Try to list some common property names with better error handling
        local propNames = {"ItemData", "m_ItemData", "Items", "m_Items", "Inventory", "m_Inventory"}
        local itemDataObj = nil
        local foundCount = 0
        
        for _, propName in ipairs(propNames) do
            local success = pcall(function()
                local val = saveManager[propName]
                Log(string.format("    Checking %s: val=%s, type=%s", propName, tostring(val), type(val)))
                if val ~= nil then
                    local isValid = false
                    if val.IsValid then
                        isValid = val:IsValid()
                    end
                    Log(string.format("    %s found! IsValid=%s", propName, tostring(isValid)))
                    foundCount = foundCount + 1
                    if propName == "ItemData" then
                        itemDataObj = val
                    end
                else
                    Log(string.format("    %s is nil", propName))
                end
            end)
            if not success then
                Log(string.format("    ERROR accessing %s", propName))
            end
        end
        
        Log(string.format("  Found %d properties", foundCount))
        
        -- If we found ItemData, explore it
        if itemDataObj then
            Log("  Exploring ItemData object...")
            DumpMetatableKeys("ItemData", itemDataObj)
            
            -- ItemData supports indexed access! Let's explore what's inside
            Log("    Exploring indexed elements in ItemData...")
            for i = 1, 3 do
                local item = itemDataObj[i]
                if item then
                    Log(string.format("    ItemData[%d] properties:", i))
                    DumpMetatableKeys(string.format("ItemData[%d]", i), item)
                    
                    -- Try common property names on each indexed item
                    local props = {"Count", "m_Count", "Num", "m_Num", "Value", "m_Value", "Amount", "m_Amount", "ItemID", "ItemId", "ID", "m_ID"}
                    for _, propName in ipairs(props) do
                        pcall(function()
                            local val = item[propName]
                            if val ~= nil and type(val) == "number" then
                                Log(string.format("      [%d].%s = %d", i, propName, val))
                            elseif val ~= nil and val ~= 0 then
                                Log(string.format("      [%d].%s = %s (type: %s)", i, propName, tostring(val), type(val)))
                            end
                        end)
                    end

                    -- Try KismetSystemLibrary:GetIntPropertyByName on the item entry
                    if kismetLib and kismetLib.IsValid and kismetLib:IsValid() and item and item.IsValid and item:IsValid() then
                        local kProps = {"Count", "Num", "Amount", "ItemID", "ID"}
                        for _, kProp in ipairs(kProps) do
                            pcall(function()
                                local v = kismetLib:GetIntPropertyByName(item, FName(kProp))
                                Log(string.format("      [Kismet] %s = %s", kProp, tostring(v)))
                            end)
                        end
                    end
                end
            end
            
            -- Try the Items container with more detailed exploration
            Log("    Exploring Items container...")
            local items = saveManager["Items"]
            if items then
                for i = 1, 3 do
                    local item = items[i]
                    if item then
                        Log(string.format("    Items[%d] properties:", i))
                        local props = {"Count", "m_Count", "Num", "m_Num", "Value", "m_Value", "Amount", "m_Amount", "ItemID", "ItemId", "ID", "m_ID"}
                        for _, propName in ipairs(props) do
                            pcall(function()
                                local val = item[propName]
                                if val ~= nil and type(val) == "number" then
                                    Log(string.format("      Items[%d].%s = %d", i, propName, val))
                                elseif val ~= nil and val ~= 0 then
                                    Log(string.format("      Items[%d].%s = %s", i, propName, tostring(val)))
                                end
                            end)
                        end
                    end
                end
            end
            
            -- Try m_Items with detailed exploration
            Log("    Exploring m_Items container...")
            local mItems = saveManager["m_Items"]
            if mItems then
                -- First check if m_Items has properties like Data or Num
                local mItemsProps = {"Data", "m_Data"}
                local mItemsData = nil
                for _, propName in ipairs(mItemsProps) do
                    pcall(function()
                        local val = mItems[propName]
                        if val ~= nil then
                            Log(string.format("    m_Items.%s found", propName))
                            mItemsData = val
                        end
                    end)
                end
                
                -- If we found Data or m_Data, explore it
                if mItemsData then
                    Log("    Exploring m_Items.Data...")
                    for i = 1, 3 do
                        local item = mItemsData[i]
                        if item then
                            Log(string.format("    m_Items.Data[%d] properties:", i))
                            local props = {"Count", "m_Count", "Num", "m_Num", "Value", "m_Value", "Amount", "m_Amount"}
                            for _, propName in ipairs(props) do
                                pcall(function()
                                    local val = item[propName]
                                    if val ~= nil and type(val) == "number" then
                                        Log(string.format("      Data[%d].%s = %d", i, propName, val))
                                    end
                                end)
                            end
                        end
                    end
                end
            end
        else
            Log("  Could not find or access ItemData object")
        end
        
        -- Final check
        Log("  FINAL status check...")
        local finalCount = dbApi:GetItemNumBP(1)
        Log(string.format("  ItemID 1 count: %d (started at 819066)", finalCount))
        
        -- Try NEW APPROACH: Trigger item rewards through the treasure/reward system
        Log("")
        Log("--- Testing Treasure Reward Triggers ---")
        Log("  Trying to trigger reward-related state triggers...")

        -- Track some named items before/after (these exist in Reward.json)
        local itemNamesToCheck = {
            "IT_hpotion",
            "IT_potion",
            "IT_gpotion",
            "it_gil",
            "it_elixir",
        }

        local function LogItemCounts(prefix)
            Log(prefix)
            for _, itemName in ipairs(itemNamesToCheck) do
                local count = dbApi:GetItemNumBP(itemName)
                Log(string.format("  %s: %s", itemName, tostring(count)))
            end
        end

        LogItemCounts("  Item counts BEFORE triggers:")
        
        -- Try actual reward-related state trigger names from Reward.uasset
        local triggerNames = {
            "sctCmn_GetQuestReward_Qst02",
            "sctCmn_GetQuestReward_Qst05",
            "sctCmn_GetQuestReward_Qst18",
            "sctCmn_GetQuestReward_Qst24",
            "sctCmn_GetQuestReward_Qst25",
            "sctCmn_GetQuestReward_Qst27",
            "sctCmn_GetQuestReward_Qst32",
            "sctCmn_GetQuestReward_Qst36",
            "sctCmn_GetCardGameReward_Qst36",
            "sctCmn_check_Piano_Reward_AmorCard",
            "scnCmn_Reward_TournamentWinning",
            "scnCmn_Reward_NotTournamentWinning",
        }
        
        for _, triggerName in ipairs(triggerNames) do
            pcall(function()
                fieldApi:SendStateTriggerByName(FName(triggerName))
                Log(string.format("  SendStateTriggerByName('%s'): executed", triggerName))
            end)
        end

        LogItemCounts("  Item counts AFTER triggers:")
    else
        Log("  ERROR: Save manager not valid!")
    end
    
    Log("=== End Item Manipulation Test ===")
end

-- ============================================================================
-- Initialization
-- ============================================================================

---Apply slot data settings from AP server
---@param slotData table Slot data from server
function GameState.ApplySlotData(slotData)
    if not slotData then
        return
    end
    
    State.SlotData = slotData
    
    -- TODO: Apply game-specific settings based on slot data
    -- Examples:
    -- - Enemy randomization settings
    -- - Starting inventory
    -- - Difficulty modifiers
    
    LogDebug("Slot data applied")
end

-- ============================================================================
-- Additional Test Functions (for hotkeys)
-- ============================================================================

---Test GetItemNumBP with a range of IDs to understand the item ID mapping
function GameState.TestGetItemNumBP()
    Log("=== GetItemNumBP Test ===")
    
    local dbApi = GetDataBaseAPI()
    if not dbApi then
        Log("ERROR: DataBase API not available")
        return
    end

    -- Test different ID ranges based on game data structure
    local testRanges = {
        {name = "Low IDs", start = 1, stop = 50},
        {name = "100s", start = 100, stop = 150},
        {name = "1000s", start = 1000, stop = 1050},
        {name = "Consumables (4M)", start = 4000001, stop = 4000050},
        {name = "Weapons (1M)", start = 1000001, stop = 1000020},
        {name = "Armor (2M)", start = 2000001, stop = 2000020},
        {name = "Accessories (3M)", start = 3000001, stop = 3000020},
        {name = "Materia (5M)", start = 5000001, stop = 5000020},
    }

    for _, range in ipairs(testRanges) do
        Log(string.format("--- %s (%d - %d) ---", range.name, range.start, range.stop))
        local nonZeroCount = 0
        for id = range.start, range.stop do
            local success, count = pcall(function()
                return dbApi:GetItemNumBP(id)
            end)
            if success and count and count > 0 then
                Log(string.format("  ID %d = %d", id, count))
                nonZeroCount = nonZeroCount + 1
            end
        end
        if nonZeroCount == 0 then
            Log("  (all zero or failed)")
        end
    end

    Log("=== GetItemNumBP Test Complete ===")
end

---Enumerate all functions on a UObject using UE4SS reflection
---@param obj userdata The UObject to enumerate
---@param label string Label for logging
function GameState.EnumerateFunctions(obj, label)
    Log(string.format("=== Enumerating Functions on %s ===", label))
    
    if not obj or not obj:IsValid() then
        Log("  Object is nil or invalid")
        return {}
    end
    
    local fullName = obj:GetFullName()
    Log(string.format("  Object: %s", fullName))
    
    -- Get the class (UClass inherits from UStruct which has ForEachFunction)
    local class = obj:GetClass()
    if not class or not class:IsValid() then
        Log("  Could not get class")
        return {}
    end
    
    local className = class:GetFullName()
    Log(string.format("  Class: %s", className))
    
    -- Collect all functions
    local allFuncs = {}
    local interestingFuncs = {}
    
    -- Use ForEachFunction (inherited from UStruct)
    local success, err = pcall(function()
        class:ForEachFunction(function(func)
            local funcName = func:GetFName():ToString()
            table.insert(allFuncs, funcName)
            
            -- Filter for interesting functions
            local lowerName = string.lower(funcName)
            if string.find(lowerName, "item") or
               string.find(lowerName, "add") or
               string.find(lowerName, "give") or
               string.find(lowerName, "receive") or
               string.find(lowerName, "grant") or
               string.find(lowerName, "gain") or
               string.find(lowerName, "reward") or
               string.find(lowerName, "equip") or
               string.find(lowerName, "weapon") or
               string.find(lowerName, "materia") or
               string.find(lowerName, "gil") or
               string.find(lowerName, "money") or
               string.find(lowerName, "inventory") or
               string.find(lowerName, "set") then
                table.insert(interestingFuncs, {name = funcName, func = func})
            end
            
            return false -- continue iteration
        end)
    end)
    
    if not success then
        Log(string.format("  ForEachFunction error: %s", tostring(err)))
    end
    
    Log(string.format("  Total functions: %d", #allFuncs))
    Log(string.format("  Interesting functions: %d", #interestingFuncs))
    
    -- Log interesting functions
    for _, entry in ipairs(interestingFuncs) do
        Log(string.format("    [*] %s", entry.name))
    end
    
    -- Also enumerate properties
    local properties = {}
    success, err = pcall(function()
        class:ForEachProperty(function(prop)
            local propName = prop:GetFName():ToString()
            local lowerName = string.lower(propName)
            if string.find(lowerName, "item") or
               string.find(lowerName, "inventory") or
               string.find(lowerName, "gil") or
               string.find(lowerName, "money") then
                table.insert(properties, propName)
            end
            return false
        end)
    end)
    
    if #properties > 0 then
        Log(string.format("  Interesting properties: %d", #properties))
        for _, propName in ipairs(properties) do
            Log(string.format("    [P] %s", propName))
        end
    end
    
    return interestingFuncs
end

---Find and enumerate player character functions
function GameState.EnumeratePlayerCharacterFunctions()
    Log("=== Searching for Player Character ===")
    
    -- Try various player class names
    local playerClasses = {
        "EndPlayerCharacter",
        "EndCharacter", 
        "EndPlayerController",
        "PlayerController",
        "EndGameInstance",
        "EndGameMode"
    }
    
    for _, className in ipairs(playerClasses) do
        local success, obj = pcall(function()
            return FindFirstOf(className)
        end)
        
        if success and obj and obj:IsValid() then
            -- Skip default objects
            local fullName = obj:GetFullName()
            if not string.find(fullName, "Default__") then
                Log(string.format("Found: %s", className))
                GameState.EnumerateFunctions(obj, className)
            end
        end
    end
end

---Try calling functions via UE4SS CallFunction API
function GameState.TestCallFunction()
    Log("=== Testing CallFunction API ===")
    
    local dbApi = GetDataBaseAPI()
    if not dbApi or not dbApi:IsValid() then
        Log("ERROR: Database API not available")
        return
    end
    
    local class = dbApi:GetClass()
    if not class then
        Log("ERROR: Could not get class")
        return
    end
    
    -- Collect all functions and their signatures
    local allFuncs = {}
    pcall(function()
        class:ForEachFunction(function(func)
            local funcName = func:GetFName():ToString()
            table.insert(allFuncs, {name = funcName, func = func})
            return false
        end)
    end)
    
    Log(string.format("Total functions on EndDataBaseDataBaseAPI: %d", #allFuncs))
    
    -- Look for interesting functions
    local itemFuncs = {}
    for _, entry in ipairs(allFuncs) do
        local lowerName = string.lower(entry.name)
        if string.find(lowerName, "item") or
           string.find(lowerName, "add") or
           string.find(lowerName, "set") or
           string.find(lowerName, "gil") or
           string.find(lowerName, "money") then
            table.insert(itemFuncs, entry)
            Log(string.format("  Found: %s", entry.name))
        end
    end
    
    -- Test calling SetItem or AddItem style functions if they exist
    for _, entry in ipairs(itemFuncs) do
        local lowerName = string.lower(entry.name)
        
        -- Skip read-only functions we know about
        if string.find(lowerName, "get") or string.find(lowerName, "is") then
            -- Skip getters
        elseif string.find(lowerName, "setitem") or string.find(lowerName, "additem") then
            Log(string.format("  ** Trying to call: %s **", entry.name))
            
            -- Try calling with typical item parameters (ID=4000005 is a potion)
            local success, result = pcall(function()
                -- Method 1: Call via object:function
                return dbApi:CallFunction(entry.func, 4000005, 1)
            end)
            Log(string.format("    CallFunction(id=4000005, qty=1): success=%s, result=%s", 
                tostring(success), tostring(result)))
            
            -- Method 2: Direct call on function object
            success, result = pcall(function()
                return entry.func(dbApi, 4000005, 1)
            end)
            Log(string.format("    Direct call: success=%s, result=%s", 
                tostring(success), tostring(result)))
        end
    end
    
    -- Try to find and test any SetItemNumBP function
    Log("--- Looking for SetItemNum functions ---")
    for _, entry in ipairs(allFuncs) do
        if string.find(string.lower(entry.name), "setitemnum") then
            Log(string.format("  Found SetItemNum-style function: %s", entry.name))
            
            -- Try calling it
            local success, result = pcall(function()
                return entry.func(dbApi, 4000005, 99)
            end)
            Log(string.format("    Call attempt: success=%s, result=%s", 
                tostring(success), tostring(result)))
            
            -- Check if it worked
            local count = -1
            pcall(function()
                count = dbApi:GetItemNumBP(4000005)
            end)
            Log(string.format("    GetItemNumBP(4000005) after: %d", count))
        end
    end
    
    -- Test BlueprintCallable functions
    Log("--- Testing via direct method access ---")
    
    -- Try accessing methods directly on the object
    local testMethods = {"AddItem", "SetItem", "GiveItem", "GrantItem", "AddItemBP", "SetItemBP", "AddItemNumBP", "SetItemNumBP"}
    for _, methodName in ipairs(testMethods) do
        local success, method = pcall(function()
            return dbApi[methodName]
        end)
        if success and method then
            Log(string.format("  Found method via indexer: %s (type=%s)", methodName, type(method)))
            
            -- Try calling it
            success, result = pcall(function()
                if type(method) == "function" then
                    return method(dbApi, 4000005, 1)
                elseif type(method) == "userdata" then
                    return dbApi:CallFunction(method, 4000005, 1)
                end
            end)
            Log(string.format("    Call result: success=%s, result=%s", 
                tostring(success), tostring(result)))
        end
    end
    
    Log("=== CallFunction Test Complete ===")
end

---Comprehensive test: Find any object with item-granting capability
function GameState.TestFindItemGranter()
    Log("=== Searching for Item Granting Objects ===")
    
    -- Objects that might have item-granting functions
    local targetClasses = {
        -- Database APIs
        "EndDataBaseDataBaseAPI",
        "EndDataBaseAPI",
        "EndItemAPI",
        "EndPartyAPI", 
        "EndMenuAPI",
        "EndMenuBPAPI",
        "EndFieldAPI",
        
        -- Game instances and modes
        "EndGameInstance",
        "EndGameMode",
        "EndGameState",
        
        -- Player related
        "EndPlayerController",
        "EndPlayerCharacter",
        "EndPlayerState",
        
        -- Save/data managers
        "EndSaveGame",
        "EndOneSaveDataManager",
        "EndSaveDataManager",
        
        -- Inventory/item managers (guesses based on common patterns)
        "EndItemManager",
        "EndInventoryManager",
        "EndInventoryComponent",
        "EndItemComponent",
        "ItemManager",
        "InventoryManager",
        
        -- Party/character managers
        "EndPartyManager",
        "EndCharacterManager",
        
        -- Subsystems
        "EndGameInstanceSubsystem",
        "EndWorldSubsystem",
    }
    
    local foundObjects = {}
    
    for _, className in ipairs(targetClasses) do
        -- Try FindFirstOf
        local success, obj = pcall(function()
            return FindFirstOf(className)
        end)
        
        if success and obj and obj:IsValid() then
            local fullName = obj:GetFullName()
            if not string.find(fullName, "Default__") then
                Log(string.format("\n=== %s (instance) ===", className))
                Log(string.format("  Full name: %s", fullName))
                
                local funcs = GameState.EnumerateFunctions(obj, className)
                
                -- Store promising objects
                if #funcs > 0 then
                    table.insert(foundObjects, {name = className, obj = obj, funcs = funcs})
                end
                
                -- Try calling any promising functions
                for _, funcEntry in ipairs(funcs) do
                    local lowerName = string.lower(funcEntry.name)
                    if (string.find(lowerName, "add") or
                        string.find(lowerName, "give") or
                        string.find(lowerName, "grant") or
                        string.find(lowerName, "setitem")) and
                       not string.find(lowerName, "get") then
                        Log(string.format("  ** POTENTIAL GRANT FUNCTION: %s **", funcEntry.name))
                    end
                end
            end
        end
    end
    
    -- Also search using FindAllOf to find all instances
    Log("\n=== Searching with FindAllOf ===")
    local searchPatterns = {"ItemManager", "Inventory", "ItemComponent", "SaveData"}
    
    for _, pattern in ipairs(searchPatterns) do
        local success, objects = pcall(function()
            return FindAllOf(pattern)
        end)
        
        if success and objects then
            local count = 0
            for _, obj in ipairs(objects) do
                if obj:IsValid() then
                    local fullName = obj:GetFullName()
                    if not string.find(fullName, "Default__") then
                        count = count + 1
                        if count <= 3 then
                            Log(string.format("  FindAllOf(%s): %s", pattern, fullName))
                        end
                    end
                end
            end
            if count > 3 then
                Log(string.format("    ... and %d more", count - 3))
            end
        end
    end
    
    -- Try to find blueprint-implemented classes
    Log("\n=== Looking for Blueprint Classes ===")
    local bpPatterns = {"BP_", "WBP_", "ABP_"}
    
    for _, prefix in ipairs(bpPatterns) do
        local success, objects = pcall(function()
            return FindAllOf(prefix .. "Item")
        end)
        
        if success and objects then
            for i, obj in ipairs(objects) do
                if obj:IsValid() and i <= 5 then
                    Log(string.format("  %s%s: %s", prefix, "Item*", obj:GetFullName()))
                end
            end
        end
    end
    
    Log("\n=== Search Complete ===")
    Log(string.format("Found %d objects with interesting functions", #foundObjects))
    
    return foundObjects
end

-- ============================================================================
-- Initialization
-- ============================================================================

function GameState.Initialize()
    Log("Initializing game state interface...")
    
    -- Try to find and cache all API references
    local dataBaseApi = GetDataBaseAPI()
    local menuBpApi = GetMenuBPAPI()
    local battleApi = GetBattleAPI()
    local partyApi = GetPartyAPI()
    
    Log(string.format("API Status: DataBase=%s, MenuBP=%s, Battle=%s, Party=%s",
        dataBaseApi and "OK" or "MISSING",
        menuBpApi and "OK" or "MISSING",
        battleApi and "OK" or "MISSING",
        partyApi and "OK" or "MISSING"
    ))
    
    -- DON'T run API tests here - game world not loaded yet!
    -- Tests will run when player spawns (OnPlayerSpawn)
    Log("API tests will run when player spawns into game world...")
    
    State.Initialized = true
    Log("Game state interface initialized")
end

return GameState
