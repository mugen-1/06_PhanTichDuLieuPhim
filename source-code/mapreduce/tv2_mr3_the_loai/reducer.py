#!/usr/bin/env python3
# MR3 - Reduce: gom theo imdb_id, bo the loai lap lai, in 1 dong / cap (phim, the loai).
import sys

key_cu, da_co = None, set()
for line in sys.stdin:
    imdb_id, genre = line.rstrip("\n").split("\t", 1)
    if imdb_id != key_cu:
        key_cu, da_co = imdb_id, set()
    if genre not in da_co:
        da_co.add(genre)
        print(f"{imdb_id}\t{genre}")
