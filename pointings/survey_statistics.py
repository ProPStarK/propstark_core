"""Survey progress statistics and plots."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from propstark_core.survey import (
    compute_cumulative_observed_time,
    select_semester_columns,
    survey_progress_dataframe,
)

SEMESTER_COLORS = {
    "26A": "tab:blue",
    "27B": "tab:orange",
}


def plot_observed_fraction(
    semester: str | None = None,
    sessions: pd.DataFrame | str | Path | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """
    Plot the fraction of observed sessions for each source.
    if a semester is specified, it will plot the fraction of observed sessions for that semester.
    if no semester is specified, it will plot the fraction of observed sessions for the whole project

    If a semester is specified, then only the targets that have planned observations for that semester will be plotted.
    If no semester is specified, then all targets will be plotted.
    """

    progress = survey_progress_dataframe(sessions)
    frame = select_semester_columns(progress, semester)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure

    for planned_semester, group in frame.groupby("plot_semester", sort=False):
        ax.scatter(
            group["Source"],
            group["fraction_observed"],
            color=SEMESTER_COLORS.get(planned_semester, "tab:gray"),
            edgecolor="black",
            label=planned_semester,
        )

        for _, row in group.iterrows():
            ax.annotate(
                f"planned: {row['obs']}",
                (row["Source"], row["fraction_observed"]),
                fontsize=7,
                xytext=(3, 3),
                textcoords="offset points",
            )

    title = (
        f"Survey progress — {semester}"
        if semester is not None
        else "Survey progress — all semesters"
    )

    ax.set_xlabel("Region")
    ax.set_ylabel("Fraction Observed")
    ax.tick_params(axis="x", labelrotation=85)
    ax.set_title(title)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend(title="Planned semester")

    return fig, ax


def plot_cumulative_observed_time(
    sessions: pd.DataFrame | str | Path | None = None,
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Plot cumulative observed project time."""
    frame = compute_cumulative_observed_time(sessions)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    else:
        fig = ax.figure

    ax.step(frame["date"], frame["cumulative_hours"], where="post")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative observed time [hours]")
    ax.set_title("Cumulative observed project time")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()

    return fig, ax


def make_survey_statistics_figures(
    semester: str | None = None,
    sessions: pd.DataFrame | str | Path | None = None,
    save_prefix: str = "ProPStarK_survey_statistics",
) -> tuple[Figure, Figure]:
    """Create and save survey progress figures."""
    fig1, _ = plot_observed_fraction(semester, sessions)
    fig2, _ = plot_cumulative_observed_time(sessions)

    suffix = f"_{semester}" if semester is not None else ""
    fig1.savefig(
        f"{save_prefix}_fraction{suffix}.png",
        dpi=150,
        bbox_inches="tight",
    )
    fig2.savefig(
        f"{save_prefix}_cumulative{suffix}.png",
        dpi=150,
        bbox_inches="tight",
    )

    return fig1, fig2
