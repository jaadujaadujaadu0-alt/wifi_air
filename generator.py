import string
import itertools
import os
from typing import List, Optional

LETTERS_LOWER = string.ascii_lowercase
LETTERS_UPPER = string.ascii_uppercase
DIGITS = string.digits
SPECIALS = "!@#$%^&*()_+-=[]{}|;:,.<>/?"

def parse_mask(mask: str) -> List[str]:
    charset_map = {
        'c': LETTERS_LOWER,
        'C': LETTERS_UPPER,
        'd': DIGITS,
        's': SPECIALS,
    }
    return [charset_map.get(char, char) for char in mask]

def count_total(mask: str) -> int:
    charsets = parse_mask(mask)
    return int(itertools.prod(len(cs) for cs in charsets))

def generate_part(mask: str, part: int, total_parts: int, output_file: str, chunk_size=100000):
    charsets = parse_mask(mask)
    total = count_total(mask)
    
    if total_parts < 1 or part < 1 or part > total_parts:
        raise ValueError("Invalid part or total_parts")

    start_index = (total * (part - 1)) // total_parts
    end_index = (total * part) // total_parts

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", buffering=8*1024*1024) as f:
        count = 0
        generated = 0
        
        for candidate in itertools.product(*charsets):
            if count >= start_index:
                f.write(''.join(candidate) + '\n')
                generated += 1
                
                if generated % chunk_size == 0:
                    print(f"Part {part}/{total_parts} → Generated: {generated:,}", flush=True)
                
                if count >= end_index - 1:
                    break
            count += 1

    print(f"✅ Part {part}/{total_parts} completed: {generated:,} passwords")
    return generated
