#!/usr/bin/env python3
"""Rule-based name resolution for SHG and CLF registers. No model, standard library only.

Given the text of a register page and the roster of the book it belongs to, find every
person mentioned and decide one of three things:
    <roster id>  the person is identified;
    ASK          the text cannot safely separate two or more people, or the evidence
                 contradicts the only match, so a person must confirm;
    NEW          a person who is not on the roster.

The decision uses only what is written on the page: spelling-tolerant name matching,
plus anchors on the same row or next to the name (role, village, MIS ID, loan repayment).

Usage:
    python resolve.py                      # dev pages, reference text, print a trace
    python resolve.py --split test
    python resolve.py --text ocr_qwen3vl   # run on another transcription folder
    python resolve.py --line "BK सुनिता कुमारी को भाड़ा 300/- दिया गया" --book EKTA_CLF
"""
import argparse, csv, re, sys, time, unicodedata
from pathlib import Path

ROOT = Path(__file__).parent

# ---------- 1. A phonetic key that puts Devanagari and Latin spellings in one space ----------
CONS = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
                "k kh g gh n c ch j jh n t th d dh n t th d dh n p ph b bh m y r l v sh sh s h".split()))
VOWELS = dict(zip("अआइईउऊएऐओऔऋ", "a a i i u u e ai o au ri".split()))
MATRAS = dict(zip("ािीुूेैोौृ", "a i i u u e ai o au ri".split()))
VIRAMA, NUKTA = "्", "़"


def translit(word):
    """Devanagari -> rough Latin. Latin input passes through lower-cased."""
    w = unicodedata.normalize("NFC", word).replace(NUKTA, "")
    w = unicodedata.normalize("NFD", w).replace(NUKTA, "")   # ड़ decomposes to ड + nukta
    out, i = [], 0
    while i < len(w):
        ch = w[i]
        nxt = w[i + 1] if i + 1 < len(w) else ""
        if ch in CONS:
            out.append(CONS[ch])
            if nxt in MATRAS:
                out.append(MATRAS[nxt]); i += 1
            elif nxt == VIRAMA:
                i += 1
            else:
                out.append("a")                               # inherent vowel
        elif ch in VOWELS:
            out.append(VOWELS[ch])
        elif ch in "ंँ":
            out.append("n")
        elif ch.isascii() and ch.isalpha():
            out.append(ch.lower())
        i += 1
    return "".join(out)


def key(text):
    """Collapse spelling variation that writers and OCR produce for the same name."""
    s = translit(text)
    s = s.replace("ee", "i").replace("oo", "u").replace("aa", "a").replace("ph", "f")
    prev = None
    while prev != s:                                          # drop aspiration: sh->s, bh->b, ...
        prev, s = s, re.sub(r"([kgcjtdpbsf])h", r"\1", s)
    s = s.replace("w", "b").replace("v", "b").replace("z", "j").replace("q", "k")
    s = re.sub(r"(.)\1+", r"\1", s)                           # doubled letters
    if len(s) > 2 and s.endswith("a"):                        # final schwa: Sushila/सुशील
        s = s[:-1]
    return s


def ratio(a, b):
    """1 - normalised Levenshtein distance."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return 1 - prev[-1] / max(len(a), len(b))


# ---------- 2. Vocabulary: small word lists, the only part that changes per language ----------
SUFFIXES = {key(w) for w in "देवी कुमारी कुमार प्रसाद रानी devi kumari kumar prasad rani".split()}
ABBREV = {"कु०": {key("कुमारी"), key("कुमार")}, "कु.": {key("कुमारी"), key("कुमार")},
          "प्र०": {key("प्रसाद")}, "प्र.": {key("प्रसाद")}}
OFFICE_ROLES = {"अध्यक्ष", "उपाध्यक्ष", "सचिव", "उपसचिव", "कोषाध्यक्ष", "सदस्य"}
CADRE_ROLES = {"BK", "MBK", "CF", "BM", "CNRP", "JCRP", "VRP", "SEW", "SJYMRP", "FICRP", "CM"}
ROLE_PAIRS = {("उप", "सचिव"): "उपसचिव", ("उप", "अध्यक्ष"): "उपाध्यक्ष", ("SJY", "MRP"): "SJYMRP",
              ("FI", "CRP"): "FICRP", ("HNS", "CNRP"): "CNRP"}
# Words that are also given names. On their own they are not treated as a name;
# with a surname they are.  (आरती = a ritual, पूजा = worship, सीमा = limit, ...)
COMMON = {key(w) for w in "पूजा आरती गीता कंचन मिनी सीमा रश्मि प्रतिमा संगीता अशोक आशा किरण "
          "सुमन ममता शांति लक्ष्मी ज्योति पुष्पा रेखा सोनी श्रीमती".split()}
STOP = {key(w) for w in "सभी दीदी जो हम की का के को ने से में और बैंक समूह कुल आज श्री "
        "BOD SHG CLF VO OB P".split()}
HONORIFIC_AFTER_ROLE = {"दीदी", "जी"}

TOKEN_RE = re.compile(r"[^\s|,।()\[\]:;/=\-–]+")


def role_of(tok):
    t = tok.replace(".", "").replace("-", "")
    if t.upper() in CADRE_ROLES:
        return t.upper()
    return t if t in OFFICE_ROLES else None


# ---------- 3. Roster ----------
def load_roster(book):
    people = []
    with open(ROOT / "roster/roster.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["book"] != book:
                continue
            toks = r["name"].split()
            r["given_key"] = key("".join(toks[:-1]) if len(toks) > 1 else toks[0])
            r["sur_key"] = key(toks[-1]) if len(toks) > 1 else None
            r["village_key"] = key(r["village"]) if r["village"] else None
            people.append(r)
    return people


def name_tier(span, person):
    """How well a 1-3 token span matches a roster name. 3 exact, 2 strong,
    1 first-name only, 0.5 needs corroboration, 0 no match."""
    if len(span) == 1:
        g, s = key(span[0]), None
    else:
        g, s = key("".join(span[:-1])), span[-1]
    r = ratio(g, person["given_key"])
    if s is None:
        if person["sur_key"] is None:
            return 3 if r == 1 else 2 if r >= 0.8 else 0
        if r == 1 and len(g) >= 3 and g not in COMMON:
            return 1
        return 0
    if person["sur_key"] is None:
        return 0
    if s in ABBREV:
        sur_ok, sur_exact = person["sur_key"] in ABBREV[s], True
    else:
        sr = ratio(key(s), person["sur_key"])
        sur_ok, sur_exact = sr >= 0.8, sr == 1
    if sur_ok and r == 1 and sur_exact:
        return 3
    if sur_ok and r >= 0.8:
        return 2
    if (r == 1 and not sur_ok) or (sur_ok and r >= 0.6):
        return 0.5
    return 0


# ---------- 4. Find mentions in one cell or free-text line ----------
def find_mentions(tokens, roster):
    """Greedy, longest span first. Returns (start, end, candidates, kind)."""
    found, used = [], set()
    for length in (3, 2, 1):
        for i in range(len(tokens) - length + 1):
            span = tokens[i:i + length]
            if used & set(range(i, i + length)):
                continue
            keys = [key(t) for t in span]
            if (any(role_of(t) or not key(t) or key(t) in STOP or t.isdigit() for t in span)
                    or keys[0] in SUFFIXES):
                continue
            cands = [(p, t) for p in roster if (t := name_tier(span, p)) > 0]
            looks_like_person = length == 2 and keys[1] in SUFFIXES
            if cands or looks_like_person:
                found.append((i, i + length, cands, "name"))
                used |= set(range(i, i + length))
    # Role-only references: "CM दीदी", "CM के पास"
    for i, t in enumerate(tokens):
        r = role_of(t)
        if r in CADRE_ROLES and i not in used:
            after = tokens[i + 1:i + 3]
            if after[:1] and (after[0] in HONORIFIC_AFTER_ROLE or after == ["के", "पास"]):
                near = any(abs(m[0] - i) <= 1 or abs(m[1] - 1 - i) <= 1 for m in found)
                if not near:
                    found.append((i, i + 1, [(p, 1) for p in roster if p["role"] == r], "role_only"))
    return sorted(found)


def roles_in(tokens):
    """(first, last, role) for role words, joining two-word roles such as SJY MRP, उप सचिव."""
    out, i = [], 0
    while i < len(tokens):
        pair = tuple(t.replace(".", "") for t in tokens[i:i + 2])
        if len(pair) == 2 and (pair in ROLE_PAIRS or (pair[0].upper(), pair[1].upper()) in ROLE_PAIRS):
            out.append((i, i + 1, ROLE_PAIRS.get(pair) or ROLE_PAIRS[(pair[0].upper(), pair[1].upper())]))
            i += 2
            continue
        r = role_of(tokens[i])
        if r:
            out.append((i, i, r))
        i += 1
    return out


def attach_roles(mentions, role_pos):
    """Free text: a role word belongs to the name right before or right after it.
    "सीमा देवी CNRP" vs "CM बबीता देवी". When it sits between two names
    ("स्वीटी कुमारी CM बबीता देवी"), give it to the side that has a holder of that role;
    otherwise to the name before it (the usual signature convention)."""
    attached = {i: [] for i in range(len(mentions))}
    for first, last, role in role_pos:
        before = next((i for i, m in enumerate(mentions) if m[1] == first), None)
        after = next((i for i, m in enumerate(mentions) if m[0] == last + 1), None)
        holds = lambda i: i is not None and any(p["role"] == role for p, _ in mentions[i][2])
        if before is not None and after is not None:
            target = after if holds(after) and not holds(before) else before
        else:
            target = before if before is not None else after
        if target is not None:
            attached[target].append(role)
    return attached


# ---------- 5. Score candidates with anchors, then decide ----------
def decide(cands, anchors):
    viable, notes, contradicted = [], [], []
    for p, tier in cands:
        score, why = 0, []
        if anchors.get("mis"):
            if p["mis_id"] and p["mis_id"] in anchors["mis"]:
                score += 10; why.append("MIS ID matches")
            elif p["mis_id"]:
                score -= 10; why.append("MIS ID differs")
        hard = False
        for r in anchors.get("roles", []):
            if r == p["role"]:
                score += 3; why.append(f"role {r}")
            elif r in CADRE_ROLES or p["role"] in CADRE_ROLES and r not in OFFICE_ROLES:
                hard = True; why.append(f"role {r} contradicts {p['role']}")
            else:
                score -= 3; why.append(f"office {r} vs {p['role']}")
        for v in anchors.get("villages", []):
            if p["village_key"] and ratio(v, p["village_key"]) >= 0.8:
                score += 3; why.append("village matches")
            elif p["village_key"]:
                score -= 3; why.append("other village")
        if anchors.get("loan"):
            if p["has_loan"] == "yes":
                score += 3; why.append("repaid a loan; has one")
            elif p["has_loan"] == "no":
                score -= 3; why.append("repaid a loan; has none")
        entry = (p, tier, score, why)
        if hard:
            contradicted.append(entry)
        elif tier >= 1 or score >= 3:
            viable.append(entry)
        notes.append(f"{p['id']}(tier {tier}, {score:+d}: {', '.join(why) or 'no anchors'})")
    if not viable:
        if contradicted and max(t for _, t, _, _ in contradicted) >= 1:
            return "ASK", notes, "name matches but the written role contradicts the roster"
        return "NEW", notes, "not on roster" + (" (nearest is too weak)" if cands else "")
    viable.sort(key=lambda e: (e[2], e[1]), reverse=True)
    if len(viable) == 1:
        return viable[0][0]["id"], notes, "only plausible match"
    if viable[0][2] - viable[1][2] >= 3:
        return viable[0][0]["id"], notes, "anchors separate the candidates"
    return "ASK", notes, "same name; nothing on the page separates them"


def header_repayment_cols(cells):
    return [i for i, c in enumerate(cells) if "वपासी" in c or "वापसी" in c]


def resolve_page(lines, roster, villages):
    results, repay_cols = [], []
    for lno, line in enumerate(lines, 1):
        is_table = "|" in line
        cells = [c.strip() for c in line.split("|")] if is_table else [line]
        if is_table and any("नाम" in c for c in cells):
            repay_cols = header_repayment_cols(cells)
            continue
        is_row = is_table and cells[0].isdigit()
        row_anchors = {}
        if is_row:
            toks_all = [t for c in cells for t in TOKEN_RE.findall(c)]
            row_anchors = {
                "roles": sorted({r for _, _, r in roles_in(toks_all)}),
                "villages": [vk for t in toks_all for vk in villages if ratio(key(t), vk) >= 0.8],
                "mis": {t for t in toks_all if re.fullmatch(r"\d{10}", t)},
                "loan": any(i < len(cells) and re.fullmatch(r"\d+", cells[i] or "") and int(cells[i]) > 0
                            for i in repay_cols)}
        for ci, cell in enumerate(cells):
            toks = TOKEN_RE.findall(cell)
            mentions = find_mentions(toks, roster)
            attached = attach_roles(mentions, roles_in(toks))
            for mi, (s, e, cands, kind) in enumerate(mentions):
                if is_row:
                    anchors = row_anchors
                else:                                   # free text: only what is next to the name
                    anchors = {"roles": attached[mi]}
                    if len([m for m in mentions if m[3] == "name"]) == 1:
                        anchors["mis"] = {t for t in toks if re.fullmatch(r"\d{10}", t)}
                if kind == "role_only":
                    ids = [p["id"] for p, _ in cands]
                    dec = ids[0] if len(ids) == 1 else "ASK"
                    notes, why = ids, "referred to by role; one holder" if len(ids) == 1 else "role has several holders"
                else:
                    dec, notes, why = decide(cands, anchors)
                results.append({"line": lno, "cell": ci, "surface": " ".join(toks[s:e]),
                                "decision": dec, "kind": kind, "why": why, "candidates": notes,
                                "cand_ids": [p["id"] for p, _ in cands],
                                "is_row": is_row, "name_cell": is_row and ci == 1})
    confirm_by_signature(results)
    eliminate(results)
    return results


def confirm_by_signature(results):
    """In a table row the name column and the signature column normally name the same
    person. If one is unresolved but resembles the person the other identifies, adopt it.
    ("अमिता कुमारी" in the name column, "अनीता कुमारी" signed in the same row.)
    Rows where the two columns name different people (गीता / सुषमा) do not overlap,
    so nothing is adopted there."""
    rows = {}
    for r in results:
        if r["is_row"] and r["kind"] == "name":
            rows.setdefault(r["line"], []).append(r)
    for rs in rows.values():
        known = {r["decision"] for r in rs if r["decision"] not in ("ASK", "NEW")}
        for r in rs:
            if r["decision"] in ("ASK", "NEW"):
                hit = known & set(r["cand_ids"])
                if len(hit) == 1:
                    r["decision"], r["why"] = hit.pop(), "confirmed by the other column in the same row"


def eliminate(results):
    """One row per member in an attendance table: if two Sushmas have two rows and one
    row is identified, the other row is the other Sushma."""
    groups = {}
    for r in results:
        if r["name_cell"] and r["kind"] == "name":
            ids = frozenset(c.split("(")[0] for c in r["candidates"]
                            if "tier 3" in c or "tier 2" in c)
            if len(ids) > 1:
                groups.setdefault(ids, []).append(r)
    for ids, rows in groups.items():
        if len(rows) != len(ids):
            continue
        done = {r["decision"] for r in rows if r["decision"] in ids}
        open_rows = [r for r in rows if r["decision"] == "ASK"]
        if len(done) == len(ids) - 1 and len(open_rows) == 1:
            r = open_rows[0]
            r["decision"], r["why"] = next(iter(ids - done)), "the other same-name row is identified"
            for sig in results:                            # signature in the same row, same name
                if (sig["line"] == r["line"] and not sig["name_cell"] and sig["decision"] == "ASK"
                        and key(sig["surface"]) == key(r["surface"])):
                    sig["decision"], sig["why"] = r["decision"], "same row as its name cell"


def name_signature_mismatches(results):
    rows = {}
    for r in results:
        if r["is_row"]:
            rows.setdefault(r["line"], []).append(r)
    flags = []
    for lno, rs in rows.items():
        name = [r for r in rs if r["name_cell"]]
        sigs = [r for r in rs if not r["name_cell"] and r["cell"] == max(x["cell"] for x in rs)]
        if name and sigs and all(ratio(key(s["surface"]), key(name[0]["surface"])) < 0.8 for s in sigs):
            flags.append((lno, name[0]["surface"], " / ".join(s["surface"] for s in sigs)))
    return flags


# ---------- 6. CLI ----------
def pages(split):
    with open(ROOT / "pages.csv", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if split == "all" or r["split"] == split]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev", choices=["dev", "test", "all"])
    ap.add_argument("--text", default="clean")
    ap.add_argument("--line")
    ap.add_argument("--book", default="EKTA_CLF")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.line:
        roster = load_roster(a.book)
        vil = {p["village_key"] for p in roster if p["village_key"]}
        for r in resolve_page([a.line], roster, vil):
            print(f"{r['surface']:<22} -> {r['decision']:<4} {r['why']}\n    {'; '.join(map(str, r['candidates']))}")
        return

    out_rows, t0, n_lines = [], time.perf_counter(), 0
    for pg in pages(a.split):
        src = ROOT / "text" / a.text / f"{pg['page']}.txt"
        if not src.exists():
            print(f"[skip] {src} missing", file=sys.stderr)
            continue
        roster = load_roster(pg["book"])
        vil = {p["village_key"] for p in roster if p["village_key"]}
        lines = src.read_text(encoding="utf-8").splitlines()
        n_lines += len(lines)
        res = resolve_page(lines, roster, vil)
        for r in res:
            out_rows.append({"page": pg["page"], **{k: r[k] for k in ("line", "surface", "decision", "kind", "why")},
                             "candidates": " | ".join(map(str, r["candidates"]))})
        if not a.quiet:
            print(f"\n=== {pg['page']} ({pg['book']}, {pg['description']})")
            for r in res:
                print(f"  L{r['line']:<3} {r['surface']:<22} -> {r['decision']:<4} {r['why']}")
            for lno, n, s in name_signature_mismatches(res):
                print(f"  ! L{lno}: name column says {n!r}, signature column says {s!r}")
    secs = time.perf_counter() - t0
    dest = ROOT / "out" / f"decisions_{a.text}_{a.split}.csv"
    dest.parent.mkdir(exist_ok=True)
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["page", "line", "surface", "decision", "kind", "why", "candidates"])
        w.writeheader(); w.writerows(out_rows)
    print(f"\n{len(out_rows)} mentions on {n_lines} lines in {secs * 1000:.0f} ms -> {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
