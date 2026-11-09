# Đồ án Nhập môn Dữ liệu lớn (BDES333877) – Đề tài phim ảnh

## Cấu trúc thư mục
| Thư mục | Nội dung |
|---|---|
| `source-code/crawler` | Crawler TMDB API, script tải IMDb/MovieLens, làm sạch dữ liệu (Thành viên 2) |
| `source-code/mapreduce` | Các chương trình MapReduce (cả nhóm) |
| `source-code/hive` | Script HQL tạo bảng, truy vấn, CRUD (Trưởng nhóm) |
| `source-code/hbase` | Script/code HBase (Trưởng nhóm) |
| `source-code/pig` | Script Pig (Thành viên 3) |
| `source-code/spark` | Code Spark (Thành viên 3) |
| `source-code/gui` | Web GUI (Trưởng nhóm) |
| `source-code/backup` | Script sao lưu/phục hồi |
| `dataset/` | Dữ liệu dùng trong chương trình (file lớn hơn 100MB không commit, xem `dataset/README.md`) |
| `reports/` | Báo cáo (.docx, .pdf), slides, bảng tự chấm, bảng phân công, video |
| `refs/` | Tài liệu tham khảo |
| `libs/` | Danh sách phần mềm, thư viện, phiên bản (`versions.txt`) |

## Quy tắc làm việc
1. Mỗi người commit bằng **tài khoản GitHub của chính mình**.
2. Trước khi làm: `git pull`. Làm xong: `git add` → `git commit -m "..."` → `git pull --rebase` → `git push`.
3. Chỉ sửa trong thư mục phần mình phụ trách để tránh conflict.
4. Không commit API key: để trong file `.env` (đã có trong `.gitignore`).
