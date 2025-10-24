"""
TANAW Canonical Schema Definition
Phase 1: Design & Preparation

This module defines the master canonical schema and maps each analytic type
to its specific column requirements for the hybrid column mapping pipeline.
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

class CanonicalColumnType(Enum):
    """Master canonical schema - 8 key standard columns covering all analytics."""
    DATE = "Date"
    SALES = "Sales" 
    AMOUNT = "Amount"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    REGION = "Region"
    CUSTOMER = "Customer"
    TRANSACTION_ID = "Transaction_ID"

class AnalyticType(Enum):
    """Core analytics types supported by TANAW."""
    SALES_SUMMARY = "sales_summary"
    PRODUCT_PERFORMANCE = "product_performance"
    REGIONAL_SALES = "regional_sales"
    SALES_FORECASTING = "sales_forecasting"
    DEMAND_FORECASTING = "demand_forecasting"

class ConfidenceLevel(Enum):
    """Confidence thresholds for hybrid mapping decisions."""
    AUTO_MAP = 0.90        # ≥ 0.90: Auto-map silently
    SUGGESTED = 0.70       # 0.70-0.89: Suggest mapping (optional review)
    UNCERTAIN = 0.70       # < 0.70: Require confirmation or send to GPT

@dataclass
class ColumnRequirement:
    """Defines column requirements for specific analytics."""
    canonical_type: CanonicalColumnType
    is_required: bool
    alternatives: Set[CanonicalColumnType]  # Alternative columns that can satisfy this requirement
    description: str

@dataclass
class AnalyticRequirement:
    """Maps each analytic to its required columns."""
    analytic_type: AnalyticType
    display_name: str
    description: str
    required_columns: List[ColumnRequirement]
    purpose: str

class TANAWCanonicalSchema:
    """
    Master schema manager for TANAW's hybrid column mapping pipeline.
    
    Defines the canonical schema and maps each of the 5 core analytics
    to their specific column requirements.
    """
    
    def __init__(self):
        self.canonical_columns = self._define_canonical_columns()
        self.analytic_requirements = self._define_analytic_requirements()
        self.confidence_thresholds = self._define_confidence_thresholds()
    
    def _define_canonical_columns(self) -> Dict[CanonicalColumnType, Dict[str, Any]]:
        """Define the master canonical schema with metadata."""
        return {
            CanonicalColumnType.DATE: {
                "aliases": [
                    "date", "timestamp", "time", "created_at", "order_date", "sale_date",
                    "transaction_date", "dt", "datetime", "date_time", "when", "period"
                ],
                "description": "Date/time field for temporal analysis",
                "data_types": ["datetime", "date", "timestamp", "object"],
                "patterns": [r"\d{4}-\d{2}-\d{2}", r"\d{2}/\d{2}/\d{4}", r"\w+ \d{1,2}, \d{4}"]
            },
            CanonicalColumnType.SALES: {
                "aliases": [
                    "sales", "revenue", "sales_amount", "total_sales", "net_sales",
                    "gross_sales", "sales_value", "turnover", "income"
                ],
                "description": "Primary sales/revenue monetary value",
                "data_types": ["float64", "int64", "float32", "int32"],
                "patterns": [r"^\$?\d+\.?\d*$"]
            },
            CanonicalColumnType.AMOUNT: {
                "aliases": [
                    "amount", "price", "cost", "value", "total", "sum", "total_amount",
                    "unit_price", "selling_price", "retail_price", "money", "payment"
                ],
                "description": "Monetary amount/value field",
                "data_types": ["float64", "int64", "float32", "int32"],
                "patterns": [r"^\$?\d+\.?\d*$"]
            },
            CanonicalColumnType.PRODUCT: {
                "aliases": [
                    "product", "item", "sku", "product_name", "product_id", "item_name",
                    "product_desc", "product_description", "merchandise", "goods", "article"
                ],
                "description": "Product identifier or name",
                "data_types": ["object", "string", "category"],
                "patterns": [r"^[A-Za-z0-9\-_\s]+$"]
            },
            CanonicalColumnType.QUANTITY: {
                "aliases": [
                    "quantity", "qty", "units", "volume", "count", "quantity_sold",
                    "units_sold", "pieces", "amount_qty", "vol", "number"
                ],
                "description": "Quantity or count of items",
                "data_types": ["int64", "float64", "int32", "float32"],
                "patterns": [r"^\d+\.?\d*$"]
            },
            CanonicalColumnType.REGION: {
                "aliases": [
                    "region", "location", "area", "territory", "branch", "zone", "district",
                    "region_name", "geographic_area", "market", "locality", "place"
                ],
                "description": "Geographic or organizational region",
                "data_types": ["object", "string", "category"],
                "patterns": [r"^[A-Za-z\s\-]+$"]
            },
            CanonicalColumnType.CUSTOMER: {
                "aliases": [
                    "customer", "client", "customer_id", "customer_name", "buyer",
                    "purchaser", "client_id", "account", "customer_type", "cust"
                ],
                "description": "Customer identifier or information",
                "data_types": ["object", "string", "category", "int64"],
                "patterns": [r"^[A-Za-z0-9\s\-_]+$"]
            },
            CanonicalColumnType.TRANSACTION_ID: {
                "aliases": [
                    "transaction_id", "txn_id", "order_id", "sale_id", "receipt_id",
                    "invoice_id", "reference", "ref", "id", "transaction_number"
                ],
                "description": "Unique transaction identifier",
                "data_types": ["object", "string", "int64", "category"],
                "patterns": [r"^[A-Za-z0-9\-_]+$"]
            }
        }
    
    def _define_analytic_requirements(self) -> Dict[AnalyticType, AnalyticRequirement]:
        """Define column requirements for each of the 5 core analytics."""
        return {
            AnalyticType.SALES_SUMMARY: AnalyticRequirement(
                analytic_type=AnalyticType.SALES_SUMMARY,
                display_name="Sales Summary Report",
                description="Calculates total and average sales by time period",
                required_columns=[
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.DATE,
                        is_required=True,
                        alternatives=set(),
                        description="Date field for temporal grouping"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.SALES,
                        is_required=False,  # Either SALES or AMOUNT is required
                        alternatives={CanonicalColumnType.AMOUNT},
                        description="Sales value or monetary amount"
                    )
                ],
                purpose="Provides insights into sales trends over daily, monthly, and yearly periods"
            ),
            
            AnalyticType.PRODUCT_PERFORMANCE: AnalyticRequirement(
                analytic_type=AnalyticType.PRODUCT_PERFORMANCE,
                display_name="Product Performance Analysis",
                description="Identifies top- and low-performing products",
                required_columns=[
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.PRODUCT,
                        is_required=True,
                        alternatives=set(),
                        description="Product identifier for grouping"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.SALES,
                        is_required=False,  # Either SALES or QUANTITY is required
                        alternatives={CanonicalColumnType.QUANTITY},
                        description="Performance metric (sales value or quantity)"
                    )
                ],
                purpose="Helps identify which products drive the most revenue and which need attention"
            ),
            
            AnalyticType.REGIONAL_SALES: AnalyticRequirement(
                analytic_type=AnalyticType.REGIONAL_SALES,
                display_name="Regional Sales Analysis",
                description="Compares total sales and growth across regions",
                required_columns=[
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.REGION,
                        is_required=True,
                        alternatives=set(),
                        description="Geographic region for comparison"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.SALES,
                        is_required=False,  # Either SALES or AMOUNT is required
                        alternatives={CanonicalColumnType.AMOUNT},
                        description="Sales value for regional comparison"
                    )
                ],
                purpose="Provides geographical insights for market expansion and resource allocation"
            ),
            
            AnalyticType.SALES_FORECASTING: AnalyticRequirement(
                analytic_type=AnalyticType.SALES_FORECASTING,
                display_name="Sales Forecasting",
                description="Predicts future revenue trends using past sales data",
                required_columns=[
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.DATE,
                        is_required=True,
                        alternatives=set(),
                        description="Time series date field for forecasting"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.SALES,
                        is_required=False,  # Either SALES or AMOUNT is required
                        alternatives={CanonicalColumnType.AMOUNT},
                        description="Historical sales data for prediction model"
                    )
                ],
                purpose="Enables proactive business planning and revenue projection"
            ),
            
            AnalyticType.DEMAND_FORECASTING: AnalyticRequirement(
                analytic_type=AnalyticType.DEMAND_FORECASTING,
                display_name="Demand Forecasting", 
                description="Predicts future product demand for inventory optimization",
                required_columns=[
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.DATE,
                        is_required=True,
                        alternatives=set(),
                        description="Time series date field"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.PRODUCT,
                        is_required=True,
                        alternatives=set(),
                        description="Product identifier for demand tracking"
                    ),
                    ColumnRequirement(
                        canonical_type=CanonicalColumnType.QUANTITY,
                        is_required=True,
                        alternatives=set(),
                        description="Quantity data for demand prediction"
                    )
                ],
                purpose="Optimizes inventory management and prevents stockouts/overstock"
            )
        }
    
    def _define_confidence_thresholds(self) -> Dict[str, float]:
        """Define confidence thresholds for mapping decisions."""
        return {
            "auto_map_threshold": ConfidenceLevel.AUTO_MAP.value,
            "suggestion_threshold": ConfidenceLevel.SUGGESTED.value,
            "uncertain_threshold": ConfidenceLevel.UNCERTAIN.value,
            "gpt_escalation_threshold": ConfidenceLevel.UNCERTAIN.value
        }
    
    def get_canonical_aliases(self, canonical_type: CanonicalColumnType) -> List[str]:
        """Get all known aliases for a canonical column type."""
        return self.canonical_columns[canonical_type]["aliases"]
    
    def get_all_aliases(self) -> Dict[str, CanonicalColumnType]:
        """Get flattened mapping of all aliases to canonical types."""
        alias_mapping = {}
        for canonical_type, metadata in self.canonical_columns.items():
            for alias in metadata["aliases"]:
                alias_mapping[alias.lower()] = canonical_type
        return alias_mapping
    
    def check_analytic_feasibility(self, mapped_columns: Dict[str, CanonicalColumnType]) -> Dict[AnalyticType, bool]:
        """
        Check which analytics can be performed given the mapped columns.
        
        Args:
            mapped_columns: Dictionary mapping user column names to canonical types
            
        Returns:
            Dictionary indicating which analytics are feasible
        """
        available_types = set(mapped_columns.values())
        feasible_analytics = {}
        
        for analytic_type, requirement in self.analytic_requirements.items():
            can_perform = True
            
            for col_req in requirement.required_columns:
                # Check if the required column type is available
                has_required = col_req.canonical_type in available_types
                
                # Check if any alternative is available
                has_alternative = bool(col_req.alternatives & available_types)
                
                # If it's required and we don't have it or an alternative, can't perform
                if col_req.is_required and not (has_required or has_alternative):
                    can_perform = False
                    break
                
                # For flexible requirements (either/or), check if at least one is available
                if not col_req.is_required and col_req.alternatives:
                    if not (has_required or has_alternative):
                        can_perform = False
                        break
            
            feasible_analytics[analytic_type] = can_perform
        
        return feasible_analytics
    
    def get_analytics_summary(self, mapped_columns: Dict[str, CanonicalColumnType]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of available analytics based on mapped columns.
        
        Returns:
            Summary including feasible analytics, missing requirements, and recommendations
        """
        feasible = self.check_analytic_feasibility(mapped_columns)
        available_types = set(mapped_columns.values())
        
        summary = {
            "total_analytics": len(self.analytic_requirements),
            "feasible_analytics": sum(feasible.values()),
            "available_analytics": [],
            "unavailable_analytics": [],
            "missing_columns": [],
            "recommendations": []
        }
        
        for analytic_type, is_feasible in feasible.items():
            requirement = self.analytic_requirements[analytic_type]
            
            if is_feasible:
                summary["available_analytics"].append({
                    "type": analytic_type.value,
                    "name": requirement.display_name,
                    "description": requirement.description,
                    "purpose": requirement.purpose
                })
            else:
                # Find missing columns
                missing = []
                for col_req in requirement.required_columns:
                    has_required = col_req.canonical_type in available_types
                    has_alternative = bool(col_req.alternatives & available_types)
                    
                    if col_req.is_required and not (has_required or has_alternative):
                        missing.append(col_req.canonical_type.value)
                    elif not col_req.is_required and col_req.alternatives and not (has_required or has_alternative):
                        alternatives_list = [alt.value for alt in col_req.alternatives]
                        missing.append(f"{col_req.canonical_type.value} OR {' OR '.join(alternatives_list)}")
                
                summary["unavailable_analytics"].append({
                    "type": analytic_type.value,
                    "name": requirement.display_name,
                    "missing_columns": missing
                })
        
        # Generate recommendations
        if summary["feasible_analytics"] < summary["total_analytics"]:
            missing_types = set()
            for analytic_type, is_feasible in feasible.items():
                if not is_feasible:
                    requirement = self.analytic_requirements[analytic_type]
                    for col_req in requirement.required_columns:
                        if col_req.canonical_type not in available_types:
                            missing_types.add(col_req.canonical_type.value)
                        for alt in col_req.alternatives:
                            if alt not in available_types:
                                missing_types.add(alt.value)
            
            summary["recommendations"] = [
                f"Consider adding {col_type} data to unlock more analytics"
                for col_type in sorted(missing_types)
            ]
        
        return summary

# Global instance for easy access
tanaw_schema = TANAWCanonicalSchema()
