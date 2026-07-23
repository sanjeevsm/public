<#
.SYNOPSIS
    Extract a Murex CTT zip file into a folder structure.

.DESCRIPTION
    Wraps murex_ctt.py extract using the project virtual environment.
    Nested zips are automatically extracted recursively.

.PARAMETER Zip
    Path to the CTT .zip file to extract. (Required)

.PARAMETER Output
    Destination directory for the extracted folder.
    Defaults to the current working directory.

.PARAMETER Verbose
    Enable verbose logging.

.EXAMPLE
    .\murex_extract.ps1 -Zip <CTT_FILENAME>.zip

.EXAMPLE
    .\murex_extract.ps1 -Zip <CTT_FILENAME>.zip -Output <FULL PATH INCLUDING CTT_FOLDER_NAME>

.EXAMPLE
    .\murex_extract.ps1 -Zip <FULL PATH INCLUDING CTT_FILE_NAME> -Output <FULL PATH INCLUDING CTT_FOLDER_NAME>
#>

param(
    [Parameter(Mandatory = $true, HelpMessage = "Path to the CTT .zip file")]
    [string]$Zip,

    [Parameter(Mandatory = $false, HelpMessage = "Destination directory (default: current directory)")]
    [string]$Output = "",

    [switch]$VerboseLog
)

$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir "..\dashboard_api\.venv\Scripts\python.exe"
$cliScript  = Join-Path $scriptDir "murex_ctt.py"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment not found at: $venvPython`nRun .\scripts\setup.ps1 first."
    exit 1
}

$argList = @("extract", "--zip", $Zip)
if ($Output)     { $argList += @("--output", $Output) }
if ($VerboseLog) { $argList += "--verbose" }

Write-Host ""
Write-Host "  Murex CTT - Extract" -ForegroundColor Cyan
Write-Host ""

& $venvPython $cliScript @argList
exit $LASTEXITCODE
