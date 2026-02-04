--[[
    Shop Item Runtime Patcher
    Hooks shop data loading and modifies items at runtime
]]

local ShopPatcher = {}

-- Price test overrides (for testing)
ShopPatcher.PriceOverrides = {
    ["M_MAG_109"] = 200,  -- Test: Change Junon materia from 30 to 200
}

function ShopPatcher:Init()
    print("[ShopPatcher] Initializing shop item patcher...")
    
    -- Hook shop UI functions that setup item display
    self:HookShopDisplayFunctions()
    
    print("[ShopPatcher] Setting up DataTable load hook...")
end

function ShopPatcher:HookShopDisplayFunctions()
    print("[ShopPatcher] Attempting to hook shop display functions...")
    
    -- Try to hook the function that sets up shop items for display
    local success, result = pcall(function()
        return RegisterHook("/Script/EndGame.EndShopItemInfoWindow:OnCoreListSetupItem", function(Self, Index, ItemData)
            print("[ShopPatcher] ===== OnCoreListSetupItem CALLED! =====")
            print(string.format("[ShopPatcher] Self: %s", tostring(Self)))
            print(string.format("[ShopPatcher] Index: %s", tostring(Index)))
            print(string.format("[ShopPatcher] ItemData: %s", tostring(ItemData)))
            
            -- Try to inspect ItemData if it's valid
            if ItemData and ItemData:IsValid() then
                print(string.format("[ShopPatcher] ItemData class: %s", ItemData:GetClass():GetFullName()))
            end
        end)
    end)
    
    if success then
        print("[ShopPatcher] Successfully hooked OnCoreListSetupItem")
    else
        print("[ShopPatcher] Could not hook OnCoreListSetupItem: " .. tostring(result))
    end
    
    -- Try to hook materia shop setup
    success, result = pcall(function()
        return RegisterHook("/Script/EndGame.EndMainMateriaListBoxWindow:OnSetupItemForShop", function(Self, ItemData)
            print("[ShopPatcher] ===== OnSetupItemForShop CALLED! =====")
            print(string.format("[ShopPatcher] Self: %s", tostring(Self)))
            print(string.format("[ShopPatcher] ItemData: %s", tostring(ItemData)))
            
            -- Try to inspect ItemData
            if ItemData and ItemData:IsValid() then
                print(string.format("[ShopPatcher] ItemData class: %s", ItemData:GetClass():GetFullName()))
            end
        end)
    end)
    
    if success then
        print("[ShopPatcher] Successfully hooked OnSetupItemForShop")
    else
        print("[ShopPatcher] Could not hook OnSetupItemForShop: " .. tostring(result))
    end
end

function ShopPatcher:FindAndHookShopTables()
    print("[ShopPatcher] Searching for shop item instances...")
    
    -- Try to find the actual ShopItem instance
    local shopItem = StaticFindObject("EndDataObjectShopItem /Game/DataObject/Resident/ShopItem.ShopItem", true)
    if shopItem and shopItem:IsValid() then
        print(string.format("[ShopPatcher] FOUND ShopItem instance: %s", shopItem:GetFullName()))
        print(string.format("[ShopPatcher] ShopItem class: %s", shopItem:GetClass():GetFullName()))
        
        -- Try to access and modify properties
        -- We'll print what we find for now
        print("[ShopPatcher] ShopItem found - ready for property access")
    else
        print("[ShopPatcher] ShopItem instance not found, searching...")
        
        -- Search broadly
        local allObjects = FindAllOf("Object")
        if allObjects then
            local count = 0
            for i, obj in ipairs(allObjects) do
                if obj:IsValid() then
                    local name = obj:GetFullName()
                    if name:find("ShopItem") and name:find("/Game/DataObject") then
                        if count < 5 then
                            print(string.format("[ShopPatcher] Found: %s", name))
                            count = count + 1
                        end
                    end
                end
            end
        end
    end
end

function ShopPatcher:PatchShopItem(itemData)
    -- Modify itemData based on our price overrides
    if not itemData or not itemData.ItemId then
        return
    end
    
    local itemId = itemData.ItemId
    
    if self.PriceOverrides[itemId] then
        if itemData.OverridePrice_Array and #itemData.OverridePrice_Array > 0 then
            itemData.OverridePrice_Array[1] = self.PriceOverrides[itemId]
            print(string.format("[ShopPatcher] Changed price for %s to %d", itemId, self.PriceOverrides[itemId]))
        end
    end
end

return ShopPatcher
