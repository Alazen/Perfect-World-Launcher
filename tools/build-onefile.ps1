[CmdletBinding()]
param(
    [switch]$SkipClean
)

$ErrorActionPreference = 'Stop'

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptRoot '..')

$venvDir = Join-Path $repoRoot '.venv'
$pythonExe = Join-Path $venvDir 'Scripts/python.exe'
$pyInstallerExe = Join-Path $venvDir 'Scripts/pyinstaller.exe'
$pysideRccExe = Join-Path $venvDir 'Scripts/pyside6-rcc.exe'

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe. Activate the virtual environment first."
}
if (-not (Test-Path $pyInstallerExe)) {
    throw "PyInstaller executable not found at $pyInstallerExe. Run 'pip install pyinstaller'."
}
if (-not (Test-Path $pysideRccExe)) {
    throw "pyside6-rcc executable not found at $pysideRccExe. Run 'pip install PySide6'."
}

$resourceQrc = Join-Path $repoRoot 'perfect_world_launcher_v23.0/launcher/resources/app_icon.qrc'
$resourcePy = Join-Path $repoRoot 'perfect_world_launcher_v23.0/launcher/resources/app_icon_rc.py'

Write-Verbose 'Regenerating Qt resources...'
& $pysideRccExe $resourceQrc -o $resourcePy

if (-not $SkipClean.IsPresent) {
    Write-Verbose 'Cleaning previous build artefacts...'
    Remove-Item (Join-Path $repoRoot 'build') -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $repoRoot 'dist') -Recurse -Force -ErrorAction SilentlyContinue
}

Push-Location $repoRoot
try {
    Write-Verbose 'Building single-file executable with PyInstaller...'
    & $pyInstallerExe --noconfirm --clean 'PerfectWorldLauncher.spec'
} finally {
    Pop-Location
}

$distDir = Join-Path $repoRoot 'dist'
$rawExe = Join-Path $distDir 'PerfectWorldLauncher.exe'
if (-not (Test-Path $rawExe)) {
    throw "Expected artefact $rawExe was not produced. Check the PyInstaller output."
}

$versionFile = Join-Path $repoRoot 'perfect_world_launcher_v23.0/launcher/version.py'
$versionLine = Get-Content $versionFile | Where-Object { $_ -match 'APP_VERSION\s*=\s*' } | Select-Object -First 1
if (-not $versionLine) {
    throw "Could not detect APP_VERSION in $versionFile."
}
$version = $versionLine -replace ".*'([^']+)'.*", '$1'

$finalName = "Perfect World Launcher v$version.exe"
$finalExe = Join-Path $distDir $finalName
Move-Item -Path $rawExe -Destination $finalExe -Force

Get-ChildItem -Path $distDir -File | Where-Object { $_.FullName -ne $finalExe } | Remove-Item -Force

Write-Host "Build complete: $finalExe"
