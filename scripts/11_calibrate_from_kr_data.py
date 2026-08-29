#!/usr/bin/env python3
"""Calibrate the paper's previously-synthetic parameters from real Korean data.

Reads the CSVs downloaded by 10_download_kr_data.py and writes calibration.json.
Every number is traceable to a KOSIS/ECOS table id (see MANIFEST.json).
This grounds parameters that the working paper had set by assumption:
  - kappa_capital  : capital income share (1 - labor share)   [ECOS 200Y116]
  - rho_realloc    : cross-industry employment reallocation    [KOSIS DT_1DA9003S]
  - prod_dispersion: dispersion of industry productivity growth [KOSIS DT_344N_1D8A_AA]
  - region_penalty : lagging/leading regional productivity gap  [KOSIS DT_344N_1D8B_DD]
"""
import csv, json, os, statistics as st
from collections import defaultdict

D = os.path.join(os.path.dirname(__file__), "..", "public", "data", "kr_real")
D = os.path.abspath(D)


def rows(name):
    with open(os.path.join(D, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


out = {"source_manifest": "public/data/kr_real/MANIFEST.json", "params": {}}

# --- 1) capital income share from ECOS national accounts (labor share complement)
ni = rows("ecos_national_income_200Y116.csv")
labor_share = {}
for yr in sorted({r["TIME"] for r in ni}):
    comp = next((fnum(r["DATA_VALUE"]) for r in ni
                 if r.get("ITEM_NAME1") == "피용자보수" and r["TIME"] == yr), None)
    fni = next((fnum(r["DATA_VALUE"]) for r in ni
                if r.get("ITEM_NAME1") == "요소비용국민소득" and r["TIME"] == yr), None)
    if comp and fni:
        labor_share[yr] = comp / fni
recent = [labor_share[y] for y in sorted(labor_share)[-5:]]
ls_recent = sum(recent) / len(recent)
out["params"]["kappa_capital"] = {
    "value": round(1 - ls_recent, 4),
    "labor_share_recent5_mean": round(ls_recent, 4),
    "labor_share_2015": round(labor_share.get("2015", float("nan")), 4),
    "labor_share_2024": round(labor_share.get("2024", float("nan")), 4),
    "source": "ECOS 200Y116 (피용자보수 / 요소비용국민소득)",
    "maps_to": "AI-capital income channel weight (paper r_K / capital share)",
}

# --- 2) reallocation intensity from industry employment (annual abs share change)
emp = [r for r in rows("kosis_industry_employment_DT_1DA9003S.csv")
       if r.get("ITM_NM") == "취업자"]
# aggregate to year x industry (mean of monthly), industry = C1_NM excluding totals
by_year_ind = defaultdict(lambda: defaultdict(list))
for r in emp:
    ind = r.get("C1_NM", "")
    if not ind or "계" in ind or ind.strip() == "전체":
        continue
    yr = r.get("PRD_DE", "")[:4]
    v = fnum(r.get("DT"))
    if yr and v is not None:
        by_year_ind[yr][ind].append(v)
year_ind = {y: {i: sum(vs) / len(vs) for i, vs in inds.items()}
            for y, inds in by_year_ind.items()}
years = sorted(year_ind)
realloc = []
for a, b in zip(years, years[1:]):
    ta, tb = sum(year_ind[a].values()), sum(year_ind[b].values())
    if not ta or not tb:
        continue
    inds = set(year_ind[a]) & set(year_ind[b])
    change = sum(abs(year_ind[b][i] / tb - year_ind[a][i] / ta) for i in inds) / 2
    realloc.append(change)
rho = sum(realloc) / len(realloc)
out["params"]["rho_realloc"] = {
    "value": round(rho, 4),
    "annual_series": [round(x, 4) for x in realloc],
    "years": f"{years[0]}-{years[-1]}",
    "n_industries": len(year_ind[years[-1]]),
    "source": "KOSIS DT_1DA9003S (산업별 계절조정 취업자)",
    "definition": "mean annual sum of |industry employment share change| / 2",
    "maps_to": "paper rho (occupational-reallocation speed)",
}

# --- 3) productivity growth dispersion (industry) from labour-productivity index
prd = rows("kosis_productivity_DT_344N_1D8A_AA.csv")
# find the growth-rate item if present, else compute yoy from index level
lvl = [r for r in prd if r.get("ITM_NM") and ("지수" in r["ITM_NM"] or "index" in r["ITM_NM"].lower())]
series = defaultdict(dict)
target = lvl or prd
for r in target:
    ind = r.get("C1_NM", "")
    per = r.get("PRD_DE", "")
    v = fnum(r.get("DT"))
    if ind and per and v is not None:
        series[ind][per] = v
growths = []
for ind, s in series.items():
    ps = sorted(s)
    for a, b in zip(ps, ps[1:]):
        if s[a]:
            growths.append((s[b] - s[a]) / s[a])
if growths:
    disp = st.pstdev(growths)
    out["params"]["prod_dispersion"] = {
        "value": round(disp, 4),
        "mean_growth": round(sum(growths) / len(growths), 4),
        "n_obs": len(growths),
        "source": "KOSIS DT_344N_1D8A_AA (노동생산성지수, 산업생산기준)",
        "maps_to": "heterogeneity of productivity gains across industries",
    }

# --- 4) regional productivity penalty (manufacturing, region gap)
reg = rows("kosis_productivity_DT_344N_1D8B_DD.csv")
reg_levels = defaultdict(list)
latest_per = max((r.get("PRD_DE", "") for r in reg), default="")
for r in reg:
    if r.get("PRD_DE") != latest_per:
        continue
    region = r.get("C1_NM") or r.get("C2_NM") or ""
    v = fnum(r.get("DT"))
    if region and v is not None:
        reg_levels[region].append(v)
reg_mean = {k: sum(v) / len(v) for k, v in reg_levels.items() if v}
if len(reg_mean) >= 3:
    hi = max(reg_mean.values())
    lo = min(reg_mean.values())
    out["params"]["region_penalty"] = {
        "value": round((hi - lo) / hi, 4),
        "period": latest_per,
        "n_regions": len(reg_mean),
        "top": round(hi, 2), "bottom": round(lo, 2),
        "source": "KOSIS DT_344N_1D8B_DD (제조업 지역별 노동생산성)",
        "maps_to": "paper non-capital-region effective-access penalty",
    }

with open(os.path.join(D, "..", "..", "..", "calibration.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(json.dumps(out, ensure_ascii=False, indent=2))
