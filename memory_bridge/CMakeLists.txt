cmake_minimum_required(VERSION 3.15)
project(FFVIIRebirthMemoryBridge)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCES
    main.cpp
    MemoryBridge.cpp
)

set(HEADERS
    MemoryBridge.h
)

# Create executable
add_executable(MemoryBridge ${SOURCES} ${HEADERS})

# Link Windows libraries
target_link_libraries(MemoryBridge ws2_32)

# Set output directory
set_target_properties(MemoryBridge PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

# Windows-specific settings
if(WIN32)
    # Set subsystem to console
    set_target_properties(MemoryBridge PROPERTIES
        LINK_FLAGS "/SUBSYSTEM:CONSOLE"
    )
endif()
