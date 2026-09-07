from __future__ import annotations

import astropy.units as u
import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from propstark_core import pointings


def make_wcs_header() -> fits.Header:
    # create a simple WCS header for testing purposes
    wcs = WCS(naxis=2)
    wcs.wcs.crpix = [1, 1]
    wcs.wcs.cdelt = np.array([-0.01, 0.01])
    wcs.wcs.crval = [30.0, 40.0]
    wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
    return wcs.to_header()


def test_pst_to_ds9_fk5_regions_writes_valid_regions(tmp_path) -> None:
    # creates a PST file with one valid pointing and one comment line,
    # then converts it to DS9 region file
    pst_path = tmp_path / "pointings.pst"
    pst_path.write_text(
        "# Comment\nNAME;A;B;C;RA;DEC\nfield-1;A;B;C;02:00:00;+40:00:00\n",
        encoding="utf-8",
    )

    output_path = pointings.pst_to_ds9_fk5_regions(
        pst_path, radius_arcsec=42.0, color="red"
    )

    assert output_path == pst_path.with_suffix(".reg")
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "# Region file format: DS9 version 4.1",
        'global color=red dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1',
        "fk5",
        'circle(02:00:00,+40:00:00,42.0") # text={field-1}',
    ]


def test_pst_to_ds9_fk5_regions_rejects_file_without_pointings(tmp_path) -> None:
    # check that a PST file with no valid pointings raises a ValueError
    pst_path = tmp_path / "empty.pst"
    pst_path.write_text("NAME;A;B;C;RA;DEC\n", encoding="utf-8")

    with pytest.raises(ValueError, match="No valid pointings"):
        pointings.pst_to_ds9_fk5_regions(pst_path)


def test_pointings_on_image_filters_low_and_out_of_bounds_points() -> None:
    header = make_wcs_header()
    wcs = WCS(header)
    bright_point, dim_point, outside_point = wcs.pixel_to_world([1, 2, 20], [1, 2, 20])
    image = np.zeros((4, 4))
    image[1, 1] = 2.0
    image[2, 2] = 0.5

    retained = pointings._pointings_on_image(
        [bright_point, dim_point, outside_point], header, image, threshold=1.0
    )

    assert retained == [bright_point]


def test_plot_pointings_draws_retained_source_pointings(tmp_path, monkeypatch) -> None:
    header = make_wcs_header()
    image_path = tmp_path / "map.fits"
    image = np.ones((4, 4))
    fits.PrimaryHDU(image, header).writeto(image_path)
    wcs = WCS(header)
    expected_pointing = wcs.pixel_to_world(1, 1)
    drawn = []

    monkeypatch.setattr(pointings, "_plot_image", lambda *args: None)
    monkeypatch.setattr(
        pointings.mph, "compute_pointings", lambda *args, **kwargs: [expected_pointing]
    )
    monkeypatch.setattr(
        pointings.plotting,
        "plot_circle_wcs",
        lambda *args, **kwargs: drawn.append(args),
    )

    axes, retained = pointings.plot_pointings(
        image_path,
        {
            "target-A": {
                "RA0": "02:00:00",
                "Dec0": "+40:00:00",
                "width": "1 arcmin",
                "height": "1 arcmin",
                "PA": "0 deg",
            },
            "other-B": {
                "RA0": "02:00:00",
                "Dec0": "+40:00:00",
                "width": "1 arcmin",
                "height": "1 arcmin",
                "PA": "0 deg",
            },
        },
        "target",
        threshold=0.5,
        primary_beam=1 * u.deg,
    )

    assert axes.figure is not None
    assert retained == [expected_pointing]
    assert len(drawn) == 1
