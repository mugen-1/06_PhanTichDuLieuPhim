#!/usr/bin/env python3
# MR2 - Loai phim trung theo imdb_id (du lieu TMDB dang JSON lines).
# Map: moi phim -> key = imdb_id, value = tmdb_id | vote_count | title
import json
import sys

for line in sys.stdin:
    try:
        p = json.loads(line)
    except ValueError:
        sys.stderr.write("reporter:counter:MR2_LoaiTrung,Loi_JSON,1\n")
        continue
    imdb = (p.get("imdb_id") or "").strip()
    if not imdb.startswith("tt"):
        sys.stderr.write("reporter:counter:MR2_LoaiTrung,ThieuImdbId,1\n")
        continue
    title = (p.get("title") or "").replace("\t", " ")
    print(f"{imdb}\t{p.get('id')}\t{p.get('vote_count') or 0}\t{title}")
