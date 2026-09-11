"""Static metadata and progress tracking for the ProPStarK survey."""

from pathlib import Path
from typing import TypedDict

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


def load_sessions(
    sessions: pd.DataFrame | str | Path | None = None,
) -> pd.DataFrame:
    """
    Load archive observations from a DataFrame or CSV file.
    This represents the observations actually carried out during the semester.
    """
    if isinstance(sessions, pd.DataFrame):
        return sessions.copy()

    from .archive import load_observations_csv

    return load_observations_csv(sessions)


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
