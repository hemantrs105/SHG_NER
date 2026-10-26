# Rulebook: who does this name on the register refer to?

This is every rule the demo uses, in order. You can follow it by hand with a pencil,
or code it in any language. It needs no AI model and no training data.

---

## What you need

1. **The text of the page**, line by line. Tables keep their columns, separated by `|`.
   If the text comes from an OCR model, clean it first: split words the OCR glued together
   ("सुनिताकुमारी" → "सुनिता कुमारी", "देवीCNRP" → "देवी CNRP"), and turn line breaks inside a
   table cell into spaces. `ocr_post.py` does this for BODHAN.
2. **The roster** of the group the register belongs to. One row per person:
   ID, name, role, village, MIS ID (if any), and whether she has a loan.
   Use only the roster of that register's own group. An SHG register is checked
   against that SHG's members and CM. A CLF minute book is checked against its board
   and cadre.
3. **Six short word lists** (at the end of this rulebook). These are the only part that
   changes for another language.

## What you get

For every person mentioned on the page, one of three answers:

| Answer | Meaning | What happens next |
|---|---|---|
| **A roster ID** | We know who this is | Post the entry |
| **ASK** | Two or more people fit and the page does not say which one, or the page contradicts the only match | Read it back to the group with the facts that tell them apart |
| **NEW** | A person who is not on the roster | Check, and add to the roster if needed |

**The golden rule: never guess.** A wrong person is worse than a question.

---

## Step 1. Turn every name into a spelling key

People write the same name in many ways, and OCR adds more. Before comparing, reduce
every name (Devanagari or English) to a rough sound key:

| Rule | Example |
|---|---|
| Short and long vowels are the same | ि = ी, ु = ू → सुनिता = सुनीता |
| ब and व are the same | बिमला = विमला |
| श, ष, स are the same | सुषमा = सुशमा = सुसमा |
| ण = न, ड़ = ड | पीणा = पीना |
| ं and ँ become "n" | बंसती → "bansati" |
| Drop the "h" of aspirated letters | भ = ब, ध = द, "sh" = "s" → Shobha = Sobha |
| Doubled letters count once | "Dikshha" = "Diksha" |
| Drop a final "a" | सुशीला and सुशील → same key "susil" |
| English letters use the same key | "Sushil" = सुशील, "Diksha" = दीक्षा |

## Step 2. Measure how close two keys are

**Closeness = 1 − (number of letters you must add, remove or change ÷ length of the longer key)**

| Keys | Changes | Closeness |
|---|---|---|
| sunit / sunit (सुनिता / सुनीता) | 0 | 1.0 (same) |
| sunil / susil | 1 of 5 | 0.8 |
| amit / anit (अमिता / अनीता) | 1 of 4 | 0.75 |
| rin / rit (रीना / रिता) | 1 of 3 | 0.67 |

Two numbers matter throughout: **0.8 means "close"**, **0.6 means "weakly similar"**.

## Step 3. Split the page into rows and cells

- A line with `|` that starts with a number is a **table row**. Treat each cell separately.
- A line with `|` that contains the word **नाम** is a **header row**. Note which columns
  say **वापसी / वपासी** (repayment). You need them in step 5.
- Every other line is **free text**.
- **A line that is exactly the same as the line before or after it** is an OCR loop, not two entries.
  Every name on it is **ASK**, and it is not used in step 8. (Only matters for machine-read text;
  people do not write the same line twice.)

## Step 4. Find the names

Look at every run of **1, 2 or 3 words** in each cell or free-text line.

**Skip a run if** it contains a role word, a number, a stop word, half of a two-word
role (such as FI or CRP), or if it starts with a surname word (देवी, कुमारी, ...).

**Compare the run with every person on the roster.** The last word is the surname; the
rest is the first name. Give each person a grade:

| Grade | When | Example |
|---|---|---|
| **A, exact** | First name has the same key, and the surname is the same or fits an abbreviation (कु० = कुमारी/कुमार, प्र० = प्रसाद) | सुनिता कुमारी → सुनीता कुमारी; अशोक कु० → अशोक कुमार |
| **B, close** | First-name closeness at least 0.8, surname fits | सुनपना देवी → सुनयना देवी |
| **C, first name only** | A single word, exact first name, at least 3 letters, not a common word | "400 स्वीटी" → स्वीटी कुमारी |
| **D, needs proof** | First name exact but surname different; or surname fits and first-name closeness 0.6 to 0.8 | नरेन्द्र कुमार → नरेन्द्र प्रसाद; बंसती → बसंती |

**Two words ending in देवी, कुमारी, कुमार, प्रसाद or रानी are a person** even if nobody on
the roster is close. Keep them; they may turn out to be NEW.

**When runs overlap,** keep the best grade. On a tie keep the longer run. A single
first-name word (grade C) always loses to a two-word run that covers it.

## Step 5. Collect the evidence around each name

**In a table row,** everything in the row is evidence for every name in the row:

- role words (BK, CNRP, सचिव, सदस्य, ...);
- village names (closeness at least 0.8 to a roster village);
- a 10-digit MIS ID;
- any amount in a repayment column (step 3).

**In free text,** only a **role word right next to the name** counts:

- "सीमा देवी **CNRP**": the role after the name.
- "**BK** सुनिता कुमारी": the role before the name.
- A role between two names ("स्वीटी कुमारी **CM** बबीता देवी") goes to the name that
  has someone with that role among its candidates. If both or neither do, it goes to
  the name before it.
- If the line has only one name, an MIS ID anywhere on the line also counts.

## Step 6. Score each candidate

Start at 0 for every person who got a grade in step 4.

| Evidence | Fits the person | Does not fit |
|---|---|---|
| MIS ID | +10 | −10 |
| Role is a **job** (BK, MBK, CF, BM, CNRP, JCRP, VRP, SEW, SJY-MRP, FI CRP, CM) | +3 | **Ruled out** |
| Role is an **office** (अध्यक्ष, उपाध्यक्ष, सचिव, उपसचिव, कोषाध्यक्ष, सदस्य) | +3 | −3 only |
| Village | +3 | −3 |
| A repayment is written in her row | +3 if she has a loan | −3 if she has none |

Why is an office only −3 and not "ruled out"? Minutes say "आज की कार्यवाही अध्यक्ष
रीमा कुमारी": the chair for the day rotates, so the word अध्यक्ष does not prove her office.

## Step 7. Decide

1. **Keep a candidate** if she is not ruled out, and she has grade A, B or C, or grade D
   with a score of at least +3.
2. **Nobody kept:**
   - if someone with grade A, B or C was ruled out only by her role → **ASK**
     ("the name matches but the written role does not");
   - otherwise → **NEW**.
3. **One kept** → **that person**.
4. **Several kept** → if the top score is **at least 3 more** than the next → **the top
   person**. Otherwise → **ASK**.

## Step 8. Use the shape of the table (attendance and savings tables)

Do these after every row has been decided.

- **8a. The same row confirms itself.** The name column and the signature column
  normally name the same person. If one is ASK or NEW but the person found in the other
  column is among its candidates, take that person.
  *("अमिता कुमारी" in the name column, "अनीता कुमारी" signed beside it.)*
- **8b. One row per member.** If two rows carry the same name and there are exactly two
  such people, and one row has been identified, the other row is the other person.
  **Exception:** not if the evidence in that row scored her below zero.
- **8c. Flag, do not fix.** If the signature column names a different person from the
  name column, flag the row for review.

## Step 9. A role with no name

A job role followed by **दीदी**, **जी** or **के पास**, with no name next to it ("CM दीदी",
"600 CM के पास"):

- if exactly one person on the roster holds that role → **that person**;
- otherwise → **ASK**.

---

## The word lists (change these for another language)

| List | Words used in the demo |
|---|---|
| Surname / suffix words | देवी, कुमारी, कुमार, प्रसाद, रानी (and the English spellings) |
| Abbreviations | कु० = कुमारी or कुमार; प्र० = प्रसाद |
| Office roles | अध्यक्ष, उपाध्यक्ष, सचिव, उपसचिव, कोषाध्यक्ष, सदस्य |
| Job roles | BK, MBK, CF, BM, CNRP, JCRP, VRP, SEW, CM, SJY-MRP, FI CRP; two-word forms: SJY MRP, FI CRP, HNS CNRP, उप सचिव |
| Common words that are also names (never a name on their own) | पूजा, आरती, गीता, कंचन, मिनी, सीमा, रश्मि, प्रतिमा, संगीता, अशोक, आशा, किरण, सुमन, ममता, शांति, लक्ष्मी, ज्योति, पुष्पा, रेखा, सोनी, श्रीमती |
| Stop words (never part of a name) | सभी, दीदी, जो, हम, की, का, के, को, ने, से, में, और, बैंक, समूह, कुल, आज, श्री, बजे, दिन, समय, तारीख, माह, वर्ष, दिनांक, स्थान, BOD, SHG, CLF, VO, OB |

## The numbers, in one place

| Number | Used for |
|---|---|
| 0.8 | "Close": names (grade B), surnames, villages |
| 0.6 | "Weakly similar": the lower edge of grade D |
| +3 / −3 | Role, village, loan evidence |
| +10 / −10 | MIS ID |
| 3 | The lead the top candidate needs over the next one |

---

## Five worked examples (from the Nalanda pages)

1. **Two सुषमा कुमारी, one repayment.** Row 12 of the 8 Sep table has ₹7,000 + ₹460
   in the repayment columns.
   - The Sushma with a loan scores +3; the other scores −3. The lead is 6, so row 12 is
     the one with the loan.
   - Row 13 has the same name and no evidence. By step 8b it is the other Sushma.
2. **Two पिंकी देवी on the board.** One row says चौरासी, उपसचिव; the other says
   सकरपुरा, सदस्य.
   - In each row, village and role give the right Pinki +6 and the other −6.
3. **"BK सुनिता कुमारी".** Two सुनीता कुमारी are on the roster: a board member and the
   bookkeeper.
   - BK is a job role, so the board member is ruled out. The bookkeeper is the only one
     left.
4. **"C.M सीमा देवी".** The only सीमा देवी on the roster is a CNRP.
   - CM is a job role that does not fit, so she is ruled out. Her name was grade A, so
     the answer is **ASK**.
5. **"सफाई कर्मी रीना देवी".** The nearest roster name is रिता देवी, closeness 0.67:
   grade D.
   - There is no evidence for रिता, so she is not kept. The answer is **NEW**.

## What these rules cannot do

- **Separate same-name members when the page holds no evidence at all.** The two
  गुड़िया कुमारी are always ASK. The fix is upstream: write the LokOS member code on the
  register, or say it in the read-back.
- **Read the handwriting.** The rules start from text. Getting good text off the photo
  is a separate problem.
