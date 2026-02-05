#!/usr/bin/env powershell
<#
.SYNOPSIS
Extract asset from FF7R game paks, optionally converting from Zen to Legacy format

.PARAMETER PakDirectory
Directory containing the .utoc files (the Paks folder)

.PARAMETER AssetName
Name/path of the asset to search for (e.g., "ShopItem" or "DataObject/Resident/ShopItem")

.PARAMETER OutputDirectory
Directory to extract the asset to

.PARAMETER ConvertToLegacy
If $true, converts Zen format to Legacy format (.uasset + .uexp split)
If $false, extracts raw Zen format (.uasset only with bundled data)

.PARAMETER RetocPath
Path to retoc executable
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PakDirectory,
    
    [Parameter(Mandatory=$true)]
    [string]$AssetName,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputDirectory,
    
    [bool]$ConvertToLegacy = $true,

    [ValidateSet("substring", "file-name", "path-segment", "exact-path")]
    [string]$FilterMode = "path-segment",

    [string[]]$ExcludeSegments = @(
        "Texture",
        "Material",
        "UI",
        "Menu",
        "Environment",
        "Motion",
        "VFX",
        "Effect",
        "Sound",
        "Audio",
        "Animation",
        "Anim",
        "Niagara",
        "MovieScene",
        "Widget"
    ),

    [string[]]$ExcludeExtensions = @(),
    
    [string]$RetocPath = ".\bin\retoc_filtered.exe"
)

Write-Host "=== FF7R Asset Extraction ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Asset: $AssetName" -ForegroundColor Yellow
Write-Host "Pak Directory: $PakDirectory" -ForegroundColor Yellow
Write-Host "Output Directory: $OutputDirectory" -ForegroundColor Yellow
Write-Host "Convert to Legacy: $ConvertToLegacy" -ForegroundColor Yellow
Write-Host "Filter mode: $FilterMode" -ForegroundColor Yellow
if ($ExcludeSegments.Count -gt 0) {
    Write-Host "Exclude segments: $($ExcludeSegments -join ', ')" -ForegroundColor Yellow
}
if ($ExcludeExtensions.Count -gt 0) {
    Write-Host "Exclude extensions: $($ExcludeExtensions -join ', ')" -ForegroundColor Yellow
}
Write-Host ""

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDirectory)) {
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
}

$command = if ($ConvertToLegacy) { "to-legacy" } else { "unpack" }

Write-Host "Using '$command' command..." -ForegroundColor Cyan
Write-Host ""

try {
    if ($ConvertToLegacy) {
        # Use to-legacy to convert Zen format to Legacy format
        Write-Host "Converting from Zen/IoStore to Legacy format..." -ForegroundColor Yellow
        $retocArgs = @(
            "to-legacy",
            $PakDirectory,
            $OutputDirectory,
            "--filter", $AssetName,
            "--filter-mode", $FilterMode,
            "--version", "UE4_26",
            "-v"
        )
        foreach ($seg in $ExcludeSegments) {
            $retocArgs += @("--exclude-segment", $seg)
        }
        foreach ($ext in $ExcludeExtensions) {
            $retocArgs += @("--exclude-ext", $ext)
        }

        $result = & $RetocPath @retocArgs 2>&1
    }
    else {
        # Use unpack to extract raw Zen format
        Write-Host "Extracting raw Zen format..." -ForegroundColor Yellow
        $retocArgs = @(
            "unpack",
            "$PakDirectory\pakchunk3-WindowsNoEditor.utoc",
            $OutputDirectory,
            "--filter", $AssetName,
            "--filter-mode", $FilterMode,
            "-v"
        )
        foreach ($seg in $ExcludeSegments) {
            $retocArgs += @("--exclude-segment", $seg)
        }
        foreach ($ext in $ExcludeExtensions) {
            $retocArgs += @("--exclude-ext", $ext)
        }

        $result = & $RetocPath @retocArgs 2>&1
    }
    
    Write-Host ""
    Write-Host "Command output:" -ForegroundColor Gray
    $result | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    Write-Host ""
    
    # Check if any files were extracted
    $extractedFiles = @(Get-ChildItem -Path $OutputDirectory -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*$($AssetName.Split('/')[-1])*" })
    
    if ($extractedFiles.Count -gt 0) {
        Write-Host "Extraction successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Extracted files:" -ForegroundColor Cyan
        $extractedFiles | ForEach-Object {
            $size = "{0:N0}" -f $_.Length
            Write-Host "  - $($_.Name) ($size bytes)" -ForegroundColor Cyan
            Write-Host "    Path: $($_.FullName)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "No files extracted - asset may not have been found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error during extraction: $_" -ForegroundColor Red
    exit 1
}
