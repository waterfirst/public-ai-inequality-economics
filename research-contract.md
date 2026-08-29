# Research contract — Public AI & polarization on a real Korean population

Follows the `nvidia-korea-econophysics-lab` skill. Written before the rigor upgrade;
governs `scripts/12,13` and the paper's real-population sections.

## Research question
Does universal public/sovereign AI limit AI-driven economic polarization in a Korean
population, and which policy design (if any) reverses it rather than merely widening access?

## Falsifiable hypotheses
- **H1.** Universal *access alone* does not remove the initial-resource gradient in effective AI
  benefit (polarization still rises). *Falsified if* Δ Wolfson ≤ 0 under universal access.
- **H2.** A compensatory package (access + progressive education + capital-ownership + care)
  reduces Δ Wolfson relative to the market benchmark by a margin whose 95% CI excludes 0.
- **H3.** Education is the pivotal mechanism: ablating education removes most of the package's
  vulnerable-employment gain.

## Population, unit, time
- Unit: household/agent. Demographic structure from NVIDIA Nemotron-Personas-Korea
  (dataset 1.0, CC BY 4.0) aggregated to age×sex×region(시도)×education×broad-occupation
  (validated profile, forbidden narrative fields absent). Synthetic, marginal-aligned — NOT a survey.
- Time step: model period; horizon 15; finite-size checks at n ∈ {250,500,1000,2000}.

## Mechanisms & competing explanations
Effective-AI-service (access×quality×adoption×capability); skill accumulation; task
displacement vs complementarity by occupation; premium-quality gap; AI-capital returns;
care/time constraints; regional effective-access frictions. Competing explanation tested by
ablation: outcomes driven by *reallocation speed* vs by the *education/capital gradient*.

## Interventions & baseline
Baseline = market/premium AI. Policies: universal access; +education; +care; comprehensive
package; low-quality failure case (skill §4). Redistribution budget identity enforced (|error|<1e-10).

## Primary outcomes
Δ Wolfson polarization (primary), Δ Gini, Δ Atkinson(ε=1), Δ middle-income share,
Δ net EDE income (cost-adjusted), Δ vulnerable-group employment, top-decile AI-capital share.

## Calibration / provenance (labelled)
- `calibrated` from KOSIS/ECOS: reallocation speed ρ=0.0136 (DT_1DA9003S); capital income
  share κ=0.327 (ECOS 200Y116); region effective-access capacity from regional manufacturing
  productivity (DT_344N_1D8B_DD).
- `literature`/`scenario`: policy coverage, quality, trust levels; premium-quality gap range.
- `normalization`: resource rank, capital scaling to κ.
Each config constant carries a provenance tag in code.

## Validation, uncertainty, falsification
Paired Monte Carlo with common random numbers; report 95% CIs; mechanism ablations;
finite-size scaling; out-of-sample check that the initial capital-income share matches κ.
Report null results and policy-failure regions.

## Permitted vs prohibited claims
- Permitted: model-conditional comparative statics; mechanism identification; ranking of
  policy designs under stated assumptions.
- Prohibited: forecasts, causal policy effects, public-opinion inference, or treating the
  NVIDIA synthetic cross-section as a representative Korean sample or joint distribution.
