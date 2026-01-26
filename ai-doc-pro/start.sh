#!/bin/bash

# AI Doc Pro - Loyihani ishga tushirish scripti

echo "🚀 AI Doc Pro ishga tushirilmoqda..."

# Backend
echo "📦 Backend o'rnatilmoqda..."
cd backend
python -m venv venv 2>/dev/null
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt -q

echo "🔧 Backend serveri ishga tushirilmoqda (port 8000)..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

# Frontend
echo "📦 Frontend o'rnatilmoqda..."
cd frontend
npm install -q

echo "🌐 Frontend serveri ishga tushirilmoqda (port 3000)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Loyiha muvaffaqiyatli ishga tushirildi!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To'xtatish uchun Ctrl+C bosing"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
