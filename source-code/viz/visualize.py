import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("reports/figures", exist_ok=True)

movies = pd.read_csv("dataset/clean/movies.tsv", sep="\t")
genres = pd.read_csv("dataset/clean/movie_genres.tsv", sep="\t")

movies = movies.rename(columns={'movie_id': 'id', 'tmdb_vote_avg': 'rating', 'tmdb_vote_count': 'votes'})
genres = genres.rename(columns={'movie_id': 'id', 'genre_id': 'genre'})
# Doi genre_id sang ten the loai
ten_tl = pd.read_csv("dataset/clean/genres.tsv", sep="\t")
genres['genre'] = genres['genre'].map(dict(zip(ten_tl.genre_id, ten_tl.genre_name)))

# 1. Bar: Số phim theo thể loại
plt.figure(figsize=(10, 6))
genre_counts = genres['genre'].value_counts().head(10)
sns.barplot(x=genre_counts.index, y=genre_counts.values, palette="viridis")
plt.title("Số lượng phim theo thể loại (Top 10)")
plt.xlabel("Thể loại"); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
plt.ylabel("Số lượng phim")
plt.savefig("reports/figures/1_bar_genre.png")
plt.close()

# 2. Line: Số phim theo năm
plt.figure(figsize=(10, 6))
year_counts = movies['year'].value_counts().sort_index()
plt.plot(year_counts.index, year_counts.values, marker='o', color='b')
plt.title("Số lượng phim theo năm phát hành")
plt.xlabel("Năm")
plt.ylabel("Số lượng phim")
plt.savefig("reports/figures/2_line_year.png")
plt.close()

# 3. Pie: Tỷ lệ ngôn ngữ
plt.figure(figsize=(8, 8))
lang_counts = movies['language'].value_counts().head(5)
plt.pie(lang_counts.values, labels=lang_counts.index, autopct='%1.1f%%', startangle=140)
plt.title("Tỷ lệ ngôn ngữ phim (Top 5)")
plt.savefig("reports/figures/3_pie_language.png")
plt.close()

# 4. Scatter: Budget vs Revenue
plt.figure(figsize=(10, 6))
plt.scatter(movies['budget'], movies['revenue'], alpha=0.5, color='r')
plt.title("Mối quan hệ giữa Ngân sách và Doanh thu")
plt.xlabel("Ngân sách")
plt.ylabel("Doanh thu")
plt.savefig("reports/figures/4_scatter_budget.png")
plt.close()

# 5. Heatmap: Thể loại x Thập niên
movies['decade'] = (movies['year'] // 10) * 10
merged = pd.merge(movies[['id', 'decade']], genres, on='id')
pivot = merged.groupby(['genre', 'decade']).size().unstack(fill_value=0)
plt.figure(figsize=(12, 8))
sns.heatmap(pivot, cmap="YlGnBu", annot=False)
plt.title("Phân bố thể loại theo thập niên")
plt.xlabel("Thập niên")
plt.ylabel("Thể loại")
plt.savefig("reports/figures/5_heatmap_genre_decade.png")
plt.close()

print("Đã vẽ xong 5 biểu đồ vào thư mục reports/figures/")
