FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    aircrack-ng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir psutil

COPY bot.py run.sh ./
RUN chmod +x run.sh

# Copy capture file if present
COPY capture.pcap* ./

CMD ["./run.sh"]
