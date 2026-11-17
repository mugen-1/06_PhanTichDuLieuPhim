movies = LOAD 'dataset/sample/movies.tsv' USING PigStorage('\t') AS (
    movie_id:int, imdb_id:chararray, title:chararray, title_vi:chararray, 
    year:int, release_date:chararray, runtime:int, budget:long, revenue:long, 
    box_office_us:long, language:chararray, country:chararray, rated:chararray, 
    tmdb_vote_avg:double, tmdb_vote_count:int, imdb_rating:double, 
    imdb_votes:int, metascore:int, rotten_tomatoes:int
);

-- Lọc bỏ các dòng có chứa N/A hoặc lỗi
movies_clean = FILTER movies BY tmdb_vote_avg IS NOT NULL;

genres = LOAD 'dataset/sample/movie_genres.tsv' USING PigStorage('\t') AS (m_id:int, genre_id:int);

-- JOIN và tính trung bình
joined = JOIN movies_clean BY movie_id, genres BY m_id;
grouped = GROUP joined BY genre_id;
avg_rating = FOREACH grouped GENERATE group AS genre_id, AVG(joined.tmdb_vote_avg) AS avg_score;

STORE avg_rating INTO 'output_pig_avg' USING PigStorage('\t');
