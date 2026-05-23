#!/bin/bash
apt-get update && apt-get install -y aircrack-ng

pip install fastapi uvicorn psutil

echo "Starting FastAPI Server..."
uvicorn main:app --host 0.0.0.0 --port 8000
