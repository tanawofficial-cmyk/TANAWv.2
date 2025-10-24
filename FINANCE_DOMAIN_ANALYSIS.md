# TANAW Chart Generation System Analysis
## Complete Flow from Mapping to Visualization

### 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Data Flow Architecture](#data-flow-architecture)
3. [Key Components](#key-components)
4. [Domain Detection & Analytics](#domain-detection--analytics)
5. [Finance Domain Current State](#finance-domain-current-state)
6. [Implementation Strategy for Finance](#implementation-strategy-for-finance)

---

## System Overview

### Architecture Layers
```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  - Dashboard.js (User uploads file)                             │
│  - ChartComponents.js (Displays visualizations)                 │
└──────────────────┬───────────────────────────────────────────────┘
                   │ POST /api/files/upload-clean
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Node.js/Express)                           │
│  - fileController.js (Route handler)                            │
│  - Forwards to Flask service                                    │
└──────────────────┬───────────────────────────────────────────────┘
                   │ POST /api/files/upload-clean
                   ↓
┌─────────────────────────────────────────────────────────────────┐
│           ANALYTICS SERVICE (Flask/Python)                       │
│  - app_clean.py (Main processor)                                │
│  - TANAWDataProcessor class                                     │
│  ├── 1. File Parsing (robust_file_parser.py)                    │
│  ├── 2. Column Mapping (gpt_column_mapper.py)                   │
│  ├── 3. Domain Detection (domain_detector.py)                   │
│  ├── 4. Data Cleaning & Transformation                          │
│  ├── 5. Domain-Specific Analytics                               │
│  └── 6. Chart Generation                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

### Step-by-Step Process

#### 1. **File Upload (Frontend → Backend)**
```javascript
// frontend/src/pages/Dashboard.js
const handleUpload = async () => {
  const formData = new FormData();
  formData.append("file", selectedFile);
  
  const res = await api.post("/files/upload-clean", formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "multipart/form-data",
    },
  });
  
  // Response includes: charts, mappings, domain, summary_metrics
}
```

#### 2. **Backend Routing (Node.js)**
```javascript
// backend/controllers/fileController.js
const uploadClean = async (req, res) => {
  // Forward file to Flask analytics service
  const formData = new FormData();
  formData.append("file", fs.createReadStream(req.file.path));
  
  flaskRes = await axios.post(`${FLASK_BASE_URL}/api/files/upload-clean`, formData);
  
  // Log API usage for OpenAI calls
  await ApiUsage.logApiUsage({
    service: 'openai',
    tokensUsed: estimatedTokens,
    estimatedCost: estimatedCost,
    userId: req.user.id
  });
}
```

#### 3. **Flask Processing Pipeline**

**3.1 File Parsing**
```python
# backend/analytics_service/app_clean.py
@app.route("/api/files/upload-clean", methods=["POST"])
def analyze_clean():
    # Step 1: Parse file
    parse_result = parse_file_robust(tmp_path, None)
    df = parse_result.dataframe
    # Returns: DataFrame with original column names
```

**3.2 GPT Column Mapping**
```python
    # Step 2: OpenAI Column Mapping
    gpt_mapper = GPTColumnMapper(api_key)
    columns = [str(col) for col in df.columns]
    mapping_result = gpt_mapper.map_columns(columns, "retail")
    
    # Example mapping_result.mappings:
    # [
    #   ColumnMapping(original_column='order_date', mapped_to='Date', confidence=0.95),
    #   ColumnMapping(original_column='total_sales', mapped_to='Sales', confidence=0.98),
    #   ColumnMapping(original_column='product_name', mapped_to='Product', confidence=0.92)
    # ]
```

**3.3 Domain Detection**
```python
    # Step 3.1: Domain Detection
    column_mapping = {m.original_column: m.mapped_to for m in mapping_result.mappings}
    domain_classification = tanaw_processor.domain_detector.detect_domain(df, column_mapping)
    
    # domain_classification contains:
    # - domain: 'sales' | 'inventory' | 'finance' | 'customer'
    # - confidence: 0.0 - 1.0
    # - indicators: List of detected keywords
    # - suggested_analytics: List of analytics suitable for domain
```

**3.4 Data Cleaning & Transformation**
```python
    # Step 3.2: Clean and transform data
    cleaned_df = tanaw_processor.clean_and_transform_data(df, column_mapping)
    
    # Transformations:
    # - Apply column mappings (rename to canonical names)
    # - Convert data types (Date → datetime, Sales → float)
    # - Handle missing values
    # - Normalize data formats
```

**3.5 Domain-Specific Analytics**
```python
    # Step 3.3: Generate domain analytics and charts
    analytics_result = tanaw_processor.generate_domain_analytics(
        cleaned_df, 
        column_mapping, 
        domain_classification
    )
    
    # analytics_result contains:
    # - charts: List[Chart] - Generated visualizations
    # - readiness: Analytics availability status
    # - domain: Detected domain name
    # - domain_confidence: Confidence score
```

---

## Key Components

### 1. Canonical Schema

**Purpose**: Standardizes column names across different datasets

```python
# tanaw_canonical_schema.py
class CanonicalColumnType(Enum):
    DATE = "Date"
    SALES = "Sales" 
    AMOUNT = "Amount"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    REGION = "Region"
    CUSTOMER = "Customer"
    TRANSACTION_ID = "Transaction_ID"
```

**Example Mapping**:
```
User Dataset:          Canonical:
├─ order_date    →    Date
├─ total_sales   →    Sales
├─ product_name  →    Product
├─ units_sold    →    Quantity
└─ region_code   →    Region
```

### 2. Domain Detection System

**Purpose**: Automatically classifies datasets into business domains

```python
# domain_detector.py
class TANAWDomainDetector:
    def detect_domain(self, df: pd.DataFrame, column_mapping: Dict):
        # Analyzes column mappings and data patterns
        # Returns domain classification with confidence
```

**Domain Patterns**:
```python
domain_patterns = {
    'sales': {
        'primary_indicators': ['sales', 'revenue', 'amount', 'price', 'profit'],
        'secondary_indicators': ['product', 'customer', 'date', 'region']
    },
    'inventory': {
        'primary_indicators': ['stock', 'inventory', 'quantity', 'warehouse'],
        'secondary_indicators': ['product', 'supplier', 'location']
    },
    'finance': {
        'primary_indicators': ['expense', 'income', 'budget', 'cash', 'balance'],
        'secondary_indicators': ['account', 'ledger', 'debit', 'credit']
    },
    'customer': {
        'primary_indicators': ['customer', 'client', 'segment', 'lifetime_value'],
        'secondary_indicators': ['name', 'email', 'activity', 'engagement']
    }
}
```

### 3. Chart Generation Flow

```python
# app_clean.py - TANAWDataProcessor
def generate_domain_analytics(self, df, column_mapping, domain_classification):
    # 1. Clean data using original method
    cleaned_df = self.clean_and_transform_data(df, column_mapping)
    
    # 2. Generate base analytics (bar charts, line charts, forecasts)
    analytics_result = self.generate_analytics_and_charts(cleaned_df, column_mapping)
    charts = analytics_result.get('charts', [])
    
    # 3. Add domain-specific analytics
    domain = domain_classification.domain.lower()
    
    if domain == 'inventory':
        inventory_charts = self.inventory_analytics.generate_analytics(df, column_mapping)
        charts.extend([self._convert_inventory_chart(chart) for chart in inventory_charts])
        
    elif domain == 'finance':
        # CURRENTLY DISABLED - Creates duplicates
        # finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
        # charts.extend([self._convert_finance_chart(chart) for chart in finance_charts])
        pass
        
    elif domain == 'customer':
        customer_charts = self.customer_analytics.generate_analytics(df, column_mapping)
        charts.extend([self._convert_customer_chart(chart) for chart in customer_charts])
    
    # 4. Generate conversational insights using OpenAI
    if self.conversational_insights:
        charts = self.conversational_insights.add_insights_to_charts(charts, cleaned_df)
    
    return {
        "charts": charts,
        "readiness": {...},
        "domain": domain,
        "domain_confidence": domain_classification.confidence
    }
```

### 4. Chart Data Structure

**Chart Object Format**:
```python
{
    "id": "unique_chart_id",
    "title": "Chart Title",
    "type": "bar" | "line" | "pie" | "scatter",
    "description": "What this chart shows",
    "icon": "📊",
    "data": {
        "x": [values],  # X-axis data
        "y": [values],  # Y-axis data
        "labels": [values],  # For categorical data
    },
    "config": {
        "maintainAspectRatio": False,
        "responsive": True,
        "plugins": {...}
    },
    "insight": "AI-generated conversational insight (optional)"
}
```

---

## Domain Detection & Analytics

### Current Domain Support

#### 1. **Sales Domain** ✅ ACTIVE
- **Detection Criteria**: Presence of sales, revenue, amount columns
- **Analytics Generated**:
  - Bar Charts (Product Performance, Regional Sales)
  - Line Charts (Sales Trends, Time Series)
  - Sales Forecasting (Predictive)
  
#### 2. **Inventory Domain** ✅ ACTIVE
- **Detection Criteria**: Presence of stock, inventory, quantity columns
- **Analytics Generated**:
  - Stock Level Analysis
  - Inventory Turnover
  - Reorder Point Analysis
  - Stock Forecasting

#### 3. **Customer Domain** ✅ ACTIVE
- **Detection Criteria**: Presence of customer, client, segment columns
- **Analytics Generated**:
  - Customer Segmentation
  - Lifetime Value Analysis
  - Churn Prediction
  - Retention Analysis

#### 4. **Finance Domain** ⚠️ DISABLED (Creates Duplicates)
- **Detection Criteria**: Presence of expense, income, budget columns
- **Analytics** Attempted**:
  - Expense Breakdown
  - Cash Flow Analysis
  - Budget vs Actual
  - Profit Margin Analysis
  - Financial Forecasting

---

## Finance Domain Current State

### Current Implementation

**File**: `backend/analytics_service/finance_analytics.py`

```python
class TANAWFinanceAnalytics:
    """
    Finance analytics engine for TANAW.
    Provides expense analysis, cash flow, budget tracking, and profit margins.
    """
    
    def __init__(self):
        self.analytics_config = {
            'expense_breakdown': {
                'name': 'Expense Breakdown Analysis',
                'type': 'pie'
            },
            'cash_flow_analysis': {
                'name': 'Cash Flow Analysis',
                'type': 'line'
            },
            'budget_vs_actual': {
                'name': 'Budget vs Actual Report',
                'type': 'bar'
            },
            'profit_margin': {
                'name': 'Profit Margin Analysis',
                'type': 'bar'
            },
            'financial_forecast': {
                'name': 'Financial Forecasting',
                'type': 'line'
            }
        }
    
    def generate_analytics(self, df: pd.DataFrame, column_mapping: Dict):
        """Generate finance analytics charts"""
        charts = []
        
        # 1. Expense Breakdown Analysis (pie chart)
        expense_chart = self._generate_expense_breakdown(df, column_mapping)
        
        # 2. Cash Flow Analysis (line chart)
        cashflow_chart = self._generate_cashflow_analysis(df, column_mapping)
        
        # 3. Budget vs Actual (bar chart)
        budget_chart = self._generate_budget_analysis(df, column_mapping)
        
        # 4. Profit Margin Analysis (bar chart)
        profit_chart = self._generate_profit_analysis(df, column_mapping)
        
        # 5. Financial Forecasting (line chart)
        forecast_chart = self._generate_financial_forecast(df, column_mapping)
        
        return charts
```

### Why It's Currently Disabled

**Location**: `backend/analytics_service/app_clean.py:776-780`

```python
elif domain == 'finance':
    # DISABLED: Finance analytics module creates duplicates with line chart generator
    # print("💰 Adding finance-specific analytics...")
    # finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
    # charts.extend([self._convert_finance_chart(chart) for chart in finance_charts])
    print("💰 Finance analytics disabled to prevent duplicates with line chart generator")
```

**Reason**: The finance module generates line charts and bar charts that duplicate what the base analytics system already generates (line_chart_generator.py, bar_chart_generator.py).

### Issues with Current Finance Implementation

1. **Column Mapping Confusion**:
   ```python
   # Current code looks for 'Sales' for amount data
   if canonical_col == 'Sales' and orig_col in df.columns:
       amount_col = orig_col
   
   # Should look for finance-specific columns like:
   # - 'Expense', 'Income', 'Amount', 'Balance'
   ```

2. **Lacks Finance-Specific Canonical Columns**:
   - No `Expense` canonical type
   - No `Income` canonical type
   - No `Budget` canonical type
   - No `Account` canonical type

3. **Duplicates Base Analytics**:
   - Line charts already generated by `line_chart_generator.py`
   - Bar charts already generated by `bar_chart_generator.py`

---

## Implementation Strategy for Finance

### Proposed Solution

#### Phase 1: Extend Canonical Schema

**Add Finance-Specific Columns** to `tanaw_canonical_schema.py`:

```python
class CanonicalColumnType(Enum):
    # Existing columns
    DATE = "Date"
    SALES = "Sales" 
    AMOUNT = "Amount"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    REGION = "Region"
    CUSTOMER = "Customer"
    TRANSACTION_ID = "Transaction_ID"
    
    # NEW: Finance-specific columns
    EXPENSE = "Expense"
    INCOME = "Income"
    BUDGET = "Budget"
    ACCOUNT = "Account"
    CATEGORY = "Category"
    BALANCE = "Balance"
    PROFIT = "Profit"
    COST = "Cost"
```

**Add Finance Aliases**:
```python
CanonicalColumnType.EXPENSE: {
    "aliases": [
        "expense", "expenses", "cost", "expenditure", "spending",
        "outflow", "payment", "disbursement", "expense_amount"
    ],
    "description": "Expense or cost field",
    "data_types": ["float64", "int64", "float32", "int32"]
},
CanonicalColumnType.INCOME: {
    "aliases": [
        "income", "revenue", "earnings", "inflow", "receipts",
        "proceeds", "profit", "gain", "income_amount"
    ],
    "description": "Income or revenue field",
    "data_types": ["float64", "int64", "float32", "int32"]
},
CanonicalColumnType.BUDGET: {
    "aliases": [
        "budget", "budgeted", "planned", "forecast", "allocation",
        "budget_amount", "planned_amount", "estimated"
    ],
    "description": "Budgeted amount field",
    "data_types": ["float64", "int64", "float32", "int32"]
},
CanonicalColumnType.ACCOUNT: {
    "aliases": [
        "account", "account_name", "account_code", "gl_account",
        "ledger", "account_type", "category", "department"
    ],
    "description": "Account or category identifier",
    "data_types": ["object", "string", "category"]
}
```

#### Phase 2: Update Finance Analytics Module

**Refactor** `finance_analytics.py` to use finance-specific columns:

```python
class TANAWFinanceAnalytics:
    def _generate_expense_breakdown(self, df, column_mapping):
        # Look for finance-specific columns
        expense_col = self._find_column(column_mapping, ['Expense', 'Cost', 'Amount'])
        category_col = self._find_column(column_mapping, ['Account', 'Category', 'Product'])
        
        if not expense_col or not category_col:
            return None
        
        # Group by category and sum expenses
        expense_data = df.groupby(category_col)[expense_col].sum()
        
        return FinanceChart(
            id='expense_breakdown',
            title='Expense Breakdown by Category',
            type='pie',
            data={'labels': categories, 'values': expenses}
        )
    
    def _generate_budget_vs_actual(self, df, column_mapping):
        budget_col = self._find_column(column_mapping, ['Budget'])
        actual_col = self._find_column(column_mapping, ['Expense', 'Amount'])
        category_col = self._find_column(column_mapping, ['Account', 'Category'])
        
        if not budget_col or not actual_col or not category_col:
            return None
        
        # Calculate variance
        comparison = df.groupby(category_col).agg({
            budget_col: 'sum',
            actual_col: 'sum'
        })
        
        return FinanceChart(
            id='budget_vs_actual',
            title='Budget vs Actual Expenses',
            type='bar',
            data={
                'categories': comparison.index,
                'budget': comparison[budget_col],
                'actual': comparison[actual_col]
            }
        )
```

#### Phase 3: Add Finance-Specific Analytics Types

**New Analytics** that don't duplicate base system:

1. **Expense Breakdown** (Pie Chart) - NEW
   - Groups expenses by category/account
   - Shows percentage distribution

2. **Budget Variance Analysis** (Bar Chart) - NEW
   - Compares budgeted vs actual
   - Highlights over/under budget items

3. **Cash Flow Statement** (Waterfall Chart) - NEW
   - Shows inflows and outflows
   - Running balance visualization

4. **Profit & Loss Summary** (Table + Chart) - NEW
   - Income - Expenses = Profit
   - Period comparison

5. **Financial Ratios** (Card Display) - NEW
   - Expense Ratio
   - Profit Margin
   - Budget Adherence Rate

#### Phase 4: Integration Strategy

**Modify** `app_clean.py` to properly integrate finance analytics:

```python
def generate_domain_analytics(self, df, column_mapping, domain_classification):
    # Base analytics
    analytics_result = self.generate_analytics_and_charts(cleaned_df, column_mapping)
    charts = analytics_result.get('charts', [])
    
    domain = domain_classification.domain.lower()
    
    if domain == 'finance':
        print("💰 Adding finance-specific analytics...")
        
        # Generate ONLY finance-specific charts (no duplicates)
        finance_charts = self.finance_analytics.generate_analytics(df, column_mapping)
        
        # Filter out duplicates before adding
        unique_finance_charts = self._filter_duplicate_charts(finance_charts, charts)
        charts.extend([self._convert_finance_chart(chart) for chart in unique_finance_charts])
        
        print(f"✅ Added {len(unique_finance_charts)} unique finance charts")
```

---

## Summary

### Current System Flow

1. **Frontend** uploads file → **Backend** routes to Flask
2. **Flask** parses file → GPT maps columns → Detects domain
3. **Domain-specific analytics** generate charts based on detected domain
4. **Charts returned** to frontend for visualization

### Finance Domain Status

- **Module exists**: ✅ `finance_analytics.py`
- **Currently active**: ❌ Disabled due to duplicates
- **Needs**:
  - Extended canonical schema with finance columns
  - Refactored analytics to use finance-specific columns
  - Duplicate detection and filtering
  - Finance-specific chart types (waterfall, variance)

### Next Steps to Implement Finance

1. ✅ Understand current system (COMPLETE)
2. ⏭️ Extend canonical schema with finance columns
3. ⏭️ Update domain detection for finance patterns
4. ⏭️ Refactor finance analytics module
5. ⏭️ Add finance-specific visualizations
6. ⏭️ Re-enable finance domain in app_clean.py
7. ⏭️ Test with finance datasets


