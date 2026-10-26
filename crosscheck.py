#!/usr/bin/env python3
"""Two independent reads of a register table: how often do they agree, and are agreed cells right?

Usage: python crosscheck.py <labelA> <labelB> [dev|test|all]
  labels are folders under text/ (e.g. ocr_lab_harness+post_dev), as written by eval_ocr.py.
Table rows are matched by serial number (first cell) between read A, read B and the reference reading.
Fields: the name cell (2nd), the signature cell (last), and each number cell (left to right).
A field "agrees" when both reads give the same text (spaces ignored). It is "right" when it equals the reference.
"""
import csv, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROW = re.compile(r"^\s*(\d{1,3})\s*\.?\s*\|")


def rows(path):
    out = {}
    for l in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(l)
        if m and m.group(1) not in out:
            cells = [c.strip() for c in l.split("|")]
            while len(cells) > 2 and not cells[-1]:          # a trailing "|" is not an empty signature
                cells.pop()
            out[m.group(1)] = cells
    return out


def fields(cells):
    f = {"name": cells[1] if len(cells) > 1 else "", "signature": cells[-1] if len(cells) > 2 else ""}
    nums = [re.sub(r"[^\d]", "", c) for c in cells[2:] if re.fullmatch(r"[\d,./-]+", c)]
    for i, n in enumerate(nums):
        f[f"num{i}"] = n
    f["numbers"] = " ".join(nums)
    return f


def norm(s):
    s = re.sub(r"\[[^\]]*\]", "", s)                       # [अँगूठा], [कटा हुआ]
    return re.sub(r"\s+", "", s)


def main():
    la, lb = sys.argv[1], sys.argv[2]
    split = sys.argv[3] if len(sys.argv) > 3 else "all"
    pages = [r["page"] for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))
             if split in ("all", r["split"]) and r["kind"] == "table"]
    stats = {k: Counter() for k in ("name", "signature", "numbers")}
    for p in pages:
        fa, fb = ROOT / "text" / la / f"{p}.txt", ROOT / "text" / lb / f"{p}.txt"
        if not (fa.exists() and fb.exists()):
            continue
        ref, A, B = rows(ROOT / "text/clean" / f"{p}.txt"), rows(fa), rows(fb)
        for n, rc in ref.items():
            r = fields(rc)
            a, b = fields(A[n]) if n in A else None, fields(B[n]) if n in B else None
            for k in stats:
                if not r[k]:
                    continue
                va, vb = (norm(a[k]) if a else ""), (norm(b[k]) if b else "")
                truth = norm(r[k])
                agree = va == vb and va != ""
                stats[k]["fields"] += 1
                stats[k]["A right"] += va == truth
                stats[k]["agree"] += agree
                stats[k]["agree, right"] += agree and va == truth
                stats[k]["agree, wrong"] += agree and va != truth
                stats[k]["disagree"] += not agree
                stats[k]["A wrong"] += va != truth
                stats[k]["A wrong, caught by disagreement"] += va != truth and not agree
    print(f"A = {la}\nB = {lb}\nsplit = {split} (table pages)\n")
    print(f"{'field':<10} {'n':>4} {'A right':>8} {'agree':>6} {'agreed & right':>15} {'agreed & wrong':>15} "
          f"{'A errors caught':>16}")
    for k, s in stats.items():
        n = s["fields"]
        print(f"{k:<10} {n:>4} {s['A right']:>8} {s['agree']:>6} "
              f"{s['agree, right']:>7} ({100 * s['agree, right'] / max(s['agree'], 1):4.1f}%) "
              f"{s['agree, wrong']:>7} ({100 * s['agree, wrong'] / max(s['agree'], 1):4.1f}%) "
              f"{s['A wrong, caught by disagreement']:>6} of {s['A wrong']:<4}")


if __name__ == "__main__":
    main()
