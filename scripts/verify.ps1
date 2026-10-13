# Verification Script for Windows (PowerShell)
Write-Host "🚀 Starting Project Verification..." -ForegroundColor Cyan

Write-Host "--- 🐍 Backend Tests ---" -ForegroundColor Yellow
cd backend
pytest -q
if ($LASTEXITCODE -ne 0) { throw "Backend tests failed" }
cd ..

Write-Host "--- ⚛️ Frontend Type Check ---" -ForegroundColor Yellow
cd frontend
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) { throw "Frontend type check failed" }

Write-Host "--- 📦 Frontend Build ---" -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
cd ..

Write-Host "✅ All checks passed successfully!" -ForegroundColor Green
