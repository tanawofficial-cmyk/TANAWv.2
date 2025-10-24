# analytics_requirements.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AnalyticsType(Enum):
    """Enumeration of available analytics types in TANAW."""
    SALES_SUMMARY = "sales_summary"
    PRODUCT_PERFORMANCE = "product_performance"
    REGIONAL_ANALYSIS = "regional_analysis"
    CUSTOMER_ANALYSIS = "customer_analysis"
    TIME_SERIES_FORECASTING = "time_series_forecasting"
    CORRELATION_ANALYSIS = "correlation_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PROFITABILITY_ANALYSIS = "profitability_analysis"
    SEASONAL_ANALYSIS = "seasonal_analysis"

@dataclass
class ColumnRequirement:
    """Defines a column requirement for an analytics type."""
    column_type: str  # e.g., 'date', 'sales', 'product', 'region'
    required: bool    # Whether this column is mandatory
    alternatives: List[str]  # Alternative column types that can satisfy this requirement
    confidence_threshold: float  # Minimum confidence required for auto-mapping
    description: str  # Human-readable description

@dataclass
class AnalyticsRequirement:
    """Defines requirements for a specific analytics type."""
    analytics_type: AnalyticsType
    name: str
    description: str
    required_columns: List[ColumnRequirement]
    optional_columns: List[ColumnRequirement]
    min_data_points: int
    estimated_complexity: str  # 'low', 'medium', 'high'
    output_types: List[str]  # ['chart', 'table', 'insight', 'forecast']

class AnalyticsRequirementsManager:
    """Manages analytics requirements and determines which analytics are feasible."""
    
    def __init__(self):
        self.requirements = self._initialize_requirements()
    
    def _initialize_requirements(self) -> Dict[AnalyticsType, AnalyticsRequirement]:
        """Initialize all analytics requirements."""
        return {
            AnalyticsType.SALES_SUMMARY: AnalyticsRequirement(
                analytics_type=AnalyticsType.SALES_SUMMARY,
                name="Sales Summary Report",
                description="Comprehensive overview of sales performance including totals, trends, and key metrics",
                required_columns=[
                    ColumnRequirement(
                        column_type="date",
                        required=True,
                        alternatives=["timestamp", "time", "created_at", "order_date"],
                        confidence_threshold=80.0,
                        description="Date field for temporal analysis"
                    ),
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "price", "cost", "value"],
                        confidence_threshold=85.0,
                        description="Sales amount or revenue field"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="product",
                        required=False,
                        alternatives=["item", "sku", "product_name", "category"],
                        confidence_threshold=75.0,
                        description="Product identifier for product-level analysis"
                    ),
                    ColumnRequirement(
                        column_type="region",
                        required=False,
                        alternatives=["location", "area", "territory", "branch"],
                        confidence_threshold=75.0,
                        description="Geographic or organizational region"
                    ),
                    ColumnRequirement(
                        column_type="quantity",
                        required=False,
                        alternatives=["qty", "units", "volume", "count"],
                        confidence_threshold=75.0,
                        description="Quantity of items sold"
                    )
                ],
                min_data_points=30,
                estimated_complexity="medium",
                output_types=["chart", "table", "insight"]
            ),
            
            AnalyticsType.PRODUCT_PERFORMANCE: AnalyticsRequirement(
                analytics_type=AnalyticsType.PRODUCT_PERFORMANCE,
                name="Product Performance Analysis",
                description="Analysis of product sales performance, ranking, and trends",
                required_columns=[
                    ColumnRequirement(
                        column_type="product",
                        required=True,
                        alternatives=["item", "sku", "product_name", "category"],
                        confidence_threshold=85.0,
                        description="Product identifier"
                    ),
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "price"],
                        confidence_threshold=85.0,
                        description="Sales amount per product"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="date",
                        required=False,
                        alternatives=["timestamp", "time", "order_date"],
                        confidence_threshold=75.0,
                        description="Date for temporal product analysis"
                    ),
                    ColumnRequirement(
                        column_type="quantity",
                        required=False,
                        alternatives=["qty", "units", "volume"],
                        confidence_threshold=75.0,
                        description="Quantity sold per product"
                    )
                ],
                min_data_points=20,
                estimated_complexity="low",
                output_types=["chart", "table", "insight"]
            ),
            
            AnalyticsType.TIME_SERIES_FORECASTING: AnalyticsRequirement(
                analytics_type=AnalyticsType.TIME_SERIES_FORECASTING,
                name="Time Series Forecasting",
                description="Predict future trends using historical data patterns",
                required_columns=[
                    ColumnRequirement(
                        column_type="date",
                        required=True,
                        alternatives=["timestamp", "time", "created_at"],
                        confidence_threshold=90.0,
                        description="Date field for time series analysis"
                    ),
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "quantity"],
                        confidence_threshold=85.0,
                        description="Numeric field to forecast"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="product",
                        required=False,
                        alternatives=["item", "sku", "category"],
                        confidence_threshold=75.0,
                        description="Product for product-specific forecasting"
                    )
                ],
                min_data_points=50,
                estimated_complexity="high",
                output_types=["chart", "forecast", "insight"]
            ),
            
            AnalyticsType.REGIONAL_ANALYSIS: AnalyticsRequirement(
                analytics_type=AnalyticsType.REGIONAL_ANALYSIS,
                name="Regional Performance Analysis",
                description="Analysis of sales performance by geographic or organizational regions",
                required_columns=[
                    ColumnRequirement(
                        column_type="region",
                        required=True,
                        alternatives=["location", "area", "territory", "branch"],
                        confidence_threshold=85.0,
                        description="Regional identifier"
                    ),
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "price"],
                        confidence_threshold=85.0,
                        description="Sales amount by region"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="date",
                        required=False,
                        alternatives=["timestamp", "time", "order_date"],
                        confidence_threshold=75.0,
                        description="Date for temporal regional analysis"
                    ),
                    ColumnRequirement(
                        column_type="product",
                        required=False,
                        alternatives=["item", "sku", "category"],
                        confidence_threshold=75.0,
                        description="Product for product-region analysis"
                    )
                ],
                min_data_points=15,
                estimated_complexity="medium",
                output_types=["chart", "table", "insight"]
            ),
            
            AnalyticsType.CORRELATION_ANALYSIS: AnalyticsRequirement(
                analytics_type=AnalyticsType.CORRELATION_ANALYSIS,
                name="Correlation Analysis",
                description="Identifies relationships between different variables in the dataset",
                required_columns=[
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "price"],
                        confidence_threshold=80.0,
                        description="Primary numeric field"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="quantity",
                        required=False,
                        alternatives=["qty", "units", "volume"],
                        confidence_threshold=75.0,
                        description="Secondary numeric field for correlation"
                    ),
                    ColumnRequirement(
                        column_type="date",
                        required=False,
                        alternatives=["timestamp", "time"],
                        confidence_threshold=75.0,
                        description="Date field for temporal correlation"
                    )
                ],
                min_data_points=30,
                estimated_complexity="medium",
                output_types=["chart", "table", "insight"]
            ),
            
            AnalyticsType.ANOMALY_DETECTION: AnalyticsRequirement(
                analytics_type=AnalyticsType.ANOMALY_DETECTION,
                name="Anomaly Detection",
                description="Identifies unusual patterns or outliers in the data",
                required_columns=[
                    ColumnRequirement(
                        column_type="sales",
                        required=True,
                        alternatives=["amount", "revenue", "quantity"],
                        confidence_threshold=80.0,
                        description="Numeric field for anomaly detection"
                    )
                ],
                optional_columns=[
                    ColumnRequirement(
                        column_type="date",
                        required=False,
                        alternatives=["timestamp", "time"],
                        confidence_threshold=75.0,
                        description="Date field for temporal anomaly detection"
                    )
                ],
                min_data_points=50,
                estimated_complexity="high",
                output_types=["chart", "table", "insight"]
            )
        }
    
    def get_available_analytics(self, column_mapping_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine which analytics are available based on column mapping results.
        
        Args:
            column_mapping_results: Results from column mapping containing mapped_columns, uncertain_columns, etc.
            
        Returns:
            List of available analytics with their requirements and status
        """
        available_analytics = []
        
        # Extract mapped columns
        mapped_columns = column_mapping_results.get('mapped_columns', [])
        uncertain_columns = column_mapping_results.get('uncertain_columns', [])
        
        # Create a mapping of column types to actual columns
        column_type_map = {}
        uncertain_column_map = {}
        
        for col in mapped_columns:
            # Accept columns as mapped if they have high confidence (80%+) or are user-confirmed
            confidence = col.get('confidence', 0)
            is_user_confirmed = col.get('method') == 'user_confirmed'
            is_high_confidence = confidence >= 80.0
            
            if col.get('status') == 'mapped' and (is_high_confidence or is_user_confirmed):
                mapped_type = col.get('mapped_column', '').lower()
                column_type_map[mapped_type] = col.get('original_column')
        
        for col in uncertain_columns:
            uncertain_column_map[col.get('column')] = col
        
        # Check each analytics type
        for analytics_type, requirement in self.requirements.items():
            analytics_status = self._check_analytics_feasibility(
                requirement, column_type_map, uncertain_column_map
            )
            
            if analytics_status['status'] != 'unavailable':
                available_analytics.append({
                    'analytics_type': analytics_type.value,
                    'name': requirement.name,
                    'description': requirement.description,
                    'status': analytics_status['status'],
                    'missing_required': analytics_status['missing_required'],
                    'missing_optional': analytics_status['missing_optional'],
                    'uncertain_columns': analytics_status['uncertain_columns'],
                    'estimated_complexity': requirement.estimated_complexity,
                    'output_types': requirement.output_types,
                    'min_data_points': requirement.min_data_points
                })
        
        return available_analytics
    
    def _check_analytics_feasibility(self, requirement: AnalyticsRequirement, 
                                   column_type_map: Dict[str, str],
                                   uncertain_column_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an analytics type is feasible given the available columns.
        
        Returns:
            Dict with status: 'ready', 'pending_confirmation', 'unavailable'
        """
        missing_required = []
        missing_optional = []
        uncertain_columns = []
        
        # Check required columns
        for req_col in requirement.required_columns:
            found = False
            found_column = None
            
            # First, check if we have a high-confidence mapping
            for alt_type in [req_col.column_type] + req_col.alternatives:
                if alt_type in column_type_map:
                    found = True
                    found_column = column_type_map[alt_type]
                    break
            
            if not found:
                # Look for uncertain columns that could satisfy this requirement
                for col_name, col_info in uncertain_column_map.items():
                    col_mapped_type = col_info.get('mapped_column', '').lower()
                    if col_mapped_type in [req_col.column_type.lower()] + [alt.lower() for alt in req_col.alternatives]:
                        # Only add if confidence is reasonable (50%+) and not already high confidence
                        confidence = col_info.get('confidence', 0)
                        if 50 <= confidence < 80:  # Only show if uncertain but not too low
                            uncertain_columns.append({
                                'column': col_name,
                                'required_type': req_col.column_type,
                                'confidence': confidence,
                                'suggestions': col_info.get('suggestions', [])
                            })
                        found = True
                        break
                
                if not found:
                    missing_required.append(req_col.column_type)
        
        # Check optional columns
        for opt_col in requirement.optional_columns:
            found = False
            for alt_type in [opt_col.column_type] + opt_col.alternatives:
                if alt_type in column_type_map:
                    found = True
                    break
            
            if not found:
                missing_optional.append(opt_col.column_type)
        
        # Determine status
        if missing_required:
            status = 'unavailable'
        elif uncertain_columns:
            status = 'pending_confirmation'
        else:
            status = 'ready'
        
        return {
            'status': status,
            'missing_required': missing_required,
            'missing_optional': missing_optional,
            'uncertain_columns': uncertain_columns
        }
    
    def get_column_requirements_for_analytics(self, analytics_type: str) -> Optional[AnalyticsRequirement]:
        """Get column requirements for a specific analytics type."""
        try:
            analytics_enum = AnalyticsType(analytics_type)
            return self.requirements.get(analytics_enum)
        except ValueError:
            return None
    
    def suggest_column_mapping(self, uncertain_column: str, 
                             available_analytics: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest column mappings based on uncertain column name and available analytics.
        
        Args:
            uncertain_column: Name of the uncertain column
            available_analytics: List of available analytics
            
        Returns:
            List of suggested column types
        """
        suggestions = set()
        
        # Extract all required column types from available analytics
        for analytics in available_analytics:
            analytics_type = analytics['analytics_type']
            requirement = self.requirements.get(AnalyticsType(analytics_type))
            
            if requirement:
                # Add all required and optional column types
                for col_req in requirement.required_columns + requirement.optional_columns:
                    suggestions.add(col_req.column_type)
                    suggestions.update(col_req.alternatives)
        
        # Convert to list and sort by relevance
        suggestions_list = list(suggestions)
        suggestions_list.sort()
        
        return suggestions_list
    
    def evaluate_analytics_with_confirmed_mappings(self, 
                                                   per_analytic_mappings: Dict[str, Dict[str, str]],
                                                   all_columns: List[str]) -> Dict[str, Any]:
        """
        Re-evaluate analytics availability after user confirms per-analytic mappings.
        
        Args:
            per_analytic_mappings: Dict mapping analytics_type -> {column_name -> column_type or "Ignore"}
            all_columns: List of all column names in the dataset
            
        Returns:
            Dict with available and unavailable analytics
        """
        result = {
            'available_analytics': [],
            'unavailable_analytics': [],
            'ignored_mappings': {}
        }
        
        for analytics_type, requirement in self.requirements.items():
            analytics_type_str = analytics_type.value
            user_mappings = per_analytic_mappings.get(analytics_type_str, {})
            
            # Check if this analytic is feasible with user's confirmed mappings
            feasibility = self._check_feasibility_with_user_mappings(
                requirement, user_mappings, all_columns
            )
            
            analytics_info = {
                'analytics_type': analytics_type_str,
                'name': requirement.name,
                'description': requirement.description,
                'status': feasibility['status'],
                'reason': feasibility.get('reason', ''),
                'ignored_columns': feasibility.get('ignored_columns', []),
                'confirmed_mappings': feasibility.get('confirmed_mappings', {}),
                'estimated_complexity': requirement.estimated_complexity,
                'output_types': requirement.output_types
            }
            
            if feasibility['status'] == 'available':
                result['available_analytics'].append(analytics_info)
            else:
                result['unavailable_analytics'].append(analytics_info)
            
            # Track ignored columns
            if feasibility.get('ignored_columns'):
                result['ignored_mappings'][analytics_type_str] = feasibility['ignored_columns']
        
        return result
    
    def _check_feasibility_with_user_mappings(self, requirement: AnalyticsRequirement,
                                             user_mappings: Dict[str, str],
                                             all_columns: List[str]) -> Dict[str, Any]:
        """
        Check if analytics is feasible with user-confirmed mappings (including ignores).
        
        Returns:
            Dict with status, reason, and mapping details
        """
        ignored_columns = []
        confirmed_mappings = {}
        missing_required = []
        
        # Check required columns
        for req_col in requirement.required_columns:
            found = False
            ignored_required = False
            
            # Check if any column is mapped to this requirement
            for col_name, mapped_type in user_mappings.items():
                # Check for ignore
                if mapped_type.lower() == 'ignore':
                    ignored_columns.append(col_name)
                    # Check if this ignored column was needed for a required field
                    if req_col.column_type.lower() in col_name.lower() or \
                       any(alt.lower() in col_name.lower() for alt in req_col.alternatives):
                        ignored_required = True
                    continue
                
                # Check if mapped type matches requirement
                mapped_type_lower = mapped_type.lower()
                if mapped_type_lower == req_col.column_type.lower() or \
                   mapped_type_lower in [alt.lower() for alt in req_col.alternatives]:
                    found = True
                    confirmed_mappings[col_name] = mapped_type
                    break
            
            if ignored_required:
                return {
                    'status': 'unavailable',
                    'reason': f'Required column "{req_col.column_type}" was ignored',
                    'ignored_columns': ignored_columns,
                    'confirmed_mappings': confirmed_mappings
                }
            
            if not found:
                missing_required.append(req_col.column_type)
        
        # If any required columns are missing (not mapped and not explicitly ignored)
        if missing_required:
            return {
                'status': 'unavailable',
                'reason': f'Missing required columns: {", ".join(missing_required)}',
                'ignored_columns': ignored_columns,
                'confirmed_mappings': confirmed_mappings
            }
        
        # Check optional columns (just for tracking)
        for opt_col in requirement.optional_columns:
            for col_name, mapped_type in user_mappings.items():
                if mapped_type.lower() == 'ignore':
                    if col_name not in ignored_columns:
                        ignored_columns.append(col_name)
                    continue
                
                mapped_type_lower = mapped_type.lower()
                if mapped_type_lower == opt_col.column_type.lower() or \
                   mapped_type_lower in [alt.lower() for alt in opt_col.alternatives]:
                    confirmed_mappings[col_name] = mapped_type
        
        return {
            'status': 'available',
            'reason': 'All required columns are mapped',
            'ignored_columns': ignored_columns,
            'confirmed_mappings': confirmed_mappings
        }