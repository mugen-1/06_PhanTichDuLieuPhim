#!/usr/bin/env python3
# Gom movie_id theo tu khoa. Ket qua: tu<TAB>id1,id2,...
import sys

cur, ids = None, set()

def xuat():
    if cur is not None:
        print("%s\t%s" % (cur, ",".join(sorted(ids, key=int))))

for line in sys.stdin:
    w, mid = line.rstrip("\n").split("\t", 1)
    if w != cur:
        xuat()
        cur, ids = w, set()
    ids.add(mid)
xuat()
