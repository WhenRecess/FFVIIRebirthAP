-- HTTP Client for Memory Bridge communication
-- Pure Lua socket implementation for UE4SS (no external dependencies)

local HttpClient = {}
local fallbackFilePath = nil

function HttpClient.SetFallbackFilePath(path)
    fallbackFilePath = path
end

-- Simple socket connection using Windows API
function HttpClient.SendRequest(method, url, body)
    -- Parse URL
    local host, port, path = url:match("http://([^:]+):(%d+)(/.*)")
    if not host then
        host, path = url:match("http://([^/]+)(/.*)") 
        port = 80
    end
    port = tonumber(port) or 80
    
    -- Try to use UE4SS socket if available
    -- Otherwise, use fallback file-based communication
    
    local success, socket = pcall(require, "socket")
    if not success then
        -- UE4SS doesn't have socket library, try alternative
        return HttpClient.SendRequestFallback(method, url, body)
    end
    
    -- Create TCP socket
    local tcp = socket.tcp()
    tcp:settimeout(5) -- 5 second timeout
    
    local ok, err = tcp:connect(host, port)
    if not ok then
        return false, "Connection failed: " .. tostring(err)
    end
    
    -- Build HTTP request
    local request = method .. " " .. path .. " HTTP/1.1\r\n"
    request = request .. "Host: " .. host .. "\r\n"
    request = request .. "Connection: close\r\n"
    
    if body then
        request = request .. "Content-Type: application/json\r\n"
        request = request .. "Content-Length: " .. #body .. "\r\n"
        request = request .. "\r\n"
        request = request .. body
    else
        request = request .. "\r\n"
    end
    
    -- Send request
    tcp:send(request)
    
    -- Receive response
    local response = ""
    while true do
        local chunk, err = tcp:receive(1024)
        if not chunk then break end
        response = response .. chunk
    end
    
    tcp:close()
    
    -- Parse response status
    local status = response:match("HTTP/[%d.]+ (%d+)")
    if status == "200" then
        -- Extract JSON body
        local jsonBody = response:match("\r\n\r\n(.+)$")
        return true, jsonBody
    else
        return false, "HTTP " .. (status or "error")
    end
end

-- Fallback: Use Windows named pipe or file-based IPC
function HttpClient.SendRequestFallback(method, url, body)
    -- Preferred fallback: file-based IPC
    if fallbackFilePath and body then
        local file = io.open(fallbackFilePath, "a")
        if file then
            file:write(body)
            file:write("\n")
            file:close()
            return true, "file-ipc"
        end
    end

    -- Alternative: Try to execute curl if available (may not work in UE4SS sandbox)
    local curlCmd = string.format('curl -s -X %s "%s"', method, url)
    
    if body then
        -- Escape JSON for command line
        local escapedBody = body:gsub('"', '\\"')
        curlCmd = curlCmd .. string.format(' -H "Content-Type: application/json" -d "%s"', escapedBody)
    end
    
    local handle = io.popen(curlCmd)
    if handle then
        local result = handle:read("*a")
        handle:close()
        if result and #result > 0 then
            return true, result
        end
    end
    
    return false, "No HTTP client available"
end

-- Simple POST wrapper
function HttpClient.Post(url, data)
    local json = ""
    if type(data) == "table" then
        -- Simple JSON encoding (no external library)
        local pairs_list = {}
        for k, v in pairs(data) do
            if type(v) == "number" then
                table.insert(pairs_list, string.format('"%s":%d', k, v))
            elseif type(v) == "string" then
                table.insert(pairs_list, string.format('"%s":"%s"', k, v))
            elseif type(v) == "boolean" then
                table.insert(pairs_list, string.format('"%s":%s', k, tostring(v)))
            end
        end
        json = "{" .. table.concat(pairs_list, ",") .. "}"
    else
        json = tostring(data)
    end
    
    return HttpClient.SendRequest("POST", url, json)
end

-- Simple GET wrapper  
function HttpClient.Get(url)
    return HttpClient.SendRequest("GET", url, nil)
end

return HttpClient
