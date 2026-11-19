#!/usr/bin/env python3
# Chuyen du lieu sach cua trunghieu (dataset/clean) sang dinh dang dataset/SCHEMA.txt
# de Hive, HBase, MapReduce va web cua trungtruc doc duoc.
#   movies.tsv        11 cot (the loai ghep bang |, overview lay tu movie_texts.jsonl)
#   imdb_ratings.tsv  3 cot  (imdb_id, imdb_rating, imdb_votes cua OMDb)
#   ratings.tsv       4 cot  (lay tu reviews: moi author = 1 user, diem thang 10 doi ve thang 5)
# Chay tu thu muc goc repo: python3 source-code/trungtruc/chuyen_doi_du_lieu.py
import csv, json, os, sys
from datetime import datetime, timezone

SRC = sys.argv[1] if len(sys.argv) > 1 else "dataset/clean"
OUT = sys.argv[2] if len(sys.argv) > 2 else "dataset/chuyen_doi"
os.makedirs(OUT, exist_ok=True)
csv.field_size_limit(10**9)


def doc_tsv(ten):
    with open(os.path.join(SRC, ten), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def sach(v):
    """\\N -> rong; bo TAB va xuong dong trong o."""
    if v is None or v == "\\N":
        return ""
    return " ".join(str(v).split())


ten_the_loai = {r["genre_id"]: r["genre_name"] for r in doc_tsv("genres.tsv")}
the_loai = {}
for r in doc_tsv("movie_genres.tsv"):
    the_loai.setdefault(r["movie_id"], []).append(ten_the_loai.get(r["genre_id"], r["genre_id"]))

overview = {}
with open(os.path.join(SRC, "movie_texts.jsonl"), encoding="utf-8") as f:
    for line in f:
        d = json.loads(line)
        overview[str(d["movie_id"])] = d.get("overview_tmdb") or d.get("wiki_tom_tat") or ""

phim, n_imdb = set(), 0
with open(os.path.join(OUT, "movies.tsv"), "w", encoding="utf-8") as fm, \
     open(os.path.join(OUT, "imdb_ratings.tsv"), "w", encoding="utf-8") as fi:
    for r in doc_tsv("movies.tsv"):
        mid = r["movie_id"]
        if not mid.isdigit() or not r["year"].isdigit():
            continue
        phim.add(mid)
        fm.write("\t".join(sach(x) for x in [
            mid, r["imdb_id"], r["title"], r["release_date"], r["year"], r["runtime"],
            "|".join(sorted(the_loai.get(mid, []))), r["language"],
            r["budget"], r["revenue"], overview.get(mid, "")]) + "\n")
        if sach(r["imdb_rating"]) and sach(r["imdb_votes"]):
            fi.write("%s\t%s\t%s\n" % (r["imdb_id"], sach(r["imdb_rating"]), sach(r["imdb_votes"])))
            n_imdb += 1

user_id, diem = {}, {}
for r in doc_tsv("reviews.tsv"):
    if r["movie_id"] not in phim or sach(r["rating"]) == "":
        continue
    uid = user_id.setdefault(r["author"], len(user_id) + 1)
    try:
        ts = int(datetime.strptime(r["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp())
    except ValueError:
        ts = 0
    diem[(uid, int(r["movie_id"]))] = (round(float(r["rating"]) / 2, 2), ts)  # trung thi giu ban sau

with open(os.path.join(OUT, "ratings.tsv"), "w", encoding="utf-8") as fr:
    for (uid, mid), (d, ts) in sorted(diem.items()):
        fr.write("%d\t%d\t%s\t%d\n" % (uid, mid, d, ts))

print("movies: %d | imdb_ratings: %d | ratings: %d (tu %d nguoi review)" % (len(phim), n_imdb, len(diem), len(user_id)))
print("Ghi vao", OUT)
