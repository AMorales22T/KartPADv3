param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if ($Clean) {
    Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
}

python -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name KartPADv3 `
  --icon assets/kartpadv3.ico `
  --add-data "assets;assets" `
  --add-data "static;static" `
  --add-data "LICENSE;." `
  desktop_launcher.py
