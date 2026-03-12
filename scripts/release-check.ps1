param(
    [switch]$SkipTests,
    [switch]$OpenDist
)

$ErrorActionPreference = "Stop"

function Step($msg) {
    Write-Host ""
    Write-Host "==> $msg" -ForegroundColor Cyan
}

function Run-Checked([scriptblock]$Command, [string]$StepName) {
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$StepName failed with exit code $LASTEXITCODE"
    }
}

Step "Python environment check"
Run-Checked { python --version } "Python version check"

Step "Checking PyInstaller availability"
Run-Checked { python -m PyInstaller --version } "PyInstaller check"

if (-not $SkipTests) {
    Step "Running test suite"
    Run-Checked { python -m pytest -q } "Test suite"
}

Step "Building Windows .exe (release-like)"
Run-Checked {
    python -m PyInstaller --noconfirm --clean --onefile --windowed --name Metal-Lattice-Visualisation main.py
} "PyInstaller build"

$exePath = Join-Path -Path (Get-Location) -ChildPath "dist\\Metal-Lattice-Visualisation.exe"
if (-not (Test-Path $exePath)) {
    throw "Build finished without exe: $exePath"
}

Step "Build finished"
Write-Host "EXE: $exePath" -ForegroundColor Green

if ($OpenDist) {
    Step "Opening dist folder"
    Start-Process explorer.exe (Join-Path -Path (Get-Location) -ChildPath "dist")
}
