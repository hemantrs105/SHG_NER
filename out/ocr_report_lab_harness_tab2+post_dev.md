# OCR run: lab_harness_tab2+post_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **26.8%** (1864 edits over 6962 reference characters)
- Numbers (2+ digits) found: **215 of 262** (82%); the OCR produced 238 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 70 | 53.0% |
| correct no-link | 10 | 7.6% |
| held back (asked / not on roster) | 12 | 9.1% |
| missed (name not read) | 40 | 30.3% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 75
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 63; naming someone the key does not have on that row: **2**

  - IMG_0208 row 5: `अनिता कुमारी` → V12; key on that row ['V05']
  - IMG_0208 row 5: `अनिता कुमारी` → V12; key on that row ['V05']

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 15% | 51/53 | 74.1 | serial_breaks, cell_count_outliers |
| IMG_0207 | minutes | 910 | 27% | 9/12 | 10.1 |  |
| IMG_0208 | table | 742 | 26% | 33/52 | 143.3 | serial_breaks |
| IMG_0209 | minutes | 850 | 39% | 6/13 | 54.6 | zoom_rejected |
| IMG_0096 | table | 915 | 37% | 7/7 | 32.9 |  |
| IMG_0100 | table | 1074 | 14% | 57/57 | 64.7 | date_outliers |
| IMG_0139 | table | 874 | 16% | 39/46 | 31.6 | serial_breaks |
| IMG_0164 | minutes | 874 | 39% | 13/22 | 17.5 | cell_count_outliers |
