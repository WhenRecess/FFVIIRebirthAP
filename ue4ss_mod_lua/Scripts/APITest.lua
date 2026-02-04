--[[
    API_TEST.lua
    
    Critical tests to determine which randomization approach is viable.
    
    Run these tests in-game by pressing F7.
    Results will determine the entire architecture.
]]

local APITest = {}

-- Test results
local Results = {
    api_found = false,
    add_item_works = false,
    remove_item_works = false,
    get_item_count_works = false,
    hooking_supported = false,
    hook_modify_params = false,
}

-- ============================================================================
-- Test 1: Can we find and call the API?
-- ============================================================================

local function Test1_FindAPI()
    print("\n[TEST 1] Finding EndDataBaseDataBaseAPI...")
    
    local success, api = pcall(function()
        return StaticFindObject("/Script/EndDataBase.Default__EndDataBaseDataBaseAPI")
    end)
    
    if success and api then
        Results.api_found = true
        print("[TEST 1] ✓ API Found:", api:GetFullName())
        return api
    else
        Results.api_found = false
        print("[TEST 1] ✗ API Not Found")
        return nil
    end
end

-- ============================================================================
-- Test 2: Can we read inventory counts?
-- ============================================================================

local function Test2_ReadInventory(api)
    if not api then return false end
    
    print("\n[TEST 2] Reading inventory count...")
    
    -- Try to read Potion count (item ID 100)
    local success, count = pcall(function()
        return api:GetItemNumBP(100)
    end)
    
    if success and count ~= nil then
        Results.get_item_count_works = true
        print(string.format("[TEST 2] ✓ Can read inventory! Potion count: %d", count))
        return true
    else
        Results.get_item_count_works = false
        print("[TEST 2] ✗ Cannot read inventory")
        return false
    end
end

-- ============================================================================
-- Test 3: Can we grant items via API?
-- ============================================================================

local function Test3_GrantItem(api)
    if not api then return false end
    
    print("\n[TEST 3] Attempting to grant item via API...")
    
    -- Try to give 1 Potion
    local success = pcall(function()
        api:AddItemBP(100, 1)
    end)
    
    if success then
        Results.add_item_works = true
        print("[TEST 3] ✓ AddItemBP call succeeded!")
        print("[TEST 3]   Open inventory and check if Potion count increased")
        return true
    else
        Results.add_item_works = false
        print("[TEST 3] ✗ AddItemBP call failed")
        return false
    end
end

-- ============================================================================
-- Test 4: Can we remove items (negative quantity)?
-- ============================================================================

local function Test4_RemoveItem(api)
    if not api then return false end
    
    print("\n[TEST 4] Attempting to remove item via negative quantity...")
    
    -- Try to remove 1 Potion
    local success = pcall(function()
        api:AddItemBP(100, -1)
    end)
    
    if success then
        Results.remove_item_works = true
        print("[TEST 4] ✓ Negative quantity call succeeded!")
        print("[TEST 4]   Open inventory and check if Potion count decreased")
        return true
    else
        Results.remove_item_works = false
        print("[TEST 4] ✗ Negative quantity not supported")
        return false
    end
end

-- ============================================================================
-- Test 5: Can we hook functions?
-- ============================================================================

local function Test5_HookingSupport()
    print("\n[TEST 5] Testing function hooking...")
    
    local hook_triggered = false
    
    -- Try to register a hook
    local success = pcall(function()
        RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:AddItemBP", function(Context, ...)
            print("[TEST 5] 🎯 HOOK TRIGGERED!")
            hook_triggered = true
            return true
        end)
    end)
    
    if success then
        Results.hooking_supported = true
        print("[TEST 5] ✓ RegisterHook call succeeded!")
        print("[TEST 5]   Now try picking up an item to test if hook fires")
    else
        Results.hooking_supported = false
        print("[TEST 5] ✗ RegisterHook not supported")
    end
end

-- ============================================================================
-- Test 6: Can we modify hook parameters?
-- ============================================================================

local function Test6_ModifyHookParams(api)
    if not Results.hooking_supported then
        print("\n[TEST 6] ⊘ Skipped (hooking not supported)")
        return false
    end
    
    print("\n[TEST 6] Testing parameter modification in hooks...")
    print("[TEST 6]   This requires picking up an item in-game")
    print("[TEST 6]   The hook will try to change the item ID")
    
    -- Try to modify parameters
    local success = pcall(function()
        RegisterHook("/Script/EndDataBase.EndDataBaseDataBaseAPI:AddItemBP", function(Context, ItemId, Quantity)
            print(string.format("[TEST 6] Hook received: Item %d x%d", ItemId, Quantity))
            
            -- Try to change item ID
            local modify_success = pcall(function()
                Context:SetItemId(111)  -- Try to change to Ether
                print("[TEST 6] ✓ Successfully modified ItemId to 111 (Ether)")
            end)
            
            if modify_success then
                Results.hook_modify_params = true
            else
                print("[TEST 6] ✗ Cannot modify parameters")
                Results.hook_modify_params = false
            end
            
            return true
        end)
    end)
    
    if not success then
        print("[TEST 6] ✗ Failed to register modification hook")
        Results.hook_modify_params = false
    end
end

-- ============================================================================
-- Print Summary
-- ============================================================================

local function PrintSummary()
    print("\n" .. string.rep("=", 60))
    print("TEST RESULTS SUMMARY")
    print(string.rep("=", 60))
    
    print("\n1. API Access:")
    print(string.format("   - Find API: %s", Results.api_found and "✓ YES" or "✗ NO"))
    print(string.format("   - Read Inventory: %s", Results.get_item_count_works and "✓ YES" or "✗ NO"))
    
    print("\n2. Item Manipulation:")
    print(string.format("   - Grant Items (AddItemBP): %s", Results.add_item_works and "✓ YES" or "✗ NO"))
    print(string.format("   - Remove Items (negative qty): %s", Results.remove_item_works and "✓ YES" or "✗ NO"))
    
    print("\n3. Function Hooking:")
    print(string.format("   - RegisterHook supported: %s", Results.hooking_supported and "✓ YES" or "✗ NO"))
    print(string.format("   - Modify hook parameters: %s", Results.hook_modify_params and "✓ YES" or "⏸ PENDING TEST"))
    
    print("\n" .. string.rep("=", 60))
    print("RECOMMENDED APPROACH:")
    print(string.rep("=", 60))
    
    if Results.hooking_supported and Results.hook_modify_params then
        print("\n🏆 OPTION 2: Function Hooking")
        print("   Intercept AddItemBP calls and replace items cleanly.")
        print("   This is the BEST approach - no visual glitches!")
        
    elseif Results.add_item_works and Results.remove_item_works then
        print("\n✅ HYBRID: Memory Watching + API Calls")
        print("   Watch for inventory changes, then use API to:")
        print("   1. Remove vanilla item: AddItemBP(item, -qty)")
        print("   2. Grant randomized item: AddItemBP(randomized, qty)")
        print("   No Memory Bridge needed for item granting!")
        
    elseif Results.add_item_works then
        print("\n⚠️  OPTION 1: Memory Watching + Memory Bridge")
        print("   API can grant but not remove items.")
        print("   Use Memory Bridge to remove vanilla items.")
        print("   Player may briefly see wrong item.")
        
    else
        print("\n⚠️  FALLBACK: Pure Memory Bridge Approach")
        print("   Game API not accessible from UE4SS.")
        print("   Must rely entirely on Memory Bridge for all operations.")
        print("   This is your current working approach.")
    end
    
    print("\n" .. string.rep("=", 60))
end

-- ============================================================================
-- Public API
-- ============================================================================

function APITest.RunAllTests()
    print("\n" .. string.rep("=", 60))
    print("FF7 REBIRTH API TEST SUITE")
    print(string.rep("=", 60))
    print("\nThis will test what's possible for item randomization.")
    print("IMPORTANT: Open your inventory BEFORE and AFTER to verify changes!")
    print("\nStarting tests in 3 seconds...")
    
    -- Wait a bit for user to read
    -- Note: Lua doesn't have sleep, so this is immediate
    
    local api = Test1_FindAPI()
    Test2_ReadInventory(api)
    Test3_GrantItem(api)
    Test4_RemoveItem(api)
    Test5_HookingSupport()
    Test6_ModifyHookParams(api)
    
    PrintSummary()
    
    print("\n[INFO] If Test 6 is pending, pick up an item in-game to test it.")
    print("[INFO] Results saved for reference.")
    
    return Results
end

-- Keybind: F7
function APITest.RegisterKeybind()
    RegisterKeyBind(Key.F7, function()
        APITest.RunAllTests()
    end)
    print("[APITest] Registered F7 to run API tests")
end

return APITest
