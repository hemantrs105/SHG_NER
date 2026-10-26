# OCR run: lab_harness_tab2_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **31.0%** (2159 edits over 6962 reference characters)
- Numbers (2+ digits) found: **210 of 262** (80%); the OCR produced 265 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 57 | 43.2% |
| correct no-link | 5 | 3.8% |
| held back (asked / not on roster) | 16 | 12.1% |
| missed (name not read) | 54 | 40.9% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 62
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 51; naming someone the key does not have on that row: **2**

  - IMG_0208 row १: `श्रीमती देवी` → V01; key on that row []
  - IMG_0208 row १: `भीमती देवी` → V01; key on that row []

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 15% | 51/53 | 74.1 | serial_breaks, cell_count_outliers |
| IMG_0207 | minutes | 910 | 30% | 12/12 | 10.1 |  |
| IMG_0208 | table | 742 | 58% | 21/52 | 143.3 | serial_breaks |
| IMG_0209 | minutes | 850 | 44% | 9/13 | 54.6 | zoom_rejected |
| IMG_0096 | table | 915 | 34% | 7/7 | 32.9 |  |
| IMG_0100 | table | 1074 | 16% | 57/57 | 64.7 | date_outliers |
| IMG_0139 | table | 874 | 24% | 31/46 | 31.6 | serial_breaks |
| IMG_0164 | minutes | 874 | 32% | 22/22 | 17.5 | cell_count_outliers |
