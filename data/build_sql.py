"""Write tamarind_bank.sql: the 13 tables and every row, in one plain SQL file.

The reader's way in: run this one file in any PostgreSQL and the practice database is
built. Plain CREATE TABLE + multi-row INSERT, no COPY and no psql commands, so it also runs from
a query window in a graphical PostgreSQL tool. An empty CSV field is NULL, as COPY ... CSV reads it.

    python data/build_sql.py        (from the repository's top folder; Python 3, standard library only)
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "tamarind_bank.sql"
BATCH = 500

HEADER = """\
-- Tamarind Bank practice database, for the book "Banking Domain by Diagram" by Kapil Dev V.
-- Tamarind Bank Ltd, its customers and every row below are fictional; emails use example.com.
--
-- Run this whole file once in an empty PostgreSQL database. It creates 13 tables and fills them.
-- Then check:  SELECT count(*) FROM transactions;   -- 21054
--
-- Written by data/build_sql.py from data/schema.sql and data/csv/. Do not edit by hand.

"""


def literal(value: str) -> str:
    return "NULL" if value == "" else "'" + value.replace("'", "''") + "'"


def main() -> None:
    parts = [HEADER, (HERE / "schema.sql").read_text(encoding="utf-8").rstrip() + "\n"]
    counts = {}
    for path in sorted((HERE / "csv").glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        head, body = rows[0], rows[1:]
        counts[path.stem] = len(body)
        parts.append(f"\n-- {path.stem}: {len(body)} rows\n")
        for i in range(0, len(body), BATCH):
            values = ",\n".join("(" + ", ".join(literal(v) for v in r) + ")" for r in body[i:i + BATCH])
            parts.append(f"INSERT INTO {path.stem} ({', '.join(head)}) VALUES\n{values};\n")
    OUT.write_text("".join(parts), encoding="utf-8", newline="\n")
    print(f"{OUT.name}: {len(counts)} tables, {sum(counts.values())} rows, {OUT.stat().st_size:,} bytes")
    for table, n in counts.items():
        print(f"  {table} {n}")


if __name__ == "__main__":
    main()
