# propstark_core
![PyPI - License](https://img.shields.io/pypi/l/propstark_core?color=green)
![PyPI - Version](https://img.shields.io/pypi/v/propstark_core)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2F2Fpropstark%2Fpropstark_core%2Fmaster%2Fpyproject.toml)

Collection of analysis and display helpers for the ProPStarK program.

## Installation

Installation using pip:
```python
pip install propstark_core
```

From the repository root:

Install the package from a clone with:
```bash
python -m pip install .
```

## Pointing plots

`plot_pointings` plots VLA pointing footprints over a FITS integrated-intensity map.
Load the catalogue boxes and pass explicit paths to the map and catalogue:

```python
import astropy.units as u
import yaml

from propstark_core import plot_pointings

with open("data/catalogue_boxes.yml", encoding="utf-8") as catalogue_file:
    catalogue = yaml.safe_load(catalogue_file)

axes, pointings = plot_pointings(
    "data/B1_NH3_11_all_rebase3_mom0_QA_trim.fits",
    catalogue,
    "Barnard1",
    distance=301 * u.pc,
)
```

The complete worked example remains in [pointings/image_overlay.ipynb](pointings/image_overlay.ipynb), ready to be included in future Read the Docs documentation.

The scheduling-block list is included in installed distributions and can be read with `propstark_core.load_observations_csv()`.

## Credits

Developed by Jaime E Pineda ([@jpinedaf](http://github.com/jpinedaf)) and Brian Svoboda ([@autocorr](http://github.com/autocorr)).

## Dependencies
---

- astropy (>=5.0)
- scipy (>=1.7)
- numpy (>=1.21)
- pyyaml
- matplotlib (>=3.4)
- radio-beam (>=0.3)
- mosaic_proposal_helper (>=0.5)
- scikit-image (>=0.9)