import jax.numpy as jnp
import polars as pl

from abayes.config import ExperimentConfig
from abayes.results import TestResults


class TestTestResults:
    """Test TestResults functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = ExperimentConfig(
            name="test_experiment",
            metric="conversion",
            variants=["control", "treatment"],
            rope_bounds=(-0.02, 0.02),
            credible_interval=0.95,
        )

        # Mock MCMC samples
        self.samples = {
            "control_rate": jnp.array([0.10, 0.12, 0.11, 0.13, 0.09]),
            "treatment_rate": jnp.array([0.15, 0.17, 0.16, 0.18, 0.14]),
            "difference": jnp.array([0.05, 0.05, 0.05, 0.05, 0.05]),
            "effect_size": jnp.array([0.15, 0.16, 0.14, 0.17, 0.13]),  # Mock effect sizes
        }

        self.data = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
            }
        )

    def test_initialization(self):
        """Test TestResults initialization"""
        results = TestResults(self.config, self.samples, self.data)

        assert results.config == self.config
        assert results.samples == self.samples
        assert results.data.equals(self.data)

    def test_prob_better(self):
        """Test probability calculations"""
        results = TestResults(self.config, self.samples, self.data)

        prob = results.prob_better(baseline="control")

        assert "treatment" in prob
        assert 0.0 <= prob["treatment"] <= 1.0
        # With our mock data, treatment should be better 100% of the time
        assert prob["treatment"] == 1.0

    def test_credible_intervals(self):
        """Test credible interval calculations"""
        results = TestResults(self.config, self.samples, self.data)

        intervals = results.credible_intervals()

        assert "control_rate" in intervals
        assert "treatment_rate" in intervals
        assert "difference" in intervals

        # Each interval should be a tuple of (lower, upper)
        for interval in intervals.values():
            assert len(interval) == 2
            assert interval[0] <= interval[1]

    def test_rope_decision_reject_null(self):
        """Test ROPE decision when difference is outside ROPE"""
        # Samples with large difference (outside ROPE)
        samples = {
            "control_rate": jnp.array([0.10, 0.11, 0.10, 0.12]),
            "treatment_rate": jnp.array([0.20, 0.21, 0.19, 0.22]),
            "difference": jnp.array([0.10, 0.10, 0.09, 0.10]),  # All outside ROPE (-0.02, 0.02)
        }

        results = TestResults(self.config, samples, self.data)
        decision = results.rope_decision()

        assert decision == "reject_null"

    def test_rope_decision_accept_null(self):
        """Test ROPE decision when difference is inside ROPE"""
        # Samples with small difference (inside ROPE)
        samples = {
            "control_rate": jnp.array([0.10, 0.11, 0.10, 0.12]),
            "treatment_rate": jnp.array([0.101, 0.111, 0.100, 0.121]),
            "difference": jnp.array([0.001, 0.001, 0.000, 0.001]),  # All inside ROPE
        }

        results = TestResults(self.config, samples, self.data)
        decision = results.rope_decision()

        assert decision == "accept_null"

    def test_rope_decision_undecided(self):
        """Test ROPE decision when some samples are inside, some outside ROPE"""
        # Mixed samples
        samples = {
            "control_rate": jnp.array([0.10, 0.11, 0.10, 0.12]),
            "treatment_rate": jnp.array([0.12, 0.14, 0.101, 0.13]),
            "difference": jnp.array([0.02, 0.03, 0.001, 0.01]),  # Mixed inside/outside ROPE
        }

        results = TestResults(self.config, samples, self.data)
        decision = results.rope_decision()

        assert decision == "undecided"

    def test_summary(self):
        """Test business-friendly summary"""
        results = TestResults(self.config, self.samples, self.data)

        summary = results.summary()

        required_keys = ["winner", "lift", "confidence", "sample_sizes", "decision"]
        for key in required_keys:
            assert key in summary

        assert summary["winner"] in ["control", "treatment", "undecided"]
        assert isinstance(summary["lift"], (int, float))
        assert 0.0 <= summary["confidence"] <= 1.0
        assert isinstance(summary["sample_sizes"], dict)

    def test_effect_size_calculation(self):
        """Test effect size calculation (following Kruschke's definition)"""
        results = TestResults(self.config, self.samples, self.data)

        effect_size = results.effect_size()

        assert isinstance(effect_size, dict)
        assert "mean" in effect_size
        assert "credible_interval" in effect_size

        # Effect size should be reasonable
        assert -5.0 <= effect_size["mean"] <= 5.0
