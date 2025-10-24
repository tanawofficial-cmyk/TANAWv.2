# 📦 Inventory Test Dataset

## Overview
This dataset is designed to test TANAW's inventory analytics and stock forecasting capabilities.

## Dataset Details
- **File**: `inventory_test_dataset.csv`
- **Records**: 75 rows (15 business days × 5 products)
- **Time Period**: January 1-31, 2024
- **Format**: CSV with 8 columns

## Columns Description
| Column | Description | Example |
|--------|-------------|---------|
| `Date` | Business date | 2024-01-01 |
| `Product` | Product name | Laptop Pro |
| `Stock_Level` | Current stock quantity | 150 |
| `Location` | Warehouse location | Warehouse A |
| `Supplier` | Supplier name | TechSupply Inc |
| `Reorder_Point` | Minimum stock threshold | 50 |
| `Cost_Per_Unit` | Unit cost in currency | 1200.00 |
| `Last_Updated` | Last update timestamp | 2024-01-01 09:00:00 |

## Products Included
1. **Laptop Pro** - High-value item ($1,200)
   - Stock: 150 → 40 (declining trend)
   - Reorder Point: 50 (near reorder threshold)
   - Supplier: TechSupply Inc

2. **Wireless Mouse** - Fast-moving item ($25)
   - Stock: 300 → 0 (stockout occurred)
   - Reorder Point: 100 (critical reorder needed)
   - Supplier: Peripheral Co

3. **USB Cable** - Medium velocity ($15)
   - Stock: 500 → 60 (steady decline)
   - Reorder Point: 200 (approaching threshold)
   - Supplier: CableCorp

4. **Monitor 24"** - Critical item ($300)
   - Stock: 80 → 0 (stockout occurred)
   - Reorder Point: 30 (urgent reorder needed)
   - Supplier: DisplayTech

5. **Keyboard** - Standard item ($45)
   - Stock: 200 → 90 (moderate decline)
   - Reorder Point: 75 (approaching threshold)
   - Supplier: KeyBoard Ltd

## Testing Scenarios

### 1. Context Detection
- **Expected**: "Inventory Dataset Detected" banner
- **Expected**: High confidence (90%+) for inventory context
- **Expected**: No sales forecast generation

### 2. Stock Forecast Generation
- **Expected**: Stock Forecast chart with Prophet AI
- **Expected**: 30-day forecast period
- **Expected**: Confidence intervals (95%)
- **Expected**: Historical + forecast data points

### 3. Reorder Analysis
- **Expected**: Reorder point calculations
- **Expected**: Urgency levels (Critical/High/Medium/Low)
- **Expected**: Safety stock recommendations
- **Expected**: Lead time demand analysis

### 4. Business Intelligence
- **Expected**: Critical alerts for stockouts
- **Expected**: Reorder recommendations
- **Expected**: Trend analysis per product
- **Expected**: Seasonality detection

## Expected Results

### Charts Generated
1. **Stock Level Overview** (Bar Chart)
   - Current stock levels by product
   - Reorder point indicators
   - Critical stock alerts

2. **Inventory Turnover** (Line Chart)
   - Stock movement trends over time
   - Velocity analysis per product

3. **Stock Forecast** (Line Forecast)
   - 30-day stock level predictions
   - Prophet AI forecasting
   - Confidence intervals

### Insights Expected
- **Critical Alerts**: Wireless Mouse, Monitor 24" (stockouts)
- **High Urgency**: Laptop Pro (near reorder point)
- **Medium Urgency**: USB Cable, Keyboard (approaching thresholds)
- **Reorder Recommendations**: Specific actions for each product

## Usage Instructions

1. **Upload Dataset**
   - Go to TANAW dashboard
   - Click "Choose File"
   - Select `inventory_test_dataset.csv`
   - Click "Upload & Analyze"

2. **Verify Context Detection**
   - Check for "Inventory Dataset Detected" banner
   - Verify confidence level > 90%
   - Confirm inventory-specific message

3. **Review Analytics**
   - Check for 3 charts generated
   - Verify Stock Forecast with Prophet AI
   - Review reorder analysis insights

4. **Validate Business Intelligence**
   - Check critical stockout alerts
   - Verify reorder recommendations
   - Confirm urgency classifications

## Success Criteria
- ✅ Context detection: "Inventory Dataset Detected"
- ✅ Charts generated: 3 (Stock Level, Inventory Turnover, Stock Forecast)
- ✅ Stock Forecast: Prophet AI with confidence intervals
- ✅ Reorder Analysis: Critical/High/Medium urgency levels
- ✅ No Sales Forecast: Inventory context only
