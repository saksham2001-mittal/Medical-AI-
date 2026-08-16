[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$launcherPath = Join-Path $PSScriptRoot 'Start-OllamaServer.ps1'
$startupCommandPath = Join-Path $PSScriptRoot 'Ollama-Autostart.cmd'
$startupFolder = [Environment]::GetFolderPath('Startup')
$installedCommandPath = Join-Path $startupFolder 'Ollama-Autostart.cmd'

if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "The launcher script was not found: $launcherPath"
}

if (-not (Test-Path -LiteralPath $startupCommandPath)) {
    throw "The startup command was not found: $startupCommandPath"
}

Copy-Item -LiteralPath $startupCommandPath -Destination $installedCommandPath -Force
& $launcherPath

Write-Host 'Installed Ollama autostart. Ollama will start automatically after each restart when you sign in.'
