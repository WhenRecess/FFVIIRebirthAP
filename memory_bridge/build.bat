@echo off
REM Build script for Memory Bridge
REM Requires Visual Studio or MinGW

echo =========================================
echo   Building FF7 Rebirth Memory Bridge
echo =========================================
echo.

REM Try to find Visual Studio Developer Command Prompt
if exist "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2026 Community
    call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    goto :build_msvc
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2022 Community
    call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    goto :build_msvc
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    echo Found Visual Studio 2019 Community
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
    goto :build_msvc
)

REM Try MinGW
where g++ >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found MinGW g++
    goto :build_mingw
)

echo ERROR: No compiler found!
echo.
echo Please install one of:
echo - Visual Studio 2019/2022 with C++ tools
echo - MinGW-w64
echo.
pause
exit /b 1

:build_msvc
echo Building with MSVC...
cl /EHsc /std:c++17 /O2 /Fe:MemoryBridge.exe main.cpp MemoryBridge.cpp /link ws2_32.lib
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! MemoryBridge.exe created
    goto :done
) else (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)

:build_mingw
echo Building with MinGW...
g++ -std=c++17 -O2 -o MemoryBridge.exe main.cpp MemoryBridge.cpp -lws2_32 -static-libgcc -static-libstdc++
if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! MemoryBridge.exe created
    goto :done
) else (
    echo.
    echo BUILD FAILED
    pause
    exit /b 1
)

:done
echo.
echo =========================================
echo.
echo To use:
echo 1. Run MemoryBridge.exe
echo 2. Launch FF7 Rebirth
echo 3. Bridge will auto-attach
echo.
echo =========================================
pause
