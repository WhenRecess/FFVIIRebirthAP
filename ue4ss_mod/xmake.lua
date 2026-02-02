-- xmake.lua for FFVIIRebirthAP UE4SS Mod

-- Set the project name
set_project("FFVIIRebirthAP")

-- Set the C++ standard
set_languages("c++20")

-- Define build modes
add_rules("mode.debug", "mode.release")

-- Include directories
includes("include")

-- Target: FFVIIRebirthAP DLL
target("FFVIIRebirthAP")
    set_kind("shared")
    
    -- Source files
    add_files("src/*.cpp")
    add_files("dllmain.cpp")
    
    -- Header files
    add_headerfiles("include/*.hpp")
    add_includedirs("include")
    
    -- UE4SS SDK paths (adjust these based on your environment)
    -- You need to set UE4SS_SDK_PATH environment variable or edit paths here
    add_includedirs("$(env UE4SS_SDK_PATH)/include", {public = false})
    add_linkdirs("$(env UE4SS_SDK_PATH)/lib")
    
    -- apclient C++ library paths (adjust based on your setup)
    -- You need to set APCLIENT_PATH environment variable or edit paths here
    add_includedirs("$(env APCLIENT_PATH)/include", {public = false})
    add_linkdirs("$(env APCLIENT_PATH)/lib")
    
    -- Link libraries
    add_links("UE4SS")
    add_links("apclient")
    
    -- Windows-specific settings
    if is_plat("windows") then
        add_defines("UNICODE", "_UNICODE")
        add_cxflags("/EHsc")
        add_ldflags("/SUBSYSTEM:WINDOWS", "/DLL")
    end
    
    -- Output directory
    set_targetdir("bin/$(mode)/$(plat)/$(arch)")
    set_objectdir("build/$(mode)/$(plat)/$(arch)")
    
-- TODO: Add tasks for copying DLL to game directory
-- task("install")
--     on_run(function ()
--         print("Copying DLL to game Mods directory...")
--         os.cp("bin/release/windows/x64/FFVIIRebirthAP.dll", 
--               "<GAME_DIR>/Binaries/Win64/Mods/FFVIIRebirthAP/")
--     end)
-- task_end()
