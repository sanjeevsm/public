#!/usr/bin/env bash
echo "PrimeCare+ Server Health Check"
echo "================================"
echo ""

check_endpoint() {
    local url="$1" name="$2"
    if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
        echo "✓ $name is running"
        return 0
    else
        echo "✗ $name is not responding ($url)"
        return 1
    fi
}

echo "Checking API Server (Port 5000)..."
check_endpoint "http://localhost:5000/specialities" "API Server" && API_OK=true || API_OK=false
echo ""

echo "Checking Web Client (Port 5001)..."
check_endpoint "http://localhost:5001/" "Web Client" && WEB_OK=true || WEB_OK=false
echo ""

echo "Checking Reports Module..."
if [ "$WEB_OK" = "true" ]; then
    check_endpoint "http://localhost:5001/reports" "Reports Module" && REP_OK=true || REP_OK=false
else
    echo "✗ Cannot check Reports Module (Web Client not running)"
    REP_OK=false
fi

echo ""
echo "================================"

if [ "$API_OK" = "true" ] && [ "$WEB_OK" = "true" ] && [ "$REP_OK" = "true" ]; then
    echo "✓ All services are running!"
    echo ""
    echo "Access the application at:"
    echo "  Home:    http://localhost:5001/"
    echo "  Reports: http://localhost:5001/reports"
else
    echo "✗ Some services are not running"
    echo ""
    echo "Run './start_servers.sh' to start the servers"
fi
echo ""
