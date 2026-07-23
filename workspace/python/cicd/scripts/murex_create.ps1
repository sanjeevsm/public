<#
.SYNOPSIS
    Create a Murex CTT zip file from a folder structure.

.DESCRIPTION
    Wraps murex_ctt.py create using the project virtual environment.
    Each subdirectory in the source folder is converted to a nested zip.

.PARAMETER Folder
    Path to the source folder to package. (Required)

.PARAMETER Output
    Output zip file path.
    Defaults to <FolderName>_YYYYMMDD_HHMMSS.zip in the current directory.

.PARAMETER Verbose
    Enable verbose logging.

.EXAMPLE
    .\murex_create.ps1 -Folder <CTT_FOLDER_NAME>

.EXAMPLE
    .\murex_create.ps1 -Folder <CTT_FOLDER_NAME> -Output <CTT_FILENAME>.zip

.EXAMPLE
    .\murex_create.ps1 -Folder <FULL PATH INCLUDING CTT_FOLDER_NAME> -Output <FULL PATH INCLUDING CTT_FILE_NAME>
#>

param(
    [Parameter(Mandatory = $true, HelpMessage = "Source folder to package into a CTT zip")]
    [string]$Folder,

    [Parameter(Mandatory = $false, HelpMessage = "Output zip file path (default: <folder>_timestamp.zip)")]
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

$argList = @("create", "--folder", $Folder)
if ($Output)     { $argList += @("--output", $Output) }
if ($VerboseLog) { $argList += "--verbose" }

Write-Host ""
Write-Host "  Murex CTT - Create" -ForegroundColor Cyan
Write-Host ""

& $venvPython $cliScript @argList
exit $LASTEXITCODE
