#!/usr/bin/env python3
# Sinh du lieu MAU (gia) ~100 phim de dung bang va viet MapReduce truoc.
# Khi trunghieu co du lieu that thi thay the, giu dung cot nhu dataset/SCHEMA.txt
import random, os, sys

random.seed(6)
out = sys.argv[1] if len(sys.argv) > 1 else "dataset/sample"
os.makedirs(out, exist_ok=True)

GENRES = ["Action", "Drama", "Comedy", "Thriller", "Romance", "Sci-Fi",
          "Horror", "Animation", "Adventure", "Crime"]
LANGS = ["en"] * 6 + ["fr", "ja", "ko", "vi", "es"]
ADJ = ["Silent", "Last", "Hidden", "Broken", "Golden", "Dark", "Lost", "Final",
       "Secret", "Wild", "Red", "Endless"]
NOUN = ["River", "Empire", "Dream", "City", "Storm", "Garden", "Mission",
        "Memory", "Island", "Planet", "Heart", "Road"]
WORDS = ["a", "young", "detective", "family", "war", "love", "space", "journey",
         "secret", "city", "friend", "survive", "revenge", "music", "school",
         "robot", "ghost", "island", "mission", "dream", "team", "king", "future"]

def overview():
    return " ".join(random.choice(WORDS) for _ in range(random.randint(10, 18))).capitalize() + "."

movies = []
for i in range(100):
    mid = 1001 + i
    year = random.randint(1990, 2024)
    budget = 0 if random.random() < 0.15 else random.randint(1, 200) * 1_000_000
    revenue = 0 if budget == 0 else int(budget * random.uniform(0.3, 4.0))
    movies.append([
        mid, "tt%07d" % (100000 + mid),
        "The %s %s" % (random.choice(ADJ), random.choice(NOUN)) + ("" if i < 60 else " %d" % (i % 3 + 2)),
        "%d-%02d-%02d" % (year, random.randint(1, 12), random.randint(1, 28)), year,
        random.randint(80, 180),
        "|".join(random.sample(GENRES, random.randint(1, 3))),
        random.choice(LANGS), budget, revenue, overview()])

with open(os.path.join(out, "movies_sample.tsv"), "w") as f:
    for m in movies:
        f.write("\t".join(map(str, m)) + "\n")

with open(os.path.join(out, "imdb_ratings_sample.tsv"), "w") as f:
    for m in movies[:90]:  # 10 phim khong co tren IMDb -> kiem tra join
        f.write("%s\t%.1f\t%d\n" % (m[1], random.uniform(3.0, 9.3), random.randint(50, 900000)))
    for k in range(5):     # 5 ma IMDb khong co tren TMDB
        f.write("tt%07d\t%.1f\t%d\n" % (900000 + k, random.uniform(3, 9), random.randint(50, 5000)))

pairs = set()
while len(pairs) < 600:
    pairs.add((random.randint(1, 50), random.choice(movies)[0]))
with open(os.path.join(out, "ratings_sample.tsv"), "w") as f:
    for u, mid in sorted(pairs):
        f.write("%d\t%d\t%.1f\t%d\n" % (u, mid, random.randint(1, 10) / 2,
                                        random.randint(1_500_000_000, 1_730_000_000)))
print("Da tao du lieu mau trong", out)
