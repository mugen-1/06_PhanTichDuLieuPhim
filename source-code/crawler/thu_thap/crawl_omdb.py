#!/usr/bin/env python3
# Nguon 2 - OMDb API (omdbapi.com): diem IMDb, Rotten Tomatoes, Metacritic,
# doanh thu phong ve My, giai thuong. Tra cuu theo imdb_id lay tu du lieu TMDB.
# Key mien phi gioi han ~1000 luot/ngay: het luot thi chuong trinh tu dung,
# hom sau chay lai lenh cu se lay tiep phan con thieu.
#
# Cach chay:  export OMDB_API_KEY=...
#             python3 crawl_omdb.py

import json
import os
import sys
import time

import requests

DANH_SACH = "dataset/raw/tmdb/danh_sach_tmdb.txt"
TMDB = "dataset/raw/tmdb/tmdb_movies.jsonl"
OUT = "dataset/raw/omdb/omdb_movies.jsonl"
LOG_LOI = "dataset/raw/omdb/omdb_loi.txt"
URL = "https://www.omdbapi.com/"


def doc_imdb_id():
    # Lay imdb_id cua cac phim trong danh sach TMDB (theo dung thu tu danh sach)
    with open(DANH_SACH, encoding="utf-8") as f:
        ds = [line.strip() for line in f if line.strip()]
    tmdb2imdb = {}
    with open(TMDB, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            tmdb2imdb[str(p["id"])] = p.get("imdb_id")
    ids = [tmdb2imdb.get(t) for t in ds]
    thieu = sum(1 for i in ids if not i)
    print(f"Danh sach TMDB: {len(ds)} phim, khong co imdb_id (hoac chua lay duoc tu TMDB): {thieu}")
    return list(dict.fromkeys(i for i in ids if i))     # 2 phim TMDB co the chung 1 imdb_id


def main():
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        sys.exit("Chua co bien moi truong OMDB_API_KEY")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    ids = doc_imdb_id()
    da_lay = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                da_lay.add(json.loads(line)["imdbID"])
    # Phim OMDb da tra loi "khong tim thay" thi khong hoi lai (khong ton luot)
    khong_co = set()
    if os.path.exists(LOG_LOI):
        with open(LOG_LOI, encoding="utf-8") as f:
            for line in f:
                ma, _, ly_do = line.rstrip("\n").partition("\t")
                if "not found" in ly_do.lower() or "incorrect" in ly_do.lower():
                    khong_co.add(ma)
    can_lay = [i for i in ids if i not in da_lay and i not in khong_co]
    print(f"Da co: {len(da_lay)} | OMDb khong co: {len(khong_co)} | can lay: {len(can_lay)}")

    ok = loi = 0
    with open(OUT, "a", encoding="utf-8") as out, open(LOG_LOI, "a", encoding="utf-8") as log:
        for n, imdb_id in enumerate(can_lay, 1):
            try:
                r = requests.get(URL, params={"i": imdb_id, "apikey": api_key, "plot": "short"}, timeout=15)
                d = r.json()
            except (requests.RequestException, ValueError) as e:
                log.write(f"{imdb_id}\t{e}\n")
                loi += 1
                time.sleep(2)
                continue
            if d.get("Response") == "True":
                out.write(json.dumps(d, ensure_ascii=False) + "\n")
                ok += 1
            else:
                thong_bao = d.get("Error", "khong ro")
                if "limit" in thong_bao.lower() or "invalid api key" in thong_bao.lower():
                    print(f"Dung lai: {thong_bao}")        # het luot trong ngay / sai key
                    break
                log.write(f"{imdb_id}\t{thong_bao}\n")
                loi += 1
            if n % 100 == 0:
                print(f"  {n}/{len(can_lay)}  thanh cong={ok}  loi={loi}")
                out.flush()
            time.sleep(0.1)
    print(f"Xong luot nay. Thanh cong: {ok}, loi: {loi}. Tong da co: {len(da_lay) + ok}/{len(ids)}")


if __name__ == "__main__":
    main()
