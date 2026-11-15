-- Nap cac file TSV da lam sach vao MySQL (bang cha truoc, bang con sau).
-- Chay tu thu muc goc repo:  mysql --local-infile=1 -u tv2 -p moviedb < source-code/crawler/mysql/nap_mysql.sql
-- (\N trong file duoc MySQL hieu la NULL; IGNORE 1 LINES = bo dong tieu de)
SET NAMES utf8mb4;
LOAD DATA LOCAL INFILE 'dataset/clean/movies.tsv'       INTO TABLE movies       CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'dataset/clean/genres.tsv'       INTO TABLE genres       CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'dataset/clean/movie_genres.tsv' INTO TABLE movie_genres CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'dataset/clean/people.tsv'       INTO TABLE people       CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'dataset/clean/movie_people.tsv' INTO TABLE movie_people CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'dataset/clean/reviews.tsv'      INTO TABLE reviews      CHARACTER SET utf8mb4 FIELDS TERMINATED BY '\t' IGNORE 1 LINES;
SHOW WARNINGS LIMIT 10;
