#!/usr/bin/env python3
"""Synthetic stress test: does the resolver fail safe on noisy text?

The local OCR model produced no usable transcript, so there is no real OCR text to
test on. Instead we corrupt the reference text with the confusions Devanagari OCR
and handwriting typically produce, at increasing rates, and count wrong links.
This is SYNTHETIC noise. It shows robustness, not field accuracy.

Usage: python stress.py [--split all] [--seeds 5]
"""
import argparse, csv, random, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SWAPS = {"ि": "ी", "ी": "ि", "ु": "ू", "ू": "ु", "ब": "व", "व": "ब", "श": "स", "स": "श",
         "ष": "स", "न": "ण", "ण": "न", "े": "ै", "ा": "", "ं": "", "ँ": "ं"}


def corrupt(text, rate, rng):
    out = []
    for ch in text:
        if ch in SWAPS and rng.random() < rate:
            out.append(SWAPS[ch])
        elif "ऀ" <= ch <= "ॿ" and rng.random() < rate / 4:
            continue                                    # dropped character
        else:
            out.append(ch)
    return "".join(out)


ap = argparse.ArgumentParser()
ap.add_argument("--split", default="all")
ap.add_argument("--seeds", type=int, default=5)
a = ap.parse_args()

pages = [r["page"] for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))]
print(f"{'noise':>6} {'seed':>4} {'correct':>8} {'asked':>6} {'not-on-roster':>14} {'missed':>7} {'WRONG':>6}")
for rate in (0.0, 0.05, 0.10, 0.20, 0.30):
    for seed in range(a.seeds if rate else 1):
        name = f"noise_{int(rate * 100):02d}_{seed}"
        d = ROOT / "text" / name
        d.mkdir(parents=True, exist_ok=True)
        rng = random.Random(seed)
        for p in pages:
            src = (ROOT / "text/clean" / f"{p}.txt").read_text(encoding="utf-8")
            (d / f"{p}.txt").write_text(corrupt(src, rate, rng), encoding="utf-8")
        subprocess.run([sys.executable, "-I", str(ROOT / "resolve.py"), "--split", a.split,
                        "--text", name, "--quiet"], check=True, capture_output=True)
        out = subprocess.run([sys.executable, "-I", str(ROOT / "score.py"), "--split", a.split,
                              "--text", name], check=True, capture_output=True, text=True).stdout
        get = lambda label: int(re.search(r"\s(\d+)\s", next(l for l in out.splitlines() if label in l)).group(1))
        ok = get("correct link") + get("correct no-link")
        wrong = get("WRONG: linked") + get("WRONG: guessed")
        print(f"{rate:>6.0%} {seed:>4} {ok:>8} {get('asked, link'):>6} {get('said not-on'):>14} "
              f"{get('missed'):>7} {wrong:>6}")
        shutil.rmtree(d)
        (ROOT / "out" / f"decisions_{name}_{a.split}.csv").unlink()
