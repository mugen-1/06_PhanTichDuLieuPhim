SET hive.auto.convert.join=false;
USE phim_db;

-- 1. So phim theo nam (dung partition)
SELECT release_year, COUNT(*) AS so_phim FROM movies GROUP BY release_year ORDER BY release_year;

-- 2. Loc theo the loai va nam (partition pruning: chi doc thu muc nam 2010-2020)
SELECT movie_id, title, release_year FROM movies
WHERE release_year BETWEEN 2010 AND 2020 AND array_contains(genres, 'Action')
ORDER BY release_year LIMIT 20;

-- 3. Bang xep hang theo diem nguoi dung (it nhat 3 luot danh gia)
SELECT m.movie_id, m.title, ROUND(AVG(r.rating), 2) AS diem_tb, COUNT(*) AS so_luot
FROM ratings r JOIN movies m ON r.movie_id = m.movie_id
GROUP BY m.movie_id, m.title
HAVING COUNT(*) >= 3
ORDER BY diem_tb DESC, so_luot DESC LIMIT 10;

-- 4. Ket hop TMDB va IMDb theo imdb_id
SELECT m.title, m.release_year, i.average_rating, i.num_votes
FROM movies m JOIN imdb_ratings_raw i ON m.imdb_id = i.imdb_id
WHERE i.num_votes >= 1000
ORDER BY i.average_rating DESC LIMIT 10;
