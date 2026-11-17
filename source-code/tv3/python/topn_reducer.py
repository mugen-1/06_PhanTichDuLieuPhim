#!/usr/bin/env python3
import sys
import heapq

top_movies = [] # Dùng heap để lấy Top 10

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        rating_str, movie_info = line.split("\t", 1)
        rating = float(rating_str)
        # Dùng heap để giữ lại 10 phim điểm cao nhất
        if len(top_movies) < 10:
            heapq.heappush(top_movies, (rating, movie_info))
        else:
            heapq.heappushpop(top_movies, (rating, movie_info))
    except ValueError:
        pass

# In ra theo thứ tự giảm dần
for rating, movie_info in sorted(top_movies, reverse=True):
    print(movie_info)
