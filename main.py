from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import subprocess

app = FastAPI(title="WiFi Wordlist Generator & Cracker")

class GenerateRequest(BaseModel):
    mask: str
    part: int = 1
    total_parts: int = 1
    filename: str = "wordlist.txt"

class AttackRequest(BaseModel):
    wordlist: str = "part1.txt"
    capture: str = "capture.pcap"

# ===================== GENERATOR =====================
import string
import itertools
from functools import reduce
import operator

LETTERS_LOWER = string.ascii_lowercase
LETTERS_UPPER = string.ascii_uppercase
DIGITS = string.digits
SPECIALS = "!@#$%^&*()_+-=[]{}|;:,.<>/?"

def parse_mask(mask: str):
    charset_map = {'c': LETTERS_LOWER, 'C': LETTERS_UPPER, 'd': DIGITS, 's': SPECIALS}
    return [charset_map.get(char, char) for char in mask]

def count_total(mask: str):
    charsets = parse_mask(mask)
    return reduce(operator.mul, (len(cs) for cs in charsets), 1)

def generate_part(mask: str, part: int, total_parts: int, output_file: str):
    charsets = parse_mask(mask)
    total = count_total(mask)
    start_index = (total * (part - 1)) // total_parts
    end_index = (total * part) // total_parts

    os.makedirs("wordlists", exist_ok=True)
    output_path = f"wordlists/{output_file}"

    print(f"🔨 Generating {mask} | Part {part}/{total_parts} | Total: {total:,}")

    with open(output_path, "w", buffering=8*1024*1024) as f:
        count = 0
        generated = 0
        for candidate in itertools.product(*charsets):
            if count >= start_index:
                f.write(''.join(candidate) + '\n')
                generated += 1
                if generated % 100000 == 0:
                    print(f"Part {part}/{total_parts} → Generated: {generated:,}", flush=True)
                if count >= end_index - 1:
                    break
            count += 1

    print(f"✅ Part {part}/{total_parts} completed!")
    return generated

# ===================== ATTACK =====================
def run_aircrack_live(wordlist: str, capture: str):
    wordlist_path = f"wordlists/{wordlist}"
    print(f"🚀 Starting aircrack-ng with {wordlist}")
    print(f"File size: {os.path.getsize(wordlist_path)/(1024**3):.2f} GB")

    try:
        cmd = ["aircrack-ng", "-w", wordlist_path, capture, "-l", "cracked.txt"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            line = line.strip()
            if line:
                print(line, flush=True)
        process.wait()
        print("✅ Aircrack-ng finished.")
    except Exception as e:
        print(f"❌ Error: {e}")

@app.get("/")
def home():
    return {"status": "online", "endpoints": ["/generate", "/attack", "/status"]}

@app.post("/generate")
def generate_wordlist(req: GenerateRequest):
    try:
        generated = generate_part(req.mask, req.part, req.total_parts, req.filename)
        return {
            "status": "success",
            "file": f"wordlists/{req.filename}",
            "generated": generated
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/attack")
def start_attack(req: AttackRequest, background_tasks: BackgroundTasks):
    wordlist_path = f"wordlists/{req.wordlist}"
    if not os.path.exists(wordlist_path):
        raise HTTPException(404, f"Wordlist not found: {req.wordlist}")
    if not os.path.exists(req.capture):
        raise HTTPException(404, f"Capture not found: {req.capture}")

    background_tasks.add_task(run_aircrack_live, req.wordlist, req.capture)
    return {"status": "attack_started", "message": "Check Railway logs for live progress"}

@app.get("/status")
def get_status():
    return {
        "wordlists": os.listdir("wordlists") if os.path.exists("wordlists") else [],
        "cracked_exists": os.path.exists("cracked.txt")
    }
