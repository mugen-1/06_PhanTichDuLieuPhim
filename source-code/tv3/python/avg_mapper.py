#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.replace('\r', '').strip()
    if not line: continue
    
    fields = line.split("\t")
    if len(fields) < 2: fields = line.split(",") 
    
    if "movie_id" in line: continue
    
    if len(fields) == 2:
        movie_id = fields[0].strip()
        genre_id = fields[1].strip()
        print(f"GENRE\t{genre_id}\t{movie_id}")
        
    elif len(fields) >= 16:
        movie_id = fields[0].strip()
        # Cột 14 (index 13) là tmdb_vote_avg
        rating = fields[13].strip() 
        print(f"MOVIE\t{movie_id}\t{rating}")
