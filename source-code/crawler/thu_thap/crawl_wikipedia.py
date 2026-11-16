#!/usr/bin/env python3
# Nguon 3 - Wikipedia (uu tien tieng Viet), khong can key.
# Buoc 1: hoi Wikidata (SPARQL) xem moi imdb_id ung voi bai Wikipedia nao (vi / en),
#         moi lan hoi 50 phim, loi thi cho roi thu lai.
# Buoc 2: voi tung phim, lay ten va doan tom tat cua bai viet (REST API cua Wikipedia).
#         Co bai tieng Viet thi lay tieng Viet, khong co thi lay tieng Anh.

import json
import os
import time
from urllib.parse import quote

import requests

TMDB = "dataset/raw/tmdb/tmdb_movies.jsonl"
DANH_SACH = "dataset/raw/tmdb/danh_sach_tmdb.txt"
OUT = "dataset/raw/wikipedia/wiki_movies.jsonl"
SPARQL = "https://query.wikidata.org/sparql"
# Wikimedia yeu cau ghi ro chuong trinh nao dang goi
HEADERS = {"User-Agent": "DoAnBigData-Nhom06/1.0 (do an sinh vien; https://github.com/mugen-1/06_PhanTichDuLieuPhim)"}

CAU_HOI = """
SELECT ?imdb ?item ?tenVi ?baiVi ?baiEn WHERE {
  VALUES ?imdb { %s }
  ?item wdt:P345 ?imdb .
  OPTIONAL { ?item rdfs:label ?tenVi FILTER(LANG(?tenVi) = "vi") }
  OPTIONAL { ?a schema:about ?item ; schema:isPartOf <https://vi.wikipedia.org/> ; schema:name ?baiVi }
  OPTIONAL { ?b schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?baiEn }
}"""


def doc_imdb_id():
    with open(DANH_SACH, encoding="utf-8") as f:
        ds = [line.strip() for line in f if line.strip()]
    tmdb2imdb = {}
    with open(TMDB, encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            tmdb2imdb[str(p["id"])] = p.get("imdb_id")
    return list(dict.fromkeys(tmdb2imdb[t] for t in ds if tmdb2imdb.get(t)))


def hoi_wikidata(nhom):
    # Hoi Wikidata cho 1 nhom phim. May chu Wikidata hay qua tai (loi 502, 503, 429, het thoi gian)
    # -> cho roi thu lai, toi da 5 lan, moi lan cho lau hon (5, 10, 20, 40, 80 giay).
    q = CAU_HOI % " ".join(f'"{x}"' for x in nhom)
    for lan in range(5):
        try:
            r = requests.get(SPARQL, params={"query": q, "format": "json"}, headers=HEADERS, timeout=60)
            if r.status_code == 200:
                break
            ly_do = r.status_code
        except requests.RequestException as e:
            ly_do = type(e).__name__
        cho = 5 * 2 ** lan
        print(f"    Wikidata loi {ly_do}, cho {cho} giay roi thu lai ({lan + 1}/5)")
        time.sleep(cho)
    else:
        return None                              # 5 lan deu loi -> bo qua nhom nay, lan sau chay lai
    ket_qua = {}
    for b in r.json()["results"]["bindings"]:
        imdb = b["imdb"]["value"]
        if imdb in ket_qua:                      # 1 phim co the tra ve nhieu dong -> lay dong dau
            continue
        ket_qua[imdb] = {
            "wikidata_id": b["item"]["value"].rsplit("/", 1)[-1],
            "ten_vi": b.get("tenVi", {}).get("value"),
            "bai_vi": b.get("baiVi", {}).get("value"),
            "bai_en": b.get("baiEn", {}).get("value"),
        }
    return ket_qua


def lay_tom_tat(lang, bai):
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote(bai.replace(' ', '_'), safe='')}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    d = r.json()
    return {"tieu_de": d.get("title"), "tom_tat": d.get("extract"),
            "url": d.get("content_urls", {}).get("desktop", {}).get("page")}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    ids = doc_imdb_id()
    da_lay = set()
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                da_lay.add(json.loads(line)["imdb_id"])
    can_lay = [i for i in ids if i not in da_lay]
    print(f"Phim can tim tren Wikipedia: {len(can_lay)} (da co {len(da_lay)})")
    if not can_lay:
        return

    # Lam tung nhom 50 phim: hoi Wikidata -> lay tom tat -> ghi file ngay.
    # Bi loi giua chung thi phim da ghi van con, chay lai se lam tiep phan con thieu.
    co_vi = co_en = khong_co = bo_qua = 0
    with open(OUT, "a", encoding="utf-8") as out:
        for i in range(0, len(can_lay), 50):
            nhom = can_lay[i:i + 50]
            wd = hoi_wikidata(nhom)
            if wd is None:
                bo_qua += len(nhom)
                print(f"  Bo qua {len(nhom)} phim vi Wikidata loi lien tuc (chay lai sau)")
                continue
            for imdb_id in nhom:
                w = wd.get(imdb_id, {})
                ban, ngon_ngu = None, None
                if w.get("bai_vi"):
                    ban, ngon_ngu = lay_tom_tat("vi", w["bai_vi"]), "vi"
                if ban is None and w.get("bai_en"):
                    ban, ngon_ngu = lay_tom_tat("en", w["bai_en"]), "en"
                if ban is None:
                    ngon_ngu = None
                    khong_co += 1
                elif ngon_ngu == "vi":
                    co_vi += 1
                else:
                    co_en += 1
                out.write(json.dumps({"imdb_id": imdb_id, "wikidata_id": w.get("wikidata_id"),
                                      "ten_vi": w.get("ten_vi"), "ngon_ngu": ngon_ngu,
                                      **(ban or {})}, ensure_ascii=False) + "\n")
                time.sleep(0.1)
            out.flush()
            print(f"  {min(i + 50, len(can_lay))}/{len(can_lay)}  tieng Viet={co_vi}  tieng Anh={co_en}  khong co={khong_co}")
            time.sleep(1)
    if bo_qua:
        print(f"Con {bo_qua} phim chua lay duoc do Wikidata loi -> chay lai lenh nay de lay tiep")
    print(f"Xong. Tom tat tieng Viet: {co_vi}, tieng Anh: {co_en}, khong co bai: {khong_co}")


if __name__ == "__main__":
    main()
