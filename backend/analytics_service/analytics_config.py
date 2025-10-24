# analytics_config.py
"""
TANAW Analytics Configuration
Defines the 5 core analytics types and their required columns.
"""
from typing import Dict, List, Any
from enum import Enum


class ColumnType(str, Enum):
    """Standard column types for TANAW analytics."""
    DATE = "Date"
    SALES = "Sales"
    AMOUNT = "Amount"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    REGION = "Region"
    IGNORE = "Ignore"


class AnalyticsType(str, Enum):
    """Five core analytics types in TANAW."""
    SALES_SUMMARY = "Sales Summary Report"
    PRODUCT_PERFORMANCE = "Product Performance Analysis"
    REGIONAL_SALES = "Regional Sales Analysis"
    SALES_FORECASTING = "Sales Forecasting"
    DEMAND_FORECASTING = "Demand Forecasting"


# Analytics Requirements Configuration
ANALYTICS_REQUIREMENTS = {
    AnalyticsType.SALES_SUMMARY: {
        "type": "descriptive",
        "required_columns": [ColumnType.DATE, [ColumnType.SALES, ColumnType.AMOUNT]],
        "description": "Calculate total and average sales per period (daily, monthly, yearly)",
        "explanation": "Used to calculate total and average sales per period (daily, monthly, yearly).",
        "outputs": ["Total Sales", "Average Sales", "Sales by Period", "Sales Trend"]
    },
    AnalyticsType.PRODUCT_PERFORMANCE: {
        "type": "descriptive",
        "required_columns": [ColumnType.PRODUCT, [ColumnType.SALES, ColumnType.QUANTITY]],
        "description": "Identify which products are best or least performing",
        "explanation": "Identifies which products are best or least performing.",
        "outputs": ["Top Products", "Bottom Products", "Product Rankings", "Performance Metrics"]
    },
    AnalyticsType.REGIONAL_SALES: {
        "type": "descriptive",
        "required_columns": [ColumnType.REGION, [ColumnType.SALES, ColumnType.AMOUNT]],
        "description": "Compare total sales and growth across geographic regions",
        "explanation": "Compares total sales and growth across geographic regions.",
        "outputs": ["Sales by Region", "Regional Growth", "Regional Rankings", "Market Share"]
    },
    AnalyticsType.SALES_FORECASTING: {
        "type": "predictive",
        "required_columns": [ColumnType.DATE, [ColumnType.SALES, ColumnType.AMOUNT]],
        "description": "Forecast future revenue trends based on historical sales data",
        "explanation": "Forecasts future revenue trends based on historical sales data.",
        "outputs": ["30-Day Forecast", "90-Day Forecast", "Confidence Intervals", "Trend Analysis"]
    },
    AnalyticsType.DEMAND_FORECASTING: {
        "type": "predictive",
        "required_columns": [ColumnType.DATE, ColumnType.PRODUCT, ColumnType.QUANTITY],
        "description": "Predict future product demand levels to optimize inventory and production planning",
        "explanation": "Predicts future product demand levels to optimize inventory and production planning.",
        "outputs": ["Demand Forecast by Product", "Inventory Recommendations", "Production Planning"]
    }
}


# Required Columns for Dropdown Options
REQUIRED_COLUMNS = [
    ColumnType.DATE,
    ColumnType.SALES,
    ColumnType.AMOUNT,
    ColumnType.PRODUCT,
    ColumnType.QUANTITY,
    ColumnType.REGION,
    ColumnType.IGNORE
]


# Synonym mappings for each column type (for intelligent detection)
COLUMN_SYNONYMS = {
    ColumnType.DATE: [
        'date', 'time', 'timestamp', 'datetime', 'created_at', 'updated_at',
        'order_date', 'transaction_date', 'purchase_date', 'sale_date',
        'invoice_date', 'period', 'day', 'month', 'year', 'dt'
    ],
    ColumnType.SALES: [
        'sales', 'revenue', 'income', 'earnings', 'turnover', 'gross_sales',
        'net_sales', 'total_sales', 'sale_amount', 'sales_amount'
    ],
    ColumnType.AMOUNT: [
        'amount', 'amt', 'total', 'total_amount', 'price', 'value',
        'cost', 'total_price', 'sum', 'grand_total'
    ],
    ColumnType.PRODUCT: [
        'product', 'item', 'sku', 'product_name', 'item_name', 'product_id',
        'item_id', 'goods', 'merchandise', 'article', 'product_code', 'prod'
    ],
    ColumnType.QUANTITY: [
        'quantity', 'qty', 'units', 'volume', 'count', 'pieces', 'items',
        'number', 'amount_sold', 'units_sold', 'sold', 'stock'
    ],
    ColumnType.REGION: [
        'region', 'area', 'territory', 'zone', 'district', 'location',
        'city', 'state', 'country', 'province', 'market', 'geo'
    ]
}


# Semantic descriptions for SBERT matching
COLUMN_SEMANTIC_DESCRIPTIONS = {
    ColumnType.DATE: "date time timestamp when temporal period day month year",
    ColumnType.SALES: "sales revenue income earnings money sold",
    ColumnType.AMOUNT: "amount total value price cost sum",
    ColumnType.PRODUCT: "product item sku name goods merchandise what",
    ColumnType.QUANTITY: "quantity units count volume how many number",
    ColumnType.REGION: "region area location territory where geographic place"
}


def get_required_columns_for_analytic(analytic_type: AnalyticsType) -> List[str]:
    """
    Get the required columns for a specific analytics type.
    
    Args:
        analytic_type: The analytics type
        
    Returns:
        List of required column types
    """
    requirements = ANALYTICS_REQUIREMENTS.get(analytic_type, {})
    required = requirements.get("required_columns", [])
    
    # Flatten nested lists (for OR requirements like Sales OR Amount)
    flattened = []
    for col in required:
        if isinstance(col, list):
            flattened.append(col)  # Keep as list to indicate OR condition
        else:
            flattened.append(col)
    
    return flattened


def check_analytics_readiness(column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Check which analytics can be performed based on available columns.
    
    Args:
        column_mapping: Dictionary mapping original columns to standard types
        
    Returns:
        Dictionary with analytics readiness status
    """
    readiness = {}
    available_columns = set(column_mapping.values())
    
    for analytic_type, config in ANALYTICS_REQUIREMENTS.items():
        required = config["required_columns"]
        can_perform = True
        missing_columns = []
        
        for requirement in required:
            if isinstance(requirement, list):
                # OR condition - at least one must be present
                if not any(col.value in available_columns for col in requirement):
                    can_perform = False
                    missing_columns.append(f"One of: {', '.join([c.value for c in requirement])}")
            else:
                # Single requirement
                if requirement.value not in available_columns:
                    can_perform = False
                    missing_columns.append(requirement.value)
        
        readiness[analytic_type.value] = {
            "can_perform": can_perform,
            "required_columns": [
                [c.value for c in req] if isinstance(req, list) else req.value
                for req in required
            ],
            "missing_columns": missing_columns,
            "type": config["type"],
            "description": config["description"],
            "explanation": config["explanation"]
        }
    
    return readiness


def get_dropdown_options() -> List[str]:
    """
    Get the list of options for column mapping dropdowns.
    
    Returns:
        List of column type options
    """
    return [col.value for col in REQUIRED_COLUMNS]


def get_canonical_column_name(column_type: str) -> str:
    """
    Get the canonical name for a column type.
    Handles Sales/Amount being interchangeable.
    
    Args:
        column_type: The column type string
        
    Returns:
        Canonical column name
    """
    if column_type in [ColumnType.SALES.value, ColumnType.AMOUNT.value]:
        return "Sales/Amount"
    return column_type


def get_analytics_summary() -> Dict[str, Any]:
    """
    Get a comprehensive summary of all analytics configurations.
    
    Returns:
        Summary dictionary
    """
    return {
        "total_analytics": len(ANALYTICS_REQUIREMENTS),
        "descriptive_analytics": [
            k.value for k, v in ANALYTICS_REQUIREMENTS.items() if v["type"] == "descriptive"
        ],
        "predictive_analytics": [
            k.value for k, v in ANALYTICS_REQUIREMENTS.items() if v["type"] == "predictive"
        ],
        "required_columns": [col.value for col in REQUIRED_COLUMNS if col != ColumnType.IGNORE],
        "column_synonyms_count": {
            col.value: len(synonyms) for col, synonyms in COLUMN_SYNONYMS.items()
        }
    }


if __name__ == "__main__":
    # Test the configuration
    print("=" * 70)
    print("TANAW ANALYTICS CONFIGURATION")
    print("=" * 70)
    
    print("\n📊 ANALYTICS TYPES:")
    for analytic_type, config in ANALYTICS_REQUIREMENTS.items():
        print(f"\n{analytic_type.value} ({config['type'].upper()})")
        print(f"  Description: {config['description']}")
        print(f"  Required Columns: {config['required_columns']}")
        print(f"  Outputs: {', '.join(config['outputs'])}")
    
    print("\n\n🗂️ REQUIRED COLUMNS:")
    for col_type in REQUIRED_COLUMNS:
        if col_type != ColumnType.IGNORE:
            synonyms = COLUMN_SYNONYMS.get(col_type, [])
            print(f"\n{col_type.value}:")
            print(f"  Synonyms: {', '.join(synonyms[:10])}...")
    
    print("\n\n✅ DROPDOWN OPTIONS:")
    print(get_dropdown_options())
    
    print("\n\n📈 ANALYTICS SUMMARY:")
    import json
    print(json.dumps(get_analytics_summary(), indent=2))

