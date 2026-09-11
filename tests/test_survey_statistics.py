from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from pointings.survey_statistics import plot_observed_fraction
from propstark_core.survey import planned_observations_dataframe


def test_plot_observed_fraction_filters_to_planned_semester() -> None:
    sessions = pd.DataFrame(
        {
            "Source": ["L1448", "L1448", "B18-A"],
            "Semester": ["26A", "26A", "27B"],
        }
    )

    fig, ax = plot_observed_fraction("26A", sessions)

    assert ax.get_title() == "Survey progress — 26A"
    annotations = [annotation.get_text() for annotation in ax.texts]
    planned_26a = list(
        planned_observations_dataframe().query("semester == '26A'")["Source"]
    )
    assert [tick.get_text() for tick in ax.get_xticklabels()] == planned_26a
    assert all(tick.get_rotation() == 85 for tick in ax.get_xticklabels())
    assert len(annotations) == len(planned_26a)
    assert "planned: 7" in annotations
    assert ax.get_ylabel() == "Fraction Observed"

    l1448_annotation = next(
        annotation for annotation in ax.texts if annotation.xy[0] == "L1448"
    )
    assert l1448_annotation.xy[1] == pytest.approx(2 / 7)
    plt.close(fig)


def test_plot_observed_fraction_plots_all_targets_without_semester() -> None:
    sessions = pd.DataFrame(
        {
            "Source": ["L1448", "L1448", "B18-A"],
            "Semester": ["26A", "26A", "27B"],
        }
    )

    fig, ax = plot_observed_fraction(sessions=sessions)

    assert ax.get_title() == "Survey progress — all semesters"
    assert len(ax.texts) == len(planned_observations_dataframe())
    assert sum(len(collection.get_offsets()) for collection in ax.collections) == len(
        planned_observations_dataframe()
    )
    plt.close(fig)
