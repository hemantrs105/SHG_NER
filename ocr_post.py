#!/usr/bin/env python3
"""Clean BODHAN's text before name resolution. No model, standard library only.

Usage: python ocr_post.py <ocr_out_dir> <new_dir> [--split dev|test|all]
Copies every page's .md (and .json) from <ocr_out_dir> to <new_dir>, with these fixes:

1. LaTeX to plain text. BODHAN's text prompt asks for maths in LaTeX, so some register lines come back as
   $$\\text{कुल सख्त} = \\frac{140}{1}$$. (The harness does this too.)
2. Devanagari digits to ASCII digits (१२ -> 12).
3. A space where Devanagari and Latin letters touch: "देवीCNRP" -> "देवी CNRP", "C.Mसीमा" -> "C.M सीमा";
   and before capitals that follow a lower-case letter: "kumariCNRP" -> "kumari CNRP".
   BODHAN glues a role written beside a name onto the name.
4. A space before a surname word glued onto a name: "सुनिताकुमारी" -> "सुनिता कुमारी",
   "Dikshakumari" -> "Diksha kumari". Compound given names (राजकुमार, ...) are left alone.

5. Tables read in strips (one block cut into several, as the harness does for big tables) can repeat a
   row or the header: the header band stacked over each strip includes the first data row. Within a run
   of adjacent tables, a row whose serial number was already seen is dropped, and so is a header row
   after the first table. A repeated row would post the same member twice.

Nothing here knows the roster or the page.
"""
import argparse, csv, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DEVA = "\u0900-\u097F"
SUFFIXES = ["कुमारी", "कुमार", "देवी", "प्रसाद"]    # longest first; not रानी: पुरानी, निगरानी are words
COMPOUND_NAMES = {"राजकुमार", "राजकुमारी", "सुकुमार", "सुकुमारी", "नंदकुमार", "शिवकुमार", "रामप्रसाद",
                  "शिवप्रसाद", "देवप्रसाद", "गुरुप्रसाद", "कालीप्रसाद", "दुर्गाप्रसाद", "श्रीदेवी", "महादेवी"}
LATIN_SUFFIX = re.compile(r"(?<![A-Za-z])([A-Za-z]{3,}?)([Kk]umari|[Kk]umar|[Dd]evi|[Pp]rasad|[Rr]ani)(?![a-z])")
LATIN_COMPOUND = {"rajkumar", "rajkumari", "sukumar", "nandkumar", "shivkumar", "ramprasad", "shivprasad"}
DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def latex_to_plain(t):
    t = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", t)
    t = re.sub(r"\\(?:text|mathrm|textbf|mathbf)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:quad|qquad|,|;|:|!| )", " ", t)
    t = re.sub(r"\\(?:times|cdot)", "x", t)
    t = re.sub(r"\\[A-Za-z]+", "", t)
    t = t.replace("$$", " ").replace("$", " ")
    t = re.sub(r"[{}]", "", t)
    return re.sub(r"[ \t]{2,}", " ", t)


def split_suffix(word):
    if word in COMPOUND_NAMES:
        return word
    for s in SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 2:
            head = word[: -len(s)]
            if head[-1] in "्":                              # half letter: not a word boundary
                return word
            return f"{split_suffix(head)} {s}"
    return word


TABLE = re.compile(r"<table.*?</table>", re.S | re.I)
TR = re.compile(r"<tr[^>]*>.*?</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)


def dedupe_strips(md):
    out, last, seen = [], 0, set()
    for m in TABLE.finditer(md):
        gap = md[last:m.start()]
        if gap.strip():                                       # text between tables: a new run starts
            seen = None
        out.append(gap)
        tbl = m.group(0)
        if seen is None or not out[:-1]:
            seen = set()
            first = True
        else:
            first = False
        def keep(tr):
            cells = [re.sub(r"<[^>]+>", "", c).strip() for c in CELL.findall(tr.group(0))]
            if not cells:
                return tr.group(0)
            if "<th" in tr.group(0).lower() or not re.fullmatch(r"\d{1,3}\.?", cells[0].translate(DIGITS)):
                return tr.group(0) if first else ""         # header rows only from the run's first table
            n = int(cells[0].translate(DIGITS).rstrip("."))
            if n in seen:
                return ""
            seen.add(n)
            return tr.group(0)
        out.append(TR.sub(keep, tbl))
        last = m.end()
    out.append(md[last:])
    return "".join(out)


def clean(text):
    t = dedupe_strips(text)
    t = latex_to_plain(t)
    t = t.translate(DIGITS)
    t = re.sub(rf"(?<=[{DEVA}])(?=[A-Za-z])|(?<=[A-Za-z.])(?=[{DEVA}])", " ", t)
    t = re.sub(r"(?<=[a-z])(?=[A-Z][A-Z.])", " ", t)                 # "kumariCNRP" -> "kumari CNRP"
    t = re.sub(rf"[{DEVA}]+", lambda m: split_suffix(m.group(0)), t)
    t = LATIN_SUFFIX.sub(lambda m: m.group(0) if m.group(0).lower() in LATIN_COMPOUND
                         else f"{m.group(1)} {m.group(2)}", t)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--split", default="all", choices=["dev", "test", "all"])
    a = ap.parse_args()
    keep = {r["page"] for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))
            if a.split == "all" or r["split"] == a.split}
    a.dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(a.src.glob("*.md")):
        if f.stem not in keep:
            continue
        (a.dst / f.name).write_text(clean(f.read_text(encoding="utf-8")), encoding="utf-8")
        if f.with_suffix(".json").exists():
            shutil.copy(f.with_suffix(".json"), a.dst / f"{f.stem}.json")
        n += 1
    print(f"{n} pages cleaned -> {a.dst}")


if __name__ == "__main__":
    main()
