#!/usr/bin/env python3
# MapReduce 1 - Inverted index: tu khoa -> danh sach movie_id
# Doc movies TSV: cot 0 = movie_id, cot 2 = title, cot 10 = overview
import sys, re

STOP = {"a", "an", "the", "of", "and", "or", "to", "in", "on", "at", "for",
        "with", "is", "are", "his", "her", "their", "from", "by", "as", "into"}

for line in sys.stdin:
    f = line.rstrip("\n").split("\t")
    if len(f) < 11 or not f[0].isdigit():
        continue
    for w in set(re.findall(r"\w+", (f[2] + " " + f[10]).lower())):
        if len(w) > 1 and w not in STOP and not w.isdigit():
            print("%s\t%s" % (w, f[0]))
