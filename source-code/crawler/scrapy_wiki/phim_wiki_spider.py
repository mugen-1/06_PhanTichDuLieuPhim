#!/usr/bin/env python3
# Nguon bo sung - Cao trang Wikipedia tieng Viet bang Scrapy (giong ky thuat Lab04).
# Buoc 1: mo trang danh sach phim (mac dinh: "Danh sach phim co doanh thu cao nhat"),
#         lay link bai viet cua tung phim trong cac bang (table.wikitable).
# Buoc 2: vao tung bai, doc khung thong tin ben phai (infobox): dao dien, kinh phi,
#         doanh thu, thoi luong, quoc gia... va ma Wikidata (Q...) de noi voi du lieu khac.
#
# Chay tu thu muc goc repo:
#   scrapy runspider source-code/crawler/scrapy_wiki/phim_wiki_spider.py -O dataset/raw/wikipedia/vi_phim_scrapy.jsonl
# Doi trang bat dau:  -a start="https://vi.wikipedia.org/wiki/..."   Gioi han so phim: -a toi_da=100

import re
from urllib.parse import unquote, urlparse

import scrapy

# Link toi cac trang khong phai bai viet (anh, the loai, ban mau...) thi bo qua
KHONG_PHAI_BAI = ("Tập tin", "Hình", "Thể loại", "Bản mẫu", "Wikipedia", "Đặc biệt", "Trợ giúp",
                  "Cổng thông tin", "File", "Category", "Template", "Special", "Help", "Portal")

# Nhan trong infobox tieng Viet -> ten truong luu ra file
NHAN = {
    "Đạo diễn": "dao_dien",
    "Kinh phí": "kinh_phi",
    "Doanh thu": "doanh_thu",
    "Thời lượng": "thoi_luong",
    "Quốc gia": "quoc_gia",
    "Ngôn ngữ": "ngon_ngu",
    "Công chiếu": "cong_chieu",
    "Phát hành": "phat_hanh",
    "Diễn viên": "dien_vien",
}


class PhimWikiSpider(scrapy.Spider):
    name = "phim_wiki"
    custom_settings = {
        "ROBOTSTXT_OBEY": True,          # ton trong robots.txt cua Wikipedia
        "DOWNLOAD_DELAY": 1,             # nghi 1 giay giua 2 lan tai trang
        "CONCURRENT_REQUESTS": 2,
        "USER_AGENT": "DoAnBigData-Nhom06/1.0 (do an sinh vien; https://github.com/mugen-1/06_PhanTichDuLieuPhim)",
        "FEED_EXPORT_ENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, start=None, toi_da=200, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start or "https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_phim_c%C3%B3_doanh_thu_cao_nh%E1%BA%A5t"]
        self.toi_da = int(toi_da)
        self.da_gui = set()

    def ten_bai(self, href, trang_hien_tai):
        # Wikipedia tra link dang day du "https://vi.wikipedia.org/wiki/Avatar_(2009_film)"
        # hoac dang ngan "/wiki/Avatar". Tra ve ten bai, hoac None neu khong phai bai viet.
        url = urlparse(href)
        cung_trang = not url.netloc or url.netloc == urlparse(trang_hien_tai).netloc   # chi lay link trong vi.wikipedia
        if not url.path.startswith("/wiki/") or url.query or not cung_trang:
            return None
        ten = unquote(url.path[len("/wiki/"):]).replace("_", " ")
        if ":" in ten and ten.split(":")[0] in KHONG_PHAI_BAI:   # "Tập tin:x.jpg" thi bo, "Avengers: Endgame" thi giu
            return None
        if re.fullmatch(r"\d{3,4}|Năm \d+", ten):                   # link sang trang nam
            return None
        return ten

    def parse(self, response):
        # Moi dong cua bang: ten phim nam trong o tieu de dong (th scope=row), chu nghieng <i>
        for dong in response.css("table.wikitable tr"):
            links = dong.css("th[scope=row] a") or dong.css("i a") or dong.css("td a")
            for a in links:
                if "new" in (a.attrib.get("class") or ""):          # link do: bai chua duoc viet
                    continue
                ten = self.ten_bai(a.attrib.get("href", ""), response.url)
                if ten is None:
                    continue
                if ten not in self.da_gui and len(self.da_gui) < self.toi_da:
                    self.da_gui.add(ten)
                    yield response.follow(a.attrib["href"], callback=self.parse_phim)
                break                     # chi lay 1 link moi dong (cot ten phim)
        self.logger.info("Trang danh sach: tim thay %d bai phim", len(self.da_gui))

    def parse_phim(self, response):
        item = {"ten_bai": response.css("h1#firstHeading ::text").get(default="").strip(),
                "url": response.url}
        # Ma Wikidata: lay o muc "Khoan muc Wikidata" ben trai, khong co thi tim trong cau hinh cua trang
        wd = response.css("li#t-wikibase a::attr(href)").get() or ""
        m = re.search(r"Q\d+", wd) or re.search(r'"wgWikibaseItemId":"(Q\d+)"', response.text)
        item["wikidata_id"] = (m.group(1) if m and m.groups() else m.group(0)) if m else None
        for tr in response.css("table.infobox tr"):
            nhan = " ".join(tr.css("th ::text").getall()).strip()
            if nhan in NHAN:
                # Lay chu trong o, bo so chu thich [1] (the <sup>) va CSS
                chu = tr.xpath("./td//text()[not(ancestor::sup) and not(ancestor::style)]").getall()
                # Danh sach nguoi (dao dien, dien vien): moi ten 1 doan chu -> noi bang dau phay
                noi = ", " if NHAN[nhan] in ("dao_dien", "dien_vien") else " "
                chu = [c.strip() for c in chu if c.strip()]
                item[NHAN[nhan]] = re.sub(r"\s+", " ", noi.join(chu)).strip() or None
        if item["wikidata_id"] is None and not any(k in item for k in NHAN.values()):
            self.logger.info("Bo qua (khong phai bai phim): %s", response.url)
            return
        yield item
