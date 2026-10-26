# OCR run: lab_harness_tab15+post_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **27.6%** (1923 edits over 6962 reference characters)
- Numbers (2+ digits) found: **219 of 262** (84%); the OCR produced 239 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 79 | 59.8% |
| correct no-link | 8 | 6.1% |
| held back (asked / not on roster) | 10 | 7.6% |
| missed (name not read) | 34 | 25.8% |
| WRONG: linked to another person | 1 | 0.8% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 86
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 70; naming someone the key does not have on that row: **4**

  - IMG_0208 row 4: `अनिता कुमारी` → V12; key on that row ['ASK']
  - IMG_0208 row 4: `अनिता कुमारी` → V12; key on that row ['ASK']
  - IMG_0096 row 9: `सुनयना देवी` → C07; key on that row ['C09']
  - IMG_0096 row 9: `सुनीना देवी` → C07; key on that row ['C09']

### Every wrong or stray link
- IMG_0096: key `सुनयना देवी` = C09; OCR `सुनयना देवी` → C07

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 15% | 51/53 | 47.9 | serial_breaks, cell_count_outliers |
| IMG_0207 | minutes | 910 | 31% | 12/12 | 3.9 |  |
| IMG_0208 | table | 742 | 35% | 32/52 | 47.2 | serial_breaks |
| IMG_0209 | minutes | 850 | 42% | 9/13 | 4.8 | zoom_rejected |
| IMG_0096 | table | 915 | 32% | 7/7 | 156.8 |  |
| IMG_0100 | table | 1074 | 15% | 57/57 | 41.2 | date_outliers, cell_count_outliers |
| IMG_0139 | table | 874 | 19% | 36/46 | 25.0 | serial_breaks |
| IMG_0164 | minutes | 874 | 33% | 15/22 | 13.1 | cell_count_outliers |
