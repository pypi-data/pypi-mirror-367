"""
Results analysis following Kruschke's BEST methodology.

Provides rich posterior analysis including:
- ROPE (Region of Practical Equivalence) decisions
- Probability calculations
- Effect size estimation
- Business-friendly summaries

All following the principled Bayesian approach from BEST.
"""

import jax.numpy as jnp
import polars as pl
from beartype import beartype
from beartype.typing import Any, Dict, Optional, Tuple
from jaxtyping import Array, Float

from .config import ExperimentConfig


class TestResults:
    """
    Results container with posterior samples and BEST-style analysis.

    Provides rich information following Kruschke's approach:
    - Complete posterior distributions
    - ROPE-based decisions
    - Probability calculations
    - Effect size analysis
    """

    @beartype
    def __init__(
        self,
        config: ExperimentConfig,
        samples: Dict[str, Float[Array, " N_samples"]],
        data: pl.DataFrame,
    ):
        """
        Initialize test results.

        Args:
            config: Experiment configuration
            samples: MCMC posterior samples from Numpyro
            data: Original experiment data
        """
        self.config = config
        self.samples = samples
        self.data = data

        # Validate we have required samples
        self._validate_samples()

    def _validate_samples(self) -> None:
        """Validate that required samples are present"""
        required_keys = ["difference"]

        for key in required_keys:
            if key not in self.samples:
                raise ValueError(f"Missing required sample: {key}")

    @beartype
    def prob_better(self, baseline: str = "control") -> Dict[str, float]:
        """
        Calculate P(variant > baseline) for each variant.

        Core BEST analysis: probability that treatment is better
        than control based on posterior samples.

        Args:
            baseline: Baseline variant name

        Returns:
            Dictionary of probabilities for each non-baseline variant
        """
        if self.config.metric == "conversion":
            # For conversion: P(treatment_rate > control_rate)
            control_samples = self.samples["control_rate"]
            treatment_samples = self.samples["treatment_rate"]

            prob_treatment_better = jnp.mean(treatment_samples > control_samples)
            return {"treatment": float(prob_treatment_better)}

        elif self.config.metric == "revenue":
            # For revenue: P(mu_treatment > mu_control)
            control_samples = self.samples["mu_control"]
            treatment_samples = self.samples["mu_treatment"]

            prob_treatment_better = jnp.mean(treatment_samples > control_samples)
            return {"treatment": float(prob_treatment_better)}

        elif self.config.metric == "retention":
            # For retention: P(treatment_median > control_median)
            # Higher median survival time is better
            control_samples = self.samples["control_median"]
            treatment_samples = self.samples["treatment_median"]

            prob_treatment_better = jnp.mean(treatment_samples > control_samples)
            return {"treatment": float(prob_treatment_better)}

        else:
            raise ValueError(f"Unknown metric: {self.config.metric}")

    @beartype
    def credible_intervals(self) -> Dict[str, Tuple[float, float]]:
        """
        Calculate credible intervals for all parameters.

        Returns HDI (Highest Density Interval) following Kruschke's approach.

        Returns:
            Dictionary of (lower, upper) credible intervals
        """
        alpha = 1 - self.config.credible_interval
        lower_percentile = 100 * alpha / 2
        upper_percentile = 100 * (1 - alpha / 2)

        intervals = {}

        for param_name, samples in self.samples.items():
            lower = float(jnp.percentile(samples, lower_percentile))
            upper = float(jnp.percentile(samples, upper_percentile))
            intervals[param_name] = (lower, upper)

        return intervals

    @beartype
    def rope_decision(self) -> str:
        """
        Make ROPE-based decision following Kruschke's BEST methodology.

        Core innovation of BEST: can accept null hypothesis when
        credible values fall within Region of Practical Equivalence.

        Returns:
            One of: "reject_null", "accept_null", "undecided"
        """
        rope_lower, rope_upper = self.config.get_rope_bounds_for_metric()
        difference_samples = self.samples["difference"]

        # Calculate proportion of posterior in ROPE
        in_rope = jnp.logical_and(
            difference_samples >= rope_lower, difference_samples <= rope_upper
        )

        prop_in_rope = jnp.mean(in_rope)

        # Decision thresholds (following Kruschke's recommendations)
        accept_threshold = 0.95  # 95% of posterior in ROPE
        reject_threshold = 0.05  # 5% or less of posterior in ROPE

        if prop_in_rope >= accept_threshold:
            return "accept_null"
        elif prop_in_rope <= reject_threshold:
            return "reject_null"
        else:
            return "undecided"

    @beartype
    def effect_size(self) -> Dict[str, Any]:
        """
        Calculate effect size following Kruschke's definition.

        Returns:
            Dictionary with effect size statistics
        """
        if "effect_size" not in self.samples:
            raise ValueError("Effect size not available in samples")

        effect_samples = self.samples["effect_size"]

        return {
            "mean": float(jnp.mean(effect_samples)),
            "median": float(jnp.median(effect_samples)),
            "std": float(jnp.std(effect_samples)),
            "credible_interval": self.credible_intervals()["effect_size"],
        }

    @beartype
    def summary(self) -> Dict[str, Any]:
        """
        Generate business-friendly summary.

        Returns:
            Dictionary with key business metrics and decisions
        """
        prob_better = self.prob_better()
        rope_decision = self.rope_decision()
        intervals = self.credible_intervals()

        # Determine winner
        treatment_prob = prob_better.get("treatment", 0.0)

        if rope_decision == "accept_null":
            winner = "no_difference"
        elif treatment_prob > 0.95:
            winner = "treatment"
        elif treatment_prob < 0.05:
            winner = "control"
        else:
            winner = "undecided"

        # Calculate lift
        difference_mean = float(jnp.mean(self.samples["difference"]))

        if self.config.metric == "conversion":
            # Convert to percentage points
            lift_pct = difference_mean * 100
        elif self.config.metric == "revenue":
            # Lift as dollar amount
            lift_pct = difference_mean
        else:
            lift_pct = difference_mean

        # Get sample sizes
        sample_sizes = self._get_sample_sizes()

        return {
            "winner": winner,
            "lift": lift_pct,
            "confidence": treatment_prob,
            "decision": rope_decision,
            "sample_sizes": sample_sizes,
            "credible_intervals": intervals,
            "rope_bounds": self.config.get_rope_bounds_for_metric(),
        }

    def _get_sample_sizes(self) -> Dict[str, int]:
        """Get sample sizes from data"""
        if "variant" in self.data.columns:
            # Convert Polars result to proper dict format
            grouped = self.data.group_by("variant").agg(pl.len().alias("count"))
            # Convert to proper Dict[str, int] format
            result = {}
            variants = grouped["variant"].to_list()
            counts = grouped["count"].to_list()
            for variant, count in zip(variants, counts):
                result[variant] = count
            return result
        else:
            # Fallback if no variant column
            return {"total": len(self.data)}

    @beartype
    def posterior_summary_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Comprehensive posterior summary statistics.

        Returns:
            Nested dictionary with summary stats for each parameter
        """
        stats = {}

        for param_name, samples in self.samples.items():
            stats[param_name] = {
                "mean": float(jnp.mean(samples)),
                "median": float(jnp.median(samples)),
                "std": float(jnp.std(samples)),
                "var": float(jnp.var(samples)),
                "min": float(jnp.min(samples)),
                "max": float(jnp.max(samples)),
                "q25": float(jnp.percentile(samples, 25)),
                "q75": float(jnp.percentile(samples, 75)),
            }

        return stats

    @beartype
    def diagnostic_summary(self) -> Dict[str, Any]:
        """
        MCMC diagnostic summary.

        Returns:
            Dictionary with convergence diagnostics
        """
        # Basic diagnostics - could be extended with more sophisticated checks
        diagnostics = {
            "n_samples": len(list(self.samples.values())[0]),
            "n_parameters": len(self.samples),
            "parameter_names": list(self.samples.keys()),
        }

        # Check for any NaN or infinite values
        for param_name, samples in self.samples.items():
            diagnostics[f"{param_name}_has_nan"] = bool(jnp.any(jnp.isnan(samples)))
            diagnostics[f"{param_name}_has_inf"] = bool(jnp.any(jnp.isinf(samples)))

        return diagnostics
