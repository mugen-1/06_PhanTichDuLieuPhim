# Đồ án Nhập môn Dữ liệu lớn (BDES333877) – Nhóm 06 – Phân tích dữ liệu phim ảnh

## Cấu trúc thư mục
| Thư mục | Nội dung | Người làm |
|---|---|---|
| `source-code/crawler` | Thu thập TMDB, OMDb, Wikipedia, Scrapy; làm sạch; MySQL; Flume; sổ tay lệnh | trunghieu |
| `source-code/mapreduce/tv2_*` | 3 MapReduce: lọc lỗi OMDb, loại trùng imdb_id, chuẩn hóa thể loại | trunghieu |
| `source-code/pig`, `spark`, `viz` | Pig, Spark, trực quan hóa | ngocnhan |
| `source-code/tv3` | 3 MapReduce: đếm phim theo thể loại, top-N, điểm TB theo thể loại | ngocnhan |
| `source-code/trungtruc` | Hive, HBase, CRUD, 2 MapReduce, sao lưu/phục hồi, web, Kafka, chuyển đổi dữ liệu | trungtruc |
| `dataset/clean` | Dữ liệu sạch 1.500 phim (3 nguồn) | trunghieu |
| `dataset/chuyen_doi` | Dữ liệu theo `dataset/SCHEMA.txt` cho Hive/HBase/web | trungtruc |
| `dataset/sample` | Mẫu nhỏ để thử | cả nhóm |
| `reports/` | Báo cáo, slides, bảng tự chấm, bảng phân công, ảnh chụp, biểu đồ | cả nhóm |
| `refs/`, `libs/` | Tài liệu tham khảo, phiên bản phần mềm (`libs/versions.txt`) | cả nhóm |

## Quy tắc làm việc
1. Mỗi người commit bằng **tài khoản GitHub của chính mình**.
2. Trước khi làm: `git pull`. Làm xong: `git add` → `git commit -m "..."` → `git pull --rebase` → `git push`.
3. Chỉ sửa trong thư mục phần mình phụ trách để tránh conflict.
4. Không commit API key: để trong file `.env` (đã có trong `.gitignore`).
