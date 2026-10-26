# OCR run: lab_harness+post_all

Pages read: 19 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **25.1%** (4079 edits over 16272 reference characters)
- Numbers (2+ digits) found: **530 of 558** (95%); the OCR produced 580 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 197 | 57.9% |
| correct no-link | 36 | 10.6% |
| held back (asked / not on roster) | 47 | 13.8% |
| missed (name not read) | 60 | 17.6% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 340
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 203
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 173; naming someone the key does not have on that row: **2**

  - IMG_0110 row 1: `सुनैना देवी` → K17; key on that row ['C01']
  - IMG_0110 row 9: `सीमा देवी` → K04; key on that row ['C09']

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 14% | 52/53 | 0.2 |  |
| IMG_0207 | minutes | 910 | 31% | 12/12 | 0.1 |  |
| IMG_0208 | table | 742 | 11% | 49/52 | 0.3 |  |
| IMG_0209 | minutes | 850 | 45% | 9/13 | 0.1 | zoom_rejected |
| IMG_0096 | table | 915 | 29% | 7/7 | 0.1 |  |
| IMG_0100 | table | 1074 | 15% | 56/57 | 0.1 | date_outliers |
| IMG_0139 | table | 874 | 6% | 45/46 | 0.1 |  |
| IMG_0164 | minutes | 874 | 26% | 22/22 |  |  |
| IMG_0210 | table | 713 | 21% | 51/55 | 0.2 | zoom_rejected |
| IMG_0211 | minutes | 990 | 23% | 11/14 | 0.1 |  |
| IMG_0212 | table | 687 | 16% | 49/51 | 0.2 |  |
| IMG_0213 | minutes | 842 | 33% | 14/15 | 0.1 |  |
| IMG_0214 | table | 768 | 7% | 51/53 | 0.1 |  |
| IMG_0215 | minutes | 1007 | 42% | 13/15 | 0.1 |  |
| IMG_0104 | table | 914 | 14% | 35/35 | 0.1 |  |
| IMG_0110 | table | 971 | 45% | 6/6 | 0.1 |  |
| IMG_0118 | table | 769 | 28% | 8/8 | 0.1 |  |
| IMG_0145 | table | 772 | 26% | 33/35 | 0.1 |  |
| IMG_0153 | table | 877 | 34% | 7/9 | 0.1 |  |
