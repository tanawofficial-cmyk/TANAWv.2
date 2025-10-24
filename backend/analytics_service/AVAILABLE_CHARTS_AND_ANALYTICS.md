# TANAW Analytics System - Complete Chart & Analytics Catalog

## 📊 Current System Capabilities (As of October 2025)

TANAW can intelligently analyze datasets and generate **context-aware** charts and analytics across **Sales** and **Inventory** domains.

---

## 🎯 Intelligent Features

### 1. **Semantic Context Detection**
- ✅ Automatically detects if dataset is **SALES**, **INVENTORY**, or **MIXED**
- ✅ Uses OpenAI GPT-4o-mini to analyze column names and sample data
- ✅ Generates domain-specific charts based on context
- ✅ Prevents misleading chart generation (e.g., no inventory charts for sales data)

### 2. **Enhanced Narrative Insights**
- ✅ AI-powered business intelligence using OpenAI
- ✅ Specific recommendations with timelines (0-30 days, 1-3 months, 3-12 months)
- ✅ Risk assessment and opportunity identification
- ✅ Success metrics for measuring impact
- ✅ SME-focused actionable insights

### 3. **Advanced Forecasting**
- ✅ Prophet AI (Facebook Prophet) for superior accuracy
- ✅ Confidence intervals and trend analysis
- ✅ Linear regression fallback for reliability

---

## 📈 SALES DOMAIN CHARTS

### 1. Product Comparison by Sales (Bar Chart)
**Type:** Bar Chart
**Generator:** `bar_chart_generator.py` → `generate_product_performance()`
**Context:** SALES, MIXED, UNKNOWN

**What it shows:**
- Sales performance across different products
- Top and bottom performing products
- Product-level sales comparison

**Requirements:**
- Product/Item column
- Sales/Revenue column

**Features:**
- Top N products (configurable)
- Sorted by sales value (descending)
- Includes total sales and product count
- Color-coded for visual clarity

**Insights Provided:**
- Top 3 performers with specific values
- Bottom 3 performers with specific values
- Concentration ratio (Pareto analysis)
- Performance gap analysis
- Specific recommendations for inventory, marketing, and product strategy

---

### 2. Location-based Sales Distribution (Bar Chart)
**Type:** Bar Chart
**Generator:** `bar_chart_generator.py` → `generate_regional_sales()`
**Context:** SALES, MIXED, UNKNOWN

**What it shows:**
- Sales distribution across different locations
- Geographic/organizational performance
- Location-based comparison

**Requirements:**
- Location column (Branch, Region, Area, City, State, Country, etc.)
- Sales/Revenue column

**Features:**
- Supports multiple location types (flexible)
- Top N locations (configurable)
- Sorted by sales value
- Dynamic labels based on column names

**Insights Provided:**
- Top performing locations
- Geographic expansion opportunities
- Resource allocation recommendations
- Market penetration analysis

---

### 3. Sales Over Time (Line Chart)
**Type:** Line Chart
**Generator:** `line_chart_generator.py` → `generate_sales_summary()`
**Context:** SALES, MIXED, UNKNOWN

**What it shows:**
- Sales trends over time
- Temporal patterns and seasonality
- Growth trajectory

**Requirements:**
- Date/Time column
- Sales/Revenue column

**Features:**
- Daily aggregation
- Sorted chronologically
- Trend line visualization
- Time series analysis

**Insights Provided:**
- Growth trends (upward/downward/stable)
- Seasonal patterns
- Peak sales periods
- Revenue optimization strategies

---

### 4. Sales Forecast (Line Chart with Forecast)
**Type:** Line Chart with Forecast
**Generator:** `sales_forecast_generator.py` → `generate_sales_forecast()`
**Context:** SALES, MIXED, UNKNOWN
**AI Model:** Facebook Prophet (with linear regression fallback)

**What it shows:**
- Historical sales data
- Future sales predictions (30 days default)
- Confidence intervals (upper/lower bounds)
- Trend analysis

**Requirements:**
- Date column
- Sales/Revenue column
- Minimum 7 days of historical data

**Features:**
- **Prophet AI forecasting** for superior accuracy
- Confidence intervals (default: 80%)
- Automatic trend detection
- Seasonality handling
- Linear regression fallback for robustness

**Insights Provided:**
- Predicted revenue for next 30 days
- Growth rate analysis
- Forecast trend (increasing/decreasing/stable)
- Capacity planning recommendations
- Goal setting strategies
- Model accuracy indicators

---

## 📦 INVENTORY DOMAIN CHARTS

### 5. Stock Level Overview by Product (Bar Chart)
**Type:** Bar Chart
**Generator:** `bar_chart_generator.py` → `generate_stock_level_overview()`
**Context:** INVENTORY, MIXED, UNKNOWN

**What it shows:**
- Current stock levels for each product
- Inventory distribution across products
- Product-level stock comparison

**Requirements:**
- Product/Item column
- Stock Level/Quantity column

**Features:**
- Top N products (configurable)
- Sorted by stock level (descending)
- Total inventory count
- Stock level distribution

**Insights Provided:**
- Products with highest stock
- Products with lowest stock
- Overstocking identification
- Understocking warnings
- Inventory optimization recommendations

---

### 6. Reorder Status - Items Needing Attention (Bar Chart)
**Type:** Bar Chart
**Generator:** `bar_chart_generator.py` → `generate_reorder_status()`
**Context:** INVENTORY, MIXED, UNKNOWN

**What it shows:**
- Products requiring reorder
- Stock levels vs reorder points
- Urgency analysis

**Requirements:**
- Product/Item column
- Stock Level column
- Reorder Point column (optional - can be estimated)

**Features:**
- Calculates reorder threshold (20% of max stock)
- Identifies items below reorder point
- Urgency classification
- Priority ranking

**Insights Provided:**
- Critical items needing immediate reorder
- Items approaching reorder point
- Stockout risk analysis
- Procurement recommendations
- Supply chain efficiency tips

---

### 7. Stock Level Analysis (Line Chart)
**Type:** Line Chart
**Generator:** `line_chart_generator.py` → `generate_sales_summary()` (reused with inventory data)
**Context:** INVENTORY, MIXED, UNKNOWN

**What it shows:**
- Stock level changes over time
- Inventory trends
- Temporal patterns in stock movement

**Requirements:**
- Date column
- Stock Level column

**Features:**
- Daily aggregation
- Last value per day (inventory snapshot)
- Time series visualization
- Trend analysis

**Insights Provided:**
- Stock depletion rate
- Replenishment patterns
- Inventory turnover trends
- Dead stock identification

---

### 8. Inventory Turnover Report (Line Chart)
**Type:** Line Chart
**Generator:** `line_chart_generator.py` → `generate_inventory_turnover()`
**Context:** INVENTORY, MIXED, UNKNOWN

**What it shows:**
- Inventory turnover rate over time
- How quickly inventory is sold/used
- Cash flow implications

**Requirements:**
- Date column
- Turnover Rate column (or calculated)

**Features:**
- Daily aggregation
- Last value per day
- Turnover rate visualization
- Temporal analysis

**Insights Provided:**
- Fast-moving vs slow-moving items
- Cash flow implications
- Dead stock identification
- Supplier relationship optimization
- Working capital recommendations

---

### 9. Stock Forecast (Line Chart with Forecast)
**Type:** Line Chart with Forecast
**Generator:** `stock_forecast_generator.py` → `generate_stock_forecast()`
**Context:** INVENTORY, MIXED, UNKNOWN
**AI Model:** Facebook Prophet (with linear regression fallback)

**What it shows:**
- Historical stock levels
- Future stock level predictions (30 days default)
- Confidence intervals
- Reorder recommendations

**Requirements:**
- Date column
- Stock Level column
- Minimum 7 days of historical data

**Features:**
- **Prophet AI forecasting** for demand planning
- Confidence intervals (default: 80%)
- Reorder point calculation
- Safety stock recommendations
- Lead time demand analysis
- Urgency classification (Critical/High/Medium/Low)

**Insights Provided:**
- Predicted stock levels for next 30 days
- Optimal reorder points
- Safety stock levels
- Lead time demand
- Stockout risk warnings
- Procurement timing recommendations
- Urgency-based priority list

**Reorder Recommendations Include:**
- Product name
- Current stock level
- Reorder point
- Safety stock
- Lead time demand
- Urgency level
- Recommended action

---

## 🎨 CHART TYPES SUPPORTED

### Bar Charts
- ✅ Product Performance
- ✅ Location-based Sales
- ✅ Stock Level Overview
- ✅ Reorder Status

### Line Charts
- ✅ Sales Over Time
- ✅ Stock Level Analysis
- ✅ Inventory Turnover

### Forecast Charts (Line with Prediction)
- ✅ Sales Forecast (Prophet AI)
- ✅ Stock Forecast (Prophet AI)

---

## 🤖 AI-POWERED FEATURES

### 1. Semantic Context Detection
**Model:** OpenAI GPT-4o-mini
**Purpose:** Determine dataset domain (SALES/INVENTORY/MIXED)

**How it works:**
1. Analyzes column names
2. Samples random rows (5+ per column)
3. Detects business context
4. Returns confidence score
5. Rule-based fallback if needed

**Output:**
```json
{
  "context": "SALES",
  "confidence": 0.85,
  "method": "openai",
  "reasoning": "Dataset contains sales, revenue, and product columns..."
}
```

---

### 2. Narrative Insights Generation
**Model:** OpenAI GPT-4o-mini
**Purpose:** Generate intelligent business recommendations

**For each chart, provides:**
1. **Business Description** - What the data reveals with specific numbers
2. **Strategic Insight** - Organizational implications
3. **Actionable Recommendations** - 3 timelines:
   - Immediate (0-30 days)
   - Short-term (1-3 months)
   - Long-term (3-12 months)
4. **Risk Assessment** - Risks and opportunities
5. **Success Metrics** - How to measure impact

**Example Insight:**
```
Business Description: "Product 1089 leads with ₱220,000 (22.9% of revenue)..."

Actionable Recommendations:
1. Immediate (0-30 days): Increase inventory for top 3 products by 15-20%. 
   Expected: 10-15% revenue boost.
2. Short-term (1-3 months): Analyze underperformers, test promotions. 
   Target: 30% sales increase.
3. Long-term (3-12 months): Develop new products. 
   ROI: ₱300K-400K additional revenue.
```

---

### 3. Prophet AI Forecasting
**Model:** Facebook Prophet
**Purpose:** Superior time series forecasting

**Features:**
- Automatic trend detection
- Seasonality handling
- Holiday effects (configurable)
- Confidence intervals
- Change point detection

**Advantages over linear regression:**
- Handles non-linear trends
- Captures seasonality
- More robust to outliers
- Better accuracy for complex patterns

---

## 📊 ANALYTICS METADATA

### Data Quality Metrics
Every analysis includes:
- ✅ Total rows processed
- ✅ Missing values count
- ✅ Data quality score
- ✅ Column mapping details
- ✅ Processing time

### Chart Metadata
Every chart includes:
- ✅ Chart ID and type
- ✅ Title and description
- ✅ Icon for visual identification
- ✅ Axis labels
- ✅ Data ranges
- ✅ Total values
- ✅ Item counts

### Insights Metadata
Every insight includes:
- ✅ Confidence score (0.0-1.0)
- ✅ Generation timestamp
- ✅ Insight type
- ✅ Domain classification
- ✅ Chart title reference

---

## 🔄 CONTEXT-AWARE CHART GENERATION

### SALES Context
**Generates:**
1. Product Comparison by Sales
2. Location-based Sales Distribution
3. Sales Over Time
4. Sales Forecast (Prophet AI)

**Skips:**
- Stock Level Overview
- Reorder Status
- Inventory Turnover
- Stock Forecast

---

### INVENTORY Context
**Generates:**
1. Stock Level Overview by Product
2. Reorder Status - Items Needing Attention
3. Stock Level Analysis
4. Inventory Turnover Report
5. Stock Forecast (Prophet AI)

**Skips:**
- Product Comparison by Sales
- Location-based Sales Distribution
- Sales Forecast

---

### MIXED Context
**Generates:**
All available charts from both domains:
1. Product Comparison by Sales
2. Location-based Sales Distribution
3. Stock Level Overview by Product
4. Reorder Status - Items Needing Attention
5. Sales Over Time
6. Sales Forecast (Prophet AI)
7. Stock Level Analysis
8. Inventory Turnover Report
9. Stock Forecast (Prophet AI)

---

### UNKNOWN Context
**Generates:**
All available charts (same as MIXED)
- System tries to generate all charts
- Only successful ones are returned
- Graceful fallback for missing data

---

## 📥 EXPORT CAPABILITIES

### 1. PDF Report
- ✅ Professional format
- ✅ All charts and insights
- ✅ Executive summary
- ✅ Business intelligence sections
- ✅ Print-ready with page breaks
- ✅ TANAW branding

### 2. Excel/CSV Export
- ✅ Spreadsheet format
- ✅ Chart metadata
- ✅ Insights as text
- ✅ Easy integration with other tools

### 3. JSON Export
- ✅ Raw data format
- ✅ Complete analysis structure
- ✅ API integration ready
- ✅ Machine-readable

---

## 🎯 INTELLIGENT COLUMN DETECTION

The system automatically detects:

### Product/Item Columns:
- Product, Item, Product_Name, SKU, Item_Code, etc.

### Sales/Revenue Columns:
- Sales, Revenue, Amount, Total_Sales, Sales_Amount, etc.

### Location Columns:
- Location, Branch, Region, Area, City, State, Country, Territory, Zone, District, Warehouse, Store, Outlet

### Stock Columns:
- Stock, Stock_Level, Quantity, Inventory, Available, On_Hand, etc.

### Date Columns:
- Date, Order_Date, Transaction_Date, Timestamp, Created_At, etc.

### Reorder Columns:
- Reorder_Point, Reorder_Level, Min_Stock, Threshold, etc.

---

## 🚀 SYSTEM PERFORMANCE

### Processing Speed:
- **Column Mapping**: 0.2-0.5 seconds (OpenAI-powered)
- **Chart Generation**: 1-2 seconds per chart
- **Narrative Insights**: 2-4 seconds per batch (3 charts)
- **Total Analysis**: 5-15 seconds for complete dataset

### Cost Efficiency:
- **Column Mapping**: ~$0.0001 per dataset
- **Narrative Insights**: ~$0.001-0.002 per batch (3 charts)
- **Full Analysis (10 charts)**: ~$0.005-0.008 total
- **Extremely cost-effective for SMEs!**

### Reliability:
- ✅ 3 retry attempts with exponential backoff
- ✅ Fallback insights when AI fails
- ✅ Graceful error handling
- ✅ Robust data validation

---

## 📋 SUMMARY

### Total Charts Available: **9 Chart Types**

**Sales Charts (4):**
1. Product Comparison by Sales
2. Location-based Sales Distribution
3. Sales Over Time
4. Sales Forecast (Prophet AI)

**Inventory Charts (5):**
5. Stock Level Overview by Product
6. Reorder Status - Items Needing Attention
7. Stock Level Analysis
8. Inventory Turnover Report
9. Stock Forecast (Prophet AI)

### AI Features:
- ✅ Semantic Context Detection
- ✅ Intelligent Column Mapping
- ✅ Enhanced Narrative Insights
- ✅ Prophet AI Forecasting
- ✅ Business Recommendations

### Export Formats:
- ✅ PDF Report
- ✅ Excel/CSV
- ✅ JSON Data

---

## 🎨 COMING SOON (Currently Disabled)

### Finance Domain Charts:
- Expense Distribution (temporarily disabled)
- Profit Margin Analysis (temporarily disabled)
- Revenue Analysis (planned)
- Cash Flow Analysis (planned)

*Finance charts will be re-enabled after completing the semantic detection system for all three domains.*

---

## 🌟 Key Strengths

1. **🎯 Context-Aware**: Generates relevant charts based on dataset type
2. **🤖 AI-Powered**: Uses OpenAI for intelligent insights
3. **📈 Prophet Forecasting**: Superior accuracy with Facebook Prophet
4. **💡 Actionable**: Specific recommendations with timelines
5. **💰 Cost-Effective**: Pennies per analysis
6. **🛡️ Robust**: Multiple fallback mechanisms
7. **📊 Comprehensive**: 9 chart types covering sales and inventory
8. **🚀 Fast**: Complete analysis in seconds
9. **📱 Professional**: Export to PDF, Excel, or JSON

---

**TANAW - Smart Analytics for SMEs** 🎯✨

*Last Updated: October 2025*

