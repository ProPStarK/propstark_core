import re
from pathlib import Path

import pandas as pd
import pytest

from propstark_core.survey import (
    REGION_DISTANCES,
    SEMESTERS,
    compute_cumulative_observed_time,
    get_planned_observations,
    get_region_distance,
    load_sessions,
    planned_observations_dataframe,
    select_semester_columns,
    survey_progress_dataframe,
)


def test_get_region_distance_returns_parsecs() -> None:
    assert get_region_distance("Barnard1") == 301.0
    assert get_region_distance("L1688") == 138.4


def test_get_region_distance_rejects_unknown_region() -> None:
    with pytest.raises(KeyError, match="Unknown ProPStarK region: Unknown"):
        get_region_distance("Unknown")


def test_get_planned_observations_rejects_unknown_region() -> None:
    with pytest.raises(KeyError, match="Unknown ProPStarK region: Unknown"):
        get_planned_observations("Unknown")


def test_region_distances_contains_all_known_regions() -> None:
    assert len(REGION_DISTANCES) == 27


def test_planned_observations_dataframe_structure() -> None:
    df = planned_observations_dataframe()
    assert list(df.columns) == ["Source", "obs", "semester"]
    assert "L1448" in df["Source"].values


def test_survey_progress_dataframe_calculates_observed_counts() -> None:
    sessions = pd.DataFrame(
        {
            "Source": ["L1448", "L1448", "L1455", "B18-A"],
            "Semester": ["26A", "26A", "26A", "27B"],
        }
    )
    progress = survey_progress_dataframe(sessions)

    assert "observed_26A" in progress.columns
    assert "observed_27B" in progress.columns
    assert "observed_total" in progress.columns

    l1448 = progress[progress["Source"] == "L1448"].iloc[0]
    assert l1448["observed_26A"] == 2
    assert l1448["observed_27B"] == 0
    assert l1448["observed_total"] == 2

    b18a = progress[progress["Source"] == "B18-A"].iloc[0]
    assert b18a["observed_26A"] == 0
    assert b18a["observed_27B"] == 1
    assert b18a["observed_total"] == 1




def test_select_semester_columns_calculates_fraction() -> None:
    sessions = pd.DataFrame(
        {
            "Source": ["L1448", "L1448"],
            "Semester": ["26A", "26A"],
        }
    )
    progress = survey_progress_dataframe(sessions)
    selected = select_semester_columns(progress, "26A")

    assert "n_observed" in selected.columns
    assert "fraction_observed" in selected.columns

    row = selected[selected["Source"] == "L1448"].iloc[0]
    assert row["n_observed"] == 2
    # L1448 planned obs is 7
    assert row["fraction_observed"] == pytest.approx(2 / 7)


def test_select_semester_columns_invalid_semester_raises() -> None:
    progress = survey_progress_dataframe()
    with pytest.raises(
        ValueError,
        match=re.escape(f"semester must be one of {SEMESTERS} or None, got '99X'"),
    ):
        select_semester_columns(progress, "99X")


def test_load_sessions_from_dataframe() -> None:
    df = pd.DataFrame({"Source": ["L1448"], "Semester": ["26A"]})
    result = load_sessions(df)
    pd.testing.assert_frame_equal(result, df)
    # Ensure it returns a copy
    assert result is not df


def test_load_sessions_from_csv_path(tmp_path: Path) -> None:
    csv_path = tmp_path / "sessions.csv"
    df = pd.DataFrame({"Source": ["L1455"], "Semester": ["26A"]})
    df.to_csv(csv_path, index=False)

    result = load_sessions(csv_path)
    pd.testing.assert_frame_equal(result, df)


def test_load_sessions_none_loads_bundled_csv() -> None:
    result = load_sessions(None)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "Source" in result.columns
    assert "Semester" in result.columns


def test_select_semester_columns_none_semester() -> None:
    sessions = pd.DataFrame(
        {
            "Source": ["L1448", "L1448", "B18-A"],
            "Semester": ["26A", "26A", "27B"],
        }
    )
    progress = survey_progress_dataframe(sessions)
    selected = select_semester_columns(progress, None)

    assert "n_observed" in selected.columns
    assert "fraction_observed" in selected.columns
    assert "plot_semester" in selected.columns

    l1448_row = selected[selected["Source"] == "L1448"].iloc[0]
    assert l1448_row["n_observed"] == 2
    assert l1448_row["plot_semester"] == "26A"
    assert l1448_row["fraction_observed"] == pytest.approx(2 / 7)

    b18a_row = selected[selected["Source"] == "B18-A"].iloc[0]
    assert b18a_row["n_observed"] == 1
    assert b18a_row["plot_semester"] == "27B"
    assert b18a_row["fraction_observed"] == pytest.approx(1 / 2)


def test_compute_cumulative_observed_time() -> None:
    sessions = pd.DataFrame(
        {
            "Observation Start": [
                "2026-01-01 00:00:00",
                "2026-01-02 00:00:00",
            ],
            "Observation Stop": [
                "2026-01-01 02:00:00",
                "2026-01-02 03:30:00",
            ],
        }
    )
    time_df = compute_cumulative_observed_time(sessions)

    assert list(time_df.columns) == ["date", "duration_hours", "cumulative_hours"]
    assert list(time_df["duration_hours"]) == [2.0, 3.5]
    assert list(time_df["cumulative_hours"]) == [2.0, 5.5]
