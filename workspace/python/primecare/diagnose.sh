#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "PrimeCare+ Diagnostic Tool"
echo "=========================="
echo ""

# Check 1: Files exist
echo "1. Checking files..."
for f in "api/app.py" "web-app/client.py" "web-app/reports.html"; do
    if [ -f "$ROOT/$f" ]; then
        echo "  ✓ $f exists"
    else
        echo "  ✗ $f missing"
    fi
done
echo ""

# Check 2: Virtual environments
echo "2. Checking virtual environments..."
for venv in "api/venv/bin/python" "web-app/venv/bin/python"; do
    if [ -f "$ROOT/$venv" ]; then
        echo "  ✓ $venv exists"
    else
        echo "  ✗ $venv missing (run ./setup.sh)"
    fi
done
echo ""

# Check 3: Ports in use
echo "3. Checking if ports are in use..."
for port in 5000 5001; do
    if command -v lsof &>/dev/null; then
        if lsof -i ":$port" &>/dev/null 2>&1; then
            echo "  ⚠ Port $port is in use"
            lsof -i ":$port" 2>/dev/null | tail -n +2 | awk '{print "    " $0}'
        else
            echo "  ✓ Port $port is available"
        fi
    elif command -v ss &>/dev/null; then
        if ss -tlnp 2>/dev/null | grep -q ":$port "; then
            echo "  ⚠ Port $port is in use"
        else
            echo "  ✓ Port $port is available"
        fi
    else
        echo "  ? Port $port - cannot check (lsof/ss not found)"
    fi
done
echo ""

# Check 4: PostgreSQL
echo "4. Checking PostgreSQL..."
if command -v pg_isready &>/dev/null; then
    if pg_isready -h localhost >/dev/null 2>&1; then
        echo "  ✓ PostgreSQL is accepting connections"
    else
        echo "  ✗ PostgreSQL is not accepting connections"
        echo "    Start the PostgreSQL service and retry"
    fi
else
    echo "  ⚠ pg_isready not found - cannot check PostgreSQL"
    echo "    Install PostgreSQL client tools or verify manually"
fi
echo ""

# Check 5: API endpoints in app.py
echo "5. Checking API endpoints in app.py..."
APP_PY="$ROOT/api/app.py"
if [ -f "$APP_PY" ]; then
    for endpoint in "/reports/summary" "/reports/appointments" "/reports/doctors" \
                    "/reports/specialities" "/reports/patients" "/reports/revenue" "/reports/export"; do
        if grep -qF "$endpoint" "$APP_PY"; then
            echo "  ✓ $endpoint endpoint found"
        else
            echo "  ✗ $endpoint endpoint missing"
        fi
    done
fi
echo ""

# Check 6: Client route
echo "6. Checking client route..."
CLIENT_PY="$ROOT/web-app/client.py"
if [ -f "$CLIENT_PY" ]; then
    if grep -q "@app\.route('/reports')" "$CLIENT_PY"; then
        echo "  ✓ /reports route found in client.py"
    else
        echo "  ✗ /reports route missing in client.py"
    fi
    if grep -q "render_template('reports\.html')" "$CLIENT_PY" || \
       grep -q "render_template(\"reports\.html\")" "$CLIENT_PY"; then
        echo "  ✓ reports.html template reference found"
    else
        echo "  ✗ reports.html template reference missing"
    fi
fi
echo ""
echo "=========================="
echo ""
echo "Recommendations:"
echo ""
echo "If all checks passed:"
echo "  1. Run './start_servers.sh' to start both servers"
echo "  2. Wait 5 seconds for servers to start"
echo "  3. Open http://localhost:5001/reports in browser"
echo ""
echo "If ports are in use:"
echo "  Kill the processes using those ports or run ./stop_servers.sh"
echo ""
echo "If PostgreSQL is not running:"
echo "  Start the PostgreSQL service or install PostgreSQL"
echo ""
