#!/usr/bin/env python3
"""공공·소버린 AI, 공교육, 돌봄, 프리미엄 AI의 분배효과 모의실험.

수치는 모두 인공 상태방정식의 결과이며 현실 정책효과 추정치가 아니다.
"""
from __future__ import annotations

import argparse, importlib.util, json, sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from polarization_experiment.metrics import gini, wolfson_polarization  # noqa: E402

plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False


@dataclass(frozen=True)
class Environment:
    premium_gap: float = .45
    rearrangement_speed: float = .045
    capital_return: float = .065
    feedback: float = .18


@dataclass(frozen=True)
class Policy:
    name: str
    public_access: float
    public_quality: float
    education: float
    care: float
    capital_dividend: float
    worker_ownership: float
    equalizing_design: float
    trust: float


POLICIES = (
    Policy("시장·고가AI", .10, .30, 0, 0, 0, 0, 0, .65),
    Policy("전국민 공공AI", .98, .72, 0, 0, 0, 0, .10, .82),
    Policy("공공AI+공교육", .98, .82, .065, 0, 0, 0, .25, .86),
    Policy("공공AI+돌봄", .98, .78, 0, .075, 0, 0, .10, .88),
    Policy("공공AI 종합안", .98, .90, .065, .075, .22, .08, .35, .92),
    Policy("공공AI 실패", .90, .42, .018, .025, 0, 0, .04, .38),
)
COLORS = {p.name: c for p, c in zip(POLICIES, ["#B42318", "#2E90FA", "#F79009", "#7A5AF8", "#039855", "#667085"])}


def sigmoid(x): return 1 / (1 + np.exp(-np.clip(x, -30, 30)))


def norm(x):
    lo, hi = np.min(x), np.max(x)
    return np.zeros_like(x) if hi == lo else (x - lo) / (hi - lo)


def population(seed, n):
    rng = np.random.default_rng(seed); z = rng.normal(size=n)
    labor = np.exp(.42*z + .30*rng.normal(size=n))
    skill = sigmoid(.85*z + .65*rng.normal(size=n))
    capital = np.exp(-2.15 + .82*z + .55*rng.normal(size=n))
    resource = norm(.58*np.log(labor)+.25*skill+.17*np.log1p(capital))
    vulnerable = (rng.random(n) < (.08 + .28*(1-resource))).astype(float)
    care_burden = vulnerable * rng.uniform(.35, .90, n)
    exposure = rng.beta(2.1, 2.1, n)
    flexibility = np.clip(.42*skill + .25*resource + .33*rng.random(n), 0, 1)
    premium = rng.random(n) < sigmoid(-4.2 + 7.0*resource)
    trust = np.clip(.55 + .2*rng.normal(size=n), .05, .95)
    return dict(labor=labor, skill=skill, capital=capital, resource=resource,
                vulnerable=vulnerable, care_burden=care_burden, exposure=exposure,
                flexibility=flexibility, premium=premium, trust=trust)


def metrics(s, income, employed, initial_income):
    low = s["resource"] <= .2; high = s["resource"] >= .8; vulnerable = s["vulnerable"] > 0
    median = np.median(income)
    quant = pd.qcut(pd.Series(s["resource"]), 5, labels=False, duplicates="drop").to_numpy()
    growth = np.log(income / initial_income)
    ede=float(np.exp(np.mean(np.log(income)))); mean_income=float(np.mean(income))
    result = {
        "gini": gini(income), "wolfson": wolfson_polarization(income),
        "atkinson_e1": float(1-ede/mean_income), "ede_e1": ede,
        "middle_share": float(np.mean((income >= .75*median) & (income <= 1.25*median))),
        "bottom20_income": float(np.mean(income[low])), "top20_income": float(np.mean(income[high])),
        "employment": float(np.mean(employed)),
        "vulnerable_employment": float(np.mean(employed[vulnerable])) if vulnerable.any() else 0,
        "skill_gap": float(np.mean(s["skill"][high])-np.mean(s["skill"][low])),
        "capital_top10": float(np.sum(np.sort(s["capital"])[-max(1,len(income)//10):])/np.sum(s["capital"])),
        "output": mean_income,
    }
    for q in range(5): result[f"growth_q{q+1}"] = float(np.mean(growth[quant == q]))
    return result


def simulate(seed, policy, env=Environment(), n=1400, periods=12, keep_path=False):
    rng=np.random.default_rng(seed+91827); s=population(seed,n)
    initial_state={k:v.copy() for k,v in s.items()}
    labor=s["labor"].copy(); capital=s["capital"]; skill=s["skill"]; burden=s["care_burden"]
    initial_income=labor+env.capital_return*capital
    initial_employed=np.clip(1-.18*s["vulnerable"]*burden,.70,1); employed=initial_employed.copy()
    prior=np.zeros(n); path=[]; total_tax=total_transfer=0.
    def snap(t, income):
        if keep_path: path.append({"period":t,**metrics(s,income,employed,initial_income)})
    snap(0,initial_income)
    for t in range(1,periods+1):
        actual_public=policy.public_access*policy.trust*s["trust"]
        has_public=rng.random(n)<actual_public
        quality=np.where(s["premium"],1+env.premium_gap,np.where(has_public,policy.public_quality,.22))
        effective=quality*sigmoid(-.8+2.5*skill+1.2*s["flexibility"])
        edu_target=(1.15-s["resource"])*(1-skill)
        skill[:]=np.clip(skill+policy.education*edu_target+.018*effective*(1-skill),0,1)
        burden[:]=np.maximum(0,burden-policy.care*s["vulnerable"]*(1-burden))
        adaptation=np.clip(.42*skill+.28*s["flexibility"]+.30*np.minimum(effective,1),0,1)
        augmentation=.043*s["exposure"]*effective*(.28+.72*skill)
        augmentation+=.055*policy.equalizing_design*s["exposure"]*has_public*(1-skill)*(1-s["resource"])
        displacement=env.rearrangement_speed*s["exposure"]*(1-adaptation)
        care_relief=.020*policy.care*s["vulnerable"]*(1-burden)
        growth=np.clip(augmentation-displacement+care_relief+env.feedback*prior,-.14,.18)
        employed=np.clip(employed-.055*displacement+.050*adaptation*policy.education+.030*policy.care*s["vulnerable"],.45,1)
        labor*=np.exp(growth)*(.985+.015*employed)
        ai_profit=env.capital_return*capital*s["exposure"]*np.minimum(effective,1.5)
        tax=policy.capital_dividend*ai_profit; pool=float(tax.sum()); weights=1.05-s["resource"]; weights/=weights.sum()
        dividend=pool*weights if policy.capital_dividend else np.zeros(n)
        worker_grant=policy.worker_ownership*float(ai_profit.sum())*weights
        capital[:]=np.maximum(1e-6,.985*capital+.44*(ai_profit-tax)+.02*np.maximum(labor-s["labor"],0)+worker_grant)
        total_tax+=pool; total_transfer+=float(dividend.sum())
        income=labor+ai_profit-tax+dividend; prior=growth; snap(t,income)
    final=metrics(s,income,employed,initial_income); initial=metrics(initial_state,initial_income,initial_employed,initial_income)
    row={"seed":seed,"policy":policy.name,**asdict(env),**asdict(policy)}
    row.update({f"initial_{k}":v for k,v in initial.items()}); row.update({f"final_{k}":v for k,v in final.items()})
    row.update({f"delta_{k}":final[k]-initial[k] for k in final})
    public_cost=0.0 if policy.name=="시장·고가AI" else periods*(.0035*policy.public_access*policy.public_quality**2+.012*policy.education+.010*policy.care+.0015*policy.worker_ownership)
    row["fiscal_cost"]=public_cost
    row["delta_net_output"]=row["delta_output"]-public_cost
    row["delta_net_ede_e1"]=row["delta_ede_e1"]-public_cost
    return row,pd.DataFrame(path) if keep_path else None,{"budget_error":total_transfer-total_tax}


def trajectories(df,out):
    items=[("wolfson","Wolfson 양극화"),("middle_share","중간층 비중"),("skill_gap","AI 역량 격차"),("capital_top10","상위10% AI 자본 몫")]
    fig,axes=plt.subplots(2,2,figsize=(11.5,7.5))
    for ax,(m,title) in zip(axes.flat,items):
        for p in POLICIES:
            q=df[df.policy==p.name].groupby("period")[m].quantile([.1,.5,.9]).unstack()
            ax.plot(q.index,q[.5],color=COLORS[p.name],label=p.name,lw=2); ax.fill_between(q.index,q[.1],q[.9],color=COLORS[p.name],alpha=.09)
        ax.set(title=title,xlabel="모형 시점"); ax.grid(alpha=.2)
    axes[0,0].legend(ncol=2,fontsize=8,frameon=False); fig.suptitle("공공 AI 정책조합별 분배 동학",fontweight="bold")
    fig.tight_layout(); fig.savefig(out,dpi=180,bbox_inches="tight"); plt.close(fig)


def quintile_growth(df,out):
    cols=[f"delta_growth_q{i}" for i in range(1,6)]; keep=["시장·고가AI","전국민 공공AI","공공AI+공교육","공공AI 종합안","공공AI 실패"]
    fig,ax=plt.subplots(figsize=(9,5.2)); x=np.arange(1,6)
    for name in keep:
        s=df[df.policy==name][cols].mean(); ax.plot(x,s.values,marker="o",lw=2.2,label=name,color=COLORS[name])
    ax.axhline(0,color="#667085",lw=1); ax.set_xticks(x,["하위20%","2분위","3분위","4분위","상위20%"])
    ax.set(ylabel="초기 대비 평균 로그소득 변화",title="누가 AI 전환의 이익을 얻는가"); ax.grid(alpha=.2); ax.legend(frameon=False,ncol=2)
    fig.tight_layout(); fig.savefig(out,dpi=180,bbox_inches="tight"); plt.close(fig)


def frontier(df,out):
    s=df.groupby("policy").agg(wolfson=("delta_wolfson","mean"),output=("delta_output","mean"),vulnerable=("delta_vulnerable_employment","mean")).reset_index()
    fig,ax=plt.subplots(figsize=(8.8,5.4))
    for _,r in s.iterrows():
        ax.scatter(r.output,r.wolfson,s=130+4000*max(r.vulnerable,0),color=COLORS[r.policy],alpha=.85); ax.annotate(r.policy,(r.output,r.wolfson),xytext=(5,5),textcoords="offset points",fontsize=9)
    ax.axhline(0,color="#667085",lw=1); ax.set(xlabel="평균소득 변화(모형 단위)",ylabel="Δ Wolfson",title="효율–양극화 정책 프런티어\n점 크기: 취약계층 고용 개선")
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(out,dpi=180,bbox_inches="tight"); plt.close(fig)


def phase_chart(df,out):
    vmax=max(abs(df.delta_wolfson.min()),abs(df.delta_wolfson.max())); normc=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),sharey=True)
    for ax,name in zip(axes,["전국민 공공AI","공공AI 종합안"]):
        p=df[df.policy==name].pivot(index="rearrangement_speed",columns="premium_gap",values="delta_wolfson")
        im=ax.imshow(p.values,origin="lower",aspect="auto",cmap="RdBu_r",norm=normc)
        ax.set_xticks(range(len(p.columns)),[f"{v:.2f}" for v in p.columns]); ax.set_yticks(range(len(p.index)),[f"{v:.3f}" for v in p.index]); ax.set(xlabel="민간 프리미엄 AI 품질격차",title=name)
    axes[0].set_ylabel("직업 재편 속도"); fig.colorbar(im,ax=axes,label="Δ Wolfson",shrink=.82); fig.suptitle("고가 AI와 직업 재편이 공공 AI를 압도하는 임계영역",fontweight="bold")
    fig.subplots_adjust(left=.08,right=.88,bottom=.15,top=.83,wspace=.18); fig.savefig(out,dpi=180,bbox_inches="tight"); plt.close(fig)


def prevention_chart(df,out):
    p=df.pivot(index="equalizing_design",columns="capital_dividend",values="delta_wolfson")
    vmax=max(abs(df.delta_wolfson.min()),abs(df.delta_wolfson.max())); nc=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    fig,ax=plt.subplots(figsize=(7.8,5.1)); im=ax.imshow(p.values,origin="lower",aspect="auto",cmap="RdBu_r",norm=nc)
    ax.set_xticks(range(len(p.columns)),[f"{v:.1f}" for v in p.columns]); ax.set_yticks(range(len(p.index)),[f"{v:.2f}" for v in p.index])
    ax.set(xlabel="AI 자본수익 환류율",ylabel="저역량층 우선설계 강도",title="이상적 경계 실험: 양극화 역전 임계점")
    fig.colorbar(im,ax=ax,label="Δ Wolfson"); fig.tight_layout(); fig.savefig(out,dpi=180,bbox_inches="tight"); plt.close(fig)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,default=ROOT/"results"/"public_ai"); ap.add_argument("--quick",action="store_true"); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    seeds=range(8 if a.quick else 40); n=500 if a.quick else 1400; finals=[]; paths=[]
    for seed in seeds:
        for p in POLICIES:
            r,path,ledger=simulate(seed,p,n=n,periods=15,keep_path=True); finals.append({**r,**ledger}); path["seed"],path["policy"]=seed,p.name; paths.append(path)
    f=pd.DataFrame(finals); t=pd.concat(paths,ignore_index=True); f.to_csv(a.output_dir/"policy_runs.csv",index=False,encoding="utf-8-sig"); t.to_csv(a.output_dir/"policy_paths.csv",index=False,encoding="utf-8-sig")
    trajectories(t,a.output_dir/"01_policy_dynamics.png"); quintile_growth(f,a.output_dir/"02_quintile_growth.png"); frontier(f,a.output_dir/"03_policy_frontier.png")
    phase=[]; phase_seeds=range(3 if a.quick else 12); gaps=(.10,.30,.50,.75,1.00); speeds=(.015,.030,.045,.065,.090)
    for name in ("전국민 공공AI","공공AI 종합안"):
        p=next(p for p in POLICIES if p.name==name)
        for gap in gaps:
            for speed in speeds:
                vals=[simulate(seed,p,Environment(premium_gap=gap,rearrangement_speed=speed),n=n,periods=12)[0]["delta_wolfson"] for seed in phase_seeds]
                phase.append({"policy":name,"premium_gap":gap,"rearrangement_speed":speed,"delta_wolfson":float(np.mean(vals))})
    ph=pd.DataFrame(phase); ph.to_csv(a.output_dir/"phase_grid.csv",index=False,encoding="utf-8-sig"); phase_chart(ph,a.output_dir/"04_phase_threshold.png")
    prevention=[]; prevent_seeds=range(3 if a.quick else 12)
    for design in (0,1,2,3,5,8):
        for dividend in (0,.30,.60,.90):
            p=Policy("역전탐색",1.0,1.2,.15,.10,dividend,.5*dividend,design,.98)
            ideal=Environment(premium_gap=0,rearrangement_speed=0,capital_return=.02,feedback=0)
            vals=[simulate(seed,p,ideal,n=n,periods=15)[0]["delta_wolfson"] for seed in prevent_seeds]
            prevention.append({"equalizing_design":design,"capital_dividend":dividend,"delta_wolfson":float(np.mean(vals))})
    pv=pd.DataFrame(prevention); pv.to_csv(a.output_dir/"prevention_grid.csv",index=False,encoding="utf-8-sig"); prevention_chart(pv,a.output_dir/"05_prevention_threshold.png")
    summary=f.groupby("policy").agg(delta_gini=("delta_gini","mean"),delta_wolfson=("delta_wolfson","mean"),delta_atkinson=("delta_atkinson_e1","mean"),delta_ede=("delta_ede_e1","mean"),fiscal_cost=("fiscal_cost","mean"),delta_net_output=("delta_net_output","mean"),delta_net_ede=("delta_net_ede_e1","mean"),delta_middle=("delta_middle_share","mean"),delta_skill_gap=("delta_skill_gap","mean"),delta_capital=("delta_capital_top10","mean"),delta_output=("delta_output","mean"),delta_vulnerable_employment=("delta_vulnerable_employment","mean")).reindex([p.name for p in POLICIES])
    summary.to_csv(a.output_dir/"policy_summary.csv",encoding="utf-8-sig")
    report={"empirical_claim":False,"baseline_runs":len(f),"phase_runs":2*len(gaps)*len(speeds)*len(list(phase_seeds)),"prevention_runs":len(prevention)*len(list(prevent_seeds)),"policy_means":summary.round(6).to_dict(orient="index"),"max_budget_error":float(f.budget_error.abs().max()),"limit":"인공 정책 메커니즘 실험; 현실 예측·인과효과 아님"}
    (a.output_dir/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8"); print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__": main()
