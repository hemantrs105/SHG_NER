#!/usr/bin/env python3
"""Walk through the hard cases on the real Nalanda register pages, one at a time.

    python demo.py            # real names: for your own screen only
    python demo.py --pseudo   # names, villages and MIS IDs replaced: safe to screenshot
    python demo.py --step     # pause after each case (press Enter)
"""
import argparse, csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from resolve import TOKEN_RE, key, load_roster, name_signature_mismatches, resolve_page

CASES = [
    ("IMG_0210", [14, 15], "Two members called सुषमा कुमारी. Only one repaid a loan this week, "
                           "so the row with repayments is hers; the other row is the other Sushma."),
    ("IMG_0212", [13, 15], "Two members called गुड़िया कुमारी and nothing on the page separates them. "
                           "It asks instead of guessing."),
    ("IMG_0096", [9, 16], "Two पिंकी देवी on the CLF board. The village column separates them."),
    ("IMG_0096", [10], "सुनिता कुमारी the board member..."),
    ("IMG_0164", [4], "...and सुनिता कुमारी the bookkeeper (BK). Same name, the role word decides."),
    ("IMG_0118", [17], "The name matches a CNRP on the roster, but the page labels her C.M. "
                       "Contradiction, so it asks."),
    ("IMG_0104", [7], "The cleaner is not on the roster. One letter from VRP रिता देवी, "
                      "too far to link: reported as not on roster."),
    ("IMG_0139", [16], "Written नरेन्द्र कुमार here, नरेन्द्र प्रसाद in the MIS table. "
                       "The surname disagrees; the role SJY-MRP confirms him."),
    ("IMG_0096", [19], "Latin-script signatures: Sushil Rajan = सुशील रंजन."),
    ("IMG_0210", [12], "Name column अमिता, signature अनीता in the same row: the signature confirms."),
    ("IMG_0207", [10], "A role between two names ('… स्वीटी कुमारी CM बबीता देवी'): CM goes to the "
                       "side that has a CM."),
    ("IMG_0215", [2], "No name at all: 'CM दीदी'. The group has one CM."),
    ("IMG_0210", [6], "Check, not a name: the signature column is out of line with the name column."),
]

FEMALE = ("अंजलि बीना चंदा दुर्गा एकता फूलमती गौरी हेमा इंदु जया कमला लता माधुरी नीलम ऊषा पार्वती "
          "राधा सरला तारा उर्मिला वंदना यमुना अर्चना भारती चमेली दीपा गंगा हीरा जानकी मालती "
          "ललिता मंजू निर्मला प्रभा रजनी शकुन सविता तुलसी विजया शारदा").split()
MALE = "अमर भोला चेतन देवेश गोपाल हरिश जगदीश कमल मोहन नवीन ओमप्रकाश पंकज राजेश संजय".split()
LATIN = dict(zip(FEMALE + MALE + ["सिंह"],
                 ("Anjali Beena Chanda Durga Ekta Phoolmati Gauri Hema Indu Jaya Kamla Lata Madhuri Neelam "
                  "Usha Parvati Radha Sarla Tara Urmila Vandana Yamuna Archana Bharati Chameli Deepa Ganga "
                  "Heera Janki Malti Lalita Manju Nirmala Prabha Rajni Shakun Savita Tulsi Vijaya Sharda "
                  "Amar Bhola Chetan Devesh Gopal Harish Jagdish Kamal Mohan Naveen Omprakash Pankaj "
                  "Rajesh Sanjay Singh").split()))
GENERIC = {key(s) for s in "देवी कुमारी कुमार प्रसाद रानी".split()}


def pseudonymiser():
    """Swap people's names, villages and MIS IDs for stand-ins, keeping same-name
    pairs as pairs and women's names as women's names."""
    names, villages = {}, {}

    def add(given, female):
        k = key(given)
        if k not in names:
            pool = FEMALE if female else MALE
            used = sum(1 for v in names.values() if v in pool)
            names[k] = pool[used % len(pool)]
    with open(ROOT / "roster/roster.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            toks = r["name"].split()
            female = toks[-1] in ("देवी", "कुमारी")
            add("".join(toks[:-1]) if len(toks) > 1 else toks[0], female)
            if len(toks) > 1 and key(toks[-1]) not in GENERIC:
                names.setdefault(key(toks[-1]), "सिंह")         # surnames such as रंजन
            if r["village"]:
                villages.setdefault(key(r["village"]), f"गाँव-{len(villages) + 1}")
    for w in ["रीना", "बबिता", "रेखा", "Sandhya"]:                # people not on the roster
        add(w, True)
    names[key("अमिता")] = names[key("अनीता")][:-1] + "ी"         # writer's variant stays a variant

    def nearest(k, table):
        from resolve import ratio
        best = max(table, key=lambda t: ratio(k, t))
        return table[best] if ratio(k, best) >= 0.8 else None

    def sub(text):
        out = text
        for tok in sorted(set(TOKEN_RE.findall(text)), key=len, reverse=True):
            k = key(tok)
            if tok.isdigit() and len(tok) == 10:
                out = out.replace(tok, "10XXXXXXXX")
            elif len(k) < 3 or k in GENERIC or tok.isascii() and tok.isupper():
                continue
            elif (v := nearest(k, villages)):
                out = out.replace(tok, v)
            elif (n := nearest(k, names)):
                out = out.replace(tok, LATIN.get(n, n) if tok.isascii() else n)
        return out
    return sub


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pseudo", action="store_true")
    ap.add_argument("--step", action="store_true")
    a = ap.parse_args()
    show = pseudonymiser() if a.pseudo else (lambda s: s)
    books = {r["page"]: r["book"] for r in csv.DictReader(open(ROOT / "pages.csv", encoding="utf-8"))}
    for n, (page, lnos, story) in enumerate(CASES, 1):
        roster = load_roster(books[page])
        vil = {p["village_key"] for p in roster if p["village_key"]}
        lines = (ROOT / "text/clean" / f"{page}.txt").read_text(encoding="utf-8").splitlines()
        res = resolve_page(lines, roster, vil)
        by_id = {p["id"]: p for p in roster}
        print(f"\n── {n}. {show(story)}")
        for lno in lnos:
            print(f"   {page} line {lno}:  {show(lines[lno - 1])}")
            for r in (x for x in res if x["line"] == lno):
                d = r["decision"]
                who = by_id.get(d)
                detail = f"{d} = {show(who['name'])}, {who['role']}" + (
                    f", {show(who['village'])}" if who and who["village"] else "") if who else d
                print(f"      {show(r['surface']):<20} → {detail:<34} {r['why']}")
        for lno, name, sig in name_signature_mismatches(res):
            if lno in lnos:
                print(f"      ! name column {show(name)!r}, signature column {show(sig)!r}: flag for review")
        if a.step:
            input("   [Enter] ")
    print("\nScores: python score.py --split test    (frozen v1 result: out/score_test_v1_frozen.txt)")


if __name__ == "__main__":
    main()
