#!/bin/bash
set -e

echo "🚀 Starting Project Verification..."

echo "--- 🐍 Backend Tests ---"
cd backend
pytest -q
cd ..

echo "--- ⚛️ Frontend Type Check ---"
cd frontend
npx tsc --noEmit
echo "--- 📦 Frontend Build ---"
npm run build
cd ..

echo "✅ All checks passed successfully!"
