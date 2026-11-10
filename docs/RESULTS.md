# Recorded results

These values are transcribed from the project's October 2026 report and result-analysis slides. They are result snapshots, not reruns from data included in this repository.

## HCP S1200 descriptive characterization

- 1,003 subjects; 300 ICA-derived components; 4,800 time points per subject.
- Graph construction: 17.5% density, 7,848 edges, mean degree approximately 52.32.
- Across-subject summaries are stored in `results/hcp_descriptive_snapshot.csv`.

The edge count and mean degree are determined by the fixed-density design and should not be interpreted as biological discoveries.

## OpenNeuro ds005237 cohort

- 241 processed participants: 149 `Patient`, 92 `GenPop`.
- 488-parcel representation; two sites represented by 137 and 104 participants.
- None of the 13 adjusted graph-theory/TDA comparisons survived Benjamini–Hochberg correction.
- No group-by-site interaction survived the reported correction.
- All 24 adjusted metric-by-density tests across 10%, 15%, 17.5%, and 20% density had adjusted p-values above 0.05.

See the supplied CSV snapshots for selected effect estimates and p-values. Nonsignificance does not establish equivalence or prove the absence of a group effect.

## Inductive GNN experiment

The report describes a 168/36/37 participant train/validation/test split and a validation-selected threshold of 0.555. The final test snapshot was balanced accuracy 0.6398, macro-F1 0.6191, ROC-AUC 0.6087. Best epoch was 54 and best validation loss was 0.7020.

The report explicitly notes that the test set was reused in earlier exploratory comparisons. The test metrics are therefore exploratory and may be optimistic; they are not an untouched generalization estimate.

## Different network snapshots

The resume bullet highlights one analysed graph with 300 nodes, 7,849 edges, and modularity 0.4816. The HCP cohort result deck reports a 17.5%-density construction with 7,848 edges and an across-subject mean modularity of 0.3519 (SD 0.0278). This repository does not treat the single-graph highlight and cohort-level mean as interchangeable.
