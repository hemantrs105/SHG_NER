# OCR run: bodhan_harness_tmpl

Pages read: 19 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **24.4%** (3976 edits over 16272 reference characters)
- Numbers (2+ digits) found: **515 of 558** (92%); the OCR produced 580 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 188 | 55.3% |
| correct no-link | 32 | 9.4% |
| held back (asked / not on roster) | 43 | 12.6% |
| missed (name not read) | 73 | 21.5% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 4 | 1.2% |

Name mentions in the key for these pages: 340
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 198
- Person linked more often on a page than the key has her: **4** extra link(s)
- Links on numbered table rows: 172; naming someone the key does not have on that row: **6**

  - IMG_0208: V04 linked 2 times, key has 0
  - IMG_0208: V06 linked 2 times, key has 0
  - IMG_0208 row 4: `सुषमा कुमारी` → V04; key on that row ['ASK']
  - IMG_0208 row 4: `सुषमा कुमारी` → V04; key on that row ['ASK']
  - IMG_0208 row 13: `सुषमा कुमारी` → V06; key on that row ['ASK']
  - IMG_0208 row 13: `सुषमा कुमारी` → V06; key on that row ['ASK']
  - IMG_0110 row 1: `सुनैना देवी` → K17; key on that row ['C01']
  - IMG_0110 row 9: `सीमा देवी` → K04; key on that row ['C09']

### Every wrong or stray link
- IMG_0208: key `सुषमा कुमारी` = ASK; OCR `सुषमा कुमारी` → V04
- IMG_0208: key `सुषमा कुमारी` = ASK; OCR `सुषमा कुमारी` → V04
- IMG_0208: key `सुषमा कुमारी` = ASK; OCR `सुषमा कुमारी` → V06
- IMG_0208: key `सुषमा कुमारी` = ASK; OCR `सुषमा कुमारी` → V06

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 8% | 52/53 |  |  |
| IMG_0207 | minutes | 910 | 31% | 12/12 |  |  |
| IMG_0208 | table | 742 | 4% | 49/52 |  |  |
| IMG_0209 | minutes | 850 | 45% | 9/13 |  |  |
| IMG_0096 | table | 915 | 30% | 7/7 |  |  |
| IMG_0100 | table | 1074 | 15% | 56/57 |  |  |
| IMG_0139 | table | 874 | 15% | 31/46 |  |  |
| IMG_0164 | minutes | 874 | 26% | 22/22 |  |  |
| IMG_0210 | table | 713 | 16% | 51/55 |  |  |
| IMG_0211 | minutes | 990 | 23% | 10/14 |  |  |
| IMG_0212 | table | 687 | 10% | 49/51 |  |  |
| IMG_0213 | minutes | 842 | 33% | 14/15 |  |  |
| IMG_0214 | table | 768 | 7% | 51/53 |  |  |
| IMG_0215 | minutes | 1007 | 42% | 13/15 |  |  |
| IMG_0104 | table | 914 | 14% | 35/35 |  |  |
| IMG_0110 | table | 971 | 45% | 6/6 |  |  |
| IMG_0118 | table | 769 | 28% | 8/8 |  |  |
| IMG_0145 | table | 772 | 26% | 33/35 |  |  |
| IMG_0153 | table | 877 | 34% | 7/9 |  |  |
