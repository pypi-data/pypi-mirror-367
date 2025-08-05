"""
BayesAB: Bayesian A/B Testing following Kruschke's BEST methodology.

A modern Python library for principled Bayesian A/B testing with:
- Robust statistical models (Beta-Binomial, Student-t, Survival)
- ROPE-based decision making
- Sequential testing support
- Rich posterior analysis

Built with:
- Numpyro for probabilistic modeling
- JAX for efficient computation
- Polars for data processing
- Pydantic for type safety
- Hydra for configuration
"""

__version__ = "0.0.2"
__author__ = "BayesAB Team"
__email__ = "team@abayes.dev"

from beartype.claw import beartype_this_package

beartype_this_package()

from .config import ConversionConfig, ExperimentConfig, RetentionConfig, RevenueConfig
from .data import Dataset, TimeSeriesDataset
from .results import TestResults
from .test import BayesianTest

# Plotting functions (optional import)
try:
    from . import plotting

    _plotting_available = True
except ImportError:
    _plotting_available = False
    plotting = None

__all__ = [
    "ExperimentConfig",
    "ConversionConfig",
    "RevenueConfig",
    "RetentionConfig",
    "Dataset",
    "TimeSeriesDataset",
    "BayesianTest",
    "TestResults",
]

# Add plotting to __all__ if available
if _plotting_available:
    __all__.append("plotting")

# Add plotting to __all__ if available
if _plotting_available:
    __all__.append("plotting")
