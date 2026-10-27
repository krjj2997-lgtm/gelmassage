# -*- coding: utf-8 -*-
"""Geocode shop street addresses once and cache them."""
import json
import os
import time
import urllib.parse
import urllib.request

import build_site as b

CACHE = os.path.join(b.ROOT, "gelmsg", "address_points.json")
UA = "outcallmassage.co.kr address cache (contact: krjj2997@gmail.com)"


def load_cache():
    if not os.path.isfile(CACHE):
        return {}
    with open(CACHE, encoding="utf-8") as handle:
        return json.load(handle)


def save_cache(cache):
    tmp = CACHE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(cache, handle, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, CACHE)


def lookup(query):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "format": "json",
        "limit": "1",
        "countrycodes": "kr",
        "q": query,
    })
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        rows = json.loads(response.read().decode("utf-8"))
    if not rows:
        return None
    lat = float(rows[0]["lat"])
    lng = float(rows[0]["lon"])
    if not (33.0 <= lat <= 39.6 and 124.0 <= lng <= 132.2):
        return None
    return [round(lat, 6), round(lng, 6)]


def main():
    shops = b.build_shops()
    queries = []
    seen = set()
    for shop in shops:
        query = b.map_address(shop).strip()
        if len(query) < 4 or query in seen:
            continue
        seen.add(query)
        queries.append(query)
    cache = load_cache()
    todo = [query for query in queries if query not in cache]
    print("unique", len(queries), "cached", len(queries) - len(todo), "todo", len(todo), flush=True)
    for index, query in enumerate(todo, start=1):
        try:
            point = lookup(query)
        except Exception as error:
            print("fail", index, query, error, flush=True)
            time.sleep(2)
            continue
        cache[query] = point
        if index % 20 == 0 or index == len(todo):
            save_cache(cache)
            print("saved", index, "/", len(todo), query, point, flush=True)
        else:
            print(index, query, point, flush=True)
        time.sleep(1.1)
    save_cache(cache)
    print("done", len(cache), flush=True)


if __name__ == "__main__":
    main()
