#!/usr/bin/env python3
"""Publication-grade experiments on the validated NVIDIA-broad Korean population.

Implements skill gates: paired Monte Carlo with 95% CIs, mechanism ablations,
and finite-size scaling. Uses the governance-validated broad-occupation profile
and KOSIS/ECOS calibration (see research-contract.md).
"""
from __future__ import annotations
import importlib.util, json, sys
from dataclasses import replace
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
spec = importlib.util.spec_from_file_location("pa07", ROOT / "scripts" / "07_public_ai_policy_simulation.py")
mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)

DATA = ROOT / "public" / "data"
profile = json.loads((DATA / "nvidia-korea-profile-broad.json").read_text(encoding="utf-8"))
calib = json.loads((ROOT / "calibration.json").read_text(encoding="utf-8"))
RHO = calib["params"]["rho_realloc"]["value"]
KAPPA = calib["params"]["kappa_capital"]["value"]
R_K_BASE = .065

# ---- 시도-level effective-access capacity from KOSIS regional productivity ----
def sido_capacity():
    df = pd.read_csv(DATA / "kr_real" / "kosis_productivity_DT_344N_1D8B_DD.csv")
    df = df[df["PRD_DE"] == df["PRD_DE"].max()]
    col = "C1_NM" if "C1_NM" in df.columns else df.columns[1]
    cap = {}
    for _, r in df.iterrows():
        v = pd.to_numeric(r.get("DT"), errors="coerce")
        if not pd.isna(v):
            cap[str(r[col])] = float(v)
    top = max(cap.values())
    return {k: v / top for k, v in cap.items()}, top

SIDO_CAP, _ = sido_capacity()
DEFAULT_CAP = float(np.mean(list(SIDO_CAP.values())))

EDU_SKILL = {"무학": .10, "초등학교": .18, "중학교": .28, "고등학교": .42,
             "2~3년제 전문대학": .55, "전문대학": .55, "4년제 대학교": .70, "대학교": .70,
             "대학원": .85, "미상": .40, "기타": .40}
# broad occupation -> (exposure, complementarity, employable, vuln_bias)
OCC = {
    "비경제활동": (.15, .15, 0.0, .55), "관리자": (.80, .85, 1.0, .05),
    "전문가·기술직": (.82, .80, 1.0, .05), "사무·행정": (.78, .60, 1.0, .10),
    "판매": (.60, .45, 1.0, .18), "서비스·돌봄": (.50, .35, 1.0, .22),
    "장치·기계·생산": (.45, .30, 1.0, .25), "기능·건설": (.45, .28, 1.0, .25),
    "단순노무": (.40, .20, 1.0, .35), "농림어업": (.35, .25, 1.0, .25),
    "기타": (.55, .45, 1.0, .20), "미상": (.55, .45, 1.0, .20),
}
def cap_for(region):
    return next((SIDO_CAP[k] for k in SIDO_CAP if k in str(region)), DEFAULT_CAP)


def nv_population(seed, n):
    rng = np.random.default_rng(seed)
    S = profile["strata"]; w = np.array([s["count"] for s in S], float)
    idx = rng.choice(len(S), size=n, p=w / w.sum())
    sk = np.empty(n); ex = np.empty(n); co = np.empty(n); em = np.empty(n); vb = np.empty(n); rc = np.empty(n)
    for j, i in enumerate(idx):
        s = S[i]
        sk[j] = EDU_SKILL.get(s["education"], .40)
        ex[j], co[j], em[j], vb[j] = OCC.get(s["occupation"], OCC["기타"])
        rc[j] = cap_for(s["region"])
    skill = np.clip(sk + .12 * rng.normal(size=n), .02, .98)
    resource = mod.norm(.55 * skill + .20 * co + .25 * rc + .10 * rng.normal(size=n))
    labor = np.exp(.9 * (resource - .5) + .30 * rng.normal(size=n)) * (0.35 + 0.65 * em)
    capital = np.exp(-2.15 + 1.6 * (resource - .5) + .55 * rng.normal(size=n))
    capital *= (KAPPA / (1 - KAPPA)) * labor.sum() / (R_K_BASE * capital.sum())
    vulnerable = ((rng.random(n) < (vb + .15 * (1 - resource))) | (em == 0)).astype(float)
    care_burden = vulnerable * rng.uniform(.35, .90, n)
    flexibility = np.clip(.42 * skill + .25 * co + .20 * rc + .13 * rng.random(n), 0, 1)
    premium = rng.random(n) < mod.sigmoid(-4.2 + 7.0 * resource)
    trust = np.clip((.55 + .2 * rng.normal(size=n)) * (0.6 + 0.4 * rc), .05, .95)
    return dict(labor=labor, skill=skill, capital=capital, resource=resource, vulnerable=vulnerable,
                care_burden=care_burden, exposure=ex, flexibility=flexibility, premium=premium, trust=trust)


mod.population = nv_population
ENV = mod.Environment(premium_gap=.45, rearrangement_speed=RHO, capital_return=R_K_BASE, feedback=.18)


def ci95(x):
    x = np.asarray(x, float); m = x.mean(); se = x.std(ddof=1) / np.sqrt(len(x))
    return round(float(m), 4), round(float(m - 1.96 * se), 4), round(float(m + 1.96 * se), 4)


def run_policies(seeds, n, policies=None):
    policies = policies or mod.POLICIES
    rows = []
    for seed in seeds:                       # common random numbers -> paired
        for p in policies:
            r, _, _ = mod.simulate(seed, p, env=ENV, n=n, periods=15, keep_path=False)
            rows.append(r)
    return pd.DataFrame(rows)


def main():
    out = ROOT / "results" / "rigor"; out.mkdir(parents=True, exist_ok=True)
    quick = "--quick" in sys.argv
    seeds = range(8 if quick else 40); n = 800 if quick else 1600
    report = {"population": "NVIDIA broad-occupation (validated)", "strata": len(profile["strata"]),
              "calibration": {"rho": RHO, "kappa": KAPPA}, "n": n, "n_seeds": len(list(seeds))}

    # --- Experiment 1: paired MC with 95% CIs ---
    df = run_policies(seeds, n)
    e1 = {}
    for p in mod.POLICIES:
        g = df[df.policy == p.name]
        e1[p.name] = {m: ci95(g[f"delta_{m}"]) for m in
                      ("wolfson", "gini", "net_ede_e1", "net_output", "vulnerable_employment", "middle_share")}
    report["exp1_paired_mc_ci"] = e1
    # H2 test: comprehensive vs market improvement CI (paired by seed)
    piv = df.pivot_table(index="seed", columns="policy", values="delta_wolfson")
    diff = piv["시장·고가AI"] - piv["공공AI 종합안"]        # >0 means comprehensive lowers polarization more
    report["H2_market_minus_comprehensive_dWolfson"] = ci95(diff)

    # --- Experiment 2: mechanism ablations on the comprehensive package ---
    comp = next(p for p in mod.POLICIES if p.name == "공공AI 종합안")
    ablations = {"full": comp,
                 "-education": replace(comp, education=0),
                 "-equalizing_design": replace(comp, equalizing_design=0),
                 "-capital_dividend": replace(comp, capital_dividend=0, worker_ownership=0),
                 "-care": replace(comp, care=0)}
    e2 = {}
    for label, pol in ablations.items():
        g = run_policies(seeds, n, [replace(pol, name=label)])
        e2[label] = {"dWolfson": ci95(g["delta_wolfson"]),
                     "dVulEmp": ci95(g["delta_vulnerable_employment"])}
    report["exp2_ablations"] = e2

    # --- Experiment 3: finite-size scaling (market vs comprehensive) ---
    e3 = {}
    for nn in ([300, 800] if quick else [250, 500, 1000, 2000]):
        g = run_policies(range(8 if quick else 20), nn,
                         [p for p in mod.POLICIES if p.name in ("시장·고가AI", "공공AI 종합안")])
        e3[str(nn)] = {p: ci95(g[g.policy == p]["delta_wolfson"])
                       for p in ("시장·고가AI", "공공AI 종합안")}
    report["exp3_finite_size"] = e3

    (out / "rigor_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
