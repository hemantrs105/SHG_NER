"""Expand gold_spec.txt into gold.csv and check every surface exists on its line."""
import csv, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
rows, errors = [], []
for raw in (ROOT / "gold/gold_spec.txt").read_text(encoding="utf-8").splitlines():
    line = raw.split("#", 1)[0].strip()
    if not line:
        continue
    head, body = line.split("|", 1)
    page, lno = head.split()
    text_lines = (ROOT / "text/clean" / f"{page}.txt").read_text(encoding="utf-8").splitlines()
    src = text_lines[int(lno) - 1]
    for item in body.split(";"):
        item = item.strip()
        cat = "role_only" if "[role_only]" in item else "name"
        item = item.replace("[role_only]", "").strip()
        rep = 2 if item.endswith(" x2") else 1
        item = item[:-3].strip() if rep == 2 else item
        surface, exp = [x.strip() for x in item.rsplit("=", 1)]
        if src.count(surface) < rep:
            errors.append(f"{page}:{lno} surface {surface!r} x{rep} not found in: {src}")
        for _ in range(rep):
            rows.append({"page": page, "line": lno, "surface": surface, "expected": exp, "category": cat})
with open(ROOT / "gold/gold.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["page", "line", "surface", "expected", "category"])
    w.writeheader(); w.writerows(rows)
print(len(rows), "gold mentions")
print("\n".join(errors) if errors else "all surfaces found on their lines")
sys.exit(1 if errors else 0)
