from datetime import datetime, timedelta

import jax.numpy as jnp
import polars as pl

from abayes.data import Dataset, TimeSeriesDataset


class TestDataset:
    """Test basic Dataset functionality"""

    def test_dataset_creation(self):
        """Test creating a basic dataset with control and treatment data"""
        control = jnp.array([1, 0, 1, 0, 1], dtype=jnp.float32)
        treatment = jnp.array([1, 1, 0, 1, 1], dtype=jnp.float32)

        dataset = Dataset(control=control, treatment=treatment)

        assert dataset.control.shape == (5,)
        assert dataset.treatment.shape == (5,)
        assert dataset.covariates is None

    def test_dataset_with_covariates(self):
        """Test dataset creation with covariates"""
        control = jnp.array([1.2, 0.8, 1.5])
        treatment = jnp.array([1.8, 1.1, 2.0])
        covariates = jnp.array([[25, 1], [30, 0], [28, 1]], dtype=jnp.float32)  # age, gender

        dataset = Dataset(control=control, treatment=treatment, covariates=covariates)

        assert dataset.control.shape == (3,)
        assert dataset.treatment.shape == (3,)
        assert dataset.covariates.shape == (3, 2)

    def test_dataset_from_polars(self):
        """Test creating dataset from Polars DataFrame"""
        df = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
                "age": [25, 30, 28, 35],
                "gender": [1, 0, 1, 0],
            }
        )

        dataset = Dataset.from_polars(df, outcome_col="outcome", covariate_cols=["age", "gender"])

        assert len(dataset.control) == 2  # 2 control observations
        assert len(dataset.treatment) == 2  # 2 treatment observations
        assert dataset.covariates.shape[1] == 2  # 2 covariates


class TestTimeSeriesDataset:
    """Test time series dataset functionality"""

    def test_timeseries_creation(self):
        """Test creating a time series dataset"""
        control = jnp.array([1, 0, 1, 0], dtype=jnp.float32)
        treatment = jnp.array([1, 1, 0, 1], dtype=jnp.float32)
        timestamps = jnp.array([1, 2, 3, 4], dtype=jnp.float32)  # Simple integer timestamps

        ts_dataset = TimeSeriesDataset(control=control, treatment=treatment, timestamps=timestamps)

        assert ts_dataset.control.shape == (4,)
        assert ts_dataset.treatment.shape == (4,)
        assert ts_dataset.timestamps.shape == (4,)

    def test_timeseries_from_polars(self):
        """Test creating time series dataset from Polars DataFrame"""
        dates = [
            datetime.now() - timedelta(days=3),
            datetime.now() - timedelta(days=2),
            datetime.now() - timedelta(days=1),
            datetime.now(),
        ]

        df = pl.DataFrame(
            {
                "variant": ["control", "treatment", "control", "treatment"],
                "outcome": [1, 1, 0, 1],
                "timestamp": dates,
                "user_id": [1, 2, 3, 4],
            }
        )

        ts_dataset = TimeSeriesDataset.from_polars(
            df, outcome_col="outcome", timestamp_col="timestamp"
        )

        assert len(ts_dataset.control) == 2
        assert len(ts_dataset.treatment) == 2
        assert len(ts_dataset.timestamps) == 4
        assert len(ts_dataset.control) == 2
        assert len(ts_dataset.treatment) == 2
        assert len(ts_dataset.timestamps) == 4
