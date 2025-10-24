# 🧪 FINANCE LINE CHART TESTING GUIDE

## **📊 Test Scenarios for Finance Domain Line Charts**

### **🎯 Expected Results Summary:**

| Test File | Expected Charts | Description |
|-----------|----------------|-------------|
| **TEST 1** | 6 charts (3 bar, 3 line) | Standard Finance data with all columns |
| **TEST 2** | 6 charts (3 bar, 3 line) | Ambiguous column names (Transaction_Date, Total_Revenue) |
| **TEST 3** | 4 charts (2 bar, 2 line) | Profit-focused data (EBIT, Earnings) |
| **TEST 4** | 4 charts (2 bar, 2 line) | Cash Flow-focused data |
| **TEST 5** | 8 charts (4 bar, 4 line) | Mixed domains (Sales + Finance) |
| **TEST 6** | 2 charts (2 bar only) | Insufficient data for line charts |
| **TEST 7** | 3 charts (3 bar only) | No date column - no line charts |
| **TEST 8** | 6 charts (3 bar, 3 line) | Negative profit values |
| **TEST 9** | 6 charts (3 bar, 3 line) | Spanish column names |
| **TEST 10** | 6 charts (3 bar, 3 line) | Dense monthly data |

---

## **📋 Detailed Test Cases:**

### **TEST 1: Standard Finance Data**
**File:** `finance_test1_standard_revenue.csv`
**Columns:** `Date`, `Revenue`, `Profit`, `Cash_Flow`, `Expense_Category`, `Expense_Amount`
**Expected Result:** 6 charts
- **Bar Charts (3):** Expense Distribution, Profit Margin by Department, Cash Flow by Account
- **Line Charts (3):** Revenue Over Time, Profit Trend, Cash Flow Analysis

### **TEST 2: Ambiguous Column Names**
**File:** `finance_test2_ambiguous_columns.csv`
**Columns:** `Transaction_Date`, `Total_Revenue`, `Net_Profit`, `Operating_Cash_Flow`, `Expense_Type`, `Amount`
**Expected Result:** 6 charts
- **Bar Charts (3):** Expense Distribution, Profit Margin by Department, Cash Flow by Account
- **Line Charts (3):** Revenue Over Time, Profit Trend, Cash Flow Analysis
**Test Focus:** Column name flexibility and detection

### **TEST 3: Profit-Focused Data**
**File:** `finance_test3_profit_focus.csv`
**Columns:** `Period`, `EBIT`, `Earnings`, `Free_Cash_Flow`, `Department`, `Margin_Percentage`
**Expected Result:** 4 charts
- **Bar Charts (2):** Profit Margin by Department, Cash Flow by Department
- **Line Charts (2):** Profit Trend (EBIT), Cash Flow Analysis (Free_Cash_Flow)
**Test Focus:** EBIT and Earnings detection for profit charts

### **TEST 4: Cash Flow-Focused Data**
**File:** `finance_test4_cashflow_focus.csv`
**Columns:** `Date`, `Cash_Flow`, `Net_Cash_Flow`, `Operating_Cash_Flow`, `Account_Type`, `Balance`
**Expected Result:** 4 charts
- **Bar Charts (2):** Cash Flow by Account Type, Balance by Account Type
- **Line Charts (2):** Cash Flow Analysis, Revenue Over Time (if Revenue detected)
**Test Focus:** Multiple cash flow column detection

### **TEST 5: Mixed Domains**
**File:** `finance_test5_mixed_domains.csv`
**Columns:** `Date`, `Sales_Amount`, `Revenue`, `Profit`, `Cash_Flow`, `Product`, `Region`, `Expense_Category`, `Expense_Amount`
**Expected Result:** 8 charts
- **Bar Charts (4):** Product Performance, Regional Sales, Expense Distribution, Profit Margin
- **Line Charts (4):** Sales Over Time, Revenue Over Time, Profit Trend, Cash Flow Analysis
**Test Focus:** Multi-domain chart generation

### **TEST 6: Insufficient Data**
**File:** `finance_test6_insufficient_data.csv`
**Columns:** `Date`, `Revenue`
**Expected Result:** 2 charts
- **Bar Charts (2):** Revenue Distribution, Revenue by Category
- **Line Charts (0):** Insufficient data points for time series
**Test Focus:** Graceful handling of insufficient data

### **TEST 7: No Date Column**
**File:** `finance_test7_no_date.csv`
**Columns:** `Revenue`, `Profit`, `Cash_Flow`, `Department`, `Amount`
**Expected Result:** 3 charts
- **Bar Charts (3):** Revenue Distribution, Profit by Department, Cash Flow by Department
- **Line Charts (0):** No date column available
**Test Focus:** Date column requirement for line charts

### **TEST 8: Negative Values**
**File:** `finance_test8_negative_values.csv`
**Columns:** `Date`, `Revenue`, `Profit`, `Cash_Flow`, `Expense_Category`, `Expense_Amount`
**Expected Result:** 6 charts
- **Bar Charts (3):** Expense Distribution, Profit Margin, Cash Flow Analysis
- **Line Charts (3):** Revenue Over Time, Profit Trend (with negative values), Cash Flow Analysis
**Test Focus:** Handling negative profit values

### **TEST 9: Spanish Column Names**
**File:** `finance_test9_spanish_columns.csv`
**Columns:** `Fecha`, `Ingresos`, `Ganancia`, `Flujo_Efectivo`, `Categoria_Gasto`, `Monto`
**Expected Result:** 6 charts
- **Bar Charts (3):** Expense Distribution, Profit Margin, Cash Flow Analysis
- **Line Charts (3):** Revenue Over Time, Profit Trend, Cash Flow Analysis
**Test Focus:** International column name support

### **TEST 10: Dense Monthly Data**
**File:** `finance_test10_dense_monthly.csv`
**Columns:** `Date`, `Monthly_Revenue`, `Net_Income`, `Free_Cash_Flow`, `Division`, `Profit_Margin`
**Expected Result:** 6 charts
- **Bar Charts (3):** Revenue Distribution, Profit Margin by Division, Cash Flow by Division
- **Line Charts (3):** Revenue Over Time, Profit Trend, Cash Flow Analysis
**Test Focus:** Performance with dense data and monthly patterns

---

## **🔍 Key Testing Points:**

### **1. Column Detection Flexibility**
- ✅ Standard names: `Date`, `Revenue`, `Profit`, `Cash_Flow`
- ✅ Variations: `Transaction_Date`, `Total_Revenue`, `Net_Profit`, `Operating_Cash_Flow`
- ✅ Financial terms: `EBIT`, `Earnings`, `Free_Cash_Flow`
- ✅ International: `Fecha`, `Ingresos`, `Ganancia`, `Flujo_Efectivo`

### **2. Chart Type Generation**
- ✅ **Revenue Over Time:** When Date + Revenue columns exist
- ✅ **Profit Trend:** When Date + Profit columns exist
- ✅ **Cash Flow Analysis:** When Date + Cash_Flow columns exist
- ✅ **Sales Summary:** When Date + Sales columns exist (mixed domains)

### **3. Edge Case Handling**
- ✅ **Insufficient Data:** < 2 rows → No line charts
- ✅ **No Date Column:** Only bar charts generated
- ✅ **Negative Values:** Charts still generated with negative data
- ✅ **Mixed Domains:** All applicable charts generated

### **4. Expected Chart Counts**
- **Minimum:** 2 charts (bar only, no date)
- **Standard:** 6 charts (3 bar + 3 line)
- **Maximum:** 8 charts (4 bar + 4 line, mixed domains)

---

## **🚀 Testing Instructions:**

1. **Upload each test file** to the TANAW system
2. **Verify chart count** matches expected results
3. **Check chart types** (bar vs line) are correct
4. **Validate column detection** works with ambiguous names
5. **Test edge cases** (insufficient data, no date, negative values)
6. **Confirm international support** (Spanish column names)

---

## **✅ Success Criteria:**

- **All 10 test files** should upload successfully
- **Chart counts** should match expected results
- **Line charts** should render properly in frontend
- **Column detection** should work with various naming conventions
- **Edge cases** should be handled gracefully without errors
- **Mixed domains** should generate maximum possible charts

---

## **🔧 Debugging Tips:**

If charts are missing:
1. Check terminal logs for column detection messages
2. Verify date column is properly detected
3. Confirm numeric columns have sufficient valid data
4. Check for column name variations in detection logic

If line charts don't render:
1. Verify frontend can handle new chart types
2. Check data structure matches expected format
3. Confirm chart type is set to "line"
