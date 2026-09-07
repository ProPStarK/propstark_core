from __future__ import annotations

import argparse

from propstark_core.pointings import pst_to_ds9_fk5_regions


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a ; separated PST file into a DS9 FK5 region file "
            "with circle regions."
        )
    )
    parser.add_argument("pst_path", help="Input PST file path")
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        default=None,
        help="Output DS9 region file path (default: same stem as PST, .reg)",
    )
    parser.add_argument(
        "-r",
        "--radius-arcsec",
        type=float,
        default=53.113,
        help="Circle radius in arcseconds (default: 53.113)",
    )
    parser.add_argument(
        "-c",
        "--color",
        default="cyan",
        help="DS9 region color (default: cyan)",
    )
    args = parser.parse_args()

    output = pst_to_ds9_fk5_regions(
        pst_path=args.pst_path,
        output_path=args.output_path,
        radius_arcsec=args.radius_arcsec,
        color=args.color,
    )
    print(f"Wrote DS9 region file: {output}")


if __name__ == "__main__":
    main()
