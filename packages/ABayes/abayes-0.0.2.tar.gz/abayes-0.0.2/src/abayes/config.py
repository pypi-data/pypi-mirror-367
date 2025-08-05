"""
Configuration management for Bayesian A/B testing experiments.

Uses Hydra for configuration management with Pydantic models for validation.
Follows Kruschke's BEST principles with configurable priors and ROPE parameters.
"""

from dataclasses import dataclass, field

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Tuple
from hydra.core.config_store import ConfigStore


@dataclass
class ExperimentConfig:
    """
    Hydra-compatible configuration for Bayesian A/B tests.

    Designed around Kruschke's BEST methodology with support for:
    - Different metric types (conversion, revenue, retention)
    - Configurable priors following BEST principles
    - ROPE (Region of Practical Equivalence) parameters
    - Sequential testing parameters
    - Robust modeling options
    """

    # Experiment identification
    name: str
    metric: str  # "conversion", "revenue", "retention"
    variants: List[str] = field(default_factory=lambda: ["control", "treatment"])

    # Prior configuration - following Kruschke's recommendations
    prior_type: str = "beta"  # "beta", "normal", "student_t", "gamma", "exponential"
    prior_params: Optional[Dict[str, Any]] = None

    # ROPE (Region of Practical Equivalence) - key BEST concept
    rope_bounds: Tuple[float, float] = (-0.01, 0.01)  # Default: ±1% difference

    # Analysis parameters
    credible_interval: float = 0.95  # Following Kruschke's standard
    min_samples: int = 100
    max_samples: Optional[int] = None

    # Sequential testing (avoiding NHST problems)
    check_interval: int = 100  # How often to check for stopping

    # Robust modeling (core BEST feature)
    use_student_t: bool = True  # Handle outliers like original BEST
    nu_prior_params: Dict[str, float] = field(
        default_factory=lambda: {"rate": 1 / 29}  # Kruschke's choice: mean of 29
    )

    # MCMC parameters
    num_samples: int = 2000
    num_warmup: int = 1000
    num_chains: int = 4

    def __post_init__(self):
        """Set default prior parameters based on metric type"""
        if self.prior_params is None:
            self.prior_params = self._get_default_priors()

    @beartype
    def _get_default_priors(self) -> Dict[str, Any]:
        """
        Get default prior parameters following BEST principles.

        Returns appropriate priors for different metric types based on
        Kruschke's recommendations and common A/B testing scenarios.
        """
        if self.metric == "conversion":
            # Beta-Binomial model: use weak Beta(1,1) = Uniform prior
            return {"alpha": 1.0, "beta": 1.0}

        elif self.metric == "revenue":
            # Student-t model: broad, non-committal priors
            return {
                "mu_mean": 0.0,  # Center prior at 0 (no difference expected)
                "mu_scale": 1000.0,  # Very broad prior on means
                "sigma_low": 0.001,  # Very small lower bound
                "sigma_high": 1000.0,  # Very large upper bound
            }

        elif self.metric == "retention":
            # Survival/Exponential model
            return {"rate": 1.0}  # Exponential rate parameter

        else:
            raise ValueError(f"Unknown metric type: {self.metric}")

    @beartype
    def get_rope_bounds_for_metric(self) -> Tuple[float, float]:
        """
        Get appropriate ROPE bounds for the metric type.

        Returns bounds scaled appropriately for different metrics,
        following practical significance thresholds.
        """
        if self.metric == "conversion":
            # For conversion rates, default ±1% is reasonable
            return self.rope_bounds

        elif self.metric == "revenue":
            # For revenue, might want larger absolute bounds
            if self.rope_bounds == (-0.01, 0.01):  # Default
                return (-5.0, 5.0)  # ±$5 default for revenue
            return self.rope_bounds

        elif self.metric == "retention":
            # For retention (time-based), depends on time scale
            return self.rope_bounds

        else:
            return self.rope_bounds

    @beartype
    def validate_config(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.credible_interval <= 0 or self.credible_interval >= 1:
            raise ValueError("credible_interval must be between 0 and 1")

        if self.min_samples < 2:
            raise ValueError("min_samples must be at least 2")

        if self.max_samples is not None and self.max_samples < self.min_samples:
            raise ValueError("max_samples must be >= min_samples")

        if self.rope_bounds[0] >= self.rope_bounds[1]:
            raise ValueError("ROPE lower bound must be < upper bound")

        if self.metric not in ["conversion", "revenue", "retention"]:
            raise ValueError(f"Unsupported metric type: {self.metric}")

        if len(self.variants) < 2:
            raise ValueError("Must have at least 2 variants")


@dataclass
class ConversionConfig(ExperimentConfig):
    """Specialized config for conversion experiments"""

    metric: str = field(default="conversion", init=False)
    prior_type: str = "beta"
    rope_bounds: Tuple[float, float] = (-0.01, 0.01)  # ±1% conversion rate


@dataclass
class RevenueConfig(ExperimentConfig):
    """Specialized config for revenue experiments"""

    metric: str = field(default="revenue", init=False)
    prior_type: str = "student_t"
    rope_bounds: Tuple[float, float] = (-5.0, 5.0)  # ±$5 revenue
    use_student_t: bool = True  # Essential for revenue (outliers)


@dataclass
class RetentionConfig(ExperimentConfig):
    """Specialized config for retention/survival experiments"""

    metric: str = field(default="retention", init=False)
    prior_type: str = "exponential"
    rope_bounds: Tuple[float, float] = (-0.1, 0.1)  # ±0.1 time units


# Register configs with Hydra
def register_configs():
    """Register configuration schemas with Hydra ConfigStore"""
    cs = ConfigStore.instance()

    # Base config
    cs.store(name="base_config", node=ExperimentConfig)

    # Specialized configs
    cs.store(name="conversion_config", node=ConversionConfig)
    cs.store(name="revenue_config", node=RevenueConfig)
    cs.store(name="retention_config", node=RetentionConfig)


# Auto-register when module is imported
register_configs()
