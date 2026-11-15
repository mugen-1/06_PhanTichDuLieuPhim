#!/usr/bin/env python3
# Lam sach va ghep du lieu phim tu 3 nguon: TMDB, OMDb, Wikipedia -> dataset/clean/
# Khoa noi 3 nguon: imdb_id (TMDB co san truong nay, OMDb va Wikipedia tra cuu theo no).
# Khong sua file raw. Moi buoc ghi so dong truoc/sau vao bao_cao_lam_sach.txt.

import json
import os
import re

import pandas as pd

RAW = "dataset/raw"
CLEAN = "dataset/clean"
NULL = "\\N"            # MySQL LOAD DATA, Sqoop, Hive deu hieu \N la NULL

# OMDb dung ten the loai khac TMDB -> dua ve ten cua TMDB
# (chi doi ten khi cung nghia; the loai TMDB khong co nhu Biography, Sport thi giu nguyen)
DOI_TEN_THE_LOAI = {"Sci-Fi": "Science Fiction", "Musical": "Music", "Film-Noir": "Film Noir",
                    "Short": None, "N/A": None}

nhat_ky = []


def ghi(msg):
    print(msg)
    nhat_ky.append(msg)


def lam_gon(s):
    # Bo tab / xuong dong trong chuoi vi file ra dung tab lam dau phan cach
    if not isinstance(s, str):
        return s
    return re.sub(r"\s+", " ", s).strip()


def so_tu_chuoi(s):
    # "1,234,567" -> 1234567 ; "$28,767,189" -> 28767189 ; "142 min" -> 142 ; "N/A" -> None
    if not isinstance(s, str) or s.strip() in ("", "N/A"):
        return None
    chu_so = re.sub(r"[^\d.]", "", s.split(" ")[0] if "min" in s else s)
    return float(chu_so) if chu_so else None


def doc_jsonl(duong_dan):
    with open(duong_dan, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ------------------------------------------------------------------ 1. TMDB
def lam_sach_tmdb():
    with open(f"{RAW}/tmdb/danh_sach_tmdb.txt", encoding="utf-8") as f:
        ds = [int(x) for x in f if x.strip()]
    rows = [r for r in doc_jsonl(f"{RAW}/tmdb/tmdb_movies.jsonl") if r["id"] in set(ds)]
    ghi(f"[tmdb] Danh sach: {len(ds)} phim, doc duoc chi tiet: {len(rows)} phim")

    t = pd.DataFrame(rows).drop_duplicates("id")
    t["imdb_id"] = t["imdb_id"].where(t["imdb_id"].fillna("").str.match(r"^tt\d+$"))
    ghi(f"[tmdb] Thieu imdb_id (khong noi duoc voi 2 nguon kia): {t['imdb_id'].isna().sum()} -> loai")
    t = t[t["imdb_id"].notna()]
    truoc = len(t)
    t = t.sort_values("vote_count", ascending=False).drop_duplicates("imdb_id")
    ghi(f"[tmdb] Trung imdb_id: {truoc - len(t)} -> giu ban nhieu vote nhat")

    t["release_date"] = pd.to_datetime(t["release_date"], errors="coerce")
    ghi(f"[tmdb] release_date rong/sai: {t['release_date'].isna().sum()}")
    for cot in ["runtime", "budget", "revenue"]:
        t[cot] = pd.to_numeric(t[cot], errors="coerce")
        so_0 = int((t[cot] == 0).sum())
        t.loc[t[cot] == 0, cot] = pd.NA          # 0 nghia la TMDB chua co so lieu
        ghi(f"[tmdb] {cot} = 0 -> NULL: {so_0}")
    t.loc[t["vote_count"] == 0, "vote_average"] = pd.NA
    t = t.rename(columns={"id": "movie_id"})
    return t


# ------------------------------------------------------------------ 2. OMDb
def lam_sach_omdb():
    rows = doc_jsonl(f"{RAW}/omdb/omdb_movies.jsonl")
    o = pd.DataFrame(rows).drop_duplicates("imdbID")
    ghi(f"[omdb] Doc {len(rows)} ban ghi, sau bo trung: {len(o)}")
    so_na = {c: int((o[c] == "N/A").sum()) for c in ["imdbRating", "Metascore", "BoxOffice", "Awards"]}
    ghi(f"[omdb] So o ghi 'N/A' (-> NULL): {so_na}")

    def diem_rt(ds):
        # Ratings = [{"Source": "Rotten Tomatoes", "Value": "93%"}, ...]
        for x in ds or []:
            if x.get("Source") == "Rotten Tomatoes":
                return so_tu_chuoi(x.get("Value"))
        return None

    ket_qua = pd.DataFrame({
        "imdb_id": o["imdbID"],
        "imdb_rating": o["imdbRating"].map(so_tu_chuoi),
        "imdb_votes": o["imdbVotes"].map(so_tu_chuoi),
        "metascore": o["Metascore"].map(so_tu_chuoi),
        "rotten_tomatoes": o["Ratings"].map(diem_rt),
        "box_office_us": o["BoxOffice"].map(so_tu_chuoi),
        "omdb_runtime": o["Runtime"].map(so_tu_chuoi),
        "omdb_year": pd.to_numeric(o["Year"].str[:4], errors="coerce"),
        "rated": o["Rated"].where(~o["Rated"].isin(["N/A", "Not Rated", "Unrated"])),
        "country": o["Country"].where(o["Country"] != "N/A").str.split(",").str[0].str.strip(),
        "awards": o["Awards"].where(o["Awards"] != "N/A"),
        "omdb_genre": o["Genre"],
    })
    ghi(f"[omdb] Co diem Rotten Tomatoes: {ket_qua['rotten_tomatoes'].notna().sum()}, "
        f"co Metascore: {ket_qua['metascore'].notna().sum()}, co BoxOffice: {ket_qua['box_office_us'].notna().sum()}")
    return ket_qua


# ------------------------------------------------------------------ 3. Wikipedia
def lam_sach_wiki():
    rows = doc_jsonl(f"{RAW}/wikipedia/wiki_movies.jsonl")
    w = pd.DataFrame(rows).drop_duplicates("imdb_id")
    ghi(f"[wiki] Doc {len(w)} phim: tieng Viet {int((w['ngon_ngu'] == 'vi').sum())}, "
        f"tieng Anh {int((w['ngon_ngu'] == 'en').sum())}, khong co bai {int(w['ngon_ngu'].isna().sum())}")
    w["tom_tat"] = w.get("tom_tat").map(lam_gon) if "tom_tat" in w else None
    # Ten tieng Viet: uu tien nhan tieng Viet tren Wikidata, khong co thi lay tieu de bai tieng Viet
    w["title_vi"] = w["ten_vi"].where(w["ten_vi"].notna(), w["tieu_de"].where(w["ngon_ngu"] == "vi"))
    return w


# ------------------------------------------------------------------ 4. Scrapy (bai Wikipedia tieng Viet)
def tien_vi(s):
    # "237 triệu USD" -> 237000000 ; "2,923 tỷ USD" -> 2923000000 (tieng Viet dung dau phay thap phan)
    if not isinstance(s, str):
        return None
    m = re.search(r"([\d.,]+)\s*(triệu|tỷ)\s*(USD|đô)", s)
    if not m:
        return None
    so = float(m.group(1).replace(".", "").replace(",", "."))
    return int(so * (1e6 if m.group(2) == "triệu" else 1e9))


def doc_scrapy():
    duong_dan = f"{RAW}/wikipedia/vi_phim_scrapy.jsonl"
    if not os.path.exists(duong_dan):
        ghi("[scrapy] Chua co file vi_phim_scrapy.jsonl -> bo qua")
        return {}
    rows = [r for r in doc_jsonl(duong_dan) if r.get("wikidata_id")]
    for r in rows:
        r["kinh_phi_usd"] = tien_vi(r.get("kinh_phi"))
        r["doanh_thu_usd"] = tien_vi(r.get("doanh_thu"))
    ghi(f"[scrapy] {len(rows)} bai phim tieng Viet, doi duoc kinh phi ra so: "
        f"{sum(1 for r in rows if r['kinh_phi_usd'])}, doanh thu: {sum(1 for r in rows if r['doanh_thu_usd'])}")
    return {r["wikidata_id"]: r for r in rows}


def ghi_tsv(df, ten):
    df.to_csv(f"{CLEAN}/{ten}", sep="\t", index=False, na_rep=NULL)
    ghi(f"  -> {ten}: {len(df)} dong")


def main():
    os.makedirs(CLEAN, exist_ok=True)
    t = lam_sach_tmdb()
    o = lam_sach_omdb()
    w = lam_sach_wiki()

    df = t.merge(o, on="imdb_id", how="left").merge(w[["imdb_id", "title_vi"]], on="imdb_id", how="left")
    ghi(f"[ghep] Tong {len(df)} phim | co OMDb: {df['imdb_rating'].notna().sum()} | co ten tieng Viet: {df['title_vi'].notna().sum()}")

    # Thoi luong: TMDB va OMDb lech nhau qua 10 phut thi dem lai de bao cao, uu tien TMDB
    lech = ((df["runtime"] - df["omdb_runtime"]).abs() > 10).sum()
    ghi(f"[ghep] Thoi luong TMDB va OMDb lech > 10 phut: {lech} phim (giu so cua TMDB)")
    df["runtime"] = df["runtime"].fillna(df["omdb_runtime"])

    df["year"] = df["release_date"].dt.year.astype("Int64")
    df["year"] = df["year"].fillna(df["omdb_year"].astype("Int64"))      # TMDB thieu ngay -> lay nam cua OMDb
    df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")
    df["title"] = df["title"].map(lam_gon)
    df["title_vi"] = df["title_vi"].map(lam_gon)
    df = df.rename(columns={"original_language": "language", "vote_average": "tmdb_vote_avg",
                            "vote_count": "tmdb_vote_count"})
    for cot in ["runtime", "budget", "revenue", "tmdb_vote_count", "imdb_votes", "metascore",
                "rotten_tomatoes", "box_office_us"]:
        df[cot] = pd.to_numeric(df[cot], errors="coerce").round().astype("Int64")
    movies = df[["movie_id", "imdb_id", "title", "title_vi", "year", "release_date", "runtime",
                 "budget", "revenue", "box_office_us", "language", "country", "rated",
                 "tmdb_vote_avg", "tmdb_vote_count", "imdb_rating", "imdb_votes",
                 "metascore", "rotten_tomatoes"]]

    # The loai: lay tu TMDB, phim nao TMDB de trong thi lay tu OMDb (doi ten cho thong nhat)
    cap, bu_omdb = [], 0
    for _, r in df.iterrows():
        ds = list(r["genres"])
        if not ds and isinstance(r["omdb_genre"], str):
            ds = [DOI_TEN_THE_LOAI.get(g.strip(), g.strip()) for g in r["omdb_genre"].split(",")]
            ds = [g for g in ds if g]
            bu_omdb += 1 if ds else 0
        for g in dict.fromkeys(ds):
            cap.append((r["movie_id"], g))
    genres = pd.DataFrame(sorted({g for _, g in cap}), columns=["genre_name"])
    genres.insert(0, "genre_id", range(1, len(genres) + 1))
    gid = dict(zip(genres["genre_name"], genres["genre_id"]))
    movie_genres = pd.DataFrame([(m, gid[g]) for m, g in cap], columns=["movie_id", "genre_id"])
    ghi(f"[the loai] {len(genres)} the loai, {len(movie_genres)} cap phim-the loai, bu tu OMDb: {bu_omdb} phim")

    # Nguoi: 5 dien vien dau + dao dien (TMDB)
    people, mp = {}, {}
    for _, r in df.iterrows():
        for c in r["cast"][:5]:
            people[c["id"]] = lam_gon(c["name"])
            mp.setdefault((r["movie_id"], c["id"], "cast"), c.get("order"))
        for d in r["directors"]:
            people[d["id"]] = lam_gon(d["name"])
            mp.setdefault((r["movie_id"], d["id"], "director"), None)
    people_df = pd.DataFrame(sorted(people.items()), columns=["person_id", "name"])
    mp_df = pd.DataFrame([(m, p, vt, tt) for (m, p, vt), tt in sorted(mp.items())],
                         columns=["movie_id", "person_id", "role", "cast_order"])
    mp_df["cast_order"] = mp_df["cast_order"].astype("Int64")

    # Review: phan diem dua vao MySQL, noi dung dai dua vao MongoDB
    rv = []
    for _, r in df.iterrows():
        for x in r["reviews"]:
            rv.append({"movie_id": r["movie_id"], "author": lam_gon(x.get("author")),
                       "rating": x.get("rating"), "created_at": x.get("created_at"),
                       "content": x.get("content")})
    rv = pd.DataFrame(rv, columns=["movie_id", "author", "rating", "created_at", "content"])
    truoc = len(rv)
    rv = rv.drop_duplicates(["movie_id", "author", "created_at"])
    rv["rating"] = pd.to_numeric(rv["rating"], errors="coerce")
    rv.loc[~rv["rating"].between(0, 10), "rating"] = pd.NA
    rv["created_at"] = pd.to_datetime(rv["created_at"], errors="coerce", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    rv.insert(0, "review_id", range(1, len(rv) + 1))
    ghi(f"[review] {truoc} -> {len(rv)} (bo trung {truoc - len(rv)}), co diem: {rv['rating'].notna().sum()}")

    ghi("[ghi file] dataset/clean/")
    ghi_tsv(movies, "movies.tsv")
    ghi_tsv(genres, "genres.tsv")
    ghi_tsv(movie_genres, "movie_genres.tsv")
    ghi_tsv(people_df, "people.tsv")
    ghi_tsv(mp_df, "movie_people.tsv")
    ghi_tsv(rv[["review_id", "movie_id", "author", "rating", "created_at"]], "reviews.tsv")

    # Van ban dai -> JSON lines cho MongoDB
    wmap = w.set_index("imdb_id").to_dict("index")
    scr = doc_scrapy()
    khop = lech = 0
    for _, r in df.iterrows():
        x = scr.get((wmap.get(r["imdb_id"]) or {}).get("wikidata_id"))
        if x:
            khop += 1
            if x["doanh_thu_usd"] and pd.notna(r["revenue"]) and abs(x["doanh_thu_usd"] - r["revenue"]) > 0.05 * r["revenue"]:
                lech += 1
    if scr:
        ghi(f"[scrapy] Noi duoc voi {khop}/{len(scr)} bai (qua ma Wikidata); doanh thu Wikipedia lech TMDB > 5%: {lech} phim")
    with open(f"{CLEAN}/movie_texts.jsonl", "w", encoding="utf-8") as f:
        for _, r in df.iterrows():
            x = wmap.get(r["imdb_id"], {})
            f.write(json.dumps({"movie_id": int(r["movie_id"]), "imdb_id": r["imdb_id"], "title": r["title"],
                                "title_vi": r["title_vi"] if isinstance(r["title_vi"], str) else None,
                                "overview_tmdb": r["overview"] or None,
                                "wiki_ngon_ngu": x.get("ngon_ngu"), "wiki_tom_tat": x.get("tom_tat"),
                                "wiki_url": x.get("url"),
                                "awards": r["awards"] if isinstance(r["awards"], str) else None,
                                "wiki_vi_infobox": {k: v for k, v in (scr.get(x.get("wikidata_id")) or {}).items()
                                                    if k not in ("url", "wikidata_id")} or None},
                               ensure_ascii=False) + "\n")
    with open(f"{CLEAN}/reviews.jsonl", "w", encoding="utf-8") as f:
        for _, r in rv.iterrows():
            f.write(json.dumps({"review_id": int(r["review_id"]), "movie_id": int(r["movie_id"]),
                                "author": r["author"], "content": r["content"]}, ensure_ascii=False) + "\n")
    ghi(f"  -> movie_texts.jsonl: {len(df)} dong, reviews.jsonl: {len(rv)} dong")

    with open(f"{CLEAN}/bao_cao_lam_sach.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(nhat_ky) + "\n")


if __name__ == "__main__":
    main()
