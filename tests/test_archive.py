from __future__ import annotations

import pandas as pd

from propstark_core.archive import (
    get_number_observation_per_region,
    load_observations_csv,
)


def test_load_observations_csv_loads_bundled_data() -> None:
    observations = load_observations_csv()

    assert not observations.empty
    assert {"Archive File", "Project", "Source"} <= set(observations.columns)


def test_load_observations_csv_accepts_custom_path(tmp_path) -> None:
    csv_path = tmp_path / "observations.csv"
    expected = pd.DataFrame({"Source": ["Test source"], "Scans": [3]})
    expected.to_csv(csv_path, index=False)

    observations = load_observations_csv(csv_path)

    pd.testing.assert_frame_equal(observations, expected)


def test_get_number_observation_per_region_includes_planned_count() -> None:
    observations = pd.DataFrame({"Source": ["L1448", "L1448", "L1455"]})

    summary = get_number_observation_per_region(observations)

    expected = pd.DataFrame(
        {
            "Source": ["L1448", "L1455"],
            "N_Obs": [2, 1],
            "N_Expected": [7, 2],
        }
    )
    pd.testing.assert_frame_equal(summary, expected)
