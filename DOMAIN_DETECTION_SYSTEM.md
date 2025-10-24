# TANAW Domain Detection System

## 🎯 Supported Domains

TANAW now supports **5 domain categories** with intelligent detection:

1. **SALES** 📊 - Transaction and revenue data
2. **INVENTORY** 📦 - Stock and warehouse management
3. **FINANCE** 💰 - Budget, expenses, and cash flow
4. **CUSTOMER** 👥 - Customer behavior and segmentation
5. **MIXED** 🔀 - Combination of multiple domains

---

## 🔍 How Domain Detection Works

### Detection Algorithm

```python
# Step 1: Score each domain based on column patterns
for domain in ['sales', 'inventory', 'finance', 'customer']:
    score = 0
    
    # Primary indicators (weight: 3 points each)
    if column matches primary_indicators:
        score += 3
    
    # Secondary indicators (weight: 1 point each)
    if column matches secondary_indicators:
        score += 1
    
    # Pattern matching (weight: 2 points each)
    if column matches regex patterns:
        score += 2

# Step 2: Determine domain
top_domain = highest_score
second_domain = second_highest_score

if second_domain_score / top_domain_score >= 0.6:
    detected_domain = 'mixed'  # Multiple domains present
else:
    detected_domain = top_domain  # Single domain
```

---

## 📊 Domain Patterns

### 1. SALES Domain

**Primary Indicators** (3 points each):
- `sales`, `revenue`, `amount`, `price`, `cost`, `profit`, `margin`
- `transaction`, `order`, `purchase`, `payment`, `total`

**Secondary Indicators** (1 point each):
- `product`, `item`, `sku`, `category`, `region`, `territory`
- `customer`, `client`, `date`, `time`, `period`, `quarter`

**Analytics Generated**:
- Sales Summary Report (Line Chart)
- Product Performance Analysis (Bar Chart)
- Regional Sales Analysis (Bar Chart)
- Sales Forecasting (Forecast Chart)
- **+ Finance Analytics** (Revenue/Expense Trend, Profit Margin, Cash Flow)
- **+ Customer Analytics** (Segmentation, Frequency, CLV)

---

### 2. INVENTORY Domain

**Primary Indicators** (3 points each):
- `stock`, `inventory`, `quantity`, `units`, `warehouse`, `location`
- `supplier`, `vendor`, `reorder`, `threshold`, `minimum`, `maximum`

**Secondary Indicators** (1 point each):
- `product`, `item`, `sku`, `category`, `date`, `time`
- `location`, `warehouse`, `shelf`, `bin`

**Analytics Generated**:
- Stock Level Analysis (Bar Chart)
- Inventory Turnover Report (Line Chart)
- Reorder Point Analysis (Scatter Chart)
- Stock Forecasting (Forecast Chart)

---

### 3. FINANCE Domain 💰 NEW!

**Primary Indicators** (3 points each):
- `expense`, `income`, `budget`, `cash`, `flow`, `balance`
- `account`, `ledger`, `debit`, `credit`, `asset`, `liability`

**Secondary Indicators** (1 point each):
- `date`, `time`, `period`, `category`, `department`
- `account`, `vendor`, `description`

**Analytics Generated**:
- Revenue and Expense Trend (Multi-Line Chart)
- Profit Margin Analysis (Bar Chart)
- Cash Flow Forecast (Forecast Chart)
- Expense Breakdown Analysis (Pie Chart)
- Budget vs Actual Report (Bar Chart)

---

### 4. CUSTOMER Domain

**Primary Indicators** (3 points each):
- `customer`, `client`, `user`, `member`, `segment`, `demographic`
- `lifetime`, `value`, `churn`, `retention`, `satisfaction`

**Secondary Indicators** (1 point each):
- `name`, `email`, `phone`, `address`, `age`, `gender`
- `date`, `time`, `activity`, `engagement`

**Analytics Generated**:
- Customer Segmentation Analysis (Pie Chart)
- Customer Purchase Frequency (Bar Chart)
- Customer Lifetime Value (Bar Chart)
- Churn Analysis (Line Chart)

---

### 5. MIXED Domain 🔀 NEW!

**Detection Criteria**:
- Second domain score >= 60% of top domain score
- Dataset contains significant characteristics of multiple domains

**Example Scenarios**:

**Scenario 1: Sales + Finance**
```
Columns: Date, Product, Revenue, Expenses, Profit
Detection: SALES (score: 15) + FINANCE (score: 12)
Ratio: 12/15 = 80% → MIXED
Charts: Sales charts + Finance charts
```

**Scenario 2: Sales + Inventory**
```
Columns: Date, Product, Sales, Stock_Level, Reorder_Point
Detection: SALES (score: 12) + INVENTORY (score: 11)
Ratio: 11/12 = 92% → MIXED
Charts: Sales charts + Inventory charts
```

**Analytics Generated**:
- **All relevant analytics** from detected domains
- Combines base analytics + domain-specific analytics
- Prevents duplicates with domain tagging

---

## 🎨 Domain-Specific Chart Generation

### SALES Domain
```python
if domain == 'sales':
    # Base Sales Charts
    - Product Performance (Bar)
    - Sales Over Time (Line)
    - Sales Forecast (Forecast)
    
    # + Finance Charts
    - Revenue & Expense Trend (Multi-Line)
    - Profit Margin Analysis (Bar)
    - Cash Flow Forecast (Forecast)
    
    # + Customer Charts
    - Customer Segmentation (Pie)
    - Purchase Frequency (Bar)
    - Lifetime Value (Bar)
```

### FINANCE Domain
```python
if domain == 'finance':
    # Base Charts (if applicable)
    - Time Series (Line) - if date + amount
    
    # Finance-Specific Charts
    - Revenue & Expense Trend (Multi-Line)
    - Profit Margin Analysis (Bar)
    - Cash Flow Forecast (Forecast)
    - Expense Breakdown (Pie)
    - Budget vs Actual (Bar)
```

### INVENTORY Domain
```python
if domain == 'inventory':
    # Base Charts
    - Product Performance (Bar) - if applicable
    
    # Inventory-Specific Charts
    - Stock Level Analysis (Bar)
    - Inventory Turnover (Line)
    - Reorder Point Analysis (Scatter)
    - Stock Forecast (Forecast)
```

### CUSTOMER Domain
```python
if domain == 'customer':
    # Base Charts
    - Time Series (Line) - if applicable
    
    # Customer-Specific Charts
    - Customer Segmentation (Pie)
    - Purchase Frequency (Bar)
    - Lifetime Value (Bar)
    - Churn Analysis (Line)
```

### MIXED Domain
```python
if domain == 'mixed':
    # Combines all relevant charts from detected domains
    # Example: Sales + Finance
    
    # Sales Charts
    - Product Performance (Bar)
    - Sales Over Time (Line)
    - Sales Forecast (Forecast)
    
    # Finance Charts
    - Revenue & Expense Trend (Multi-Line)
    - Profit Margin Analysis (Bar)
    - Cash Flow Forecast (Forecast)
```

---

## 🧪 Testing Domain Detection

### Test Case 1: Pure Finance Dataset
**Columns**: Date, Revenue, Expenses, Budget, Account
**Expected**: FINANCE domain (confidence > 0.7)
**Charts**: Finance-specific analytics only

### Test Case 2: Sales Dataset with Finance Data
**Columns**: Date, Product, Sales, Revenue, Expenses
**Expected**: SALES domain OR MIXED domain
**Charts**: Sales + Finance analytics

### Test Case 3: Mixed Sales + Inventory
**Columns**: Date, Product, Sales, Stock_Level, Warehouse
**Expected**: MIXED domain
**Charts**: Sales + Inventory analytics

### Test Case 4: Pure Sales Dataset
**Columns**: Date, Product, Sales, Region
**Expected**: SALES domain (confidence > 0.7)
**Charts**: Sales analytics + Finance (if revenue/expense detected) + Customer

---

## 📝 Domain Classification Output

```python
DomainClassification(
    domain='sales' | 'inventory' | 'finance' | 'customer' | 'mixed',
    confidence=0.0-1.0,  # Confidence score
    indicators=[...],  # List of detected indicators
    suggested_analytics=[...]  # List of analytics for this domain
)
```

---

## 🎯 Benefits

### Before (Old System)
- ❌ Only SALES and INVENTORY domains
- ❌ Finance charts disabled (created duplicates)
- ❌ Customer analytics not integrated
- ❌ No mixed domain support

### After (New System)
- ✅ **4 distinct domains** + MIXED
- ✅ **Finance domain** properly detected and charts generated
- ✅ **Customer analytics** integrated
- ✅ **MIXED domain** combines multiple analytics
- ✅ **No duplicates** (domain tagging prevents conflicts)
- ✅ **Flexible detection** (60% threshold for mixed domains)

---

## 🔄 Domain Detection Flow

```
1. Upload Dataset
   ↓
2. Parse Columns
   ↓
3. GPT Column Mapping
   ↓
4. Domain Detection
   ├─ Calculate scores for each domain
   ├─ Find top 2 domains
   └─ Check if mixed (score_ratio >= 60%)
   ↓
5. Generate Domain-Specific Analytics
   ├─ SALES → Sales + Finance + Customer charts
   ├─ FINANCE → Finance charts only
   ├─ INVENTORY → Inventory charts only
   ├─ CUSTOMER → Customer charts only
   └─ MIXED → Combine charts from multiple domains
   ↓
6. Return Charts to Frontend
```

---

## 📊 Example Detection Results

### Example 1: Our Test Dataset
```
Columns: Date, Revenue, Expenses, Product, Category

Domain Scores:
- SALES: 15 (Revenue=sales pattern, Product, Date)
- FINANCE: 12 (Revenue=income, Expenses, Date)
- INVENTORY: 3 (Product only)
- CUSTOMER: 2 (Category only)

Score Ratio: 12/15 = 80%

Result: MIXED (SALES + FINANCE)
Confidence: 0.85
Charts: Sales analytics + Finance analytics
```

### Example 2: Pure Finance Dataset
```
Columns: Date, Expenses, Income, Budget, Account

Domain Scores:
- FINANCE: 18 (Expenses, Income, Budget, Account)
- SALES: 5 (Income=revenue pattern)
- INVENTORY: 0
- CUSTOMER: 1 (Account)

Score Ratio: 5/18 = 28%

Result: FINANCE (single domain)
Confidence: 0.75
Charts: Finance analytics only
```

---

## ✅ Implementation Complete

- ✅ MIXED domain detection logic
- ✅ Enhanced finance domain patterns
- ✅ Dynamic analytics combination
- ✅ 60% threshold for mixed detection
- ✅ Improved logging and debugging
- ✅ Domain-specific chart routing

The system can now intelligently detect and handle:
- **Pure domains** (SALES, INVENTORY, FINANCE, CUSTOMER)
- **Mixed domains** (combinations of 2+ domains)
- **Appropriate analytics** for each domain type


