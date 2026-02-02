-- xmake build script for FFVII Rebirth Archipelago UE4SS Mod
-- Based on similar projects like LiesOfAP
-- Usage: xmake build

set_xmakever("2.8.0")

-- Set project info
set_project("FFVIIRebirthAP")
set_version("0.1.0")
set_languages("c++20")

-- Add build modes
add_rules("mode.debug", "mode.release")

-- Platform and architecture settings
set_arch("x64")

-- Define the DLL target
target("FFVIIRebirthAP")
    set_kind("shared")
    
    -- Add source files
    add_files("src/*.cpp")
    add_files("dllmain.cpp")
    
    -- Add header search paths
    add_includedirs("include")
    
    -- Add preprocessor definitions
    add_defines("UNICODE", "_UNICODE")
    if is_mode("debug") then
        add_defines("_DEBUG")
    else
        add_defines("NDEBUG")
    end
    
    -- Add compiler flags
    add_cxxflags("/permissive-", "/W4", "/EHsc")
    if is_mode("release") then
        add_cxxflags("/O2")
    end
    
    -- Add linker flags
    add_ldflags("/SUBSYSTEM:WINDOWS")
    
    -- TODO: Add UE4SS SDK include paths when available
    -- add_includedirs("path/to/UE4SS/include")
    
    -- TODO: Add apclient library when available
    -- add_includedirs("path/to/apclient/include")
    -- add_linkdirs("path/to/apclient/lib")
    -- add_links("apclient")
    
    -- Output directory
    set_targetdir("$(buildir)/$(mode)/$(plat)/$(arch)")
    
    -- After build, copy to output
    after_build(function (target)
        print("Built: " .. target:targetfile())
        print("Install to: <UE4SS_Mods_Directory>/FFVIIRebirthAP/dlls/main.dll")
    end)

target_end()

-- Build all targets
add_requires("vcpkg::nlohmann_json", {optional = true})
