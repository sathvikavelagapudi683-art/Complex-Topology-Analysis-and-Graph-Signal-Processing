# Complex Topology Analysis & Graph Signal Processing

**Formal project title:** *A Multiscale Mathematical Framework for Functional Brain Networks*  
**Methods:** graph theory, graph signal processing (GSP), topological data analysis (TDA), and an inductive graph neural network (GNN) experiment.

This repository contains the reusable analysis script and carefully separated result snapshots from the project report and result-analysis slides. It does **not** include fMRI files, participant-level tables, identifiers, checkpoints, or raw connectome data.

## Project at a glance

The analysis combines three complementary mathematical views of functional connectivity:

- **Graph theory** describes network structure, including connected components, clustering, path-based integration, and modularity.
- **Graph signal processing** studies variation of signals over a graph using the graph Laplacian and graph-frequency energy summaries.
- **Topological data analysis** summarizes H0 component evolution and H1 loop-like features over a filtration using persistent homology.

A separate downstream experiment used 20 engineered subject-level features to construct a participant-similarity graph and train a shallow inductive GNN for the dataset labels `Patient` and `GenPop`.

## Two cohorts — kept separate

| Cohort | Representation | Project role | Recorded scale |
|---|---|---|---|
| HCP S1200 | 300 ICA-derived components per subject | Large-cohort descriptive characterization | 1,003 subjects; 4,800 time points per subject |
| OpenNeuro `ds005237` | 488-parcel representation | Transdiagnostic group comparisons, robustness checks, and participant-level GNN | 241 processed participants: 149 `Patient`, 92 `GenPop` |

These cohorts use different representations and preprocessing. Their raw feature values are **not directly comparable**. The OpenNeuro cohort is transdiagnostic; the source project explicitly cautions against relabelling it as a Parkinson's disease cohort based on local folder names.

## HCP descriptive snapshot

The result-analysis slides record a 300-node graph constructed at 17.5% density, with 7,848 edges and mean degree approximately 52.32. These are design-constrained quantities. Across-subject summaries included:

| Feature | Mean | SD | Range |
|---|---:|---:|---:|
| Modularity | 0.3519 | 0.0278 | 0.2617–0.4481 |
| Mean clustering | 0.0865 | 0.0215 | 0.0461–0.2289 |
| Low/high graph-energy ratio | 1.6035 | 0.1954 | 1.2378–2.1986 |
| H1 total persistence | 6.0849 | 0.9716 | 3.2201–9.6058 |

The project résumé separately highlights one analysed graph with 300 nodes, 7,849 edges, and modularity 0.4816. The cohort-summary slide deck records 7,848 edges for the fixed-density HCP construction and reports average modularity 0.3519. These are retained as distinct source snapshots rather than silently reconciled.

## OpenNeuro group-comparison snapshot

The adjusted comparisons used HC3 robust standard errors and adjusted for site, age, and sex. None of the 13 adjusted graph-theory/TDA comparisons remained significant after Benjamini–Hochberg correction. For example, H1 finite-bar count had nominal p ≈ 0.047 but adjusted p ≈ 0.182. The density analysis tested 10%, 15%, 17.5%, and 20%; all 24 adjusted metric-by-density tests had adjusted p-values above 0.05. This is not evidence of equivalence or proof that the groups are identical.

The GSP energy-balance tests were also inconclusive after correction. The recorded low-versus-rest adjusted effect was approximately −0.040 (95% CI [−0.089, 0.008], p = 0.105); mid-versus-high was approximately +0.021 (95% CI [−0.001, 0.044], p = 0.059; BH-adjusted p ≈ 0.105).

## Downstream inductive GNN snapshot

The report records 241 participants represented by 20 engineered features, with stratified splits of 168 training, 36 validation, and 37 test participants. Validation and test nodes connected only to training nodes in the inductive graph; no validation–test edges were used.

| Metric | Reported value |
|---|---:|
| Validation balanced accuracy | 0.5649 |
| Validation-selected threshold | 0.555 |
| Test balanced accuracy | 0.6398 |
| Test macro-F1 | 0.6191 |
| Test ROC-AUC | 0.6087 |
| Best epoch | 54 |
| Best validation loss | 0.7020 |

**Interpretation:** modest exploratory predictive signal only. The cohort and test split are limited, and the test set was reused during earlier exploratory model comparisons. The report explicitly warns that the result is not an unbiased estimate of generalization and does not establish clinical utility.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── brain_network_project_master.py
├── docs/
│   ├── METHODS.md
│   ├── RESULTS.md
│   └── REPRODUCIBILITY.md
├── results/
│   ├── hcp_descriptive_snapshot.csv
│   ├── openneuro_adjusted_comparisons.csv
│   ├── openneuro_gsp_balance.csv
│   ├── openneuro_density_sensitivity.csv
│   ├── inductive_gnn_results.csv
│   └── resume_highlight_graph_snapshot.csv
└── tests/
    └── test_core.py
```

## Setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run the reusable pipeline

For a regional time-series matrix saved as `.npy` with shape `(time_points, nodes)`:

```bash
python brain_network_project_master.py timeseries \\
  --input path/to/regional_timeseries.npy \\
  --orientation time_nodes \\
  --density 0.175 \\
  --outdir outputs/subject
```

The command computes Pearson functional connectivity, thresholds the strongest absolute correlations, calculates graph-theoretic and GSP descriptors, computes exploratory H0/H1 persistence summaries, and saves matrices, numerical summaries, and JSON output.

The script also supports a `summarize` command for descriptive statistics and data-quality checks of an existing feature CSV. Group, interaction, and density-sensitivity results in `results/` are archived aggregate snapshots from the project report; the original participant-level tables are not included, and those analyses are not exposed as CLI commands here. See `docs/REPRODUCIBILITY.md` for input expectations and caveats.

## Important interpretation notes

- Functional connectivity expresses statistical relationships; it is not a direct anatomical connection or causal pathway.
- HCP d300 nodes are ICA-derived components, not necessarily anatomical regions.
- Graph frequency is defined by the graph Laplacian and is not EEG frequency in hertz.
- Fixed-density edge count and mean degree are constrained by graph construction.
- The implemented TDA dissimilarity `1 - |FC|` is not guaranteed to satisfy every metric axiom; persistence results should be interpreted cautiously.
- NetworkX `global_efficiency` in the supplied script is unweighted.
- H0/H1 features are mathematical components/loop-like structures in a filtration, not literal biological circuits.
- These analyses are exploratory and do not establish a diagnostic biomarker or causal neural mechanism.

See `docs/RESULTS.md` and `docs/REPRODUCIBILITY.md` before interpreting the reported values.
