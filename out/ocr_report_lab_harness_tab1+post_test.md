# OCR run: lab_harness_tab1+post_test

Pages read: 11 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **28.0%** (2603 edits over 9310 reference characters)
- Numbers (2+ digits) found: **269 of 296** (91%); the OCR produced 300 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 104 | 50.0% |
| correct no-link | 21 | 10.1% |
| held back (asked / not on roster) | 31 | 14.9% |
| missed (name not read) | 51 | 24.5% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 1 | 0.5% |

Name mentions in the key for these pages: 208
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 107
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 97; naming someone the key does not have on that row: **2**

  - IMG_0110 row 1: `सुनैना देवी` → K17; key on that row ['C01']
  - IMG_0110 row 9: `सीमा देवी` → K04; key on that row ['C09']

### Every wrong or stray link
- IMG_0118: key `सीमा देवी` = ASK; OCR `सीमा देवी` → K04

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0210 | table | 713 | 20% | 51/55 | 42.2 | zoom_rejected, cell_count_outliers |
| IMG_0211 | minutes | 990 | 23% | 11/14 | 0.1 |  |
| IMG_0212 | table | 687 | 17% | 49/51 | 30.3 | serial_breaks |
| IMG_0213 | minutes | 842 | 33% | 14/15 | 0.1 |  |
| IMG_0214 | table | 768 | 16% | 42/53 | 31.9 | serial_breaks |
| IMG_0215 | minutes | 1007 | 42% | 13/15 | 0.1 |  |
| IMG_0104 | table | 914 | 14% | 35/35 | 0.1 |  |
| IMG_0110 | table | 971 | 45% | 6/6 | 0.1 |  |
| IMG_0118 | table | 769 | 29% | 8/8 | 13.3 |  |
| IMG_0145 | table | 772 | 26% | 33/35 | 0.1 |  |
| IMG_0153 | table | 877 | 34% | 7/9 | 0.1 |  |
