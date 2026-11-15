#!/usr/bin/env python3
# MR1 - Loc va chuan hoa ban ghi OMDb (job chi co Map).
# Moi dong vao la 1 ban ghi JSON cua OMDb. Ban ghi hop le duoc in ra dang tab:
#   imdb_id  imdb_rating  imdb_votes  metascore  rotten_tomatoes
# "N/A" doi thanh \N (NULL). Ban ghi loi chi tang bo dem, khong in ra.
import json
import re
import sys


def dem(ten, so=1):
    # Hadoop Streaming doc dong nay tu stderr va cong vao bo dem cua job
    sys.stderr.write(f"reporter:counter:MR1_OMDb,{ten},{so}\n")


def so(s):
    # "1,234,567" -> "1234567" ; "93%" -> "93" ; "N/A" -> \N
    if not isinstance(s, str) or s.strip() in ("", "N/A"):
        return "\\N"
    return re.sub(r"[^\d.]", "", s) or "\\N"


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        d = json.loads(line)
    except ValueError:
        dem("Loi_JSON_hong")
        continue
    if d.get("Response") != "True":
        dem("Loi_Response_False")
        continue
    imdb = d.get("imdbID", "")
    if not re.match(r"^tt\d+$", imdb):
        dem("Loi_imdbID_sai")
        continue
    rt = "\\N"
    for x in d.get("Ratings", []):
        if x.get("Source") == "Rotten Tomatoes":
            rt = so(x.get("Value"))
    gia_tri = [so(d.get("imdbRating")), so(d.get("imdbVotes")), so(d.get("Metascore")), rt]
    for ten, g in zip(["ThieuDiemIMDb", "ThieuVotes", "ThieuMetascore", "ThieuRottenTomatoes"], gia_tri):
        if g == "\\N":
            dem(ten)
    dem("HopLe")
    print(imdb + "\t" + "\t".join(gia_tri))
