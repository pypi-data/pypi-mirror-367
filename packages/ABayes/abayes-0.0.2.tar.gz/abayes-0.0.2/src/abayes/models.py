"""
Numpyro models for Bayesian A/B testing following Kruschke's BEST principles.

Implements robust statistical models for different metric types:
- Beta-Binomial for conversion rates
- Student-t for revenue (robust to outliers)
- Survival models for retention

All models follow BEST methodology with proper priors and robust estimation.
"""

import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist
from beartype import beartype
from jaxtyping import Array, Float, Int

from .config import ExperimentConfig


@beartype
def beta_binomial_model(
    control_successes: int,
    control_trials: int,
    treatment_successes: int,
    treatment_trials: int,
    config: ExperimentConfig,
) -> None:
    """
    Beta-Binomial model for conversion rate experiments.

    Following BEST principles with proper Beta priors and
    derived quantities for decision making.

    Args:
        control_successes: Number of conversions in control
        control_trials: Total trials in control
        treatment_successes: Number of conversions in treatment
        treatment_trials: Total trials in treatment
        config: Experiment configuration
    """
    # Prior parameters from config
    alpha = config.prior_params["alpha"]
    beta = config.prior_params["beta"]

    # Priors on conversion rates - Beta conjugate to Binomial
    control_rate = numpyro.sample("control_rate", dist.Beta(alpha, beta))
    treatment_rate = numpyro.sample("treatment_rate", dist.Beta(alpha, beta))

    # Likelihoods - convert to float32 for JAX automatic differentiation compatibility
    # The Binomial distribution requires float values, not integers, for gradient computation
    control_successes_float = jnp.array(control_successes, dtype=jnp.float32)
    treatment_successes_float = jnp.array(treatment_successes, dtype=jnp.float32)
    control_trials_float = jnp.array(control_trials, dtype=jnp.float32)
    treatment_trials_float = jnp.array(treatment_trials, dtype=jnp.float32)

    numpyro.sample(
        "control_obs",
        dist.Binomial(control_trials_float, control_rate),
        obs=control_successes_float,
    )
    numpyro.sample(
        "treatment_obs",
        dist.Binomial(treatment_trials_float, treatment_rate),
        obs=treatment_successes_float,
    )

    # Derived quantities for BEST-style analysis
    difference = numpyro.deterministic("difference", treatment_rate - control_rate)
    relative_lift = numpyro.deterministic("relative_lift", difference / control_rate)

    # Effect size (following Kruschke's definition)
    # Use the float32 arrays we already created for the likelihood
    pooled_rate = (control_successes_float + treatment_successes_float) / (
        control_trials_float + treatment_trials_float
    )
    pooled_variance = pooled_rate * (1 - pooled_rate)
    effect_size = numpyro.deterministic("effect_size", difference / jnp.sqrt(pooled_variance))


@beartype
def student_t_model(
    control_data: Float[Array, " N_control"],
    treatment_data: Float[Array, " N_treatment"],
    config: ExperimentConfig,
) -> None:
    """
    Robust Student-t model for continuous outcomes (e.g., revenue).

    Core BEST model following Kruschke's approach with:
    - Student-t distributions for robustness to outliers
    - Broad, non-committal priors
    - Shared normality parameter across groups

    Args:
        control_data: Control group observations
        treatment_data: Treatment group observations
        config: Experiment configuration
    """
    # Prior parameters
    mu_mean = config.prior_params["mu_mean"]
    mu_scale = config.prior_params["mu_scale"]
    sigma_low = config.prior_params["sigma_low"]
    sigma_high = config.prior_params["sigma_high"]

    # Pooled data statistics for scaling priors (Kruschke's approach)
    pooled_data = jnp.concatenate([control_data, treatment_data])
    pooled_mean = jnp.mean(pooled_data)
    pooled_std = jnp.std(pooled_data)

    # Scale priors by data (broad but reasonable)
    mu_scale_scaled = mu_scale * pooled_std
    sigma_high_scaled = sigma_high * pooled_std
    sigma_low_scaled = sigma_low * pooled_std

    # Priors on group means - broad normal centered on pooled mean
    mu_control = numpyro.sample("mu_control", dist.Normal(pooled_mean, mu_scale_scaled))
    mu_treatment = numpyro.sample("mu_treatment", dist.Normal(pooled_mean, mu_scale_scaled))

    # Priors on group standard deviations - uniform on reasonable range
    sigma_control = numpyro.sample(
        "sigma_control", dist.Uniform(sigma_low_scaled, sigma_high_scaled)
    )
    sigma_treatment = numpyro.sample(
        "sigma_treatment", dist.Uniform(sigma_low_scaled, sigma_high_scaled)
    )

    # Prior on normality parameter (shared across groups)
    # Following Kruschke: exponential with mean 29
    nu_rate = config.nu_prior_params["rate"]
    nu_minus_one = numpyro.sample("nu_minus_one", dist.Exponential(nu_rate))
    nu = numpyro.deterministic("nu", nu_minus_one + 1)

    # Likelihoods - Student-t for robustness
    with numpyro.plate("control", len(control_data)):
        numpyro.sample(
            "control_obs", dist.StudentT(nu, mu_control, sigma_control), obs=control_data
        )

    with numpyro.plate("treatment", len(treatment_data)):
        numpyro.sample(
            "treatment_obs", dist.StudentT(nu, mu_treatment, sigma_treatment), obs=treatment_data
        )

    # Derived quantities (BEST-style analysis)
    difference = numpyro.deterministic("difference", mu_treatment - mu_control)
    sigma_difference = numpyro.deterministic("sigma_difference", sigma_treatment - sigma_control)

    # Effect size (Kruschke's definition)
    pooled_sigma = jnp.sqrt((sigma_control**2 + sigma_treatment**2) / 2)
    effect_size = numpyro.deterministic("effect_size", difference / pooled_sigma)

    # Relative lift
    relative_lift = numpyro.deterministic("relative_lift", difference / jnp.abs(mu_control))


@beartype
def exponential_survival_model(
    control_times: Float[Array, " N_control"],
    control_censored: Int[Array, " N_control"],
    treatment_times: Float[Array, " N_treatment"],
    treatment_censored: Int[Array, " N_treatment"],
    config: ExperimentConfig,
) -> None:
    """
    Exponential survival model for retention experiments.

    Models time-to-event data with censoring, appropriate for
    retention and churn analysis.

    Args:
        control_times: Observed times for control group
        control_censored: Censoring indicators for control (1=censored, 0=observed)
        treatment_times: Observed times for treatment group
        treatment_censored: Censoring indicators for treatment
        config: Experiment configuration
    """
    # Prior parameters
    rate_prior = config.prior_params["rate"]

    # Priors on hazard rates (exponential parameters)
    control_rate = numpyro.sample("control_rate", dist.Exponential(rate_prior))
    treatment_rate = numpyro.sample("treatment_rate", dist.Exponential(rate_prior))

    # Likelihoods with censoring using vectorized approach

    # Control group likelihood
    # For observed events (censored=0): log(PDF) = log(rate) - rate * time
    # For censored events (censored=1): log(S(t)) = -rate * time
    control_observed_loglik = jnp.log(control_rate) - control_rate * control_times
    control_censored_loglik = -control_rate * control_times

    # Select appropriate likelihood based on censoring status
    control_log_prob = jnp.where(
        control_censored == 0,  # condition: not censored
        control_observed_loglik,  # if true: use observed likelihood
        control_censored_loglik,  # if false: use censored likelihood
    )
    numpyro.factor("control_likelihood", jnp.sum(control_log_prob))

    # Treatment group likelihood
    treatment_observed_loglik = jnp.log(treatment_rate) - treatment_rate * treatment_times
    treatment_censored_loglik = -treatment_rate * treatment_times

    treatment_log_prob = jnp.where(
        treatment_censored == 0,  # condition: not censored
        treatment_observed_loglik,  # if true: use observed likelihood
        treatment_censored_loglik,  # if false: use censored likelihood
    )
    numpyro.factor("treatment_likelihood", jnp.sum(treatment_log_prob))

    # Derived quantities
    # Hazard ratio
    hazard_ratio = numpyro.deterministic("hazard_ratio", treatment_rate / control_rate)

    # Median survival times
    control_median = numpyro.deterministic("control_median", jnp.log(2) / control_rate)
    treatment_median = numpyro.deterministic("treatment_median", jnp.log(2) / treatment_rate)

    # Difference in median survival times
    median_difference = numpyro.deterministic(
        "median_difference", treatment_median - control_median
    )

    # Add "difference" alias for compatibility with TestResults validation
    difference = numpyro.deterministic("difference", median_difference)


@beartype
def select_model(config: ExperimentConfig):
    """
    Select appropriate model based on metric type.

    Args:
        config: Experiment configuration

    Returns:
        Model function appropriate for the metric type
    """
    if config.metric == "conversion":
        return beta_binomial_model
    elif config.metric == "revenue":
        return student_t_model
    elif config.metric == "retention":
        return exponential_survival_model
    else:
        raise ValueError(f"Unknown metric type: {config.metric}")
