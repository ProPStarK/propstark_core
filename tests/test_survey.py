import pytest

from propstark_core.survey import REGION_DISTANCES, get_region_distance


def test_get_region_distance_returns_parsecs() -> None:
    assert get_region_distance("Barnard1") == 301.0
    assert get_region_distance("L1688") == 138.4


def test_get_region_distance_rejects_unknown_region() -> None:
    with pytest.raises(KeyError, match="Unknown ProPStarK region: Unknown"):
        get_region_distance("Unknown")


def test_region_distances_contains_all_known_regions() -> None:
    assert len(REGION_DISTANCES) == 27
