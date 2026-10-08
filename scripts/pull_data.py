#!/usr/bin/env python3
"""Download TDLR electrician license subsets from data.texas.gov (Socrata).

Writes data/raw/tdlr_{EC,JE,ME}_*.json (paged, 50k per page). Idempotent:
existing complete pages are skipped; a final partial page is overwritten.
"""
import json, sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
RAW.mkdir(parents=True, exist_ok=True)
BASE = "https://data.texas.gov/resource/7358-krk7.json"
SUBTYPES = ["EC", "JE", "ME"]
PAGE = 50000
UA = {"User-Agent": "texas-electricians-directory build (contact: repo owner)"}


def fetch(url, tries=3):
    for t in range(tries):
        try:
            with urlopen(Request(url, headers=UA), timeout=300) as r:
                return json.load(r)
        except Exception as e:
            if t == tries - 1:
                raise
            print(f"  retry {t+1} after {e}", flush=True)
            import time
            time.sleep(5)


def main():
    only = sys.argv[1:] or SUBTYPES
    for sub in only:
        page = 0
        total = 0
        while True:
            out = RAW / f"tdlr_{sub}_{page}.json"
            if out.exists():
                try:
                    cur = json.load(open(out))
                except Exception:
                    cur = None
                if cur is not None and len(cur) < PAGE:
                    total += len(cur)
                    print(f"{sub}: page {page} already complete ({len(cur)} rows)")
                    break
            url = f"{BASE}?$limit={PAGE}&$offset={page*PAGE}&license_subtype={sub}&$order=license_number"
            print(f"{sub}: fetching page {page} ...", flush=True)
            rows = fetch(url)
            out.write_text(json.dumps(rows))
            total += len(rows)
            print(f"{sub}: page {page} -> {len(rows)} rows (running {total})")
            if len(rows) < PAGE:
                break
            page += 1
        print(f"{sub}: {total} rows total")


if __name__ == "__main__":
    main()