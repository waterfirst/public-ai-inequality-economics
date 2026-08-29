#!/usr/bin/env python3
"""Download real Korean statistics (KOSIS + ECOS) for ISTANS paper calibration.

Deterministic, API-direct (no MCP). Saves CSV + a provenance manifest so every
figure in the paper can be traced to a statistics table id and query date.
Keys are read from the environment, never hard-coded.
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from datetime import date

OUT = os.path.join(os.path.dirname(__file__), "..", "public", "data", "kr_real")
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)

KOSIS_KEY = os.environ.get("KOSIS_API_KEY")
ECOS_KEY = os.environ.get("ECOS_API_KEY")
QUERY_DATE = date.today().isoformat()
manifest = []


def _get(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "istans-paper/1.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8")


def _kosis_call(tbl, prd_se, start, end, org, objs, extra=None):
    p = {"method": "getList", "apiKey": KOSIS_KEY, "format": "json", "jsonVD": "Y",
         "orgId": org, "tblId": tbl, "prdSe": prd_se, "startPrdDe": start,
         "endPrdDe": end, "itmId": "ALL"}
    p.update(objs)
    if extra:
        p.update(extra)
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do?" + urllib.parse.urlencode(p)
    data = json.loads(_get(url))
    if isinstance(data, dict) and data.get("err"):
        raise RuntimeError(f"err {data['err']}: {data.get('errMsg')}")
    return data


def kosis(tbl, prd_se, start, end, org="101", extra=None):
    """Try progressively simpler classification levels (tables differ in objL depth)."""
    last = None
    for objs in ({"objL1": "ALL", "objL2": "ALL"}, {"objL1": "ALL"}, {}):
        try:
            return _kosis_call(tbl, prd_se, start, end, org, objs, extra)
        except RuntimeError as e:
            last = e
            if "err 21" in str(e) or "err 20" in str(e):
                continue  # wrong variables -> fewer objL levels
            raise
    raise RuntimeError(f"KOSIS {tbl} {last}")


def kosis_chunked(tbl, prd_se, years, org="101"):
    """Fetch year-by-year to stay under the 40,000-cell cap (err 31)."""
    allrows = []
    for y in years:
        rows = kosis(tbl, prd_se, str(y), str(y), org=org)
        allrows.extend(rows)
        time.sleep(0.3)
    return allrows


def ecos(stat, cycle, start, end):
    url = f"https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_KEY}/json/kr/1/5000/{stat}/{cycle}/{start}/{end}"
    data = json.loads(_get(url))
    ss = data.get("StatisticSearch")
    if not ss:
        raise RuntimeError(f"ECOS {stat}: {json.dumps(data)[:200]}")
    return ss.get("row", [])


def save(name, rows, source, tbl_id, note=""):
    if not rows:
        print(f"  !! {name}: 0 rows")
        return
    path = os.path.join(OUT, name)
    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    manifest.append({"file": name, "rows": len(rows), "source": source,
                     "table_id": tbl_id, "query_date": QUERY_DATE, "note": note})
    print(f"  OK {name}: {len(rows)} rows -> {source}/{tbl_id}")


def main():
    if not KOSIS_KEY or not ECOS_KEY:
        sys.exit("KOSIS_API_KEY / ECOS_API_KEY missing in env")

    # 1) rho: industry employment (seasonally adjusted, monthly)
    try:
        save("kosis_industry_employment_DT_1DA9003S.csv",
             kosis("DT_1DA9003S", "M", "201301", "202512"),
             "KOSIS 경제활동인구조사", "DT_1DA9003S", "산업별 계절조정 취업자(천명)")
    except Exception as e:
        print("  ERR emp:", e)

    # 2) productivity index (industrial-production basis)
    for tbl, note, org in [
        ("DT_344N_1D8A_AA", "노동생산성지수(산업생산기준)", "344"),
        ("DT_344N_1D8B_DD", "제조업 지역별 노동생산성", "344"),
    ]:
        got = False
        for prd in ("Q", "M", "Y"):
            try:
                rows = kosis(tbl, prd, "2011", "2026", org=org)
                if rows:
                    save(f"kosis_productivity_{tbl}.csv", rows,
                         "KOSIS 노동생산성지수", tbl, f"{note} (prdSe={prd})")
                    got = True
                    break
            except Exception as e:
                last = e
        if not got:
            print(f"  ERR prod {tbl}: {last}")

    # 3) regional x industry employment (지역별고용조사) - chunk by year (40k cell cap)
    got = False
    for prd in ("H", "Y", "A"):
        try:
            rows = kosis_chunked("DT_1ES3C06S", prd, range(2013, 2026))
            if rows:
                save("kosis_region_industry_emp_DT_1ES3C06S.csv", rows,
                     "KOSIS 지역별고용조사", "DT_1ES3C06S", f"시군구/산업별 취업자 (prdSe={prd}, 연도별 청크)")
                got = True
                break
        except Exception as e:
            last = e
    if not got:
        print(f"  ERR region: {last}")

    # 4) ECOS: national income components (labor share) + income distribution
    try:
        save("ecos_national_income_200Y116.csv",
             ecos("200Y116", "A", "1990", "2025"),
             "ECOS 국민계정", "200Y116", "부문별 국민처분가능소득(피용자보수/영업잉여 -> 노동소득분배율)")
    except Exception as e:
        print("  ERR ecos income:", e)
    try:
        save("ecos_income_distribution_901Y112.csv",
             ecos("901Y112", "A", "2011", "2025"),
             "ECOS 소득분배지표", "901Y112", "지니계수 등 (분배지표 검증용)")
    except Exception as e:
        print("  ERR ecos dist:", e)

    with open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump({"generated": QUERY_DATE, "datasets": manifest}, f, ensure_ascii=False, indent=2)
    print(f"\nmanifest: {len(manifest)} datasets -> {OUT}/MANIFEST.json")


if __name__ == "__main__":
    main()
