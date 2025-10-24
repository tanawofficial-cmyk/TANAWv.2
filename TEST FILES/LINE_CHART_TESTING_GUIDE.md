# 📈 TANAW Line Chart Testing Guide - Sales Domain

## 🎯 Testing Objective
Validate that line charts work correctly across various scenarios while bar charts continue to function properly.

---

## 📋 Test Suite Overview

| # | Test Name | File | Charts Expected | Purpose |
|---|-----------|------|-----------------|---------|
| 1 | Standard Time Series | `line_test1_standard_timeseries.csv` | 2 Bar + 1 Line | Baseline test |
| 2 | Sparse Dates | `line_test2_sparse_dates.csv` | 2 Bar + 1 Line | Irregular intervals |
| 3 | Dense Daily Data | `line_test3_dense_daily.csv` | 2 Bar + 1 Line | Large dataset (400 days) |
| 4 | Duplicate Dates | `line_test4_duplicate_dates.csv` | 2 Bar + 1 Line | Date aggregation |
| 5 | No Date Column | `line_test5_no_date.csv` | 2 Bar Only | Error handling |

---

## 🧪 TEST 1: Standard Sales Time Series

**File:** `line_test1_standard_timeseries.csv`

### **Dataset Characteristics:**
- 20 rows (20 days of data)
- Columns: `ProductName`, `SalesDate`, `AmountSold`, `Territory`, `QtySold`
- Clean daily data (Jan 1-20, 2024)
- Multiple products, multiple regions

### **Expected OpenAI Mapping:**
```
ProductName → Product
SalesDate   → Date
AmountSold  → Sales
Territory   → Region
QtySold     → Quantity
```

### **Expected Domain:** SALES

### **Expected Charts (Total: 3):**

#### **Bar Chart 1: Product Performance**
- X-axis: Product names (Laptop, Mouse, Keyboard, etc.)
- Y-axis: Total sales per product
- Should show ~15 different products

#### **Bar Chart 2: Regional Sales**
- X-axis: Territories (North, South, East, West)
- Y-axis: Total sales per region
- Should show 4 regions

#### **Line Chart 1: Sales Over Time** ← NEW!
- X-axis: Dates (Jan 1 - Jan 20)
- Y-axis: Daily sales amounts
- Should show ~20 data points
- Trend: Should calculate if increasing/decreasing

### **Success Criteria:**
- [ ] All 3 charts render correctly
- [ ] Line chart X-axis shows dates properly formatted
- [ ] Line chart shows smooth trend line
- [ ] Tooltip shows date + sales amount on hover
- [ ] Chart title is "AmountSold Over Time" or similar
- [ ] Y-axis label includes units (₱)
- [ ] No console errors
- [ ] Bar charts still work (not broken by line chart addition)

---

## 🧪 TEST 2: Sparse/Irregular Dates

**File:** `line_test2_sparse_dates.csv`

### **Dataset Characteristics:**
- 15 rows spread over 10 months
- Columns: `Item`, `TransactionDt`, `Val`, `Loc`, `Cnt`
- Irregular gaps (Jan 5, Jan 18, Feb 2, Feb 21, etc.)
- Tests line chart with sparse data

### **Expected OpenAI Mapping:**
```
Item          → Product
TransactionDt → Date
Val           → Sales
Loc           → Region
Cnt           → Quantity
```

### **Expected Charts (Total: 3):**
- Bar: Item Performance
- Bar: Location Distribution
- Line: Value Over Time with gaps

### **Success Criteria:**
- [ ] Line chart handles irregular date spacing
- [ ] X-axis dates are not evenly spaced (shows actual gaps)
- [ ] Line connects data points across gaps
- [ ] No interpolation of missing dates
- [ ] Trend calculation works with sparse data
- [ ] Bar charts aggregate correctly

---

## 🧪 TEST 3: Dense Daily Data (400 Days)

**File:** `line_test3_dense_daily.csv`

### **Dataset Characteristics:**
- **400 rows** (400 days of data - over 1 year)
- Columns: `SaleDate`, `ProductID`, `DailySales`, `SalesRegion`, `UnitsSold`
- Daily data from Jan 1, 2024 to Feb 4, 2025
- **Tests auto-sampling feature** (should trigger at >365 points)

### **Expected OpenAI Mapping:**
```
SaleDate     → Date
ProductID    → Product
DailySales   → Sales
SalesRegion  → Region
UnitsSold    → Quantity
```

### **Expected Charts (Total: 3):**
- Bar: Product Performance (5 products)
- Bar: Regional Sales (4 regions)
- Line: Sales Over Time **SAMPLED TO WEEKLY**

### **Success Criteria:**
- [ ] System detects >365 data points
- [ ] Line chart auto-samples to weekly data
- [ ] Console shows: "⚠️ Too many data points (400) - sampling for performance"
- [ ] X-axis shows ~57 weekly points instead of 400 daily
- [ ] Chart still renders smoothly (no lag)
- [ ] Trend calculation accurate despite sampling
- [ ] Meta data shows original data_points: 400

---

## 🧪 TEST 4: Duplicate Dates (Aggregation Test)

**File:** `line_test4_duplicate_dates.csv`

### **Dataset Characteristics:**
- 24 rows (4-6 transactions per day over 5 days)
- Columns: `Prod`, `Dt`, `Amt`, `Rgn`, `Qty`
- Same date appears multiple times (multiple sales per day)
- Tests groupby aggregation

### **Expected OpenAI Mapping:**
```
Prod → Product
Dt   → Date
Amt  → Sales
Rgn  → Region
Qty  → Quantity
```

### **Expected Charts (Total: 3):**
- Bar: Product Performance
- Bar: Regional Sales
- Line: Sales Over Time (5 aggregated points)

### **Expected Behavior:**
```
Raw Data:
2024-01-15: 15000, 2500, 4500, 22000  (4 transactions)

Aggregated:
2024-01-15: 44000  (sum of all transactions that day)
```

### **Success Criteria:**
- [ ] Line chart shows 5 data points (not 24)
- [ ] Each point is sum of all transactions that day
- [ ] No duplicate dates on X-axis
- [ ] Bar charts show all products/regions correctly
- [ ] Console shows groupby operation
- [ ] Total sales matches bar chart totals

---

## 🧪 TEST 5: No Date Column (Graceful Degradation)

**File:** `line_test5_no_date.csv`

### **Dataset Characteristics:**
- 15 rows
- Columns: `ProductCode`, `SalesValue`, `Branch`, `OrderQty`, `CustomerType`
- **NO date column at all**
- Should only generate bar charts

### **Expected OpenAI Mapping:**
```
ProductCode  → Product
SalesValue   → Sales
Branch       → Region
OrderQty     → Quantity
CustomerType → Ignore (or Region)
```

### **Expected Charts (Total: 2):**
- Bar: Product Performance ✅
- Bar: Branch Distribution ✅
- Line: **NONE** ❌ (correct - no date column)

### **Expected Console Output:**
```
📈 Phase 2: Generating Line Charts with dedicated module
🔍 Sales Summary check: {"ready": false, "missing_columns": ["Date column"]}
⏭️ Sales Summary not available: ["Date column"]
📈 Generated 0 line charts total
```

### **Success Criteria:**
- [ ] System detects no date column
- [ ] Shows message: "Sales Summary not available: Date column"
- [ ] Only bar charts generated (2 charts total)
- [ ] No crashes or errors
- [ ] Frontend displays bar charts normally
- [ ] No blank line chart cards

---

## 📊 COMPREHENSIVE TEST MATRIX

### **What Each Test Validates:**

| Feature | T1 | T2 | T3 | T4 | T5 |
|---------|----|----|----|----|----| 
| Date parsing | ✅ | ✅ | ✅ | ✅ | - |
| Standard intervals | ✅ | - | ✅ | - | - |
| Irregular intervals | - | ✅ | - | - | - |
| Large dataset handling | - | - | ✅ | - | - |
| Auto-sampling | - | - | ✅ | - | - |
| Date aggregation | - | - | - | ✅ | - |
| Missing date handling | - | - | - | - | ✅ |
| Bar chart compatibility | ✅ | ✅ | ✅ | ✅ | ✅ |
| Trend calculation | ✅ | ✅ | ✅ | ✅ | - |
| Dynamic labels | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 EXPECTED OUTCOMES SUMMARY

### **Expected Total Charts Per Test:**

| Test | Bar Charts | Line Charts | Total | Should Pass? |
|------|-----------|-------------|-------|--------------|
| **Test 1** | 2 | 1 | **3** | ✅ Yes |
| **Test 2** | 2 | 1 | **3** | ✅ Yes |
| **Test 3** | 2 | 1 | **3** | ✅ Yes (with sampling) |
| **Test 4** | 2 | 1 | **3** | ✅ Yes (with aggregation) |
| **Test 5** | 2 | 0 | **2** | ✅ Yes (graceful degradation) |

---

## 📝 TESTING CHECKLIST

### **For Each Test File:**

1. **Upload File**
   - [ ] File uploads successfully
   - [ ] No upload errors

2. **Check Console (Backend)**
   - [ ] Domain detection logged
   - [ ] Column mapping shown
   - [ ] Bar chart generation logged
   - [ ] Line chart generation logged
   - [ ] Number of charts matches expected

3. **Check Frontend Display**
   - [ ] Correct number of charts appear
   - [ ] Bar charts render properly
   - [ ] Line chart renders properly
   - [ ] No blank/broken charts

4. **Verify Line Chart Details**
   - [ ] X-axis shows dates
   - [ ] Y-axis shows values with units
   - [ ] Line connects points smoothly
   - [ ] Tooltip works on hover
   - [ ] Labels are domain-appropriate (not hardcoded "Sales")

5. **Verify Bar Charts Still Work**
   - [ ] Product performance shown
   - [ ] Regional distribution shown
   - [ ] No interference from line chart

---

## 🐛 COMMON ISSUES TO WATCH FOR

### **Date-Related Issues:**
- Line chart shows "Invalid Date" on X-axis
- Dates not sorted chronologically
- Date parsing fails silently

### **Aggregation Issues:**
- Duplicate dates create multiple points instead of one
- Aggregation sums incorrectly
- Grouped data doesn't match raw data totals

### **Sampling Issues:**
- Large dataset doesn't trigger sampling
- Sampled data loses important trends
- Weekly sampling creates gaps

### **Integration Issues:**
- Line chart breaks bar charts
- Charts don't display in correct order
- Chart types conflict

---

## 📊 TESTING LOG TEMPLATE

```
═══════════════════════════════════════════════════════════════
TEST: [Test Number] - [Test Name]
FILE: [Filename]
DATE: [Test Date/Time]
═══════════════════════════════════════════════════════════════

UPLOAD STATUS:
[ ] File uploaded successfully
[ ] Parsing completed

BACKEND CONSOLE OUTPUT:
Domain Detected: [Domain] ([Confidence]%)
Columns Mapped:
  - [Original] → [Canonical]
  
Bar Charts Generated: [Number]
Line Charts Generated: [Number]
Total Charts: [Number]

FRONTEND DISPLAY:
Charts Visible: [Number]
Chart 1: [Title] - [Type] - ✅/❌
Chart 2: [Title] - [Type] - ✅/❌
Chart 3: [Title] - [Type] - ✅/❌

LINE CHART DETAILS:
X-axis Label: [Label]
Y-axis Label: [Label]
Data Points: [Number]
Trend: [Increasing/Decreasing/Stable] [%]
Date Range: [Start] to [End]

ISSUES FOUND:
- [List any issues]

RESULT: ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

NOTES:
- [Additional observations]
═══════════════════════════════════════════════════════════════
```

---

## 🚀 QUICK START

**Start testing now:**
1. Upload `line_test1_standard_timeseries.csv`
2. Check you get 3 charts (2 bar + 1 line)
3. Verify line chart shows date trend
4. Move to next test

**Report back with results for each test!** 🧪

