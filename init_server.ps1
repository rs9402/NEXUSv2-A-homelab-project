#Script run in Task Scheduler at Log on

Start-Transcript -Path "C:\Logs\ServerInit_$(Get-Date -Format yyyyMMdd_HHmmss).log" -Append

# init_server.ps1
Write-Host "Initializing Server..."

$scripts = @(
    "C:\Users\darkm\Desktop\stuff\Server\PrivNetShutdown\startup.ps1",
    "C:\Users\darkm\Desktop\stuff\Server\dashboard backend\startmicroservice.ps1",
	"C:\Users\darkm\Desktop\stuff\Server\dashboard\webserver.ps1"
)

foreach ($s in $scripts) {
    $folder = Split-Path $s
    Start-Process powershell.exe -ArgumentList "-NoExit","-File `"$s`"" -WorkingDirectory $folder
}


Stop-Transcript

# note: other services and applications run through Windows 10's Startup Apps (shell:startup) functionality