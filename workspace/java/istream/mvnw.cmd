@echo off
setlocal enabledelayedexpansion

set MAVEN_VERSION=3.9.9
set MAVEN_DIST=apache-maven-%MAVEN_VERSION%
set WRAPPER_HOME=%USERPROFILE%\.m2\wrapper\dists\%MAVEN_DIST%
set MVN_CMD=%WRAPPER_HOME%\bin\mvn.cmd

if not exist "%MVN_CMD%" (
    echo [mvnw] Maven %MAVEN_VERSION% not found. Downloading...
    set ZIP=%TEMP%\%MAVEN_DIST%-bin.zip
    powershell -Command "Invoke-WebRequest -Uri 'https://archive.apache.org/dist/maven/maven-3/%MAVEN_VERSION%/binaries/%MAVEN_DIST%-bin.zip' -OutFile '%ZIP%'"
    if !errorlevel! neq 0 (
        echo [mvnw] Download failed. Please install Maven manually.
        exit /b 1
    )
    powershell -Command "Expand-Archive -Path '%TEMP%\%MAVEN_DIST%-bin.zip' -DestinationPath '%USERPROFILE%\.m2\wrapper\dists\' -Force"
    del "%ZIP%" 2>nul
    echo [mvnw] Maven %MAVEN_VERSION% installed.
)

"%MVN_CMD%" %*
