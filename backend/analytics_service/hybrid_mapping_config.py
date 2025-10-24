"""
Hybrid Mapping Configuration
Phase 1: Configuration settings for the hybrid column mapping pipeline

This module defines all configuration parameters, thresholds, and settings
for the confidence-based hybrid mapping system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class MappingThresholds:
    """Confidence thresholds for mapping decisions."""
    auto_map: float = 0.90          # ≥ 0.90: Auto-map silently
    suggested_min: float = 0.70     # 0.70-0.89: Suggest mapping (optional review)
    suggested_max: float = 0.89     # Upper bound for suggestions
    uncertain: float = 0.70         # < 0.70: Require confirmation
    gpt_escalation: float = 0.70    # Send to GPT if below this threshold
    
@dataclass
class LocalAnalyzerConfig:
    """Configuration for the local analyzer (first pass)."""
    # Rule-based matching weight
    rule_weight: float = 0.4
    
    # Fuzzy matching configuration
    fuzzy_weight: float = 0.3
    fuzzy_threshold: float = 0.75   # Minimum fuzzy similarity score
    
    # Type heuristics weight
    type_weight: float = 0.3
    
    # Alias matching configuration
    enable_partial_aliases: bool = True
    alias_min_length: int = 3
    
    # Normalization settings
    normalize_case: bool = True
    remove_punctuation: bool = True
    replace_underscores: bool = True
    trim_whitespace: bool = True

@dataclass
class GPTConfig:
    """Configuration for GPT escalation (second pass)."""
    # API configuration
    model: str = "gpt-4o-mini"  # Most cost-effective and accurate model
    max_tokens: int = 500
    temperature: float = 0.1
    
    # Request settings
    max_columns_per_request: int = 10  # Batch size for GPT requests
    timeout_seconds: int = 30
    max_retries: int = 3
    
    # Cost optimization
    enable_caching: bool = True
    cache_ttl_hours: int = 24
    
    # Prompt configuration
    include_sample_data: bool = False   # Never send actual data to GPT
    include_analytics_context: bool = True
    max_context_length: int = 2000

@dataclass
class UIConfig:
    """Configuration for user interface components."""
    # Dropdown settings
    max_suggestions_per_column: int = 3
    show_confidence_scores: bool = True
    enable_ignore_option: bool = True
    
    # Display settings
    show_analytics_preview: bool = True
    highlight_uncertain_mappings: bool = True
    
    # Interaction settings
    auto_submit_high_confidence: bool = False  # Always show for user review
    enable_bulk_actions: bool = True

@dataclass
class KnowledgeBaseConfig:
    """Configuration for the mapping knowledge base."""
    # Storage settings
    database_type: str = "sqlite"  # or "mongodb" for production
    connection_string: str = "tanaw_mapping_kb.db"
    
    # Learning settings
    enable_learning: bool = True
    min_confirmations_for_auto: int = 3  # Require multiple confirmations
    confidence_decay_days: int = 90      # Reduce confidence over time
    
    # Reuse settings
    enable_cross_user_learning: bool = False  # Privacy: per-user only
    enable_global_dictionary: bool = True  # Build shared alias list (anonymous)
    similarity_threshold_for_reuse: float = 0.85

@dataclass
class AnalyticsActivationConfig:
    """Configuration for analytics activation logic."""
    # Requirements checking
    strict_requirements: bool = True    # Must meet all required columns
    enable_partial_analytics: bool = False  # Don't run partial analytics
    
    # User notification
    show_missing_columns: bool = True
    suggest_data_improvements: bool = True
    
    # Performance settings
    check_data_quality: bool = True
    min_data_points: int = 10
    max_null_percentage: float = 0.3

class HybridMappingConfig:
    """
    Central configuration manager for the hybrid mapping pipeline.
    
    Manages all configuration settings and provides environment-specific
    configurations for development, testing, and production.
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.thresholds = MappingThresholds()
        self.local_analyzer = LocalAnalyzerConfig()
        self.gpt_config = GPTConfig()
        self.ui_config = UIConfig()
        self.knowledge_base = KnowledgeBaseConfig()
        self.analytics_activation = AnalyticsActivationConfig()
        
        # Load environment-specific overrides
        self._load_environment_config()
    
    def _load_environment_config(self):
        """Load environment-specific configuration overrides."""
        if self.environment == "production":
            # Production optimizations
            self.gpt_config.model = "gpt-4o-mini"  # More cost-effective
            self.gpt_config.enable_caching = True
            self.knowledge_base.database_type = "mongodb"
            self.knowledge_base.enable_cross_user_learning = False  # Privacy first
            
        elif self.environment == "testing":
            # Testing configurations
            self.gpt_config.timeout_seconds = 5
            self.gpt_config.max_retries = 1
            self.knowledge_base.connection_string = "test_tanaw_mapping_kb.db"
            self.analytics_activation.min_data_points = 5
            
        elif self.environment == "development":
            # Development configurations
            self.ui_config.show_confidence_scores = True
            self.gpt_config.temperature = 0.2  # More deterministic for testing
    
    def get_analytics_requirements(self) -> Dict[str, List[str]]:
        """Get the required columns for each TANAW analytics type."""
        return {
            "Sales Summary Report": ["Date", ["Sales", "Amount"]],
            "Product Performance Analysis": ["Product", ["Sales", "Quantity"]],
            "Regional Sales Analysis": ["Region", ["Sales", "Amount"]],
            "Sales Forecasting": ["Date", ["Sales", "Amount"]],
            "Demand Forecasting": ["Date", "Product", "Quantity"]
        }
    
    def check_analytics_readiness(self, mapped_columns: Dict[str, str]) -> Dict[str, Any]:
        """
        Check which analytics are ready based on mapped columns.
        
        Args:
            mapped_columns: Dictionary of {original_column: mapped_canonical_type}
            
        Returns:
            Dictionary with analytics readiness status
        """
        requirements = self.get_analytics_requirements()
        readiness = {}
        
        for analytic_name, required_cols in requirements.items():
            is_ready = True
            missing_cols = []
            
            for req_col in required_cols:
                if isinstance(req_col, list):
                    # OR condition (e.g., ["Sales", "Amount"])
                    has_any = any(req_col in mapped_columns.values() for req_col in req_col)
                    if not has_any:
                        is_ready = False
                        missing_cols.append(f"({' OR '.join(req_col)})")
                else:
                    # Single required column
                    if req_col not in mapped_columns.values():
                        is_ready = False
                        missing_cols.append(req_col)
            
            readiness[analytic_name] = {
                "ready": is_ready,
                "missing_columns": missing_cols if not is_ready else [],
                "required_columns": required_cols
            }
        
        return readiness
    
    def get_prompt_template(self) -> str:
        """Get the GPT prompt template for column mapping."""
        return """You are a data analyst helping map column headers to a standardized schema for business analytics.

CONTEXT:
- Business: SME (Small-Medium Enterprise) 
- Goal: Enable 5 core analytics: Sales Summary, Product Performance, Regional Analysis, Sales Forecasting, Demand Forecasting
- Privacy: You will NEVER receive actual data, only column headers

CANONICAL SCHEMA (8 standard columns):
1. Date - Date/time fields
2. Sales - Primary sales/revenue amounts  
3. Amount - Monetary values/prices
4. Product - Product names/IDs/categories
5. Quantity - Quantities/counts/units
6. Region - Geographic locations/areas
7. Customer - Customer IDs/names/types
8. Transaction_ID - Unique identifiers

ANALYTICS REQUIREMENTS:
- Sales Summary: Needs Date + (Sales OR Amount)
- Product Performance: Needs Product + (Sales OR Quantity) 
- Regional Analysis: Needs Region + (Sales OR Amount)
- Sales Forecasting: Needs Date + (Sales OR Amount)
- Demand Forecasting: Needs Date + Product + Quantity

TASK:
Map these column headers to the canonical schema: {column_headers}

RULES:
1. Map each header to the MOST LIKELY canonical column type
2. Use "null" if no reasonable mapping exists
3. Provide confidence score 0-100 for each mapping
4. Consider the analytics context - prioritize columns that enable analytics

RESPONSE FORMAT (JSON only):
{{
  "mappings": [
    {{"original": "column_name", "mapped_to": "canonical_type", "confidence": 85, "reasoning": "brief explanation"}}
  ]
}}"""

    def get_local_analyzer_rules(self) -> Dict[str, List[str]]:
        """Get the rule-based mapping dictionary for local analyzer."""
        return {
            # Date variations
            "Date": [
                "date", "dt", "datetime", "timestamp", "time", "created_at", "order_date",
                "sale_date", "transaction_date", "txn_date", "when", "period", "day",
                "month", "year", "fecha", "datum"
            ],
            
            # Sales variations  
            "Sales": [
                "sales", "revenue", "sales_amount", "total_sales", "net_sales",
                "gross_sales", "sales_value", "turnover", "income", "earnings",
                "proceeds", "receipts", "sales_rev", "rev"
            ],
            
            # Amount variations
            "Amount": [
                "amount", "price", "cost", "value", "total", "sum", "total_amount",
                "unit_price", "selling_price", "retail_price", "money", "payment",
                "charge", "fee", "rate", "amt", "val", "precio", "costo"
            ],
            
            # Product variations
            "Product": [
                "product", "item", "sku", "product_name", "product_id", "item_name",
                "product_desc", "product_description", "merchandise", "goods", "article",
                "prod", "item_id", "catalog", "inventory", "producto", "articulo"
            ],
            
            # Quantity variations
            "Quantity": [
                "quantity", "qty", "units", "volume", "count", "quantity_sold",
                "units_sold", "pieces", "amount_qty", "vol", "number", "num",
                "sold", "qtd", "cantidad", "unidades"
            ],
            
            # Region variations
            "Region": [
                "region", "location", "area", "territory", "branch", "zone", "district",
                "region_name", "geographic_area", "market", "locality", "place", "city",
                "state", "country", "loc", "geo", "region", "zona"
            ],
            
            # Customer variations
            "Customer": [
                "customer", "client", "customer_id", "customer_name", "buyer",
                "purchaser", "client_id", "account", "customer_type", "cust",
                "client_name", "consumer", "cliente", "comprador"
            ],
            
            # Transaction ID variations
            "Transaction_ID": [
                "transaction_id", "txn_id", "order_id", "sale_id", "receipt_id",
                "invoice_id", "reference", "ref", "id", "transaction_number",
                "order_number", "receipt_no", "invoice_no", "trans_id"
            ]
        }
    
    def save_config(self, filepath: str):
        """Save current configuration to JSON file."""
        config_dict = {
            "environment": self.environment,
            "thresholds": self.thresholds.__dict__,
            "local_analyzer": self.local_analyzer.__dict__,
            "gpt_config": self.gpt_config.__dict__,
            "ui_config": self.ui_config.__dict__,
            "knowledge_base": self.knowledge_base.__dict__,
            "analytics_activation": self.analytics_activation.__dict__
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_config(cls, filepath: str) -> 'HybridMappingConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        instance = cls(config_dict.get("environment", "development"))
        
        # Update configurations
        if "thresholds" in config_dict:
            for key, value in config_dict["thresholds"].items():
                setattr(instance.thresholds, key, value)
        
        if "local_analyzer" in config_dict:
            for key, value in config_dict["local_analyzer"].items():
                setattr(instance.local_analyzer, key, value)
        
        # ... similar updates for other configs
        
        return instance

# Global configuration instance
hybrid_config = HybridMappingConfig()
