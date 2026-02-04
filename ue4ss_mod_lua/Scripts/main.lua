--[[
    FFVII Rebirth Archipelago Mod
    Main entry point for UE4SS Lua mod
    
    This mod connects Final Fantasy VII: Rebirth to an Archipelago multiworld server.
]]

local ModName = "FFVIIRebirthAP"
local ModVersion = "0.1.0"

-- Load submodules
local json = require("json")
local APClient = require("APClient")
local GameState = require("GameState")
local ItemHandler = require("ItemHandler")
local MemoryItem = require("MemoryItem")
local ShopPatcher = require("ShopPatcher")

-- Configuration
local Config = {
    PollIntervalMs = 100,       -- How often to poll AP server
    AutoReconnect = true,       -- Reconnect on disconnect
    ReconnectDelayMs = 5000,    -- Delay before reconnect attempt
    DebugMode = true,           -- Enable debug logging
}

-- State
local State = {
    Initialized = false,
    LastPollTime = 0,
    LastReconnectAttempt = 0,
    InitializationTime = nil,  -- Track when mod was initialized
    TestsTriggered = false,    -- Track if we've triggered API tests
}

---Print a message to the UE4SS console
---@param msg string
local function Log(msg)
    print(string.format("[%s] %s", ModName, msg))
end

---Print debug message (only if debug mode enabled)
---@param msg string
local function LogDebug(msg)
    if Config.DebugMode then
        print(string.format("[%s][DEBUG] %s", ModName, msg))
    end
end

---Initialize the mod
local function Initialize()
    if State.Initialized then
        return
    end
    
    print("[FFVIIRebirthAP] =========================================")
    print("[FFVIIRebirthAP]   " .. ModName .. " v" .. ModVersion)
    print("[FFVIIRebirthAP]   Final Fantasy VII: Rebirth x Archipelago")
    print("[FFVIIRebirthAP] =========================================")
    
    -- Initialize shop patcher
    ShopPatcher:Init()
    
    print("[FFVIIRebirthAP] Testing basic print...")
    
    -- Test if StaticFindObject exists
    print("[FFVIIRebirthAP] Checking UE4SS functions...")
    if StaticFindObject then
        print("[FFVIIRebirthAP] StaticFindObject: AVAILABLE")
    else
        print("[FFVIIRebirthAP] StaticFindObject: NOT FOUND")
    end
    
    if FindFirstOf then
        print("[FFVIIRebirthAP] FindFirstOf: AVAILABLE")
    else
        print("[FFVIIRebirthAP] FindFirstOf: NOT FOUND")
    end
    
    if RegisterHook then
        print("[FFVIIRebirthAP] RegisterHook: AVAILABLE")
    else
        print("[FFVIIRebirthAP] RegisterHook: NOT FOUND")
    end
    
    -- Try to find some objects
    print("[FFVIIRebirthAP] Testing StaticFindObject...")
    local testSuccess, testResult = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
    end)
    print("[FFVIIRebirthAP] EndDataBaseDataBaseAPI: success=" .. tostring(testSuccess) .. ", result=" .. tostring(testResult))
    
    testSuccess, testResult = pcall(function()
        return StaticFindObject("/Script/EndGame.Default__EndMenuBPAPI")
    end)
    print("[FFVIIRebirthAP] EndMenuBPAPI: success=" .. tostring(testSuccess) .. ", result=" .. tostring(testResult))
    
    -- Try FindFirstOf as alternative
    print("[FFVIIRebirthAP] Testing FindFirstOf...")
    testSuccess, testResult = pcall(function()
        return FindFirstOf("EndDataBaseDataBaseAPI")
    end)
    print("[FFVIIRebirthAP] FindFirstOf EndDataBaseDataBaseAPI: success=" .. tostring(testSuccess) .. ", result=" .. tostring(testResult))
    
    -- Initialize subsystems  
    print("[FFVIIRebirthAP] Initializing APClient...")
    APClient.Initialize()
    print("[FFVIIRebirthAP] Initializing GameState...")
    GameState.Initialize()
    print("[FFVIIRebirthAP] Initializing ItemHandler...")
    ItemHandler.Initialize()
    print("[FFVIIRebirthAP] Initializing MemoryItem...")
    MemoryItem.Initialize()
    
    -- Set up callbacks
    APClient.SetItemReceivedCallback(function(itemId, itemName, senderName)
        Log(string.format("Received: %s from %s", itemName, senderName))
        ItemHandler.ReceiveItem(itemId, itemName, senderName)
    end)
    
    APClient.SetLocationInfoCallback(function(locationId, locationName)
        LogDebug(string.format("Location scouted: %s (%d)", locationName, locationId))
    end)
    
    APClient.SetConnectedCallback(function(slotData)
        Log("Connected to Archipelago server!")
        Log(string.format("Slot data received: %d keys", slotData and #slotData or 0))
        GameState.ApplySlotData(slotData)
    end)
    
    APClient.SetDisconnectedCallback(function(reason)
        Log(string.format("Disconnected: %s", reason or "Unknown"))
    end)
    
    APClient.SetDeathLinkCallback(function(source, cause)
        Log(string.format("DeathLink from %s: %s", source, cause or "died"))
        GameState.TriggerDeath()
    end)
    
    State.Initialized = true
    State.InitializationTime = os.time()  -- Record when mod started
    print("[FFVIIRebirthAP] Mod initialized!")
end

---Main update loop - called every tick
local function OnTick()
    if not State.Initialized then
        return
    end
    
    local currentTime = os.clock() * 1000  -- Convert to milliseconds
    
    -- NO AUTOMATIC API TESTS - they will only run via /ap testapi command
    
    -- Poll AP server at configured interval
    if currentTime - State.LastPollTime >= Config.PollIntervalMs then
        State.LastPollTime = currentTime
        
        if APClient.IsConnected() then
            APClient.Poll()
            
            -- Check for completed locations
            local newChecks = GameState.GetNewLocationChecks()
            if #newChecks > 0 then
                LogDebug(string.format("Sending %d location checks", #newChecks))
                APClient.SendLocationChecks(newChecks)
            end
            
            -- Check for death (DeathLink)
            if APClient.IsDeathLinkEnabled() and GameState.CheckPlayerDeath() then
                Log("Player died - sending DeathLink")
                APClient.SendDeath("Died in FFVII Rebirth")
            end
            
            -- Check for goal completion
            if GameState.CheckGoalComplete() then
                Log("Goal complete! Sending to server...")
                APClient.SendGoalComplete()
            end
        elseif Config.AutoReconnect and APClient.HasConnectionInfo() then
            -- Auto-reconnect logic
            if currentTime - State.LastReconnectAttempt >= Config.ReconnectDelayMs then
                State.LastReconnectAttempt = currentTime
                LogDebug("Attempting auto-reconnect...")
                APClient.Reconnect()
            end
        end
    end
end

---Handle console commands
---@param fullCommand string
---@param commandParts table
---@return boolean handled
local function OnCommand(fullCommand, commandParts)
    local cmd = commandParts[1]
    
    if cmd ~= "/ap" and cmd ~= "/archipelago" then
        return false  -- Not our command
    end
    
    local subCmd = commandParts[2] or "help"
    
    if subCmd == "help" then
        Log("=== Archipelago Commands ===")
        Log("/ap connect <server> <slot> [password] - Connect to AP server")
        Log("/ap disconnect - Disconnect from server")
        Log("/ap status - Show connection status")
        Log("/ap deathlink [on|off] - Toggle DeathLink")
        Log("/ap items - List received items")
        Log("/ap locations - List checked locations")
        Log("/ap debug [on|off] - Toggle debug mode")
        Log("/ap test - Run basic diagnostic tests")
        Log("/ap testapi - Run full API discovery test")
        Log("/ap testitem2 - Run item manipulation exploration test")
        Log("/ap testitem <name> - Test granting an item")
        Log("/ap dumpmappings - Dump item name mappings")
        return true
        
    elseif subCmd == "connect" then
        local server = commandParts[3]
        local slot = commandParts[4]
        local password = commandParts[5] or ""
        
        if not server or not slot then
            Log("Usage: /ap connect <server:port> <slotname> [password]")
            Log("Example: /ap connect archipelago.gg:38281 PlayerName")
            return true
        end
        
        Log(string.format("Connecting to %s as %s...", server, slot))
        APClient.Connect(server, slot, password)
        return true
        
    elseif subCmd == "disconnect" then
        APClient.Disconnect()
        Log("Disconnected from server")
        return true
        
    elseif subCmd == "status" then
        if APClient.IsConnected() then
            local info = APClient.GetConnectionInfo()
            Log(string.format("Connected to: %s", info.server or "unknown"))
            Log(string.format("Slot: %s", info.slot or "unknown"))
            Log(string.format("Items received: %d", ItemHandler.GetReceivedCount()))
            Log(string.format("Locations checked: %d", GameState.GetCheckedCount()))
            Log(string.format("DeathLink: %s", APClient.IsDeathLinkEnabled() and "ON" or "OFF"))
        else
            Log("Not connected to any server")
        end
        return true
        
    elseif subCmd == "deathlink" then
        local toggle = commandParts[3]
        if toggle == "on" then
            APClient.SetDeathLink(true)
            Log("DeathLink enabled")
        elseif toggle == "off" then
            APClient.SetDeathLink(false)
            Log("DeathLink disabled")
        else
            APClient.SetDeathLink(not APClient.IsDeathLinkEnabled())
            Log(string.format("DeathLink %s", APClient.IsDeathLinkEnabled() and "enabled" or "disabled"))
        end
        return true
        
    elseif subCmd == "items" then
        local items = ItemHandler.GetReceivedItems()
        Log(string.format("=== Received Items (%d) ===", #items))
        for i, item in ipairs(items) do
            if i <= 20 then  -- Limit output
                Log(string.format("  %s (from %s)", item.name, item.sender))
            end
        end
        if #items > 20 then
            Log(string.format("  ... and %d more", #items - 20))
        end
        return true
        
    elseif subCmd == "locations" then
        local locs = GameState.GetCheckedLocations()
        Log(string.format("=== Checked Locations (%d) ===", #locs))
        for i, loc in ipairs(locs) do
            if i <= 20 then
                Log(string.format("  %s", loc.name or tostring(loc.id)))
            end
        end
        if #locs > 20 then
            Log(string.format("  ... and %d more", #locs - 20))
        end
        return true
        
    elseif subCmd == "debug" then
        local toggle = commandParts[3]
        if toggle == "on" then
            Config.DebugMode = true
        elseif toggle == "off" then
            Config.DebugMode = false
        else
            Config.DebugMode = not Config.DebugMode
        end
        Log(string.format("Debug mode %s", Config.DebugMode and "enabled" or "disabled"))
        return true
        
    elseif subCmd == "test" then
        Log("=== Running Basic Diagnostics ===")
        Log(string.format("Game Loaded: %s", GameState.IsGameLoaded() and "YES" or "NO"))
        Log(string.format("Current Map: %s", GameState.GetCurrentMap() or "Unknown"))
        Log(string.format("Chapter: %d", GameState.GetChapterProgress()))
        Log(string.format("AP Connected: %s", APClient.IsConnected() and "YES" or "NO"))
        Log(string.format("WebSocket Available: %s", APClient.IsWebSocketAvailable() and "YES" or "NO"))
        Log(string.format("Items Pending: %d", ItemHandler.GetPendingCount()))
        return true
        
    elseif subCmd == "testitem2" then
        Log("Running item manipulation test...")
        GameState.TestItemManipulation()
        return true
        
    elseif subCmd == "testitem" then
        local itemName = commandParts[3]
        if not itemName then
            Log("Usage: /ap testitem <itemname>")
            Log("Example: /ap testitem Potion")
            return true
        end
        
        Log(string.format("Testing item grant: %s", itemName))
        local success = ItemHandler.GrantItem(0, itemName)
        Log(string.format("Result: %s", success and "SUCCESS" or "FAILED"))
        return true
        
    elseif subCmd == "dumpmappings" then
        ItemHandler.DumpMappings()
        return true
        
    else
        Log(string.format("Unknown command: %s. Use /ap help for commands.", subCmd))
        return true
    end
end

-- ============================================================================
-- UE4SS Entry Points
-- ============================================================================

-- Register console command handler (if available)
if RegisterConsoleCommandHandler then
    RegisterConsoleCommandHandler("/ap", function(fullCommand, parts)
        return OnCommand(fullCommand, parts)
    end)

    RegisterConsoleCommandHandler("/archipelago", function(fullCommand, parts)
        return OnCommand(fullCommand, parts)
    end)
end

-- Hook into game events if available
RegisterHook("/Script/Engine.PlayerController:ClientRestart", function(Context)
    LogDebug("Player restarted - checking game state")
    GameState.OnPlayerSpawn()
end)

-- ============================================================================
-- INITIALIZE IMMEDIATELY (UE4SS 3.0 runs script directly)
-- ============================================================================
print("[FFVIIRebirthAP] Script executing...")
Initialize()
print("[FFVIIRebirthAP] Initialization complete!")

-- Register hotkeys for testing (since console is not accessible)
if RegisterKeyBind then
    -- F3 - Scan for shop DataTables (use when in a shop)
    RegisterKeyBind(Key.F3, function()
        print("[FFVIIRebirthAP] F3 - SHOP DATATABLE SCAN")
        ShopPatcher:FindAndHookShopTables()
    end)
    print("[FFVIIRebirthAP] F3 = Scan for shop DataTables (press when in shop)")

    -- F5 - Quick status check
    RegisterKeyBind(Key.F5, function()
        Log("=== F5 - STATUS CHECK ===")
        Log(string.format("Game Loaded: %s", GameState.IsGameLoaded() and "YES" or "NO"))
        Log(string.format("Current Map: %s", GameState.GetCurrentMap() or "Unknown"))
        Log(string.format("Chapter: %d", GameState.GetChapterProgress()))
        Log(string.format("AP Connected: %s", APClient.IsConnected() and "YES" or "NO"))
    end)
    print("[FFVIIRebirthAP] F5 = Status check")

    -- F6 - Test give potion
    RegisterKeyBind(Key.F6, function()
        Log("=== F6 - TEST GIVE POTION ===")
        local success = ItemHandler.GrantItem(0, "Potion")
        Log(string.format("GrantItem Potion: %s", success and "SUCCESS" or "FAILED"))
        success = ItemHandler.GrantItem(0, "IT_Potion")
        Log(string.format("GrantItem IT_Potion: %s", success and "SUCCESS" or "FAILED"))
    end)
    print("[FFVIIRebirthAP] F6 = Test give potion")

    -- F7 - Run item manipulation test
    RegisterKeyBind(Key.F7, function()
        Log("=== F7 - ITEM MANIPULATION TEST ===")
        local success, err = pcall(function()
            GameState.TestItemManipulation()
        end)
        if not success then
            Log("ERROR: " .. tostring(err))
        end
    end)
    print("[FFVIIRebirthAP] F7 = Item manipulation test")

    -- F8 - Dump item mappings
    RegisterKeyBind(Key.F8, function()
        Log("=== F8 - DUMP ITEM MAPPINGS ===")
        ItemHandler.DumpMappings()
    end)
    print("[FFVIIRebirthAP] F8 = Dump item mappings")

    -- F9 - Full API tests (existing)
    RegisterKeyBind(Key.F9, function()
        Log("=== F9 PRESSED - Running API Tests ===")
        local success, err = pcall(function()
            GameState.TestAllAPIs()
        end)
        if not success then
            Log("ERROR in basic tests: " .. tostring(err))
        end
        
        Log("=== Running Item Manipulation Test ===")
        success, err = pcall(function()
            GameState.TestItemManipulation()
        end)
        if not success then
            Log("ERROR in item manipulation test: " .. tostring(err))
        end
        Log("=== All Tests Complete ===")
    end)
    print("[FFVIIRebirthAP] F9 = Full API tests")

    -- F10 - Test GetItemNumBP with various IDs
    RegisterKeyBind(Key.F10, function()
        Log("=== F10 - GETITEMNUMBP TEST ===")
        local success, err = pcall(function()
            GameState.TestGetItemNumBP()
        end)
        if not success then
            Log("ERROR: " .. tostring(err))
        end
    end)
    print("[FFVIIRebirthAP] F10 = GetItemNumBP test")

    -- F11 - Enumerate player character functions
    RegisterKeyBind(Key.F11, function()
        Log("=== F11 - ENUMERATE PLAYER FUNCTIONS ===")
        local success, err = pcall(function()
            GameState.EnumeratePlayerCharacterFunctions()
        end)
        if not success then
            Log("ERROR: " .. tostring(err))
        end
    end)
    print("[FFVIIRebirthAP] F11 = Enumerate player functions")

    -- F12 - Find item granters and test CallFunction
    RegisterKeyBind(Key.F12, function()
        Log("=== F12 - FIND ITEM GRANTERS ===")
        local success, err = pcall(function()
            GameState.TestFindItemGranter()
        end)
        if not success then
            Log("ERROR: " .. tostring(err))
        end
        
        Log("=== Testing CallFunction API ===")
        success, err = pcall(function()
            GameState.TestCallFunction()
        end)
        if not success then
            Log("ERROR in CallFunction test: " .. tostring(err))
        end
    end)
    print("[FFVIIRebirthAP] F12 = Find item granters + CallFunction test")

    -- F1 - Test memory-based item giving (NEW)
    RegisterKeyBind(Key.F1, function()
        Log("=== F1 - MEMORY ITEM TEST ===")
        local success, err = pcall(function()
            Log("Testing memory access...")
            MemoryItem.TestMemoryAccess()
            
            Log("Attempting to give Potion via memory...")
            local ok, msg = MemoryItem.GiveItem(MemoryItem.ItemDatabase.POTION, 5)
            Log(string.format("Result: %s - %s", ok and "SUCCESS" or "FAILED", msg))
        end)
        if not success then
            Log("ERROR: " .. tostring(err))
        end
    end)
    print("[FFVIIRebirthAP] F1 = Memory item test")

    print("[FFVIIRebirthAP] =========================================")
    print("[FFVIIRebirthAP] HOTKEYS REGISTERED:")
    print("[FFVIIRebirthAP]   F1  = Memory item test (NEW - direct memory write)")
    print("[FFVIIRebirthAP]   F3  = Scan for shop DataTables (PRESS WHEN IN SHOP)")
    print("[FFVIIRebirthAP]   F5  = Status check")
    print("[FFVIIRebirthAP]   F6  = Test give potion")
    print("[FFVIIRebirthAP]   F7  = **API TEST SUITE** (IMPORTANT)")
    print("[FFVIIRebirthAP]   F8  = Dump item mappings")
    print("[FFVIIRebirthAP]   F9  = Full API tests")
    print("[FFVIIRebirthAP]   F10 = GetItemNumBP test")
    print("[FFVIIRebirthAP]   F11 = Enumerate player functions")
    print("[FFVIIRebirthAP]   F12 = Find item granters")
    print("[FFVIIRebirthAP] ========================================")
else
    print("[FFVIIRebirthAP] RegisterKeyBind not available")
end

-- Export for other modules
return {
    Log = Log,
    LogDebug = LogDebug,
    Config = Config,
    State = State,
}
