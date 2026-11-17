#!/usr/bin/env python3
import sys
from collections import defaultdict

movie_ratings = {}
genre_movies = defaultdict(list)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split("\t")
    
    if parts[0] == "MOVIE":
        movie_id = parts[1]
        try:
            movie_ratings[movie_id] = float(parts[2])
        except ValueError:
            pass
    elif parts[0] == "GENRE":
        genre_id = parts[1]
        movie_id = parts[2]
        genre_movies[genre_id].append(movie_id)

for genre_id, movie_ids in genre_movies.items():
    total = 0
    count = 0
    for mid in movie_ids:
        if mid in movie_ratings:
            total += movie_ratings[mid]
            count += 1
    if count > 0:
        print(f"The loai {genre_id}: Diem trung binh = {total/count:.2f} (co {count} phim)")
