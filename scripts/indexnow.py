#!/usr/bin/env python3
"""Ping IndexNow (Bing/Yandex/Seznam) with every sitemap URL.

Key file must exist at <host>/<key>.txt (root repo jdstager.github.io).
202 = accepted. Safe to re-run (re-pings are allowed; engines dedupe).
"""
import json, re, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.load(open(ROOT / "config/state.json"))
HOST = CONFIG["indexnow_host"]
KEY = CONFIG["indexnow_key"]
KEYLOC = CONFIG["indexnow_key_location"]
BASE = CONFIG["canonical_base"].rstrip("/")

paths = re.findall(r"<loc>/([^<]+)</loc>", (ROOT / "site/dist/sitemap.xml").read_text())
urls = [f"{BASE}/{p}" for p in paths]
if not urls:
    raise SystemExit("no urls in sitemap")
print(f"{CONFIG['site_name']}: submitting {len(urls)} urls, host={HOST}")
for i in range(0, len(urls), 1000):
    batch = urls[i:i+1000]
    body = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEYLOC, "urlList": batch}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=180) as r:
        print(f"  batch {i//1000}: {len(batch)} urls -> HTTP {r.status}")
print("indexnow done")
