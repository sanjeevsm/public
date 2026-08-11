Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..\frontend'))
Write-Host 'Frontend server starting on http://localhost:3000' -ForegroundColor Green
Write-Host ''
npm run dev
