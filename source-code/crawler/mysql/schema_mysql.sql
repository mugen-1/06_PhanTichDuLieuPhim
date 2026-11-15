-- CSDL quan he cho du lieu phim (Thanh vien 2) - 3 nguon TMDB, OMDb, Wikipedia
-- Chay: sudo mysql < source-code/crawler/mysql/schema_mysql.sql
CREATE DATABASE IF NOT EXISTS moviedb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE moviedb;

DROP TABLE IF EXISTS reviews, movie_people, movie_genres, people, genres, movies;

CREATE TABLE movies (
  movie_id        INT PRIMARY KEY,          -- id phim tren TMDB
  imdb_id         VARCHAR(12) NOT NULL UNIQUE,
  title           VARCHAR(300) NOT NULL,
  title_vi        VARCHAR(300) NULL,        -- ten tieng Viet (Wikipedia/Wikidata)
  year            SMALLINT NULL,
  release_date    DATE NULL,
  runtime         SMALLINT NULL,            -- phut
  budget          BIGINT NULL,              -- USD (TMDB), NULL = chua co so lieu
  revenue         BIGINT NULL,              -- USD toan cau (TMDB)
  box_office_us   BIGINT NULL,              -- USD tai My (OMDb)
  language        VARCHAR(10) NULL,
  country         VARCHAR(60) NULL,         -- quoc gia dau tien (OMDb)
  rated           VARCHAR(15) NULL,         -- phan loai do tuoi: PG-13, R... (OMDb)
  tmdb_vote_avg   DECIMAL(4,2) NULL,
  tmdb_vote_count INT NULL,
  imdb_rating     DECIMAL(3,1) NULL,        -- OMDb
  imdb_votes      INT NULL,                 -- OMDb
  metascore       TINYINT NULL,             -- Metacritic 0-100 (OMDb)
  rotten_tomatoes TINYINT NULL              -- % Rotten Tomatoes (OMDb)
);

CREATE TABLE genres (
  genre_id   INT PRIMARY KEY,
  genre_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE movie_genres (
  movie_id INT,
  genre_id INT,
  PRIMARY KEY (movie_id, genre_id),
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id),
  FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE people (
  person_id INT PRIMARY KEY,                -- id nguoi tren TMDB
  name      VARCHAR(200) NOT NULL
);

CREATE TABLE movie_people (
  movie_id   INT,
  person_id  INT,
  role       VARCHAR(10),                   -- 'cast' hoac 'director'
  cast_order SMALLINT NULL,
  PRIMARY KEY (movie_id, person_id, role),
  FOREIGN KEY (movie_id)  REFERENCES movies(movie_id),
  FOREIGN KEY (person_id) REFERENCES people(person_id)
);

CREATE TABLE reviews (
  review_id  INT PRIMARY KEY,
  movie_id   INT NOT NULL,
  author     VARCHAR(200) NULL,
  rating     DECIMAL(3,1) NULL,             -- diem nguoi viet review cho (0-10), co the trong
  created_at DATETIME NULL,
  FOREIGN KEY (movie_id) REFERENCES movies(movie_id)
);
