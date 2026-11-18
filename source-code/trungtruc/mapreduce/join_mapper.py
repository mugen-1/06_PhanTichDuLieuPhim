#!/usr/bin/env python3
# MapReduce 2 - Join TMDB (movies, 11 cot) voi IMDb ratings (3 cot) theo imdb_id
import sys

for line in sys.stdin:
    f = line.rstrip("\n").split("\t")
    if len(f) == 11 and f[1].startswith("tt"):      # movies: gan nhan M
        print("%s\tM\t%s\t%s\t%s\t%s" % (f[1], f[0], f[2], f[4], f[6]))
    elif len(f) == 3 and f[0].startswith("tt"):     # imdb: gan nhan I
        print("%s\tI\t%s\t%s" % (f[0], f[1], f[2]))
