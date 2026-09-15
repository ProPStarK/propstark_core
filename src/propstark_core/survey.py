"""Static metadata and progress tracking for the ProPStarK survey."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, TypedDict

import pandas as pd

# The distances to each ProPStarK region, in parsecs.
# These values are taken from the GAS survey paper (Friesen et al. 2017).
REGION_DISTANCES = {
    "HC2": 138.6,
    "B18": 126.6,
    "L1495": 126.6,
    "L1451": 279.0,
    "L1448": 288.0,
    "L1455": 279.0,
    "NGC1333": 299.0,
    "Barnard1": 301.0,
    "B1E": 301.0,
    "IC348": 321.0,
    "Per7/34": 301.0,
    "L1688": 138.4,
    "L1689": 144.2,
    "L1712": 144.2,
    "Orion A": 397.0,
    "Orion A-S": 428.0,
    "NGC2023": 403.0,
    "NGCC2068": 417.0,
    "IC5146": 813.0,
    "CrAEast": 154.0,
    "CrAWest": 154.0,
    "B59": 163.0,
    "Core40": 163.0,
    "Serpens_Aquila": 436.0,
    "MWC297": 436.0,
    "L1228": 346.0,
    "L1251": 346.0,
}

# Semester 26A, already in OPT
# Semester 27B still to be created


class PlannedObservation(TypedDict):
    obs: int
    semester: str


# The number of planned observations for each ProPStarK region,
# and the semester in which they are scheduled.
# This should match what is in the OPT database,
# but is hard-coded here for convenience.
planned_obs: dict[str, PlannedObservation] = {
    # Semester 26A, already in OPT
    "IC348-SE": {"obs": 3, "semester": "26A"},
    "IC348-Main": {"obs": 10, "semester": "26A"},
    "L1228": {"obs": 2, "semester": "26A"},
    "L1251-A": {"obs": 7, "semester": "26A"},
    "L1251-B": {"obs": 10, "semester": "26A"},
    "L1448": {"obs": 7, "semester": "26A"},
    "L1455": {"obs": 2, "semester": "26A"},
    "L1495-A": {"obs": 2, "semester": "26A"},
    "L1495-B": {"obs": 3, "semester": "26A"},
    "L1495-C": {"obs": 6, "semester": "26A"},
    "L1495-D": {"obs": 3, "semester": "26A"},
    "L1495-E": {"obs": 2, "semester": "26A"},
    "L1495-F": {"obs": 2, "semester": "26A"},
    "Serpens_MWC297": {"obs": 2, "semester": "26A"},
    # Semester 27B, still to be created, numbers from proposal
    "Barnard1-Main": {"obs": 10, "semester": "27B"},
    "Barnard1-South": {"obs": 3, "semester": "27B"},
    "B1E": {"obs": 1, "semester": "27B"},
    "B18-A": {"obs": 2, "semester": "27B"},
    "B18-B": {"obs": 4, "semester": "27B"},
    "B18-C": {"obs": 2, "semester": "27B"},
    "B18-D": {"obs": 2, "semester": "27B"},
    "B59": {"obs": 4, "semester": "27B"},
    "CrAEast": {"obs": 4, "semester": "27B"},
    "CrAWest": {"obs": 4, "semester": "27B"},
    "Core40": {"obs": 4, "semester": "27B"},
    "IC5146": {"obs": 4, "semester": "27B"},
    "L1451": {"obs": 1, "semester": "27B"},
    "L1688": {"obs": 2, "semester": "27B"},
    "L1689": {"obs": 2, "semester": "27B"},
    "L1712": {"obs": 2, "semester": "27B"},
    "NGC2023": {"obs": 3, "semester": "27B"},
    "NGCC2068": {"obs": 3, "semester": "27B"},
    "Orion A": {"obs": 3, "semester": "27B"},
    "Orion A-S": {"obs": 3, "semester": "27B"},
    "Per7/34": {"obs": 1, "semester": "27B"},
    "Serpens_Aquila": {"obs": 5, "semester": "27B"},
    "TMC1-1C": {"obs": 6, "semester": "27B"},
}


def get_region_distance(region_name: str) -> float:
    """Return the distance to ``region_name`` in parsecs.

    Raises
    ------
    KeyError
        If the region is not represented in the ProPStarK survey metadata.
    """
    try:
        return REGION_DISTANCES[region_name]
    except KeyError as error:
        raise KeyError(f"Unknown ProPStarK region: {region_name}") from error


def get_planned_observations(region_name: str) -> int:
    """Return the number of planned observations for ``region_name``."""
    if region_name in planned_obs:
        return planned_obs[region_name]["obs"]
    else:
        raise KeyError(f"Unknown ProPStarK region: {region_name}")


def planned_observations_dataframe() -> pd.DataFrame:
    """Return planned observations as a new DataFrame."""
    return (
        pd.DataFrame.from_dict(planned_obs, orient="index")
        .rename_axis("Source")
        .reset_index()
    )


SEMESTERS = ("26A", "27B")

# Default mapping of source names to scheduling block substrings in Archive File names.
# These values are taken from the OPT submitted SBs.
SOURCE_SB_MAPPINGS: dict[str, list[str]] = {
    "IC348-Main": ["sb51050327", "sb51050643"],
    "IC348-SE": ["sb51033402", "sb51078485"],
    "L1228": ["sb51112127", "sb51112375"],
    "L1251-A": ["sb51117415", "sb51173190"],
    "L1251-B": ["sb51174165", "sb51174488"],
    "L1448": ["sb51049239", "sb51049579"],
    "L1455": [
        "sb51051436",
        "sb51058048",
        "sb51076362",
        "sb51071496",
        "sb51076099",
        "sb51076362",
    ],
    "L1495-A": ["sb51060262", "sb51060493"],
    "L1495-B": ["sb51078708", "sb51078972"],
    "L1495-C": ["sb51079732", "sb51080058"],
    "L1495-D": ["sb51079212", "sb51079488"],
    "L1495-E": ["sb51061210", "sb51061441"],
    "L1495-F": ["sb51062144", "sb51062367"],
}

# Date ranges defining observing semesters.
SEMESTER_DATE_RANGES: dict[str, tuple[str, str]] = {
    "26A": ("2026-02-20 00:00:00", "2026-10-19 23:59:59"),
    "26B": ("2026-10-20 00:00:00", "2027-02-15 23:59:59"),
    "27A": ("2027-03-16 00:00:00", "2027-10-25 23:59:59"),
    "27B": ("2027-10-26 00:00:00", "2028-02-21 23:59:59"),
}


def extract_sb_id(archive_file: Any) -> str:
    """Extract the scheduling block identifier from an archive file name.

    For example, from '26A-517.sb51050327.eb51180015.61288.31844270833',
    returns 'sb51050327'.
    """
    parts = str(archive_file).split(".")
    if len(parts) > 1:
        return parts[1]
    return str(archive_file)


def get_source_from_archive_file(
    archive_file: Any,
    source_mapping: Mapping[str, Sequence[str] | str] | None = None,
) -> str | None:
    """Determine the source from an archive file name and source mapping."""
    if pd.isna(archive_file):
        return None
    mapping = SOURCE_SB_MAPPINGS if source_mapping is None else source_mapping

    sb_id = extract_sb_id(archive_file)
    for source, identifiers in mapping.items():
        if isinstance(identifiers, str):
            identifiers = [identifiers]
        for ident in identifiers:
            if ident in sb_id:
                return source
    return None


def get_semester_from_date(
    date: Any,
    semester_dates: Mapping[str, tuple[str, str]] | None = None,
) -> str | None:
    """Determine the semester from an observation start date."""
    if pd.isna(date):
        return None
    dates = SEMESTER_DATE_RANGES if semester_dates is None else semester_dates

    try:
        dt = pd.Timestamp(date)
    except Exception:
        return None

    for semester, (start, end) in dates.items():
        start_dt = pd.Timestamp(start)
        end_dt = pd.Timestamp(end)
        if start_dt <= dt <= end_dt:
            return semester

    return None


def assign_source_and_semester(
    observations: pd.DataFrame,
    source_mapping: Mapping[str, Sequence[str] | str] | None = None,
    semester_dates: Mapping[str, tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """Populate 'Source' and 'Semester' columns in observations DataFrame if missing or containing nulls."""
    df = observations.copy()

    def _resolve_source(val: Any) -> str | None:
        return get_source_from_archive_file(val, source_mapping)

    def _resolve_semester(val: Any) -> str | None:
        return get_semester_from_date(val, semester_dates)

    archive_col = None
    for col in ("Archive File", "archive_file"):
        if col in df.columns:
            archive_col = col
            break

    if archive_col is not None:
        if "Source" not in df.columns:
            df["Source"] = df[archive_col].map(_resolve_source)
        elif df["Source"].isna().any():
            filled_sources = df[archive_col].map(_resolve_source)
            df["Source"] = df["Source"].fillna(filled_sources)

    start_col = None
    for col in ("Observation Start", "observation_start"):
        if col in df.columns:
            start_col = col
            break

    if start_col is not None:
        if "Semester" not in df.columns:
            df["Semester"] = df[start_col].map(_resolve_semester)
        elif df["Semester"].isna().any():
            filled_semesters = df[start_col].map(_resolve_semester)
            df["Semester"] = df["Semester"].fillna(filled_semesters)

    return df


def load_sessions(
    sessions: pd.DataFrame | str | Path | None = None,
    source_mapping: Mapping[str, Sequence[str] | str] | None = None,
    semester_dates: Mapping[str, tuple[str, str]] | None = None,
) -> pd.DataFrame:
    """
    Load archive observations from a DataFrame or CSV file.
    This represents the observations actually carried out during the semester.
    """
    if isinstance(sessions, pd.DataFrame):
        return assign_source_and_semester(
            sessions, source_mapping=source_mapping, semester_dates=semester_dates
        )

    from .archive import load_observations_csv

    return load_observations_csv(
        sessions, source_mapping=source_mapping, semester_dates=semester_dates
    )


def _get_column(frame: pd.DataFrame, *names: str) -> str:
    """Return the first matching column name."""
    for name in names:
        if name in frame.columns:
            return name

    raise KeyError(
        f"Expected one of {names}; available columns are {list(frame.columns)}"
    )


def survey_progress_dataframe(
    sessions: pd.DataFrame | str | Path | None = None,
) -> pd.DataFrame:
    """
    Combine planned observations with archive observations.

    The returned DataFrame contains one row per source and these columns:

    - ``Source``
    - ``obs``
    - ``semester``
    - ``observed_26A``
    - ``observed_27B``
    - ``observed_total``
    """
    observations = load_sessions(sessions)
    source_column = _get_column(observations, "Source", "source")
    semester_column = _get_column(
        observations,
        "Semester",
        "semester",
        "Observing Semester",
        "observing_semester",
    )

    planned = planned_observations_dataframe()

    counts = (
        pd.DataFrame(
            {
                "Source": observations[source_column],
                "Semester": observations[semester_column],
            }
        )
        .groupby(["Source", "Semester"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=SEMESTERS, fill_value=0)
        .rename(columns={"26A": "observed_26A", "27B": "observed_27B"})
        .reset_index()
    )

    progress = planned.merge(counts, on="Source", how="left")

    for column in ("observed_26A", "observed_27B"):
        progress[column] = progress[column].fillna(0).astype(int)

    progress["observed_total"] = progress["observed_26A"] + progress["observed_27B"]

    return progress


def select_semester_columns(
    progress: pd.DataFrame,
    semester: str | None,
) -> pd.DataFrame:
    """
    Adds columns with summary statistics for the selected semester or whole project.
    It includes the following columns:
    n_observed - the number of observed sessions for the selected semester or total
    fraction_observed - the fraction of observed sessions for the selected semester or total
    plot_semester - the semester to be used for plotting (either the selected semester or the
    whole project)
    """
    if semester is not None and semester not in SEMESTERS:
        raise ValueError(
            f"semester must be one of {SEMESTERS} or None, got {semester!r}"
        )

    result = progress.copy()

    if semester is None:
        result["n_observed"] = result["observed_total"]
        result["plot_semester"] = result["semester"]
    else:
        result = result[result["semester"] == semester].copy()
        result["n_observed"] = result[f"observed_{semester}"]
        result["plot_semester"] = semester

    result["fraction_observed"] = (result["n_observed"] / result["obs"]).where(
        result["obs"] > 0
    )

    return result


def compute_cumulative_observed_time(
    sessions: pd.DataFrame | str | Path | None = None,
) -> pd.DataFrame:
    """Compute cumulative observed time from archive observation times."""
    observations = load_sessions(sessions)

    start_column = _get_column(
        observations,
        "Observation Start",
        "observation_start",
    )
    stop_column = _get_column(
        observations,
        "Observation Stop",
        "observation_stop",
    )

    start = pd.to_datetime(observations[start_column], errors="coerce")
    stop = pd.to_datetime(observations[stop_column], errors="coerce")

    frame = pd.DataFrame(
        {
            "date": stop,
            "duration_hours": (stop - start).dt.total_seconds() / 3600,
        }
    ).dropna()

    frame = frame[frame["duration_hours"] >= 0].sort_values("date")
    frame["cumulative_hours"] = frame["duration_hours"].cumsum()

    return frame
