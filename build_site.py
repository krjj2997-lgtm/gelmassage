# -*- coding: utf-8 -*-
"""Build the static directory for https://outcallmassage.co.kr/."""
import json
import math
import os
import re
import shutil
from html import escape
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "gelmsg", "market_full.json")
IMG_SRC = os.path.join(ROOT, "images")
WEB = os.path.join(ROOT, "web", "assets")
OUT = os.path.join(ROOT, "site")
ORIGIN = "https://outcallmassage.co.kr"
BRAND = "콜건마"
LOCATION_TREE = {}
COORDS = {
    "강남": (37.497, 127.028), "서초": (37.483, 127.032), "송파": (37.514, 127.106),
    "강동": (37.530, 127.123), "광진": (37.538, 127.082), "성동": (37.563, 127.037),
    "용산": (37.532, 126.990), "중구": (37.564, 126.997), "종로": (37.573, 126.979),
    "동대문": (37.574, 127.040), "성북": (37.589, 127.016), "강북": (37.640, 127.026),
    "도봉": (37.668, 127.047), "노원": (37.654, 127.056), "중랑": (37.606, 127.093),
    "마포": (37.566, 126.902), "서대문": (37.579, 126.937), "은평": (37.602, 126.929),
    "영등포": (37.526, 126.896), "동작": (37.512, 126.939), "관악": (37.478, 126.951),
    "금천": (37.457, 126.895), "구로": (37.495, 126.888), "양천": (37.517, 126.866),
    "강서": (37.551, 126.850), "여의도": (37.522, 126.924),
    "수원": (37.263, 127.029), "성남": (37.420, 127.127), "분당": (37.382, 127.119),
    "용인": (37.241, 127.178), "광교": (37.285, 127.058), "고양": (37.658, 126.832),
    "일산": (37.670, 126.750), "부천": (37.504, 126.766), "안양": (37.394, 126.957),
    "평촌": (37.394, 126.963), "안산": (37.322, 126.831), "시흥": (37.380, 126.803),
    "화성": (37.199, 126.831), "동탄": (37.200, 127.075), "김포": (37.615, 126.716),
    "남양주": (37.636, 127.217), "하남": (37.539, 127.215), "광주하남": (37.429, 127.255),
    "평택": (36.992, 127.113), "파주": (37.760, 126.780), "의정부": (37.738, 127.034),
    "구리": (37.594, 127.130), "군포": (37.361, 126.935), "광명": (37.478, 126.864),
    "이천": (37.272, 127.435), "오산": (37.150, 127.077), "양주": (37.785, 127.046),
    "포천": (37.895, 127.200), "동두천": (37.903, 127.060), "과천": (37.429, 126.988),
    "의왕": (37.345, 126.976), "여주": (37.298, 127.637), "안성": (37.008, 127.280),
    "인천": (37.456, 126.705), "부평": (37.507, 126.722), "계양": (37.537, 126.738),
    "남동": (37.447, 126.731), "연수": (37.410, 126.678), "미추홀": (37.463, 126.650),
    "서구": (37.545, 126.676), "검단": (37.602, 126.658), "강화": (37.747, 126.488),
    "부산": (35.179, 129.075), "해운대": (35.163, 129.164), "부산진": (35.163, 129.053),
    "동래": (35.205, 129.084), "수영": (35.145, 129.113), "남구": (35.136, 129.084),
    "연제": (35.176, 129.080), "금정": (35.243, 129.092), "사상": (35.153, 128.991),
    "사하": (35.104, 128.974), "기장": (35.244, 129.222), "영도": (35.091, 129.068),
    "대구": (35.871, 128.601), "수성": (35.858, 128.631), "달서": (35.830, 128.533),
    "대전": (36.351, 127.385), "유성": (36.362, 127.356), "대덕": (36.347, 127.435),
    "광주": (35.160, 126.851), "광산": (35.139, 126.794),
    "울산": (35.538, 129.311), "울주": (35.522, 129.243),
    "세종": (36.480, 127.289),
    "춘천": (37.882, 127.730), "원주": (37.342, 127.920), "강릉": (37.752, 128.876),
    "동해": (37.525, 129.114), "삼척": (37.450, 129.165), "속초": (38.207, 128.592),
    "태백": (37.164, 128.986), "정선": (37.381, 128.661), "횡성": (37.492, 127.985),
    "홍천": (37.697, 127.889), "평창": (37.370, 128.390), "영월": (37.184, 128.462),
    "양양": (38.076, 128.619), "인제": (38.070, 128.171), "철원": (38.146, 127.313),
    "청주": (36.642, 127.489), "충주": (36.991, 127.926), "제천": (37.132, 128.191),
    "천안": (36.815, 127.114), "아산": (36.790, 127.002), "공주": (36.447, 127.119),
    "서산": (36.785, 126.450), "당진": (36.893, 126.628),
    "전주": (35.824, 127.148), "군산": (35.968, 126.737), "익산": (35.948, 126.958),
    "남원": (35.416, 127.390),
    "여수": (34.760, 127.662), "순천": (34.950, 127.487), "목포": (34.812, 126.392),
    "광양": (34.940, 127.696), "나주": (35.016, 126.711),
    "포항": (36.019, 129.343), "경주": (35.856, 129.225), "구미": (36.119, 128.344),
    "안동": (36.568, 128.730), "김천": (36.140, 128.114),
    "창원": (35.228, 128.682), "김해": (35.228, 128.889), "진주": (35.180, 128.108),
    "양산": (35.335, 129.037), "거제": (34.880, 128.621), "통영": (34.854, 128.433),
    "사천": (35.003, 128.064), "장유": (35.191, 128.813),
    "제주": (33.499, 126.531), "서귀포": (33.254, 126.560),
}

REGIONS = [
    ("서울", "seoul"),
    ("경기", "gyeonggi"),
    ("인천", "incheon"),
    ("부산", "busan"),
    ("대구", "daegu"),
    ("대전", "daejeon"),
    ("광주", "gwangju"),
    ("울산", "ulsan"),
    ("세종", "sejong"),
    ("강원", "gangwon"),
    ("충북", "chungbuk"),
    ("충남", "chungnam"),
    ("전북", "jeonbuk"),
    ("전남", "jeonnam"),
    ("경북", "gyeongbuk"),
    ("경남", "gyeongnam"),
    ("제주", "jeju"),
    ("기타", "etc"),
]
REGION_SLUG = {name: slug for name, slug in REGIONS}
SEOUL = {
    "강남", "강남역", "송파", "강서", "마포", "광진", "관악", "노원", "동대문",
    "영등포", "여의도", "강동", "중랑", "종로", "서초", "용산", "구로", "금천",
    "성북", "양천", "강북", "도봉", "은평", "동작", "성동", "중구", "서대문",
    "선릉", "잠실", "홍대", "신촌", "건대", "왕십리", "청량리", "수유", "미아",
}
CITY = {
    "수원": "경기", "분당": "경기", "일산": "경기", "부천": "경기", "화성": "경기",
    "시흥": "경기", "안산": "경기", "안양": "경기", "김포": "경기", "남양주": "경기",
    "하남": "경기", "평택": "경기", "용인": "경기", "고양": "경기", "파주": "경기",
    "광명": "경기", "구리": "경기", "군포": "경기", "이천": "경기", "오산": "경기",
    "의정부": "경기", "양주": "경기", "포천": "경기", "동두천": "경기", "과천": "경기",
    "의왕": "경기", "여주": "경기", "광교": "경기", "성남": "경기", "안성": "경기",
    "광주하남": "경기",
    "청주": "충북", "충주": "충북", "제천": "충북",
    "천안": "충남", "아산": "충남", "공주": "충남", "서산": "충남", "당진": "충남",
    "창원": "경남", "김해": "경남", "진주": "경남", "양산": "경남", "거제": "경남",
    "통영": "경남", "사천": "경남",
    "포항": "경북", "경주": "경북", "구미": "경북", "안동": "경북", "김천": "경북",
    "전주": "전북", "군산": "전북", "익산": "전북", "남원": "전북",
    "여수": "전남", "순천": "전남", "목포": "전남", "광양": "전남", "나주": "전남",
    "강릉": "강원", "원주": "강원", "춘천": "강원", "속초": "강원", "동해": "강원",
    "삼척": "강원", "태백": "강원", "홍천": "강원",
    "제주": "제주", "서귀포": "제주", "세종": "세종",
}
HEADINGS = ("공지안내", "영업시간", "오시는길", "관리사님", "프로그램")


def norm(value):
    return re.sub(r"[^0-9a-z가-힣]", "", (value or "").lower())


def fold_digits(text):
    return re.sub(r"(?<=[0-9])\s+(?=[0-9])", "", text or "")


def jpeg_size(path):
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:2] != b"\xff\xd8":
        return 4, 3
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[i + 5:i + 7], "big")
            width = int.from_bytes(data[i + 7:i + 9], "big")
            if width and height:
                return width, height
            break
        if marker in (0xD8, 0xD9):
            i += 2
            continue
        size = int.from_bytes(data[i + 2:i + 4], "big")
        if size < 2:
            break
        i += 2 + size
    return 4, 3


def region_from_text(text):
    raw = text or ""
    rules = (
        ("서울", "서울특별시"),
        ("부산", "부산광역시"),
        ("대구", "대구광역시"),
        ("인천", "인천광역시"),
        ("광주", "광주광역시"),
        ("대전", "대전광역시"),
        ("울산", "울산광역시"),
        ("세종", "세종특별"),
        ("경기", "경기도"),
        ("강원", "강원"),
        ("충북", "충청북도"),
        ("충남", "충청남도"),
        ("전북", "전북"),
        ("전북", "전라북도"),
        ("전남", "전라남도"),
        ("전남", "전남"),
        ("경북", "경상북도"),
        ("경남", "경상남도"),
        ("제주", "제주"),
        ("서울", "서울시"),
        ("부산", "부산시"),
        ("대구", "대구시"),
        ("인천", "인천시"),
        ("대전", "대전시"),
        ("울산", "울산시"),
    )
    for name, token in rules:
        if token in raw:
            return name
    return ""


def region_from_token(token):
    token = re.sub(r"(마사지|출장|홈타이|1인샵)$", "", token or "")
    if token in SEOUL:
        return "서울"
    return CITY.get(token, "")


METRO = {"서울", "부산", "대구", "인천", "광주", "대전", "울산"}
METRO_GU = {
    "강남", "송파", "강서", "마포", "광진", "관악", "노원", "동대문", "영등포", "강동",
    "중랑", "종로", "서초", "용산", "구로", "금천", "성북", "양천", "강북", "도봉",
    "은평", "동작", "성동", "중구", "서대문", "영도", "부산진", "동래", "해운대",
    "사하", "금정", "연제", "수영", "사상", "기장", "수성", "달서", "달성", "군위",
    "미추홀", "연수", "남동", "부평", "계양", "강화", "옹진", "검단", "광산", "유성",
    "대덕", "울주", "동구", "서구", "남구", "북구",
}
REGION_WORDS = {name for name, _slug in REGIONS}
JEONNAM_CITY = (
    "나주", "목포", "여수", "순천", "광양", "무안", "해남", "담양", "장성", "영광",
    "함평", "영암", "보성", "화순", "고흥", "곡성", "구례", "진도", "완도", "강진",
    "장흥", "신안",
)


def region_from_address(address):
    raw = address or ""
    if "전남광주통합특별시" in raw:
        head = raw.split("/")[0]
        if any(city in head for city in JEONNAM_CITY):
            return "전남"
        return "광주"
    return region_from_text(raw)


def region_from_title_places(title):
    for part in title_place_parts(title):
        if part in SEOUL:
            return "서울"
        if part in CITY:
            return CITY[part]
        base = re.sub(r"(시|군|구)$", "", part)
        if base in SEOUL:
            return "서울"
        if base in CITY:
            return CITY[base]
    return ""


def title_place_parts(title):
    head = (title or "").split("〔")[0].split("[")[0].split("｛")[0]
    head = re.sub(r"(1인홈케어|2인홈케어|3인홈케어|1인샵|2인샵|3인샵|홈케어|홈타이|1인홈|&홈)", " ", head)
    head = re.sub(r"[\.·]", " ", head)
    parts = []
    for part in head.split():
        part = part.strip()
        if not part or part in ("남쌤", "샵"):
            continue
        parts.append(part)
    return parts


def admin_tokens(text):
    text = re.sub(r"\([^)]*\)", " ", text or "")
    text = text.replace("전남광주통합특별시", " ")
    text = re.sub(r"(특별자치시|특별자치도|특별시|광역시)", " ", text)
    found = []
    chunks = [chunk for chunk in re.split(r"[\s/,·]+", text) if chunk]
    for chunk in chunks:
        road_dong = re.fullmatch(r"([가-힣]{2,12}로\d+가)", chunk)
        if road_dong:
            found.append((road_dong.group(1), "dong"))
            continue
        match = re.fullmatch(r"([가-힣]{1,10})(시|군|구|읍|면|동|리|역)(\d+가)?", chunk)
        if not match:
            continue
        name, kind, ga = match.group(1), match.group(2), match.group(3) or ""
        if kind == "리" and (name.endswith("사거") or chunk.endswith("사거리")):
            continue
        if kind == "시":
            if len(name) < 2:
                continue
            found.append((name, "si"))
        elif kind == "군":
            if len(name) < 2:
                continue
            found.append((name, "gun"))
        elif kind == "구":
            if len(name) < 1:
                continue
            if len(name) == 1 or name in ("중", "동", "서", "남", "북"):
                name = name + "구"
            found.append((name, "gu"))
        elif kind == "역":
            if len(name) < 2:
                continue
            found.append((name + "역", "station"))
        else:
            if len(name) < 1:
                continue
            found.append((name + kind + ga, "dong"))
    return found


def choose_sub(region, tokens, title_parts):
    for part in title_parts:
        if part in REGION_WORDS:
            continue
        base = re.sub(r"(시|군|구)$", "", part)
        base = re.sub(r"역$", "", base)
        if base in CITY or base in METRO_GU:
            return base
    if region in METRO:
        gus = [name for name, kind in tokens if kind == "gu"]
        if gus:
            return gus[0]
    for kind in ("si", "gun", "gu"):
        names = [name for name, token_kind in tokens if token_kind == kind]
        if names:
            return names[0]
    for name, kind in tokens:
        if kind != "dong":
            continue
        short = re.sub(r"\d+가$", "", name)
        short = re.sub(r"(동|읍|면|리)$", "", short)
        if len(short) >= 2 and short not in REGION_WORDS:
            return short
    return "기타"


def choose_spots(sub, tokens, title_parts):
    spots = []
    for name, kind in tokens:
        if kind in ("dong", "station") and name not in spots:
            spots.append(name)
    for part in title_parts:
        if part in REGION_WORDS or part == sub:
            continue
        label = part.replace("&", "")
        label = re.sub(r"(1인|2인|3인|샵|홈)$", "", label).strip()
        if label in ("홈", "샵", "1인", "2인", "3인", "케어", "홈케어", "전지역", "관리", "방문"):
            continue
        if label in CITY or label in METRO_GU:
            continue
        label = re.sub(r"(시|군|구)$", "", label)
        if len(label) < 2 or label == sub or label in spots or label in REGION_WORDS:
            continue
        spots.append(label)
    kept = []
    for spot in spots:
        if any(spot != other and spot in other for other in spots):
            continue
        if spot not in kept:
            kept.append(spot)
    return kept[:8]


def location_of(address, title, region):
    tokens = admin_tokens(address)
    title_parts = title_place_parts(title)
    sub = choose_sub(region, tokens, title_parts)
    spots = choose_spots(sub, tokens, title_parts)
    return sub, spots


def shop_name(title):
    match = re.search(r"[〔｛\[]\s*(.+?)\s*[〕｝\]]", title or "")
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()
    return re.sub(r"\s+", " ", title or "").strip()


def place_label(title, region):
    head = (title or "").split("〔")[0].split("[")[0].split("｛")[0]
    head = re.sub(r"[\.·]", " ", head)
    head = re.sub(r"\s+", " ", head).strip()
    return head or region or "전국"


def first_price(content):
    text = content or ""
    match = re.search(r"(\d+)\s*만", text)
    if match:
        return f"{int(match.group(1))}만원~"
    for match in re.finditer(r"(\d{1,3}(?:,\d{3})+|\d{4,7})\s*원", text):
        amount = int(match.group(1).replace(",", ""))
        if amount >= 10000:
            return f"{amount:,}원~"
    return ""


def hours_of(content):
    lines = (content or "").split("\n")
    for index, line in enumerate(lines):
        compact = re.sub(r"[^가-힣]", "", line)
        if compact == "영업시간":
            for nxt in lines[index + 1:index + 5]:
                text = nxt.strip()
                if text:
                    return text[:48]
    return ""


def blurb(content, fallback):
    kept = []
    for line in (content or "").split("\n"):
        text = line.strip()
        if not text:
            continue
        compact = re.sub(r"[^가-힣]", "", text)
        if compact in HEADINGS:
            break
        kept.append(text)
    text = re.sub(r"\s+", " ", " ".join(kept[2:7])).strip()
    text = text or fallback
    if len(text) > 140:
        text = text[:139].rstrip() + "…"
    return text


FLAGS = (
    ("한국", "kr", "한국.jpg"),
    ("중국", "cn", "중국.jpg"),
    ("일본", "jp", "일본.jpg"),
    ("태국", "th", "태국.jpg"),
    ("베트남", "vn", "베트남.PNG"),
    ("러시아", "ru", "러시아.jpg"),
)
NATION_NAMES = tuple(name for name, _code, _file in FLAGS)


def staff_text(content):
    lines = []
    on = False
    for raw in (content or "").split("\n"):
        text = raw.strip()
        if not text:
            continue
        head = heading_of(text)
        if head:
            if on:
                break
            on = head == "관리사님"
            continue
        if on:
            lines.append(text)
    return "\n".join(lines)


def nations_in(text):
    flat = re.sub(r"\s+", "", text or "")
    for token in ("한국어", "한국말", "일본식", "일본스웨디시", "일본유학", "일본협회"):
        flat = flat.replace(token, " ")
    found = []

    def add(name):
        if name not in found:
            found.append(name)

    for match in re.finditer(r"(베트남|러시아|태국|일본|중국|한국)인", flat):
        add(match.group(1))
        before = flat[max(0, match.start() - 18):match.start()]
        for name in NATION_NAMES:
            if name in before:
                add(name)
    for match in re.finditer(r"국적[:：]?([^.]{0,48})", flat):
        chunk = match.group(1)
        for name in NATION_NAMES:
            if name in chunk:
                add(name)
    for name in NATION_NAMES:
        if re.search(r"[(\[（【]" + name + r"(?:인)?[)\]）】]", flat):
            add(name)
        if re.search(name + r"(?:관리사|테라피스트|쌤|원장)", flat):
            add(name)
        if re.search(name + r"[가-힣]{1,4}쌤", flat):
            add(name)
    ordered = [name for name in NATION_NAMES if name in found]
    return ordered


def flag_html(names):
    bits = []
    have = set(names or [])
    for name, code, filename in FLAGS:
        if name not in have:
            continue
        ext = "png" if filename.lower().endswith(".png") else "jpg"
        bits.append(
            f'<img class="flag" src="/images/flags/{code}.{ext}" alt="{escape(name)}" width="20" height="14">'
        )
    if not bits:
        return ""
    return f'<span class="flags">{"".join(bits)}</span>'


def heading_of(line):
    compact = re.sub(r"[^가-힣]", "", line or "")
    if compact in HEADINGS:
        return compact
    return ""


def is_price_line(text):
    if not re.search(r"\d+(?:\.\d+)?\s*만", text or ""):
        return False
    if len(text) > 46:
        return False
    if re.search(r"합니다|입니다|주세요|추가|포함|할인", text):
        return False
    return True


def is_point_line(text):
    compact = re.sub(r"[\s\(\)\[\]「」『』\*\#\.·・]", "", text or "")
    if not compact or len(compact) > 16:
        return False
    if re.search(r"\d|합니다|입니다|주세요|드립니다|가능", compact):
        return False
    if re.search(r"주간|야간", compact) and re.search(r"테라피|할인|코스|이벤트|관리", compact):
        return True
    if re.search(r"(코스|테라피)$", compact):
        return True
    return False


def won_label(prefix, amount):
    name = {"주": "주간", "야": "야간"}.get(prefix or "", prefix or "")
    if name:
        return f"{name} {amount}만원"
    return f"{amount}만원"


def render_rate(text):
    parts = re.split(r"\s*[➜➳➔→>]\s*", text)
    def amounts(chunk):
        found = []
        for match in re.finditer(r"(주간|야간|심야|주야|주|야)?\s*(\d+(?:\.\d+)?)\s*만", chunk):
            found.append(won_label(match.group(1), match.group(2)))
        return found
    before = amounts(parts[0]) if parts else []
    after = []
    for chunk in parts[1:]:
        after.extend(amounts(chunk))
    minute = re.search(r"(\d+)\s*분", text)
    if minute:
        lead = text[:minute.start()]
        lead = re.sub(r"[^\w가-힣A-Za-z0-9\s]", " ", lead)
        lead = re.sub(r"\s+", " ", lead).strip(" .-")
        left = f"{lead} {minute.group(1)}분".strip()
    else:
        left = re.split(r"[➜➳➔→>]|\d+(?:\.\d+)?\s*만", text)[0]
        left = re.sub(r"[^\w가-힣A-Za-z0-9\s]", " ", left)
        left = re.sub(r"\s+", " ", left).strip()
    pays = []
    sale = bool(after)
    for label in before:
        pays.append(f"<s>{escape(label)}</s>" if sale else f"<b>{escape(label)}</b>")
    for label in after:
        pays.append(f"<b>{escape(label)}</b>")
    if not left and not pays:
        return ""
    return (
        f'<div class="rate"><span class="rate-time">{escape(left or "코스")}</span>'
        f'<span class="rate-pay">{"".join(pays)}</span></div>'
    )


def batchim(word):
    for char in reversed(word or ""):
        if "가" <= char <= "힣":
            return (ord(char) - 0xAC00) % 28 != 0
    return True


def euro(word):
    for char in reversed(word or ""):
        if "가" <= char <= "힣":
            code = (ord(char) - 0xAC00) % 28
            return "로" if code in (0, 8) else "으로"
    return "으로"


def ira(word):
    return "이라고" if batchim(word) else "라고"


def particle(word, pair):
    return pair[0] if batchim(word) else pair[1]


REVIEW_SEEN = set()


def review_texts(shop):
    name = (shop.get("name") or "업체").strip()
    place = (shop.get("place") or shop.get("region") or "이 지역").strip()
    service = ((shop.get("service") or "마사지").split() or ["마사지"])[0]
    price = (shop.get("price") or "").strip()
    hours = (shop.get("hours") or "").strip()
    sub = (shop.get("sub") or "").strip()
    if sub in ("", "기타"):
        sub = (shop.get("region") or place).strip()
    address = ((shop.get("address") or "").split("/")[0] or "").strip()
    seed = sum((index + 1) * ord(char) for index, char in enumerate(str(shop.get("id") or name)))
    ne = particle(name, ("은", "는"))
    neul = particle(name, ("을", "를"))
    ni = particle(name, ("이", "가"))
    se = particle(service, ("은", "는"))
    si = particle(service, ("이", "가"))
    place_e = particle(place, ("에서", "에서"))
    bits = []
    if price:
        shown = price.rstrip("~～ ").strip()
        label = shown + ("부터" if price.endswith(("~", "～")) else "")
        bits.append(f"시작 가격은 {label}{ira(label)} 적혀 있다")
        bits.append(f"표에 나온 첫 금액은 {label}이다")
    if hours:
        bits.append(f"영업시간은 {hours}{euro(hours)} 안내된다")
        bits.append(f"문을 여는 시간은 {hours}{ira(hours)} 적혀 있다")
    if address:
        bits.append(f"주소에는 {address}{particle(address, ('이', '가'))} 보인다")
        bits.append(f"찾아가는 글에는 {address}{particle(address, ('이', '가'))} 적혀 있다")
    bits.extend([
        f"{sub} 일대를 기준으로 위치를 비교하기 쉽다",
        f"{service} 관리 시간을 프로그램 표에서 먼저 보면 된다",
        "공지에 적힌 취소 시간을 읽고 움직이는 편이 낫다",
        "전화로 받을 수 있는 시간을 한 번 더 확인하면 된다",
        "코스 이름이 나뉘어 있어 원하는 시간을 고르기 쉽다",
        "오시는 길과 영업시간을 같이 보고 출발하면 된다",
        "예약 문자는 희망 시간을 적어서 남기는 편이 분명하다",
        f"{place} 안에서 코스 길이를 먼저 고르면 일정이 덜 겹친다",
        "관리 전 주의 사항은 공지 문장을 다시 읽는 쪽이 안전하다",
        f"{sub}{euro(sub)} 갈 때는 오시는 길 문장을 먼저 보면 된다",
    ])
    frames = [
        [
            "{place}{pe} {name}{neul} 찾을 때 {service} 안내가 먼저 보였다. {bit}.",
            "{name} 상세를 {place} 업체로 열어 보니 {service} 코스 설명이 위에 있었다. {bit}.",
            "{place} 목록에서 {name}{neul} 골랐더니 {service}{si} 어떤 시간으로 나뉘는지 바로 보였다. {bit}.",
            "{sub} 쪽 {name}{neun} {service} 소개가 짧고 분명해서 예약 전에 읽기 좋았다. {bit}.",
        ],
        [
            "{name}{neun} {sub}에서 코스 시간을 표로 적어 두어 비교가 쉬웠다. {bit}.",
            "{sub} {name} 프로그램은 시간별로 줄이 나뉘어 원하는 길이를 집기 편했다. {bit}.",
            "{name} 코스를 {sub} 기준으로 읽어 보니 짧은 관리와 긴 관리가 구분돼 있었다. {bit}.",
            "{place} {name}{neun} 관리 시간을 숫자로 보여 줘서 일정을 맞추기 수월했다. {bit}.",
        ],
        [
            "{place} {name} 글을 읽고 나니 예약 전에 확인할 항목이 분명했다. {bit}.",
            "{name}{neul} 예약하려면 {place} 위치와 코스를 먼저 맞춰 보는 구성이었다. {bit}.",
            "{sub}에서 {name} 예약을 준비할 때 공지와 프로그램이 따로 보여 조건이 안 섞였다. {bit}.",
            "{name} 안내문은 {place} 방문 전에 볼 문장과 코스 문장이 나뉘어 있었다. {bit}.",
        ],
        [
            "{sub}에서 {name} 위치를 볼 때는 오시는 길 문장을 같이 보는 게 좋았다. {bit}.",
            "{name}{neun} {place} 오시는 길을 따로 적어 두어 길 찾기가 덜 헷갈렸다. {bit}.",
            "{place}에서 {name}{neul} 찾아갈 때는 주소 문장을 코스보다 먼저 읽게 됐다. {bit}.",
            "{sub} {name}{neun} 위치 설명이 본문 안에 있어 지도 전에 방향을 가늠할 수 있었다. {bit}.",
        ],
        [
            "{place} {name} 프로그램은 {service} 시간 단위로 나뉘어 있어 일정을 맞추기 편했다. {bit}.",
            "{service}{se} {name}에서 시간대별로 적혀 있어 {place} 일정에 끼워 넣기 쉬웠다. {bit}.",
            "{place} {name}{neun} {service} 코스를 여러 길이로 나눠 두어 한 가지만 고르면 됐다. {bit}.",
            "{place} {name}의 {service} 안내는 관리 시간이 줄마다 달라 비교가 빨랐다. {bit}.",
        ],
        [
            "{place} {name}{neun} 공지와 코스를 따로 적어 두어 조건을 놓치지 않았다. {bit}.",
            "{name} 공지를 먼저 읽고 코스를 보니 {sub} 방문 조건이 더 분명해졌다. {bit}.",
            "{sub} {name}{neun} 주의 사항이 가격표와 섞이지 않아 읽다가 빠뜨릴 일이 적었다. {bit}.",
            "{name}{neul} 이용하기 전에 공지 문단을 끝까지 읽는 구성이라 {place}에서 확인이 쉬웠다. {bit}.",
        ],
        [
            "{name}{neul} {sub} 업체로 좁혀 보니 연락 전에 볼 내용이 한 페이지에 모여 있었다. {bit}.",
            "{sub}에서 {name}{ni} 어떤 곳인지 볼 때 전화, 시간, 코스가 한눈에 들어왔다. {bit}.",
            "{place} {name} 페이지는 문의 전에 필요한 줄이 위에 모여 있었다. {bit}.",
            "{name}{neun} {sub} 검색 결과에서 열었을 때 소개와 가격이 이어져 읽기 편했다. {bit}.",
        ],
        [
            "{place}에서 {name} 영업 안내를 먼저 읽고 코스를 고르니 선택이 빨라졌다. {bit}.",
            "{name} 영업 안내를 보고 {place} 일정에 맞는 코스만 남기게 됐다. {bit}.",
            "{sub} {name}{neun} 여는 시간을 본 다음 프로그램을 보게 되어 헛걸음이 줄었다. {bit}.",
            "{name}{neul} {place}에서 고를 때 영업시간과 코스를 같이 두어 결정이 짧았다. {bit}.",
        ],
        [
            "{name}{neun} {service} 소개와 위치 문장이 이어져 있어 {sub} 방문을 가늠하기 좋았다. {bit}.",
            "{service}{si} 필요하다고 {place}에서 찾을 때 {name} 소개가 위치와 붙어 있었다. {bit}.",
            "{sub}에서 {service}{neul_s} 알아보는데 {name}{ni} 코스와 길을 같이 적어 두었다. {bit}.",
            "{name}의 {service} 글은 {place}에서 어떤 관리인지 먼저 알려 주고 위치를 뒤에 두었다. {bit}.",
        ],
        [
            "{place} {name} 페이지는 가격, 시간, 주소가 떨어져 있어 필요한 줄만 다시 읽기 쉬웠다. {bit}.",
            "{name}{neun} 금액과 주소와 시간을 다른 문단에 두어 {sub}에서 다시 찾기 쉬웠다. {bit}.",
            "{place}에서 {name} 정보를 나눌 때 가격표만 따로 보게 되어 비교가 단순했다. {bit}.",
            "{sub} {name} 글은 주소 한 줄, 시간 한 줄, 코스 한 덩어리로 나뉘어 있었다. {bit}.",
        ],
    ]
    texts = []
    used = set()
    for index, group in enumerate(frames):
        for turn in range(len(group) * len(bits)):
            bit = bits[(seed + index * 5 + turn) % len(bits)]
            pattern = group[(seed + index + turn) % len(group)]
            text = pattern.format(
                place=place,
                name=name,
                service=service,
                sub=sub,
                bit=bit,
                neun=ne,
                neul=neul,
                ni=ni,
                se=se,
                si=si,
                pe=place_e,
                neul_s=particle(service, ("을", "를")),
            )
            if text not in used:
                used.add(text)
                texts.append(text)
                break
        else:
            texts.append(f"{place} {name} 안내 {index + 1}번째는 {bits[index % len(bits)]}.")
    unique = []
    for text in texts:
        if text not in REVIEW_SEEN:
            REVIEW_SEEN.add(text)
            unique.append(text)
            continue
        extra = f"{text} {place} {name} 상세를 다시 읽고 정리한 글이다."
        if address:
            extra = f"{text} {address}에 있는 {name} 안내를 보고 적었다."
        n = 2
        while extra in REVIEW_SEEN:
            extra = f"{text} {place} {name} 안내를 보고 적은 {n}번째 글이다."
            n += 1
        REVIEW_SEEN.add(extra)
        unique.append(extra)
    return unique


def review_section(shop):
    items = "".join(f"<p>{escape(text)}</p>" for text in review_texts(shop))
    return f'<section class="story reviews"><h2>후기</h2><div class="story-body">{items}</div></section>'


def format_content(content, after_notice="", flags=""):
    raw_lines = []
    for raw in (content or "").split("\n"):
        text = raw.strip()
        if text:
            raw_lines.append(text)
    kinds = []
    for index, text in enumerate(raw_lines):
        if heading_of(text):
            kinds.append("head")
        elif is_price_line(text):
            kinds.append("rate")
        elif is_point_line(text):
            kinds.append("point")
        else:
            nxt = index + 1 < len(raw_lines) and is_price_line(raw_lines[index + 1])
            compact = re.sub(r"\s+", "", text)
            if nxt and len(compact) <= 16 and not re.search(r"\d|합니다|입니다|주세요|가능|포함", compact):
                kinds.append("point")
            else:
                kinds.append("text")
    sections = []
    title = ""
    blocks = []
    pending = [after_notice]

    def flush():
        nonlocal title
        if not title and not blocks:
            return
        mark = flags if title == "관리사님" else ""
        heading = f"<h2>{escape(title)}{mark}</h2>" if title else ""
        html = []
        rates = []

        def dump_rates():
            if rates:
                html.append(f'<div class="rate-list">{"".join(rates)}</div>')
                rates.clear()

        for kind, text in blocks:
            if kind == "rate":
                rates.append(render_rate(text))
                continue
            dump_rates()
            if kind == "point":
                html.append(f'<p class="point">{escape(text)}</p>')
            else:
                html.append(f"<p>{escape(text)}</p>")
        dump_rates()
        sections.append(f'<section class="story">{heading}<div class="story-body">{"".join(html)}</div></section>')
        if title == "공지안내" and pending[0]:
            sections.append(pending[0])
            pending[0] = ""

    for text, kind in zip(raw_lines, kinds):
        if kind == "head":
            flush()
            title = heading_of(text)
            blocks = []
            continue
        blocks.append((kind, text))
    flush()
    if pending[0]:
        sections.append(pending[0])
    return "\n".join(sections)


def tel_href(phone):
    digits = re.sub(r"[^0-9+]", "", phone or "")
    return f"tel:{digits}" if digits else ""


def map_address(shop):
    raw = (shop.get("address") or shop.get("place") or shop.get("name") or "").strip()
    parts = [part.strip() for part in re.split(r"[/\n]", raw) if part.strip()]
    for part in parts:
        if re.search(r"(로|길)", part):
            return part
    return parts[0] if parts else (shop.get("name") or "")


def detail_actions(shop):
    phone = tel_href(shop.get("phone"))
    if phone:
        call = f'<a class="detail-action" href="{phone}">전화하기</a>'
    else:
        call = '<button type="button" class="detail-action" disabled>전화하기</button>'
    query = quote(map_address(shop))
    naver = f"https://map.naver.com/p/search/{query}"
    kakao = f"https://map.kakao.com/link/search/{query}"
    tmap = f"tmap://search?name={query}"
    return f"""<nav class="detail-actions" aria-label="업체 바로가기">
  {call}
  <button type="button" class="detail-action" id="open-route">길찾기</button>
  <a class="icon-btn" href="/nearby/" aria-label="내주변">{PIN_ICON}</a>
</nav>
<dialog id="route-dialog" class="route-dialog">
  <div class="route-sheet">
    <p class="route-title">길찾기</p>
    <p class="route-address">{escape(map_address(shop))}</p>
    <div class="route-apps">
      <a class="route-app" href="{naver}" target="_blank" rel="noopener">
        <span class="route-icon naver" aria-hidden="true"><svg viewBox="0 0 48 48" width="48" height="48"><rect width="48" height="48" rx="14" fill="#03C75A"/><path fill="#fff" d="M13 13h7.4L24 22.2V13h11v22H27.6L24 25.8V35H13z"/></svg></span>
        <span>네이버지도</span>
      </a>
      <a class="route-app" href="{kakao}" target="_blank" rel="noopener">
        <span class="route-icon kakao" aria-hidden="true"><svg viewBox="0 0 48 48" width="48" height="48"><rect width="48" height="48" rx="14" fill="#FEE500"/><path fill="#3C1E1E" d="M24 10c-6.1 0-11 4.2-11 9.4 0 3.4 2.2 6.3 5.5 8l-1.4 5.1c-.1.5.4.9.8.6l6.1-4c.3 0 .7.1 1 .1 6.1 0 11-4.2 11-9.8S30.1 10 24 10z"/></svg></span>
        <span>카카오맵</span>
      </a>
      <a class="route-app" href="{tmap}">
        <span class="route-icon tmap" aria-hidden="true"><svg viewBox="0 0 48 48" width="48" height="48"><rect width="48" height="48" rx="14" fill="#E51937"/><path fill="#fff" d="M24 8l4.2 10.2L39 20l-8 6.4L33.2 38 24 32.2 14.8 38 17 26.4 9 20l10.8-1.8z"/></svg></span>
        <span>티맵</span>
      </a>
    </div>
    <button type="button" class="route-close" id="close-route">닫기</button>
  </div>
</dialog>"""


def img_url(filename):
    return "/images/" + quote(filename)


def abs_url(path):
    return ORIGIN + path


def monogram(name):
    for char in name or "":
        if "가" <= char <= "힣" or char.isalnum():
            return char
    return "샵"


def alt_for(shop, filename, index, total):
    place = shop["place"]
    name = shop["name"]
    service = (shop.get("service") or "마사지").split()[0]
    service_bit = "" if service and (service in (name or "") or service in (place or "")) else service
    bits = []
    seen = set()
    for bit in (place, name, service_bit, "업체 사진"):
        for word in (bit or "").split():
            if word and word not in seen:
                bits.append(word)
                seen.add(word)
    alt = " ".join(bits)
    alt = re.sub(r"\s+", " ", alt).strip()
    if total > 1:
        alt = f"{alt} {index + 1}"
    if len(alt) > 90:
        alt = alt[:89].rstrip() + "…"
    return alt


LOGO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="28" height="28" aria-hidden="true">'
    '<circle cx="16" cy="16" r="12" fill="none" stroke="#ffd700" stroke-width="3"/>'
    '<circle cx="16" cy="16" r="5.5" fill="none" stroke="#ffd700" stroke-width="3"/></svg>'
)
SEARCH_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
    '<circle cx="10" cy="10" r="6.25" fill="none" stroke="currentColor" stroke-width="2"/>'
    '<path d="M15.2 15.2L21 21" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
)
PIN_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
    '<path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/></svg>'
)
MENU_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
    '<path fill="currentColor" d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z"/></svg>'
)
CHEVRON_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 8" width="11" height="8" aria-hidden="true">'
    '<path fill="currentColor" d="M1.1 1.2l4.9 4.9 4.9-4.9 1.1 1.1L6 8.3.1 2.3z"/></svg>'
)
THEMES = (
    ("스웨디시", "스웨디시"),
    ("타이", "타이마사지"),
    ("아로마", "아로마"),
    ("왁싱", "왁싱"),
    ("중국", "중국마사지"),
    ("발마사지", "발마사지"),
)


def won_price(price):
    text = price or ""
    if "만" in text:
        match = re.search(r"(\d+)", text)
        if not match:
            return ""
        return f"{int(match.group(1)) * 10000:,}원~"
    match = re.search(r"(\d[\d,]*)", text)
    if not match:
        return ""
    amount = int(match.group(1).replace(",", ""))
    if amount < 1000:
        return ""
    return f"{amount:,}원~"


def short_line(text, limit=72):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def badge(shop):
    blob = " ".join([shop.get("service") or "", shop.get("name") or "", shop.get("filename_text") or ""])
    if any(word in blob for word in ("출장", "홈타이", "홈케어")):
        return "출장마사지", "shop-type shop-type-outcall"
    return "힐링샵", "shop-type"


def location_tree(shops):
    tree = {}
    for shop in shops:
        region = shop.get("region") or "기타"
        sub = shop.get("sub") or "기타"
        bucket = tree.setdefault(region, {}).setdefault(sub, [])
        for spot in shop.get("spots") or []:
            if spot not in bucket:
                bucket.append(spot)
    ordered = {}
    for name, _slug in REGIONS:
        if name not in tree:
            continue
        subs = tree[name]
        ordered[name] = {sub: sorted(subs[sub]) for sub in sorted(subs)}
    return ordered


def region_options(active=""):
    options = ['<option value="">지역을 선택하세요</option>']
    names = [name for name, _slug in REGIONS if not LOCATION_TREE or name in LOCATION_TREE]
    for name in names:
        selected = " selected" if name == active else ""
        options.append(
            f'<option value="{escape(name)}" data-slug="{REGION_SLUG[name]}"{selected}>{escape(name)}</option>'
        )
    return "".join(options)


def side_menu():
    return f"""<div class="nav-backdrop" id="nav-backdrop" hidden></div>
<nav class="side-menu" id="side-menu" hidden aria-label="전체 메뉴">
  <p class="side-title">{BRAND}</p>
  <a id="menu-login" href="/login/">로그인</a>
  <a href="/signup/">회원가입</a>
  <hr class="menu-rule">
  <a href="/inquiry/">입점 문의</a>
  <a href="/notice/">공지사항</a>
  <a href="/event/">이벤트</a>
</nav>"""


def finder_bar(page, active=""):
    if page == "home":
        form = 'action="/all/" method="get"'
        chips = (
            '<a class="filter-btn active" href="/all/">전체</a>'
            '<a class="filter-btn" href="/all/?kind=shop">마사지</a>'
            '<a class="filter-btn" href="/all/?kind=outcall">출장마사지</a>'
        )
    else:
        form = 'action="" onsubmit="return false"'
        chips = (
            '<button type="button" class="filter-btn active" id="chip-all" data-kind="" data-theme="">전체</button>'
            '<button type="button" class="filter-btn" id="chip-shop" data-kind="shop" data-theme="">마사지</button>'
            '<button type="button" class="filter-btn" id="chip-outcall" data-kind="outcall" data-theme="">출장마사지</button>'
        )
    sub_disabled = "" if active else " disabled"
    theme_options = ['<option value="">테마보기</option>']
    for key, label in THEMES:
        theme_options.append(f'<option value="{escape(key)}">{escape(label)}</option>')
    return f"""<section class="finder" id="finder">
  <form class="text-search" role="search" {form}>
    <label class="skip" for="q">검색어</label>
    <input id="q" name="q" type="search" placeholder="검색어를 입력하세요" autocomplete="off">
    <button class="search-icon" type="submit" aria-label="검색">{SEARCH_ICON}</button>
  </form>
  <div class="loc-selects">
    <select id="sel-region" aria-label="지역을 선택하세요">{region_options(active)}</select>
    <div class="loc-row" style="display:flex;flex-direction:row;flex-wrap:nowrap;gap:10px;align-items:stretch;">
      <select id="sel-sub" aria-label="세부지역" style="flex:1 1 0;width:50%;min-width:0;"{sub_disabled}><option value="">세부지역</option></select>
      <select id="sel-spot" aria-label="동/역" style="flex:1 1 0;width:50%;min-width:0;" disabled><option value="">동/역</option></select>
    </div>
  </div>
</section>
<section class="filter-section">
  <div class="filter-container">
    {chips}
    <select id="sel-theme" class="theme-select" aria-label="테마보기">{''.join(theme_options)}</select>
    <button type="button" class="filter-btn" id="related-info">관련정보</button>
  </div>
</section>
<dialog class="info-dialog" id="info-dialog">
  <h2>관련정보</h2>
  <p>지역을 고르면 그 지역의 업체가 나오고, 세부지역을 고르면 가까운 동네부터 정렬됩니다.</p>
  <p>마사지는 매장 업체, 출장마사지는 출장·홈타이·홈케어 업체만 보여 줍니다. 테마보기는 스웨디시, 타이, 아로마처럼 종목으로 다시 거릅니다.</p>
  <p>예약은 업체 상세의 전화번호로 확인해 주세요.</p>
  <p><a href="/all/">전체 업체 보기</a></p>
  <form method="dialog"><button type="submit">닫기</button></form>
</dialog>"""


def page_shell(title, description, canonical, body, json_ld=None, robots="index,follow", og_image="", page="shop", region="", extra_head=""):
    ld = ""
    if json_ld:
        payload = json.dumps(json_ld, ensure_ascii=False).replace("<", "\\u003c")
        ld = f'<script type="application/ld+json">{payload}</script>'
    desc = escape(description)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#667eea">
<link rel="canonical" href="{escape(canonical)}">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{escape(canonical)}">
{f'<meta property="og:image" content="{escape(og_image)}">' if og_image else ''}
<meta name="twitter:card" content="{'summary_large_image' if og_image else 'summary'}">
<link rel="icon" href="/assets/favicon.svg">
<link rel="stylesheet" href="/assets/style.css?v=17">
{extra_head}
{ld}
</head>
<body data-page="{escape(page)}" data-region="{escape(region)}">
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="header" role="banner">
  <div class="header-content">
    <a class="logo" href="/">{LOGO}<span>{BRAND}</span></a>
    <div class="header-tools">
      <button type="button" class="icon-btn" id="open-search" aria-label="검색 창으로 이동">{SEARCH_ICON}</button>
      <a class="icon-btn" id="header-map-btn" href="/nearby/" aria-label="내주변">{PIN_ICON}</a>
      <button type="button" class="icon-btn" id="open-menu" aria-label="전체 메뉴 열기" aria-controls="side-menu" aria-expanded="false">{MENU_ICON}</button>
    </div>
  </div>
</header>
{side_menu()}
{"" if page in ("shop", "nearby", "login", "account", "signup", "inquiry", "notice", "event") else finder_bar(page, region)}
{body}
<footer class="foot">
  <div class="foot-inner">
    <p>{BRAND}는 지역별 마사지·출장 업체의 위치, 코스, 영업시간을 비교하는 안내 사이트입니다. 예약 전 전화로 시간을 확인해 주세요.</p>
    <p>© {BRAND}</p>
  </div>
</footer>
<script src="/assets/site.js?v=9" defer></script>
</body>
</html>
"""


def card_html(shop, eager=False):
    image = shop["images"][0] if shop["images"] else None
    label, klass = badge(shop)
    if image:
        loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
        media = (
            f'<img class="shop-image" src="{image["src"]}" alt="{escape(image["alt"])}" '
            f'width="{image["w"]}" height="{image["h"]}" {loading}>'
        )
    else:
        media = f'<div class="ph" aria-hidden="true">{escape(monogram(shop["name"]))}</div>'
    price = won_price(shop["price"])
    price_html = f'<div class="price"><span class="price-label">최저가</span>{escape(price)}</div>' if price else ""
    greeting = short_line(shop.get("slogan") or shop.get("description") or "")
    greet_html = f'<div class="greeting">{escape(greeting)}</div>' if greeting else ""
    address = short_line(shop.get("address") or shop.get("place") or "", 36)
    phone = shop.get("phone") or ""
    foot_bits = [bit for bit in (address, phone) if bit]
    foot = f'<div class="shop-address-info">{escape(" | ".join(foot_bits))}</div>' if foot_bits else ""
    query = " ".join(
        [shop["name"], shop["place"], shop["region"], shop["service"], shop["address"], shop["filename_text"]]
    )
    spots = "|".join(shop.get("spots") or [])
    kind = "outcall" if "outcall" in klass else "shop"
    located = shop_point(shop)
    latlng = f' data-lat="{located[0]}" data-lng="{located[1]}"' if located else ""
    return f"""<a class="massage-card" href="/shop/{shop["id"]}/" data-q="{escape(query)}" data-region="{escape(shop.get("region") or "")}" data-sub="{escape(shop.get("sub") or "")}" data-spots="{escape(spots)}" data-kind="{kind}"{latlng}>
  <div class="card-image">{media}<div class="image-overlay"><div class="{klass}">{label}</div></div></div>
  <div class="card-content">
    <div>
      <div class="name-row"><div class="shop-name">{escape(shop["name"])}</div><span class="shop-km"></span></div>
      <div class="shop-district">{escape(shop["place"])}{flag_html(shop.get("nations"))}</div>
    </div>
    {greet_html}
    <div class="card-footer">{price_html}{foot}</div>
  </div>
</a>"""


def build_shops():
    data = json.load(open(DATA, encoding="utf-8"))
    shops = []
    for item in data:
        fields = item.get("fields") or {}
        title = item.get("title") or ""
        address = (fields.get("위치") or "").strip()
        content = item.get("content") or ""
        price = first_price(content)
        if not price:
            continue
        region = region_from_address(address) or region_from_text(title)
        if not region:
            for source in (address, title):
                token = re.split(r"[\.\s]", (source or "").strip())
                token = token[0] if token else ""
                token = re.sub(r"(광역시|특별시|특별자치시|도)$", "", token)
                if token in REGION_WORDS and token != "기타":
                    region = token
                    break
                found = region_from_token(token)
                if found:
                    region = found
                    break
        if not region:
            region = region_from_title_places(title)
        if not region:
            region = "기타"
        name = shop_name(title) or title
        sub, spots = location_of(address, title, region)
        service = (fields.get("종목") or "").strip() or "마사지"
        nations = nations_in(staff_text(content))
        slogan = re.sub(r"\s+", " ", (fields.get("title") or "").strip())
        if len(slogan) > 80:
            slogan = slogan[:79].rstrip() + "…"
        shops.append({
            "id": str(item["id"]),
            "name": name,
            "title": title,
            "place": place_label(title, region),
            "region": region,
            "sub": sub,
            "spots": spots,
            "service": service,
            "guest": (fields.get("guest") or "").strip(),
            "phone": (fields.get("전화") or fields.get("예약") or "").strip(),
            "address": address,
            "hours": hours_of(content),
            "price": price,
            "slogan": slogan,
            "description": blurb(content, f"{place_label(title, region)} {name} 마사지 업체 정보입니다."),
            "content": content,
            "nations": nations,
            "images": [],
            "filename_text": "",
            "kind": "shop",
        })
    return shops


NAME_TAILS = ("아로마테라피", "스웨디시", "로미로미", "홈타이", "홈케어", "테라피", "마사지", "왁싱", "스파")


def same_shop_name(brand, shop_name):
    if len(brand) < 2 or len(shop_name) < 2:
        return False
    if brand == shop_name:
        return True
    for tail in NAME_TAILS:
        if brand == shop_name + tail or shop_name == brand + tail:
            return True
    return False


def brand_key(text):
    text = norm(text)
    for prefix in ("1인샵", "2인샵", "3인샵"):
        if text.startswith(prefix) and len(text) > len(prefix):
            return text[len(prefix):]
    return text


def name_matches_photo(brand, shop_name):
    brand = brand_key(brand)
    shop_name = norm(shop_name)
    if not brand or not shop_name:
        return False
    if brand == shop_name:
        return True
    return same_shop_name(brand, shop_name)


def photo_brand(filename):
    stem = os.path.splitext(filename)[0].strip()
    if "_" not in stem and re.search(r"[-－]", stem):
        stem = re.split(r"[-－]", stem, maxsplit=1)[-1]
    return stem.split("_")[-1]


def image_files():
    names = [
        name
        for name in os.listdir(IMG_SRC)
        if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]
    names.sort()
    return names


def attach_images(shops):
    """Repeat the photo pool until each shop has one image.

    40 photos and 200 shops means each photo is used 5 times.
    """
    files = image_files()
    if not files:
        return shops, 0, 0
    cursor = 0
    used = {name: 0 for name in files}
    total = len(files)
    for shop in shops:
        chosen = ""
        for _ in range(total):
            filename = files[cursor % total]
            cursor += 1
            if name_matches_photo(photo_brand(filename), shop.get("name") or ""):
                continue
            chosen = filename
            break
        if not chosen:
            chosen = files[cursor % total]
            cursor += 1
        shop["images"] = [chosen]
        used[chosen] += 1
    counts = list(used.values())
    return shops, total, (min(counts), max(counts)) if counts else (0, 0)

def finalize_images(shops):
    for shop in shops:
        total = len(shop["images"])
        prepared = []
        for index, filename in enumerate(shop["images"]):
            path = os.path.join(IMG_SRC, filename)
            width, height = jpeg_size(path)
            prepared.append({
                "file": filename,
                "src": img_url(filename),
                "alt": alt_for(shop, filename, index, total),
                "w": width,
                "h": height,
            })
        shop["images"] = prepared


def crumb(items):
    html = ['<nav class="crumb" aria-label="경로">']
    for index, (label, href) in enumerate(items):
        if index:
            html.append(" / ")
        if href:
            html.append(f'<a href="{href}">{escape(label)}</a>')
        else:
            html.append(escape(label))
    html.append("</nav>")
    return "".join(html)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def render_home(shops):
    featured = []
    seen = set()
    pictured = [shop for shop in shops if shop["images"]]
    for shop in pictured:
        if shop["region"] in seen:
            continue
        featured.append(shop)
        seen.add(shop["region"])
        if len(featured) == 30:
            break
    if len(featured) < 30:
        for shop in pictured:
            if shop in featured:
                continue
            featured.append(shop)
            if len(featured) == 30:
                break
    cards = "\n".join(card_html(shop, eager=(index == 0)) for index, shop in enumerate(featured))
    faq = [
        ("어느 지역 업체를 볼 수 있나요?", "서울, 경기, 인천을 비롯해 부산, 대구, 광주, 대전, 강원, 제주 등 등록된 지역의 업체를 지역 페이지에서 볼 수 있습니다."),
        ("카드에는 어떤 정보가 있나요?", "업체 이름, 지역, 종목, 대표 사진, 시작 가격이 있는 경우 그 가격을 보여 줍니다. 카드를 누르면 위치, 전화, 코스, 영업시간, 공지가 있는 상세 페이지로 이동합니다."),
        ("예약은 어떻게 하나요?", "상세 페이지의 전화번호로 문의하면 됩니다. 영업 중 통화가 어려우면 문자로 희망 시간을 남기는 업체가 많습니다."),
        ("사진이 없는 업체도 있나요?", "사진이 등록된 업체만 이미지를 보여 줍니다. 사진이 없어도 이름, 지역, 소개 글은 상세 페이지에서 확인할 수 있습니다."),
    ]
    faq_html = []
    faq_ld = []
    for question, answer in faq:
        faq_html.append(f"<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>")
        faq_ld.append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        })
    body = f"""<main id="main" class="main-content">
  <div class="results-header"><h1>{BRAND} 추천 샵</h1></div>
  <div class="massage-list">{cards}</div>
  <p><a href="/all/">전체 업체 보기</a></p>
  <div class="faq">
    <h2>이용 전에 자주 묻는 질문</h2>
    {''.join(faq_html)}
  </div>
</main>"""
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": BRAND,
            "url": ORIGIN + "/",
            "description": "지역별 마사지와 출장 업체 정보를 비교하는 사이트",
            "inLanguage": "ko-KR",
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_ld,
        },
    ]
    html = page_shell(
        f"{BRAND} | 지역별 마사지 업체 검색",
        "서울·경기·인천·부산 등 지역별 마사지, 스웨디시, 출장 업체의 위치·가격·영업시간과 사진을 비교하고 상세 페이지에서 바로 문의하세요.",
        ORIGIN + "/",
        body,
        ld,
        page="home",
    )
    write(os.path.join(OUT, "index.html"), html)


def render_listing(shops, title, description, canonical, h1, intro, active="", page="region"):
    cards = "\n".join(card_html(shop, eager=(index == 0 and shop["images"])) for index, shop in enumerate(shops))
    body = f"""<main id="main" class="main-content">
  {crumb([("홈", "/"), (h1, "")])}
  <div class="results-header"><h1>{escape(h1)}</h1></div>
  <p id="result-note" class="result-note">{escape(intro)}</p>
  <p id="empty" class="empty" hidden>조건에 맞는 업체가 없습니다. 다른 지역이나 이름으로 다시 찾아보세요.</p>
  <div class="massage-list">{cards}</div>
</main>"""
    return page_shell(title, description, canonical, body, page=page, region=active if page == "region" else "")


def render_regions(shops):
    grouped = {name: [] for name, _slug in REGIONS}
    for shop in shops:
        grouped.setdefault(shop["region"], []).append(shop)
    for name, slug in REGIONS:
        rows = grouped.get(name) or []
        if not rows:
            continue
        rows.sort(key=lambda shop: (0 if shop["images"] else 1, shop["name"]))
        intro = f"{name}에 등록된 마사지 업체 {len(rows)}곳입니다. 사진, 가격, 위치를 보고 카드를 누르면 코스와 영업시간, 연락처를 확인할 수 있습니다."
        html = render_listing(
            rows,
            f"{name} 마사지 업체 | {BRAND}",
            f"{name} 마사지·스웨디시·출장 업체 {len(rows)}곳의 위치, 가격, 영업시간을 비교하세요.",
            f"{ORIGIN}/region/{slug}/",
            f"{name} 마사지 업체",
            intro,
            active=name,
        )
        write(os.path.join(OUT, "region", slug, "index.html"), html)


def render_all(shops):
    rows = sorted(shops, key=lambda shop: (shop["region"], shop["name"]))
    html = render_listing(
        rows,
        f"전체 마사지 업체 | {BRAND}",
        "등록된 마사지·출장 업체를 이름, 지역, 종목으로 검색하고 상세 페이지에서 코스와 연락처를 확인하세요.",
        ORIGIN + "/all/",
        "전체 마사지 업체",
        f"등록 업체 {len(rows)}곳입니다. 검색창에 지역, 역, 업체 이름을 입력하면 카드가 바로 걸러집니다.",
        page="all",
    )
    write(os.path.join(OUT, "all", "index.html"), html)


def render_shop(shop):
    images = shop["images"]
    if images:
        first = images[0]
        hero = (
            f'<img class="heroimg" src="{first["src"]}" alt="{escape(first["alt"])}" '
            f'width="{first["w"]}" height="{first["h"]}" fetchpriority="high">'
        )
    else:
        hero = f'<div class="ph detail-hero" aria-hidden="true">{escape(monogram(shop["name"]))}</div>'
    shown_price = won_price(shop["price"]) or shop["price"]
    facts = []
    if shop["address"]:
        facts.append(f'<div class="fact"><span>주소</span><address>{escape(shop["address"])}</address></div>')
    if shop["hours"]:
        facts.append(f'<div class="fact"><span>영업시간</span><p>{escape(shop["hours"])}</p></div>')
    if shop["phone"]:
        facts.append(
            f'<div class="fact"><span>전화</span><p><a href="{tel_href(shop["phone"])}">{escape(shop["phone"])}</a></p></div>'
        )
    price_html = f'<p class="detail-price"><span class="price-label">최저가</span>{escape(shown_price)}</p>' if shown_price else ""
    call = ""
    if shop["phone"]:
        call = f'<a class="call" href="{tel_href(shop["phone"])}">전화 문의 {escape(shop["phone"])}</a>'
    gallery = ""
    if len(images) > 1:
        bits = []
        for image in images[1:]:
            bits.append(
                f'<img src="{image["src"]}" alt="{escape(image["alt"])}" width="{image["w"]}" height="{image["h"]}" loading="lazy" decoding="async">'
            )
        gallery = f'<div class="gallery">{"".join(bits)}</div>'
    region_slug = REGION_SLUG.get(shop["region"], "etc")
    url = f"{ORIGIN}/shop/{shop['id']}/"
    ld = {
        "@context": "https://schema.org",
        "@type": "HealthAndBeautyBusiness",
        "name": shop["name"],
        "url": url,
        "description": shop["description"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": shop["address"] or shop["place"],
            "addressRegion": shop["region"],
            "addressCountry": "KR",
        },
        "areaServed": shop["region"],
    }
    if shop["phone"]:
        ld["telephone"] = shop["phone"]
    if images:
        ld["image"] = [abs_url(image["src"]) for image in images]
    crumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": ORIGIN + "/"},
            {"@type": "ListItem", "position": 2, "name": shop["region"], "item": f"{ORIGIN}/region/{region_slug}/"},
            {"@type": "ListItem", "position": 3, "name": shop["name"], "item": url},
        ],
    }
    title = f"{shop['name']} | {shop['place']} {shop['service']}"
    if len(title) > 42:
        title = f"{shop['name']} | {shop['region']} 마사지"
    title = f"{title} | {BRAND}"
    district = " · ".join(bit for bit in (shop["place"], shop["service"]) if bit)
    body = f"""<main id="main" class="main-content detail">
  {crumb([("홈", "/"), (shop["region"], f"/region/{region_slug}/"), (shop["name"], "")])}
  <div class="detail-cover">{hero}</div>
  <section class="detail-card">
    <h1 class="detail-name">{escape(shop["name"])}</h1>
    <div class="shop-district">{escape(district)}{flag_html(shop.get("nations"))}</div>
    {price_html}
    <section class="fact-list">{''.join(facts) or '<div class="fact"><span>안내</span><p>상세 코스와 예약은 업체에 확인해 주세요.</p></div>'}</section>
    {call}
  </section>
  {gallery}
  <article class="prose">{format_content(shop["content"], review_section(shop), flag_html(shop.get("nations")))}</article>
  {near_section(shop)}
  {detail_actions(shop)}
</main>"""
    image_url = abs_url(images[0]["src"]) if images else ""
    html = page_shell(title, shop["description"], url, body, [ld, crumb_ld], og_image=image_url)
    write(os.path.join(OUT, "shop", shop["id"], "index.html"), html)
    return url


def shop_point(shop):
    for label in [shop.get("sub"), *(shop.get("spots") or [])]:
        if label in COORDS:
            lat, lng = COORDS[label]
            shift = sum(ord(ch) for ch in str(shop["id"]))
            lat += ((shift % 17) - 8) * 0.0011
            lng += (((shift // 17) % 17) - 8) * 0.0011
            return round(lat, 5), round(lng, 5)
    return None


def km_between(a, b):
    earth = 6371
    d_lat = math.radians(b[0] - a[0])
    d_lng = math.radians(b[1] - a[1])
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return 2 * earth * math.asin(min(1, math.sqrt(h)))


def km_label(km):
    if km < 1:
        return f"{max(1, round(km * 1000))}m"
    return f"{km:.1f}km"


def attach_near(shops, limit=5):
    located = []
    for shop in shops:
        point = shop_point(shop)
        shop["_point"] = point
        if point:
            located.append(shop)
    for shop in shops:
        origin = shop.get("_point")
        if not origin:
            shop["near"] = []
            continue
        ranked = []
        for other in located:
            if other["id"] == shop["id"]:
                continue
            ranked.append((km_between(origin, other["_point"]), other))
        ranked.sort(key=lambda item: item[0])
        shop["near"] = ranked[:limit]


def near_section(shop):
    rows = shop.get("near") or []
    if not rows:
        return ""
    cards = []
    for km, other in rows:
        image = other["images"][0] if other.get("images") else None
        if image:
            media = (
                f'<img src="{image["src"]}" alt="{escape(other["name"])}" '
                f'width="74" height="74" loading="lazy" decoding="async">'
            )
        else:
            media = f'<span class="near-ph" aria-hidden="true">{escape(monogram(other["name"]))}</span>'
        price = won_price(other.get("price")) or other.get("price") or ""
        price_html = f'<b>{escape(price)}</b>' if price else ""
        hours = (other.get("hours") or "").strip()
        hours_html = f'<small>{escape(hours)}</small>' if hours else ""
        cards.append(
            f'<a class="near-card" href="/shop/{other["id"]}/">{media}'
            f'<span><strong>{escape(other["name"])}</strong>'
            f'<em>{escape(other.get("place") or other.get("region") or "")} · {km_label(km)}</em>'
            f'{hours_html}{price_html}</span></a>'
        )
    return f'<section class="near-shops"><h2>가까운 업체</h2>{"".join(cards)}</section>'


def nearby_rows(shops):
    rows = []
    for shop in shops:
        point = shop_point(shop)
        if not point:
            continue
        label, klass = badge(shop)
        blob = " ".join([shop.get("service") or "", shop.get("name") or ""])
        image = shop["images"][0]["src"] if shop.get("images") else ""
        rows.append({
            "id": shop["id"],
            "name": shop["name"],
            "place": shop.get("place") or shop.get("region") or "",
            "addr": short_line(shop.get("address") or shop.get("place") or "", 42),
            "hours": short_line(shop.get("hours") or "", 32),
            "kind": "outcall" if "outcall" in klass else "shop",
            "badge": label,
            "one": 1 if "1인" in blob else 0,
            "home": 1 if ("홈케어" in blob or "홈타이" in blob) else 0,
            "q": short_line(blob, 80),
            "price": won_price(shop.get("price")) or shop.get("price") or "",
            "short": shop.get("price") or "",
            "img": image,
            "lat": point[0],
            "lng": point[1],
        })
    return rows


def render_nearby():
    body = """<main id="main" class="nearby-wrap">
  <p id="nearby-status" class="nearby-status"><span>지도를 준비하고 있습니다.</span><button type="button" id="nearby-gps">내 위치</button></p>
  <nav class="nearby-cats" id="nearby-cats">
    <button type="button" class="active" data-cat="">전체</button>
    <button type="button" data-cat="shop">마사지</button>
    <button type="button" data-cat="outcall">출장마사지</button>
    <button type="button" data-cat="one">1인샵</button>
    <button type="button" data-cat="home">홈케어</button>
  </nav>
  <div class="nearby-filters" id="nearby-radius">
    <button type="button" class="active" data-km="0">전체</button>
    <button type="button" data-km="1">1km</button>
    <button type="button" data-km="3">3km</button>
    <button type="button" data-km="5">5km</button>
    <button type="button" data-km="10">10km</button>
    <button type="button" id="nearby-theme-toggle">테마보기 <svg class="theme-caret" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" aria-hidden="true"><path fill="currentColor" d="M207 381.5L12.7 187.1c-9.4-9.4-9.4-24.6 0-33.9l22.7-22.7c9.4-9.4 24.5-9.4 33.9 0L224 284.5 378.7 130.5c9.4-9.3 24.5-9.3 33.9 0l22.7 22.7c9.4 9.4 9.4 24.6 0 33.9L241 381.5c-9.4 9.4-24.6 9.4-34 0z"/></svg></button>
  </div>
  <div class="nearby-themes" id="nearby-themes" hidden>
    <div class="nearby-theme-grid">
      <button type="button" class="active" data-theme="">전체</button>
      <button type="button" data-theme="스웨디시">스웨디시</button>
      <button type="button" data-theme="타이">타이마사지</button>
      <button type="button" data-theme="아로마">아로마마사지</button>
      <button type="button" data-theme="왁싱">왁싱</button>
      <button type="button" data-theme="중국">중국마사지</button>
      <button type="button" data-theme="발마사지">발마사지</button>
      <button type="button" data-theme="스파">스파</button>
    </div>
  </div>
  <div class="nearby-map-wrap">
    <div id="nearby-map" role="region" aria-label="내 주변 지도"></div>
    <div id="nearby-picker" class="nearby-picker" hidden>
      <div class="nearby-picker-title">이 위치의 업체</div>
      <div id="nearby-picker-list"></div>
    </div>
  </div>
  <div class="nearby-healing">
    <button type="button" class="healing-chip" id="nearby-healing" aria-pressed="false" aria-label="힐링샵만 보기">
      <span class="healing-chip-label">힐링샵</span>
      <span class="healing-switch" aria-hidden="true"><span class="healing-knob"></span></span>
    </button>
  </div>
  <section id="nearby-list" class="nearby-list"></section>
</main>
<script src="/assets/nearby.js?v=10"></script>"""
    html = page_shell(
        f"내주변 지도 | {BRAND}",
        f"현재 위치에서 가까운 마사지 업체를 지도에서 찾아보세요. {BRAND}",
        ORIGIN + "/nearby/",
        body,
        page="nearby",
    )
    write(os.path.join(OUT, "nearby", "index.html"), html)
    return ORIGIN + "/nearby/"


def render_auth(page, title, description, body):
    html = page_shell(
        f"{title} | {BRAND}",
        description,
        ORIGIN + f"/{page}/",
        body,
        robots="noindex,nofollow",
        page=page,
        extra_head='<script src="/assets/auth.js?v=1" defer></script>',
    )
    write(os.path.join(OUT, page, "index.html"), html)


def render_auth_pages():
    render_auth(
        "login",
        "관리자 로그인",
        f"{BRAND} 관리자 로그인",
        """<main id="main" class="auth-wrap">
  <form class="auth-card" id="login-form">
    <h1>관리자 로그인</h1>
    <p class="auth-lead">아이디 또는 이메일과 비밀번호를 입력해 주세요.</p>
    <label for="login">아이디 또는 이메일</label>
    <input id="login" name="login" autocomplete="username" required>
    <label for="password">비밀번호</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <p class="auth-msg" id="auth-msg" role="status"></p>
    <button class="auth-submit" type="submit">로그인</button>
  </form>
</main>""",
    )
    render_auth(
        "account",
        "관리자 계정",
        f"{BRAND} 관리자 계정",
        """<main id="main" class="auth-wrap">
  <form class="auth-card" id="account-form">
    <h1>관리자 계정</h1>
    <p class="auth-lead">아이디, 이메일, 비밀번호를 바꿀 수 있습니다. 비밀번호를 유지하려면 새 비밀번호를 비워 두세요.</p>
    <label for="login">아이디</label>
    <input id="login" name="login" autocomplete="username" required>
    <label for="email">이메일</label>
    <input id="email" name="email" type="email" autocomplete="email" required>
    <label for="current-password">현재 비밀번호</label>
    <input id="current-password" name="currentPassword" type="password" autocomplete="current-password" required>
    <label for="new-password">새 비밀번호</label>
    <input id="new-password" name="newPassword" type="password" autocomplete="new-password">
    <label for="confirm-password">새 비밀번호 확인</label>
    <input id="confirm-password" name="confirmPassword" type="password" autocomplete="new-password">
    <p class="auth-msg" id="auth-msg" role="status"></p>
    <button class="auth-submit" type="submit">저장</button>
    <button class="auth-logout" type="button" id="logout">로그아웃</button>
  </form>
</main>""",
    )


def render_menu_pages():
    pages = [
        (
            "signup",
            "회원가입",
            f"{BRAND} 회원가입",
            "noindex,nofollow",
            """<main id="main" class="auth-wrap">
  <section class="auth-card">
    <h1>회원가입</h1>
    <p class="auth-lead">일반 회원 가입은 준비 중입니다. 지금은 등록된 관리자만 로그인할 수 있습니다.</p>
    <p class="auth-lead">업체를 등록하려면 입점 문의로 남겨 주세요.</p>
    <p><a class="auth-submit" href="/login/">로그인</a></p>
    <p><a href="/inquiry/">입점 문의</a></p>
  </section>
</main>""",
        ),
        (
            "inquiry",
            "입점 문의",
            f"{BRAND} 업체 입점 문의",
            "index,follow",
            """<main id="main" class="auth-wrap">
  <form class="auth-card" id="inquiry-form">
    <h1>입점 문의</h1>
    <p class="auth-lead">업체명, 지역, 연락처를 남겨 주시면 메일로 이어집니다.</p>
    <label for="shop-name">업체명</label>
    <input id="shop-name" name="shopName" required>
    <label for="shop-region">지역</label>
    <input id="shop-region" name="region" required>
    <label for="shop-phone">연락처</label>
    <input id="shop-phone" name="phone" type="tel" required>
    <label for="shop-note">문의 내용</label>
    <textarea id="shop-note" name="note" rows="5" required></textarea>
    <p class="auth-msg" id="auth-msg" role="status"></p>
    <button class="auth-submit" type="submit">문의 보내기</button>
  </form>
</main>""",
        ),
        (
            "notice",
            "공지사항",
            f"{BRAND} 공지사항",
            "index,follow",
            f"""<main id="main" class="auth-wrap">
  <section class="auth-card">
    <h1>공지사항</h1>
    <article>
      <h2>사이트 안내</h2>
      <p>지역을 고르면 그 지역 업체가 나오고, 세부지역을 고르면 가까운 동네부터 정렬됩니다. 예약은 업체 상세의 전화번호로 확인해 주세요.</p>
    </article>
    <article>
      <h2>이름 변경</h2>
      <p>사이트 이름은 {BRAND}입니다.</p>
    </article>
  </section>
</main>""",
        ),
        (
            "event",
            "이벤트",
            f"{BRAND} 이벤트",
            "index,follow",
            """<main id="main" class="auth-wrap">
  <section class="auth-card">
    <h1>이벤트</h1>
    <p class="auth-lead">진행 중인 이벤트가 없습니다. 새 소식이 있으면 이 페이지에 올립니다.</p>
  </section>
</main>""",
        ),
    ]
    urls = []
    for page, title, description, robots, body in pages:
        html = page_shell(
            f"{title} | {BRAND}",
            description,
            ORIGIN + f"/{page}/",
            body,
            robots=robots,
            page=page,
        )
        write(os.path.join(OUT, page, "index.html"), html)
        if robots.startswith("index"):
            urls.append(ORIGIN + f"/{page}/")
    return urls


def render_404():
    body = f"""<main id="main" class="main-content">
    <h1>페이지를 찾지 못했습니다</h1>
    <p>주소가 바뀌었거나 없는 페이지입니다. 지역 목록에서 업체를 다시 찾아 주세요.</p>
    <p><a href="/">홈으로 이동</a></p>
    </main>"""
    html = page_shell(
        f"페이지를 찾지 못했습니다 | {BRAND}",
        f"요청한 페이지가 없습니다. {BRAND} 홈에서 지역별 업체를 찾아보세요.",
        ORIGIN + "/404.html",
        body,
        robots="noindex,follow",
        page="missing",
    )
    write(os.path.join(OUT, "404.html"), html)


def main():
    global LOCATION_TREE
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy2(os.path.join(WEB, "style.css"), os.path.join(OUT, "assets", "style.css"))
    shutil.copy2(os.path.join(WEB, "site.js"), os.path.join(OUT, "assets", "site.js"))
    shutil.copy2(os.path.join(WEB, "auth.js"), os.path.join(OUT, "assets", "auth.js"))
    shutil.copy2(os.path.join(WEB, "nearby.js"), os.path.join(OUT, "assets", "nearby.js"))
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#2f6f62"/><path fill="#f6efe4" d="M16 6c-3.6 4.4-6 7.2-6 10.6a6 6 0 0 0 12 0C22 13.2 19.6 10.4 16 6z"/></svg>"""
    write(os.path.join(OUT, "assets", "favicon.svg"), favicon)
    shops = build_shops()
    REVIEW_SEEN.clear()
    shops, photo_count, photo_repeats = attach_images(shops)
    finalize_images(shops)
    LOCATION_TREE = location_tree(shops)
    write(os.path.join(OUT, "assets", "locations.json"), json.dumps(LOCATION_TREE, ensure_ascii=False))
    write(
        os.path.join(OUT, "assets", "places.json"),
        json.dumps({name: [lat, lng] for name, (lat, lng) in COORDS.items()}, ensure_ascii=False),
    )
    flag_dir = os.path.join(OUT, "images", "flags")
    os.makedirs(flag_dir, exist_ok=True)
    for _name, code, filename in FLAGS:
        ext = "png" if filename.lower().endswith(".png") else "jpg"
        shutil.copy2(os.path.join(IMG_SRC, "국기", filename), os.path.join(flag_dir, f"{code}.{ext}"))
    copied = set()
    for shop in shops:
        for image in shop["images"]:
            if image["file"] in copied:
                continue
            shutil.copy2(os.path.join(IMG_SRC, image["file"]), os.path.join(OUT, "images", image["file"]))
            copied.add(image["file"])
    write(os.path.join(OUT, "assets", "nearby.json"), json.dumps(nearby_rows(shops), ensure_ascii=False, separators=(",", ":")))
    render_home(shops)
    render_regions(shops)
    render_all(shops)
    urls = [ORIGIN + "/", ORIGIN + "/all/", render_nearby()]
    for name, slug in REGIONS:
        if any(shop["region"] == name for shop in shops):
            urls.append(f"{ORIGIN}/region/{slug}/")
    attach_near(shops)
    for shop in shops:
        urls.append(render_shop(shop))
    render_auth_pages()
    urls.extend(render_menu_pages())
    render_404()
    sitemap = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        sitemap.append(f"<url><loc>{escape(url)}</loc></url>")
    sitemap.append("</urlset>")
    write(os.path.join(OUT, "sitemap.xml"), "\n".join(sitemap) + "\n")
    write(os.path.join(OUT, "robots.txt"), "User-agent: *\nAllow: /\nSitemap: https://outcallmassage.co.kr/sitemap.xml\n")
    write(os.path.join(OUT, "CNAME"), "outcallmassage.co.kr\n")
    write(os.path.join(OUT, ".nojekyll"), "")
    headers = """/assets/*
  Cache-Control: public, max-age=604800
/images/*
  Cache-Control: public, max-age=2592000
"""
    write(os.path.join(OUT, "_headers"), headers)
    print(
        f"shops={len(shops)} with_photos={sum(1 for shop in shops if shop['images'])} "
        f"photos={photo_count} repeat={photo_repeats[0]}-{photo_repeats[1]} copied={len(copied)} urls={len(urls)}"
    )


if __name__ == "__main__":
    main()
