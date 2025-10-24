"""
Configuration for GPT-powered column mapping.
"""

import os
from typing import Dict, Any

class GPTConfig:
    """Configuration for GPT column mapping."""
    
    # OpenAI API Configuration
    API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL = "gpt-4o-mini"  # Cost-effective model
    TEMPERATURE = 0.1  # Low temperature for consistent results
    MAX_TOKENS = 500  # Limit tokens for cost control
    
    # Cost Optimization
    CACHE_ENABLED = True
    CACHE_DB_PATH = "tanaw_mapping_cache.db"
    SIMILARITY_THRESHOLD = 0.85  # For cache matching
    
    # Retail-specific settings
    RETAIL_CONTEXT = "retail"
    CANONICAL_TYPES = [
        'Date',      # Time series data
        'Sales',     # Monetary values  
        'Product',   # Product identifiers
        'Region',    # Geographic locations
        'Quantity'   # Volume metrics
    ]
    
    # Analytics requirements for TANAW
    ANALYTICS_REQUIREMENTS = {
        'Sales Summary Report': {
            'required_columns': ['Date', 'Sales'],
            'optional_columns': ['Product', 'Region'],
            'priority': 1
        },
        'Product Performance Analysis': {
            'required_columns': ['Product', 'Sales'],
            'optional_columns': ['Quantity', 'Date', 'Region'],
            'priority': 1
        },
        'Regional Sales Analysis': {
            'required_columns': ['Region', 'Sales'],
            'optional_columns': ['Date', 'Product'],
            'priority': 1
        },
        'Sales Forecasting': {
            'required_columns': ['Date', 'Sales'],
            'optional_columns': ['Region', 'Product'],
            'priority': 2
        },
        'Demand Forecasting': {
            'required_columns': ['Date', 'Product', 'Quantity'],
            'optional_columns': ['Region'],
            'priority': 2
        }
    }
    
    # Cost tracking
    COST_LIMITS = {
        'daily_limit': 1.0,  # $1 per day
        'monthly_limit': 10.0,  # $10 per month
        'per_request_limit': 0.01  # $0.01 per request
    }
    
    # Fallback settings
    FALLBACK_ENABLED = True
    FALLBACK_CONFIDENCE_THRESHOLD = 70.0
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return {
            'api_key': cls.API_KEY,
            'model': cls.MODEL,
            'temperature': cls.TEMPERATURE,
            'max_tokens': cls.MAX_TOKENS,
            'cache_enabled': cls.CACHE_ENABLED,
            'cache_db_path': cls.CACHE_DB_PATH,
            'similarity_threshold': cls.SIMILARITY_THRESHOLD,
            'retail_context': cls.RETAIL_CONTEXT,
            'canonical_types': cls.CANONICAL_TYPES,
            'analytics_requirements': cls.ANALYTICS_REQUIREMENTS,
            'cost_limits': cls.COST_LIMITS,
            'fallback_enabled': cls.FALLBACK_ENABLED,
            'fallback_confidence_threshold': cls.FALLBACK_CONFIDENCE_THRESHOLD
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings."""
        if not cls.API_KEY:
            print("❌ OPENAI_API_KEY not found in environment variables")
            return False
        
        if cls.COST_LIMITS['daily_limit'] <= 0:
            print("❌ Daily cost limit must be positive")
            return False
        
        if cls.FALLBACK_CONFIDENCE_THRESHOLD < 0 or cls.FALLBACK_CONFIDENCE_THRESHOLD > 100:
            print("❌ Fallback confidence threshold must be between 0 and 100")
            return False
        
        return True
