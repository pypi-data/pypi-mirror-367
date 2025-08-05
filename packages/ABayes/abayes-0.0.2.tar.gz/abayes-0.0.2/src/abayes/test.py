"""
Main Bayesian A/B testing interface following Kruschke's BEST methodology.

Provides the primary user interface for conducting Bayesian A/B tests with:
- Multiple metric types (conversion, revenue, retention)
- Robust statistical modeling
- ROPE-based decision making
- Sequential testing support
"""

import jax
import jax.numpy as jnp
import polars as pl
from beartype import beartype
from beartype.typing import Dict, List, Optional
from numpyro.infer import MCMC, NUTS

from .config import ExperimentConfig
from .data import Dataset, TimeSeriesDataset
from .models import select_model
from .results import TestResults


class BayesianTest:
    """
    Main interface for Bayesian A/B testing.

    Implements Kruschke's BEST methodology with modern tools:
    - Numpyro for probabilistic modeling
    - JAX for efficient computation
    - Polars for data processing
    - ROPE for principled decision making
    """

    @beartype
    def __init__(self, config: ExperimentConfig):
        """
        Initialize Bayesian A/B test.

        Args:
            config: Experiment configuration
        """
        self.config = config
        self.data: Optional[pl.DataFrame] = None

        # Validate configuration
        self.config.validate_config()

    @beartype
    def add_data(self, df: pl.DataFrame) -> None:
        """
        Add experiment data via Polars DataFrame.

        Expected columns:
        - variant: Variant assignment (control/treatment)
        - outcome: Outcome measurement
        - Optional: user_id, timestamp, covariates

        Args:
            df: DataFrame with experiment data
        """
        # Validate required columns
        required_cols = ["variant", "outcome"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Concatenate with existing data
        if self.data is None:
            self.data = df
        else:
            self.data = pl.concat([self.data, df])

    @beartype
    def analyze(self) -> TestResults:
        """
        Run Bayesian analysis and return results.

        Returns:
            TestResults object with posterior samples and analysis methods
        """
        if self.data is None:
            raise ValueError("No data added to test")

        # Check minimum sample size
        total_samples = len(self.data)
        if total_samples < self.config.min_samples:
            raise ValueError(f"Insufficient data: {total_samples} < {self.config.min_samples}")

        # Convert to appropriate format for model
        model_data = self._to_jax_format()

        # Run MCMC inference
        samples = self._run_inference(model_data)

        return TestResults(self.config, samples, self.data)

    @beartype
    def _to_jax_format(self) -> Dict:
        """
        Convert Polars data to JAX format for Numpyro models.

        Returns:
            Dictionary with model-appropriate data arrays
        """
        if self.config.metric == "conversion":
            return self._prepare_conversion_data()
        elif self.config.metric == "revenue":
            return self._prepare_revenue_data()
        elif self.config.metric == "retention":
            return self._prepare_retention_data()
        else:
            raise ValueError(f"Unknown metric: {self.config.metric}")

    def _prepare_conversion_data(self) -> Dict[str, int]:
        """Prepare data for Beta-Binomial conversion model"""
        # Group by variant and calculate success/trial counts
        summary = self.data.group_by("variant").agg(
            [pl.sum("outcome").alias("successes"), pl.len().alias("trials")]
        )

        # Extract control and treatment data
        control_row = summary.filter(pl.col("variant") == "control")
        treatment_row = summary.filter(pl.col("variant") == "treatment")

        if len(control_row) == 0 or len(treatment_row) == 0:
            raise ValueError("Missing control or treatment data")

        return {
            "control_successes": int(control_row["successes"][0]),
            "control_trials": int(control_row["trials"][0]),
            "treatment_successes": int(treatment_row["successes"][0]),
            "treatment_trials": int(treatment_row["trials"][0]),
        }

    def _prepare_revenue_data(self) -> Dict[str, jnp.ndarray]:
        """Prepare data for Student-t revenue model"""
        control_data = self.data.filter(pl.col("variant") == "control")["outcome"].to_numpy()
        treatment_data = self.data.filter(pl.col("variant") == "treatment")["outcome"].to_numpy()

        if len(control_data) == 0 or len(treatment_data) == 0:
            raise ValueError("Missing control or treatment data")

        return {
            "control_data": jnp.array(control_data),
            "treatment_data": jnp.array(treatment_data),
        }

    def _prepare_retention_data(self) -> Dict[str, jnp.ndarray]:
        """Prepare data for survival retention model"""
        # For survival analysis, outcome is time-to-event
        # Need censoring indicators (assume all observed for now)

        control_data = self.data.filter(pl.col("variant") == "control")
        treatment_data = self.data.filter(pl.col("variant") == "treatment")

        if len(control_data) == 0 or len(treatment_data) == 0:
            raise ValueError("Missing control or treatment data")

        # Extract survival times
        control_times = jnp.array(control_data["outcome"].to_numpy())
        treatment_times = jnp.array(treatment_data["outcome"].to_numpy())

        # Check for censoring column, otherwise assume all observed
        if "censored" in self.data.columns:
            control_censored = jnp.array(control_data["censored"].to_numpy(), dtype=jnp.int32)
            treatment_censored = jnp.array(treatment_data["censored"].to_numpy(), dtype=jnp.int32)
        else:
            # All events observed (not censored)
            control_censored = jnp.zeros(len(control_times), dtype=jnp.int32)
            treatment_censored = jnp.zeros(len(treatment_times), dtype=jnp.int32)

        return {
            "control_times": control_times,
            "control_censored": control_censored,
            "treatment_times": treatment_times,
            "treatment_censored": treatment_censored,
        }

    @beartype
    def _run_inference(self, data: Dict) -> Dict[str, jnp.ndarray]:
        """
        Run Numpyro MCMC inference.

        Args:
            data: Model data dictionary

        Returns:
            Posterior samples dictionary
        """
        # Select appropriate model
        model_fn = select_model(self.config)

        # Set up MCMC sampler
        kernel = NUTS(model_fn)
        mcmc = MCMC(
            kernel,
            num_samples=self.config.num_samples,
            num_warmup=self.config.num_warmup,
            num_chains=self.config.num_chains,
        )

        # Run inference
        rng_key = jax.random.PRNGKey(42)  # Fixed seed for reproducibility
        mcmc.run(rng_key, **data, config=self.config)

        # Extract samples
        samples = mcmc.get_samples()

        return samples

    @beartype
    def analyze_sequential(self, batch_size: int = None) -> List[TestResults]:
        """
        Run sequential analysis for ongoing experiments.

        Analyzes data in batches to support sequential testing
        without the false positive inflation of NHST.

        Args:
            batch_size: Size of sequential batches

        Returns:
            List of TestResults for each analysis point
        """
        if self.data is None:
            raise ValueError("No data added to test")

        if batch_size is None:
            batch_size = self.config.check_interval

        # Convert to time series dataset if timestamps available
        if "timestamp" in self.data.columns:
            ts_dataset = TimeSeriesDataset.from_polars(self.data, timestamp_col="timestamp")
            batches = ts_dataset.get_sequential_batches(batch_size)
        else:
            # Sequential batches by order
            results = []
            total_rows = len(self.data)

            for i in range(batch_size, total_rows + 1, batch_size):
                batch_data = self.data[:i]  # Cumulative data up to point i

                # Check if batch has both control and treatment data
                variants = batch_data["variant"].unique().to_list()
                has_both_variants = "control" in variants and "treatment" in variants

                if len(batch_data) >= self.config.min_samples and has_both_variants:
                    # Create temporary test with batch data
                    temp_test = BayesianTest(self.config)
                    temp_test.data = batch_data

                    try:
                        result = temp_test.analyze()
                        results.append(result)
                    except ValueError as e:
                        # Skip batches that can't be analyzed (e.g., missing data)
                        print(f"⚠️ Skipping batch at size {i}: {e}")
                        continue

            return results

        # Analyze each batch
        results = []
        for batch_dataset in batches:
            # Convert back to DataFrame for analysis
            # This is a simplification - in practice might want to keep Dataset format
            batch_df = self._dataset_to_dataframe(batch_dataset)

            temp_test = BayesianTest(self.config)
            temp_test.data = batch_df

            if len(batch_df) >= self.config.min_samples:
                result = temp_test.analyze()
                results.append(result)

        return results

    def _dataset_to_dataframe(self, dataset: Dataset) -> pl.DataFrame:
        """Convert Dataset back to DataFrame format (helper method)"""
        # This is a simplified conversion - would need more sophisticated handling
        # for different metric types and metadata preservation

        control_df = pl.DataFrame(
            {"variant": ["control"] * len(dataset.control), "outcome": dataset.control.tolist()}
        )

        treatment_df = pl.DataFrame(
            {
                "variant": ["treatment"] * len(dataset.treatment),
                "outcome": dataset.treatment.tolist(),
            }
        )

        return pl.concat([control_df, treatment_df])
