"""
Data models for Bayesian A/B testing using Pydantic and JaxTyping.

Following Kruschke's BEST principles with robust, type-safe data handling.
"""

import jax.numpy as jnp
import polars as pl
from beartype import beartype
from beartype.typing import List, Optional, Union
from jaxtyping import Array, Float, Int
from pydantic import BaseModel, ConfigDict, field_validator


class Dataset(BaseModel):
    """
    Base dataset for A/B testing experiments.

    Holds data for control and treatment groups with optional covariates,
    following the structure needed for Bayesian estimation.
    """

    control: Float[Array, " N_control"]
    treatment: Float[Array, " N_treatment"]
    covariates: Optional[Float[Array, "N_total D"]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("control", "treatment")
    @classmethod
    def validate_arrays(cls, v):
        """Ensure arrays are 1D JAX arrays with float dtype"""
        if not isinstance(v, jnp.ndarray):
            v = jnp.array(v, dtype=jnp.float32)
        if v.ndim != 1:
            raise ValueError("Control and treatment arrays must be 1-dimensional")
        # Ensure float dtype for Float[Array, ...] type annotation
        if not jnp.issubdtype(v.dtype, jnp.floating):
            v = v.astype(jnp.float32)
        return v

    @field_validator("covariates")
    @classmethod
    def validate_covariates(cls, v):
        """Ensure covariates are 2D if provided with float dtype"""
        if v is not None:
            if not isinstance(v, jnp.ndarray):
                v = jnp.array(v, dtype=jnp.float32)
            if v.ndim != 2:
                raise ValueError("Covariates must be 2-dimensional (N_samples, N_features)")
            # Ensure float dtype for Float[Array, ...] type annotation
            if not jnp.issubdtype(v.dtype, jnp.floating):
                v = v.astype(jnp.float32)
        return v

    @classmethod
    @beartype
    def from_polars(
        cls,
        df: pl.DataFrame,
        outcome_col: str = "outcome",
        variant_col: str = "variant",
        covariate_cols: Optional[List[str]] = None,
        control_name: str = "control",
        treatment_name: str = "treatment",
    ) -> "Dataset":
        """
        Create Dataset from Polars DataFrame.

        Args:
            df: DataFrame with experiment data
            outcome_col: Column name for the outcome variable
            variant_col: Column name for variant assignment
            covariate_cols: List of covariate column names
            control_name: Name of control variant
            treatment_name: Name of treatment variant

        Returns:
            Dataset instance
        """
        # Filter to control and treatment groups
        control_df = df.filter(pl.col(variant_col) == control_name)
        treatment_df = df.filter(pl.col(variant_col) == treatment_name)

        if len(control_df) == 0:
            raise ValueError(f"No control group data found (looking for '{control_name}')")
        if len(treatment_df) == 0:
            raise ValueError(f"No treatment group data found (looking for '{treatment_name}')")

        # Extract outcome data (ensure float32 for consistency)
        control_data = jnp.array(control_df[outcome_col].to_numpy(), dtype=jnp.float32)
        treatment_data = jnp.array(treatment_df[outcome_col].to_numpy(), dtype=jnp.float32)

        # Extract covariates if specified
        covariates = None
        if covariate_cols:
            # Combine control and treatment for covariates
            combined_df = pl.concat([control_df, treatment_df])
            covariates = jnp.array(combined_df[covariate_cols].to_numpy(), dtype=jnp.float32)

        return cls(control=control_data, treatment=treatment_data, covariates=covariates)

    @property
    def n_control(self) -> int:
        """Number of control observations"""
        return len(self.control)

    @property
    def n_treatment(self) -> int:
        """Number of treatment observations"""
        return len(self.treatment)

    @property
    def n_total(self) -> int:
        """Total number of observations"""
        return self.n_control + self.n_treatment


class TimeSeriesDataset(Dataset):
    """
    Time series dataset for sequential A/B testing.

    Extends base Dataset with timestamp information for analyzing
    experiments over time and implementing sequential testing.
    """

    timestamps: Float[Array, " N_total"]

    @field_validator("timestamps")
    @classmethod
    def validate_timestamps(cls, v):
        """Ensure timestamps are 1D with float dtype"""
        if not isinstance(v, jnp.ndarray):
            v = jnp.array(v, dtype=jnp.float32)
        if v.ndim != 1:
            raise ValueError("Timestamps must be 1-dimensional")
        # Ensure float dtype for Float[Array, ...] type annotation
        if not jnp.issubdtype(v.dtype, jnp.floating):
            v = v.astype(jnp.float32)
        # Note: Not enforcing monotonic here as data might be shuffled
        return v

    @classmethod
    @beartype
    def from_polars(
        cls,
        df: pl.DataFrame,
        outcome_col: str = "outcome",
        variant_col: str = "variant",
        timestamp_col: str = "timestamp",
        covariate_cols: Optional[List[str]] = None,
        control_name: str = "control",
        treatment_name: str = "treatment",
    ) -> "TimeSeriesDataset":
        """
        Create TimeSeriesDataset from Polars DataFrame.

        Args:
            df: DataFrame with experiment data
            outcome_col: Column name for the outcome variable
            variant_col: Column name for variant assignment
            timestamp_col: Column name for timestamps
            covariate_cols: List of covariate column names
            control_name: Name of control variant
            treatment_name: Name of treatment variant

        Returns:
            TimeSeriesDataset instance
        """
        # Sort by timestamp for proper time series analysis
        df_sorted = df.sort(timestamp_col)

        # Get base dataset
        base_dataset = Dataset.from_polars(
            df_sorted, outcome_col, variant_col, covariate_cols, control_name, treatment_name
        )

        # Extract timestamps - need to handle different timestamp formats
        if df_sorted[timestamp_col].dtype == pl.Datetime:
            # Convert datetime to Unix timestamp (seconds since epoch)
            timestamps = jnp.array(
                df_sorted[timestamp_col].dt.timestamp().to_numpy() / 1e6  # microseconds to seconds
            )
        else:
            # Assume numeric timestamp
            timestamps = jnp.array(df_sorted[timestamp_col].to_numpy())

        return cls(
            control=base_dataset.control,
            treatment=base_dataset.treatment,
            covariates=base_dataset.covariates,
            timestamps=timestamps,
        )

    @beartype
    def get_data_up_to_time(self, cutoff_time: float) -> "TimeSeriesDataset":
        """
        Get subset of data up to a specific timestamp.

        Useful for sequential testing and interim analyses.

        Args:
            cutoff_time: Timestamp cutoff

        Returns:
            New TimeSeriesDataset with data up to cutoff time
        """
        mask = self.timestamps <= cutoff_time

        # Split mask by control/treatment
        control_mask = mask[: self.n_control]
        treatment_mask = mask[self.n_control :]

        new_control = self.control[control_mask]
        new_treatment = self.treatment[treatment_mask]
        new_timestamps = self.timestamps[mask]

        new_covariates = None
        if self.covariates is not None:
            new_covariates = self.covariates[mask]

        return TimeSeriesDataset(
            control=new_control,
            treatment=new_treatment,
            covariates=new_covariates,
            timestamps=new_timestamps,
        )

    @beartype
    def get_sequential_batches(self, batch_size: int) -> List["TimeSeriesDataset"]:
        """
        Split data into sequential batches for sequential testing.

        Args:
            batch_size: Number of observations per batch

        Returns:
            List of TimeSeriesDataset objects, each with cumulative data
        """
        batches = []
        total_samples = self.n_total

        for i in range(batch_size, total_samples + 1, batch_size):
            # Get data up to the i-th observation by timestamp
            cutoff_time = jnp.sort(self.timestamps)[min(i - 1, total_samples - 1)]
            batch_data = self.get_data_up_to_time(cutoff_time)

            # Only add if we have data from both groups
            if batch_data.n_control > 0 and batch_data.n_treatment > 0:
                batches.append(batch_data)

        return batches
