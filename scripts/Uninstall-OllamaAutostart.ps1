[CmdletBinding()]
param()

$startupFolder = [Environment]::GetFolderPath('Startup')
$installedCommandPath = Join-Path $startupFolder 'Ollama-Autostart.cmd'
Remove-Item -LiteralPath $installedCommandPath -Force -ErrorAction SilentlyContinue
Write-Host 'Removed Ollama autostart.'
