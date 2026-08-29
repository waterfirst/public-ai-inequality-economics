#!/usr/bin/env python3
"""AI-and-polarization simulation driven by THREE real Korean data sources.

Population: NVIDIA Nemotron-Personas-Korea strata (age x sex x region x education x occupation).
Dynamics : the transparent transition model of scripts/07, unchanged.
Calibration (replaces the former synthetic constants):
  - occupational-reallocation speed  <- KOSIS DT_1DA9003S           (calibration.json rho_realloc)
  - AI-capital return (income share)  <- ECOS 200Y116               (calibration.json kappa_capital)
  - non-capital regional access penalty <- KOSIS DT_344N_1D8B_DD    (regional productivity ratio)

Only demographic *structure* comes from NVIDIA (fully synthetic, marginal-aligned);
economic states are assigned by transparent rules and disciplined by the KOSIS/ECOS anchors.
Results are model-conditional comparative statics, not forecasts.
"""
from __future__ import annotations
import importlib.util, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# ---- load script 07 as a module and reuse its dynamics + plots ----
spec = importlib.util.spec_from_file_location("pa07", ROOT / "scripts" / "07_public_ai_policy_simulation.py")
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod          # required so @dataclass can resolve the module
spec.loader.exec_module(mod)

DATA = ROOT / "public" / "data"
profile = json.loads((DATA / "nvidia-korea-profile.json").read_text(encoding="utf-8"))
calib = json.loads((ROOT / "calibration.json").read_text(encoding="utf-8"))
RHO = calib["params"]["rho_realloc"]["value"]
KAPPA = calib["params"]["kappa_capital"]["value"]

# ---- regional effective-access capacity from KOSIS manufacturing productivity ----
SIDO2KWON = {
    "서울": "수도권", "인천": "수도권", "경기": "수도권",
    "대전": "충청권", "세종": "충청권", "충북": "충청권", "충남": "충청권",
    "광주": "호남권", "전북": "호남권", "전남": "호남권", "전라북": "호남권", "전라남": "호남권",
    "부산": "영남권", "대구": "영남권", "울산": "영남권", "경북": "영남권", "경남": "영남권",
    "경상북": "영남권", "경상남": "영남권",
    "강원": "강원·제주", "제주": "강원·제주",
}


def region_capacity():
    df = pd.read_csv(DATA / "kr_real" / "kosis_productivity_DT_344N_1D8B_DD.csv")
    latest = df["PRD_DE"].max()
    df = df[df["PRD_DE"] == latest]
    name_col = "C1_NM" if "C1_NM" in df.columns else df.columns[1]
    kwon = {}
    for _, r in df.iterrows():
        nm = str(r.get(name_col, ""))
        val = pd.to_numeric(r.get("DT"), errors="coerce")
        if pd.isna(val):
            continue
        grp = next((SIDO2KWON[k] for k in SIDO2KWON if k in nm), None)
        if grp:
            kwon.setdefault(grp, []).append(float(val))
    means = {k: np.mean(v) for k, v in kwon.items()}
    top = max(means.values())
    cap = {k: v / top for k, v in means.items()}       # capital region ~ 1.0
    cap.setdefault("수도권", 1.0)
    return cap, latest


REGION_CAP, REG_PERIOD = region_capacity()
DEFAULT_CAP = float(np.mean(list(REGION_CAP.values())))

R_K_BASE = .065           # baseline AI-capital return (paper), capital stock scaled to real kappa
EDU_SKILL = {"무학": .10, "초등학교": .18, "중학교": .28, "고등학교": .42,
             "2~3년제 전문대학": .55, "4년제 대학교": .70, "대학원": .85, "미상": .40}

# occupation keyword -> (exposure, complementarity, employable, vuln_bias)
OCC_RULES = [
    ("무직", (.20, .20, 0.0, .55)),
    (("전문가", "기획", "마케팅", "안전원", "교육", "연구", "개발", "분석", "설계", "디자이너"),
     (.82, .80, 1.0, .05)),
    (("사무", "경리", "회계", "비서", "상담", "행정", "총무", "인사"),
     (.78, .55, 1.0, .10)),
    (("영업", "판매", "상점"), (.60, .45, 1.0, .18)),
    (("청소", "경비", "조리", "주방", "하역", "적재", "단순", "시설", "운전", "배달", "생산", "제조"),
     (.45, .25, 1.0, .30)),
]


def occ_traits(occ: str):
    for key, val in OCC_RULES:
        if isinstance(key, str):
            if key in occ:
                return val
        elif any(k in occ for k in key):
            return val
    return (.55, .45, 1.0, .20)          # default mid-exposure worker


def nv_population(seed, n):
    """Sample the agent cross-section from real NVIDIA Korean strata."""
    rng = np.random.default_rng(seed)
    strata = profile["strata"]
    counts = np.array([s["count"] for s in strata], dtype=float)
    idx = rng.choice(len(strata), size=n, p=counts / counts.sum())
    skill_base = np.empty(n); exposure = np.empty(n); comp = np.empty(n)
    employ0 = np.empty(n); vuln_bias = np.empty(n); rcap = np.empty(n)
    for j, i in enumerate(idx):
        s = strata[i]
        skill_base[j] = EDU_SKILL.get(s["education"], .40)
        e, c, emp, vb = occ_traits(s["occupation"])
        exposure[j], comp[j], employ0[j], vuln_bias[j] = e, c, emp, vb
        rcap[j] = REGION_CAP.get(s["region"], DEFAULT_CAP)
    # economic states, disciplined by education/occupation/region + idiosyncratic noise
    skill = np.clip(skill_base + .12 * rng.normal(size=n), 0.02, .98)
    resource = mod.norm(.55 * skill + .20 * comp + .25 * rcap + .10 * rng.normal(size=n))
    labor = np.exp(.45 * (resource - .5) * 2 + .30 * rng.normal(size=n)) * (0.35 + 0.65 * employ0)
    capital = np.exp(-2.15 + 1.6 * (resource - .5) + .55 * rng.normal(size=n))
    # scale capital stock so the initial AI-capital income share equals the real ECOS value (kappa)
    target = (KAPPA / (1 - KAPPA)) * labor.sum()
    capital *= target / (R_K_BASE * capital.sum())
    vulnerable = ((rng.random(n) < (vuln_bias + .15 * (1 - resource))) | (employ0 == 0)).astype(float)
    care_burden = vulnerable * rng.uniform(.35, .90, n)
    flexibility = np.clip(.42 * skill + .25 * comp + .20 * rcap + .13 * rng.random(n), 0, 1)
    premium = rng.random(n) < mod.sigmoid(-4.2 + 7.0 * resource)
    trust = np.clip((.55 + .2 * rng.normal(size=n)) * (0.6 + 0.4 * rcap), .05, .95)  # region access penalty
    return dict(labor=labor, skill=skill, capital=capital, resource=resource,
                vulnerable=vulnerable, care_burden=care_burden, exposure=exposure,
                flexibility=flexibility, premium=premium, trust=trust)


def check_capital_share(n=4000):
    """Verify the realized initial capital-income share matches the real ECOS kappa."""
    s = nv_population(0, n)
    cap_inc = R_K_BASE * s["capital"]
    share = float(cap_inc.sum() / (s["labor"].sum() + cap_inc.sum()))
    return share


def main():
    out = ROOT / "results" / "public_ai_real"
    out.mkdir(parents=True, exist_ok=True)
    quick = "--quick" in sys.argv

    mod.population = nv_population                      # inject real population
    realized_share = check_capital_share()
    env = mod.Environment(premium_gap=.45, rearrangement_speed=RHO, capital_return=R_K_BASE, feedback=.18)

    seeds = range(6 if quick else 24)
    n = 500 if quick else 1600
    finals, paths = [], []
    for seed in seeds:
        for p in mod.POLICIES:
            row, path, ledger = mod.simulate(seed, p, env=env, n=n, periods=15, keep_path=True)
            finals.append({**row, **ledger})
            path["seed"], path["policy"] = seed, p.name
            paths.append(path)
    f = pd.DataFrame(finals)
    t = pd.concat(paths, ignore_index=True)
    f.to_csv(out / "policy_runs.csv", index=False, encoding="utf-8-sig")
    t.to_csv(out / "policy_paths.csv", index=False, encoding="utf-8-sig")

    mod.trajectories(t, out / "01_policy_dynamics.png")
    mod.quintile_growth(f, out / "02_quintile_growth.png")
    mod.frontier(f, out / "03_policy_frontier.png")

    summary = f.groupby("policy").agg(
        delta_gini=("delta_gini", "mean"), delta_wolfson=("delta_wolfson", "mean"),
        delta_atkinson=("delta_atkinson_e1", "mean"), delta_ede=("delta_ede_e1", "mean"),
        fiscal_cost=("fiscal_cost", "mean"), delta_net_output=("delta_net_output", "mean"),
        delta_net_ede=("delta_net_ede_e1", "mean"), delta_middle=("delta_middle_share", "mean"),
        delta_skill_gap=("delta_skill_gap", "mean"), delta_capital=("delta_capital_top10", "mean"),
        delta_output=("delta_output", "mean"),
        delta_vulnerable_employment=("delta_vulnerable_employment", "mean"),
    ).reindex([p.name for p in mod.POLICIES])
    summary.to_csv(out / "policy_summary.csv", encoding="utf-8-sig")

    report = {
        "empirical_population": "NVIDIA Nemotron-Personas-Korea",
        "population_strata": len(profile["strata"]),
        "population_sample_size_source": profile["sampleSize"],
        "calibration": {"rho_realloc": RHO, "kappa_capital": KAPPA, "r_K_base": R_K_BASE,
                        "realized_initial_capital_share": round(realized_share, 4),
                        "region_capacity": {k: round(v, 3) for k, v in REGION_CAP.items()},
                        "region_period": REG_PERIOD},
        "baseline_runs": len(f),
        "policy_means": summary.round(6).to_dict(orient="index"),
        "max_budget_error": float(f.budget_error.abs().max()),
        "limit": "실측 3종(KOSIS·ECOS·NVIDIA)으로 보정한 메커니즘 실험; 현실 예측·인과효과 아님",
    }
    def _json(o):
        if hasattr(o, "item"):
            return o.item()
        raise TypeError(type(o))
    txt = json.dumps(report, ensure_ascii=False, indent=2, default=_json)
    (out / "report.json").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
