#!/usr/bin/env python3
"""TDLR raw pulls -> clean entities + coverage report.

Inputs:  data/raw/tdlr_{ME,JE,EC}_*.json  (Socrata export, paged)
Outputs: data/clean/licenses_active_tx.csv.gz
         data/clean/businesses.csv
         data/clean/city_counts.csv
         data/clean/coverage_report.json (stdout too)

As-of date: today at run time. Rows whose license has expired are dropped
(methodology page will state the as-of date per build).
"""
import csv, glob, gzip, json, re, sys, time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw"
CLEAN = ROOT / "data/clean"
CLEAN.mkdir(parents=True, exist_ok=True)
TODAY = date.today()

# Filter on license_TYPE, not subtype: TDLR reuses "ME" for cosmetology
# fields (Mini Establishment / Manicurist-Esthetician), so subtype is not
# unique. Only these (type, rank) pairs enter the directory.
ELEC_TYPES = {
    "Master Electrician": 3,
    "Electrical Contractor": 2,
    "Journeyman Electrician": 1,
    "Master Sign Electrician": 2,
    "Journeyman Sign Electrician": 1,
    "Maintenance Electrician": 1,
    "Electrical Sign Contractor": 2,
    "Journeyman Industrial Electrician": 1,
    "Journeyman Lineman Electrician": 1,
}

CSZ_RE = re.compile(r"^(.+?)\s+([A-Z]{2})\s+(\d{5})(?:-\d{4})?$")


def parse_exp(s):
    try:
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except Exception:
        return None


def norm_name(s):
    s = re.sub(r"\s+", " ", (s or "").strip().upper())
    s = s.replace(",", " ").replace(".", " ").replace("&", "&")
    s = re.sub(r"\b(LLC|L L C|INC|INCORPORATED|CO|COMPANY|LTD|THE)\b", lambda m: m.group(1), s)
    s = re.sub(r"[^A-Z0-9& ]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def biz_key(row, city_norm, line1):
    name = norm_name(row.get("business_name"))
    return f"{name}::{line1.upper()}::{city_norm}"


def main():
    stats = {
        "rows_read": 0, "kept_active_tx": 0, "dropped_inactive": 0,
        "dropped_out_of_state": 0, "dropped_no_city": 0, "by_subtype": {},
    }
    licenses = []  # one row per license entity
    city_norm_map = {}

    def norm_city(c):
        k = c.upper().replace("'", "")
        k = re.sub(r"\s+", " ", k).strip()
        if k not in city_norm_map:
            city_norm_map[k] = k
        return city_norm_map[k]

    for path in sorted(RAW.glob("tdlr_*.json")):
        try:
            rows = json.load(open(path))
        except Exception as e:
            print(f"WARN unreadable {path}: {e}", file=sys.stderr)
            continue
        for r in rows:
            stats["rows_read"] += 1
            lt = (r.get("license_type") or "").strip()
            if lt not in ELEC_TYPES or "apprentice" in lt.lower():
                stats.setdefault("skipped_non_elec", 0)
                stats["skipped_non_elec"] += 1
                continue
            sub = (r.get("license_subtype") or "").strip()
            exp = parse_exp(r.get("license_expiration_date_mmddccyy", ""))
            if exp is None or exp < TODAY:
                stats["dropped_inactive"] += 1
                continue
            county_biz = (r.get("business_county") or "").strip().upper()
            csz = (r.get("business_city_state_zip") or "").strip()
            m = CSZ_RE.match(csz)
            if county_biz == "OUT OF STATE" or (m and m.group(2) != "TX"):
                stats["dropped_out_of_state"] += 1
                continue
            if m:
                city_norm, state, zip5 = norm_city(m.group(1)), m.group(2), m.group(3)
            else:
                # no parseable business city — keep license, mark unmapped
                city_norm, state, zip5 = "", "TX", ""
                stats["dropped_no_city"] += 1
            line1 = re.sub(r"\s+", " ", (r.get("business_address_line1") or "").strip().upper())
            lic = {
                "subtype": sub,
                "license_type": lt,
                "license_number": (r.get("license_number") or "").strip(),
                "business_name_raw": (r.get("business_name") or "").strip(),
                "business_name_norm": norm_name(r.get("business_name")),
                "line1": line1,
                "city": city_norm,
                "zip": zip5,
                "county": county_biz,
                "phone": re.sub(r"\D", "", r.get("business_telephone") or ""),
                "owner_name": (r.get("owner_name") or "").strip(),
                "exp_date": exp.isoformat(),
                "ce_flag": (r.get("continuing_education_flag") or "").strip(),
                "latlon": None,
            }
            geo = r.get("business_mailing")
            if isinstance(geo, dict):
                c = geo.get("coordinates")
                if c and len(c) == 2:
                    lic["latlon"] = [c[0], c[1]]  # [lon, lat]
            stats["kept_active_tx"] += 1
            stats["by_subtype"][sub] = stats["by_subtype"].get(sub, 0) + 1
            licenses.append(lic)

    # dedupe licenses (same license_number may span export pages)
    seen = {}
    for l in licenses:
        seen[l["license_number"] + "|" + l["subtype"]] = l
    licenses = list(seen.values())

    # business entity rollup
    biz = {}
    for l in licenses:
        if not l["city"]:
            continue  # person licenses without city are kept in licenses file only
        k = biz_key(l, l["city"], l["line1"])
        e = biz.get(k)
        if e is None:
            e = {
                "key": k, "name": l["business_name_raw"], "name_norm": l["business_name_norm"],
                "line1": l["line1"], "city": l["city"], "zip": l["zip"], "county": l["county"],
                "phone": "", "latlon": None, "classes": [], "lics": [], "exp_max": "0",
            }
        e["lics"].append({"n": l["license_number"], "class": l["license_type"], "sub": l["subtype"], "exp": l["exp_date"]})
        if l["phone"] and not e["phone"]:
            e["phone"] = l["phone"]
        if l["latlon"] and e["latlon"] is None:
            e["latlon"] = l["latlon"]
        if ELEC_TYPES.get(l["license_type"], 0) > 0:
            e.setdefault("class_set", set()).add(l["license_type"])
        e["exp_max"] = max(e["exp_max"], l["exp_date"])
        biz[k] = e
    entities = []
    for e in biz.values():
        e["classes"] = sorted(e.pop("class_set"))
        e["is_contractor"] = any(x == "Electrical Contractor" for x in e["classes"])
        e["has_master"] = any(x == "Master Electrician" for x in e["classes"])
        entities.append(e)

    # coverage report
    city_counts = {}
    for e in entities:
        city_counts.setdefault(e["city"], 0)
        city_counts[e["city"]] += 1
    city_sorted = sorted(city_counts.items(), key=lambda x: -x[1])
    for c, n in city_sorted[:40]:
        print(f"{n:6d}  {c}")
    coverage = {
        "as_of": TODAY.isoformat(),
        "stats": stats,
        "unique_licenses": len(licenses),
        "unique_business_entities": len(entities),
        "cities": len(city_counts),
        "cities_ge3": sum(1 for _, n in city_counts.items() if n >= 3),
        "cities_ge5": sum(1 for _, n in city_counts.items() if n >= 5),
        "top40": city_sorted[:40],
    }
    (CLEAN / "coverage_report.json").write_text(json.dumps(coverage, indent=1))

    out = CLEAN / "licenses_active_tx.csv.gz"
    with gzip.open(out, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(licenses[0].keys()))
        w.writeheader()
        w.writerows(licenses)
    be = CLEAN / "businesses.csv"
    with open(be, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(entities[0].keys()))
        w.writeheader()
        w.writerows(entities)
    with open(CLEAN / "city_counts.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["city", "businesses"])
        w.writerows(city_sorted)

    print(json.dumps({k: v for k, v in coverage.items() if k != "top40"}, default=str, indent=1))


if __name__ == "__main__":
    main()