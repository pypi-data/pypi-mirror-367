"""
Plotting functions for Bayesian A/B testing visualization.

Provides comprehensive visualization capabilities following Kruschke's BEST approach:
- Posterior distributions with credible intervals
- ROPE visualization
- Effect size distributions
- Business-friendly summary plots
- Sequential testing plots

All plots follow statistical best practices and provide clear interpretation guidance.
"""

import jax.numpy as jnp
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Tuple, Union
from plotly.subplots import make_subplots

from .config import ExperimentConfig
from .results import TestResults

# Set up plotting style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")


@beartype
def plot_posterior_distributions(
    results: TestResults,
    parameters: Optional[List[str]] = None,
    credible_interval: float = 0.95,
    show_rope: bool = True,
    figsize: Tuple[int, int] = (12, 8),
    style: str = "matplotlib",
) -> Union[plt.Figure, go.Figure]:
    """
    Plot posterior distributions for key parameters.

    Core BEST visualization showing full posterior distributions with
    credible intervals and ROPE regions for principled decision making.

    Args:
        results: TestResults object with posterior samples
        parameters: List of parameters to plot (None for all)
        credible_interval: Credible interval level (default 0.95)
        show_rope: Whether to show ROPE region for difference
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object (matplotlib or plotly)
    """
    if parameters is None:
        parameters = list(results.samples.keys())

    if style == "plotly":
        return _plot_posterior_plotly(results, parameters, credible_interval, show_rope)
    else:
        return _plot_posterior_matplotlib(
            results, parameters, credible_interval, show_rope, figsize
        )


def _plot_posterior_matplotlib(
    results: TestResults,
    parameters: List[str],
    credible_interval: float,
    show_rope: bool,
    figsize: Tuple[int, int],
) -> plt.Figure:
    """Matplotlib implementation of posterior plots"""
    n_params = len(parameters)
    n_cols = min(3, n_params)
    n_rows = (n_params + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_params == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if n_params > 1 else axes

    # Get credible intervals
    intervals = results.credible_intervals()

    for i, param in enumerate(parameters):
        ax = axes[i] if n_params > 1 else axes
        samples = np.array(results.samples[param])

        # Plot histogram with KDE
        ax.hist(samples, bins=50, density=True, alpha=0.7, color="skyblue", edgecolor="black")

        # Add KDE
        try:
            from scipy.stats import gaussian_kde

            kde = gaussian_kde(samples)
            x_range = np.linspace(samples.min(), samples.max(), 200)
            ax.plot(x_range, kde(x_range), "r-", linewidth=2, label="Posterior")
        except ImportError:
            pass

        # Add credible interval
        if param in intervals:
            lower, upper = intervals[param]
            ax.axvline(
                lower,
                color="red",
                linestyle="--",
                alpha=0.8,
                label=f"{credible_interval * 100:.0f}% CI",
            )
            ax.axvline(upper, color="red", linestyle="--", alpha=0.8)

            # Shade credible interval
            mask = (x_range >= lower) & (x_range <= upper)
            if "kde" in locals():
                ax.fill_between(x_range, 0, kde(x_range), where=mask, alpha=0.3, color="red")

        # Add ROPE for difference parameter
        if param == "difference" and show_rope:
            rope_lower, rope_upper = results.config.get_rope_bounds_for_metric()

            # ROPE region
            ax.axvspan(rope_lower, rope_upper, alpha=0.2, color="green", label="ROPE")
            ax.axvline(0, color="black", linestyle="-", alpha=0.8, label="Null (0)")

            # ROPE decision annotation
            decision = results.rope_decision()
            rope_text = f"ROPE Decision: {decision.replace('_', ' ').title()}"
            ax.text(
                0.05,
                0.95,
                rope_text,
                transform=ax.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            )

        ax.set_title(f"{param.replace('_', ' ').title()} Posterior")
        ax.set_xlabel("Value")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for i in range(n_params, len(axes)):
        axes[i].set_visible(False)

    plt.tight_layout()
    return fig


def _plot_posterior_plotly(
    results: TestResults, parameters: List[str], credible_interval: float, show_rope: bool
) -> go.Figure:
    """Plotly implementation of posterior plots"""
    n_params = len(parameters)
    n_cols = min(3, n_params)
    n_rows = (n_params + n_cols - 1) // n_cols

    fig = make_subplots(
        rows=n_rows,
        cols=n_cols,
        subplot_titles=[param.replace("_", " ").title() for param in parameters],
    )

    intervals = results.credible_intervals()

    for i, param in enumerate(parameters):
        row = i // n_cols + 1
        col = i % n_cols + 1

        samples = np.array(results.samples[param])

        # Add histogram
        fig.add_trace(
            go.Histogram(
                x=samples,
                name=f"{param} Posterior",
                opacity=0.7,
                nbinsx=50,
                histnorm="probability density",
            ),
            row=row,
            col=col,
        )

        # Add credible interval lines
        if param in intervals:
            lower, upper = intervals[param]
            fig.add_vline(x=lower, line_dash="dash", line_color="red", row=row, col=col)
            fig.add_vline(x=upper, line_dash="dash", line_color="red", row=row, col=col)

        # Add ROPE for difference
        if param == "difference" and show_rope:
            rope_lower, rope_upper = results.config.get_rope_bounds_for_metric()
            fig.add_vrect(
                x0=rope_lower,
                x1=rope_upper,
                fillcolor="green",
                opacity=0.2,
                line_width=0,
                row=row,
                col=col,
            )
            fig.add_vline(x=0, line_color="black", row=row, col=col)

    fig.update_layout(title="Posterior Distributions", showlegend=False, height=300 * n_rows)

    return fig


@beartype
def plot_effect_size(
    results: TestResults,
    rope_bounds: Optional[Tuple[float, float]] = None,
    figsize: Tuple[int, int] = (10, 6),
    style: str = "matplotlib",
) -> Union[plt.Figure, go.Figure]:
    """
    Plot effect size distribution following Kruschke's definition.

    Args:
        results: TestResults object
        rope_bounds: ROPE bounds for effect size (None for config defaults)
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object
    """
    if "effect_size" not in results.samples:
        raise ValueError("Effect size not available in results")

    effect_samples = np.array(results.samples["effect_size"])

    if rope_bounds is None:
        # Use config ROPE bounds or default effect size bounds
        rope_bounds = (-0.2, 0.2)  # Small effect size bounds

    if style == "plotly":
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=effect_samples,
                name="Effect Size",
                opacity=0.7,
                nbinsx=50,
                histnorm="probability density",
            )
        )

        # Add ROPE
        fig.add_vrect(
            x0=rope_bounds[0],
            x1=rope_bounds[1],
            fillcolor="green",
            opacity=0.2,
            line_width=0,
            annotation_text="ROPE",
        )

        fig.add_vline(x=0, line_color="black", line_dash="solid")

        fig.update_layout(
            title="Effect Size Distribution",
            xaxis_title="Effect Size (Cohen's d equivalent)",
            yaxis_title="Density",
        )

        return fig

    else:
        fig, ax = plt.subplots(figsize=figsize)

        # Plot histogram
        ax.hist(effect_samples, bins=50, density=True, alpha=0.7, color="lightcoral")

        # Add ROPE
        ax.axvspan(
            rope_bounds[0],
            rope_bounds[1],
            alpha=0.2,
            color="green",
            label="ROPE (Negligible Effect)",
        )
        ax.axvline(0, color="black", linestyle="-", label="No Effect")

        # Add credible interval
        lower, upper = np.percentile(effect_samples, [2.5, 97.5])
        ax.axvline(lower, color="red", linestyle="--", label="95% CI")
        ax.axvline(upper, color="red", linestyle="--")

        # Add interpretation guidelines
        interpretation_lines = [
            (-0.8, "Large Negative", "purple"),
            (-0.5, "Medium Negative", "blue"),
            (-0.2, "Small Negative", "lightblue"),
            (0.2, "Small Positive", "lightgreen"),
            (0.5, "Medium Positive", "green"),
            (0.8, "Large Positive", "darkgreen"),
        ]

        for value, label, color in interpretation_lines:
            if ax.get_xlim()[0] <= value <= ax.get_xlim()[1]:
                ax.axvline(value, color=color, linestyle=":", alpha=0.6)
                ax.text(
                    value,
                    ax.get_ylim()[1] * 0.9,
                    label,
                    rotation=90,
                    ha="right",
                    va="top",
                    fontsize=8,
                    color=color,
                )

        ax.set_title("Effect Size Distribution (Following Kruschke's BEST)")
        ax.set_xlabel("Effect Size (Cohen's d equivalent)")
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig


@beartype
def plot_rope_analysis(
    results: TestResults,
    parameter: str = "difference",
    figsize: Tuple[int, int] = (10, 6),
    style: str = "matplotlib",
) -> Union[plt.Figure, go.Figure]:
    """
    Specialized ROPE analysis plot showing decision regions.

    Args:
        results: TestResults object
        parameter: Parameter to analyze (default "difference")
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object
    """
    if parameter not in results.samples:
        raise ValueError(f"Parameter {parameter} not found in results")

    samples = np.array(results.samples[parameter])
    rope_lower, rope_upper = results.config.get_rope_bounds_for_metric()

    # Calculate ROPE statistics
    in_rope = np.logical_and(samples >= rope_lower, samples <= rope_upper)
    prop_in_rope = np.mean(in_rope)
    prop_below_rope = np.mean(samples < rope_lower)
    prop_above_rope = np.mean(samples > rope_upper)

    decision = results.rope_decision()

    if style == "plotly":
        fig = go.Figure()

        # Main histogram
        fig.add_trace(
            go.Histogram(
                x=samples,
                name=parameter.title(),
                opacity=0.7,
                nbinsx=50,
                histnorm="probability density",
            )
        )

        # ROPE region
        fig.add_vrect(
            x0=rope_lower,
            x1=rope_upper,
            fillcolor="green",
            opacity=0.3,
            line_width=2,
            line_color="green",
            annotation_text=f"ROPE<br>{prop_in_rope:.1%} of posterior",
        )

        # Decision regions
        fig.add_vrect(
            x0=samples.min(),
            x1=rope_lower,
            fillcolor="red",
            opacity=0.1,
            annotation_text=f"Reject Null<br>{prop_below_rope:.1%}",
        )

        fig.add_vrect(
            x0=rope_upper,
            x1=samples.max(),
            fillcolor="red",
            opacity=0.1,
            annotation_text=f"Reject Null<br>{prop_above_rope:.1%}",
        )

        fig.update_layout(
            title=f"ROPE Analysis: {decision.replace('_', ' ').title()}",
            xaxis_title=parameter.replace("_", " ").title(),
            yaxis_title="Density",
        )

        return fig

    else:
        fig, ax = plt.subplots(figsize=figsize)

        # Plot histogram
        ax.hist(samples, bins=50, density=True, alpha=0.7, color="skyblue", edgecolor="black")

        # ROPE region
        ax.axvspan(
            rope_lower,
            rope_upper,
            alpha=0.3,
            color="green",
            label=f"ROPE ({prop_in_rope:.1%} of posterior)",
        )

        # Decision regions
        x_min, x_max = ax.get_xlim()
        if rope_lower > x_min:
            ax.axvspan(
                x_min,
                rope_lower,
                alpha=0.1,
                color="red",
                label=f"Reject Null ({prop_below_rope:.1%})",
            )
        if rope_upper < x_max:
            ax.axvspan(rope_upper, x_max, alpha=0.1, color="red")

        # Null hypothesis line
        ax.axvline(0, color="black", linestyle="-", alpha=0.8, label="Null Hypothesis")

        # Add decision text
        decision_text = f"ROPE Decision: {decision.replace('_', ' ').title()}"
        color_map = {"accept_null": "green", "reject_null": "red", "undecided": "orange"}
        ax.text(
            0.05,
            0.95,
            decision_text,
            transform=ax.transAxes,
            bbox=dict(
                boxstyle="round,pad=0.5", facecolor=color_map.get(decision, "gray"), alpha=0.7
            ),
            fontsize=12,
            fontweight="bold",
        )

        ax.set_title(f"ROPE Analysis: {parameter.replace('_', ' ').title()}")
        ax.set_xlabel(parameter.replace("_", " ").title())
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig


@beartype
def plot_business_summary(
    results: TestResults, figsize: Tuple[int, int] = (12, 8), style: str = "matplotlib"
) -> Union[plt.Figure, go.Figure]:
    """
    Business-friendly summary visualization.

    Args:
        results: TestResults object
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object
    """
    summary = results.summary()
    prob_better = results.prob_better()

    if style == "plotly":
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Treatment Probability of Being Better",
                "Lift Distribution",
                "Decision Summary",
                "Sample Sizes",
            ),
            specs=[
                [{"type": "indicator"}, {"type": "histogram"}],
                [{"type": "table"}, {"type": "bar"}],
            ],
        )

        # Probability gauge
        treatment_prob = prob_better.get("treatment", 0.5)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=treatment_prob * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Treatment Win Probability (%)"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {
                        "color": (
                            "darkgreen"
                            if treatment_prob > 0.95
                            else "red"
                            if treatment_prob < 0.05
                            else "orange"
                        )
                    },
                    "steps": [
                        {"range": [0, 50], "color": "lightgray"},
                        {"range": [50, 95], "color": "yellow"},
                        {"range": [95, 100], "color": "green"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 95,
                    },
                },
            ),
            row=1,
            col=1,
        )

        # Lift distribution
        if "difference" in results.samples:
            fig.add_trace(
                go.Histogram(
                    x=np.array(results.samples["difference"]), name="Lift Distribution", opacity=0.7
                ),
                row=1,
                col=2,
            )

        # Decision table
        decision_data = [
            ["Winner", summary["winner"]],
            ["Decision", summary["decision"]],
            ["Lift", f"{summary['lift']:.3f}"],
            ["Confidence", f"{summary['confidence']:.1%}"],
        ]

        fig.add_trace(
            go.Table(
                header=dict(values=["Metric", "Value"]),
                cells=dict(values=list(zip(*decision_data))),
            ),
            row=2,
            col=1,
        )

        # Sample sizes
        if "sample_sizes" in summary:
            variants = list(summary["sample_sizes"].keys())
            sizes = list(summary["sample_sizes"].values())

            fig.add_trace(go.Bar(x=variants, y=sizes, name="Sample Sizes"), row=2, col=2)

        fig.update_layout(title="Business Summary Dashboard", height=800)

        return fig

    else:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # 1. Treatment probability gauge
        treatment_prob = prob_better.get("treatment", 0.5)

        # Create a simple gauge using a pie chart
        sizes = [treatment_prob, 1 - treatment_prob]
        colors = [
            "green" if treatment_prob > 0.95 else "red" if treatment_prob < 0.05 else "orange",
            "lightgray",
        ]
        wedges, texts = ax1.pie(sizes, colors=colors, startangle=90, counterclock=False)

        # Add percentage text in center
        ax1.text(
            0, 0, f"{treatment_prob:.1%}", ha="center", va="center", fontsize=20, fontweight="bold"
        )
        ax1.set_title("Treatment Win Probability")

        # 2. Lift distribution
        if "difference" in results.samples:
            lift_samples = np.array(results.samples["difference"])
            ax2.hist(lift_samples, bins=30, alpha=0.7, color="lightblue")
            ax2.axvline(
                np.mean(lift_samples),
                color="red",
                linestyle="--",
                label=f"Mean: {np.mean(lift_samples):.3f}",
            )
            ax2.axvline(0, color="black", linestyle="-", alpha=0.5, label="No Effect")
            ax2.set_title("Lift Distribution")
            ax2.set_xlabel("Lift")
            ax2.set_ylabel("Frequency")
            ax2.legend()

        # 3. Decision summary
        ax3.axis("off")
        decision_text = f"""
        Winner: {summary["winner"]}
        Decision: {summary["decision"].replace("_", " ").title()}
        Lift: {summary["lift"]:.3f}
        Confidence: {summary["confidence"]:.1%}
        """

        ax3.text(
            0.1,
            0.7,
            decision_text,
            transform=ax3.transAxes,
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7),
        )
        ax3.set_title("Decision Summary")

        # 4. Sample sizes
        if "sample_sizes" in summary:
            variants = list(summary["sample_sizes"].keys())
            sizes = list(summary["sample_sizes"].values())

            bars = ax4.bar(variants, sizes, color=["lightcoral", "lightgreen"])
            ax4.set_title("Sample Sizes")
            ax4.set_ylabel("Count")

            # Add value labels on bars
            for bar, size in zip(bars, sizes):
                height = bar.get_height()
                ax4.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + height * 0.01,
                    f"{size}",
                    ha="center",
                    va="bottom",
                )

        plt.tight_layout()
        return fig


@beartype
def plot_sequential_analysis(
    results_list: List[TestResults],
    metric_name: str = "difference",
    figsize: Tuple[int, int] = (12, 6),
    style: str = "matplotlib",
) -> Union[plt.Figure, go.Figure]:
    """
    Plot sequential analysis showing evolution of results over time.

    Args:
        results_list: List of TestResults from sequential analysis
        metric_name: Parameter to track over time
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object
    """
    if not results_list:
        raise ValueError("Empty results list provided")

    # Extract data for plotting
    time_points = list(range(1, len(results_list) + 1))
    means = []
    lower_bounds = []
    upper_bounds = []
    decisions = []

    for result in results_list:
        if metric_name in result.samples:
            samples = np.array(result.samples[metric_name])
            means.append(np.mean(samples))
            lower, upper = np.percentile(samples, [2.5, 97.5])
            lower_bounds.append(lower)
            upper_bounds.append(upper)
            decisions.append(result.rope_decision())
        else:
            means.append(0)
            lower_bounds.append(0)
            upper_bounds.append(0)
            decisions.append("undecided")

    if style == "plotly":
        fig = go.Figure()

        # Add credible interval band
        fig.add_trace(
            go.Scatter(
                x=time_points + time_points[::-1],
                y=upper_bounds + lower_bounds[::-1],
                fill="toself",
                fillcolor="rgba(0,100,80,0.2)",
                line=dict(color="rgba(255,255,255,0)"),
                showlegend=False,
                name="95% Credible Interval",
            )
        )

        # Add mean line
        fig.add_trace(
            go.Scatter(
                x=time_points,
                y=means,
                mode="lines+markers",
                name=f"{metric_name.title()} Mean",
                line=dict(color="blue", width=2),
            )
        )

        # Add ROPE bounds
        rope_lower, rope_upper = results_list[0].config.get_rope_bounds_for_metric()
        fig.add_hline(
            y=rope_lower, line_dash="dash", line_color="green", annotation_text="ROPE Lower"
        )
        fig.add_hline(
            y=rope_upper, line_dash="dash", line_color="green", annotation_text="ROPE Upper"
        )
        fig.add_hline(y=0, line_color="black", annotation_text="Null")

        fig.update_layout(
            title=f"Sequential Analysis: {metric_name.title()}",
            xaxis_title="Analysis Point",
            yaxis_title=metric_name.title(),
        )

        return fig

    else:
        fig, ax = plt.subplots(figsize=figsize)

        # Plot credible interval band
        ax.fill_between(
            time_points, lower_bounds, upper_bounds, alpha=0.3, color="lightblue", label="95% CI"
        )

        # Plot mean line
        ax.plot(
            time_points,
            means,
            "b-o",
            linewidth=2,
            markersize=6,
            label=f"{metric_name.title()} Mean",
        )

        # Add ROPE bounds
        rope_lower, rope_upper = results_list[0].config.get_rope_bounds_for_metric()
        ax.axhline(rope_lower, color="green", linestyle="--", alpha=0.7, label="ROPE Bounds")
        ax.axhline(rope_upper, color="green", linestyle="--", alpha=0.7)
        ax.axhline(0, color="black", linestyle="-", alpha=0.5, label="Null Hypothesis")

        # Color code decision points
        decision_colors = {"accept_null": "green", "reject_null": "red", "undecided": "orange"}
        for i, (point, decision) in enumerate(zip(time_points, decisions)):
            color = decision_colors.get(decision, "gray")
            ax.scatter(point, means[i], color=color, s=100, zorder=5)

        # Add final decision annotation
        final_decision = decisions[-1]
        ax.text(
            0.95,
            0.95,
            f"Final Decision: {final_decision.replace('_', ' ').title()}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            bbox=dict(
                boxstyle="round,pad=0.3",
                facecolor=decision_colors.get(final_decision, "gray"),
                alpha=0.7,
            ),
        )

        ax.set_title(f"Sequential Analysis: {metric_name.title()}")
        ax.set_xlabel("Analysis Point")
        ax.set_ylabel(metric_name.title())
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig


@beartype
def plot_prior_posterior_comparison(
    results: TestResults,
    parameter: str,
    prior_samples: Optional[np.ndarray] = None,
    figsize: Tuple[int, int] = (10, 6),
    style: str = "matplotlib",
) -> Union[plt.Figure, go.Figure]:
    """
    Compare prior and posterior distributions.

    Args:
        results: TestResults object
        parameter: Parameter to compare
        prior_samples: Prior samples (if None, generates from config)
        figsize: Figure size for matplotlib
        style: "matplotlib" or "plotly"

    Returns:
        Figure object
    """
    if parameter not in results.samples:
        raise ValueError(f"Parameter {parameter} not found in results")

    posterior_samples = np.array(results.samples[parameter])

    # Generate prior samples if not provided
    if prior_samples is None:
        # This is a simplified prior generation - in practice you'd use the actual prior
        prior_samples = np.random.normal(0, 1, len(posterior_samples))

    if style == "plotly":
        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=prior_samples,
                name="Prior",
                opacity=0.7,
                nbinsx=50,
                histnorm="probability density",
            )
        )

        fig.add_trace(
            go.Histogram(
                x=posterior_samples,
                name="Posterior",
                opacity=0.7,
                nbinsx=50,
                histnorm="probability density",
            )
        )

        fig.update_layout(
            title=f"Prior vs Posterior: {parameter.title()}",
            xaxis_title=parameter.title(),
            yaxis_title="Density",
            barmode="overlay",
        )

        return fig

    else:
        fig, ax = plt.subplots(figsize=figsize)

        # Plot both distributions
        ax.hist(prior_samples, bins=50, density=True, alpha=0.5, color="red", label="Prior")
        ax.hist(
            posterior_samples, bins=50, density=True, alpha=0.5, color="blue", label="Posterior"
        )

        # Add summary statistics
        prior_mean = np.mean(prior_samples)
        posterior_mean = np.mean(posterior_samples)

        ax.axvline(prior_mean, color="red", linestyle="--", label=f"Prior Mean: {prior_mean:.3f}")
        ax.axvline(
            posterior_mean,
            color="blue",
            linestyle="--",
            label=f"Posterior Mean: {posterior_mean:.3f}",
        )

        ax.set_title(f"Prior vs Posterior: {parameter.title()}")
        ax.set_xlabel(parameter.title())
        ax.set_ylabel("Density")
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig


# Convenience function for common plotting workflows
@beartype
def create_analysis_report(
    results: TestResults,
    save_path: Optional[str] = None,
    style: str = "matplotlib",
    figsize: Tuple[int, int] = (15, 20),
) -> Dict[str, Union[plt.Figure, go.Figure]]:
    """
    Create a comprehensive analysis report with all key plots.

    Args:
        results: TestResults object
        save_path: Path to save figures (without extension)
        style: "matplotlib" or "plotly"
        figsize: Figure size for matplotlib plots

    Returns:
        Dictionary of figure objects
    """
    figures = {}

    try:
        # Core plots
        figures["posterior"] = plot_posterior_distributions(results, style=style)
        figures["rope"] = plot_rope_analysis(results, style=style)
        figures["business"] = plot_business_summary(results, style=style)

        # Optional plots (if data available)
        if "effect_size" in results.samples:
            figures["effect_size"] = plot_effect_size(results, style=style)

        # Save figures if path provided
        if save_path and style == "matplotlib":
            for name, fig in figures.items():
                if isinstance(fig, plt.Figure):
                    fig.savefig(f"{save_path}_{name}.png", dpi=300, bbox_inches="tight")

        return figures

    except Exception as e:
        print(f"Error creating analysis report: {e}")
        return figures
