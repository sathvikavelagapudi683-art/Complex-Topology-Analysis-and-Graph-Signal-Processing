# Methods overview

## Functional-connectivity graph pipeline

The reusable time-series command expects a two-dimensional regional/component matrix. It computes a Pearson-correlation functional-connectivity matrix, sets the diagonal to zero, retains the strongest absolute correlations at a target undirected graph density, and forms a weighted graph.

## Graph-theoretic descriptors

The master script calculates node degree and strength summaries, weighted clustering, connected components, largest-component properties, greedy weighted modularity, unweighted global efficiency, inverse-weight path length within the giant component, and mean betweenness centrality.

## Graph signal processing

The script computes the normalized graph Laplacian and its eigendecomposition. It projects a node-level signal onto graph eigenvectors, summarizes graph spectral energy into low, middle, and high index bands, and calculates spectral entropy and graph smoothness. **Graph frequency is a property of the graph Laplacian, not temporal EEG frequency in hertz.**

## Persistent homology

The supplied implementation builds a dissimilarity matrix from normalized absolute edge weights using `1 - normalized_similarity` and passes it to Ripser for H0/H1 summaries. This transformation is the project's chosen filtration construction, but it is not guaranteed to be a true metric. Interpret the persistence outputs as properties of the implemented filtration, not direct anatomical circuits.

## OpenNeuro subject-feature analysis

The report describes a separate set of 20 subject-level features assembled from graph/TDA and GSP result tables: six graph-structure features, seven H0/H1 features, six GSP/Laplacian features, and mean absolute functional connectivity. A shallow GNN then operates on a graph whose nodes are participants and whose edges represent similarity in feature space. It is not a parcel-level GNN directly operating on the original brain regions.

## Statistical comparisons

The result slides report group comparisons adjusted for site, age, and sex with HC3 robust standard errors. Benjamini–Hochberg correction was used for multiple feature tests. Density sensitivity was checked at 10%, 15%, 17.5%, and 20%.
