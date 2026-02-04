--[[
    APClient.lua
    Archipelago client implementation using WebSocket
    
    Handles connection to AP server, message parsing, and state synchronization.
]]

local json = require("json")

local APClient = {}

-- AP Protocol Constants
local AP_VERSION = {major = 0, minor = 5, build = 0, class = "Version"}
local GAME_NAME = "Final Fantasy VII: Rebirth"
local BASE_ID = 770000  -- Must match APWorld base_id

-- Internal state
local State = {
    Connected = false,
    Authenticated = false,
    Socket = nil,
    
    -- Connection info
    Server = "",
    Slot = "",
    Password = "",
    
    -- Game state
    Team = 0,
    SlotNumber = 0,
    SlotData = {},
    
    -- Tracking
    ReceivedItemIndex = 0,
    CheckedLocations = {},
    MissingLocations = {},
    
    -- DeathLink
    DeathLinkEnabled = false,
    LastDeathTime = 0,
    
    -- Callbacks
    OnItemReceived = nil,
    OnLocationInfo = nil,
    OnConnected = nil,
    OnDisconnected = nil,
    OnDeathLink = nil,
}

-- ============================================================================
-- Utility Functions
-- ============================================================================

local function Log(msg)
    print(string.format("[APClient] %s", msg))
end

local function LogDebug(msg)
    print(string.format("[APClient][DEBUG] %s", msg))
end

-- ============================================================================
-- WebSocket Handling
-- ============================================================================

---Check if WebSocket is available (UE4SS provides this)
---@return boolean
function APClient.IsWebSocketAvailable()
    -- UE4SS should provide WebSocket support
    -- Check if the global exists
    return type(WebSocket) ~= "nil" or type(CreateWebSocket) ~= "nil"
end

---Create a WebSocket connection
---@param url string WebSocket URL (ws:// or wss://)
---@return table|nil socket
local function CreateSocket(url)
    -- Try UE4SS WebSocket API
    if type(CreateWebSocket) == "function" then
        return CreateWebSocket(url)
    end
    
    -- Try alternative WebSocket global
    if type(WebSocket) == "table" and type(WebSocket.new) == "function" then
        return WebSocket.new(url)
    end
    
    Log("ERROR: No WebSocket implementation available!")
    Log("Make sure UE4SS is properly installed with WebSocket support.")
    return nil
end

---Send a message through the WebSocket
---@param msg table Message to send (will be JSON encoded)
local function SendMessage(msg)
    if not State.Socket then
        Log("Cannot send - no connection")
        return
    end
    
    local data = json.encode({msg})  -- AP protocol wraps messages in array
    LogDebug(string.format("Sending: %s", data))
    
    if State.Socket.send then
        State.Socket:send(data)
    elseif State.Socket.Send then
        State.Socket:Send(data)
    end
end

---Handle incoming WebSocket message
---@param data string Raw message data
local function OnMessage(data)
    LogDebug(string.format("Received: %s", data:sub(1, 200)))
    
    local ok, messages = pcall(json.decode, data)
    if not ok then
        Log("Failed to parse message: " .. tostring(messages))
        return
    end
    
    -- AP sends messages as array
    if type(messages) ~= "table" then
        return
    end
    
    for _, msg in ipairs(messages) do
        APClient.HandleMessage(msg)
    end
end

---Handle WebSocket connection opened
local function OnOpen()
    Log("WebSocket connected!")
    State.Connected = true
end

---Handle WebSocket connection closed
---@param code number Close code
---@param reason string Close reason
local function OnClose(code, reason)
    Log(string.format("WebSocket closed: %s (code %d)", reason or "unknown", code or 0))
    State.Connected = false
    State.Authenticated = false
    
    if State.OnDisconnected then
        State.OnDisconnected(reason)
    end
end

---Handle WebSocket error
---@param err string Error message
local function OnError(err)
    Log("WebSocket error: " .. tostring(err))
end

-- ============================================================================
-- AP Protocol Message Handlers
-- ============================================================================

local MessageHandlers = {}

function MessageHandlers.RoomInfo(msg)
    Log("Received RoomInfo - authenticating...")
    
    -- Send Connect message
    local connectMsg = {
        cmd = "Connect",
        password = State.Password,
        name = State.Slot,
        version = AP_VERSION,
        tags = State.DeathLinkEnabled and {"DeathLink"} or {},
        items_handling = 7,  -- Receive all items (0b111 = 7: full remote inventory)
        uuid = "",
        game = GAME_NAME,
        slot_data = true,
    }
    
    SendMessage(connectMsg)
end

function MessageHandlers.Connected(msg)
    Log("Successfully authenticated!")
    State.Authenticated = true
    State.Team = msg.team or 0
    State.SlotNumber = msg.slot or 0
    State.SlotData = msg.slot_data or {}
    State.CheckedLocations = {}
    State.MissingLocations = {}
    
    -- Store checked/missing locations
    if msg.checked_locations then
        for _, loc in ipairs(msg.checked_locations) do
            State.CheckedLocations[loc] = true
        end
    end
    
    if msg.missing_locations then
        for _, loc in ipairs(msg.missing_locations) do
            State.MissingLocations[loc] = true
        end
    end
    
    Log(string.format("Slot %d on team %d", State.SlotNumber, State.Team))
    Log(string.format("Checked: %d, Missing: %d locations", 
        msg.checked_locations and #msg.checked_locations or 0,
        msg.missing_locations and #msg.missing_locations or 0))
    
    if State.OnConnected then
        State.OnConnected(State.SlotData)
    end
    
    -- Request items we've received
    SendMessage({cmd = "Sync"})
end

function MessageHandlers.ConnectionRefused(msg)
    local errors = msg.errors or {"Unknown error"}
    Log("Connection refused: " .. table.concat(errors, ", "))
    
    if State.OnDisconnected then
        State.OnDisconnected("Connection refused: " .. errors[1])
    end
end

function MessageHandlers.ReceivedItems(msg)
    local startIndex = msg.index or 0
    local items = msg.items or {}
    
    LogDebug(string.format("Received %d items starting at index %d", #items, startIndex))
    
    for i, item in ipairs(items) do
        local itemIndex = startIndex + i - 1
        
        -- Only process new items
        if itemIndex >= State.ReceivedItemIndex then
            State.ReceivedItemIndex = itemIndex + 1
            
            if State.OnItemReceived then
                local itemId = item.item
                local itemName = item.name or string.format("Item_%d", itemId)
                local senderSlot = item.player or 0
                local senderName = string.format("Player %d", senderSlot)  -- Would need player names from DataPackage
                
                State.OnItemReceived(itemId, itemName, senderName)
            end
        end
    end
end

function MessageHandlers.RoomUpdate(msg)
    -- Update checked locations if provided
    if msg.checked_locations then
        for _, loc in ipairs(msg.checked_locations) do
            State.CheckedLocations[loc] = true
            State.MissingLocations[loc] = nil
        end
    end
end

function MessageHandlers.PrintJSON(msg)
    -- Chat/notification messages
    local text = ""
    if msg.data then
        for _, part in ipairs(msg.data) do
            if type(part) == "table" then
                text = text .. (part.text or "")
            else
                text = text .. tostring(part)
            end
        end
    end
    
    if text ~= "" then
        Log("[Chat] " .. text)
    end
end

function MessageHandlers.Bounced(msg)
    -- Handle bounced messages (DeathLink, etc.)
    local tags = msg.tags or {}
    
    for _, tag in ipairs(tags) do
        if tag == "DeathLink" and State.DeathLinkEnabled then
            local data = msg.data or {}
            local source = data.source or "Unknown"
            local cause = data.cause or "died"
            local time = data.time or 0
            
            -- Ignore our own deaths
            if time ~= State.LastDeathTime then
                Log(string.format("DeathLink: %s %s", source, cause))
                if State.OnDeathLink then
                    State.OnDeathLink(source, cause)
                end
            end
        end
    end
end

function MessageHandlers.Retrieved(msg)
    -- Response to Get requests
    LogDebug("Retrieved data: " .. json.encode(msg.keys or {}))
end

function MessageHandlers.SetReply(msg)
    -- Response to Set requests
    LogDebug("SetReply for key: " .. tostring(msg.key))
end

function MessageHandlers.InvalidPacket(msg)
    Log("Server reported invalid packet: " .. (msg.text or "unknown error"))
end

---Handle a parsed AP message
---@param msg table Parsed message
function APClient.HandleMessage(msg)
    local cmd = msg.cmd
    if not cmd then
        return
    end
    
    local handler = MessageHandlers[cmd]
    if handler then
        handler(msg)
    else
        LogDebug("Unhandled message type: " .. cmd)
    end
end

-- ============================================================================
-- Public API
-- ============================================================================

function APClient.Initialize()
    Log("Initializing Archipelago client...")
    
    if not APClient.IsWebSocketAvailable() then
        Log("WARNING: WebSocket not available - connection will fail")
    end
    
    Log("Client initialized")
end

---Connect to an Archipelago server
---@param server string Server address (host:port)
---@param slot string Slot/player name
---@param password string Optional password
function APClient.Connect(server, slot, password)
    if State.Connected then
        Log("Already connected. Disconnect first.")
        return
    end
    
    State.Server = server
    State.Slot = slot
    State.Password = password or ""
    State.ReceivedItemIndex = 0
    
    -- Build WebSocket URL
    local url
    if server:find("://") then
        url = server:gsub("^http", "ws")  -- Convert http(s) to ws(s)
    else
        -- Default to wss for archipelago.gg, ws for local
        if server:find("archipelago.gg") then
            url = "wss://" .. server
        else
            url = "ws://" .. server
        end
    end
    
    Log(string.format("Connecting to %s...", url))
    
    State.Socket = CreateSocket(url)
    if not State.Socket then
        Log("Failed to create WebSocket")
        return
    end
    
    -- Set up socket callbacks
    if State.Socket.onopen then
        State.Socket.onopen = OnOpen
        State.Socket.onmessage = function(evt) OnMessage(evt.data) end
        State.Socket.onclose = function(evt) OnClose(evt.code, evt.reason) end
        State.Socket.onerror = function(evt) OnError(evt.message or "error") end
    elseif State.Socket.SetOnOpen then
        -- Alternative API style
        State.Socket:SetOnOpen(OnOpen)
        State.Socket:SetOnMessage(OnMessage)
        State.Socket:SetOnClose(OnClose)
        State.Socket:SetOnError(OnError)
    end
end

---Disconnect from the server
function APClient.Disconnect()
    if State.Socket then
        if State.Socket.close then
            State.Socket:close()
        elseif State.Socket.Close then
            State.Socket:Close()
        end
        State.Socket = nil
    end
    
    State.Connected = false
    State.Authenticated = false
end

---Reconnect using previous connection info
function APClient.Reconnect()
    if State.Server ~= "" and State.Slot ~= "" then
        APClient.Connect(State.Server, State.Slot, State.Password)
    end
end

---Check if connected and authenticated
---@return boolean
function APClient.IsConnected()
    return State.Connected and State.Authenticated
end

---Check if we have connection info for reconnect
---@return boolean
function APClient.HasConnectionInfo()
    return State.Server ~= "" and State.Slot ~= ""
end

---Get connection info
---@return table
function APClient.GetConnectionInfo()
    return {
        server = State.Server,
        slot = State.Slot,
        team = State.Team,
        slotNumber = State.SlotNumber,
    }
end

---Poll for incoming messages (call regularly)
function APClient.Poll()
    -- WebSocket should handle this automatically via callbacks
    -- But some implementations need explicit polling
    if State.Socket and State.Socket.poll then
        State.Socket:poll()
    end
end

---Send location checks to server
---@param locationIds table Array of location IDs
function APClient.SendLocationChecks(locationIds)
    if not APClient.IsConnected() then
        return
    end
    
    SendMessage({
        cmd = "LocationChecks",
        locations = locationIds,
    })
    
    -- Mark as checked locally
    for _, loc in ipairs(locationIds) do
        State.CheckedLocations[loc] = true
        State.MissingLocations[loc] = nil
    end
end

---Send goal completion
function APClient.SendGoalComplete()
    if not APClient.IsConnected() then
        return
    end
    
    SendMessage({
        cmd = "StatusUpdate",
        status = 30,  -- CLIENT_GOAL
    })
end

---Send death for DeathLink
---@param cause string Optional death cause
function APClient.SendDeath(cause)
    if not APClient.IsConnected() or not State.DeathLinkEnabled then
        return
    end
    
    local time = os.time()
    State.LastDeathTime = time
    
    SendMessage({
        cmd = "Bounce",
        tags = {"DeathLink"},
        data = {
            time = time,
            cause = cause or "died",
            source = State.Slot,
        },
    })
end

---Enable/disable DeathLink
---@param enabled boolean
function APClient.SetDeathLink(enabled)
    State.DeathLinkEnabled = enabled
    
    if APClient.IsConnected() then
        -- Update server about our tags
        SendMessage({
            cmd = "ConnectUpdate",
            tags = enabled and {"DeathLink"} or {},
        })
    end
end

---Check if DeathLink is enabled
---@return boolean
function APClient.IsDeathLinkEnabled()
    return State.DeathLinkEnabled
end

---Get slot data
---@return table
function APClient.GetSlotData()
    return State.SlotData
end

---Check if a location has been checked
---@param locationId number
---@return boolean
function APClient.IsLocationChecked(locationId)
    return State.CheckedLocations[locationId] == true
end

-- ============================================================================
-- Callback Setters
-- ============================================================================

function APClient.SetItemReceivedCallback(callback)
    State.OnItemReceived = callback
end

function APClient.SetLocationInfoCallback(callback)
    State.OnLocationInfo = callback
end

function APClient.SetConnectedCallback(callback)
    State.OnConnected = callback
end

function APClient.SetDisconnectedCallback(callback)
    State.OnDisconnected = callback
end

function APClient.SetDeathLinkCallback(callback)
    State.OnDeathLink = callback
end

return APClient
