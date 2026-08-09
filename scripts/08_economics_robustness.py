#!/usr/bin/env python3
"""Monte Carlo robustness and English figures for the public-AI economics paper."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("public_ai_model",ROOT/"scripts"/"07_public_ai_policy_simulation.py")
M=importlib.util.module_from_spec(spec); sys.modules[spec.name]=M; spec.loader.exec_module(M)
plt.rcParams["font.family"]="DejaVu Sans"; plt.rcParams["axes.unicode_minus"]=False
EN={"시장·고가AI":"Market / premium AI","전국민 공공AI":"Universal public AI","공공AI+공교육":"Public AI + education",
    "공공AI+돌봄":"Public AI + care","공공AI 종합안":"Comprehensive public option","공공AI 실패":"Low-quality public AI"}
COL={EN[k]:v for k,v in M.COLORS.items()}


def standardize_regression(df,y,features):
    x=df[features].astype(float); x=(x-x.mean())/x.std(ddof=0); yy=(df[y]-df[y].mean())/df[y].std(ddof=0)
    beta=np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),yy,rcond=None)[0][1:]
    return dict(zip(features,beta))


def english_dynamics(paths,out):
    labels=[("wolfson","Wolfson polarization"),("middle_share","Middle-income share"),("skill_gap","AI capability gap"),("capital_top10","Top-decile AI-capital share")]
    fig,axes=plt.subplots(2,2,figsize=(11.5,7.3))
    for ax,(metric,title) in zip(axes.flat,labels):
        for ko,en in EN.items():
            q=paths[paths.policy==ko].groupby("period")[metric].quantile([.1,.5,.9]).unstack()
            ax.plot(q.index,q[.5],label=en,color=COL[en],lw=2); ax.fill_between(q.index,q[.1],q[.9],color=COL[en],alpha=.08)
        ax.set(title=title,xlabel="Model period"); ax.grid(alpha=.2)
    axes[0,0].legend(ncol=2,fontsize=7.8,frameon=False); fig.suptitle("Distributional dynamics under alternative public-AI regimes",fontweight="bold")
    fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def english_quintile(runs,out):
    cols=[f"delta_growth_q{i}" for i in range(1,6)]; selected=["시장·고가AI","전국민 공공AI","공공AI+공교육","공공AI 종합안","공공AI 실패"]
    fig,ax=plt.subplots(figsize=(9,5.1)); x=range(1,6)
    for ko in selected:
        vals=runs[runs.policy==ko][cols].mean(); ax.plot(x,vals,marker="o",lw=2.2,label=EN[ko],color=COL[EN[ko]])
    ax.axhline(0,color="#667085",lw=1); ax.set_xticks(list(x),["Bottom 20%","Q2","Q3","Q4","Top 20%"])
    ax.set(ylabel="Mean log-income change",title="Incidence of the AI transition by initial-resource quintile"); ax.grid(alpha=.2); ax.legend(frameon=False,ncol=2)
    fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def english_frontier(runs,out):
    s=runs.groupby("policy").agg(pol=("delta_wolfson","mean"),output=("delta_output","mean"),vuln=("delta_vulnerable_employment","mean")).reset_index()
    fig,ax=plt.subplots(figsize=(8.7,5.3))
    for _,r in s.iterrows():
        en=EN[r.policy]; ax.scatter(r.output,r.pol,s=120+4200*max(r.vuln,0),color=COL[en],alpha=.85); ax.annotate(en,(r.output,r.pol),xytext=(5,5),textcoords="offset points",fontsize=8.5)
    ax.axhline(0,color="#667085",lw=1); ax.set(xlabel="Change in mean income (model units)",ylabel="Change in Wolfson index",title="Efficiency–polarization frontier\nMarker size: vulnerable-group employment gain")
    ax.grid(alpha=.2); fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def english_phase(phase,out):
    vmax=max(abs(phase.delta_wolfson.min()),abs(phase.delta_wolfson.max())); nc=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),sharey=True)
    for ax,ko in zip(axes,["전국민 공공AI","공공AI 종합안"]):
        p=phase[phase.policy==ko].pivot(index="rearrangement_speed",columns="premium_gap",values="delta_wolfson"); im=ax.imshow(p.values,origin="lower",aspect="auto",cmap="RdBu_r",norm=nc)
        ax.set_xticks(range(len(p.columns)),[f"{v:.2f}" for v in p.columns]); ax.set_yticks(range(len(p.index)),[f"{v:.3f}" for v in p.index]); ax.set(xlabel="Premium-quality gap",title=EN[ko])
    axes[0].set_ylabel("Occupational-reallocation rate"); fig.colorbar(im,ax=axes,label="Change in Wolfson index",shrink=.82)
    fig.suptitle("When premium AI and rapid reallocation overwhelm the public option",fontweight="bold"); fig.subplots_adjust(left=.08,right=.88,bottom=.15,top=.82,wspace=.18); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def english_prevention(df,out):
    p=df.pivot(index="equalizing_design",columns="capital_dividend",values="delta_wolfson"); vmax=max(abs(df.delta_wolfson.min()),abs(df.delta_wolfson.max())); nc=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
    fig,ax=plt.subplots(figsize=(7.8,5)); im=ax.imshow(p.values,origin="lower",aspect="auto",cmap="RdBu_r",norm=nc)
    ax.set_xticks(range(len(p.columns)),[f"{v:.1f}" for v in p.columns]); ax.set_yticks(range(len(p.index)),[f"{v:g}" for v in p.index])
    ax.set(xlabel="Share of AI-capital income recycled",ylabel="Compensatory-design intensity",title="Ideal-boundary experiment: reversing polarization")
    fig.colorbar(im,ax=ax,label="Change in Wolfson index"); fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def sensitivity_plot(coefs,out):
    features=["premium_gap","rearrangement_speed","capital_return","feedback"]; names=["Premium gap","Reallocation speed","Capital return","Dynamic feedback"]
    y=np.arange(len(features)); fig,ax=plt.subplots(figsize=(8.4,4.8)); width=.35
    ax.barh(y-width/2,[coefs["Market / premium AI"][x] for x in features],height=width,label="Market / premium AI",color="#B42318")
    ax.barh(y+width/2,[coefs["Comprehensive public option"][x] for x in features],height=width,label="Comprehensive public option",color="#039855")
    ax.axvline(0,color="#667085",lw=1); ax.set_yticks(y,names); ax.set(xlabel="Standardized association with change in Wolfson index",title="Global parameter sensitivity (not causal estimates)")
    ax.legend(frameon=False); ax.grid(axis="x",alpha=.2); fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def effect_ecdf(paired,out):
    fig,ax=plt.subplots(figsize=(8.6,5.1))
    for ko in [p.name for p in M.POLICIES if p.name!="시장·고가AI"]:
        x=np.sort(paired.loc[paired.policy==ko,"wolfson_vs_market"].to_numpy()); y=np.arange(1,len(x)+1)/len(x); en=EN[ko]
        ax.plot(x,y,label=en,color=COL[en],lw=2)
    ax.axvline(0,color="#667085",lw=1); ax.set(xlabel="Policy minus market: change in Wolfson index",ylabel="Empirical CDF",title="Robustness of polarization effects across parameter environments")
    ax.grid(alpha=.2); ax.legend(frameon=False,fontsize=8); fig.tight_layout(); fig.savefig(out,dpi=190,bbox_inches="tight"); plt.close(fig)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,default=ROOT/"results"/"economics_robustness"); ap.add_argument("--quick",action="store_true"); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    base=ROOT/"results"/"public_ai_full4"; paths=pd.read_csv(base/"policy_paths.csv"); runs=pd.read_csv(base/"policy_runs.csv")
    phase=pd.read_csv(base/"phase_grid.csv"); prevention=pd.read_csv(base/"prevention_grid.csv")
    english_dynamics(paths,a.output_dir/"01_dynamics_en.png"); english_quintile(runs,a.output_dir/"02_quintile_incidence_en.png"); english_frontier(runs,a.output_dir/"03_frontier_en.png"); english_phase(phase,a.output_dir/"04_phase_en.png"); english_prevention(prevention,a.output_dir/"05_prevention_en.png")
    rng=np.random.default_rng(20260809); specs=30 if a.quick else 200; seeds=range(2 if a.quick else 3); rows=[]
    for sid in range(specs):
        env=M.Environment(premium_gap=rng.uniform(.05,1.05),rearrangement_speed=rng.uniform(.01,.10),capital_return=rng.uniform(.02,.11),feedback=rng.uniform(-.05,.35)); cost_multiplier=rng.uniform(.5,4.0)
        for seed in seeds:
            for p in M.POLICIES:
                r,_,_=M.simulate(seed,p,env,n=450 if a.quick else 900,periods=12); r["cost_multiplier"]=cost_multiplier; r["delta_net_output_adjusted"]=r["delta_output"]-cost_multiplier*r["fiscal_cost"]; r["delta_net_ede_adjusted"]=r["delta_ede_e1"]-cost_multiplier*r["fiscal_cost"]; rows.append({"spec_id":sid,**r})
    df=pd.DataFrame(rows); df.to_csv(a.output_dir/"monte_carlo_runs.csv",index=False,encoding="utf-8-sig")
    agg=df.groupby(["spec_id","policy"])[["delta_wolfson","delta_net_output_adjusted","delta_net_ede_adjusted","delta_vulnerable_employment"]].mean().reset_index()
    market=agg[agg.policy=="시장·고가AI"].set_index("spec_id"); paired=[]
    for _,r in agg[agg.policy!="시장·고가AI"].iterrows():
        b=market.loc[r.spec_id]; paired.append({"spec_id":r.spec_id,"policy":r.policy,"wolfson_vs_market":r.delta_wolfson-b.delta_wolfson,"output_vs_market":r.delta_net_output_adjusted-b.delta_net_output_adjusted,"ede_vs_market":r.delta_net_ede_adjusted-b.delta_net_ede_adjusted,"vulnerable_vs_market":r.delta_vulnerable_employment-b.delta_vulnerable_employment})
    paired=pd.DataFrame(paired); paired.to_csv(a.output_dir/"paired_policy_effects.csv",index=False,encoding="utf-8-sig")
    features=["premium_gap","rearrangement_speed","capital_return","feedback"]; coefs={}
    for ko in ("시장·고가AI","공공AI 종합안"):
        coefs[EN[ko]]=standardize_regression(df[df.policy==ko],"delta_wolfson",features)
    sensitivity_plot(coefs,a.output_dir/"06_sensitivity_en.png"); effect_ecdf(paired,a.output_dir/"07_effect_ecdf_en.png")
    summary=[]
    for ko,g in paired.groupby("policy"):
        summary.append({"policy":EN[ko],"share_lower_polarization":float((g.wolfson_vs_market<0).mean()),"share_higher_output":float((g.output_vs_market>0).mean()),"share_higher_ede":float((g.ede_vs_market>0).mean()),"share_pareto_output_polarization":float(((g.output_vs_market>0)&(g.wolfson_vs_market<0)).mean()),"median_wolfson_effect":float(g.wolfson_vs_market.median())})
    summary=pd.DataFrame(summary); summary.to_csv(a.output_dir/"robustness_summary.csv",index=False,encoding="utf-8-sig")
    report={"parameter_specs":specs,"seeds_per_spec":len(list(seeds)),"runs":len(df),"standardized_sensitivity":coefs,"policy_robustness":summary.to_dict(orient="records"),"claim":"model robustness only; not empirical identification"}
    (a.output_dir/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8"); print(json.dumps(report,indent=2))


if __name__=="__main__": main()
