#!/bin/bash

echo "⏳ Initializing database..."

python createTables.py
python moveToDb.py

echo "🚀 Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
