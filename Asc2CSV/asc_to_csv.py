from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


DEFAULT_SOURCE_DIR = Path(
    "E:\\OneDrive - UnispectralCN\\01_\u7814\u53d1\\01-\u5f00\u53d1\u76f8\u5173\\"
    "07_MEMS\\03_Coating\\02-Macleod-\u4eff\u771f\u6570\u636e\u5e93\\Freeze\\214S\\"
    "UC700\\MDL04\u00a00623"
)
DEFAULT_EXPORT_DIR = Path(__file__).resolve().parent / "export"

NUMBER_PAIR_RE = re.compile(
    r"^\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    r"\s+"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    r"\s*$"
)


def parse_data_rows(asc_path: Path) -> list[tuple[str, str]]:
    lines = asc_path.read_text(encoding="latin-1").splitlines()

    data_start = next(
        (index + 1 for index, line in enumerate(lines) if line.strip().upper() == "#DATA"),
        None,
    )
    if data_start is not None:
        return collect_numeric_rows(lines[data_start:])

    return find_longest_numeric_block(lines)


def collect_numeric_rows(lines: list[str]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []

    for line in lines:
        match = NUMBER_PAIR_RE.match(line)
        if match:
            rows.append((match.group(1), match.group(2)))
        elif rows:
            break

    return rows


def find_longest_numeric_block(lines: list[str]) -> list[tuple[str, str]]:
    longest: list[tuple[str, str]] = []
    current: list[tuple[str, str]] = []

    for line in lines:
        match = NUMBER_PAIR_RE.match(line)
        if match:
            current.append((match.group(1), match.group(2)))
            continue

        if len(current) > len(longest):
            longest = current
        current = []

    if len(current) > len(longest):
        longest = current

    return longest


def convert_file(asc_path: Path, export_dir: Path) -> Path:
    rows = parse_data_rows(asc_path)
    if not rows:
        raise ValueError(f"No wavelength/transmittance data found: {asc_path}")

    export_dir.mkdir(parents=True, exist_ok=True)
    csv_path = export_dir / f"{asc_path.stem}.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(rows)

    return csv_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert ASC files to CSV files with wavelength and transmittance columns."
    )
    parser.add_argument(
        "source_dir",
        nargs="?",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="Directory containing ASC files.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=DEFAULT_EXPORT_DIR,
        help="Directory for exported CSV files.",
    )
    args = parser.parse_args()

    source_dir = args.source_dir
    export_dir = args.output_dir

    if not source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_dir}")

    asc_files = sorted(source_dir.glob("*.asc"))
    if not asc_files:
        raise SystemExit(f"No ASC files found in: {source_dir}")

    for asc_path in asc_files:
        csv_path = convert_file(asc_path, export_dir)
        print(f"{asc_path.name} -> {csv_path}")

    print(f"Converted {len(asc_files)} file(s).")


if __name__ == "__main__":
    main()
