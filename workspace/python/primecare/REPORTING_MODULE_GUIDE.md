# PrimeCare+ Reporting Module - Troubleshooting Guide

## Issue: Reporting Module Not Loading

### Root Cause Analysis
The reporting module files are all present and correctly implemented:
- ✅ API endpoints in `api/app.py` (lines 472-1043)
- ✅ Web client route in `web-app/client.py` (lines 120-122)
- ✅ Template file `web-app/reports.html`

The issue is that the servers need to be running properly.

## Solution

### Option 1: Using Batch File (Windows)
1. Double-click on `start_servers.bat`
2. Two command windows will open (API and Web Client)
3. Wait for both servers to start
4. Open browser and go to: http://localhost:5001/reports

### Option 2: Using PowerShell Script
1. Right-click on `start_servers.ps1` and select "Run with PowerShell"
2. Two PowerShell windows will open
3. Wait for both servers to start
4. Open browser and go to: http://localhost:5001/reports

### Option 3: Manual Start (Two Separate Terminals)

**Terminal 1 - API Server:**
```powershell
$env:DB_PASSWORD="postgres"
workspace/python/primecare/api/venv/Scripts/python.exe workspace/python/primecare/api/app.py
```

**Terminal 2 - Web Client:**
```powershell
$env:DB_PASSWORD="postgres"
workspace/python/primecare/web-app/venv/Scripts/python.exe workspace/python/primecare/web-app/client.py
```

## Verification Steps

1. **Check API Server:** Open http://localhost:5000/specialities
   - Should return JSON with specialities data

2. **Check Web Client:** Open http://localhost:5001/
   - Should show the home page with doctors

3. **Check Reports Module:** Open http://localhost:5001/reports
   - Should load the reports dashboard

## Common Issues

### Issue 1: Port Already in Use
**Error:** `Address already in use`
**Solution:** Kill existing processes:
```powershell
# Find processes using port 5000 and 5001
netstat -ano | findstr :5000
netstat -ano | findstr :5001

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Issue 2: Database Connection Error
**Error:** `could not connect to server`
**Solution:** 
1. Make sure PostgreSQL is running
2. Verify database credentials:
   - Host: localhost
   - Port: 5432
   - Database: clinic
   - User: postgres
   - Password: postgres

### Issue 3: Module Not Found Error
**Error:** `ModuleNotFoundError: No module named 'flask'`
**Solution:** Install dependencies:
```powershell
# For API
workspace/python/primecare/api/venv/Scripts/pip.exe install -r workspace/python/primecare/api/requirements.txt

# For Web Client
workspace/python/primecare/web-app/venv/Scripts/pip.exe install -r workspace/python/primecare/web-app/requirements.txt
```

## Available Reports

Once the servers are running, you can access these reports:

1. **Summary Report** - Overview of clinic operations
2. **Appointments Report** - Detailed appointment analytics with filters
3. **Doctors Report** - Doctor performance metrics
4. **Specialities Report** - Speciality-wise statistics
5. **Patients Report** - Patient demographics and visit history
6. **Revenue Report** - Financial analytics and trends

## Export Features

All reports support multiple export formats:
- 📥 CSV - For Excel/spreadsheet analysis
- 📊 Excel - Native Excel format with formatting
- 📄 JSON - For programmatic access

## API Endpoints

The following API endpoints are available:

- `GET /reports/summary` - Overall summary statistics
- `GET /reports/appointments` - Appointments report with filters
- `GET /reports/doctors` - Doctor performance report
- `GET /reports/specialities` - Speciality-wise report
- `GET /reports/patients` - Patient statistics report
- `GET /reports/revenue` - Revenue report with grouping
- `GET /reports/export/<report_type>` - Export reports in various formats

## Need Help?

If you're still experiencing issues:
1. Check the console output in both terminal windows for error messages
2. Verify PostgreSQL is running and accessible
3. Ensure all dependencies are installed
4. Check firewall settings aren't blocking ports 5000 or 5001
