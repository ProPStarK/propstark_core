from __future__ import annotations

import argparse
from pathlib import Path


def pst_to_ds9_fk5_regions(
	pst_path: str | Path,
	output_path: str | Path | None = None,
	radius_arcsec: float = 53.113,
	color: str = "cyan",
) -> Path:
	"""Convert a ; separated PST file into a DS9 FK5 region file of circles.

	PST format assumptions:
	- Column 1: pointing name
	- Column 5: RA string
	- Column 6: Dec string
	"""
	pst_path = Path(pst_path)
	if output_path is None:
		output_path = pst_path.with_suffix(".reg")
	else:
		output_path = Path(output_path)

	region_lines = [
		"# Region file format: DS9 version 4.1",
		(
			f"global color={color} dashlist=8 3 width=1 "
			"font=\"helvetica 10 normal\" select=1 highlite=1 dash=0 fixed=0 "
			"edit=1 move=1 delete=1 include=1 source=1"
		),
		"fk5",
	]

	n_regions = 0
	with pst_path.open("r", encoding="utf-8") as f_in:
		for raw_line in f_in:
			line = raw_line.strip()

			if not line or line.startswith("#"):
				continue

			cols = [c.strip() for c in line.split(";")]
			if len(cols) < 6:
				continue

			name = cols[0]
			ra = cols[4]
			dec = cols[5]

			# Skip likely header rows such as NAME;...;RA;DEC
			if ra.lower().startswith("ra") and dec.lower().startswith("dec"):
				continue

			if not ra or not dec:
				continue

			region_lines.append(f'circle({ra},{dec},{radius_arcsec}\") # text={{{name}}}')
			n_regions += 1

	if n_regions == 0:
		raise ValueError(
			"No valid pointings found in PST file. "
			"Check that columns 5 and 6 contain RA/Dec strings."
		)

	with output_path.open("w", encoding="utf-8") as f_out:
		f_out.write("\n".join(region_lines) + "\n")

	return output_path


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
