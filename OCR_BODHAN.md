# BODHAN IndicOCR on the Nalanda register pages: results, and what improves them

Run on 26 Oct 2026. Built with IndicOCR from Bodhan AI / AI4Bharat.

> Real names. Keep this file and `ocr/`, `text/ocr_*` on this laptop or in the private repo.

## In one paragraph

BODHAN reads these handwritten registers at about 26% character error against Claude's reading, and the
resolver gets 185 of 340 names to the right person from its text, with no wrong person. Bhavish's harness
changes no name and no number on these pages. Of ten training-free changes tested, only one helps and
holds up on the held-out pages: a small text clean-up after BODHAN (`ocr_post.py`), which brings 197 names
to the right person, 15 more numbers, and still no wrong person. Everything else tested (beam search,
contrast enhancement, a bigger pixel budget, reading tables in strips, upscaling) gives nothing, or makes
it worse. The rest of the gap is recognition inside the model, so it needs fine-tuning. A diagnostic
below shows which fields to fine-tune on first.

## What was run

| | |
|---|---|
| Model | `bodhan-ai/indic-ocr`, revision `cd50d301`: IndicDocLayout (33M, fp32) + IndicBlockOCR (Qwen3.5-0.8B, stored bf16) |
| Quantization | none; recognizer run in float32 (the harness default) |
| Harness | `bp-high/indic-ocr-harness` v0.1.0 (commit `b7aa6f2`), all components on |
| Without harness | the same tool with `--plain`: every harness component off, i.e. the model card's pipeline |
| Pages | the same 19 photos, upright (EXIF rotation applied first; the harness does not rotate), 2250 × 3000 px |
| Hardware | MacBook M5 Pro, 24 GB. GPU (`--device mps`) |
| Scoring | `eval_ocr.py`: text against Claude's reference readings; names through `resolve.py` (v3) against the frozen answer key, plus a link audit that does not depend on pairing |

## Speed

| | Time |
|---|---|
| One page on CPU, float32 (the setting Bhavish validated) | **96 min** (5,793 s) |
| The same page on the Mac GPU, float32 | **68 s**, output identical character for character |
| All 19 pages, harness on, GPU | 7.3 min (about 23 s a page) |
| All 19 pages, harness off, GPU | about 19 s a page of recognizer time |

The CPU path is unusable on this Mac: the model's fast linear-attention kernels are not installed
(`flash-linear-attention`, `causal-conv1d`), so it falls back to slow torch code. GPU and CPU output were
compared on one page only.

## Results (all 19 pages, 340 name mentions)

| | Claude's reading | BODHAN alone | BODHAN + harness | BODHAN + clean-up (`ocr_post.py`) |
|---|---|---|---|---|
| Character error rate | 0% (the reference) | 25.9% | 25.5% | 25.1% |
| Numbers (2+ digits) found | 558 / 558 | 515 / 558 | 515 / 558 | **530** / 558 |
| Names linked to the right person | 300 | 185 | 185 | **197** |
| Correctly not linked (ASK / NEW) | 40 | 36 | 36 | 36 |
| Held back (ASK / NEW) though a link was possible | 0 | 46 | 46 | 47 |
| Name not read | 0 | 73 | 73 | **60** |
| **Linked to the wrong person** | **0** | **0** | **0** | **0** |

The clean-up gives the same result with or without the harness.

**How the names are scored.** Each key mention is paired with an OCR mention on the same page: first
names must be close, best matches go first, and a numbered table row pairs only with the same row number.
Every link is also audited without the pairing:
- no person gets more links on a page than the key has for her;
- every link on a numbered row must name someone the key has on that row.

The row check flags 2 links in every BODHAN run, both on IMG_0110. BODHAN merged signatures written in the
margin ("सुनैना देवी V.R.P", "सीमा देवी CNRP") into table rows 1 and 9. The resolver names the right
people (the VRP and the CNRP), but on the wrong rows.

**The repeated-line rule (resolver v3).** The resolver now treats a line identical to the line next to it
as an OCR loop, and its names are ASK. Without that rule, IMG_0153 gave one wrong link (point 5 below).
The reference readings never repeat a line, so the clean-text results are unchanged (dev 132/132,
test 208/208).

> **Correction to the first version of this file (pushed earlier today).** It reported 184 right, 81 not
> read. My HTML-to-text converter dropped BODHAN's in-cell line breaks (`सीमा देवी<br/>CNRP` became
> "सीमा देवीCNRP"), which hid names from the resolver. The scorer's pairing was also order-dependent. Both
> are fixed (`eval_ocr.py`); every number in this file is from the fixed version.

### By book (BODHAN + harness, no clean-up)

| | Mentions | Right person | Correctly not linked | Held back | Not read | Wrong |
|---|---|---|---|---|---|---|
| SHG attendance tables | 139 | 82 | 34 | 7 | 16 | 0 |
| SHG minutes | 26 | 10 | 0 | 1 | 15 | 0 |
| CLF tables and signature blocks | 170 | 89 | 2 | 38 | 41 | 0 |
| CLF minutes | 5 | 4 | 0 | 0 | 1 | 0 |

## Does the harness help on these pages?

**Not for names or numbers.** Every name decision and the number count are identical with and without
it. Character error improves by 0.4 points:
- BODHAN sometimes writes register lines as LaTeX (`$$\text{कुल सख्त} = \frac{140}{1}$$`). The harness turns them back into plain text.
- A few words in non-name lines change.

It flagged 3 pages (rejected zooms on 2, an odd date on 1). It did not flag the repeated-line loop on
IMG_0153.

Bhavish's README says the remaining error is mostly recognition inside blocks (handwritten names, table
cells), which a training-free harness cannot fix. The experiments below agree.

## What goes wrong

1. **Signature blocks and minutes.** 43 of the 73 unread names are in free text, mainly the slanted
   cadre signatures under the CLF tables. Latin-script signatures (Dikshha Kumari, Sushil Rajan) are
   unread in 6 of 9.
2. **Printed column headers are garbled.** "मु० वपासी" comes out as उपधारी, दशवासी or वयाचीवक्त;
   "सदस्य" as सदल्प. The resolver then cannot tell which column holds repayments, and loses the role
   clue. The two Sushmas, separable on clean text in 7 mentions, are held back in all 7. It fails safe
   (ASK), but it does not resolve.
3. **Numbers that matter can vanish.** On IMG_0206 the only number BODHAN drops is the ₹800 interest
   repayment in row 4, the one fact that separates the two Sushmas on that page.
4. **A crossed-out amount is read as a real one.** IMG_0208 row 4 holds a struck-out 800 in the interest
   column. BODHAN reads "8", with no sign it is cancelled.
5. **A loop invents names.** On IMG_0153 BODHAN wrote "FICRP सुनीता कुमारी" three times, where the
   page has "सुशीला कुमारी FI CRP" and "प्रतिमा कुमारी FICRP". Resolver v2 linked all three to
   सुशीला; one of those stood where प्रतिमा should be. Resolver v3 asks instead.
6. **Margin text is merged into table rows** (IMG_0110). Besides putting a person on the wrong row,
   it puts a role ("V.R.P") among that row's clues.

### What-if: give the resolver the register's column layout (not adopted)

The SHG register is a printed format, so a deployed system could know which columns are repayments
instead of reading the header. Tried on the harness output:
- 3 of the 7 Sushma mentions become correct links;
- **4 new wrong links**, all from the crossed-out 800 on IMG_0208 (`out/ocr_report_bodhan_harness_tmpl.md`).

A known layout is safe only if the OCR also says when a cell is crossed out.

---

## Experiments: what improves BODHAN's accuracy

### Method

- **One change at a time.** `ocr_lab.py` runs BODHAN with exactly one change from a base (BODHAN alone,
  or with the harness). The page layout is detected once and kept, all variants share one read cache, and
  the base variants reproduce the earlier runs byte for byte.
- **Dev, then test.** Each change was tried on the 8 dev pages (132 name mentions). The ones carried
  forward were then run once on the 11 test pages (208 mentions), after code hashes and predictions were
  written down (`ocr/PREREG_TEST.md`).
- **The text clean-up was not blind.** Its rules were written after seeing BODHAN's output on all
  19 pages, so its test result is a check, not a blind test.
- **Safety first.** A change counts as a gain only if it adds no wrong link and no audit flag.

### Dev pages (132 name mentions, 262 numbers)

| Change | Right | Held back | Not read | Wrong (+ audit flags) | Numbers | Error rate |
|---|---|---|---|---|---|---|
| BODHAN alone | 80 | 14 | 26 | 0 | 238 | 24.2% |
| BODHAN + harness | 80 | 14 | 26 | 0 | 238 | 23.4% |
| **+ text clean-up** (either base) | **87** | 15 | **18** | 0 | **252** | 22.3–22.4% |
| + clean-up + beam search (3 beams) | 87 | 13 | 20 | 0 | 253 | 22.1% |
| + clean-up + 2048 px budget (tables not shrunk) | 88 | 14 | 18 | 0 | 253 | 22.6% |
| + clean-up + enhanced photos (flat lighting, contrast) | 85 | 14 | 21 | 0 | 251 | 22.6% |
| + clean-up + tables read in strips at native size | 91 | 14 | 15 | 0 | 247 | 22.7% |
| + clean-up + tables in strips at 1.5× | 79 | 10 | 34 | 1 (+4) | 219 | 27.6% |
| + clean-up + tables in strips at 2× | 70 | 12 | 40 | 0 (+2) | 215 | 26.8% |

Beam search took about 1.8× the time of greedy decoding. The 1.5× and 2× strips misread names into other
members (IMG_0208 row 4, Sushma, read as "अनिता कुमारी" and linked to Anita).

### Test pages (208 name mentions, 296 numbers), run once

| Change | Right | Held back | Not read | Wrong (+ audit flags) | Numbers | Error rate | Prediction |
|---|---|---|---|---|---|---|---|
| BODHAN alone | 105 | 32 | 47 | 0 (+2) | 277 | 27.2% | |
| BODHAN + harness | 105 | 32 | 47 | 0 (+2) | 277 | 27.1% | |
| **+ text clean-up** (either base) | **110** | 32 | **42** | 0 (+2) | **278** | 27.1–27.2% | 1, 2: **held** |
| harness + strips at native size + clean-up | 104 | 31 | 51 | 0 (+2) | 269 | 28.0% | 3: **failed** |

The +2 flags are the IMG_0110 margin merge, present in every run. The strip variant's one scorer-flagged
"guess" is the IMG_0118 "C.M सीमा देवी" line, which the strips did not read at all. The remaining
"सीमा देवी" is the CNRP, and the resolver links her correctly.

**Reading tables in strips looked good on dev (+4 names) and was worse on the held-out pages (−6
names, −9 numbers).** On IMG_0208 its first strip read every "900" as "500". It is not recommended.

### The text clean-up (`ocr_post.py`)

No model, standard library, about 1 ms a page. Nothing in it knows the roster or the page.

| Rule | Example |
|---|---|
| LaTeX to plain text | `$$\text{कुल सख्त} = \frac{140}{1}$$` → कुल सख्त = 140/1 |
| Devanagari digits to ASCII | १२ → 12 |
| Space where Devanagari and Latin letters touch, and before capitals after a lower-case letter | "C.Mसीमा" → "C.M सीमा"; "kumariCNRP" → "kumari CNRP" |
| Space before a surname glued onto a name (compound names such as राजकुमार are kept) | "सुनिताकुमारी" → "सुनिता कुमारी"; "Dikshakumari" → "Diksha kumari" |
| Drop repeated rows and headers when a table comes back in pieces | a row number already seen in the same run of tables |

Separately, **anyone parsing BODHAN's HTML tables must turn `<br/>` into a space**, not delete it.
BODHAN puts a name and the role under it in one cell with `<br/>` between them.

### Second read as a check on numbers (promising; small sample)

`crosscheck.py` compares two reads of each table row:
- the normal read;
- a second read with the tables in strips at native size.

| Field | Rows | Wrong in the normal read | Caught (the two reads disagree) | Rows sent to review | Wrong although both reads agree |
|---|---|---|---|---|---|
| Numbers in a row | 108 | 9 | **7** | 17 | 2 |
| Name cell | 154 | 48 | 14 | 18 | 34 |

For numbers, a disagreement is a useful "check this row" flag. For names it is not: two reads by the
same model mostly make the same mistake. Only 9 wrong number rows were seen, so treat this as a lead to
test on more pages, not a result.

### Where fine-tuning would pay most (diagnostic)

In BODHAN's table rows (harness + clean-up, all 19 pages), one kind of field at a time was replaced with
Claude's reading of it. The resolver was then re-run. This is an upper bound for each field, not a
prediction of what fine-tuning will reach.

| Fields read as well as the reference | Right | Held back | Not read |
|---|---|---|---|
| None (as now) | 197 | 47 | 60 |
| Column headers only | 200 | 44 | 60 (and **4 wrong**: the crossed-out cell) |
| Clue cells: role, village, MIS ID, amounts, crossed-out marks | **221** | **18** | 65 |
| Name and signature cells | **231** | 30 | **43** |
| The whole table | 257 | 4 | 43 |

Wrong-link counts are not meaningful in the last three rows. Substituting reference rows removes the
margin text BODHAN merged into them, and duplicates some names. The "Column headers only" row is the
exception: its 4 wrong links are real behaviour.

- **Even a perfect table leaves 43 names unread** in free text: signature blocks and minutes.
- **Reading the clue cells right is worth +24 names, with no wrong link.** It needs the crossed-out
  marks; the headers alone add wrong links.

---

## Recommendations

**Proven here, on dev and on the held-out pages:**

1. **Add the text clean-up after BODHAN** (`ocr_post.py`, or the same five rules in any language).
   Over all 19 pages it gives:
   - +12 names to the right person (185 → 197), 13 fewer unread;
   - +15 numbers;
   - no wrong link.
   It costs nothing.
2. **Keep the repeated-line rule in the resolver** (v3). It turned the one wrong link into a question.
3. **Run BODHAN on a GPU** (Apple MPS works, identical output on the page compared). On this Mac's CPU a
   page takes 96 minutes.

**Shown not to help on these pages (don't spend effort here):**

4. **The harness**: no change to any name or number.
5. **Beam search**: no gain; about 1.8× slower.
6. **Contrast enhancement**, or a **bigger pixel budget** (2048²): no gain.
7. **Reading big tables in strips** at native size: better on dev, worse on the held-out pages.
8. **Upscaling** (1.5×, 2×): worse, with real wrong links.

**Needs fine-tuning (for Bodhan AI); the diagnostic shows the order:**

9. **Clue cells of the register format:**
   - the printed column headers of the Jeevika SHG register;
   - the role words and abbreviations (सदस्य, अध्यक्ष, उपसचिव, BK, CNRP, VRP, FI CRP, ...);
   - villages and amounts.
   Up to +24 names, and it unlocks the loan clue that separates same-name members.
10. **Crossed-out entries must appear in the output** (for example as `<s>800</s>`). Without that, reading
    the headers right adds wrong links. That is the worst failure in this test for a ledger posting to LokOS.
11. **Handwritten names and signatures:**
    - up to +34 names from table cells;
    - signature blocks and minutes hold 43 more;
    - Latin-script signatures are mostly lost today.
12. **Keep margin text out of table rows.** Signatures written beside a table become cells of a row.

**For the harness (Bhavish):**

13. **Repeated-line guard.** It missed the three identical lines on IMG_0153.
14. **Repeated rows in tiled tables.** When it tiles a table, the header band includes the first data row,
    and that row is not always dropped: on IMG_0206 it appeared twice. Drop rows by serial number.
15. **Its zoom trigger (`min_line=32`) never fires on these pages.** Raising it to tile tables did not pay
    off (point 7).

**Not tested here:** deskewing or dewarping the photos, capture guidance for the field staff, other
prompts (the model is trained on its own), the vLLM backend, bfloat16.

## Reproduce

```bash
cd ~/claude_demo/bench/ner
~/claude_demo/.venv-indicocr/bin/indic-ocr-harness read pages_ocr/*.jpg --device mps --out-dir ocr/mps_harness --cache ocr/mps_test/cache.json
~/claude_demo/.venv-indicocr/bin/indic-ocr-harness read pages_ocr/*.jpg --device mps --plain --out-dir ocr/mps_plain --cache ocr/mps_test/cache.json
/usr/bin/python3 -I eval_ocr.py ocr/mps_harness bodhan_harness
/usr/bin/python3 -I eval_ocr.py ocr/mps_plain bodhan_plain
```

Experiments (any variant listed in `ocr_lab.py`), then the clean-up, then the score:

```bash
~/claude_demo/.venv-indicocr/bin/python ocr_lab.py harness --split all
/usr/bin/python3 -I ocr_post.py ocr/lab_harness ocr/lab_harness+post
/usr/bin/python3 -I eval_ocr.py ocr/lab_harness+post lab_harness+post_test test
```

| File | What |
|---|---|
| `ocr_lab.py` | runs one variant (base + one change) |
| `ocr_post.py` | the text clean-up |
| `eval_ocr.py` | scores a run: error rate, numbers, names, link audit |
| `crosscheck.py` | compares two reads row by row |
| `oracle_ablation.py` | the fine-tuning diagnostic |
| `ocr/PREREG_TEST.md` | code hashes and predictions written before the test pages |
| `ocr/lab_*/` | every variant's output; `ocr/layout/` the fixed layouts; `ocr/lab_cache.json` the reads |
| `out/ocr_report_*.md`, `out/ocr_pairs_*.csv` | per-run reports and pairings |
