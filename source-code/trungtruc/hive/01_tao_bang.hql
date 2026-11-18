-- Tao CSDL, bang tho (doc thang file TSV tren HDFS) va bang chinh partition theo nam
CREATE DATABASE IF NOT EXISTS phim_db;
USE phim_db;

CREATE EXTERNAL TABLE IF NOT EXISTS movies_raw (
  movie_id INT, imdb_id STRING, title STRING, release_date STRING, release_year INT,
  runtime INT, genres STRING, original_language STRING, budget BIGINT, revenue BIGINT,
  overview STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE
LOCATION '/user/nhom06/movies/raw/movies';

CREATE EXTERNAL TABLE IF NOT EXISTS imdb_ratings_raw (
  imdb_id STRING, average_rating DOUBLE, num_votes INT)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE
LOCATION '/user/nhom06/movies/raw/imdb';

CREATE EXTERNAL TABLE IF NOT EXISTS ratings_raw (
  user_id INT, movie_id INT, rating DOUBLE, ts BIGINT)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE
LOCATION '/user/nhom06/movies/raw/ratings';

-- Bang chinh: partition theo nam phat hanh, the loai la mang
CREATE TABLE IF NOT EXISTS movies (
  movie_id INT, imdb_id STRING, title STRING, release_date STRING, runtime INT,
  genres ARRAY<STRING>, original_language STRING, budget BIGINT, revenue BIGINT,
  overview STRING)
PARTITIONED BY (release_year INT)
STORED AS ORC;

CREATE TABLE IF NOT EXISTS ratings (
  user_id INT, movie_id INT, rating DOUBLE, ts BIGINT)
STORED AS ORC;

SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

INSERT OVERWRITE TABLE movies PARTITION (release_year)
SELECT movie_id, imdb_id, title, release_date, runtime, split(genres, '\\|'),
       original_language,
       CASE WHEN budget = 0 THEN NULL ELSE budget END,
       CASE WHEN revenue = 0 THEN NULL ELSE revenue END,
       overview, release_year
FROM movies_raw
WHERE movie_id IS NOT NULL AND release_year IS NOT NULL;

INSERT OVERWRITE TABLE ratings
SELECT user_id, movie_id, rating, ts FROM ratings_raw WHERE movie_id IS NOT NULL;

SHOW PARTITIONS movies;
SELECT COUNT(*) AS so_phim FROM movies;
SELECT COUNT(*) AS so_danh_gia FROM ratings;
