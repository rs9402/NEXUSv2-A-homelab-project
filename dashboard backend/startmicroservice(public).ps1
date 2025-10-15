$env:OWM_API_KEY = #KEYREDACTED

Write-Host "Starting services..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList ".\microservices.py"