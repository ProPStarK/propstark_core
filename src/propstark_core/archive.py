"""Helpers for retrieving and reading VLA archive observations."""

from __future__ import annotations

import os
from importlib.resources import files
from pathlib import Path

import numpy as np
import pandas as pd
import pyvo
from dotenv import load_dotenv

from .survey import get_planned_observations

load_dotenv()
db_project = os.getenv("PROJECT_CODE", "26A-123")


def setup_service_vla() -> pyvo.dal.TAPService:
    """Set up a TAPService for the VLA archive."""
    service = pyvo.dal.TAPService("https://archive-new.nrao.edu/tap")
    return service


def query_proposal_id(
    service: pyvo.dal.TAPService, proposal_id: str = "26A-123"
) -> pd.DataFrame:
    """Return archive rows whose publisher ID contains ``proposal_id``."""
    query = f"""
        SELECT *
        FROM tap_schema.obscore
        WHERE obs_publisher_did LIKE '%{proposal_id}%'
    """
    return service.search(query).to_table().to_pandas()


def list_observations(
    service: pyvo.dal.TAPService, proposal_id: str = db_project
) -> np.ndarray:
    """Return the unique publisher IDs for an EVLA project code."""
    query = f"""
        SELECT *
        FROM tap_schema.obscore
        WHERE project_code LIKE '%{proposal_id}%'
    """
    table = service.search(query).to_table().to_pandas()
    return np.unique(table["obs_publisher_did"])


def load_observations_csv(file_path: str | Path | None = None) -> pd.DataFrame:
    """Load the observations CSV bundled with the package or a custom path."""
    if file_path is not None:
        return pd.read_csv(file_path)

    resource = files("propstark_core").joinpath("data/sb_list.csv")
    with resource.open("rb") as csv_file:
        return pd.read_csv(csv_file)


def get_number_observation_per_region(observations: pd.DataFrame) -> pd.DataFrame:
    """Return observed and expected observation counts per region."""
    summary = observations.groupby("Source").size().reset_index(name="N_Obs")
    summary["N_Expected"] = summary["Source"].map(get_planned_observations)
    return summary
