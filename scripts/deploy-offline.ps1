#Requires -RunAsAdministrator
# Install HAL-AI stack from docs/src/ on an air-gapped Windows Server.
# Run AFTER transferring docs/src/ to this machine.
# Requires: Podman for Windows pre-installed (winget install RedHat.Podman)

param(
    [switch]$SkipVerify,
    [switch]$SkipOllama,
    [switch]$SkipPodman,
    [switch]$SkipModels
)

$ErrorActionPreference = "Stop"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleDir  = Join-Path $ScriptDir "..\docs\src"

function Log($msg) { Write-Host "[$(Get-Date -Format HH:mm:ss)] $msg" }
function Die($msg) { Write-Error "ERROR: $msg"; exit 1 }

if (-not (Test-Path $BundleDir)) { Die "Bundle dir not found: $BundleDir" }

function Verify-Bundle {
    Log "Verifying bundle checksums..."
    $checksumFile = Join-Path $BundleDir "checksums.sha256"
    if (-not (Test-Path $checksumFile)) { Die "checksums.sha256 not found. Was download.sh run?" }

    $failures = @()
    foreach ($line in Get-Content $checksumFile) {
        if ($line -match "^([a-f0-9]{64})\s+(.+)$") {
            $expected = $Matches[1]
            $relPath  = $Matches[2]
            $fullPath = Join-Path $BundleDir $relPath
            if (-not (Test-Path $fullPath)) {
                $failures += "MISSING: $relPath"
                continue
            }
            $actual = (Get-FileHash $fullPath -Algorithm SHA256).Hash.ToLower()
            if ($actual -ne $expected) { $failures += "MISMATCH: $relPath" }
        }
    }
    if ($failures.Count -gt 0) {
        $failures | ForEach-Object { Write-Host $_ }
        Die "Bundle verification failed."
    }
    Log "All checksums OK."
}

function Install-Ollama {
    $installer = Join-Path $BundleDir "installers\OllamaSetup.exe"
    if (-not (Test-Path $installer)) { Die "Missing: $installer" }

    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Log "Ollama already installed, skipping."
        return
    }

    Log "Installing Ollama..."
    Start-Process -FilePath $installer -ArgumentList "/S" -Wait
    Log "Ollama installed. Service starts automatically."
}

function Load-ContainerImages {
    Log "Loading container images via Podman..."
    $tarFiles = Get-ChildItem -Path (Join-Path $BundleDir "docker-images") -Filter "*.tar.gz"
    foreach ($tar in $tarFiles) {
        Log "Loading: $($tar.Name)"
        # Requires tar (Windows 10 1803+) and Podman in PATH
        $tmp = [System.IO.Path]::GetTempFileName() + ".tar"
        & tar -xzf $tar.FullName -O > $tmp
        podman load --input $tmp
        Remove-Item $tmp -Force
    }
    Log "Images loaded."
    podman images
}

function Restore-OllamaModels {
    $ollamaHome = "$env:USERPROFILE\.ollama"
    Log "Restoring Ollama models to $ollamaHome ..."
    New-Item -ItemType Directory -Force -Path $ollamaHome | Out-Null

    $tarFiles = Get-ChildItem -Path (Join-Path $BundleDir "ollama-models") -Filter "*.tar.gz"
    foreach ($tar in $tarFiles) {
        Log "Restoring: $($tar.Name)"
        tar -xzf $tar.FullName -C $ollamaHome
    }
    Log "Models restored."
    try { ollama list } catch { Log "(Start Ollama service to verify: ollama list)" }
}

if (-not $SkipVerify) { Verify-Bundle }
if (-not $SkipOllama) { Install-Ollama }
if (-not $SkipPodman) { Load-ContainerImages }
if (-not $SkipModels) { Restore-OllamaModels }

Log "Offline deployment complete."
Log "Next: cd project root && podman compose up -d"
