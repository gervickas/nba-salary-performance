"""Download raw Basketball-Reference pages into a local gzip cache (data/cache/).

Sports Reference asks scrapers to stay under 20 requests/minute, so every
request is followed by a pause. Already-cached pages are skipped, so the
script can be re-run safely if it is interrupted.

Usage:  python src/download.py
"""
import gzip
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
BASE = "https://www.basketball-reference.com"

SEASONS = list(range(2016, 2027))          # 2015-16 ... 2025-26 (BR labels a season by its end year)
DRAFT_YEARS = list(range(1990, 2026))      # covers every player active 2016-2026
TEAMS = ["ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
         "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
         "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
PAUSE = 3.3


def jobs():
    yield "salary_cap.html.gz", f"{BASE}/contracts/salary-cap-history.html"
    for yr in SEASONS:
        yield f"per_game_{yr}.html.gz", f"{BASE}/leagues/NBA_{yr}_per_game.html"
        yield f"advanced_{yr}.html.gz", f"{BASE}/leagues/NBA_{yr}_advanced.html"
    for yr in DRAFT_YEARS:
        yield f"draft_{yr}.html.gz", f"{BASE}/draft/NBA_{yr}.html"
    for yr in SEASONS:
        for team in TEAMS:
            yield f"team_{team}_{yr}.html.gz", f"{BASE}/teams/{team}/{yr}.html"


def fetch(session, url):
    for attempt in range(4):
        r = session.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.text
        if r.status_code == 429:
            wait = 120 * (attempt + 1)
            print(f"  429 rate-limited, sleeping {wait}s", flush=True)
            time.sleep(wait)
            continue
        print(f"  HTTP {r.status_code} for {url}", flush=True)
        return None
    return None


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [(f, u) for f, u in jobs() if not (CACHE / f).exists()]
    print(f"{len(todo)} pages to download", flush=True)
    session = requests.Session()
    for i, (fname, url) in enumerate(todo, 1):
        html = fetch(session, url)
        if html is not None:
            with gzip.open(CACHE / fname, "wt", encoding="utf-8") as fh:
                fh.write(html)
        print(f"[{i}/{len(todo)}] {fname} {'ok' if html else 'FAILED'}", flush=True)
        time.sleep(PAUSE)
    print("done", flush=True)


if __name__ == "__main__":
    sys.exit(main())
