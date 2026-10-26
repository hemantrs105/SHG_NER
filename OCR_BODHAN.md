# BODHAN IndicOCR on the Nalanda register pages, with and without Bhavish's harness

Run on 26 Oct 2026. Built with IndicOCR from Bodhan AI / AI4Bharat.

> Real names. Keep this file and `ocr/`, `text/ocr_*` on this laptop or in the private repo.

## What was run

| | |
|---|---|
| Model | `bodhan-ai/indic-ocr`, revision `cd50d301`: IndicDocLayout (33M, fp32) + IndicBlockOCR (Qwen3.5-0.8B, stored bf16) |
| Quantization | none; recognizer run in float32 (the harness default) |
| Harness | `bp-high/indic-ocr-harness` v0.1.0 (commit `b7aa6f2`), all components on |
| Without harness | the same tool with `--plain`: every harness component off, i.e. the model card's pipeline |
| Pages | the same 19 photos, upright (EXIF rotation applied first; the harness does not rotate), 2250 × 3000 px |
| Hardware | MacBook M5 Pro, 24 GB. GPU (`--device mps`) for the full runs |
| Scoring | `eval_ocr.py`: text against Claude's reference readings; names through `resolve.py` (v2) against the frozen answer key |

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

## Results

| | Claude's reading | BODHAN + harness | BODHAN without harness |
|---|---|---|---|
| Character error rate | 0% (it is the reference) | 25.8% | 26.2% |
| Numbers (2+ digits) found | 558 / 558 | 513 / 558 (92%) | 513 / 558 (92%) |
| Names linked to the right person | 300 | 184 | 184 |
| Correctly not linked (ASK / NEW) | 40 | 35 | 35 |
| Held back (ASK / NEW) though a link was possible | 0 | 40 | 40 |
| Name not read | 0 | 81 | 81 |
| **Linked to the wrong person** | **0** | **0** (1 before the repeated-line rule) | **0** (1 before the rule) |
| Total name mentions | 340 | 340 | 340 |

Names are scored with resolver v3, which adds one rule after this run: a line identical to the line
next to it is an OCR loop, so its names are ASK (see point 4 below). Before that rule the same runs
had 186 right and 1 wrong. The scorer pairs each key mention with an OCR mention on the same page by
first name; a numbered table row only pairs with the same row number. Every link is also audited
without the pairing: no person gets more links on a page than the key has for her, and all 171 links
on numbered table rows name a person the key has on the same-numbered reference row.

### By book

| | Mentions | Right person | Correctly not linked | Held back | Not read | Wrong |
|---|---|---|---|---|---|---|
| SHG attendance tables | 139 | 81 | 33 | 7 | 18 | 0 |
| SHG minutes | 26 | 10 | 0 | 1 | 15 | 0 |
| CLF tables and signature blocks | 170 | 89 | 2 | 32 | 47 | 0 |
| CLF minutes | 5 | 4 | 0 | 0 | 1 | 0 |

## Does the harness help on these pages?

**Not for names or numbers.** Every name decision is identical with and without it, and so is the
number count. Character error rate improves by 0.4 points. The harness's visible changes:

- BODHAN sometimes writes lines as LaTeX (`$$\text{कुल सख्त} = \frac{140}{1}$$`); the harness turns them back
  into plain text.
- A few words in non-name lines differ, e.g. a village spelt हरबशपुर instead of हरवरापूर (the page says हरवंशपुर).
- It flagged 3 pages (rejected zooms on 2, an odd date on 1). It did not flag the repeated-line loop on IMG_0153.

Bhavish's README says the remaining error is mostly recognition inside blocks (handwritten names, table
cells), which a training-free harness cannot fix. That matches what these pages show.

## What goes wrong, and why it matters for name resolution

1. **Signature blocks are mostly lost.** 49 of the 81 names not read are in free text, mainly the
   slanted cadre signatures under the CLF tables (BK, CNRP, CF, ...). Latin-script signatures
   (Dikshha Kumari, Sushil Rajan) are lost almost every time: 8 of 9.
2. **Printed column headers are garbled.** "मु० वपासी" comes out as उपधारी, दशवासी or वयाचीवक्त;
   "सदस्य" as सदल्प. The resolver then cannot tell which column holds repayments, and loses the
   role anchor. The two Sushmas, separable on clean text in 7 mentions, are held back in all 7.
   The two Pinkis and the board/cadre Sunitas are held back on some pages for the same reason.
   This fails safe: ASK, not a wrong link.
3. **Numbers that matter can vanish.** On IMG_0206 the only number BODHAN dropped is the ₹800 interest
   repayment in row 4, which is the one fact that separates the two Sushmas on that page.
4. **A loop invented names, and caused the one wrong link.** On IMG_0153 BODHAN wrote
   "FICRP सुनीता कुमारी" three times where the page has "सुशीला कुमारी FI CRP" and
   "प्रतिमा कुमारी FICRP". The resolver (v2) used the FI CRP role to link all three to सुशीला (the only
   FI CRP with a similar name). Two were right by luck; the third stood where प्रतिमा should be.
   **Fixed in resolver v3:** a line identical to its neighbour is treated as a loop, and its names are
   ASK. The reference readings never repeat a line, so the clean-text results are unchanged
   (dev 132/132, test 208/208).

### What-if: give the resolver the register's column layout (not adopted)

The SHG register is a printed format, so a deployed system could know that columns 7 and 8 are
repayments instead of reading the header. Tried after the runs, on the harness output:

- 3 of the 7 Sushma mentions become correct links.
- **4 new wrong links** (`out/ocr_report_bodhan_harness_tmpl.md`). On IMG_0208 row 4 the interest cell holds a **crossed-out** 800. BODHAN reads
  it as "8", with no sign it is struck out. The resolver takes the cancelled entry as a repayment,
  links the row to the Sushma with a loan, and by elimination links the other Sushma row the other way.

So a known layout is only safe if the OCR also says when a cell is crossed out. In a ledger that
posts to LokOS, a cancelled repayment read as a real one is the more serious error.

## Fixes worth trying next

1. **Ask the OCR for strike-outs:** test whether BODHAN can be prompted to mark struck-out cells, before any
   column template is used.
2. **Install the fast kernels** (`flash-linear-attention`, `causal-conv1d`) if CPU-only devices are the target,
   and re-time.
3. **Fine-tuning, not harnessing,** is where the remaining gains are: handwritten names, signatures,
   and the printed headers of this one register format.

## Reproduce

```bash
cd ~/claude_demo/bench/ner
~/claude_demo/.venv-indicocr/bin/indic-ocr-harness read pages_ocr/*.jpg --device mps --out-dir ocr/mps_harness --cache ocr/mps_test/cache.json
~/claude_demo/.venv-indicocr/bin/indic-ocr-harness read pages_ocr/*.jpg --device mps --plain --out-dir ocr/mps_plain --cache ocr/mps_test/cache.json
/usr/bin/python3 -I eval_ocr.py ocr/mps_harness bodhan_harness
/usr/bin/python3 -I eval_ocr.py ocr/mps_plain bodhan_plain
```

Outputs: `out/ocr_report_bodhan_*.md` (automatic scores and per page), `out/ocr_pairs_bodhan_*.csv`
(how each key mention was paired), `out/decisions_ocr_bodhan_*_all.csv` (every resolver decision).
The single CPU page is in `ocr/bodhan_harness/`. The what-if is `ocr/mps_harness_tmpl/` and
`out/ocr_report_bodhan_harness_tmpl.md`.
