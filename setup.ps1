# Setup script for local development

Write-Host "🚀 Setting up Medical Appointment Booking API..." -ForegroundColor Green

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Check if virtual environment exists
if (-Not (Test-Path ".venv")) {
    Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Start PostgreSQL (or run: docker-compose up -d postgres)" -ForegroundColor White
Write-Host "2. Run migrations: alembic upgrade head" -ForegroundColor White
Write-Host "3. Start the API: uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Or use Docker Compose:" -ForegroundColor Cyan
Write-Host "  docker-compose up -d" -ForegroundColor White
Write-Host ""
