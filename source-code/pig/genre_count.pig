-- Script Pig: Đếm số lượng phim theo thể loại
movies = LOAD '/user/nhom06/movies_data/movie_genres.tsv' USING PigStorage('\t') AS (movie_id:int, genre_id:int);
grouped = GROUP movies BY genre_id;
genre_count = FOREACH grouped GENERATE group AS genre_id, COUNT(movies) AS movie_count;
STORE genre_count INTO '/user/nhom06/output_pig_genre' USING PigStorage('\t');
