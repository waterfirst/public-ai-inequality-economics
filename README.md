# Public AI as Social Infrastructure

**A Heterogeneous-Agent Model of Access, Occupational Reallocation, and Economic Polarization**

This repository contains an English economics working paper, a transparent heterogeneous-agent transition model, Monte Carlo robustness analysis, tests, and reproducible figures.

## Working paper

- [PDF](Public_AI_Social_Infrastructure_Economics_Working_Paper_2026-08-09.pdf)
- [Self-contained HTML](public_ai_economics_paper_en_v1.html)
- [Quarto source](public_ai_economics_paper_en.qmd)

## Research question

Can a universal public or sovereign AI service reduce the distributional consequences of rapid AI adoption?

The model separates nominal access from effective AI use. Households differ in income, skills, AI-capital ownership, occupational exposure, flexibility, care burdens, trust, and ability to purchase premium AI. Policies combine public access, education, care, capital-income recycling, and worker ownership.

## Main computational result

Across 200 uncertain parameter environments and 3 seeds per environment:

- Public AI plus education lowered modeled polarization in 100% of environments.
- It increased net output in 53.5% and net equally distributed equivalent income in 59.0%.
- The comprehensive public option lowered modeled polarization in 100%, but increased net output in 43.5% because its resource cost was higher.
- Access alone reduced polarization but was not sufficient to reverse it.

These are **model-conditional comparative statics**, not empirical estimates, forecasts, or causal policy effects.

## Interactive Korea Policy Lab

The repository now includes a React + Three.js policy laboratory that turns the paper's heterogeneous-agent model into an explorable social network.

- **3D social physics view:** households are positioned by initial resources, income change, and Korean region; links carry peer adoption and skill spillovers.
- **Policy comparison:** market AI, free universal access, access plus education, a Korea-targeted package, a comprehensive package, and a low-quality failure case.
- **Korea-specific mechanisms:** premium-model gaps, occupational reallocation, junior career-ladder displacement, regional effective-access penalties, network learning, care, capital dividends, and worker ownership.
- **Distributional dashboard:** Wolfson polarization, Gini, middle-income share, AI capability gap, top-decile AI-capital concentration, EDE income, and policy trajectories.
- **NVIDIA experiment bridge:** import a privacy-preserving aggregate generated from `nvidia/Nemotron-Personas-Korea`; names and narrative personas are never exported.

The browser simulation is a mechanism demonstrator. Its default Korea population is synthetic and must not be interpreted as a forecast.

```bash
npm install
npm test
npm run dev
```

The production build is published by GitHub Pages. The Vite base path is configured for this repository.

## Repository structure

```text
public_ai_economics_paper_en.qmd       # paper source
references.bib                         # bibliography
scripts/07_public_ai_policy_simulation.py
scripts/08_economics_robustness.py
scripts/09_prepare_nvidia_korea_personas.py
src/polarization_experiment/metrics.py
tests/test_public_ai_policy.py
src/simulation/model.ts                # browser ABM and network layer
src/components/InequalityWorld.tsx     # Three.js visualization
docs/KOREA_POLICY_BLUEPRINT_KO.md      # Korean government policy proposal
docs/GOV_AI_COMPETITION_PITCH_KO.md    # Government AI competition pitch
docs/JOURNAL_SUBMISSION_STRATEGY.md    # econophysics/social-physics route
results/public_ai_full4/               # baseline and threshold outputs
results/economics_robustness_full/     # Monte Carlo outputs and English figures
```

## Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PYTHONPATH=src python3 -m unittest tests/test_public_ai_policy.py -v

python3 scripts/07_public_ai_policy_simulation.py \
  --output-dir results/public_ai_full4

python3 scripts/08_economics_robustness.py \
  --output-dir results/economics_robustness_full

quarto render public_ai_economics_paper_en.qmd --to html
```

### NVIDIA Korea persona experiment

`Nemotron-Personas-Korea` is a fully synthetic CC BY 4.0 dataset. The preparation script streams records, removes names and free-text personas, and writes only age×sex×region×education×occupation counts.

```bash
pip install -r requirements-nvidia.txt
python3 scripts/09_prepare_nvidia_korea_personas.py \
  --rows 100000 \
  --output public/data/nvidia-korea-profile.json
```

Upload the resulting JSON in the simulator. Because the NVIDIA data card documents independence assumptions across some demographic inputs, the profile must be audited against KOSIS, the Regional Employment Survey, and KLIPS joint distributions before empirical use.

The complete paper references 1,128 baseline/threshold experiments and 3,600 Monte Carlo runs. Four publication-scope model tests pass in this repository; the broader development workspace passed 17 tests before the final scope was extracted.

## Interpretation limits

- The population and parameters are synthetic.
- This is a partial-equilibrium transition model, not a market-clearing general-equilibrium model.
- Public-service costs are normalized resource costs, not estimated fiscal costs.
- Monte Carlo robustness is internal to the specified model family.
- No result should be interpreted as a prediction for Korea or another country.

## Citation

```bibtex
@unpublished{choi2026publicai,
  author = {Choi, Nak Cho},
  title = {Public AI as Social Infrastructure: A Heterogeneous-Agent Model of Access, Occupational Reallocation, and Economic Polarization},
  year = {2026},
  note = {Computational economics working paper}
}
```
