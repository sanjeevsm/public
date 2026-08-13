Set-Location "C:\Users\SanjeevMenon\PGit\public\workspace\python\itrack\scripts\..\backend"
.\venv\Scripts\Activate.ps1

$BACKEND_PORT = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8002 }
Write-Host "Starting iTrack+ backend on http://localhost:$BACKEND_PORT" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:$BACKEND_PORT/docs" -ForegroundColor Cyan

function Get-ListenersByPort {
	param([int]$Port)
	Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
}

$pids = Get-ListenersByPort -Port $BACKEND_PORT
if ($pids) {
	foreach ($thePid in $pids) {
		$cmdline = ""
		try { $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$thePid" | Select-Object -ExpandProperty CommandLine) } catch {}
		Write-Host "Port $BACKEND_PORT is in use by PID $thePid (cmd: $cmdline)" -ForegroundColor Red
	}
	Write-Host "Please stop the above process(es) and retry." -ForegroundColor Red
	exit 1
} else { Write-Host "No listener on port $BACKEND_PORT" -ForegroundColor Gray }

uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload
