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

$ROOT = Split-Path -Parent (Get-Location).Path
$logsDir = Join-Path $ROOT "logs"
$pidsDir = Join-Path $ROOT ".pids"
New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
New-Item -ItemType Directory -Path $pidsDir -Force | Out-Null

$logFile = Join-Path $logsDir "frontend.log"
$errFile = Join-Path $logsDir "frontend-error.log"
$proc = Start-Process cmd.exe `
    -ArgumentList "/c npm run dev -- --port $FRONTEND_PORT > `"$logFile`" 2> `"$errFile`"" `
    -WorkingDirectory (Get-Location).Path `
    -WindowStyle Hidden -PassThru

$proc.Id | Out-File (Join-Path $pidsDir "frontend.pid") -Encoding ascii
Write-Host "Frontend started (PID $($proc.Id))." -ForegroundColor Green
Write-Host "  URL:  http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
Write-Host "  Logs: $logsDir\frontend.log" -ForegroundColor Gray
Write-Host "To stop: .\scripts\stop-local.ps1" -ForegroundColor Gray
