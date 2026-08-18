# CI/CD Dashboard - Quick Start Guide

## Dashboard Not Loading? Here's the Fix!

### Problem
When you open http://localhost:8000 in your browser, the dashboard doesn't load or shows "Connection refused".

### Root Cause
The dashboard backend services (FastAPI, Prometheus, Grafana) are not running.

### Solution

#### Step 1: Start the Dashboard

Open PowerShell and run:

```powershell
cd <path-to-project>
.\scripts\start.ps1
```

**What this does:**
- Starts Prometheus (metrics database)
- Starts Grafana (visualization)
- Starts FastAPI (dashboard backend)
- Opens browsers automatically

#### Step 2: Wait for Services

The script will show:
```
[CICD] Starting Prometheus on port 9000 ...
[OK]   Prometheus started (PID 12345)
[CICD] Starting Grafana on port 9001 ...
[OK]   Grafana started (PID 12346)
[CICD] Starting CI/CD Dashboard API on port 8000 ...
[OK]   CI/CD Dashboard API started (PID 12347)
[CICD] Waiting for services to be healthy...
[OK]   Prometheus is ready
[OK]   Grafana is ready
[OK]   CI/CD Dashboard is ready

CI/CD Dashboard is running!
  Dashboard  -> http://localhost:8000
  Grafana    -> http://localhost:9001
  Prometheus -> http://localhost:9000
  API Docs   -> http://localhost:8000/api/docs
  Metrics    -> http://localhost:8000/metrics
```

#### Step 3: Access the Dashboard

The script will automatically open browsers, or you can manually navigate to:
- **Main Dashboard:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs

### First Time Setup

If this is your first time running the dashboard:

1. **Check Prerequisites:**
   ```powershell
   # Check Python installation
   python --version    # Should be 3.8 or higher
   
   # Check if Prometheus exists (path set in PROMETHEUS_EXE in .env)
   Test-Path $env:PROMETHEUS_EXE
   
   # Check if Grafana exists (path set in GRAFANA_EXE in .env)
   Test-Path $env:GRAFANA_EXE
   ```

2. **Run Setup (if needed):**
   ```powershell
   cd <path-to-project>
   .\scripts\setup.ps1
   ```

3. **Configure GitLab Token:**
   Edit `.env` file:
   ```powershell
   notepad .env
   ```
   
   Update this line with your GitLab Personal Access Token:
   ```
   GITLAB_TOKEN=your_actual_token_here
   ```

4. **Start the Dashboard:**
   ```powershell
   .\scripts\start.ps1
   ```

### Stopping the Dashboard

When you're done, stop all services:

```powershell
cd <path-to-project>
.\scripts\stop.ps1
```

This will gracefully shut down all processes.

### Verifying Services are Running

Check if processes are running:

```powershell
# Check all services
Get-Process | Where-Object {$_.ProcessName -like "*prometheus*" -or $_.ProcessName -like "*grafana*" -or $_.ProcessName -like "*uvicorn*"}

# Check specific ports
netstat -ano | findstr "8000"    # Dashboard API
netstat -ano | findstr "9000"    # Prometheus
netstat -ano | findstr "9001"    # Grafana
```

### Common Issues & Solutions

#### Issue 1: Port Already in Use

**Error:** Port 8000 is already in use

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr "8000"

# Kill the process (replace PID with actual process ID)
Stop-Process -Id PID -Force

# Or stop the dashboard properly
.\scripts\stop.ps1
```

#### Issue 2: Python Dependencies Missing

**Error:** ModuleNotFoundError: No module named 'fastapi'

**Solution:**
```powershell
# Reinstall dependencies
cd dashboard_api
.venv\Scripts\pip install -r requirements.txt
```

#### Issue 3: GitLab Token Not Set

**Warning:** GITLAB_TOKEN is not set in .env

**Solution:**
1. Get token from GitLab:
   - Go to https://gitlab.com/-/profile/personal_access_tokens
   - Click "Add new token"
   - Name: "CICD Dashboard"
   - Scopes: `api`, `read_api`, `read_repository`
   - Click "Create personal access token"
   - Copy the token

2. Add to .env:
   ```powershell
   notepad .env
   ```
   Update: `GITLAB_TOKEN=glpat-xxxxxxxxxxxxx`

3. Restart dashboard:
   ```powershell
   .\scripts\stop.ps1
   .\scripts\start.ps1
   ```

#### Issue 4: Browser Doesn't Open Automatically

**Solution:**
Manually open: http://localhost:8000

#### Issue 5: Dashboard Shows No Data

**Possible Causes:**
1. GitLab token not set or invalid
2. GitLab URL not configured
3. No projects in GitLab account

**Solution:**
Check configuration:
```powershell
Get-Content .env | Select-String "GITLAB"
```

Should show:
```
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxx
```

### Log Files

If something goes wrong, check these log files:

```powershell
# API logs
Get-Content data\api.log -Tail 50
Get-Content data\api-error.log -Tail 50

# Prometheus logs
Get-Content data\prometheus.log -Tail 50
Get-Content data\prometheus-error.log -Tail 50

# Grafana logs
Get-Content data\grafana.log -Tail 50
Get-Content data\grafana-error.log -Tail 50
```

### Environment Variables

Key configuration in `.env`:

```env
# GitLab Configuration
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token_here

# Application Ports
APP_PORT=8000
PROMETHEUS_PORT=9000
GRAFANA_PORT=9001

# Logging
LOG_LEVEL=INFO

# Cache
CACHE_TTL=300

# Export Directory
EXPORT_DIR=exports

# Data Retention
PROMETHEUS_RETENTION=30d
```

### Quick Commands Reference

```powershell
# Navigate to project
cd <path-to-project>

# Start dashboard
.\scripts\start.ps1

# Stop dashboard
.\scripts\stop.ps1

# Setup/reinstall
.\scripts\setup.ps1

# Check running processes
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"}

# View API logs
Get-Content data\api.log -Tail 50

# View error logs
Get-Content data\api-error.log -Tail 50

# Test API endpoint
Invoke-WebRequest http://localhost:8000/health
```

### Next Steps

1. ✅ Start the dashboard: `.\scripts\start.ps1`
2. ✅ Access UI: http://localhost:8000
3. ✅ Explore features: Overview, Pipelines, Jobs
4. ✅ Read guide: README.md
5. ✅ Configure GitLab integration

### Support

- **Documentation:** See README.md
- **API Docs:** http://localhost:8000/api/docs (when running)
- **Logs:** `data/` directory
- **Issues:** Check GitHub/GitLab repository

---

**TL;DR:** Run `.\scripts\start.ps1` in PowerShell from the `python/cicd` directory, then open http://localhost:8000 🚀
