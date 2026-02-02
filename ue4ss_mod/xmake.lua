-- xmake build configuration for FFVIIRebirthAP UE4SS mod

set_project("FFVIIRebirthAP")
set_version("0.1.0")
set_languages("cxx20")

-- Define the DLL target
target("FFVIIRebirthAP")
    set_kind("shared")
    
    -- Source files
    add_files("src/*.cpp")
    add_files("dllmain.cpp")
    
    -- Include directories
    add_includedirs("include", {public = true})
    
    -- Define preprocessor macros
    add_defines("UNICODE", "_UNICODE")
    
    -- Windows-specific settings
    if is_plat("windows") then
        add_cxflags("/EHsc")
        add_ldflags("/DLL")
    end
    
    -- TODO: Add UE4SS SDK include paths when available
    -- add_includedirs("path/to/UE4SS/SDK/include")
    
    -- TODO: Add AP client library when available
    -- add_links("apclient")
    -- add_linkdirs("path/to/apclient/lib")
    
    -- Output directory
    set_targetdir("$(buildir)/bin")
    
    -- Add optimization for release builds
    if is_mode("release") then
        set_optimize("fastest")
        set_warnings("all")
    else
        set_optimize("none")
        set_symbols("debug")
        set_warnings("all")
    end
