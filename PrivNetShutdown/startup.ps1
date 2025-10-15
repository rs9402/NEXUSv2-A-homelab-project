# start_privnetshutdown.ps1 (env vars redacted for my security)

$env:MASTER_PASSPHRASE = #REDACTED
$env:AUTH_SHARED_SECRET = #REDACTED
$env:FLASK_SESSION_KEY = #REDACTED

Write-Host "Starting auth service..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList ".\auth.py"

Write-Host "Starting web UI..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList ".\web.py"
