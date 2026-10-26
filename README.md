# Name resolution on SHG and CLF registers: a rule-based demo

**Question (23 Oct 2026):** given a fixed list of people (the SHG or CLF roster), how small can the thing be that decides *who* a name on a register refers to, including two members with the same name, without training a model for every language?

**Answer from this demo:** For written registers and transcripts from the SHG meetings, the decision step needs no model. 22 KB of standard-library Python handles it, plus a few short word lists. On real pages from Nalanda it made **no wrong links**. When the page cannot separate two people, it asks a person instead of guessing (OR a small NER query can be done to the LokOS database and link can be made with relevant consent). 

> **This folder contains real names from field photos** (Vidya Jeevika SHG, Harvanshpur, and Ekta Jeevika CLF, Islampur block).
> For screenshots or the WhatsApp group, use `python demo.py --pseudo`, which swaps names, villages and MIS IDs for stand-ins (available in a public repo).

---

## Results

### The data

- 19 photographed pages from the 29 Sep 2026 visit.
- 10 pages from one SHG register: 5 attendance-and-savings tables and 5 sets of minutes.
- 9 pages from one CLF minute book: board attendance, cadre honorarium tables with MIS IDs, and payment notes.
- 342 person mentions in total.

| | Dev pages (rules built here) | Test pages (held out) |
|---|---|---|
| Pages | 8 | 11 |
| Name mentions | 132 | 208 |
| ...that can be linked to one person | 120 | 180 |
| ...where the right answer is "ask" (same name, nothing separates them; or role contradicts) | 12 | 24 |
| ...people not on the roster | 0 | 4 |

### Headline: one run on the held-out test pages, rules frozen beforehand

| Outcome | Count |
|---|---|
| Correct (linked to the right person, or correctly asked / flagged as not on roster) | **207 of 208** |
| Linked to the wrong person | **0** |
| Guessed when it should have asked | **0** |
| On the roster but reported "not on roster" | 1 |
| Spurious mention (a non-name read as a name) | 1 (`11 बजे देवी स्थान` → "बजे देवी") |

The frozen rules are `resolve_v1_frozen.py` (SHA-256 in
`gold/RULES_FROZEN_BEFORE_TEST.sha256`). The run is saved in `out/score_test_v1_frozen.txt`.

That file shows 0/1 role-only references and 2 spurious mentions. One of those
"spurious" mentions is the role-only reference itself. The resolver linked "CM" in
"CM दीदी" correctly to the group's CM, but reported the span as "CM" while the answer
key said "CM दीदी", so the scorer missed the match. The scorer was fixed afterwards.

### After fixing what the test run found (v2, `resolve.py`)

Three defects were fixed. Each is marked `v2` in the code:

- The second half of a two-word role ("FI **CRP**") was read as part of a name.
- "बजे" (o'clock) was read as a name.
- When spans overlapped, the longer one beat the better one.

A fourth defect was found by the noise test below. Elimination could assign a person
the row itself argued against.

| | Dev | Test |
|---|---|---|
| Correct | 132 / 132 | 208 / 208 |
| Wrong links | 0 | 0 |

**The v2 test score is not an unbiased estimate**, because the fixes were made after
seeing the test errors. Quote the v1 headline.

One more rule was added after the BODHAN OCR run below (v3, marked in the code): a line identical
to the line next to it is an OCR loop, so its names are ASK. The reference readings never repeat a
line, so the scores above are unchanged.

### On-device OCR: BODHAN IndicOCR, with and without Bhavish's harness

Full write-up: **[OCR_BODHAN.md](OCR_BODHAN.md)**. Built with IndicOCR from Bodhan AI / AI4Bharat.

The same 19 photos were read by `bodhan-ai/indic-ocr` (0.8B recognizer, not quantized, run in
float32 on the Mac GPU), then passed through the resolver and scored against the same answer key.

| | Claude's reading | BODHAN + harness | BODHAN alone |
|---|---|---|---|
| Character error rate (against Claude's reading) | 0% | 25.8% | 26.2% |
| Numbers found | 558 / 558 | 513 / 558 | 513 / 558 |
| Names linked to the right person | 300 | 184 | 184 |
| Correctly not linked (ASK / NEW) | 40 | 35 | 35 |
| Held back though a link was possible | 0 | 40 | 40 |
| Name not read | 0 | 81 | 81 |
| **Linked to the wrong person** | **0** | **0** (1 before v3) | **0** (1 before v3) |

- **The harness does not change any name decision or number** on these pages. It cleans up LaTeX
  formatting and changes a few words in non-name lines.
- **Speed:** 96 minutes for one page on the CPU (float32); 68 seconds on the Mac GPU with identical
  output; 23 seconds a page over the full run.
- **Where it loses names:** cadre signature blocks and Latin-script signatures; garbled printed
  column headers, which remove the repayment and role clues, so same-name members are held back
  (safe, but not resolved).
- **The serious risk:** BODHAN reads a crossed-out amount as a plain number. If the resolver were
  told the column layout, a cancelled repayment on IMG_0208 would link both Sushmas the wrong way.

### Stress test: does it fail safe on noisy text? (`stress.py`, synthetic)

The test corrupts the reference text with typical Devanagari OCR and handwriting
confusions (ि/ी, ु/ू, ब/व, श/स/ष, न/ण, dropped ा or ं, dropped letters), with
5 random seeds per level. It covers all 340 name mentions.

| Character noise | Correct (mean) | Asked / not-on-roster / missed (mean) | Wrong links (all runs) |
|---|---|---|---|
| 0% | 340 | 0 | 0 |
| 5% | 319 | 21 | 0 |
| 10% | 299 | 41 | 0 |
| 20% | 269 | 71 | 0 |
| 30% | 235 | 105 | 0 |

Before the elimination fix there was **one** wrong link in 25 runs; after it, none.
The scorer pairs each answer-key name with the resolver's output by first name only,
ignoring देवी/कुमारी, so "बीना कुमारी" is never credited or blamed for "चंदा कुमारी".
An earlier version of the scorer was looser, and reported higher "correct" counts.
As text gets worse the resolver finds fewer people, but it does not start naming the
wrong ones. This noise is synthetic. Real OCR errors on these pages may differ.

### Footprint

| | |
|---|---|
| Code | `resolve.py`, 22 KB, Python standard library only, no model, no download |
| Roster | 5 KB CSV |
| Speed | about 2.6 ms per line (all 19 pages in 0.8 s, including Python start-up) |
| Memory | 20 MB peak (the Python interpreter) |
| Per-language work | about 100 words: surname/suffix words, role words, and common words that are also names |

---

## How it works

**[RULEBOOK.md](RULEBOOK.md) has every rule, step by step, in plain language.** It is
enough to rebuild the resolver without reading the code. The summary:

1. **One spelling key for every way a name gets written.** Devanagari and Latin are
   both reduced to the same rough sound key. पीणा/पिना/पीना, सोनि/सोनी,
   सुनिता/सुनीता, "Sushil Rajan"/सुशील रंजन and "Diksha"/दीक्षा all collide on
   purpose. Names are then compared with a spelling-distance score.
2. **Find mentions.** Spans of one to three words are checked against the roster. Two
   words ending in देवी/कुमारी/कुमार/प्रसाद/रानी are treated as a person even if they
   are not on the roster, so the resolver can say NEW.
3. **Anchors on the same row, or right next to the name:**
   - **Role:** BK, CNRP, VRP, CM, सचिव, ... A cadre role that contradicts the roster blocks a link.
   - **Village.**
   - **MIS ID.**
   - **Loan:** a repayment in the मु० वापसी/ब्याज वापसी columns means the member has a loan.
4. **Decide.**
   - Exactly one plausible person: link.
   - Several, and the anchors separate them: link.
   - Otherwise: **ASK**.
   - Nobody close enough: **NEW**.
5. **Use the table's structure:**
   - Each member appears once per attendance table. If one of two Sushmas is identified, the other row is the other Sushma.
   - The name column and the signature column confirm each other.
   - Rows where they name different people are flagged.

---

## What the pages themselves show (worth more than the score)

1. **Same names are normal, not an edge case.**
   - The 14-member SHG has two सुषमा कुमारी and two गुड़िया कुमारी.
   - The 12-member CLF board has two पिंकी देवी.
   - सुनिता कुमारी is both a board member and the bookkeeper.
   - सुनैना देवी is both a board member and a VRP.
   - Name matching alone cannot post entries to LokOS.
2. **The SHG register carries nothing that separates same-name members**: no member
   code, no husband's name. Only the loan trail separated the two Sushmas, and only in
   weeks when one of them repaid. The two Gudiyas were never separable.
   **Recommendation:** have the LokOS member code (or husband's name) written on the
   register, or spoken in the voice read-back. With it, resolution becomes a lookup.
3. **The signature column drifts from the name column.** On 2 of the 5 attendance
   pages, row 4 says गीता देवी while the signature beside it is सुषमा कुमारी. A third
   page shows a correction. A row check catches this for free.
4. **The meeting chair rotates.** "आज की कार्यवाही अध्यक्ष X" names the chair for the
   day, not the group's अध्यक्ष. Role words in minutes cannot all be read as offices.
5. **The same person is written differently on different pages.** नरेन्द्र is
   प्रसाद in the MIS table and कुमार elsewhere. Board names are written two or three
   ways (सुनपना/सुनयना, बंसती/बसंती). Some signatures are in Latin script.

---

## Limits: say these when showing it

- **The text was read by Claude, not by an on-device OCR model.** The reference
  readings in `text/clean/` are Claude's readings of the photos. Spot-check them
  against `pages/`. This demo tests the *decision* step only.
- **On-device OCR is the weak step.** BODHAN IndicOCR reads these pages at about 26% character
  error against Claude's reading. End to end, it gets 184 of 340 names to the right person and none to
  the wrong one (after the v3 rule), against 300 and none from Claude's reading. See
  [OCR_BODHAN.md](OCR_BODHAN.md).
  The earlier attempt with `qwen3-vl:8b` in Ollama failed outright: it is the "thinking" variant,
  ignores `think: false`, and returned no transcript on the three pages tried (logs in
  `text/ocr_qwen3vl/`). **The OCR step, not name resolution, is the unsolved part.**
- **Claude's readings are the OCR reference, not verified ground truth.** Disputed cells were
  checked against the photos (for example the ₹800 in IMG_0206 row 4 and the crossed-out 800 in
  IMG_0208 row 4).
- **The roster was built from the same register pages**, because LokOS data was not
  available. In use, it would come from LokOS.
- **Which Sushma holds the loan** is an assumption marked in the roster. The ledger does
  not say. LokOS would.
- **The answer key and the rules have the same author.** To limit bias:
  - The key was written and hash-frozen before any rules existed (`gold/FROZEN.sha256`).
  - The rules were developed on dev pages only.
  - The test pages were scored once.
- **It is a small sample:** one SHG and one CLF, in Hindi. Dialect speech is a separate
  problem and is not covered here.

---

## Run it

All commands run from this folder and need nothing beyond the Mac's built-in Python.

```bash
cd ~/claude_demo/bench/ner
```

Walk through the 13 hard cases with real names (your screen only):

```bash
/usr/bin/python3 -I demo.py --step
```

The same walkthrough, safe to screenshot or share:

```bash
/usr/bin/python3 -I demo.py --pseudo
```

Try any line yourself:

```bash
/usr/bin/python3 -I resolve.py --book EKTA_CLF --line "BK सुनिता कुमारी को भाड़ा 300/- दिया गया"
```

Full trace of the test pages, then the score:

```bash
/usr/bin/python3 -I resolve.py --split test
```

```bash
/usr/bin/python3 -I score.py --split test --show-errors
```

Noise stress test (about 30 seconds):

```bash
/usr/bin/python3 -I stress.py --split all --seeds 5
```

## Files

| Path | What |
|---|---|
| `resolve.py` | the resolver (v2, plus the v3 repeated-line rule for OCR text) |
| `resolve_v1_frozen.py` | the rules exactly as frozen before the test run |
| `score.py`, `stress.py`, `demo.py` | scoring, noise test, walkthrough |
| `roster/roster.csv` | 15 SHG members and CM; 12 CLF board members; 25 CLF cadre. One spelling each, as LokOS would hold |
| `pages.csv` | page → book, dev/test split |
| `pages/` | the 19 page photos (1600 px) |
| `text/clean/` | reference readings of each page (by Claude; spot-check) |
| `text/ocr_qwen3vl/` | logs of the failed on-device OCR attempt |
| `gold/gold_spec.txt`, `gold/gold.csv` | answer key with a reason for each hard case; `FROZEN.sha256` |
| `out/` | decisions, scores, stress results, pseudonymised demo output, OCR reports |
| `OCR_BODHAN.md` | BODHAN IndicOCR results, with and without the harness |
| `eval_ocr.py` | scores an OCR run: text, numbers, names end to end, link audit |
| `pages_ocr/` | the 19 photos upright at 2250 × 3000 px, as read by BODHAN |
| `ocr/` | BODHAN output per page (`.md` + `.json`) and its read cache |
| `text/ocr_bodhan_*/` | BODHAN output converted to the resolver's line format |

## Possible next steps

1. Spot-check `text/clean/` against the photos, especially names marked uncertain in the roster.
2. Get a real LokOS member list for this SHG and CLF and re-run. Does LokOS separate the two Sushmas and the two Gudiyas?
3. Put the same resolver behind the SHG meeting transcription and track whether the same rules hold up there as well. Those transcripts may not always have the loan details, which was crucial here.
4. For the voice route: add the member code to the spoken read-back, so the resolver never has to guess between same-name members. Also, before doing OCR on any register, we can include the LokOS details of each member on a page so that linkages can be made easily.
5. Improve the OCR step: see the tested recommendations in [OCR_BODHAN.md](OCR_BODHAN.md).
