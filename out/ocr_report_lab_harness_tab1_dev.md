# OCR run: lab_harness_tab1_dev

Pages read: 8 of 19

## Text quality (against Claude's reference readings)

- Character error rate: **28.4%** (1975 edits over 6962 reference characters)
- Numbers (2+ digits) found: **191 of 262** (73%); the OCR produced 275 numbers in all

## Names, end to end (OCR → resolver → answer key)

| Outcome | Count | Share |
|---|---|---|
| correct link | 58 | 43.9% |
| correct no-link | 4 | 3.0% |
| held back (asked / not on roster) | 15 | 11.4% |
| missed (name not read) | 55 | 41.7% |
| WRONG: linked to another person | 0 | 0.0% |
| WRONG: guessed | 0 | 0.0% |

Name mentions in the key for these pages: 132
Links to people who are not on that page at all (stray): 0

## Link audit (independent of the pairing)

- Links made: 81
- Person linked more often on a page than the key has her: **1** extra link(s)
- Links on numbered table rows: 72; naming someone the key does not have on that row: **20**

  - IMG_0206: V01 linked 3 times, key has 2
  - IMG_0208 row १: `श्रीमती देवी` → V01; key on that row []
  - IMG_0208 row १: `श्रीमती देवी` → V01; key on that row []
  - IMG_0208 row २: `रिमा कुमारी` → V02; key on that row []
  - IMG_0208 row २: `रीमा कुमारी` → V02; key on that row []
  - IMG_0208 row ३: `स्वीटी कुमारी` → V03; key on that row []
  - IMG_0208 row ३: `स्वीटी कुमारी` → V03; key on that row []
  - IMG_0208 row ५: `गीता देवी` → V05; key on that row []
  - IMG_0208 row ५: `गीता देवी` → V05; key on that row []
  - IMG_0208 row ६: `विन्दुमा कुमारी` → V07; key on that row []
  - IMG_0208 row ६: `विन्दुमा कुमारी` → V07; key on that row []
  - IMG_0208 row ८: `कंचन कुमारी` → V09; key on that row []
  - IMG_0208 row ८: `कंचन कुमारी` → V09; key on that row []
  - IMG_0208 row ९: `अरती कुमारी` → V10; key on that row []
  - IMG_0208 row ९: `अरती कुमारी` → V10; key on that row []
  - IMG_0208 row १०: `पुजा कुमारी` → V11; key on that row []
  - IMG_0208 row १०: `पुजा कुमारी` → V11; key on that row []
  - IMG_0208 row ११: `अनीता कुमारी` → V12; key on that row []
  - IMG_0208 row ११: `अनीता कुमारी` → V12; key on that row []
  - IMG_0208 row १४: `फुला देवी` → V14; key on that row []
  - IMG_0208 row १४: `फुला देवी` → V14; key on that row []

## Per page

| Page | Kind | Ref chars | CER | Numbers found | Seconds | Flags |
|---|---|---|---|---|---|---|
| IMG_0206 | table | 723 | 37% | 53/53 | 37.0 | serial_breaks |
| IMG_0207 | minutes | 910 | 31% | 12/12 | 0.1 |  |
| IMG_0208 | table | 742 | 31% | 2/52 | 24.8 | serial_breaks |
| IMG_0209 | minutes | 850 | 45% | 9/13 | 0.1 | zoom_rejected |
| IMG_0096 | table | 915 | 31% | 7/7 | 0.1 |  |
| IMG_0100 | table | 1074 | 16% | 57/57 | 24.6 | date_outliers |
| IMG_0139 | table | 874 | 15% | 31/46 | 0.1 |  |
| IMG_0164 | minutes | 874 | 26% | 20/22 |  |  |
