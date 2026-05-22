import string
import time
import psutil
import os
import sys

LETTERS = string.ascii_lowercase
OUTPUT_FILE = "pass.txt"
MIN_CPU = 50.0
MAX_CPU = 75.0
TOTAL = (26 ** 4) * 10000

def format_time(seconds):
    seconds = int(seconds)
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{days}d {hours}h {minutes}m {secs}s"

def generator():
    for a in LETTERS:
        for b in LETTERS:
            for c in LETTERS:
                for d in LETTERS:
                    prefix = f"{a}{b}{c}{d}"
                    for num in range(10000):
                        yield f"{prefix}{num:04d}\n"

def process_cpu(proc, last_cpu_time, last_wall):
    now_wall = time.time()
    cpu_times = proc.cpu_times()
    now_cpu = cpu_times.user + cpu_times.system
    cpu_used = now_cpu - last_cpu_time
    wall_used = now_wall - last_wall
    if wall_used <= 0:
        return 0.0, now_cpu, now_wall
    percent = (cpu_used / wall_used) * 100.0
    return percent, now_cpu, now_wall

def generate():
    proc = psutil.Process(os.getpid())
    gen = generator()
    count = 0
    start = time.time()
    batch = 80000
    sleep_time = 0.0

    cpu_times = proc.cpu_times()
    last_cpu = cpu_times.user + cpu_times.system
    last_wall = time.time()

    print("Starting password list generation...")
    with open(OUTPUT_FILE, "w", buffering=1024*1024*8) as f:  # bigger buffer
        while True:
            wrote = 0
            try:
                for _ in range(batch):
                    f.write(next(gen))
                    wrote += 1
            except StopIteration:
                break

            count += wrote
            cpu, last_cpu, last_wall = process_cpu(proc, last_cpu, last_wall)

            # Dynamic throttling
            if cpu > MAX_CPU:
                sleep_time += 0.03
                batch = max(10000, int(batch * 0.85))
            elif cpu < MIN_CPU:
                sleep_time = max(0.0, sleep_time - 0.015)
                batch = min(300000, int(batch * 1.12))

            if sleep_time > 0:
                time.sleep(sleep_time)

            elapsed = time.time() - start
            speed = count / elapsed if elapsed > 0 else 0
            eta = (TOTAL - count) / speed if speed > 0 else 0

            print(f"Generated: {count:,}/{TOTAL:,} | CPU: {cpu:.1f}% | "
                  f"Sleep: {sleep_time:.2f}s | Batch: {batch:,} | "
                  f"Speed: {speed:,.0f}/s | ETA: {format_time(eta)}", flush=True)

    print("\n✅ Password list generation completed!")

if __name__ == "__main__":
    generate()
