#!/usr/bin/env python3
"""Score resolver decisions against the frozen answer key.

Usage: python score.py [--split dev|test|all] [--text clean] [--show-errors]
"""
import argparse, csv, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))          # works under python -I too
from resolve import key, ratio
ap = argparse.ArgumentParser()
ap.add_argument("--split", default="dev")
ap.add_argument("--text", default="clean")
ap.add_argument("--show-errors", action="store_true")
a = ap.parse_args()

split_of = {r["page"]: r["split"] for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))}
gold = [g for g in csv.DictReader(open(ROOT / "gold/gold.csv", encoding="utf-8"))
        if a.split == "all" or split_of[g["page"]] == a.split]
pred = list(csv.DictReader(open(ROOT / "out" / f"decisions_{a.text}_{a.split}.csv", encoding="utf-8")))

SUFFIX_KEYS = [key(s) for s in "देवी कुमारी कुमार प्रसाद रानी".split()]


def given_part(surface):
    """Drop surname-like words (also misspelt ones, e.g. कुमाी) before comparing, so
    'बीना कुमारी' is not paired with 'चंदा कुमारी' just because both end in कुमारी."""
    toks = surface.split()
    keep = [t for t in toks if max(ratio(key(t), s) for s in SUFFIX_KEYS) < 0.6]
    return key("".join(keep or toks))


used, outcomes, errors = set(), Counter(), []
for g in gold:
    best, best_r = None, 0.0
    for i, p in enumerate(pred):
        if i in used or p["page"] != g["page"] or p["line"] != g["line"]:
            continue
        r = ratio(given_part(p["surface"]), given_part(g["surface"]))
        if g["category"] == "role_only" and g["surface"].startswith(p["surface"]):
            r = 1.0      # resolver reports "CM", key says "CM दीदी": same reference
        if r > best_r:   # strict: on a tie the earlier mention on the line wins
            best, best_r = i, r
    if best is None or best_r < 0.7:
        res = "missed"
        got = "-"
    else:
        used.add(best)
        got = pred[best]["decision"]
        exp = g["expected"]
        if exp in ("ASK", "NEW"):
            res = "correct no-link" if got in ("ASK", "NEW") else "WRONG: guessed"
        elif got == exp:
            res = "correct link"
        elif got == "ASK":
            res = "asked, link was possible"
        elif got == "NEW":
            res = "said not-on-roster, was on roster"
        else:
            res = "WRONG: linked to another person"
    outcomes[(g["category"], res)] += 1
    if not res.startswith("correct"):
        errors.append((res, g["page"], g["line"], g["surface"], g["expected"], got,
                       pred[best]["why"] if best is not None else ""))

spurious = [p for i, p in enumerate(pred) if i not in used]
names = [g for g in gold if g["category"] == "name"]
n = len(names)
c = lambda r: outcomes[("name", r)]
print(f"split={a.split} text={a.text}: {n} name mentions, {len(gold) - n} role-only")
for r in ["correct link", "correct no-link", "asked, link was possible",
          "said not-on-roster, was on roster", "missed", "WRONG: linked to another person", "WRONG: guessed"]:
    print(f"  {r:<36} {c(r):>4}  ({100 * c(r) / n:5.1f}%)")
print(f"  spurious mentions (not in key)       {len(spurious):>4}")
ro = [g for g in gold if g["category"] == "role_only"]
if ro:
    print(f"  role-only references correct         {outcomes[('role_only', 'correct link')]}/{len(ro)}")
links_made = c("correct link") + c("WRONG: linked to another person") + c("WRONG: guessed")
if links_made:
    print(f"  precision of links made: {100 * c('correct link') / links_made:.1f}%   "
          f"wrong links: {c('WRONG: linked to another person') + c('WRONG: guessed')}")
if a.show_errors:
    for e in errors:
        print("  -", " | ".join(map(str, e)))
    for p in spurious:
        print("  - spurious |", p["page"], p["line"], p["surface"], p["decision"], p["why"])
