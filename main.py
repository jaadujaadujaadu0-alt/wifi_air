from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import subprocess
import threading
from generator import generate_part, count_total

app = FastAPI(title="Railway Wordlist Generator")

class GenerateRequest(BaseModel):
    mask: str
    part: int = 1
    total_parts: int = 1
    filename: str = "wordlist.txt"

class AttackRequest(BaseModel):
    wordlist: str = "part1.txt"
    capture: str = "capture.pcap"

# Background attack function
def run_aircrack(wordlist: str, capture: str):
    wordlist_path = f"wordlists/{wordlist}" if not wordlist.startswith('/') else wordlist
    output_file = "cracked.txt"
    
    print(f"🚀 Starting background aircrack-ng attack with {wordlist}")
    
    try:
        cmd = f"aircrack-ng -w {wordlist_path} {capture} -l {output_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)  # 1 hour max
        
        with open(output_file, "a") as f:
            f.write("\n--- Aircrack finished ---\n")
            f.write(result.stdout)
        
        print("✅ Aircrack-ng background task completed!")
    except Exception as e:
        print(f"❌ Attack error: {e}")

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/generate")
def generate_wordlist(req: GenerateRequest):
    try:
        total = count_total(req.mask)
        output_path = f"wordlists/{req.filename}"
        
        print(f"Generating {req.mask} | Part {req.part}/{req.total_parts}")
        
        generated = generate_part(
            mask=req.mask,
            part=req.part,
            total_parts=req.total_parts,
            output_file=output_path
        )
        
        return {
            "status": "success",
            "file": output_path,
            "generated": generated,
            "total": total
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

    # Add to background
    background_tasks.add_task(run_aircrack, req.wordlist, req.capture)
    
    return {
        "status": "attack_started_in_background",
        "message": f"Attack started with {req.wordlist}. Check Railway logs for progress.",
        "output_file": "cracked.txt"
    }
