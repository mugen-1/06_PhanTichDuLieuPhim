#!/usr/bin/env python3
# GUI web phim - Flask + HBase (qua Thrift, cong 9090) + Hive (tuy chon, cong 10000)
# Chay: source ~/venv_web/bin/activate && python3 app.py  -> mo http://localhost:5000
import re
import happybase
from flask import Flask, request, redirect, url_for, render_template_string, abort

app = Flask(__name__)
COLS = ["imdb_id", "title", "release_date", "release_year", "runtime", "genres",
        "language", "budget", "revenue", "overview"]
GENRES = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Drama",
          "Horror", "Romance", "Sci-Fi", "Thriller"]


def ket_noi():
    return happybase.Connection("localhost", 9090)


def doc_phim(key, data):
    p = {c: data.get(("info:" + c).encode(), b"").decode() for c in COLS}
    p["movie_id"] = key.decode() if isinstance(key, bytes) else key
    return p


def tim_theo_index(conn, q):
    """Dung bang search_index (ket qua MapReduce inverted index): giao cac tap id."""
    tap = None
    for w in re.findall(r"\w+", q.lower()):
        row = conn.table("search_index").row(w.encode())
        ids = set(row.get(b"i:ids", b"").decode().split(",")) - {""}
        tap = ids if tap is None else tap & ids
    return tap or set()


BASE = """<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>Phim - Nhom 06</title><style>
body{font-family:system-ui,sans-serif;max-width:960px;margin:24px auto;padding:0 16px;color:#222}
a{color:#0b57d0;text-decoration:none} nav a{margin-right:16px;font-weight:600}
table{border-collapse:collapse;width:100%;margin-top:12px} td,th{border-bottom:1px solid #ddd;padding:6px;text-align:left}
input,select,textarea{padding:6px;margin:2px 0} .note{color:#666;font-size:14px}
</style></head><body>
<nav><a href="/">Tìm phim</a><a href="/ranking">Bảng xếp hạng</a><a href="/add">+ Thêm phim</a></nav>
{% block body %}{% endblock %}</body></html>"""

HOME = BASE.replace("{% block body %}{% endblock %}", """
<h2>Tìm phim</h2>
<form>
 <input name="q" value="{{q}}" placeholder="Từ khóa tên/nội dung">
 <select name="genre"><option value="">-- Thể loại --</option>
 {% for g in genres %}<option {{'selected' if g==genre}}>{{g}}</option>{% endfor %}</select>
 Năm <input name="y1" value="{{y1}}" size="5"> - <input name="y2" value="{{y2}}" size="5">
 <button>Tìm</button>
</form>
<p class="note">{{ds|length}} phim{{' (tìm bằng inverted index)' if q}}</p>
<table><tr><th>ID</th><th>Tên phim</th><th>Năm</th><th>Thể loại</th></tr>
{% for p in ds %}<tr><td>{{p.movie_id}}</td><td><a href="/movie/{{p.movie_id}}">{{p.title}}</a></td>
<td>{{p.release_year}}</td><td>{{p.genres}}</td></tr>{% endfor %}</table>""")

DETAIL = BASE.replace("{% block body %}{% endblock %}", """
<h2>{{p.title}} ({{p.release_year}})</h2>
<p><b>Thể loại:</b> {{p.genres}} | <b>Ngôn ngữ:</b> {{p.language}} | <b>Thời lượng:</b> {{p.runtime}} phút</p>
<p><b>Budget:</b> {{p.budget or 'chưa có'}} | <b>Revenue:</b> {{p.revenue or 'chưa có'}} | <b>IMDb:</b> {{p.imdb_id}}</p>
<p>{{p.overview}}</p>
<p><b>Điểm người dùng:</b> {{tb}} ({{n}} lượt đánh giá, đọc từ bảng ratings theo rowkey {{p.movie_id}}_*)</p>
<p><a href="/edit/{{p.movie_id}}">Sửa</a></p>
<form method="post" action="/delete/{{p.movie_id}}" onsubmit="return confirm('Xóa phim này?')">
<button>Xóa phim</button></form>""")

FORM = BASE.replace("{% block body %}{% endblock %}", """
<h2>{{'Sửa phim ' ~ p.movie_id if p.movie_id else 'Thêm phim'}}</h2>
<form method="post">
{% if not p.movie_id %}ID phim <input name="movie_id" required><br>{% endif %}
{% for c in cols %}{{c}} <br>
{% if c=='overview' %}<textarea name="{{c}}" rows="4" cols="70">{{p[c]}}</textarea>
{% else %}<input name="{{c}}" value="{{p[c]}}" size="60">{% endif %}<br>{% endfor %}
<button>Lưu</button></form>""")

RANK = BASE.replace("{% block body %}{% endblock %}", """
<h2>Bảng xếp hạng (ít nhất {{toi_thieu}} lượt đánh giá)</h2>
<p class="note">Nguồn: {{nguon}}. <a href="/ranking?nguon=hive">Tính bằng Hive</a> (chậm, chạy job trên YARN)
 | <a href="/ranking">Tính nhanh từ HBase</a></p>
<table><tr><th>#</th><th>Tên phim</th><th>Điểm TB</th><th>Số lượt</th></tr>
{% for r in ds %}<tr><td>{{loop.index}}</td><td><a href="/movie/{{r[0]}}">{{r[1]}}</a></td>
<td>{{r[2]}}</td><td>{{r[3]}}</td></tr>{% endfor %}</table>""")


@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "")
    y1, y2 = request.args.get("y1", ""), request.args.get("y2", "")
    conn = ket_noi()
    t = conn.table("movies")
    if q:
        ds = [doc_phim(k, d) for k, d in t.rows([i.encode() for i in tim_theo_index(conn, q)])]
    else:
        ds = [doc_phim(k, d) for k, d in t.scan(limit=5000)]
    if genre:
        ds = [p for p in ds if genre in p["genres"].split("|")]
    if y1.isdigit():
        ds = [p for p in ds if p["release_year"].isdigit() and int(p["release_year"]) >= int(y1)]
    if y2.isdigit():
        ds = [p for p in ds if p["release_year"].isdigit() and int(p["release_year"]) <= int(y2)]
    conn.close()
    return render_template_string(HOME, ds=ds[:200], q=q, genre=genre, y1=y1, y2=y2, genres=GENRES)


@app.route("/movie/<mid>")
def detail(mid):
    conn = ket_noi()
    d = conn.table("movies").row(mid.encode())
    if not d:
        abort(404)
    diem = [float(v[b"r:rating"]) for _, v in conn.table("ratings").scan(row_prefix=(mid + "_").encode())]
    conn.close()
    tb = round(sum(diem) / len(diem), 2) if diem else "chưa có"
    return render_template_string(DETAIL, p=doc_phim(mid, d), tb=tb, n=len(diem))


def luu(mid):
    conn = ket_noi()
    conn.table("movies").put(mid.encode(), {("info:" + c).encode(): request.form.get(c, "").encode() for c in COLS})
    conn.close()


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        mid = request.form["movie_id"].strip()
        luu(mid)
        return redirect(url_for("detail", mid=mid))
    return render_template_string(FORM, p=dict.fromkeys(COLS + ["movie_id"], ""), cols=COLS)


@app.route("/edit/<mid>", methods=["GET", "POST"])
def edit(mid):
    if request.method == "POST":
        luu(mid)
        return redirect(url_for("detail", mid=mid))
    conn = ket_noi()
    d = conn.table("movies").row(mid.encode())
    conn.close()
    if not d:
        abort(404)
    return render_template_string(FORM, p=doc_phim(mid, d), cols=COLS)


@app.route("/delete/<mid>", methods=["POST"])
def delete(mid):
    conn = ket_noi()
    conn.table("movies").delete(mid.encode())
    conn.close()
    return redirect(url_for("home"))


@app.route("/ranking")
def ranking():
    toi_thieu = 3
    if request.args.get("nguon") == "hive":
        from pyhive import hive  # pip install "pyhive[hive_pure_sasl]"
        cur = hive.connect(host="localhost", port=10000, username="nhom06").cursor()
        cur.execute("""SELECT m.movie_id, m.title, ROUND(AVG(r.rating),2), COUNT(*)
            FROM phim_db.ratings r JOIN phim_db.movies m ON r.movie_id = m.movie_id
            GROUP BY m.movie_id, m.title HAVING COUNT(*) >= %d
            ORDER BY 3 DESC, 4 DESC LIMIT 20""" % toi_thieu)
        return render_template_string(RANK, ds=cur.fetchall(), toi_thieu=toi_thieu, nguon="Hive (phim_db)")
    conn = ket_noi()
    tong = {}
    for k, v in conn.table("ratings").scan(columns=[b"r:rating"]):
        mid = k.decode().split("_")[0]
        s, n = tong.get(mid, (0.0, 0))
        tong[mid] = (s + float(v[b"r:rating"]), n + 1)
    top = sorted(((m, round(s / n, 2), n) for m, (s, n) in tong.items() if n >= toi_thieu),
                 key=lambda x: (-x[1], -x[2]))[:20]
    ten = {k.decode(): d.get(b"info:title", b"").decode()
           for k, d in conn.table("movies").rows([m.encode() for m, _, _ in top])}
    conn.close()
    ds = [(m, ten.get(m, "(đã xóa)"), tb, n) for m, tb, n in top]
    return render_template_string(RANK, ds=ds, toi_thieu=toi_thieu, nguon="HBase (bảng ratings)")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
