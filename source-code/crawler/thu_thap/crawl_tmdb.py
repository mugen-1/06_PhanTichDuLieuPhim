#!/usr/bin/env python3
# Nguon 1 - TMDB API (themoviedb.org)
# Buoc 1: lay danh sach N phim co nhieu luot vote nhat (API /discover/movie, 20 phim/trang)
# Buoc 2: lay chi tiet tung phim (kem dien vien, dao dien, review)
# Chay lai duoc nhieu lan: phim nao da co trong file thi bo qua.
#
# Cach chay:  export TMDB_API_KEY=...       (khong ghi key vao code / git)
#             python3 crawl_tmdb.py --so-phim 1500

import json
import os
import sys
import time

import requests

DANH_SACH = "dataset/raw/tmdb/danh_sach_tmdb.txt"
OUT = "dataset/raw/tmdb/tmdb_movies.jsonl"
LOG_LOI = "dataset/raw/tmdb/tmdb_loi.txt"
API = "https://api.themoviedb.org/3"


def goi_api(url, params):
    # Goi API, gap 429 (goi qua nhanh) thi cho roi thu lai, toi da 3 lan
    for _ in range(3):
        try:
            r = requests.get(url, params=params, timeout=15)
        except requests.RequestException:
            time.sleep(2)
            continue
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", 5)))
            continue
        return r
    return None


def lay_danh_sach(api_key, so_phim):
    # Da co danh sach du so phim thi dung lai, khong goi lai
    if os.path.exists(DANH_SACH):
        with open(DANH_SACH, encoding="utf-8") as f:
            ids = [line.strip() for line in f if line.strip()]
        if len(ids) >= so_phim:
            return ids[:so_phim]

    ids = []
    trang = 1
    while len(ids) < so_phim and trang <= 500:
        r = goi_api(f"{API}/discover/movie", {"api_key": api_key, "sort_by": "vote_count.desc",
                                              "include_adult": "false", "page": trang})
        if r is None or r.status_code != 200:
            sys.exit(f"Loi khi lay trang {trang}: {r.status_code if r is not None else 'mat ket noi'}")
        for p in r.json()["results"]:
            if str(p["id"]) not in ids:          # 2 trang lien tiep co the tra trung phim
                ids.append(str(p["id"]))
        trang += 1
        time.sleep(0.05)
    ids = ids[:so_phim]
    with open(DANH_SACH, "w", encoding="utf-8") as f:
        f.write("\n".join(ids) + "\n")
    print(f"Lay danh sach: {trang - 1} trang -> {len(ids)} phim")
    return ids


def rut_gon(d):
    # Chi giu cac truong can dung, file raw khong qua nang
    return {
        "id": d.get("id"),
        "imdb_id": d.get("imdb_id"),
        "title": d.get("title"),
        "original_title": d.get("original_title"),
        "release_date": d.get("release_date"),
        "runtime": d.get("runtime"),
        "budget": d.get("budget"),
        "revenue": d.get("revenue"),
        "original_language": d.get("original_language"),
        "genres": [g["name"] for g in d.get("genres", [])],
        "overview": d.get("overview"),
        "vote_average": d.get("vote_average"),
        "vote_count": d.get("vote_count"),
        "popularity": d.get("popularity"),
        "countries": [c["iso_3166_1"] for c in d.get("production_countries", [])],
        "cast": [{"id": c["id"], "name": c["name"], "order": c.get("order")}
                 for c in d.get("credits", {}).get("cast", [])[:10]],
        "directors": [{"id": c["id"], "name": c["name"]}
                      for c in d.get("credits", {}).get("crew", []) if c.get("job") == "Director"],
        "reviews": [{"author": r.get("author"),
                     "rating": (r.get("author_details") or {}).get("rating"),
                     "content": r.get("content"),
                     "created_at": r.get("created_at")}
                    for r in d.get("reviews", {}).get("results", [])],
    }


def main():
    api_key = os.environ.get("TMDB_API_KEY")
    if not api_key:
        sys.exit("Chua co bien moi truong TMDB_API_KEY")
    so_phim = 1500
    if "--so-phim" in sys.argv:
        so_phim = int(sys.argv[sys.argv.index("--so-phim") + 1])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ids = lay_danh_sach(api_key, so_phim)

    da_lay = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                da_lay.add(str(json.loads(line)["id"]))
    can_lay = [i for i in ids if i not in da_lay]
    print(f"Danh sach: {len(ids)} phim | da co san: {len(ids) - len(can_lay)} | can lay them: {len(can_lay)}")

    ok = loi = 0
    with open(OUT, "a", encoding="utf-8") as out, open(LOG_LOI, "a", encoding="utf-8") as log:
        for n, tmdb_id in enumerate(can_lay, 1):
            r = goi_api(f"{API}/movie/{tmdb_id}", {"api_key": api_key, "language": "en-US",
                                                    "append_to_response": "credits,reviews"})
            if r is not None and r.status_code == 200:
                out.write(json.dumps(rut_gon(r.json()), ensure_ascii=False) + "\n")
                ok += 1
            else:
                log.write(f"{tmdb_id}\t{r.status_code if r is not None else 'mat ket noi'}\n")
                loi += 1
            if n % 100 == 0:
                print(f"  {n}/{len(can_lay)}  thanh cong={ok}  loi={loi}")
                out.flush()
            time.sleep(0.05)
    print(f"Xong. Lay them thanh cong: {ok}, loi: {loi}")


if __name__ == "__main__":
    main()
