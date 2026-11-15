# Phần Thành viên 2 – Thu thập và đưa dữ liệu vào hệ thống

Chạy mọi lệnh từ thư mục gốc repo `~/06_PhanTichDuLieuPhim`.

| Thứ tự | File | Việc |
|---|---|---|
| 1 | `thu_thap/crawl_tmdb.py` | TMDB API: 1.500 phim nhiều vote nhất → `dataset/raw/tmdb/` |
| 2 | `thu_thap/crawl_omdb.py` | OMDb API: điểm IMDb, Rotten Tomatoes, Metacritic → `dataset/raw/omdb/` |
| 2b | `thu_thap/crawl_wikipedia.py` | Wikidata + Wikipedia: tên và tóm tắt tiếng Việt → `dataset/raw/wikipedia/` |
| 2c | `scrapy_wiki/phim_wiki_spider.py` | Scrapy cào infobox các bài phim trên Wikipedia tiếng Việt → `dataset/raw/wikipedia/vi_phim_scrapy.jsonl` |
| 3 | `lam_sach/lam_sach.py` | Làm sạch, ghép 3 nguồn theo imdb_id → `dataset/clean/` |
| 4 | `mysql/schema_mysql.sql`, `mysql/nap_mysql.sql` | Tạo CSDL `moviedb` (6 bảng) và nạp dữ liệu |
| 5 | `flume/tv2-spool.conf` | Flume spooldir → HDFS `/user/nhom06/movies/raw/flume` |
| 6 | `../mapreduce/tv2_mr1..mr3` | MR lọc bản ghi lỗi, loại trùng imdb_id, chuẩn hóa thể loại |

Dữ liệu thô (`dataset/raw/`) không đưa lên GitHub (đã chặn trong .gitignore).
API key để trong biến môi trường `TMDB_API_KEY`, `OMDB_API_KEY`, không ghi vào code.
