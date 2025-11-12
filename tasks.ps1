# Task runner script for common development tasks
# Usage: .\tasks.ps1 <command>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        'setup', 'install', 'migrate', 'run', 'test', 'test-unit', 'test-integration',
        'test-concurrency', 'docker-up', 'docker-down', 'docker-logs', 'db-shell',
        'create-migration', 'format', 'lint', 'clean', 'help'
    )]
    [string]$Command,
    
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

function Show-Help {
    Write-Host @"
🚀 Medical Appointment Booking API - Task Runner

Available Commands:
  setup              - Initial project setup (venv + dependencies)
  install            - Install/update dependencies
  migrate            - Run database migrations
  run                - Start the API server
  test               - Run all tests
  test-unit          - Run unit tests only
  test-integration   - Run integration tests
  test-concurrency   - Run concurrency test only
  docker-up          - Start all Docker services
  docker-down        - Stop all Docker services
  docker-logs        - View Docker logs
  db-shell           - Open PostgreSQL shell
  create-migration   - Create new migration (pass message as arg)
  format             - Format code with black
  lint               - Run linter (ruff)
  clean              - Clean cache and temporary files
  help               - Show this help message

Examples:
  .\tasks.ps1 setup
  .\tasks.ps1 run
  .\tasks.ps1 test
  .\tasks.ps1 docker-up
  .\tasks.ps1 create-migration "add new field"
"@
}

switch ($Command) {
    'setup' {
        Write-Host "🔧 Setting up project..." -ForegroundColor Green
        & .\setup.ps1
    }
    
    'install' {
        Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    
    'migrate' {
        Write-Host "🔄 Running migrations..." -ForegroundColor Yellow
        alembic upgrade head
    }
    
    'run' {
        Write-Host "🚀 Starting API server..." -ForegroundColor Green
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    }
    
    'test' {
        Write-Host "🧪 Running all tests..." -ForegroundColor Cyan
        pytest tests/ -v
    }
    
    'test-unit' {
        Write-Host "🧪 Running unit tests..." -ForegroundColor Cyan
        pytest tests/unit/ -v
    }
    
    'test-integration' {
        Write-Host "🧪 Running integration tests..." -ForegroundColor Cyan
        pytest tests/integration/ -v
    }
    
    'test-concurrency' {
        Write-Host "🧪 Running concurrency test..." -ForegroundColor Cyan
        pytest tests/integration/test_appointments.py::TestConcurrentBooking -v -s
    }
    
    'docker-up' {
        Write-Host "🐳 Starting Docker services..." -ForegroundColor Blue
        docker-compose up -d
        Write-Host "✅ Services started!" -ForegroundColor Green
        Write-Host "API: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "pgAdmin: http://localhost:5050" -ForegroundColor Cyan
    }
    
    'docker-down' {
        Write-Host "🛑 Stopping Docker services..." -ForegroundColor Yellow
        docker-compose down
    }
    
    'docker-logs' {
        Write-Host "📋 Docker logs..." -ForegroundColor Cyan
        docker-compose logs -f
    }
    
    'db-shell' {
        Write-Host "🐘 Opening PostgreSQL shell..." -ForegroundColor Cyan
        docker exec -it clinic_postgres psql -U postgres -d appointment_db
    }
    
    'create-migration' {
        if ($Args.Count -eq 0) {
            Write-Host "❌ Please provide a migration message" -ForegroundColor Red
            Write-Host "Usage: .\tasks.ps1 create-migration 'your message'" -ForegroundColor Yellow
            exit 1
        }
        $message = $Args -join " "
        Write-Host "📝 Creating migration: $message" -ForegroundColor Yellow
        alembic revision --autogenerate -m $message
    }
    
    'format' {
        Write-Host "🎨 Formatting code..." -ForegroundColor Magenta
        black app/ tests/
    }
    
    'lint' {
        Write-Host "🔍 Running linter..." -ForegroundColor Magenta
        ruff check app/ tests/
    }
    
    'clean' {
        Write-Host "🧹 Cleaning cache files..." -ForegroundColor Yellow
        Get-ChildItem -Path . -Include __pycache__,.pytest_cache,.ruff_cache -Recurse -Directory | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Include *.pyc,*.pyo -Recurse -File | Remove-Item -Force
        Write-Host "✅ Cleaned!" -ForegroundColor Green
    }
    
    'help' {
        Show-Help
    }
}
