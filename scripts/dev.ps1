$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backend = Start-Process -FilePath "python" -ArgumentList @(
    "-m", "uvicorn", "backend.app.main:app", "--reload", "--port", "8000"
) -WorkingDirectory $repoRoot -PassThru -NoNewWindow
try {
    npm.cmd --prefix (Join-Path $repoRoot "frontend") run dev
}
finally {
    if (-not $backend.HasExited) { Stop-Process -Id $backend.Id }
}

