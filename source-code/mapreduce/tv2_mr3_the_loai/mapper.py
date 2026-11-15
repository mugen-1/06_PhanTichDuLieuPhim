#!/usr/bin/env python3
# MR3 - Chuan hoa the loai trong du lieu OMDb.
# Truong Genre dang "Action, Sci-Fi, Thriller" -> tach thanh tung dong
# (imdb_id, the loai) va doi ten ve bo ten chung voi TMDB.
import json
import sys

DOI_TEN = {"Sci-Fi": "Science Fiction", "Musical": "Music", "Film-Noir": "Film Noir"}
BO_QUA = {"N/A", "Short", ""}

for line in sys.stdin:
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("Response") != "True":
        continue
    for g in (d.get("Genre") or "").split(","):
        g = g.strip()
        if g in BO_QUA:
            sys.stderr.write("reporter:counter:MR3_TheLoai,BoQua,1\n")
            continue
        if g in DOI_TEN:
            sys.stderr.write("reporter:counter:MR3_TheLoai,DaDoiTen,1\n")
        print(f"{d['imdbID']}\t{DOI_TEN.get(g, g)}")
