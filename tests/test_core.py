"""Small deterministic smoke tests for the non-TDA core graph pipeline."""
import unittest
import numpy as np

import brain_network_project_master as project


class CorePipelineTests(unittest.TestCase):
    def test_connectivity_is_symmetric_and_zero_diagonal(self):
        rng = np.random.default_rng(7)
        x = rng.normal(size=(120, 12))
        fc = project.functional_connectivity(x)
        self.assertEqual(fc.shape, (12, 12))
        self.assertTrue(np.allclose(fc, fc.T))
        self.assertTrue(np.allclose(np.diag(fc), 0.0))

    def test_threshold_has_expected_edge_count(self):
        rng = np.random.default_rng(9)
        x = rng.normal(size=(150, 20))
        fc = project.functional_connectivity(x)
        density = 0.20
        adjacency = project.threshold_absolute_fc(fc, density=density)
        observed = int(np.count_nonzero(np.triu(adjacency, 1)))
        possible = 20 * 19 // 2
        expected = max(1, min(possible, int(round(density * possible))))
        self.assertEqual(observed, expected)
        self.assertTrue(np.allclose(adjacency, adjacency.T))

    def test_graph_and_gsp_features_are_finite(self):
        rng = np.random.default_rng(11)
        x = rng.normal(size=(200, 15))
        fc = project.functional_connectivity(x)
        adjacency = project.threshold_absolute_fc(fc, density=0.25)
        graph = project.graph_theory_features(adjacency)
        gsp = project.gsp_features(adjacency, x)
        self.assertEqual(graph["n_nodes"], 15)
        self.assertTrue(np.isfinite(graph["modularity_greedy"]))
        self.assertTrue(np.isfinite(gsp["lambda_max"]))
        self.assertEqual(len(gsp["eigenvalues"]), 15)


if __name__ == "__main__":
    unittest.main()
