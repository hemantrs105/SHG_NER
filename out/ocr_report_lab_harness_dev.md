# OCR run: lab_harness_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **23.4%** (1630 edits over 6962 reference characters)
- Numbers (2+ digits) found: **238 of 262** (91%); the OCR produced 268 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 80 | 60.6% |
| correct no-link | 12 | 9.1% |
| held back (asked / not on roster) | 14 | 10.6% |
| missed (name not read) | 26 | 19.7% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 83
- Person linked more often on a page than the key has her: **0** extra link(s)
- Links on numbered table rows: 67; naming someone the key does not have on that row: **0**

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 14% | 52/53 | 0.2 |  |
| IMG_0207 | minutes | 910 | 31% | 12/12 | 0.1 |  |
| IMG_0208 | table | 742 | 11% | 49/52 | 0.3 |  |
| IMG_0209 | minutes | 850 | 45% | 9/13 | 0.1 | zoom_rejected |
| IMG_0096 | table | 915 | 30% | 7/7 | 0.1 |  |
| IMG_0100 | table | 1074 | 15% | 56/57 | 0.1 | date_outliers |
| IMG_0139 | table | 874 | 15% | 31/46 | 0.1 |  |
| IMG_0164 | minutes | 874 | 26% | 22/22 |  |  |
