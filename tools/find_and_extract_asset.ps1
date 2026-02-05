#!/usr/bin/env powershell
<#
.SYNOPSIS
Search all pak files for a specific asset and extract it

.PARAMETER PakDirectory
Directory containing the .utoc files

.PARAMETER AssetName
Name of the asset to search for (e.g., "ShopItem")

.PARAMETER OutputDirectory
Directory to extract the asset to
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$PakDirectory,
    
    [Parameter(Mandatory=$true)]
    [string]$AssetName,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputDirectory,
    
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

# Create output directory if it doesn't exist
if (-not (Test-Path $OutputDirectory)) {
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
}

Write-Host "Searching for '$AssetName' in all pak files in: $PakDirectory" -ForegroundColor Cyan
Write-Host "Filter mode: $FilterMode" -ForegroundColor Cyan
if ($ExcludeSegments.Count -gt 0) {
    Write-Host "Exclude segments: $($ExcludeSegments -join ', ')" -ForegroundColor Cyan
}
if ($ExcludeExtensions.Count -gt 0) {
    Write-Host "Exclude extensions: $($ExcludeExtensions -join ', ')" -ForegroundColor Cyan
}

$utocFiles = @(Get-ChildItem -Path $PakDirectory -Filter "*.utoc" | Sort-Object Name)
$allFoundFiles = @()
$foundPaks = @()

for ($i = 0; $i -lt $utocFiles.Count; $i++) {
    $utocFile = $utocFiles[$i]
    Write-Host ""
    Write-Host "[$($i+1)/$($utocFiles.Count)] Searching in: $($utocFile.Name)" -ForegroundColor Yellow
    
    $tempDir = Join-Path $OutputDirectory "temp_$([System.IO.Path]::GetRandomFileName())"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    # Try to unpack with filter
    $retocArgs = @(
        "unpack",
        $utocFile.FullName,
        $tempDir,
        "--filter", $AssetName,
        "--filter-mode", $FilterMode
    )

    foreach ($seg in $ExcludeSegments) {
        $retocArgs += @("--exclude-segment", $seg)
    }
    foreach ($ext in $ExcludeExtensions) {
        $retocArgs += @("--exclude-ext", $ext)
    }

    $result = & $RetocPath @retocArgs 2>&1
    
    # Check if any files were extracted
    $extractedFiles = @(Get-ChildItem -Path $tempDir -Recurse -File -ErrorAction SilentlyContinue)
    
    if ($extractedFiles.Count -gt 0) {
        Write-Host "Found in $($utocFile.Name)" -ForegroundColor Green
        Write-Host "  Files extracted:"
        $extractedFiles | ForEach-Object {
            $relPath = $_.FullName.Substring($tempDir.Length + 1)
            Write-Host "  - $relPath" -ForegroundColor Green
        }
        
        # Move extracted files to final output directory
        $extractedFiles | ForEach-Object {
            $relPath = $_.FullName.Substring($tempDir.Length + 1)
            $destPath = Join-Path $OutputDirectory $relPath
            $destDir = Split-Path $destPath
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Force -Path $destDir | Out-Null
            }
            Copy-Item $_.FullName $destPath -Force
            $allFoundFiles += $destPath
        }
        
        $foundPaks += $utocFile.Name
    }
    else {
        Write-Host "  (not found)" -ForegroundColor Gray
    }
    
    # Clean up temp directory
    if (Test-Path $tempDir) {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if ($allFoundFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "Asset extraction complete!" -ForegroundColor Green
    Write-Host "  Total files found: $($allFoundFiles.Count)" -ForegroundColor Green
    Write-Host "  Found in pak chunks: $($foundPaks -join ', ')" -ForegroundColor Green
    Write-Host "  Output directory: $OutputDirectory" -ForegroundColor Green
    Write-Host ""
    Write-Host "Extracted files:" -ForegroundColor Cyan
    $allFoundFiles | ForEach-Object {
        $relPath = $_.Substring($OutputDirectory.Length + 1)
        $size = (Get-Item $_).Length
        Write-Host "  - $relPath ($([string]::Format('{0:N0}', $size)) bytes)" -ForegroundColor Cyan
    }
}
else {
    Write-Host ""
    Write-Host "'$AssetName' not found in any pak file" -ForegroundColor Red
}

