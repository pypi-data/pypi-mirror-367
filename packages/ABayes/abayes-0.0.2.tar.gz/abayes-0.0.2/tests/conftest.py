"""Shared pytest fixtures and configuration for ABayes tests."""

from hypothesis import settings

# Configure Hypothesis for property-based testing
settings.register_profile("ci", max_examples=100, deadline=None)
settings.register_profile("dev", max_examples=10, deadline=None)
settings.load_profile("dev")
