# 📦 INVENTORY TURNOVER LINE CHART - TEST SCENARIOS

## 🎯 Test Objective
Test the flexibility and robustness of the Inventory Turnover line chart generator with various column naming conventions and data structures.

---

## 📋 Test Cases

### **TEST 1: Standard Column Names**
**File**: `INVENTORY_TURNOVER_TEST_1.csv`

**Columns**:
- `Date` (standard date column)
- `Turnover_Rate` (standard turnover rate)
- `Product` (product identifier)
- `Stock_Level` (stock quantity - should NOT trigger this chart)

**Expected Result**:
- ✅ **1 Line Chart**: "Inventory Turnover"
  - X-axis: Date (2024-01-01 to 2024-01-15)
  - Y-axis: Turnover Rate (5.1 to 6.5)
  - Chart type: `line`
  - Description: "Measure stock movement speed over time"

**Also Expected** (from other generators):
- ✅ **0-1 Bar Charts**: Stock Level Overview (if Product + Stock_Level detected)

**Key Points**:
- Should NOT confuse `Stock_Level` with `Turnover_Rate`
- Line chart should use `Turnover_Rate`, NOT `Stock_Level`

---

### **TEST 2: Alternative Naming (InventoryTurnover)**
**File**: `INVENTORY_TURNOVER_TEST_2.csv`

**Columns**:
- `Transaction_Date` (alternative date column name)
- `InventoryTurnover` (compound word, no underscore)
- `SKU` (product code)
- `Quantity` (stock quantity)

**Expected Result**:
- ✅ **1 Line Chart**: "Inventory Turnover"
  - X-axis: Transaction_Date (2024-02-01 to 2024-02-10)
  - Y-axis: Turnover Rate (4.8 to 5.7)
  - Detects `InventoryTurnover` as turnover column
  - Detects `Transaction_Date` as date column

**Key Points**:
- Tests compound word detection
- Alternative date column name

---

### **TEST 3: Spanish/Alternative Names (ITR abbreviation)**
**File**: `INVENTORY_TURNOVER_TEST_3.csv`

**Columns**:
- `Fecha` (Spanish for "Date")
- `ITR` (Inventory Turnover Ratio abbreviation)
- `Producto` (Spanish for "Product")
- `Inventario` (Spanish for "Inventory")

**Expected Result**:
- ✅ **1 Line Chart**: "Inventory Turnover"
  - X-axis: Fecha (2024-03-01 to 2024-03-12)
  - Y-axis: Turnover Rate (3.5 to 4.6)
  - Detects `ITR` as turnover column
  - Detects `Fecha` as date column

**Key Points**:
- Tests abbreviation detection (ITR)
- Tests Spanish column names
- International compatibility

---

### **TEST 4: Period-Based (Quarterly) + Turn_Rate**
**File**: `INVENTORY_TURNOVER_TEST_4.csv`

**Columns**:
- `Period` (quarterly periods: 2024-Q1, Q2, Q3, Q4)
- `Turn_Rate` (alternative turnover rate name)
- `Item_Code` (product identifier)
- `On_Hand` (stock on hand)

**Expected Result**:
- ✅ **1 Line Chart**: "Inventory Turnover"
  - X-axis: Period (Q1 to Q4)
  - Y-axis: Turnover Rate (7.1 to 8.1)
  - Detects `Turn_Rate` as turnover column
  - Detects `Period` as date column

**Key Points**:
- Tests period-based dates (quarters)
- Alternative column name: `Turn_Rate`
- Alternative stock name: `On_Hand`

---

### **TEST 5: DateTime + Rotation_Rate**
**File**: `INVENTORY_TURNOVER_TEST_5.csv`

**Columns**:
- `DateTime` (full timestamp with time component)
- `Rotation_Rate` (alternative name for turnover)
- `Stock_Item` (product identifier)
- `Available` (available stock)

**Expected Result**:
- ✅ **1 Line Chart**: "Inventory Turnover"
  - X-axis: DateTime (2024-04-01 to 2024-04-10)
  - Y-axis: Turnover Rate (6.8 to 7.7)
  - Detects `Rotation_Rate` as turnover column
  - Detects `DateTime` as date column

**Key Points**:
- Tests full timestamp detection
- Alternative term: `Rotation_Rate`
- Tests time component in dates

---

## 🔍 What We're Testing

### **Column Name Flexibility**
- ✅ Standard: `Turnover_Rate`
- ✅ Compound: `InventoryTurnover`
- ✅ Abbreviation: `ITR`, `ITO`
- ✅ Alternative: `Turn_Rate`, `Rotation_Rate`
- ✅ Spanish: `Fecha` (Date)

### **Date Column Variations**
- ✅ `Date`
- ✅ `Transaction_Date`
- ✅ `Fecha`
- ✅ `Period` (quarterly)
- ✅ `DateTime` (with time)

### **Anti-Duplication**
- ✅ Should NOT confuse `Stock_Level` / `Quantity` / `On_Hand` with `Turnover_Rate`
- ✅ Should NOT generate duplicate charts for same data
- ✅ Should work alongside Stock Level Overview bar charts

### **Edge Cases**
- ✅ Different date formats
- ✅ Quarterly periods
- ✅ Timestamps with time component
- ✅ Various numeric ranges (3.5-8.1)

---

## 🎯 Success Criteria

### **For Each Test**:
1. ✅ Generates exactly **1 Inventory Turnover line chart**
2. ✅ Correctly identifies Date column
3. ✅ Correctly identifies Turnover Rate column
4. ✅ Does NOT use Stock/Quantity columns for turnover
5. ✅ Chart has proper title: "Inventory Turnover"
6. ✅ Chart has proper description: "Measure stock movement speed over time"
7. ✅ Y-axis labeled: "Turnover Rate"
8. ✅ No duplicate charts generated

### **Overall System**:
1. ✅ No confusion with Stock Level Overview bar charts
2. ✅ Works alongside other chart types
3. ✅ Handles international naming conventions
4. ✅ Handles abbreviations and alternative terms
5. ✅ Robust error handling for edge cases

---

## 📊 Expected Chart Count Summary

| Test File | Inventory Turnover (Line) | Stock Level (Bar) | Total Expected |
|-----------|---------------------------|-------------------|----------------|
| TEST 1    | 1                         | 0-1               | 1-2            |
| TEST 2    | 1                         | 0-1               | 1-2            |
| TEST 3    | 1                         | 0-1               | 1-2            |
| TEST 4    | 1                         | 0-1               | 1-2            |
| TEST 5    | 1                         | 0-1               | 1-2            |

**Note**: Stock Level bar charts may or may not appear depending on whether the system detects valid Product + Stock columns.

---

## 🚨 What Would Indicate a Problem

### **Red Flags**:
- ❌ No Inventory Turnover chart generated (should be 1)
- ❌ Multiple Inventory Turnover charts for same dataset
- ❌ Using `Stock_Level` / `Quantity` instead of `Turnover_Rate`
- ❌ Chart showing static stock levels instead of turnover trend
- ❌ Date column not detected
- ❌ Chart content is duplicate of Stock Level Overview

### **System Errors**:
- ❌ JSON serialization errors
- ❌ Column mapping failures
- ❌ Type conversion errors
- ❌ Frontend rendering issues

---

## ✅ Post-Test Validation

After running all 5 tests, verify:

1. **Uniqueness**: Each chart is unique (no duplicate content)
2. **Correctness**: Turnover values match source data
3. **Labels**: All labels are domain-appropriate
4. **Insights**: AI insights are relevant to inventory turnover
5. **Rendering**: Charts display correctly in frontend
6. **Performance**: Processing time is reasonable (<5 seconds per file)

---

**Status**: Ready for testing! 🚀

