#!/usr/bin/env python3
"""Multiscale functional brain-network analysis: graph theory, GSP and TDA.

This is a reusable analysis script. It does not contain or download the study's
private neuroimaging data or reproduce the historical participant-level GNN.
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

try:
    from ripser import ripser
except ImportError:
    ripser = None


DEFAULT_DENSITY = 0.175


def ensure_dir(path):
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def functional_connectivity(time_by_node: np.ndarray) -> np.ndarray:
    """Pearson correlation between node time series; diagonal is set to zero."""
    x = np.asarray(time_by_node, dtype=float)
    if x.ndim != 2 or not np.isfinite(x).all():
        raise ValueError("Input must be a finite 2-D time-by-node matrix.")
    if min(x.shape) < 3:
        raise ValueError("Need at least three time points and three nodes.")
    fc = np.corrcoef(x, rowvar=False)
    fc = np.nan_to_num(fc, nan=0.0, posinf=0.0, neginf=0.0)
    np.fill_diagonal(fc, 0.0)
    return fc


def threshold_absolute_fc(fc: np.ndarray, density: float = DEFAULT_DENSITY) -> np.ndarray:
    """Keep the strongest absolute FC edges at the requested undirected density."""
    fc = np.asarray(fc, dtype=float)
    if fc.ndim != 2 or fc.shape[0] != fc.shape[1]:
        raise ValueError("FC matrix must be square.")
    if not 0 < density <= 1:
        raise ValueError("density must be in (0, 1].")
    n = fc.shape[0]
    i, j = np.triu_indices(n, 1)
    weights = np.abs(fc[i, j])
    k = max(1, min(len(weights), int(round(density * len(weights)))))
    selected = np.argpartition(weights, -k)[-k:]
    adjacency = np.zeros_like(fc, dtype=float)
    adjacency[i[selected], j[selected]] = weights[selected]
    adjacency[j[selected], i[selected]] = weights[selected]
    return adjacency


def graph_theory_features(adjacency: np.ndarray) -> dict:
    """Compute weighted structure summaries and explicitly unweighted efficiency."""
    a = np.asarray(adjacency, dtype=float).copy()
    np.fill_diagonal(a, 0.0)
    g = nx.from_numpy_array(a)
    n = len(g)
    degree = np.asarray([d for _, d in g.degree()], dtype=float)
    strength = np.asarray([s for _, s in g.degree(weight="weight")], dtype=float)
    clustering = nx.clustering(g, weight="weight")
    components = list(nx.connected_components(g))
    giant = max(components, key=len) if components else set()
    path_length = float("nan")
    if len(giant) > 1:
        gg = g.subgraph(giant).copy()
        for _, _, data in gg.edges(data=True):
            data["distance"] = 1.0 / max(float(data.get("weight", 0.0)), np.finfo(float).eps)
        try:
            path_length = float(nx.average_shortest_path_length(gg, weight="distance"))
        except nx.NetworkXError:
            pass
    try:
        communities = list(nx.community.greedy_modularity_communities(g, weight="weight"))
        modularity = float(nx.community.modularity(g, communities, weight="weight")) if g.number_of_edges() else 0.0
    except (nx.NetworkXError, ZeroDivisionError):
        communities, modularity = [], float("nan")
    return {
        "n_nodes": n,
        "n_edges": g.number_of_edges(),
        "observed_density": float(nx.density(g)),
        "mean_degree": float(degree.mean()) if n else 0.0,
        "min_degree": int(degree.min()) if n else 0,
        "max_degree": int(degree.max()) if n else 0,
        "mean_strength": float(strength.mean()) if n else 0.0,
        "std_strength": float(strength.std(ddof=1)) if n > 1 else 0.0,
        "mean_clustering": float(np.mean(list(clustering.values()))) if n else 0.0,
        "std_clustering": float(np.std(list(clustering.values()), ddof=1)) if n > 1 else 0.0,
        "num_components": len(components),
        "largest_component": len(giant),
        "largest_component_fraction": len(giant) / n if n else float("nan"),
        "num_communities_greedy": len(communities),
        "modularity_greedy": modularity,
        "global_efficiency_unweighted": float(nx.global_efficiency(g)),
        "giant_component_path_length_inverse_weight": path_length,
        "mean_betweenness": float(np.mean(list(nx.betweenness_centrality(g).values()))) if n else 0.0,
    }


def gsp_features(adjacency: np.ndarray, time_by_node: np.ndarray) -> dict:
    """Normalized-Laplacian spectrum and energy summaries for the mean node signal."""
    a = np.asarray(adjacency, dtype=float)
    x = np.asarray(time_by_node, dtype=float)
    n = a.shape[0]
    if a.shape != (n, n) or x.ndim != 2 or x.shape[1] != n:
        raise ValueError("Adjacency and time-series node dimensions do not match.")
    degree = a.sum(axis=1)
    inv = np.zeros_like(degree)
    inv[degree > 0] = 1.0 / np.sqrt(degree[degree > 0])
    lap = np.eye(n) - (inv[:, None] * a * inv[None, :])
    lap[degree == 0, degree == 0] = 0.0
    eigenvalues, eigenvectors = np.linalg.eigh(lap)
    signal = x.mean(axis=0)
    coefficients = eigenvectors.T @ signal
    energy = coefficients ** 2
    total = float(energy.sum())
    probability = energy / total if total > 0 else np.zeros_like(energy)
    split = max(1, n // 3)
    low = float(energy[:split].sum())
    mid = float(energy[split:2 * split].sum())
    high = float(energy[2 * split:].sum())
    entropy = float(-np.sum(probability[probability > 0] * np.log(probability[probability > 0])))
    return {
        "lambda_min": float(eigenvalues.min()),
        "lambda_max": float(eigenvalues.max()),
        "lambda_mean": float(eigenvalues.mean()),
        "low_graph_energy": low,
        "mid_graph_energy": mid,
        "high_graph_energy": high,
        "low_high_energy_ratio": low / high if high > 0 else float("nan"),
        "spectral_entropy": entropy,
        "mean_graph_smoothness": float(signal @ lap @ signal),
        "eigenvalues": eigenvalues,
        "spectral_energy": energy,
    }


def persistent_homology_features(adjacency: np.ndarray, threshold: float = 1.0) -> dict:
    """H0/H1 persistence summaries from the project's 1 - normalized |FC| filtration."""
    if ripser is None:
        raise ImportError("Install ripser first: pip install ripser")
    a = np.asarray(adjacency, dtype=float)
    maximum = float(a.max()) if a.size else 0.0
    similarity = a / maximum if maximum > 0 else a.copy()
    distance = np.clip(1.0 - similarity, 0.0, 1.0)
    distance = (distance + distance.T) / 2.0
    np.fill_diagonal(distance, 0.0)
    diagrams = ripser(distance, distance_matrix=True, maxdim=1, thresh=threshold)["dgms"]
    result = {"tda_threshold": float(threshold), "tda_n_nodes": len(a)}
    for dim, label in ((0, "H0"), (1, "H1")):
        bars = []
        if dim < len(diagrams):
            for birth, death in diagrams[dim]:
                if np.isfinite(birth) and np.isfinite(death):
                    bars.append(max(0.0, float(death - birth)))
        result[f"{label}_finite_bars"] = len(bars)
        result[f"{label}_max_persistence"] = max(bars) if bars else 0.0
        result[f"{label}_mean_persistence"] = float(np.mean(bars)) if bars else 0.0
        result[f"{label}_total_persistence"] = float(np.sum(bars)) if bars else 0.0
    return result


def load_timeseries(path, orientation="time_nodes"):
    x = np.load(path)
    if x.ndim != 2:
        raise ValueError(f"Expected 2-D .npy array, got {x.shape}")
    if orientation == "nodes_time":
        x = x.T
    elif orientation != "time_nodes":
        raise ValueError("orientation must be time_nodes or nodes_time")
    if not np.isfinite(x).all():
        raise ValueError("Time series contains NaN or infinite values.")
    return np.asarray(x, dtype=float)


def run_timeseries(input_path, outdir, orientation="time_nodes", density=DEFAULT_DENSITY):
    out = ensure_dir(outdir)
    x = load_timeseries(input_path, orientation)
    fc = functional_connectivity(x)
    adjacency = threshold_absolute_fc(fc, density)
    graph = graph_theory_features(adjacency)
    gsp = gsp_features(adjacency, x)
    tda = persistent_homology_features(adjacency)
    row = {
        "subject_id": Path(input_path).stem,
        "n_timepoints": len(x),
        "n_nodes": x.shape[1],
        "target_density": density,
        **graph,
        **{k: v for k, v in gsp.items() if k not in ("eigenvalues", "spectral_energy")},
        **tda,
    }
    pd.DataFrame([row]).to_csv(out / "multiscale_features.csv", index=False)
    np.save(out / "functional_connectivity.npy", fc)
    np.save(out / "adjacency.npy", adjacency)
    np.save(out / "laplacian_eigenvalues.npy", gsp["eigenvalues"])
    np.save(out / "graph_spectral_energy.npy", gsp["spectral_energy"])
    with open(out / "features.json", "w", encoding="utf-8") as handle:
        json.dump(row, handle, indent=2, allow_nan=True)
    print(json.dumps(row, indent=2, allow_nan=True))


def describe_csv(input_csv, outdir):
    out = ensure_dir(outdir)
    df = pd.read_csv(input_csv)
    numeric = df.select_dtypes(include=[np.number])
    numeric.describe().T.assign(missing=numeric.isna().sum()).to_csv(out / "descriptive_statistics.csv")
    quality = pd.DataFrame({
        "column": df.columns.astype(str),
        "dtype": [str(df[c].dtype) for c in df.columns],
        "missing_count": [int(df[c].isna().sum()) for c in df.columns],
        "unique_count": [int(df[c].nunique(dropna=True)) for c in df.columns],
    })
    quality.to_csv(out / "data_quality.csv", index=False)
    print(f"{len(df)} rows, {len(df.columns)} columns; wrote summaries to {out}")


def main():
    parser = argparse.ArgumentParser(description="Multiscale functional brain-network analysis")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("summarize", help="Descriptive summary and data-quality audit for a feature CSV")
    p.add_argument("--input", required=True)
    p.add_argument("--outdir", required=True)
    p = sub.add_parser("timeseries", help="Run FC + graph + GSP + TDA for a .npy array")
    p.add_argument("--input", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--orientation", choices=["time_nodes", "nodes_time"], default="time_nodes")
    p.add_argument("--density", type=float, default=DEFAULT_DENSITY)
    args = parser.parse_args()
    if args.command == "summarize":
        describe_csv(args.input, args.outdir)
    elif args.command == "timeseries":
        run_timeseries(args.input, args.outdir, args.orientation, args.density)


if __name__ == "__main__":
    main()
