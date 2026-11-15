#!/usr/bin/env python3
# MR2 - Reduce: cac dong cung imdb_id den lien nhau (Hadoop da sort theo key).
# Giu 1 ban ghi co vote_count lon nhat, dem so ban ghi bi loai.
import sys

key_cu, tot_nhat, so_dong = None, None, 0


def xuat():
    if key_cu is None:
        return
    if so_dong > 1:
        sys.stderr.write(f"reporter:counter:MR2_LoaiTrung,BanGhiTrungBiLoai,{so_dong - 1}\n")
    sys.stderr.write("reporter:counter:MR2_LoaiTrung,PhimSauLoaiTrung,1\n")
    print(f"{key_cu}\t" + "\t".join(tot_nhat))


for line in sys.stdin:
    imdb, tmdb_id, votes, title = line.rstrip("\n").split("\t", 3)
    if imdb != key_cu:
        xuat()
        key_cu, tot_nhat, so_dong = imdb, (tmdb_id, votes, title), 0
    elif int(votes) > int(tot_nhat[1]):
        tot_nhat = (tmdb_id, votes, title)
    so_dong += 1
xuat()
