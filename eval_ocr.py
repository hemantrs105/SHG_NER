#!/usr/bin/env python3
"""Score an OCR run on the register pages, end to end.

Usage: python eval_ocr.py <ocr_out_dir> <label> [dev|test|all]
  <ocr_out_dir>  folder with <page>.md files written by `indic-ocr-harness read --out-dir`
  <label>        name for this run, e.g. bodhan_harness, bodhan_plain

It does four things:
  1. Converts each page's Markdown (tables as HTML) into text/ocr_<label>/<page>.txt,
     one table row per line with cells joined by " | ", the shape resolve.py reads.
  2. Character error rate (CER) against the reference readings in text/clean/.
  3. Numbers: how many of the reference page's numbers (amounts, dates, IDs) the OCR has.
  4. Runs resolve.py on the OCR text and scores names against the frozen answer key.
     OCR lines do not line up with the reference lines, so names are matched on the
     same page by first name, ignoring line numbers.

The reference readings are Claude's readings of the photos, not verified ground truth.
"""
import csv, html, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from resolve import key, ratio, role_of  # noqa: E402

try:                                   # fast edit distance if available (it is, in the OCR venv)
    from rapidfuzz.distance import Levenshtein
    def edits(a, b): return Levenshtein.distance(a, b)
except ImportError:
    def edits(a, b):
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]


def md_to_lines(md):
    """HTML tables -> 'cell | cell' rows; drop Markdown markup; keep the reading order."""
    def table(m):
        rows = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(0), flags=re.S | re.I):
            cells = [re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", " ", c, flags=re.I)).strip() for c in
                     re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, flags=re.S | re.I)]
            rows.append(" | ".join(html.unescape(c) for c in cells))
        return "\n" + "\n".join(rows) + "\n"
    md = re.sub(r"<table.*?</table>", table, md, flags=re.S | re.I)
    md = re.sub(r"<[^>]+>", " ", md)
    out = []
    for line in md.splitlines():
        line = re.sub(r"^\s*(#+|[-*]\s|\d+\.\s(?=\S))", lambda m: m.group(0) if m.group(0).strip()[0].isdigit() else "", line)
        line = line.replace("**", "").replace("__", "").strip()
        if line and not re.fullmatch(r"\|?\s*:?-{3,}.*", line):          # Markdown table rules
            out.append(line.strip("| ").replace("  ", " ") if line.startswith("|") else line)
    return out


def flat(text):
    t = re.sub(r"\[[^\]]*\]", " ", text)                  # [अँगूठा], [कटा हुआ]
    t = re.sub(r"[|*#_`]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


NUM = re.compile(r"\d[\d,.]*\d|\d")


def numbers(text):
    return Counter(n.replace(",", "") for n in NUM.findall(text) if len(n.replace(",", "")) >= 2)


SUFFIX_KEYS = [key(s) for s in "देवी कुमारी कुमार प्रसाद रानी".split()]


SCRIPT_SEAM = re.compile(r"(?<=[A-Za-z.])(?=[\u0900-\u097F])|(?<=[\u0900-\u097F])(?=[A-Za-z])")


def given_part(surface):
    """First-name key for pairing. OCR glues a role onto a name ("C.Mसीमा देवी"); split at the
    Latin/Devanagari seam and drop role words, so the name itself is compared."""
    toks = [t for t in SCRIPT_SEAM.sub(" ", surface).split() if not role_of(t)] or surface.split()
    keep = [t for t in toks if max(ratio(key(t), s) for s in SUFFIX_KEYS) < 0.6]
    return key("".join(keep or toks))


def main():
    src, label = Path(sys.argv[1]), sys.argv[2]
    split = sys.argv[3] if len(sys.argv) > 3 else "all"              # optional: dev | test | all
    textdir = ROOT / "text" / f"ocr_{label}"
    textdir.mkdir(parents=True, exist_ok=True)
    pages = [r for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))]
    have = [p for p in pages if (src / f"{p['page']}.md").exists() and split in ("all", p["split"])]
    print(f"{label}: {len(have)} of {len(pages)} pages read")

    # 1-3: conversion, CER, numbers
    tot_e = tot_n = 0
    num_hit = num_ref = num_ocr = 0
    per_page = []
    for p in have:
        lines = md_to_lines((src / f"{p['page']}.md").read_text(encoding="utf-8"))
        (textdir / f"{p['page']}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        ref = (ROOT / "text/clean" / f"{p['page']}.txt").read_text(encoding="utf-8")
        a, b = flat(ref), flat("\n".join(lines))
        e = edits(a, b)
        tot_e += e; tot_n += len(a)
        rn, on = numbers(ref), numbers("\n".join(lines))
        hit = sum((rn & on).values())
        num_hit += hit; num_ref += sum(rn.values()); num_ocr += sum(on.values())
        meta = json.loads((src / f"{p['page']}.json").read_text(encoding="utf-8")) if (src / f"{p['page']}.json").exists() else {}
        per_page.append((p["page"], p["kind"], len(a), e / max(len(a), 1), hit, sum(rn.values()),
                         meta.get("sec"), list((meta.get("prep") or {}).get("flags", {}).keys())))

    # 4: names, end to end
    subprocess.run([sys.executable, "-I", str(ROOT / "resolve.py"), "--split", "all", "--text", f"ocr_{label}",
                    "--quiet"], check=True, capture_output=True)
    pred = list(csv.DictReader(open(ROOT / "out" / f"decisions_ocr_{label}_all.csv", encoding="utf-8")))
    gold = [g for g in csv.DictReader(open(ROOT / "gold/gold.csv", encoding="utf-8"))
            if g["category"] == "name" and any(g["page"] == p["page"] for p in have)]
    # Pairing each key mention with an OCR mention on the same page: the first names (given_part) must
    # be close; candidates are ranked by first name and full name together, best matches first (not in key order, so one early mismatch cannot cascade). A key mention on reference
    # row N pairs with an OCR mention on row N; with an OCR mention that is not on a numbered row (or the
    # other way round: OCR merges margin text into rows) only if the names are near-identical (first name >= 0.9, full name >= 0.7).
    # Ties go to the OCR line that holds more of the reference line's words (context), then to position.
    ROWNO = re.compile(r"\s*(\d{1,3})\s*\.?\s*\|")
    DEVDIG = str.maketrans("०१२३४५६७८९", "0123456789")
    text_of = {}
    def place(kind, page, line):
        if (kind, page) not in text_of:
            d = ROOT / "text/clean" if kind == "ref" else textdir
            text_of[(kind, page)] = (d / f"{page}.txt").read_text(encoding="utf-8").splitlines()
        lines = text_of[(kind, page)]
        text = lines[int(line) - 1].translate(DEVDIG)
        m = ROWNO.match(text)
        return (m.group(1) if m else None), int(line) / max(len(lines), 1), set(WORD.findall(text))
    WORD = re.compile(r"[^\s|,।()\[\]:;/=\-–]+")
    cands = []
    for gi, g in enumerate(gold):
        gs, gpos, gw = place("ref", g["page"], g["line"])
        for i, q in enumerate(pred):
            if q["page"] != g["page"] or q["kind"] != "name":
                continue
            qs, qpos, qw = place("ocr", q["page"], q["line"])
            if gs and qs and gs != qs:
                continue
            r = ratio(given_part(q["surface"]), given_part(g["surface"]))
            full = ratio(key(SCRIPT_SEAM.sub(" ", q["surface"])), key(SCRIPT_SEAM.sub(" ", g["surface"])))
            same_kind = (gs is None) == (qs is None)
            if r >= 0.7 if same_kind else (r >= 0.9 and full >= 0.7):
                ctx = len(gw & qw) / max(len(gw), 1)
                cands.append((-(r + full) / 2, -ctx, not same_kind, abs(gpos - qpos), gi, i))
    match, used = {}, set()
    for *_, gi, i in sorted(cands):
        if gi not in match and i not in used:
            match[gi] = i
            used.add(i)
    out, wrong, pairs = Counter(), [], []
    for gi, g in enumerate(gold):
        best = match.get(gi)
        if best is None:
            out["missed (name not read)"] += 1
            pairs.append((g["page"], g["line"], g["surface"], g["expected"], "", "", "", "missed (name not read)"))
            continue
        got, exp = pred[best]["decision"], g["expected"]
        if exp in ("ASK", "NEW"):
            res = "correct no-link" if got in ("ASK", "NEW") else "WRONG: guessed"
        elif got == exp:
            res = "correct link"
        elif got in ("ASK", "NEW"):
            res = "held back (asked / not on roster)"
        else:
            res = "WRONG: linked to another person"
        out[res] += 1
        pairs.append((g["page"], g["line"], g["surface"], exp, pred[best]["line"], pred[best]["surface"], got, res))
        if res.startswith("WRONG"):
            wrong.append((g["page"], g["surface"], exp, pred[best]["surface"], got))
    extra_links = [q for i, q in enumerate(pred) if i not in used and q["decision"] not in ("ASK", "NEW")]
    gold_ids = {}
    for g in gold:
        gold_ids.setdefault(g["page"], set()).add(g["expected"])
    stray = [q for q in extra_links if q["decision"] not in gold_ids.get(q["page"], set())]

    # Link audit, independent of the pairing above.
    # (a) per page, no person may get more links than the key has mentions of her;
    # (b) a link on a numbered table row must name a person the key has on the row with the same number.
    excess = []
    for pg in sorted({q["page"] for q in pred}):
        gc = Counter(g["expected"] for g in gold if g["page"] == pg)
        pc = Counter(q["decision"] for q in pred if q["page"] == pg and q["decision"] not in ("ASK", "NEW"))
        excess += [(pg, i, c, gc.get(i, 0)) for i, c in pc.items() if c > gc.get(i, 0)]
    row_ok, row_bad = 0, []
    for q in pred:
        if q["decision"] in ("ASK", "NEW"):
            continue
        ocr_line = (textdir / f"{q['page']}.txt").read_text(encoding="utf-8").splitlines()[int(q["line"]) - 1]
        m = re.match(r"\s*(\d{1,3})\s*\.?\s*\|", ocr_line.translate(str.maketrans("०१२३४५६७८९", "0123456789")))
        if not m:
            continue
        ref = (ROOT / "text/clean" / f"{q['page']}.txt").read_text(encoding="utf-8").splitlines()
        rows = {i + 1 for i, l in enumerate(ref) if re.match(rf"\s*{m.group(1)}\s*\.?\s*\|", l)}
        ids = {g["expected"] for g in gold if g["page"] == q["page"] and int(g["line"]) in rows}
        if q["decision"] in ids:
            row_ok += 1
        else:
            row_bad.append((q["page"], m.group(1), q["surface"], q["decision"], sorted(ids)))

    n = len(gold)
    report = [f"# OCR run: {label}", "",
              f"Pages read: {len(have)} of {len(pages)}", "",
              "## Text quality (against Claude's reference readings)", "",
              f"- Character error rate: **{100 * tot_e / max(tot_n, 1):.1f}%** "
              f"({tot_e} edits over {tot_n} reference characters)",
              f"- Numbers (2+ digits) found: **{num_hit} of {num_ref}** ({100 * num_hit / max(num_ref, 1):.0f}%); "
              f"the OCR produced {num_ocr} numbers in all", "",
              "## Names, end to end (OCR → resolver → answer key)", "",
              "| Outcome | Count | Share |", "|---|---|---|"]
    for r in ["correct link", "correct no-link", "held back (asked / not on roster)", "missed (name not read)",
              "WRONG: linked to another person", "WRONG: guessed"]:
        report.append(f"| {r} | {out[r]} | {100 * out[r] / max(n, 1):.1f}% |")
    n_links = sum(1 for q in pred if q["decision"] not in ("ASK", "NEW"))
    report += ["", f"Name mentions in the key for these pages: {n}",
               f"Links to people who are not on that page at all (stray): {len(stray)}", "",
               "## Link audit (independent of the pairing)", "",
               f"- Links made: {n_links}",
               f"- Person linked more often on a page than the key has her: "
               f"**{sum(c - k for _, _, c, k in excess)}** extra link(s)",
               f"- Links on numbered table rows: {row_ok + len(row_bad)}; naming someone the key does not have "
               f"on that row: **{len(row_bad)}**", ""]
    report += [f"  - {pg}: {i} linked {c} times, key has {k}" for pg, i, c, k in excess]
    report += [f"  - {pg} row {r}: `{s}` → {d}; key on that row {ids}" for pg, r, s, d, ids in row_bad]
    if excess or row_bad:
        report.append("")
    if wrong or stray:
        report.append("### Every wrong or stray link")
        report += [f"- {w[0]}: key `{w[1]}` = {w[2]}; OCR `{w[3]}` → {w[4]}" for w in wrong]
        report += [f"- {q['page']} line {q['line']}: OCR `{q['surface']}` → {q['decision']} (stray)" for q in stray]
        report.append("")
    report += ["## Per page", "", "| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |",
               "|---|---|---|---|---|---|---|"]
    for pg, kind, nchar, cer, hit, tot, sec, flags in per_page:
        report.append(f"| {pg} | {kind} | {nchar} | {100 * cer:.0f}% | {hit}/{tot} | {sec or ''} | {', '.join(flags)} |")
    with open(ROOT / "out" / f"ocr_pairs_{label}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["page", "key_line", "key_surface", "expected", "ocr_line", "ocr_surface", "decision", "outcome"])
        w.writerows(pairs)
    dest = ROOT / "out" / f"ocr_report_{label}.md"
    dest.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[:30]))
    print(f"\n-> {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
