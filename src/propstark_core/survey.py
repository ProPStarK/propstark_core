"""Static metadata for the ProPStarK survey."""

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
planned_obs = {
    "L1448": {"obs": 7, "semester": "26A"},
    "L1455": {"obs": 2, "semester": "26A"},
    "L1228": {"obs": 2, "semester": "26A"},
    "IC348-Main": {"obs": 10, "semester": "26A"},
    "IC348-SE": {"obs": 3, "semester": "26A"},
    "L1251-A": {"obs": 7, "semester": "26A"},
    "L1251-B": {"obs": 10, "semester": "26A"},
    "L1495-A": {"obs": 2, "semester": "26A"},
    "L1495-B": {"obs": 3, "semester": "26A"},
    "L1495-C": {"obs": 6, "semester": "26A"},
    "L1495-D": {"obs": 3, "semester": "26A"},
    "L1495-E": {"obs": 2, "semester": "26A"},
    "L1495-F": {"obs": 2, "semester": "26A"},
    "Serpens_MWC297": {"obs": 2, "semester": "26A"},
    "B18-A": {"obs": 2, "semester": "27B"},
    "B18-B": {"obs": 4, "semester": "27B"},
    "B18-C": {"obs": 2, "semester": "27B"},
    "B18-D": {"obs": 2, "semester": "27B"},
    "L1451": {"obs": 1, "semester": "27B"},
    "TMC1-1C": {"obs": 6, "semester": "27B"},
    "Barnard1-Main": {"obs": 10, "semester": "27B"},
    "Barnard1-South": {"obs": 3, "semester": "27B"},
    "B1E": {"obs": 1, "semester": "27B"},
    "Per7/34": {"obs": 1, "semester": "27B"},
    "L1688": {"obs": 2, "semester": "27B"},
    "L1689": {"obs": 2, "semester": "27B"},
    "L1712": {"obs": 2, "semester": "27B"},
    "Orion A": {"obs": 3, "semester": "27B"},
    "Orion A-S": {"obs": 3, "semester": "27B"},
    "NGC2023": {"obs": 3, "semester": "27B"},
    "NGCC2068": {"obs": 3, "semester": "27B"},
    "IC5146": {"obs": 4, "semester": "27B"},
    "CrAEast": {"obs": 4, "semester": "27B"},
    "CrAWest": {"obs": 4, "semester": "27B"},
    "B59": {"obs": 4, "semester": "27B"},
    "Core40": {"obs": 4, "semester": "27B"},
    "Serpens_Aquila": {"obs": 5, "semester": "27B"},
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
