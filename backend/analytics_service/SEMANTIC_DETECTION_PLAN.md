# 🧠 SEMANTIC DETECTION IMPLEMENTATION PLAN

## 📋 OBJECTIVE
Build intelligent context-aware chart generation that understands the **meaning** of data, not just column names.

---

## 🚨 THE PROBLEM IDENTIFIED

### Real-World Example: Balaji-Fast-Food-Sales.csv
**Dataset Columns:**
- `order_id`, `date`, `item_name`, `item_type`, `item_price`
- **`quantity`** ← SALES QUANTITY (items sold per transaction)
- `transaction_amount`, `transaction_type`, `received_by`, `time_of_sale`

**Current TANAW Behavior (WRONG):**
```
quantity → mapped to "Quantity" canonical type
↓
TANAW generates: "Stock Level Overview" and "Low Stock Items"
↓
MISLEADING: Shows "quantity sold" as "stock levels"
```

**Expected TANAW Behavior (CORRECT):**
```
quantity + transaction_amount + date → SALES CONTEXT
↓
TANAW generates: "Product Performance" and "Sales Over Time"
↓
ACCURATE: Shows actual sales performance
```

---

## 🎯 ROOT CAUSE: AMBIGUOUS CANONICAL TYPE

### The "Quantity" Problem
The canonical type `Quantity` is **context-dependent**:

| Context | Meaning | Example Columns | Should Generate |
|---------|---------|-----------------|-----------------|
| **Sales** | Items sold per transaction | `quantity_sold`, `units_sold`, `qty` | Product Performance, Sales Trends |
| **Inventory** | Stock on hand | `stock_level`, `on_hand`, `available` | Stock Overview, Reorder Status |
| **Manufacturing** | Production output | `units_produced`, `output_qty` | Production Analysis |
| **Orders** | Items ordered | `order_quantity`, `requested_qty` | Order Analysis |

**Current Issue:** TANAW treats ALL `quantity` columns as inventory stock levels!

---

## 💡 SOLUTION: SEMANTIC CONTEXT DETECTION

### Phase 1: Dataset Context Analysis (IMPLEMENT FIRST)

#### A. Sales Dataset Indicators
Look for these **sibling columns**:
```python
SALES_INDICATORS = [
    # Transaction columns
    'transaction', 'sale', 'order', 'invoice', 'receipt',
    # Money columns
    'price', 'amount', 'revenue', 'total', 'payment',
    # Customer columns
    'customer', 'buyer', 'client',
    # Sales-specific
    'discount', 'promo', 'campaign'
]
```

**If found:** `quantity` = **Sales Quantity**
- Generate: Product Performance, Sales Trends, Revenue Analysis
- Do NOT generate: Stock Level, Reorder Status

#### B. Inventory Dataset Indicators
Look for these **sibling columns**:
```python
INVENTORY_INDICATORS = [
    # Stock columns
    'stock', 'inventory', 'warehouse', 'storage',
    # Reorder columns
    'reorder', 'min_stock', 'max_stock', 'threshold',
    # Supply chain
    'supplier', 'shipment', 'delivery',
    # Inventory-specific
    'turnover', 'sku', 'bin', 'location'
]
```

**If found:** `quantity` = **Stock Level**
- Generate: Stock Overview, Reorder Status, Turnover
- Do NOT generate: Product Performance (sales)

---

### Phase 2: Smart Chart Decision Logic

```python
def detect_dataset_context(df, column_mapping):
    """
    Analyze dataset structure to determine business context
    
    Returns: "sales", "inventory", "finance", "mixed", or "unknown"
    """
    
    all_columns = set(str(col).lower() for col in df.columns)
    
    # Count indicators
    sales_score = sum(1 for indicator in SALES_INDICATORS 
                     if indicator in ' '.join(all_columns))
    
    inventory_score = sum(1 for indicator in INVENTORY_INDICATORS 
                         if indicator in ' '.join(all_columns))
    
    # Determine primary context
    if sales_score > inventory_score and sales_score >= 2:
        return "sales"
    elif inventory_score > sales_score and inventory_score >= 2:
        return "inventory"
    elif sales_score > 0 and inventory_score > 0:
        return "mixed"  # Has both contexts
    else:
        return "unknown"  # Ambiguous

def generate_charts_by_context(df, context):
    """
    Generate appropriate charts based on detected context
    """
    charts = []
    
    if context == "sales":
        # SALES CHARTS ONLY
        charts.extend(generate_product_performance(df))  # quantity = sales
        charts.extend(generate_sales_trends(df))
        charts.extend(generate_revenue_analysis(df))
        # DO NOT generate stock/inventory charts
        
    elif context == "inventory":
        # INVENTORY CHARTS ONLY
        charts.extend(generate_stock_overview(df))  # quantity = stock
        charts.extend(generate_reorder_status(df))
        charts.extend(generate_inventory_turnover(df))
        # DO NOT generate sales performance charts
        
    elif context == "mixed":
        # BOTH - but need to distinguish columns
        # Use original column names to separate
        if "quantity_sold" in columns:
            charts.extend(generate_sales_charts(df, "quantity_sold"))
        if "stock_level" in columns:
            charts.extend(generate_inventory_charts(df, "stock_level"))
    
    return charts
```

---

## 🛠️ IMPLEMENTATION STEPS

### Step 1: Create Semantic Detector Module
**File:** `backend/analytics_service/semantic_detector.py`

```python
class TANAWSemanticDetector:
    """Detect business context from dataset structure"""
    
    def __init__(self):
        self.sales_indicators = [...]
        self.inventory_indicators = [...]
    
    def detect_context(self, df, column_mapping):
        """Main detection method"""
        pass
    
    def get_quantity_meaning(self, df, column_mapping):
        """Determine if 'quantity' means sales or stock"""
        pass
```

### Step 2: Integrate into app_clean.py
**Location:** `generate_analytics_and_charts()` method

```python
# Before chart generation
context = self.semantic_detector.detect_context(df, column_mapping)
print(f"📊 Detected dataset context: {context}")

# Pass context to chart generators
bar_charts = self.bar_chart_generator.generate_all_bar_charts(
    df, column_mapping, context=context
)
line_charts = self.line_chart_generator.generate_all_line_charts(
    df, column_mapping, context=context
)
```

### Step 3: Update Chart Generators
Modify `generate_all_bar_charts()` and `generate_all_line_charts()` to:
- Accept `context` parameter
- Skip inappropriate charts for the detected context
- Use context-aware column interpretation

### Step 4: Test with Real Datasets
Test files needed:
1. `SALES_CONTEXT_TEST.csv` - Pure sales data (like Balaji)
2. `INVENTORY_CONTEXT_TEST.csv` - Pure inventory data
3. `MIXED_CONTEXT_TEST.csv` - Both sales and inventory columns

---

## 🎯 SUCCESS CRITERIA

### For Balaji-Fast-Food-Sales.csv:
**Current (Wrong):**
- ❌ Generates: "Stock Level Overview" with quantity sold
- ❌ Generates: "Low Stock Items" with sales data

**After Implementation (Correct):**
- ✅ Detects: "sales" context
- ✅ Generates: "Product Performance" with quantity sold
- ✅ Generates: "Sales Over Time" with transaction data
- ✅ Does NOT generate: Stock/Inventory charts

### For Inventory Dataset:
**After Implementation:**
- ✅ Detects: "inventory" context
- ✅ Generates: "Stock Level Overview" with actual stock
- ✅ Generates: "Reorder Status" with stock data
- ✅ Does NOT generate: Product Performance (sales)

---

## 📊 CURRENT STATUS

### ✅ Completed:
1. Identified the semantic ambiguity problem
2. Analyzed root cause (rigid canonical types)
3. Designed semantic detection solution
4. Disabled Finance charts to focus on Sales/Inventory

### 🔄 In Progress:
- Implementing semantic detector module

### ⏳ Pending:
- Integration with chart generators
- Testing with real datasets
- User feedback loop for ambiguous cases

---

## 🚀 NEXT IMMEDIATE STEPS

1. **Create `semantic_detector.py`** with context detection logic
2. **Test detection** with Balaji-Fast-Food-Sales.csv
3. **Integrate** into `app_clean.py`
4. **Update** chart generators to respect context
5. **Verify** correct chart generation for both Sales and Inventory datasets

---

**Date Created:** 2025-10-21  
**Status:** Implementation Phase 1  
**Priority:** HIGH - Critical for accurate analytics

