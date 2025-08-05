from abayes.config import ExperimentConfig


class TestExperimentConfig:
    """Test experiment configuration"""

    def test_conversion_config(self):
        """Test configuration for conversion experiments"""
        config = ExperimentConfig(
            name="signup_test",
            metric="conversion",
            variants=["control", "treatment"],
            prior_type="beta",
            prior_params={"alpha": 1, "beta": 1},
        )

        assert config.name == "signup_test"
        assert config.metric == "conversion"
        assert config.prior_type == "beta"
        assert config.rope_bounds == (-0.01, 0.01)  # Default
        assert config.credible_interval == 0.95

    def test_revenue_config(self):
        """Test configuration for revenue experiments"""
        config = ExperimentConfig(
            name="pricing_test",
            metric="revenue",
            variants=["control", "treatment"],
            prior_type="student_t",
            prior_params={"nu": 3, "mu": 0, "sigma": 1},
            rope_bounds=(-5.0, 5.0),  # Custom ROPE for revenue
        )

        assert config.metric == "revenue"
        assert config.prior_type == "student_t"
        assert config.rope_bounds == (-5.0, 5.0)

    def test_retention_config(self):
        """Test configuration for retention/survival experiments"""
        config = ExperimentConfig(
            name="retention_test",
            metric="retention",
            variants=["control", "treatment"],
            prior_type="exponential",
            prior_params={"rate": 1.0},
        )

        assert config.metric == "retention"
        assert config.prior_type == "exponential"

    def test_sequential_testing_config(self):
        """Test configuration for sequential testing"""
        config = ExperimentConfig(
            name="sequential_test",
            metric="conversion",
            variants=["control", "treatment"],
            min_samples=100,
            max_samples=10000,
            check_interval=500,
        )

        assert config.min_samples == 100
        assert config.max_samples == 10000
        assert config.check_interval == 500

    def test_robust_modeling_config(self):
        """Test configuration for robust modeling (Student-t)"""
        config = ExperimentConfig(
            name="robust_test",
            metric="revenue",
            variants=["control", "treatment"],
            use_student_t=True,
            nu_prior_params={"rate": 1 / 29},  # Following Kruschke's choice
        )

        assert config.use_student_t is True
        assert config.nu_prior_params["rate"] == 1 / 29


class TestHydraIntegration:
    """Test Hydra configuration management"""

    def test_hydra_config_loading(self):
        """Test loading config through Hydra"""
        # This would test actual Hydra integration
        # For now, just test that our config is compatible
        config = ExperimentConfig(
            name="test", metric="conversion", variants=["control", "treatment"]
        )

        # Test that config can be serialized/deserialized
        config_dict = {
            "name": config.name,
            "metric": config.metric,
            "variants": config.variants,
            "prior_type": config.prior_type,
            "credible_interval": config.credible_interval,
        }

        new_config = ExperimentConfig(**config_dict)
        assert new_config.name == config.name
        assert new_config.metric == config.metric
