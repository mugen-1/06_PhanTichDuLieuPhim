#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.replace('\r', '').strip()
    if not line: continue
    
    fields = [f.strip() for f in line.split("\t")]
    
    # Bỏ qua dòng tiêu đề
    if "movie_id" in line or len(fields) < 16: continue
        
    try:
        title = fields[2]
        # ĐÃ SỬA: Cột 15 (index 14) là Votes, Cột 16 (index 15) là Rating
        votes = float(fields[14]) 
        rating = float(fields[15])
        
        if votes >= 1000:
            print(f"{rating}\t{title} (Rating: {rating}, Votes: {votes})")
    except ValueError:
        pass
