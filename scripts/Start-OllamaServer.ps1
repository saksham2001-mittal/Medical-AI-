[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

# Do not start a second server if Ollama (or another compatible server) is
# already listening on its default local endpoint.
$alreadyRunning = $false
try {
    $client = [System.Net.Sockets.TcpClient]::new()
    $connection = $client.BeginConnect('127.0.0.1', 11434, $null, $null)
    $alreadyRunning = $connection.AsyncWaitHandle.WaitOne(1000) -and $client.Connected
    $client.Close()
}
catch {
    $alreadyRunning = $false
}

if ($alreadyRunning) {
    exit 0
}

$ollamaCandidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'),
    (Join-Path $env:ProgramFiles 'Ollama\ollama.exe')
)

$ollamaPath = $ollamaCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $ollamaPath) {
    $ollamaCommand = Get-Command ollama.exe -ErrorAction SilentlyContinue
    if ($ollamaCommand) {
        $ollamaPath = $ollamaCommand.Source
    }
}

if (-not $ollamaPath) {
    throw 'Ollama was not found. Install Ollama, then run Install-OllamaAutostart.ps1 again.'
}

Start-Process -FilePath $ollamaPath -ArgumentList 'serve' -WindowStyle Hidden
