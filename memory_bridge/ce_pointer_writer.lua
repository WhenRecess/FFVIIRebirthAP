-- Cheat Engine Lua script: writes binven_ptr to pointer.txt periodically
-- Requires Inventory/Item Control script enabled so binven_ptr updates

local pointerFile = "C:\\Users\\jeffk\\OneDrive\\Documents\\GitHub\\FFVIIRebirthAP\\memory_bridge\\pointer.txt"

if pointerWriterTimer then
    pointerWriterTimer.destroy()
    pointerWriterTimer = nil
end

pointerWriterTimer = createTimer(nil)
pointerWriterTimer.Interval = 500
pointerWriterTimer.OnTimer = function()
    local ok, addr = pcall(getAddress, "binven_ptr")
    if not ok or addr == nil or addr == 0 then return end

    local basePtr = readQword(addr)
    if basePtr == nil or basePtr == 0 then return end

    local f = io.open(pointerFile, "w")
    if f then
        f:write(string.format("0x%X", basePtr))
        f:close()
    end
end

print("binven_ptr writer active -> " .. pointerFile)
