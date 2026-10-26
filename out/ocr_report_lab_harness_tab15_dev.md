# OCR run: lab_harness_tab15_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **28.3%** (1971 edits over 6962 reference characters)
- Numbers (2+ digits) found: **214 of 262** (82%); the OCR produced 260 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 60 | 45.5% |
| correct no-link | 4 | 3.0% |
| held back (asked / not on roster) | 15 | 11.4% |
| missed (name not read) | 51 | 38.6% |
| WRONG: linked to another person | 2 | 1.5% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 67
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 58; naming someone the key does not have on that row: **6**

  - IMG_0208 row ८: `कंचन कुमारी` → V09; key on that row []
  - IMG_0208 row ८: `कंचन कुमारी` → V09; key on that row []
  - IMG_0208 row ९: `आरटी कुमारी` → V10; key on that row []
  - IMG_0208 row ९: `आरटी कुमारी` → V10; key on that row []
  - IMG_0096 row 9: `सुनयना देवी` → C07; key on that row ['C09']
  - IMG_0096 row 9: `सुनीना देवी` → C07; key on that row ['C09']

### Every wrong or stray link
- IMG_0096: key `सुनपना देवी` = C09; OCR `सुनयना देवी` → C07
- IMG_0096: key `सुनीता कुमारी` = K06; OCR `सुनीना देवी` → C07

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 15% | 51/53 | 47.9 | serial_breaks, cell_count_outliers |
| IMG_0207 | minutes | 910 | 31% | 12/12 | 3.9 |  |
| IMG_0208 | table | 742 | 34% | 30/52 | 47.2 | serial_breaks |
| IMG_0209 | minutes | 850 | 42% | 9/13 | 4.8 | zoom_rejected |
| IMG_0096 | table | 915 | 30% | 7/7 | 156.8 |  |
| IMG_0100 | table | 1074 | 18% | 57/57 | 41.2 | date_outliers, cell_count_outliers |
| IMG_0139 | table | 874 | 27% | 26/46 | 25.0 | serial_breaks |
| IMG_0164 | minutes | 874 | 31% | 22/22 | 13.1 | cell_count_outliers |
