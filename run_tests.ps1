# WebSocket Integration Tests - Setup and Run Script
# This script helps set up the test environment and run WebSocket tests

Write-Host "🧪 WebSocket Integration Test Runner" -ForegroundColor Cyan
Write-Host "====================================`n" -ForegroundColor Cyan

# Check if PostgreSQL is running
Write-Host "📊 Checking PostgreSQL service..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue

if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "✅ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "   Start it with: Start-Service postgresql-x64-16" -ForegroundColor Yellow
    exit 1
}

# Check if test database exists
Write-Host "`n📚 Checking test database..." -ForegroundColor Yellow
$checkDB = psql -U postgres -lqt | Select-String -Pattern "clinic_test_db"

if ($checkDB) {
    Write-Host "✅ Test database 'clinic_test_db' exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Test database 'clinic_test_db' not found" -ForegroundColor Yellow
    Write-Host "   Creating test database..." -ForegroundColor Yellow
    
    psql -U postgres -c "CREATE DATABASE clinic_test_db;" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test database created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create test database" -ForegroundColor Red
        Write-Host "   Please create manually: CREATE DATABASE clinic_test_db;" -ForegroundColor Yellow
        exit 1
    }
}

# Check if pytest is installed
Write-Host "`n🔧 Checking test dependencies..." -ForegroundColor Yellow
$pytestInstalled = python -m pytest --version 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ pytest is installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  pytest not found, installing test dependencies..." -ForegroundColor Yellow
    pip install pytest pytest-asyncio httpx websockets pytest-cov
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

# Display menu
Write-Host "`n📋 Test Options:" -ForegroundColor Cyan
Write-Host "  1. Run all WebSocket tests" -ForegroundColor White
Write-Host "  2. Run connection tests only" -ForegroundColor White
Write-Host "  3. Run real-time update tests only" -ForegroundColor White
Write-Host "  4. Run multiple client tests only" -ForegroundColor White
Write-Host "  5. Run with coverage report" -ForegroundColor White
Write-Host "  6. Run specific test (custom)" -ForegroundColor White
Write-Host "  0. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter your choice (0-6)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 Running all WebSocket tests...`n" -ForegroundColor Green
        python -m pytest tests/integration/test_websockets.py -v
    }
    "2" {
        Write-Host "`n🚀 Running connection tests...`n" -ForegroundColor Green
        python -m pytest tests/integration/test_websockets.py::TestWebSocketConnection -v
    }
    "3" {
        Write-Host "`n🚀 Running real-time update tests...`n" -ForegroundColor Green
        python -m pytest tests/integration/test_websockets.py::TestWebSocketRealTimeUpdates -v
    }
    "4" {
        Write-Host "`n🚀 Running multiple client tests...`n" -ForegroundColor Green
        python -m pytest tests/integration/test_websockets.py::TestWebSocketMultipleClients -v
    }
    "5" {
        Write-Host "`n🚀 Running tests with coverage...`n" -ForegroundColor Green
        python -m pytest tests/integration/test_websockets.py --cov=app.api.v1.routers.websockets --cov-report=html --cov-report=term
        Write-Host "`n📊 Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
    }
    "6" {
        $testName = Read-Host "`nEnter test name (e.g., test_websocket_connect_and_subscribe)"
        Write-Host "`n🚀 Running custom test...`n" -ForegroundColor Green
        python -m pytest "tests/integration/test_websockets.py::TestWebSocketConnection::$testName" -v -s
    }
    "0" {
        Write-Host "`nExiting..." -ForegroundColor Yellow
        exit 0
    }
    default {
        Write-Host "`n❌ Invalid choice!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n✨ Test run completed!" -ForegroundColor Cyan

# Show summary
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Check output above." -ForegroundColor Red
}

Write-Host "`n📚 For more info, see: tests/integration/README.md" -ForegroundColor Cyan
