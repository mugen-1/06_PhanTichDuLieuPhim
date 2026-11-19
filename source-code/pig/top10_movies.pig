movies = LOAD 'dataset/clean/movies.tsv' USING PigStorage('\t') AS (
    movie_id:int, imdb_id:chararray, title:chararray, title_vi:chararray, 
    year:int, release_date:chararray, runtime:int, budget:long, revenue:long, 
    box_office_us:long, language:chararray, country:chararray, rated:chararray, 
    tmdb_vote_avg:double, tmdb_vote_count:int, imdb_rating:double, 
    imdb_votes:int, metascore:int, rotten_tomatoes:int
);

-- Bỏ qua những dòng bị lỗi (không có điểm hoặc vote)
valid_movies = FILTER movies BY tmdb_vote_avg IS NOT NULL AND tmdb_vote_count IS NOT NULL;

filtered = FILTER valid_movies BY tmdb_vote_count > 1000;
sorted = ORDER filtered BY tmdb_vote_avg DESC;
top10 = LIMIT sorted 10;
result = FOREACH top10 GENERATE title, tmdb_vote_avg, tmdb_vote_count;

-- Lưu kết quả
STORE result INTO 'output_pig_top10' USING PigStorage('\t');
