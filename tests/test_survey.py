import re
from pathlib import Path

import pandas as pd
import pytest

from propstark_core.survey import (
    REGION_DISTANCES,
    SEMESTER_DATE_RANGES,
    SEMESTERS,
    SOURCE_SB_MAPPINGS,
    assign_source_and_semester,
    compute_cumulative_observed_time,
    extract_sb_id,
    get_planned_observations,
    get_region_distance,
    get_semester_from_date,
    get_source_from_archive_file,
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


def test_extract_sb_id() -> None:
    archive_file = "26A-517.sb51050327.eb51180015.61288.31844270833"
    assert extract_sb_id(archive_file) == "sb51050327"
    assert extract_sb_id("plain_string") == "plain_string"


def test_get_source_from_archive_file_default_mapping() -> None:
    assert (
        get_source_from_archive_file("26A-517.sb51050327.eb51180015.61288.31844270833")
        == "IC348-Main"
    )
    assert (
        get_source_from_archive_file("26A-517.sb51076362.eb51144155.61277.36553201389")
        == "L1455"
    )
    assert (
        get_source_from_archive_file("26A-517.sb51071496.eb51075682.61244.410701597226")
        == "L1455"
    )
    assert get_source_from_archive_file("26A-517.sb99999999.eb51075682") is None


def test_get_source_from_archive_file_custom_mapping() -> None:
    custom_mapping = {
        "Custom-Region-1": ["sb12345", "51050327"],
        "Custom-Region-2": ["sb67890"],
    }
    assert (
        get_source_from_archive_file(
            "26A-517.sb51050327.eb51180015", source_mapping=custom_mapping
        )
        == "Custom-Region-1"
    )
    assert (
        get_source_from_archive_file(
            "26A-517.sb67890.eb51180015", source_mapping=custom_mapping
        )
        == "Custom-Region-2"
    )


def test_get_semester_from_date_default_ranges() -> None:
    assert get_semester_from_date("2026-09-05 07:38:34") == "26A"
    assert get_semester_from_date("2026-07-23 09:51:25") == "26A"
    assert get_semester_from_date("2027-09-01 00:00:00") == "27A"
    assert get_semester_from_date("2025-01-01 00:00:00") is None
    assert get_semester_from_date("invalid_date") is None


def test_get_semester_from_date_custom_ranges() -> None:
    custom_dates = {
        "TestSemA": ("2025-01-01 00:00:00", "2025-06-30 23:59:59"),
        "TestSemB": ("2025-07-01 00:00:00", "2025-12-31 23:59:59"),
    }
    assert (
        get_semester_from_date("2025-03-15 12:00:00", semester_dates=custom_dates)
        == "TestSemA"
    )
    assert (
        get_semester_from_date("2025-08-20 08:30:00", semester_dates=custom_dates)
        == "TestSemB"
    )


def test_assign_source_and_semester() -> None:
    df = pd.DataFrame(
        {
            "Archive File": [
                "26A-517.sb51050327.eb51180015.61288.31844270833",
                "26A-517.sb51049579.eb51170534.61281.52464027778",
            ],
            "Observation Start": [
                "2026-09-05 07:38:34",
                "2026-08-29 12:39:31",
            ],
        }
    )
    result = assign_source_and_semester(df)
    assert list(result["Source"]) == ["IC348-Main", "L1448"]
    assert list(result["Semester"]) == ["26A", "26A"]
