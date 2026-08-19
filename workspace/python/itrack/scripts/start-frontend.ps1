Set-Location "C:\Users\SanjeevMenon\PGit\public\workspace\python\itrack\scripts\..\frontend"

$FRONTEND_PORT = if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 3000 }
Write-Host "Starting iTrack+ frontend on http://localhost:$FRONTEND_PORT" -ForegroundColor Green

function Get-ListenersByPort {
	param([int]$Port)
	Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
}

$pids = Get-ListenersByPort -Port $FRONTEND_PORT
if ($pids) {
	foreach ($thePid in $pids) {
		$cmdline = ""
		try { $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$thePid" | Select-Object -ExpandProperty CommandLine) } catch {}
		Write-Host "Port $FRONTEND_PORT is in use by PID $thePid (cmd: $cmdline)" -ForegroundColor Red
	}
	Write-Host "Please stop the above process(es) and retry." -ForegroundColor Red
	exit 1
} else { Write-Host "No listener on port $FRONTEND_PORT" -ForegroundColor Gray }

& npm run dev -- --port $FRONTEND_PORT
