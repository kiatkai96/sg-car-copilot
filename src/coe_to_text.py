"""Turns the COE results spreadsheet into plain sentences the search can understand.

Why? A table row like "2024-03, 1, Category A, 99000" means little to a text search.
The sentence "In 2024-03, bidding 1, Category A: premium S$99000" is far easier to find.

How to use:
 1. Download the COE bidding results CSV from data.gov.sg
    (search "COE bidding results") and save it as  data/raw/coe.csv
 2. Run:  python -m src.coe_to_text
 3. Then re-run:  python -m src.ingest
"""
import pandas as pd

from .config import DOCS_DIR, RAW_DIR

SRC = RAW_DIR / "coe.csv"
OUT = DOCS_DIR / "coe_results.txt"


def main():
    if not SRC.exists():
        print(f"Can't find {SRC}. Download the CSV and save it there first (see the guide).")
        return
    df = pd.read_csv(SRC)
    df.columns = [c.strip().lower() for c in df.columns]
    print("Columns found in your file:", list(df.columns))

    def get(row, name):
        v = row.get(name)
        return "unknown" if pd.isna(v) else v

    lines = []
    for _, r in df.iterrows():
        lines.append(
            f"COE result - month {get(r, 'month')}, bidding exercise {get(r, 'bidding_no')}, "
            f"{get(r, 'vehicle_class')}: premium S${get(r, 'premium')}, quota {get(r, 'quota')}, "
            f"bids received {get(r, 'bids_received')}, successful bids {get(r, 'bids_success')}."
        )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {len(lines)} sentences to {OUT}")
    print("If you see lots of 'unknown', your column names differ - edit the names in this file.")


if __name__ == "__main__":
    main()
