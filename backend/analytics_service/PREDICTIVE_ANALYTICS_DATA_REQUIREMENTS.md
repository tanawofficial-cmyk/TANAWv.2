# 📊 TANAW Predictive Analytics Data Requirements

**Date**: October 22, 2025  
**Purpose**: Complete guide to data requirements for sales forecasting and predictive analytics

---

## 🎯 OVERVIEW

TANAW's predictive analytics system requires specific data columns and formats to generate accurate forecasts. This document outlines the exact requirements for each forecasting type.

---

## 📈 SALES FORECASTING REQUIREMENTS

### **Core Data Requirements:**

#### **1. DATE COLUMN (Required)**
**Purpose**: Time series analysis and trend detection  
**Minimum Records**: 10 data points  
**Format**: Any recognizable date format

**Accepted Column Names:**
```
Primary: Date, OrderDate, Order_Date, TransactionDate, Transaction_Date
Secondary: SaleDate, Sale_Date, PurchaseDate, Purchase_Date
Tertiary: Time, Timestamp, CreatedAt, Created_At, UpdatedAt, Updated_At
```

**Data Quality Requirements:**
- ✅ Must be parseable as datetime
- ✅ At least 50% of values must be valid dates
- ✅ No more than 30% missing values
- ✅ Sequential or chronological order preferred

#### **2. SALES/VALUE COLUMN (Required)**
**Purpose**: Numeric values for forecasting  
**Data Type**: Numeric (integer or decimal)  
**Minimum Records**: 10 data points

**Accepted Column Names:**
```
Primary: Sales, Sales_Amount, SalesAmount, Revenue, Total_Sales, TotalSales
Secondary: Amount, Value, Price, Cost, Income, Profit, Earnings
```

**Data Quality Requirements:**
- ✅ Must be numeric (integers or decimals)
- ✅ At least 50% of values must be numeric
- ✅ No negative values (for sales forecasting)
- ✅ Reasonable range (not all zeros or extremely large values)

### **Optional Enhancement Columns:**

#### **3. PRODUCT/ITEM COLUMN (Optional)**
**Purpose**: Product-specific forecasting  
**Benefit**: More granular predictions

**Accepted Column Names:**
```
Product, Product_Name, ProductName, Item, Item_Name, ItemName
SKU, Product_Code, ProductCode, Name, Description
```

#### **4. LOCATION/REGION COLUMN (Optional)**
**Purpose**: Geographic forecasting  
**Benefit**: Location-based trend analysis

**Accepted Column Names:**
```
Location, Region, City, State, Country, Branch, Store
Area, Zone, Territory, Market
```

---

## 📦 STOCK FORECASTING REQUIREMENTS

### **Core Data Requirements:**

#### **1. DATE COLUMN (Required)**
**Same requirements as Sales Forecasting**

#### **2. STOCK/INVENTORY COLUMN (Required)**
**Purpose**: Inventory levels for forecasting  
**Data Type**: Numeric (integer or decimal)

**Accepted Column Names:**
```
Primary: Stock, Stock_Level, StockLevel, Inventory, Quantity, Units
Secondary: On_Hand, OnHand, Available, Current_Stock, CurrentStock
```

**Data Quality Requirements:**
- ✅ Must be numeric (integers or decimals)
- ✅ At least 50% of values must be numeric
- ✅ Non-negative values (stock can't be negative)
- ✅ Reasonable range for inventory levels

### **Optional Enhancement Columns:**

#### **3. REORDER POINT COLUMN (Optional)**
**Purpose**: Advanced reorder analysis  
**Benefit**: Automatic reorder recommendations

**Accepted Column Names:**
```
Reorder_Point, ReorderPoint, Reorder_Level, ReorderLevel
Min_Stock, MinStock, Safety_Stock, SafetyStock
```

#### **4. PRODUCT/ITEM COLUMN (Optional)**
**Same as Sales Forecasting**

---

## 🔍 DATA QUALITY REQUIREMENTS

### **Minimum Data Points:**
- **Sales Forecast**: 10 records minimum
- **Stock Forecast**: 10 records minimum
- **Recommended**: 30+ records for better accuracy

### **Data Completeness:**
- **Date Column**: ≥50% valid dates
- **Value Column**: ≥50% numeric values
- **Missing Data**: ≤30% missing values per column

### **Data Range Requirements:**
- **Sales Data**: Positive values (≥0)
- **Stock Data**: Non-negative values (≥0)
- **Date Range**: At least 7 days span for meaningful trends

---

## 📊 FORECASTING ALGORITHMS USED

### **1. Prophet AI (Primary)**
**Requirements:**
- Time series data with date and value columns
- Minimum 10 data points
- Handles seasonality and trends automatically

**Best For:**
- Sales forecasting with seasonal patterns
- Stock forecasting with demand cycles
- Complex time series with multiple patterns

### **2. Linear Regression (Fallback)**
**Requirements:**
- Same as Prophet but simpler
- Works when Prophet fails
- Good for linear trends

**Best For:**
- Simple linear trends
- When Prophet AI is unavailable
- Quick forecasting needs

---

## 🎯 EXAMPLE DATASETS

### **Sales Forecasting Dataset:**
```csv
Date,Sales,Product,Location
2024-01-01,1500,Widget A,North
2024-01-02,1200,Widget B,South
2024-01-03,1800,Widget A,North
2024-01-04,900,Widget C,East
2024-01-05,2100,Widget A,North
```

### **Stock Forecasting Dataset:**
```csv
Date,Stock_Level,Product,Reorder_Point
2024-01-01,100,Widget A,20
2024-01-02,95,Widget A,20
2024-01-03,85,Widget A,20
2024-01-04,75,Widget A,20
2024-01-05,65,Widget A,20
```

---

## ⚠️ COMMON DATA ISSUES

### **1. Date Format Issues:**
```
❌ Problem: "01/02/2024" vs "2024-01-02"
✅ Solution: TANAW auto-detects and converts formats

❌ Problem: Text dates like "January 1, 2024"
✅ Solution: TANAW parses various date formats
```

### **2. Numeric Format Issues:**
```
❌ Problem: "$1,500.00" (currency format)
✅ Solution: TANAW strips currency symbols

❌ Problem: "1.5K" (abbreviated numbers)
✅ Solution: TANAW converts to numeric values
```

### **3. Missing Data Issues:**
```
❌ Problem: 50%+ missing values
✅ Solution: TANAW requires ≥50% valid data

❌ Problem: All zeros or same values
✅ Solution: TANAW detects and warns about insufficient variation
```

---

## 🚀 OPTIMAL DATASET CHARACTERISTICS

### **For Best Forecasting Results:**

#### **Sales Forecasting:**
- **Time Span**: 3+ months of data
- **Frequency**: Daily or weekly records
- **Seasonality**: Include seasonal patterns (holidays, quarters)
- **Trends**: Clear upward/downward trends
- **Variation**: Reasonable variation in sales values

#### **Stock Forecasting:**
- **Time Span**: 2+ months of inventory data
- **Frequency**: Daily stock level updates
- **Demand Patterns**: Include demand fluctuations
- **Reorder Points**: Include reorder threshold data
- **Product Mix**: Multiple products for better analysis

---

## 📋 DATA VALIDATION CHECKLIST

### **Before Upload:**
- [ ] Date column is in recognizable format
- [ ] Sales/Stock column contains numeric values
- [ ] At least 10 data points available
- [ ] No more than 30% missing values
- [ ] Values are reasonable (not all zeros)
- [ ] Data spans meaningful time period

### **After Upload:**
- [ ] TANAW successfully parses dates
- [ ] TANAW detects numeric columns
- [ ] Forecast readiness shows "ready": true
- [ ] No data quality warnings
- [ ] Sufficient data variation detected

---

## 🎯 FORECASTING ACCURACY FACTORS

### **High Accuracy Requirements:**
- **Data Volume**: 30+ records
- **Time Span**: 3+ months
- **Data Quality**: <10% missing values
- **Trend Clarity**: Clear patterns in data
- **Seasonality**: Regular seasonal patterns

### **Medium Accuracy Requirements:**
- **Data Volume**: 15-29 records
- **Time Span**: 1-2 months
- **Data Quality**: 10-20% missing values
- **Trend Clarity**: Some patterns visible

### **Low Accuracy (Limited Forecasting):**
- **Data Volume**: 10-14 records
- **Time Span**: <1 month
- **Data Quality**: 20-30% missing values
- **Trend Clarity**: Limited patterns

---

## 🔧 TROUBLESHOOTING

### **"Forecast Not Ready" Issues:**

#### **Missing Date Column:**
```
Error: "Sales forecast requires date column"
Solution: Ensure dataset has a date column with recognizable format
```

#### **Missing Sales Column:**
```
Error: "Sales forecast requires numeric sales column"
Solution: Ensure dataset has numeric sales/revenue column
```

#### **Insufficient Data:**
```
Error: "Sales forecast requires at least 10 data points"
Solution: Add more historical data records
```

#### **Poor Data Quality:**
```
Error: "Insufficient data variation"
Solution: Ensure data has meaningful variation and trends
```

---

## 📊 SUMMARY

### **Minimum Requirements for Forecasting:**
1. **Date Column**: Recognizable date format
2. **Value Column**: Numeric sales/stock data
3. **Data Points**: Minimum 10 records
4. **Data Quality**: ≥50% valid values

### **Optimal Requirements for Best Results:**
1. **Data Volume**: 30+ records
2. **Time Span**: 3+ months
3. **Data Quality**: <10% missing values
4. **Clear Trends**: Visible patterns in data
5. **Seasonality**: Regular seasonal patterns

### **TANAW Auto-Detection:**
- ✅ Automatically detects date columns
- ✅ Automatically detects numeric columns
- ✅ Validates data quality
- ✅ Provides readiness status
- ✅ Suggests improvements

---

**TANAW's predictive analytics system is designed to work with various data formats and automatically handles most common data issues. The system will guide you through any data quality problems and suggest improvements for better forecasting accuracy! 🚀📊**
