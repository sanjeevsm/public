#!/usr/bin/env pwsh
$P = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $P\..\frontend
npm install
npm run dev -- --port 3002
Pop-Location
