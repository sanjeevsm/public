@echo off
echo Starting PrimeCare+ Servers...
echo.

echo Starting API Server (Port 5000)...
start "PrimeCare API" cmd /k "set DB_PASSWORD=postgres && C:\Users\SanjeevMenon\workspace\python\primecare\api\venv\Scripts\python.exe C:\Users\SanjeevMenon\workspace\python\primecare\api\app.py"

timeout /t 3 /nobreak >nul

echo Starting Web Client (Port 5001)...
start "PrimeCare Web" cmd /k "set DB_PASSWORD=postgres && C:\Users\SanjeevMenon\workspace\python\primecare\web-app\venv\Scripts\python.exe C:\Users\SanjeevMenon\workspace\python\primecare\web-app\client.py"

echo.
echo Both servers started!
echo API Server: http://localhost:5000
echo Web Client: http://localhost:5001
echo.
echo Access the Reports module at: http://localhost:5001/reports
echo.
pause
