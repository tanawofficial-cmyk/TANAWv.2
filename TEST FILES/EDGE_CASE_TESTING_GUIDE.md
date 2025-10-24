# 🧪 TANAW Multi-Domain Bar Charts - Edge Case Testing Guide

## 📋 Overview
Testing 5 critical edge cases to validate system robustness before proceeding to line charts.

---

## Test 1: Mixed Language/Abbreviated Columns 🌍

**File:** `test1_abbreviated.csv`

### **Challenge:**
- Abbreviated column names: `Prod`, `Vnts`, `Rgn`, `Fch`, `Cntd`, `Prc`
- Mixed Spanish: "Norte", "Sur", "Este", "Oeste"
- Spanish product names: "Teclado", "Auriculares", "Micrófono"

### **Expected OpenAI Mapping:**
```
Prod  → Product   (abbreviated product)
Vnts  → Sales     (abbreviated "Ventas" = Sales in Spanish)
Rgn   → Region    (abbreviated region)
Fch   → Date      (abbreviated "Fecha" = Date in Spanish)
Cntd  → Quantity  (abbreviated "Cantidad" = Quantity)
Prc   → Sales     (Price - could be ignored or mapped to Sales)
```

### **Expected Domain:** Sales (Spanish retail data)

### **Expected Charts:**
- ✅ Product Performance (Prod vs Vnts)
- ✅ Regional Sales (Rgn vs Vnts)

### **Success Criteria:**
- [ ] OpenAI correctly interprets abbreviated names
- [ ] Domain detection: SALES
- [ ] 2 bar charts generated with Spanish region names
- [ ] Chart labels in English (mapped names)

---

## Test 2: Business-Specific Jargon 💼

**File:** `test2_business_jargon.csv`

### **Challenge:**
- Corporate codes: `BU_ID`, `GL_Balance`, `Cost_Center`, `FY_Period`
- Accounting terminology: "GL" (General Ledger), "Accrual", "FY" (Fiscal Year)
- Complex identifiers: "MKTG-001", "CC-100-Marketing"

### **Expected OpenAI Mapping:**
```
BU_ID           → Product  (Business Unit ID = entity identifier)
GL_Balance      → Sales    (General Ledger Balance = monetary value)
Cost_Center     → Region   (Cost Center = grouping/department)
FY_Period       → Date     (Fiscal Year Period = temporal)
Transaction_Amt → Sales    (Transaction Amount = monetary value)
Accrual_Amt     → Ignore   (or could map to Sales)
```

### **Expected Domain:** Finance (Corporate accounting data)

### **Expected Charts:**
- ✅ Expense Distribution (Cost_Center vs Transaction_Amt)
- ✅ Possibly: BU Performance (BU_ID vs GL_Balance)

### **Success Criteria:**
- [ ] OpenAI understands business/accounting jargon
- [ ] Domain detection: FINANCE
- [ ] 1-2 bar charts generated
- [ ] Correct handling of "GL_Balance" vs "Transaction_Amt" (picks one)
- [ ] Chart labels readable ("Cost Center" not "CC-100-...")

---

## Test 3: No Headers (Numeric Column Names) 🔢

**File:** `test3_no_headers.csv`

### **Challenge:**
- NO header row - pandas will use first data row or create Column_0, Column_1, etc.
- OpenAI receives: `0`, `1`, `2`, `3`, `4` or similar
- Must infer from data values, not column names

### **Expected Behavior:**
This is the **HARDEST** test case!

**Option A: System detects no headers**
```
Pandas auto-generates: Column_0, Column_1, Column_2...
OpenAI sees: "Column_0", "Column_1", "Column_2"...
OpenAI can't map meaningfully → Maps based on data type inference
```

**Option B: System uses first row as header**
```
Header becomes: "Widget-A", "25000", "North", "2024-01-15", "150"
OpenAI sees weird headers that look like data
OpenAI should detect this is wrong
```

### **Expected Domain:** Unknown or Sales (if it can infer)

### **Success Criteria:**
- [ ] System doesn't crash
- [ ] Either: Shows error "No proper headers detected"
- [ ] Or: Attempts to infer from data types and generates basic charts
- [ ] Frontend handles gracefully (doesn't show broken charts)

**⚠️ This test might FAIL - that's OK! It shows us what to fix.**

---

## Test 4: Duplicate/Similar Columns 🔄

**File:** `test4_duplicate_columns.csv`

### **Challenge:**
- Multiple sales columns: `Total_Sales`, `Net_Sales`, `Gross_Sales`, `Sales_Tax`
- OpenAI must pick the BEST one
- System must not create 4 identical charts

### **Expected OpenAI Mapping:**
```
Product_Name    → Product
Total_Sales     → Sales     (BEST choice - most comprehensive)
Net_Sales       → Ignore    (alternative sales metric)
Gross_Sales     → Ignore    (alternative sales metric)
Sales_Tax       → Ignore    (derivative data)
Region          → Region
Date            → Date
Quantity_Sold   → Quantity
Unit_Price      → Ignore    (can be derived)
```

**OpenAI Prompt Rule #5:** "Map only ONE column per canonical type"

### **Expected Domain:** Sales

### **Expected Charts:**
- ✅ Product Performance (Product_Name vs Total_Sales)
- ✅ Regional Sales (Region vs Total_Sales)
- ❌ Should NOT generate 3 separate sales charts

### **Success Criteria:**
- [ ] OpenAI picks only ONE sales column (Total_Sales)
- [ ] Only 2 bar charts generated (not 6-8)
- [ ] No duplicate charts with slightly different values
- [ ] Chart uses "Total_Sales" not "Net_Sales" or "Gross_Sales"

---

## Test 5: Missing Critical Columns ❌

**File:** `test5_missing_columns.csv`

### **Challenge:**
- Has `Product_Name`, `Description`, `Category`
- NO numeric columns (Sales, Quantity, Price, etc.)
- NO date column
- Only has descriptive text and measurements (Weight, Dimensions)

### **Expected OpenAI Mapping:**
```
Product_Name → Product
Description  → Ignore  (text description)
Category     → Region  (could be grouping)
Color        → Ignore
Weight_KG    → Quantity? (numeric, but not really "quantity")
Dimensions_CM → Ignore
```

### **Expected Domain:** Unknown or Sales (but missing key data)

### **Expected Charts:**
- ❌ NO charts generated
- System should detect: "Cannot generate analytics - missing numeric value columns"

### **Success Criteria:**
- [ ] System detects missing critical columns
- [ ] Shows friendly error: "This dataset doesn't contain sales, revenue, or quantity data"
- [ ] Suggests: "Please upload a dataset with numeric values to analyze"
- [ ] Frontend shows helpful message (not a crash or blank page)
- [ ] Readiness check reports unavailable analytics

---

## 📊 Testing Checklist

### Before Testing:
- [ ] Backend server running (`python app_clean.py`)
- [ ] Frontend running (`npm start`)
- [ ] OpenAI API key configured
- [ ] All 5 test files in `TEST FILES/` folder

### For Each Test:
1. [ ] Upload CSV file
2. [ ] Check console for domain detection
3. [ ] Check console for OpenAI mapping output
4. [ ] Verify charts generated (or error shown)
5. [ ] Check chart labels are correct
6. [ ] Note any errors or unexpected behavior

### After All Tests:
- [ ] Document which tests passed
- [ ] Document which tests failed
- [ ] Identify patterns in failures
- [ ] Decide if failures are acceptable or need fixes

---

## 🎯 Expected Overall Results

### **Should Pass (High Confidence):**
- ✅ Test 1: Abbreviated columns (OpenAI is good at this)
- ✅ Test 2: Business jargon (OpenAI knows corporate terminology)
- ✅ Test 4: Duplicate columns (Our prompt explicitly handles this)

### **Might Struggle (Medium Confidence):**
- ⚠️ Test 3: No headers (Very hard problem, acceptable to fail)

### **Should Fail Gracefully:**
- ✅ Test 5: Missing columns (Should show clear error, not crash)

---

## 🐛 Common Issues to Watch For

### 1. **Mapping Issues:**
- OpenAI maps wrong column
- OpenAI ignores important columns
- OpenAI maps multiple columns to same type

### 2. **Chart Generation Issues:**
- Charts generated but show wrong data
- No charts generated despite having data
- Too many duplicate charts

### 3. **Frontend Issues:**
- Chart labels show raw column names instead of friendly names
- Charts render blank
- Error messages not user-friendly

### 4. **Error Handling Issues:**
- System crashes instead of showing error
- No feedback to user about what went wrong
- Errors show technical details instead of helpful messages

---

## 📝 Testing Log Template

```
TEST: [Test Number and Name]
DATE: [Date and Time]
TESTER: [Your Name]

UPLOAD:
- File uploaded: ✅/❌
- File parsed: ✅/❌

MAPPING:
- Domain detected: [Domain Name] ([Confidence %])
- Columns mapped:
  - [Original] → [Canonical]
  - [Original] → [Canonical]
  ...

CHARTS:
- Charts generated: [Number]
- Chart 1: [Title] - ✅/❌
- Chart 2: [Title] - ✅/❌

ISSUES:
- [List any issues found]

NOTES:
- [Any additional observations]

RESULT: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL
```

---

## 🚀 Next Steps After Testing

1. **All Pass:** Proceed to Line Charts! 🎉
2. **Some Fail:** Decide which failures are acceptable vs critical
3. **Critical Failures:** Fix before proceeding
4. **Nice-to-Have Failures:** Document and fix later

Good luck with testing! 🧪✨

