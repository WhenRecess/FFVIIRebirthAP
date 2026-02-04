--[[
    ItemHook.lua - EXAMPLE: Function hooking for item interception
    
    This demonstrates how to hook the game's item-granting function
    to intercept and replace items with randomized ones.
    
    NOTE: This is a TEMPLATE - you need to find the actual function names
    by exploring the game with UE4SS Live View.
]]

local ItemHook = {}

-- ============================================================================
-- Configuration
-- ============================================================================

-- Mapping of vanilla item locations to randomized items
-- This would be loaded from AP seed data
local RandomizedItems = {
    -- Format: [location_key] = {item_id = 101, item_name = "Hi-Potion"}
    ["Grasslands_Chest_001"] = {item_id = 111, item_name = "Ether"},
    ["Grasslands_Chest_002"] = {item_id = 116, item_name = "Phoenix Down"},
}

-- Context tracking for location detection
local ItemContext = {
    current_map = "Unknown",
    current_position = {x = 0, y = 0, z = 0},
    last_shop_id = nil,
}

-- ============================================================================
-- Function Hooking Examples
-- ============================================================================

---EXAMPLE: Hook the item-giving function
---
--- To find the function name:
--- 1. Open UE4SS Live View (press F10 in game)
--- 2. Search for "AddItem" or "GiveItem"
--- 3. Look for: /Script/End.EndDataBaseDataBaseAPI:AddItemBP
---
local function HookAddItem()
    -- This is EXAMPLE syntax - adjust to actual function signature
    RegisterHook("/Script/End.EndDataBaseDataBaseAPI:AddItemBP", function(Context, ItemId, Quantity)
        print(string.format("[ItemHook] Game tried to give: Item %d x%d", ItemId, Quantity))
        
        -- Determine location based on context
        local location_key = DetermineLocation(ItemId)
        
        -- Check if this location has a randomized item
        if location_key and RandomizedItems[location_key] then
            local randomized = RandomizedItems[location_key]
            
            print(string.format("[ItemHook] Replacing with: %s (ID %d)", 
                randomized.item_name, randomized.item_id))
            
            -- MODIFY THE PARAMETERS before game processes them
            Context:SetIntProperty("ItemId", randomized.item_id)
            
            -- Mark location as checked
            NotifyAPLocationChecked(location_key)
            
            -- Allow the modified call to proceed
            return true
        end
        
        -- Not a randomized location, allow vanilla behavior
        return true
    end)
    
    print("[ItemHook] Hooked AddItemBP function")
end

---EXAMPLE: Hook battle rewards
local function HookBattleReward()
    -- Look for: /Script/End.EndBattleAPI:OnBattleEnd
    RegisterHook("/Script/End.EndBattleAPI:OnBattleEnd", function(Context, BattleResult)
        if BattleResult == "Victory" then
            local battle_id = Context:GetBattleId()
            print(string.format("[ItemHook] Battle won: %s", battle_id))
            
            -- Check if this is a boss with randomized reward
            if RandomizedItems[battle_id] then
                -- Prevent vanilla reward
                Context:SetShouldGiveReward(false)
                
                -- Grant randomized reward separately
                GrantRandomizedReward(battle_id)
            end
        end
        return true
    end)
end

---EXAMPLE: Hook shop purchases
local function HookShopPurchase()
    -- Look for: /Script/End.EndShopAPI:PurchaseItem
    RegisterHook("/Script/End.EndShopAPI:PurchaseItem", function(Context, ShopId, SlotIndex)
        print(string.format("[ItemHook] Shop purchase: %s Slot %d", ShopId, SlotIndex))
        
        local location_key = string.format("%s_Slot_%d", ShopId, SlotIndex)
        
        if RandomizedItems[location_key] then
            -- Block vanilla item
            Context:SetCancelPurchase(true)
            
            -- Deduct gil manually
            DeductGil(Context:GetItemCost())
            
            -- Grant randomized item
            GrantRandomizedReward(location_key)
            
            NotifyAPLocationChecked(location_key)
        end
        
        return true
    end)
end

-- ============================================================================
-- Helper Functions
-- ============================================================================

---Determine which location is giving this item
---@param item_id number The vanilla item ID
---@return string|nil location_key
local function DetermineLocation(item_id)
    -- Strategy 1: Check player position
    local pos = ItemContext.current_position
    local map = ItemContext.current_map
    
    -- Check if near a known chest location
    for location_key, location_data in pairs(RandomizedItems) do
        if location_key:find("Chest") then
            -- TODO: Check distance to chest coordinates
            -- if Distance(pos, chest_pos) < 100 then
            --     return location_key
            -- end
        end
    end
    
    -- Strategy 2: Check if in shop
    if ItemContext.last_shop_id then
        return string.format("%s_Slot_%d", ItemContext.last_shop_id, item_id)
    end
    
    -- Strategy 3: Check story context
    -- TODO: Map story flags to locations
    
    return nil
end

---Grant a randomized item for a location
---@param location_key string
local function GrantRandomizedReward(location_key)
    local randomized = RandomizedItems[location_key]
    if not randomized then return end
    
    -- Use your existing ItemHandler to grant via Memory Bridge
    local ItemHandler = require("ItemHandler")
    ItemHandler.GrantItem(randomized.item_name, 1)
end

---Notify AP that a location was checked
---@param location_key string
local function NotifyAPLocationChecked(location_key)
    -- Write to checked_locations.txt
    local file = io.open("C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\memory_bridge\\ap_checked_locations.txt", "a")
    if file then
        file:write(location_key .. "\n")
        file:close()
    end
end

-- ============================================================================
-- Public API
-- ============================================================================

function ItemHook.Initialize()
    print("[ItemHook] Initializing function hooks...")
    
    -- STEP 1: Find actual function names using UE4SS Live View
    -- STEP 2: Uncomment and adjust these hooks
    
    -- HookAddItem()
    -- HookBattleReward()
    -- HookShopPurchase()
    
    print("[ItemHook] NOTE: Function hooks are DISABLED by default")
    print("[ItemHook] You must find actual function names and enable them manually")
end

function ItemHook.SetRandomizedItems(items_table)
    RandomizedItems = items_table
    print(string.format("[ItemHook] Loaded %d randomized locations", 
        #table.keys(RandomizedItems)))
end

function ItemHook.UpdateContext(map, position, shop_id)
    ItemContext.current_map = map or ItemContext.current_map
    ItemContext.current_position = position or ItemContext.current_position
    ItemContext.last_shop_id = shop_id
end

return ItemHook
