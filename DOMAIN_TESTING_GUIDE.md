# 🧪 Domain Analytics Testing Guide

## 📋 Test Files Created

I've created **6 test datasets** to verify all domain detection and chart generation scenarios:

---

## 📊 Test Files Overview

| # | File Name | Domain | Purpose |
|---|-----------|--------|---------|
| 1 | `1_PURE_SALES_Dataset.csv` | **SALES** | Test pure sales analytics only |
| 2 | `2_PURE_INVENTORY_Dataset.csv` | **INVENTORY** | Test pure inventory analytics only |
| 3 | `3_PURE_FINANCE_Dataset.csv` | **FINANCE** | Test pure finance analytics only |
| 4 | `4_PURE_CUSTOMER_Dataset.csv` | **CUSTOMER** | Test pure customer analytics only |
| 5 | `5_MIXED_SALES_INVENTORY_Dataset.csv` | **MIXED** | Test Sales + Inventory combination |
| 6 | `6_MIXED_SALES_FINANCE_CUSTOMER_Dataset.csv` | **MIXED** | Test Sales + Finance + Customer combination |

---

## 🧪 Test Scenarios

### **Test 1: Pure Sales Dataset** 📊

**File**: `1_PURE_SALES_Dataset.csv`

**Columns:**
- Date, Product, Category, Region, Customer
- Sales_Amount, Quantity_Sold, Unit_Price, Payment_Method

**Expected Domain Detection:** **SALES**

**Expected Charts Generated:**
- ✅ **Sales Charts** (from original method):
  - Product Performance Analysis (Bar)
  - Regional Sales Analysis (Bar)
  - Sales Trend Over Time (Line)
  - Sales Forecast (Line)
  
- ❌ **Finance Charts**: SKIPPED
  - Reason: No finance columns (no Expense, Budget, Account, etc.)
  - Has Sales_Amount but no Expense → Score < 3
  
- ❌ **Inventory Charts**: SKIPPED
  - Reason: No inventory columns (no Stock, Warehouse, Reorder, Supplier)
  
- ❌ **Customer Charts**: SKIPPED
  - Reason: Customer column exists but no Customer_Type/Segment
  - Score < 3 (only Customer column, need more indicators)

**Expected Total**: **~7 charts** (Sales only)

**Terminal Output Should Show:**
```
🎯 Detected Domain: SALES
📊 SALES Domain detected - Checking for additional analytics...

💰 Checking for Finance indicators...
   💰 Finance score: 0 → ❌ Insufficient
⏭️ No finance indicators found - skipping Finance charts

👥 Checking for Customer indicators...
   👥 Customer score: 3 → ❌ Insufficient (or borderline)
⏭️ No customer indicators found - skipping Customer charts
```

---

### **Test 2: Pure Inventory Dataset** 📦

**File**: `2_PURE_INVENTORY_Dataset.csv`

**Columns:**
- Product_Name, SKU, Stock_Quantity, Reorder_Level, Reorder_Quantity
- Warehouse_Location, Supplier_Name, Last_Restock_Date, Unit_Cost, Stock_Status

**Expected Domain Detection:** **INVENTORY**

**Expected Charts Generated:**
- ✅ **Inventory Charts**:
  - Stock Level Analysis (Bar)
  - Reorder Point Analysis (Bar)
  - Location-based Inventory (Bar)
  - Supplier Performance (Bar)
  
- ❌ **Finance Charts**: SKIPPED
  - Reason: Has Unit_Cost but no Revenue/Expense/Sales
  - Cannot calculate revenue (no Sales_Volume)
  - Score < 3
  
- ❌ **Sales Charts**: Limited or None
  - Reason: No Sales_Amount or transaction data
  
- ❌ **Customer Charts**: SKIPPED
  - Reason: No customer data

**Expected Total**: **~5 charts** (Inventory only)

**Terminal Output Should Show:**
```
🎯 Detected Domain: INVENTORY
📦 INVENTORY Domain detected - Generating Inventory analytics
✅ Added 5 Inventory charts

💰 Checking for Finance indicators...
   💰 Finance score: 1 → ❌ Insufficient
⏭️ No finance indicators found - skipping Finance charts
```

---

### **Test 3: Pure Finance Dataset** 💰

**File**: `3_PURE_FINANCE_Dataset.csv`

**Columns:**
- Date, Account_Name, Category, Department
- **Revenue**, **Expense**, **Budget_Allocated**
- Transaction_Type, Description

**Expected Domain Detection:** **FINANCE**

**Expected Charts Generated:**
- ✅ **Finance Charts**:
  - Revenue and Expense Trend (Multi-line)
  - Profit Margin Analysis (Bar)
  - Cash Flow Forecast (Line Forecast)
  
- ❌ **Sales Charts**: May generate some (if axis_resolver finds Sales_Amount)
  
- ❌ **Inventory Charts**: SKIPPED
  - Reason: No stock/warehouse data
  
- ❌ **Customer Charts**: SKIPPED
  - Reason: No customer data

**Expected Total**: **~3-5 charts** (Finance + maybe some sales)

**Terminal Output Should Show:**
```
🎯 Detected Domain: FINANCE
💰 FINANCE Domain detected - Focusing on Finance analytics
💰 TANAW Finance Analytics: Generating analytics for 42 records

📊 Chart 1: Generating Revenue and Expense Trend...
   💰 Finance indicator found: Revenue
   💰 Finance indicator found: Expense
   ✓ Found column 'Revenue' directly in DataFrame
   ✓ Found column 'Expense' directly in DataFrame
   ✅ Generated trend with 42 data points

✅ Added 3 Finance charts
```

---

### **Test 4: Pure Customer Dataset** 👥

**File**: `4_PURE_CUSTOMER_Dataset.csv`

**Columns:**
- Customer_ID, Customer_Name, **Customer_Type**, **Customer_Segment**
- Email, Phone, Registration_Date, Last_Purchase_Date
- Total_Purchases, Total_Spent, Purchase_Frequency
- **Satisfaction_Rating**, **Churn_Risk**

**Expected Domain Detection:** **CUSTOMER**

**Expected Charts Generated:**
- ✅ **Customer Charts**:
  - Customer Segmentation Analysis (Pie)
  - Purchase Frequency Analysis (Bar)
  - Customer Lifetime Value (Bar)
  
- ❌ **Finance Charts**: SKIPPED
  - Reason: No Revenue/Expense columns (only Total_Spent per customer)
  
- ❌ **Sales Charts**: May generate minimal charts
  
- ❌ **Inventory Charts**: SKIPPED

**Expected Total**: **~3 charts** (Customer only)

**Terminal Output Should Show:**
```
🎯 Detected Domain: CUSTOMER
👥 CUSTOMER Domain detected - Adding Customer analytics
👥 Customer indicator found: Customer_Type
👥 Customer indicator found: Customer_Segment
👥 Customer indicator found: Satisfaction_Rating
👥 Customer indicator found: Churn_Risk

✅ Added 3 Customer charts
```

---

### **Test 5: Mixed Sales + Inventory** 🔀

**File**: `5_MIXED_SALES_INVENTORY_Dataset.csv`

**Columns:**
- Date, Product, Category, Region
- **Sales_Amount**, Quantity_Sold, Unit_Price
- **Stock_Quantity**, **Reorder_Level**, **Warehouse**, **Supplier**

**Expected Domain Detection:** **MIXED** (Sales + Inventory)

**Expected Charts Generated:**
- ✅ **Sales Charts** (~7 charts):
  - Product Performance, Regional Sales, Sales Trend, Forecast
  
- ✅ **Inventory Charts** (~5 charts):
  - Stock Level, Reorder Analysis, Location Analysis, Supplier Performance
  
- ✅ **Finance Charts** (~3 charts):
  - **Reason**: Has Sales_Amount (revenue) + Can calculate from Price × Volume
  - Finance score ≥ 3 ✅
  - Revenue & Expense Trend, Profit Margin, Cash Flow Forecast
  
- ❌ **Customer Charts**: SKIPPED
  - Reason: No Customer_Type or Segment

**Expected Total**: **~15 charts** (Sales + Inventory + Finance)

**Terminal Output Should Show:**
```
🎯 Detected MIXED Domain: INVENTORY + SALES
🔀 MIXED Domain detected - Intelligently combining analytics

💰 Checking for Finance indicators...
   💰 Can calculate revenue from Price × Volume
   💰 Finance indicator found: Sales_Amount (Revenue)
   💰 Finance score: 4 → ✅ Sufficient
✅ Finance data detected - generating Finance analytics
✅ Added 3 Finance charts

📦 Checking for Inventory indicators...
   📦 Inventory indicator found: Stock_Quantity
   📦 Inventory indicator found: Reorder_Level
   📦 Inventory indicator found: Warehouse
   📦 Inventory indicator found: Supplier
   📦 Inventory score: 12 → ✅ Sufficient
✅ Inventory data detected - generating Inventory analytics
✅ Added 5 Inventory charts

👥 Checking for Customer indicators...
   👥 Customer score: 0 → ❌ Insufficient
⏭️ No customer indicators - skipping Customer charts
```

---

### **Test 6: Mixed Sales + Finance + Customer** 🔀

**File**: `6_MIXED_SALES_FINANCE_CUSTOMER_Dataset.csv`

**Columns:**
- Date, **Customer_ID**, Customer_Name, **Customer_Type**
- Product, Category, Sales_Amount
- **Revenue**, **Expense**, **Profit**
- Payment_Method, **Customer_Satisfaction**

**Expected Domain Detection:** **MIXED** or **SALES**

**Expected Charts Generated:**
- ✅ **Sales Charts** (~7 charts):
  - Product Performance, Category Analysis, Sales Trend, Forecast
  
- ✅ **Finance Charts** (~3 charts):
  - **Reason**: Has Revenue + Expense + Profit columns
  - Finance score: 9+ ✅
  - Revenue & Expense Trend, Profit Margin, Cash Flow Forecast
  
- ✅ **Customer Charts** (~3 charts):
  - **Reason**: Has Customer_ID, Customer_Type, Customer_Satisfaction
  - Customer score: 9+ ✅
  - Customer Segmentation, Purchase Frequency, Customer LTV
  
- ❌ **Inventory Charts**: SKIPPED
  - Reason: No Stock/Warehouse/Reorder data

**Expected Total**: **~13 charts** (Sales + Finance + Customer)

**Terminal Output Should Show:**
```
🎯 Detected Domain: SALES (or MIXED)

💰 Checking for Finance indicators...
   💰 Finance indicator found: Revenue
   💰 Finance indicator found: Expense
   💰 Finance indicator found: Profit
   💰 Finance score: 9 → ✅ Sufficient
✅ Finance data detected - generating Finance analytics
✅ Added 3 Finance charts

👥 Checking for Customer indicators...
   👥 Customer indicator found: Customer_ID
   👥 Customer indicator found: Customer_Type
   👥 Customer indicator found: Customer_Satisfaction
   👥 Customer score: 9 → ✅ Sufficient
✅ Customer data detected - generating Customer analytics
✅ Added 3 Customer charts
```

---

## 📝 Testing Checklist

### **For Each Test File:**

1. **Upload the CSV**
   - Go to User Dashboard
   - Upload the test file
   - Wait 15-20 seconds

2. **Check Terminal Output**
   - Look for domain detection message
   - Verify validator scores
   - Confirm which modules are skipped/included

3. **Check Generated Charts**
   - Count total charts
   - Verify only relevant charts appear
   - Check for any zero/flatline charts

4. **Verify Chart Quality**
   - Charts should have real data
   - No flatlines (unless intentional forecast baseline)
   - Insights should be relevant

---

## ✅ Expected Results Summary

| Test File | Domain | Sales | Inventory | Finance | Customer | Total Charts |
|-----------|--------|-------|-----------|---------|----------|--------------|
| 1. Pure Sales | SALES | ✅ ~7 | ❌ Skip | ❌ Skip | ❌ Skip | **~7** |
| 2. Pure Inventory | INVENTORY | ⚠️ 0-2 | ✅ ~5 | ❌ Skip | ❌ Skip | **~5** |
| 3. Pure Finance | FINANCE | ⚠️ 0-2 | ❌ Skip | ✅ ~3 | ❌ Skip | **~3** |
| 4. Pure Customer | CUSTOMER | ⚠️ 0-2 | ❌ Skip | ❌ Skip | ✅ ~3 | **~3** |
| 5. Mixed S+I | MIXED | ✅ ~7 | ✅ ~5 | ✅ ~3 | ❌ Skip | **~15** |
| 6. Mixed S+F+C | MIXED/SALES | ✅ ~7 | ❌ Skip | ✅ ~3 | ✅ ~3 | **~13** |

---

## 🎯 What to Look For

### **✅ SUCCESS Indicators:**

1. **Domain Detection**
   - Each file correctly classified
   - Confidence scores > 0.7

2. **Smart Routing**
   - Only relevant charts generated
   - Irrelevant domains properly skipped
   - Clear terminal messages

3. **No Flatlines**
   - Finance charts show real revenue (not zeros)
   - All charts have meaningful data
   - No "all zeros" or "all same value" charts

4. **Terminal Logs**
   - Clear "✅ Added X charts" messages
   - Clear "⏭️ Skipping" messages with reasons
   - Validator scores displayed

### **❌ FAILURE Indicators:**

1. **Wrong Charts Generated**
   - Finance charts appear for Pure Inventory dataset
   - Customer charts appear without customer data

2. **Flatlines Still Exist**
   - Finance charts showing all zeros
   - Revenue lines at 0

3. **Missing Expected Charts**
   - Pure Finance dataset doesn't generate finance charts
   - Inventory dataset doesn't generate inventory charts

4. **Error Messages**
   - Python exceptions in terminal
   - Failed chart generation
   - 404 errors

---

## 🔍 Detailed Test Instructions

### **Test 1: Pure Sales**
1. Upload `1_PURE_SALES_Dataset.csv`
2. **Expected**: Sales charts only
3. **Check Terminal**: Should see "⏭️ No finance indicators - skipping Finance charts"
4. **Verify**: ~7 sales charts, no finance/inventory/customer charts

### **Test 2: Pure Inventory**
1. Upload `2_PURE_INVENTORY_Dataset.csv`
2. **Expected**: Inventory charts only
3. **Check Terminal**: Should see "⏭️ No finance indicators - skipping Finance charts"
4. **Verify**: ~5 inventory charts, no finance/sales/customer charts

### **Test 3: Pure Finance**
1. Upload `3_PURE_FINANCE_Dataset.csv`
2. **Expected**: Finance charts with REAL data (not zeros!)
3. **Check Terminal**: Should see "✓ Found column 'Revenue' directly in DataFrame"
4. **Verify**: 
   - Revenue & Expense Trend shows **two lines** (green revenue, red expense)
   - Profit Margin shows **varied bars** (not all 20%)
   - Cash Flow Forecast shows **trends** (not flatline at 0)

### **Test 4: Pure Customer**
1. Upload `4_PURE_CUSTOMER_Dataset.csv`
2. **Expected**: Customer charts only
3. **Check Terminal**: Should see "👥 Customer indicator found: Customer_Type"
4. **Verify**: 
   - Customer Segmentation pie chart (VIP, Premium, Standard, Inactive)
   - Purchase Frequency bar chart
   - Customer LTV bar chart

### **Test 5: Mixed Sales + Inventory**
1. Upload `5_MIXED_SALES_INVENTORY_Dataset.csv`
2. **Expected**: Sales + Inventory + Finance charts
3. **Check Terminal**: Should see ALL three domains validated ✅
4. **Verify**: 
   - ~7 Sales charts
   - ~5 Inventory charts
   - ~3 Finance charts (because has Sales_Amount = Revenue)
   - Total: ~15 charts

### **Test 6: Mixed Sales + Finance + Customer**
1. Upload `6_MIXED_SALES_FINANCE_CUSTOMER_Dataset.csv`
2. **Expected**: Sales + Finance + Customer charts (no inventory)
3. **Check Terminal**: Should see Finance, Customer validated ✅, Inventory skipped ❌
4. **Verify**:
   - ~7 Sales charts
   - ~3 Finance charts with **real revenue/expense trends**
   - ~3 Customer charts with segmentation
   - Total: ~13 charts

---

## 🎯 Success Criteria

### **For Pure Datasets:**
- ✅ Only charts from the detected domain are generated
- ✅ Other domains are explicitly skipped with clear messages
- ✅ No flatlines or zero-value charts

### **For Mixed Datasets:**
- ✅ Multiple domains detected and validated
- ✅ Only domains with sufficient data generate charts
- ✅ Terminal shows validation scores for each domain
- ✅ Charts from multiple domains are combined intelligently

### **Overall System:**
- ✅ No 404 errors in terminal
- ✅ Flask service responds to `/` endpoint
- ✅ All charts have meaningful, non-zero data
- ✅ Processing completes within 20 seconds

---

## 🐛 Known Issues to Watch For

### **Issue 1: GPT Column Mapping Errors**
- GPT might mismap columns
- Example: `Reorder_Level` → `Date` (wrong!)
- **Impact**: Charts might not generate even with correct data

### **Issue 2: Threshold Sensitivity**
- Finance score threshold = 3
- Borderline datasets might be skipped incorrectly
- **Watch**: Datasets with only 1-2 finance columns

### **Issue 3: Duplicate Charts**
- Mixed datasets might generate duplicate charts
- Example: Same product chart from Sales + Finance modules
- **Check**: No identical charts in output

---

## 📊 Testing Order (Recommended)

1. **Start Simple**: Pure datasets first (Tests 1-4)
2. **Then Complex**: Mixed datasets (Tests 5-6)
3. **Finally**: Your Grocery Inventory (should skip Finance now ✅)

---

## 🚀 Quick Start

```bash
# 1. Ensure Flask service is running
cd backend/analytics_service
python app_clean.py

# 2. Go to User Dashboard
http://localhost:3000/dashboard

# 3. Upload test files one by one
# 4. Observe terminal output
# 5. Verify charts in UI

# 6. Check for:
✅ Correct domain detection
✅ Smart routing (skip irrelevant domains)
✅ No flatlines
✅ No 404 errors
```

---

## 📋 Test Results Template

Use this to track your testing:

```
Test 1: Pure Sales
- Domain Detected: ___________
- Charts Generated: ___________
- Finance Skipped: YES / NO
- Any Errors: ___________

Test 2: Pure Inventory  
- Domain Detected: ___________
- Charts Generated: ___________
- Finance Skipped: YES / NO
- Any Errors: ___________

Test 3: Pure Finance
- Domain Detected: ___________
- Charts Generated: ___________
- Revenue Shows Real Data: YES / NO
- Any Flatlines: YES / NO

Test 4: Pure Customer
- Domain Detected: ___________
- Charts Generated: ___________
- Finance Skipped: YES / NO
- Any Errors: ___________

Test 5: Mixed Sales+Inventory
- Domain Detected: ___________
- Charts Generated: ___________
- Finance Included: YES / NO
- Finance Score: ___________

Test 6: Mixed Sales+Finance+Customer
- Domain Detected: ___________
- Charts Generated: ___________
- All 3 Domains Included: YES / NO
- Inventory Skipped: YES / NO
```

---

## ✅ All Test Files Ready!

**Location**: `TEST FILES/` directory

Upload them one by one and observe the intelligent routing in action! 🎯


