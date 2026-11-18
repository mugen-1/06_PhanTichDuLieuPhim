-- CRUD tren Hive (bang ORC thuong): them bang INSERT INTO,
-- sua/xoa bang cach ghi de lai DUNG 1 partition (INSERT OVERWRITE).
USE phim_db;

-- CREATE: them 1 phim vao partition 2025
INSERT INTO TABLE movies PARTITION (release_year = 2025)
SELECT 999001, 'tt9999001', 'Phim Demo CRUD', '2025-01-01', 120, array('Drama'),
       'vi', CAST(NULL AS BIGINT), CAST(NULL AS BIGINT), 'Phim them de demo CRUD';

-- READ
SELECT movie_id, title, genres FROM movies WHERE release_year = 2025 AND movie_id = 999001;

-- UPDATE: doi ten phim 999001
INSERT OVERWRITE TABLE movies PARTITION (release_year = 2025)
SELECT movie_id, imdb_id,
       CASE WHEN movie_id = 999001 THEN 'Phim Demo CRUD (da sua)' ELSE title END,
       release_date, runtime, genres, original_language, budget, revenue, overview
FROM movies WHERE release_year = 2025;
SELECT movie_id, title FROM movies WHERE release_year = 2025;

-- DELETE: xoa phim 999001
INSERT OVERWRITE TABLE movies PARTITION (release_year = 2025)
SELECT movie_id, imdb_id, title, release_date, runtime, genres, original_language,
       budget, revenue, overview
FROM movies WHERE release_year = 2025 AND movie_id <> 999001;
SELECT COUNT(*) AS con_lai_2025 FROM movies WHERE release_year = 2025;
