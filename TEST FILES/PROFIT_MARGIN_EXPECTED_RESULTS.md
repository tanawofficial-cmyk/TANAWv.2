# 💰 PROFIT MARGIN CALCULATION - TEST SCENARIOS

## 🎯 Test Objective
Test the Profit Margin calculation with two data scenarios:
1. Dataset with existing Margin% column (use directly)
2. Dataset with Profit + Revenue columns (calculate margin)

---

## 📋 Test Cases

### **TEST 1: Existing Margin Column**
**File**: `PROFIT_MARGIN_TEST_1_WITH_MARGIN.csv`

**Columns**:
- `Product` (item identifier)
- `Margin_%` (existing profit margin percentage)
- `Revenue` (revenue values)
- `Sales` (sales values)

**Expected Behavior**:
- ✅ **LEVEL 1**: Use existing `Margin_%` column
- ✅ **NO calculation** needed
- ✅ Show margin values as-is

**Expected Result**:
```
Chart: Profit Margin by Product
X-Axis: Product
Y-Axis: Profit Margin (%)

Data:
- Widget C: 32.1%
- Widget E: 28.3%
- Widget A: 25.5%
- Widget B: 18.2%
- Widget D: 15.8%

Order: Highest margin first (descending)
```

**Console Logs**:
```
✅ Using existing margin column: Margin_%
💰 Generated margin data for 5 items
💰 Highest margin: Widget C with 32.10%
```

---

### **TEST 2: Calculate from Profit + Revenue**
**File**: `PROFIT_MARGIN_TEST_2_CALCULATE.csv`

**Columns**:
- `Product` (item identifier)
- `Profit` (profit values)
- `Revenue` (revenue values)
- `Date` (date for time-series)

**Expected Behavior**:
- ✅ **LEVEL 2**: Calculate margin from components
- ✅ **Formula**: `(Profit / Revenue) * 100`
- ✅ **Use LAST** values per product (most recent)

**Manual Calculation** (Most Recent Values):
```
Widget A (2024-01-06): (2800 / 11000) * 100 = 25.45%
Widget B (2024-01-07): (1800 / 9000) * 100 = 20.00%
Widget C (2024-01-08): (4200 / 13000) * 100 = 32.31%
Widget D (2024-01-04): (950 / 6000) * 100 = 15.83%
Widget E (2024-01-05): (2700 / 9000) * 100 = 30.00%
```

**Expected Result**:
```
Chart: Profit Margin by Product
X-Axis: Product
Y-Axis: Profit Margin (%)

Data (calculated, most recent):
- Widget C: 32.31%
- Widget E: 30.00%
- Widget A: 25.45%
- Widget B: 20.00%
- Widget D: 15.83%

Order: Highest margin first (descending)
```

**Console Logs**:
```
🧮 Calculating margin from Profit and Revenue
   Formula: (Profit / Revenue) * 100
✅ Calculated profit margin for 5 items
💰 Generated margin data for 5 items
💰 Highest margin: Widget C with 32.31%
```

**Meta Data**:
```
{
  "calculated": true,  ← Indicates this was calculated, not from column
  "top_item": "Widget C",
  "top_margin": 32.31,
  "average_margin": 24.72
}
```

---

## 🔍 What We're Testing

### **Level 1: Direct Margin Column**
- ✅ Uses `Margin_%` if it exists
- ✅ No calculation needed
- ✅ Faster processing
- ✅ Respects user's pre-calculated margins

### **Level 2: Component-Based Calculation**
- ✅ Detects `Profit` and `Revenue` columns
- ✅ Calculates: `(Profit / Revenue) * 100`
- ✅ Uses **LAST** values per product (most recent)
- ✅ Handles division by zero (Revenue = 0)
- ✅ Groups by Product first, then calculates

### **Anti-Duplication**
- ✅ Won't generate multiple Profit Margin charts
- ✅ Prefers existing margin column over calculation
- ✅ Only calculates if margin column doesn't exist

### **Edge Cases**
- ✅ Division by zero (Revenue = 0) → Margin = 0%
- ✅ Multiple rows per product → Use LAST (most recent)
- ✅ Missing data → Handled by dropna()

---

## 🎯 Success Criteria

### **For TEST 1 (Existing Margin)**:
1. ✅ Uses `Margin_%` column directly
2. ✅ NO calculation performed
3. ✅ Console shows: "Using existing margin column"
4. ✅ `meta.calculated = false` (or undefined)
5. ✅ Values match source data exactly

### **For TEST 2 (Calculate Margin)**:
1. ✅ Detects `Profit` and `Revenue` columns
2. ✅ Performs calculation: `(Profit / Revenue) * 100`
3. ✅ Uses LAST (most recent) values per product
4. ✅ Console shows: "Calculating margin from Profit and Revenue"
5. ✅ `meta.calculated = true`
6. ✅ Calculated values match manual calculation

### **Overall**:
1. ✅ Both tests generate 1 Profit Margin chart each
2. ✅ Charts are sorted by margin (highest first)
3. ✅ Y-axis labeled "Profit Margin (%)"
4. ✅ X-axis labeled "Product"
5. ✅ No errors or warnings
6. ✅ Proper division by zero handling

---

## 📊 Expected Chart Count Summary

| Test File | Profit Margin (Bar) | Other Charts | Total Expected |
|-----------|---------------------|--------------|----------------|
| TEST 1    | 1 (from column)     | 0-2          | 1-3            |
| TEST 2    | 1 (calculated)      | 1-3          | 2-4            |

**Note**: Other charts (Product Performance, Sales Summary, etc.) may appear depending on detected columns.

---

## 🚨 What Would Indicate a Problem

### **Red Flags**:
- ❌ No Profit Margin chart when data is available
- ❌ Calculated margin doesn't match manual calculation
- ❌ Using average margin instead of last
- ❌ Division by zero errors
- ❌ Multiple Profit Margin charts for same dataset

### **Validation Steps**:
1. **TEST 1**: Verify margin values = source values (25.5, 18.2, 32.1, etc.)
2. **TEST 2**: Manually verify: Widget C = (4200/13000)*100 = 32.31%
3. **Check meta.calculated**: Should be true for TEST 2, false/undefined for TEST 1
4. **Check console logs**: Should show correct detection level

---

**Status**: Ready for testing! 🚀

