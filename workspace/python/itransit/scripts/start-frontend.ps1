#!/usr/bin/env pwsh
$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P\..\frontend

$FRONTEND_PORT = if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 3001 }
Write-Host "Starting iTransit+ frontend on port $FRONTEND_PORT"

function Get-ListenersByPort {
	param([int]$Port)
	return Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
}

npm install

$pids = Get-ListenersByPort -Port $FRONTEND_PORT
if ($pids) {
	foreach ($thePid in $pids) {
		$cmdline = ""
		try { $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$thePid" | Select-Object -ExpandProperty CommandLine) } catch {}
		Write-Host "Port $FRONTEND_PORT is in use by PID $thePid (cmd: $cmdline)" -ForegroundColor Red
	}
	Write-Host "Please stop the above process(es) and retry." -ForegroundColor Red
	Pop-Location
	exit 1
} else {
	Write-Host "No listener on port $FRONTEND_PORT" -ForegroundColor Gray
}

Start-Process npm -ArgumentList 'run','dev','--','--port',$FRONTEND_PORT -NoNewWindow
Pop-Location
