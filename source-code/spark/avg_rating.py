from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count

spark = SparkSession.builder.appName("AvgRatingByGenre").getOrCreate()

# THÊM file:// VÀO TRƯỚC ĐƯỜNG DẪN ĐỂ ĐỌC TRÊN Ổ CỨNG MÁY ẢO
movies_df = spark.read.option("sep", "\t").option("header", "true").csv("file:///home/nhom06/06_PhanTichDuLieuPhim/dataset/clean/movies.tsv")
genres_df = spark.read.option("sep", "\t").option("header", "true").csv("file:///home/nhom06/06_PhanTichDuLieuPhim/dataset/clean/movie_genres.tsv")

# Ép kiểu và lọc bỏ dòng lỗi
movies_clean = movies_df.select(
    col("movie_id").cast("int"),
    col("tmdb_vote_avg").cast("double")
).filter(col("tmdb_vote_avg").isNotNull())

genres_clean = genres_df.select(
    col("movie_id").cast("int"),
    col("genre_id").cast("int")
)

# JOIN
joined = movies_clean.join(genres_clean, on="movie_id", how="inner")

# Tính trung bình
result = joined.groupBy("genre_id").agg(
    avg("tmdb_vote_avg").alias("avg_score"),
    count("movie_id").alias("movie_count")
).orderBy("genre_id")

result.show()

# Lưu kết quả (cũng dùng file://)
result.coalesce(1).write.csv("file:///home/nhom06/06_PhanTichDuLieuPhim/output_spark_avg", header=True, mode="overwrite")

spark.stop()
