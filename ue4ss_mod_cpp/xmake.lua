-- xmake build script for FFVII Rebirth Archipelago UE4SS C++ Mod
-- Based on LiesOfAP pattern
-- 
-- Prerequisites:
-- 1. Clone RE-UE4SS (or UE4SS source) to parent directory
-- 2. Run: xmake build
-- 
-- Install:
-- Copy the built DLL to FFVII Rebirth's Win64/Mods/FFVIIRebirthAP/dlls/ folder

local projectName = "FFVIIRebirthAP"

-- Include UE4SS as a dependency (clone RE-UE4SS to ../RE-UE4SS)
includes("../RE-UE4SS")

target(projectName)
    add_rules("ue4ss.mod")
    
    -- Source files
    add_files("src/*.cpp")
    add_files("dllmain.cpp")
    
    -- Include directories
    add_includedirs("include")
    
    -- For AP client support (optional, can add later)
    -- add_includedirs("dependencies/apclientpp")
    -- add_includedirs("dependencies/json/include")
    -- add_includedirs("dependencies/websocketpp")
    -- add_includedirs("dependencies/asio/include")
    
    -- Header files (for IDE support)
    add_headerfiles("include/*.hpp", {install = false})
    
    -- Windows definitions
    add_defines("_WIN32_WINNT=0x0600")
    add_defines("UNICODE", "_UNICODE")
    
    -- C++20 support
    add_cxxflags("/Zc:__cplusplus")
    add_cxxflags("/std:c++20")
