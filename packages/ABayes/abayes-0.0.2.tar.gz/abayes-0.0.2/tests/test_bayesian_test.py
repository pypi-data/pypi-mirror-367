from unittest.mock import patch

import jax.numpy as jnp
import polars as pl
import pytest

from abayes.config import ExperimentConfig
from abayes.test import BayesianTest


class TestBayesianTest:
    """Test main BayesianTest interface"""

    def test_initialization(self):
        """Test BayesianTest initialization"""
        config = ExperimentConfig(
            name="test_experiment", metric="conversion", variants=["control", "treatment"]
        )

        test = BayesianTest(config)

        assert test.config == config
        assert test.data is None

    def test_add_data_polars(self):
        """Test adding data via Polars DataFrame"""
        config = ExperimentConfig(
            name="test_experiment", metric="conversion", variants=["control", "treatment"]
        )

        test = BayesianTest(config)

        df = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
                "user_id": [1, 2, 3, 4],
            }
        )

        test.add_data(df)

        assert test.data is not None
        assert test.data.shape == (4, 3)

    def test_add_data_concatenation(self):
        """Test that multiple add_data calls concatenate properly"""
        config = ExperimentConfig(
            name="test_experiment", metric="conversion", variants=["control", "treatment"]
        )

        test = BayesianTest(config)

        df1 = pl.DataFrame(
            {
                "variant": ["control", "treatment"],
                "outcome": [1, 1],
            }
        )

        df2 = pl.DataFrame(
            {
                "variant": ["control", "treatment"],
                "outcome": [0, 1],
            }
        )

        test.add_data(df1)
        test.add_data(df2)

        assert test.data.shape == (4, 2)

    @patch("abayes.test.BayesianTest._run_inference")
    def test_analyze_conversion(self, mock_inference):
        """Test analysis for conversion experiments"""
        # Mock the inference results
        mock_samples = {
            "control_rate": jnp.array([0.1, 0.12, 0.11, 0.13]),
            "treatment_rate": jnp.array([0.15, 0.17, 0.16, 0.18]),
            "difference": jnp.array([0.05, 0.05, 0.05, 0.05]),
        }
        mock_inference.return_value = mock_samples

        config = ExperimentConfig(
            name="conversion_test",
            metric="conversion",
            variants=["control", "treatment"],
            min_samples=2,  # Lower minimum for testing
        )

        test = BayesianTest(config)

        df = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
            }
        )

        test.add_data(df)
        results = test.analyze()

        assert results is not None
        assert hasattr(results, "samples")
        assert hasattr(results, "config")

    def test_to_jax_format_conversion(self):
        """Test conversion to JAX format for conversion data"""
        config = ExperimentConfig(
            name="test",
            metric="conversion",
            variants=["control", "treatment"],
            min_samples=2,  # Lower minimum for testing
        )

        test = BayesianTest(config)

        df = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
            }
        )

        test.add_data(df)
        jax_data = test._to_jax_format()

        assert "control_successes" in jax_data
        assert "control_trials" in jax_data
        assert "treatment_successes" in jax_data
        assert "treatment_trials" in jax_data

        # Check values
        assert jax_data["control_successes"] == 1  # 1 success out of 2 trials
        assert jax_data["control_trials"] == 2
        assert jax_data["treatment_successes"] == 2  # 2 successes out of 2 trials
        assert jax_data["treatment_trials"] == 2

    def test_insufficient_data(self):
        """Test behavior with insufficient data"""
        config = ExperimentConfig(
            name="test", metric="conversion", variants=["control", "treatment"], min_samples=100
        )

        test = BayesianTest(config)

        df = pl.DataFrame(
            {
                "variant": ["control", "treatment"],
                "outcome": [1, 1],
            }
        )

        test.add_data(df)

        with pytest.raises(ValueError, match="Insufficient data"):
            test.analyze()
            test.analyze()
