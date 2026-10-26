#!/usr/bin/env python3
"""Which reading errors cost the most names? Replace one kind of table field in an OCR run with the
reference reading, re-run the resolver, and count. Diagnostic only: it ranks fine-tuning targets.

Usage: python oracle_ablation.py <text label, e.g. ocr_lab_harness+post_test> <out prefix>
Writes ocr/<prefix>_<field>/<page>.md for field in: headers, anchors, names, all_table.
  headers    the column-header rows (they tell the resolver which columns hold repayments)
  anchors    every cell of a numbered row except the name and signature (role, village, MIS ID, amounts)
  names      the name and signature cells of numbered rows
  all_table  all of the above
Rows are matched by serial number. Free text is left as the OCR read it.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROW = re.compile(r"^\s*(\d{1,3})\s*\.?\s*\|")
DEVDIG = str.maketrans("०१२३४५६७८९", "0123456789")


def cells(l):
    c = [x.strip() for x in l.split("|")]
    while len(c) > 2 and not c[-1]:
        c.pop()
    return c


def is_header(l):
    return "|" in l and "नाम" in l and not ROW.match(l)


def hybrid(ocr_lines, ref_lines, field):
    ref_rows = {}
    for l in ref_lines:
        m = ROW.match(l)
        if m and m.group(1) not in ref_rows:
            ref_rows[m.group(1)] = cells(l)
    ref_headers = [l for l in ref_lines if is_header(l)]
    out, h = [], 0
    for l in ocr_lines:
        m = ROW.match(l.translate(DEVDIG))
        if field in ("headers", "all_table") and is_header(l):
            out.append(ref_headers[min(h, len(ref_headers) - 1)] if ref_headers else l)
            h += 1
            continue
        if not m or m.group(1) not in ref_rows or field == "headers":
            out.append(l)
            continue
        o, r = cells(l.translate(DEVDIG)), ref_rows[m.group(1)]
        if field == "names":
            o = o[:]
            if len(o) > 1:
                o[1] = r[1]
            if len(o) > 2 and len(r) > 2:
                o[-1] = r[-1]
            out.append(" | ".join(o))
        elif field == "anchors":
            r = r[:]
            r[1] = o[1] if len(o) > 1 else ""
            if len(r) > 2:
                r[-1] = o[-1] if len(o) > 2 else ""
            out.append(" | ".join(r))
        else:
            out.append(" | ".join(r))
    if field in ("headers", "all_table") and h == 0 and ref_headers:      # OCR lost the header row
        first = next((i for i, l in enumerate(out) if ROW.match(l)), None)
        if first is not None:
            out.insert(first, ref_headers[0])
    return out


def main():
    label, prefix = sys.argv[1], sys.argv[2]
    src = ROOT / "text" / label
    for field in ("headers", "anchors", "names", "all_table"):
        dst = ROOT / "ocr" / f"{prefix}_{field}"
        dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(src.glob("*.txt")):
            ref = (ROOT / "text/clean" / f.name).read_text(encoding="utf-8").splitlines()
            lines = hybrid(f.read_text(encoding="utf-8").splitlines(), ref, field)
            (dst / f"{f.stem}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
