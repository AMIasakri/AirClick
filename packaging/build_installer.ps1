param(
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    throw "PyInstaller is not installed. Run: python -m pip install pyinstaller"
}

if (-not (Test-Path "hand_landmarker.task")) {
    throw "hand_landmarker.task is missing from the project root."
}

if (-not (Test-Path "packaging\AirClick.ico")) {
    throw "packaging\AirClick.ico is missing."
}

Get-Process pyinstaller,python -ErrorAction SilentlyContinue | ForEach-Object {
    $commandLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    if ($commandLine -match "PyInstaller|pyinstaller") {
        throw "Another PyInstaller build is still running (PID $($_.Id)). Close it and run this script again."
    }
}

pyinstaller --noconfirm --clean packaging\AirClick.spec
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE."
}

if (-not (Test-Path "dist\AirClick.exe")) {
    throw "PyInstaller completed without creating dist\AirClick.exe."
}

if ($SkipInstaller) {
    Write-Host "Standalone build created in dist\AirClick"
    exit 0
}

$isccCommand = Get-Command iscc -ErrorAction SilentlyContinue
$isccPath = if ($isccCommand) { $isccCommand.Source } else { $null }
if (-not $isccPath) {
    $knownPaths = @(
        "D:\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe"
    )
    $isccPath = $knownPaths | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $isccPath) {
    throw "Inno Setup is not installed or ISCC.exe could not be located."
}

& $isccPath packaging\AirClick.iss
Write-Host "Installer created in dist\installer"
