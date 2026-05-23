from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
from generator import generate_part, count_total

app = FastAPI(title="Railway Wordlist Generator")

class GenerateRequest(BaseModel):
    mask: str                    # e.g. "ccccdddd", "Ccccsdddd"
    part: int = 1
    total_parts: int = 1
    filename: str = "wordlist.txt"

class AttackRequest(BaseModel):
    wordlist: str = "wordlist.txt"
    capture: str = "capture.pcap"

@app.get("/")
def home():
    return {"status": "running", "message": "Wordlist Generator + Aircrack API"}

@app.post("/generate")
def generate_wordlist(req: GenerateRequest):
    try:
        total = count_total(req.mask)
        output_path = f"wordlists/{req.filename}"
        
        print(f"Generating mask: {req.mask} | Part: {req.part}/{req.total_parts} | Total: {total:,}")
        
        generated = generate_part(
            mask=req.mask,
            part=req.part,
            total_parts=req.total_parts,
            output_file=output_path
        )
        
        return {
            "status": "success",
            "mask": req.mask,
            "part": req.part,
            "total_parts": req.total_parts,
            "generated": generated,
            "file": output_path,
            "total_possible": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attack")
def start_attack(req: AttackRequest):
    wordlist_path = f"wordlists/{req.wordlist}" if not req.wordlist.startswith('/') else req.wordlist
    capture_path = req.capture

    if not os.path.exists(wordlist_path):
        raise HTTPException(status_code=404, detail=f"Wordlist not found: {wordlist_path}")
    if not os.path.exists(capture_path):
        raise HTTPException(status_code=404, detail=f"Capture file not found: {capture_path}")

    try:
        output_file = "cracked.txt"
        cmd = f"aircrack-ng -w {wordlist_path} {capture_path} -l {output_file}"
        
        print("Starting aircrack-ng attack...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        with open(output_file, "r") as f:
            cracked = f.read().strip()
        
        return {
            "status": "completed",
            "cracked_password": cracked if cracked else "Not found",
            "aircrack_output": result.stdout[-500:]  # last 500 chars
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
