# Reproducibility notes

## Included

- `brain_network_project_master.py`: reusable time-series pipeline for functional connectivity, graph theory, GSP, and persistence summaries; it also provides a descriptive-statistics/data-quality `summarize` command for existing CSVs.
- Aggregate result snapshots transcribed from the project report and result slides.
- Method and interpretation notes documenting what the script does and the limits of the recorded results.

## Not included

- HCP S1200 time series, OpenNeuro fMRI files, parcellations/ICA data, or source neuroimaging derivatives.
- Participant-level feature tables, participant IDs, group/site/age/sex rows, or raw metadata.
- Original Google Colab notebooks, every intermediate processing file, final CSV result tables, model checkpoint, or participant-level predictions referenced in the report.

The report lists the original feature tables and GNN checkpoint as files in a Google Drive workspace; these files were not present in the available project archive. The public repository therefore contains the reusable master script and aggregate summaries, not the complete original computational environment.

## Time-series input

For `timeseries`, provide a 2-D `.npy` matrix with finite numeric values. The default orientation is `(time_points, nodes)`; use `--orientation nodes_time` for `(nodes, time_points)`. The command generates functional connectivity, a fixed-density weighted adjacency matrix, graph-theoretic features, normalized-Laplacian/GSP summaries, and H0/H1 persistence outputs.

## Feature-table inputs

The `summarize` command operates on an existing CSV and writes numerical descriptive statistics and column-level data-quality information. Group-adjusted comparisons, group-by-site interactions, and density-sensitivity results are included only as aggregate result snapshots transcribed from the project report/slides; their original participant-level inputs were not present in the recovered archive, so these analyses are not exposed as CLI commands in this repository.

The historical GNN experiment is documented in the report but is not re-created by the master script. Its participant-similarity graph construction and training inputs/checkpoint were not in the recovered project package.

## Known methodological cautions

1. A correlation matrix is a statistical connectivity representation, not proof of anatomical or causal connections.
2. The HCP d300 nodes are ICA-derived components, not anatomical parcels.
3. Fixed-density graph construction constrains edge count and mean degree.
4. GSP graph frequency is not temporal frequency measured in hertz.
5. The TDA dissimilarity `1 - |FC|` is not guaranteed to be a true metric.
6. NetworkX global efficiency in the master script is unweighted.
7. Constant or mathematically related persistence/eigenvalue counts are not independent biological discoveries.
8. The alternate cohort is described in the report as transdiagnostic; retain its recorded `Patient` and `GenPop` labels and do not infer a disease-specific diagnosis from folder names.
9. Multiple testing was addressed with Benjamini–Hochberg correction; nonsignificance is not evidence of equivalence.
10. The GNN test split was reused in exploratory model comparisons. Its reported test results are not an untouched estimate of generalization.
11. The project is exploratory and has no clinical validation.
