FROM python:3.11-slim

# Install aircrack-ng
RUN apt-get update && apt-get install -y \
    aircrack-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies directly (no requirements.txt needed)
RUN pip install --no-cache-dir psutil

# Copy all project files
COPY bot.py run.sh ./

# Make run script executable
RUN chmod +x run.sh

# Copy your capture file (if it exists)
COPY capture.pcap* ./

CMD ["./run.sh"]
