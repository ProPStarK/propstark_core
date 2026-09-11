"""Plot VLA pointing footprints over integrated intensity maps."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import astropy.units as u
import matplotlib.pyplot as plt
import mosaic_proposal_helper as mph
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.units import Quantity
from astropy.visualization.wcsaxes import add_beam, add_scalebar
from astropy.wcs import WCS
from matplotlib.axes import Axes
from mosaic_proposal_helper import plotting


def pst_to_ds9_fk5_regions(
    pst_path: str | Path,
    output_path: str | Path | None = None,
    radius_arcsec: float = 53.113,
    color: str = "cyan",
) -> Path:
    """Convert a semicolon-delimited PST file into DS9 FK5 circle regions.

    The PST file must provide the pointing name, RA, and Dec in columns 1, 5,
    and 6, respectively.
    """
    pst_path = Path(pst_path)
    output_path = (
        pst_path.with_suffix(".reg") if output_path is None else Path(output_path)
    )
    region_lines = [
        "# Region file format: DS9 version 4.1",
        (
            f"global color={color} dashlist=8 3 width=1 "
            'font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 '
            "edit=1 move=1 delete=1 include=1 source=1"
        ),
        "fk5",
    ]

    with pst_path.open(encoding="utf-8") as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            columns = [column.strip() for column in line.split(";")]
            if len(columns) < 6:
                continue

            name, right_ascension, declination = columns[0], columns[4], columns[5]
            if (
                (
                    right_ascension.lower().startswith("ra")
                    and declination.lower().startswith("dec")
                )
                or not right_ascension
                or not declination
            ):
                continue

            region_lines.append(
                f'circle({right_ascension},{declination},{radius_arcsec}") # text={{{name}}}'
            )

    if len(region_lines) == 3:
        raise ValueError(
            "No valid pointings found in PST file. "
            "Check that columns 5 and 6 contain RA/Dec strings."
        )

    output_path.write_text("\n".join(region_lines) + "\n", encoding="utf-8")
    return output_path


def _pointings_on_image(
    pointings: list[SkyCoord],
    header: fits.Header,
    image: np.ndarray,
    threshold: float,
) -> list[SkyCoord]:
    wcs = WCS(header)
    selected = []
    height, width = image.shape[-2:]
    for pointing in pointings:
        x_coordinate, y_coordinate = wcs.world_to_pixel(pointing)
        x_index, y_index = int(x_coordinate), int(y_coordinate)
        if (
            0 <= x_index < width
            and 0 <= y_index < height
            and image[y_index, x_index] > threshold
        ):
            selected.append(pointing)
    return selected


def _plot_image(
    image_hdu: fits.PrimaryHDU,
    axes: Axes,
    cmap: str | object,
    wcs: WCS,
    distance: Quantity,
    label_color: str,
    vmin: float | None,
    vmax: float | None,
) -> None:
    axes.imshow(
        image_hdu.data,
        origin="lower",
        interpolation="none",
        cmap=cmap,
        transform=axes.get_transform(wcs),
        vmin=vmin,
        vmax=vmax,
    )
    length = (0.1 * u.pc / distance).to(u.deg, u.dimensionless_angles())
    add_scalebar(axes, length, label="0.1 pc", color=label_color, corner="bottom right")
    add_beam(
        axes,
        header=image_hdu.header,
        frame=False,
        pad=0.4,
        facecolor=label_color,
        corner="bottom left",
        edgecolor="black",
    )


def plot_pointings(
    image_path: str | Path,
    catalogue: Mapping[str, Mapping[str, str]],
    source_catalogue: str,
    distance: Quantity = 300 * u.pc,
    *,
    cmap: str | object = "inferno",
    label_color: str = "black",
    threshold: float = 1.0,
    vmin: float | None = None,
    vmax: float | None = None,
    linestyle: str = ":",
    primary_beam: Quantity | None = None,
) -> tuple[Axes, list[SkyCoord]]:
    """Plot valid VLA pointing footprints for a catalogue source.

    Parameters
    ----------
    image_path
        FITS integrated-intensity map to display.
    catalogue
        Mapping loaded from ``catalogue_boxes.yml``.
    source_catalogue
        Prefix selecting catalogue entries to plot.
    distance
        Source distance, used for the 0.1 pc scale bar.

    Returns
    -------
    axes, pointings
        WCS-aware axes and the pointings retained above ``threshold``.
    """
    image_path = Path(image_path)
    with fits.open(image_path) as hdul:
        image_hdu = hdul[0].copy()

    wcs = WCS(image_hdu.header)
    figure = plt.figure(figsize=(7, 7))
    axes = figure.add_subplot(111, projection=wcs)
    _plot_image(image_hdu, axes, cmap, wcs, distance, label_color, vmin, vmax)

    if primary_beam is None:
        primary_beam = plotting.pb_interferometer(23.723 * u.GHz, telescope="vla")

    retained_pointings = []
    for source_name, source in catalogue.items():
        if not source_name.startswith(source_catalogue):
            continue
        center = SkyCoord(source["RA0"], source["Dec0"], unit=(u.hourangle, u.deg))
        pointings = mph.compute_pointings(
            center.ra,
            center.dec,
            width=u.Quantity(source["width"]),
            height=u.Quantity(source["height"]),
            pb=primary_beam,
            pa=u.Quantity(source["PA"]),
        )
        for pointing in _pointings_on_image(
            pointings, image_hdu.header, image_hdu.data, threshold
        ):
            retained_pointings.append(pointing)
            plotting.plot_circle_wcs(
                axes,
                (pointing.ra, pointing.dec),
                primary_beam / 2,
                edgecolor="white",
                lw=0.5,
                alpha=1,
                ls=linestyle,
            )

    return axes, retained_pointings
