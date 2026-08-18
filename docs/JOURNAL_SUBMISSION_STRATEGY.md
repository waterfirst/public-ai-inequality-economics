# Journal submission strategy

## Recommended first target

### Journal of Economic Interaction and Coordination (JEIC)

This is the strongest first fit after the network extension is fully estimated. Its stated scope explicitly includes heterogeneous-agent models, artificial intelligence, interacting-particle systems in economics, econophysics, nonlinear dynamics, and complex networks.

Required upgrades before submission:

1. Promote the browser model's peer-adoption and skill-spillover terms into the Python research model.
2. Report finite-size checks, seed convergence, global sensitivity, and parameter-identification diagnostics.
3. Replace normalized Korea parameters with reproducible moments from KLIPS, the Regional Employment Survey, KOSIS, and Bank of Korea exposure/complementarity measures.
4. Add ablation tests that separately remove premium quality, network homophily, junior displacement, capital concentration, and progressive training.
5. Release a frozen data dictionary, configuration files, and computational environment.

## Alternative targets

| Journal | Fit | What must be emphasized |
|---|---|---|
| Journal of Artificial Societies and Social Simulation | Excellent for transparent policy ABM and reproducibility | Generative explanation, ODD-style model description, validation, replication package |
| Physica A | Conditional | Explicit statistical-mechanics contribution: phase transition, scaling, order parameter, universality/finite-size behavior—not only an ABM application |
| Journal of Computational Social Science | Strong | Korea-calibrated computational social-science contribution, data ethics, subgroup validation |
| Computational Economics | Strong | Economic calibration, welfare accounting, sensitivity, comparison with analytical or structural benchmarks |

## Two-paper strategy

**Paper A — computational economics / JEIC**

Focus on access versus capability, endogenous AI adoption on homophilous networks, occupational reallocation, and AI-capital ownership. The main contribution is the existence and location of a policy phase boundary where universal access ceases to reduce polarization efficiently.

**Paper B — social physics / Physica A or JASSS**

Focus on the distribution dynamics: network diffusion, Matthew effects, polarization as an order parameter, cluster formation, hysteresis under policy withdrawal, and finite-size scaling. A Physica A submission should derive and test these properties rather than simply reuse economic terminology.

## Falsifiable hypotheses

- H1: Universal access reduces the access gradient but leaves a positive resource gradient in effective AI services when premium quality and skill complementarity remain.
- H2: Progressive training has a larger polarization effect when network homophily is high, because targeted nodes transmit skills within disadvantaged clusters.
- H3: At high junior-displacement pressure, access-only policy can raise adoption and output while reducing the middle-income share.
- H4: Capital recycling without ownership accumulation has a weaker long-run effect than worker or citizen ownership at the same fiscal cost.
- H5: A critical compensatory-design intensity exists beyond which the Wolfson change becomes non-positive; the threshold moves with premium quality and occupational mobility.

## Minimum empirical validation package

- Bank of Korea: occupation/industry AI exposure and complementarity; representative household AI-use survey; youth-employment exposure study.
- KLIPS: longitudinal income, education, occupation transition, household burden, and capital-income proxies.
- Regional Employment Survey/KOSIS: age×sex×education×occupation×region joint distributions.
- Business Activity Survey/ICT use surveys: firm size, age, AI adoption, and productivity heterogeneity.
- NVIDIA Nemotron-Personas-Korea: synthetic stratification stress tests only, audited against the official joint distributions above.

## Claims discipline

Use “model-conditional comparative statics,” “mechanism experiment,” and “candidate phase boundary.” Do not call synthetic-persona results representative survey estimates. Do not describe calibrated parameters as causal effects unless identified from an explicit empirical design.

## Reproducibility checklist

- Deterministic seeds and machine-readable configurations
- Unit, budget-identity, and regression tests
- Monte Carlo uncertainty intervals and paired comparisons
- Finite-size and time-horizon sensitivity
- Sobol or Morris global sensitivity analysis
- NVIDIA dataset card, license, aggregation script, and joint-distribution audit
- ODD-style model protocol and equation-to-code crosswalk
- Pre-analysis plan for any human or administrative-data study
