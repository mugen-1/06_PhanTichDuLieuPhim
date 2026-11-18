#!/usr/bin/env python3
# Inner join. Ket qua: imdb_id, movie_id, title, release_year, genres, imdb_rating, num_votes
import sys

cur, m, i = None, [], []

def xuat():
    for a in m:
        for b in i:
            print("\t".join([cur] + a + b))

for line in sys.stdin:
    p = line.rstrip("\n").split("\t")
    if p[0] != cur:
        xuat()
        cur, m, i = p[0], [], []
    (m if p[1] == "M" else i).append(p[2:])
xuat()
