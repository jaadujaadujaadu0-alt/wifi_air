from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import subprocess
import threading

app = FastAPI(title="WiFi Air Cracker")

class AttackRequest(BaseModel):
    wordlist: str = "part1.txt"
    capture: str = "capture.pcap"

def run_aircrack_live(wordlist: str, capture: str):
    wordlist_path = f"wordlists/{wordlist}"
    output_file = "cracked.txt"
    
    print(f"🚀 Starting aircrack-ng attack with: {wordlist}")
    print(f"Wordlist size: {os.path.getsize(wordlist_path) / (1024*1024*1024):.2f} GB")
    
    try:
        cmd = [
            "aircrack-ng", 
            "-w", wordlist_path, 
            capture, 
            "-l", output_file
        ]
        
        # Run with real-time output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("🔴 Aircrack-ng is running... (Live logs below)")
        
        for line in process.stdout:
            line = line.strip()
            if line:
                print(line)           # This will show in Railway logs
                # Optional: Save important lines
                if "KEY FOUND" in line or "cracked" in line.lower():
                    print(f"🎉 POSSIBLE PASSWORD FOUND: {line}")
        
        process.wait()
        print("✅ Aircrack-ng process finished.")
        
    except Exception as e:
        print(f"❌ Error running aircrack: {e}")

@app.post("/attack")
def start_attack(req: AttackRequest, background_tasks: BackgroundTasks):
    wordlist_path = f"wordlists/{req.wordlist}"
    
    if not os.path.exists(wordlist_path):
        raise HTTPException(404, f"Wordlist not found: {req.wordlist}")
    if not os.path.exists(req.capture):
        raise HTTPException(404, f"Capture not found: {req.capture}")

    background_tasks.add_task(run_aircrack_live, req.wordlist, req.capture)
    
    return {
        "status": "attack_started",
        "message": "Live logs will appear in Railway. Check logs now."
    }

@app.get("/status")
def get_status():
    return {
        "wordlists_available": os.listdir("wordlists") if os.path.exists("wordlists") else [],
        "cracked_file_exists": os.path.exists("cracked.txt"),
        "message": "Check Railway live logs for aircrack progress"
    }
