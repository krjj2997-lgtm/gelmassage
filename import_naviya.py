# -*- coding: utf-8 -*-
"""나비야 업체를 기존 마켓 양식으로 넣는다. 전화번호가 같으면 건너뛴다."""
import json
import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
MARKET = os.path.join(ROOT, "gelmsg", "market_full.json")
NAVI = os.path.join(ROOT, "naviya", "b49_full.json")
IMG = os.path.join(ROOT, "images")
OUT_DIR = os.path.join(IMG, "naviya-images")

ORNAMENT = "ꕮ ˚ ❀ {label} ❀ ˚ ꕮ"
GREETINGS = [
    "찾아주셔서 감사합니다.\n{place} {name}입니다.\n그날의 컨디션을 살피며 편히 쉬실 수 있게 관리하겠습니다.",
    "안녕하세요. {place} {name}입니다.\n쌓인 피로를 잠시 내려놓을 수 있도록 차분히 안내해 드립니다.",
    "{place}에 있는 {name}입니다.\n처음 오셔도 부담 없이 문의하시고, 원하시는 만큼 편히 쉬어 가세요.",
    "반갑습니다. {name}입니다.\n{place}에서 세심한 손길로 몸과 마음이 놓이는 시간을 준비했습니다.",
    "{name}에 와 주셔서 고맙습니다.\n{place}에서 예약 후 방문해 주시면 더 정확하게 안내해 드립니다.",
]
EXTRAS = [
    ("한국인", "한국인 관리사가 케어를 맡습니다."),
    ("1인", "한 분씩 따로 관리하는 시간입니다."),
    ("커플", "함께 오시는 분도 예약으로 안내합니다."),
    ("여성전문", "여성 고객 관리를 중심으로 운영합니다."),
    ("남녀", "남녀 모두 예약으로 받습니다."),
]


def digits(value):
    return re.sub(r"\D", "", value or "")


def heading(line):
    compact = re.sub(r"[^가-힣]", "", line or "")
    labels = {
        "프로그램": "프로그램",
        "관리사님": "관리사님",
        "관리사": "관리사님",
        "오시는길": "오시는길",
        "영업시간": "영업시간",
        "공지안내": "공지안내",
    }
    return labels.get(compact, "")


def noise(line):
    text = line.strip()
    if not text or "나비야" in text:
        return True
    if re.search(r"0\s*1\s*0", text) and len(digits(text)) >= 10:
        return True
    return False


def split_body(content):
    intro = []
    sections = {key: [] for key in ("프로그램", "관리사님", "오시는길", "영업시간", "공지안내")}
    current = None
    for raw in (content or "").splitlines():
        label = heading(raw)
        if label:
            current = label
            continue
        if noise(raw):
            continue
        if current:
            sections[current].append(raw.strip())
        else:
            intro.append(raw.strip())
    return intro, sections


def shop_bits(title):
    match = re.search(r"[〔｛\[]\s*(.+?)\s*[〕｝\]]", title or "")
    name = re.sub(r"\s+", " ", match.group(1)).strip() if match else ""
    place = re.split(r"[〔｛\[]", title or "", maxsplit=1)[0].strip(" .")
    place = re.sub(r"\s+", " ", place)
    return place or "전국", name or place or "업체"


def greeting(place, name, blob, index):
    lines = [GREETINGS[index % len(GREETINGS)].format(place=place, name=name)]
    for key, sentence in EXTRAS:
        if key in blob:
            lines.append(sentence)
    return "\n".join(lines)


def notice_lines(lines):
    blob = "\n".join(lines)
    out = []
    if "예약" in blob:
        out.append("* 방문 전 예약해 주시면 안내가 더 정확합니다.")
    if "선불" in blob or "결제" in blob:
        out.append("* 입실 후에는 먼저 결제해 주세요.")
    if "10분" in blob:
        out.append("* 약속 시간에서 10분을 넘기시면 예약이 취소될 수 있습니다.")
    if "휴무" in blob or "마감" in blob or "폰" in blob:
        out.append("* 전화가 연결되지 않으면 당일 마감이거나 휴무입니다.")
    if "건전" in blob or "합법" in blob:
        out.append("* 건전한 범위의 관리만 진행합니다.")
    if not out:
        out.append("* 코스와 방문 시간은 예약 때 확인해 주세요.")
    return out


def services(program):
    text = " ".join(program)
    found = []
    for label in ("스웨디시", "아로마", "타이", "로미로미", "왁싱", "스포츠", "림프", "건식", "습식", "피부관리"):
        if label in text and label not in found:
            found.append(label)
    return " ".join(found[:4]) or "마사지"


def address_line(sections, guess):
    lines = [line for line in sections["오시는길"] if line]
    street = ""
    for line in lines:
        if re.search(r"(시|군|구|동|읍|면|로|길)", line):
            street = line
            break
    street = street or (lines[0] if lines else "")
    guess = (guess or "").strip()
    if guess and guess not in street:
        street = f"{street} / {guess}" if street else guess
    return re.sub(r"\s+", " ", street).strip()


def block(label, lines):
    body = "\n".join(line for line in lines if line.strip())
    return f"{ORNAMENT.format(label=label)}\n{body}" if body else ""


def photo_brand(filename):
    stem = os.path.splitext(filename)[0].strip()
    if "_" not in stem and re.search(r"[-－]", stem):
        stem = re.split(r"[-－]", stem, maxsplit=1)[-1]
    return stem.split("_")[-1]


def main():
    market = json.load(open(MARKET, encoding="utf-8"))
    kept = []
    for item in market:
        images = item.get("images") or []
        if images and isinstance(images[0], str) and images[0].startswith("naviya-images/"):
            continue
        kept.append(item)
    market = kept
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    navi = json.load(open(NAVI, encoding="utf-8"))
    have = set()
    ids = set()
    for item in market:
        fields = item.get("fields") or {}
        phone = digits(fields.get("전화") or fields.get("예약") or "")
        if len(phone) >= 10:
            have.add(phone)
        ids.add(str(item.get("id")))
    photos = sorted(
        name for name in os.listdir(IMG)
        if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    )
    os.makedirs(OUT_DIR, exist_ok=True)
    added = []
    seen = set()
    skipped_dup = skipped_price = 0
    cursor = 0
    for item in navi:
        phone = digits((item.get("fields") or {}).get("전화") or "")
        if len(phone) < 10 or phone in have or phone in seen:
            skipped_dup += 1
            continue
        content = item.get("content") or ""
        if not re.search(r"\d+\s*만", content) and not re.search(r"\d{4,7}\s*원", content):
            skipped_price += 1
            continue
        seen.add(phone)
        place, name = shop_bits(item.get("title") or "")
        intro, sections = split_body(content)
        blob = "\n".join(intro + sections["프로그램"] + sections["관리사님"] + sections["공지안내"])
        parts = [
            f"{place} {name}".strip(),
            (item.get("fields") or {}).get("위치추정") or "",
            "",
            greeting(place, name, blob, len(added)),
            "",
            block("프로그램", sections["프로그램"]),
            block("관리사님", sections["관리사님"]),
            block("오시는길", sections["오시는길"]),
            block("영업시간", sections["영업시간"]),
            block("공지안내", notice_lines(sections["공지안내"] or intro)),
        ]
        body = "\n".join(part for part in parts if part is not None).strip() + "\n"
        shop_id = str(item["id"])
        if shop_id in ids:
            shop_id = "nv" + shop_id
        ids.add(shop_id)
        chosen = ""
        for _ in range(len(photos) or 1):
            if not photos:
                break
            filename = photos[cursor % len(photos)]
            cursor += 1
            if photo_brand(filename) == re.sub(r"\s+", "", name):
                continue
            chosen = filename
            break
        images = []
        if chosen:
            ext = os.path.splitext(chosen)[1].lower() or ".jpg"
            dest = os.path.join(OUT_DIR, f"{shop_id}{ext}")
            shutil.copy2(os.path.join(IMG, chosen), dest)
            images = [f"naviya-images/{shop_id}{ext}"]
        phone_text = (item.get("fields") or {}).get("전화") or ""
        added.append({
            "id": shop_id,
            "url": item.get("url") or "",
            "title": f"{place} 〔 {name} 〕",
            "fields": {
                "종목": services(sections["프로그램"]),
                "guest": "여성전용" if "여성전문" in blob else "",
                "위치": address_line(sections, (item.get("fields") or {}).get("위치추정") or ""),
                "상호": f"{place} ｛ {name} ｝",
                "전화": phone_text,
                "title": f"{place} {name} 관리 안내",
                "예약": phone_text,
            },
            "content": body,
            "images": images,
        })
    market.extend(added)
    with open(MARKET, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(market, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"added={len(added)} dup={skipped_dup} no_price={skipped_price} market={len(market)}")


if __name__ == "__main__":
    main()
