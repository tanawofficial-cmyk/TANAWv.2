# analytics_readiness_checker.py
"""
Analytics Readiness Checker for TANAW
Validates which analytics can be performed based on available columns.
"""
from typing import Dict, List, Any, Optional
import pandas as pd
from analytics_config import (
    ANALYTICS_REQUIREMENTS, 
    AnalyticsType, 
    ColumnType,
    check_analytics_readiness
)


class AnalyticsReadinessChecker:
    """
    Checks which analytics can be performed based on column mappings.
    Implements Step 6 of the TANAW workflow: Analytics Readiness Check.
    """
    
    def __init__(self):
        self.analytics_requirements = ANALYTICS_REQUIREMENTS
    
    def check_readiness(self, column_mapping: Dict[str, str], 
                       dataframe: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Check which analytics can be performed based on available columns.
        
        Args:
            column_mapping: Dictionary mapping original columns to standard types
                           Format: {'original_col': 'Date', 'sales_col': 'Sales', ...}
            dataframe: Optional DataFrame to validate data quality for each column
            
        Returns:
            Dictionary with readiness status for each analytic
        """
        # Get mapped column types (values in the mapping dict)
        available_columns = set(column_mapping.values())
        
        # Remove 'Ignore' from available columns
        available_columns.discard('Ignore')
        available_columns.discard(ColumnType.IGNORE.value)
        
        readiness_results = {
            'analytics_readiness': {},
            'available_columns': list(available_columns),
            'total_analytics': len(self.analytics_requirements),
            'ready_analytics': 0,
            'disabled_analytics': 0,
            'summary': {}
        }
        
        for analytic_type, config in self.analytics_requirements.items():
            analytic_name = analytic_type.value
            required = config["required_columns"]
            
            # Check if all required columns are available
            can_perform, missing_columns = self._check_requirements(required, available_columns)
            
            # Additional data quality checks if DataFrame is provided
            quality_issues = []
            if dataframe is not None and can_perform:
                quality_issues = self._check_data_quality(dataframe, column_mapping, required)
                if quality_issues:
                    can_perform = False
            
            # Build the readiness entry
            readiness_results['analytics_readiness'][analytic_name] = {
                'can_perform': can_perform,
                'status': '✅ Ready' if can_perform else '⚠️ Disabled',
                'type': config['type'],
                'description': config['description'],
                'explanation': config['explanation'],
                'required_columns': self._format_requirements(required),
                'missing_columns': missing_columns,
                'quality_issues': quality_issues,
                'reason': self._get_reason(can_perform, missing_columns, quality_issues)
            }
            
            if can_perform:
                readiness_results['ready_analytics'] += 1
            else:
                readiness_results['disabled_analytics'] += 1
        
        # Generate summary
        readiness_results['summary'] = self._generate_summary(readiness_results)
        
        return readiness_results
    
    def _check_requirements(self, required: List, available: set) -> tuple:
        """
        Check if requirements are met.
        
        Args:
            required: List of required columns (may contain OR conditions as nested lists)
            available: Set of available column types
            
        Returns:
            Tuple of (can_perform: bool, missing_columns: list)
        """
        can_perform = True
        missing_columns = []
        
        for requirement in required:
            if isinstance(requirement, list):
                # OR condition - at least one must be present
                satisfied = any(col.value in available for col in requirement)
                if not satisfied:
                    can_perform = False
                    missing_columns.append(f"One of: {', '.join([c.value for c in requirement])}")
            else:
                # Single requirement
                if requirement.value not in available:
                    can_perform = False
                    missing_columns.append(requirement.value)
        
        return can_perform, missing_columns
    
    def _format_requirements(self, required: List) -> List[str]:
        """Format requirements for display."""
        formatted = []
        for req in required:
            if isinstance(req, list):
                formatted.append(f"({' OR '.join([c.value for c in req])})")
            else:
                formatted.append(req.value)
        return formatted
    
    def _check_data_quality(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                           required: List) -> List[str]:
        """
        Check data quality for required columns.
        
        Args:
            df: The DataFrame to check
            column_mapping: Column mapping dictionary
            required: List of required columns
            
        Returns:
            List of quality issues found
        """
        issues = []
        
        # Reverse mapping to get original column names
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        
        for requirement in required:
            if isinstance(requirement, list):
                # Check any of the OR options
                column_types = [col.value for col in requirement]
            else:
                column_types = [requirement.value]
            
            for col_type in column_types:
                if col_type in reverse_mapping:
                    original_col = reverse_mapping[col_type]
                    
                    if original_col in df.columns:
                        # Check for excessive missing values
                        missing_pct = df[original_col].isnull().mean()
                        if missing_pct > 0.5:
                            issues.append(f"{col_type}: Over 50% missing values")
                        
                        # Check for data type appropriateness
                        if col_type == 'Date':
                            if not pd.api.types.is_datetime64_any_dtype(df[original_col]):
                                # Try to convert and see if it works
                                try:
                                    test = pd.to_datetime(df[original_col].dropna().head(10), errors='coerce')
                                    if test.isna().all():
                                        issues.append(f"{col_type}: Cannot parse as datetime")
                                except:
                                    issues.append(f"{col_type}: Invalid datetime format")
                        
                        elif col_type in ['Sales', 'Amount', 'Quantity']:
                            if not pd.api.types.is_numeric_dtype(df[original_col]):
                                # Try to convert
                                try:
                                    test = pd.to_numeric(df[original_col].dropna().head(10), errors='coerce')
                                    if test.isna().all():
                                        issues.append(f"{col_type}: Cannot convert to numeric")
                                except:
                                    issues.append(f"{col_type}: Non-numeric data")
                        
                        # Check for minimum data points
                        valid_count = df[original_col].notna().sum()
                        if valid_count < 10:
                            issues.append(f"{col_type}: Insufficient data (less than 10 valid values)")
                    
                    break  # Only check the first available column in OR condition
        
        return issues
    
    def _get_reason(self, can_perform: bool, missing_columns: List[str], 
                   quality_issues: List[str]) -> str:
        """Get human-readable reason for the readiness status."""
        if can_perform:
            return "All required columns are available and data quality is sufficient"
        
        reasons = []
        if missing_columns:
            reasons.append(f"Missing columns: {', '.join(missing_columns)}")
        if quality_issues:
            reasons.append(f"Quality issues: {', '.join(quality_issues)}")
        
        return "; ".join(reasons) if reasons else "Cannot be performed"
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the readiness check."""
        ready = results['ready_analytics']
        total = results['total_analytics']
        
        ready_list = []
        disabled_list = []
        
        for analytic_name, status in results['analytics_readiness'].items():
            if status['can_perform']:
                ready_list.append(analytic_name)
            else:
                disabled_list.append({
                    'name': analytic_name,
                    'missing': status['missing_columns'],
                    'issues': status['quality_issues']
                })
        
        return {
            'ready_count': ready,
            'disabled_count': total - ready,
            'readiness_percentage': round((ready / total) * 100, 1) if total > 0 else 0,
            'ready_analytics': ready_list,
            'disabled_analytics': disabled_list,
            'message': self._get_summary_message(ready, total)
        }
    
    def _get_summary_message(self, ready: int, total: int) -> str:
        """Get a summary message based on readiness."""
        if ready == total:
            return f"✅ All {total} analytics are ready to run!"
        elif ready == 0:
            return f"⚠️ None of the {total} analytics can be performed. Please map required columns."
        else:
            return f"⚠️ {ready} out of {total} analytics are ready. {total - ready} are disabled due to missing columns."
    
    def get_required_columns_for_analytic(self, analytic_type: str) -> List[str]:
        """
        Get the required columns for a specific analytic.
        
        Args:
            analytic_type: Name of the analytic
            
        Returns:
            List of required column names
        """
        for at, config in self.analytics_requirements.items():
            if at.value == analytic_type:
                return self._format_requirements(config['required_columns'])
        return []
    
    def suggest_columns_to_map(self, current_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Suggest which additional columns should be mapped to enable more analytics.
        
        Args:
            current_mapping: Current column mapping
            
        Returns:
            Dictionary with suggestions
        """
        available = set(current_mapping.values())
        available.discard('Ignore')
        
        suggestions = {
            'high_priority': [],  # Enables multiple analytics
            'medium_priority': [],  # Enables one analytic
            'low_priority': [],  # Already have alternatives
            'all_required_columns': ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region']
        }
        
        # Count how many analytics each missing column would enable
        column_impact = {}
        
        for col_type in ['Date', 'Sales', 'Amount', 'Product', 'Quantity', 'Region']:
            if col_type not in available:
                # Count how many disabled analytics this would help enable
                impact_count = 0
                would_enable = []
                
                test_mapping = current_mapping.copy()
                test_mapping['_test'] = col_type
                
                for analytic_type, config in self.analytics_requirements.items():
                    can_perform, _ = self._check_requirements(
                        config['required_columns'], 
                        set(test_mapping.values())
                    )
                    
                    # Check if it wasn't performable before
                    can_perform_before, _ = self._check_requirements(
                        config['required_columns'],
                        available
                    )
                    
                    if can_perform and not can_perform_before:
                        impact_count += 1
                        would_enable.append(analytic_type.value)
                
                column_impact[col_type] = {
                    'count': impact_count,
                    'enables': would_enable
                }
        
        # Categorize by priority
        for col_type, impact in column_impact.items():
            if impact['count'] >= 3:
                suggestions['high_priority'].append({
                    'column': col_type,
                    'impact': impact['count'],
                    'enables': impact['enables']
                })
            elif impact['count'] >= 1:
                suggestions['medium_priority'].append({
                    'column': col_type,
                    'impact': impact['count'],
                    'enables': impact['enables']
                })
            else:
                suggestions['low_priority'].append(col_type)
        
        return suggestions


# Convenience function for quick checks
def quick_check(column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Quick readiness check without DataFrame validation.
    
    Args:
        column_mapping: Dictionary mapping original columns to standard types
        
    Returns:
        Readiness results
    """
    checker = AnalyticsReadinessChecker()
    return checker.check_readiness(column_mapping)


if __name__ == "__main__":
    # Test the checker
    print("=" * 70)
    print("ANALYTICS READINESS CHECKER TEST")
    print("=" * 70)
    
    # Test case 1: All columns available
    print("\n📊 Test 1: All columns mapped")
    test_mapping = {
        'date_col': 'Date',
        'sales_col': 'Sales',
        'product_col': 'Product',
        'qty_col': 'Quantity',
        'region_col': 'Region'
    }
    
    checker = AnalyticsReadinessChecker()
    results = checker.check_readiness(test_mapping)
    
    print(f"\n{results['summary']['message']}")
    print(f"Ready: {results['ready_analytics']}/{results['total_analytics']}")
    print("\nReady Analytics:")
    for name in results['summary']['ready_analytics']:
        print(f"  ✅ {name}")
    
    # Test case 2: Missing some columns
    print("\n\n📊 Test 2: Partial column mapping")
    partial_mapping = {
        'date_col': 'Date',
        'sales_col': 'Sales'
    }
    
    results2 = checker.check_readiness(partial_mapping)
    print(f"\n{results2['summary']['message']}")
    print(f"Ready: {results2['ready_analytics']}/{results2['total_analytics']}")
    
    print("\nReady Analytics:")
    for name in results2['summary']['ready_analytics']:
        print(f"  ✅ {name}")
    
    print("\nDisabled Analytics:")
    for disabled in results2['summary']['disabled_analytics']:
        print(f"  ❌ {disabled['name']}")
        print(f"     Missing: {', '.join(disabled['missing'])}")
    
    # Test case 3: Column suggestions
    print("\n\n📊 Test 3: Column Suggestions")
    suggestions = checker.suggest_columns_to_map(partial_mapping)
    
    if suggestions['high_priority']:
        print("\n🔴 HIGH PRIORITY (enables multiple analytics):")
        for sug in suggestions['high_priority']:
            print(f"  • {sug['column']} - enables {sug['impact']} analytics")
            print(f"    Would enable: {', '.join(sug['enables'])}")
    
    if suggestions['medium_priority']:
        print("\n🟡 MEDIUM PRIORITY:")
        for sug in suggestions['medium_priority']:
            print(f"  • {sug['column']} - enables {sug['impact']} analytics")
            print(f"    Would enable: {', '.join(sug['enables'])}")

