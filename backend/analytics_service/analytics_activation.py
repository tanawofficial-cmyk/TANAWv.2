"""
Analytics Activation - Phase 8: Analytics Activation
Converts confirmed column mappings into actionable business insights

This module handles:
- Validating data quality for analytics
- Executing the 5 core TANAW analytics
- Generating business insights and recommendations
- Creating visualizations and reports
- Providing ROI metrics for the mapping effort
- Delivering real business value from technical mappings
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

try:
    from .user_confirmation import UserConfirmationSession
    from .tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from .file_preprocessor import FileMetadata
except ImportError:
    from user_confirmation import UserConfirmationSession
    from tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from file_preprocessor import FileMetadata

class AnalyticsStatus(Enum):
    """Status of analytics execution."""
    READY = "ready"                    # All requirements met, ready to run
    PARTIAL = "partial"                # Some requirements met, limited analytics
    INSUFFICIENT = "insufficient"      # Missing critical requirements
    DATA_QUALITY_ISSUES = "data_quality_issues"  # Data quality problems
    ERROR = "error"                    # Execution error

@dataclass
class DataQualityCheck:
    """Data quality assessment for analytics."""
    column_name: str
    canonical_type: str
    
    # Quality metrics
    total_rows: int
    non_null_rows: int
    null_percentage: float
    unique_values: int
    uniqueness_ratio: float
    
    # Data type validation
    expected_type: str
    actual_type: str
    type_match: bool
    
    # Value validation
    has_valid_values: bool
    sample_values: List[Any]
    validation_issues: List[str]
    
    # Quality score
    quality_score: float  # 0-1 scale
    is_suitable: bool     # Suitable for analytics

@dataclass
class AnalyticsResult:
    """Results from a specific analytics execution."""
    analytic_type: AnalyticType
    status: AnalyticsStatus
    
    # Data used
    columns_used: List[str]
    rows_processed: int
    data_period: Optional[Tuple[datetime, datetime]]
    
    # Results
    key_insights: List[str]
    metrics: Dict[str, Any]
    visualizations: List[Dict[str, Any]]  # Chart specifications
    recommendations: List[str]
    
    # Metadata
    execution_time: float
    generated_at: datetime
    confidence_level: str  # "high", "medium", "low"

@dataclass
class BusinessInsight:
    """High-level business insight derived from analytics."""
    insight_type: str
    title: str
    description: str
    impact_level: str  # "high", "medium", "low"
    evidence: List[str]
    recommendations: List[str]
    priority: int

@dataclass
class AnalyticsActivationResult:
    """Complete results from analytics activation."""
    # Input information
    final_mappings: Dict[str, str]
    data_quality_report: List[DataQualityCheck]
    
    # Analytics execution
    executed_analytics: List[AnalyticsResult]
    failed_analytics: List[Tuple[AnalyticType, str]]  # (type, reason)
    
    # Business insights
    business_insights: List[BusinessInsight]
    executive_summary: str
    
    # ROI and value metrics
    value_metrics: Dict[str, Any]
    mapping_roi: Dict[str, Any]
    
    # Processing metadata
    activation_timestamp: datetime
    total_processing_time: float
    analytics_engine_version: str

class AnalyticsEngine:
    """
    Core analytics execution engine for the 5 TANAW analytics.
    
    Transforms mapped data into actionable business insights.
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.canonical_schema = tanaw_schema
        self.engine_version = "1.0.0"
    
    def activate_analytics(
        self, 
        confirmation_session: UserConfirmationSession,
        original_dataframe: pd.DataFrame
    ) -> AnalyticsActivationResult:
        """
        Activate analytics based on confirmed column mappings.
        
        Args:
            confirmation_session: Completed user confirmation session
            original_dataframe: Original dataset with actual data
            
        Returns:
            Complete analytics activation results with business insights
        """
        start_time = datetime.now()
        
        print(f"🚀 ACTIVATING ANALYTICS")
        print("=" * 50)
        print(f"Final mappings: {len(confirmation_session.final_mappings)}")
        
        # Step 1: Prepare mapped dataset
        mapped_df = self._prepare_mapped_dataset(
            original_dataframe, confirmation_session.final_mappings
        )
        
        # Step 2: Perform data quality checks
        print("1️⃣ Performing data quality checks...")
        quality_report = self._perform_data_quality_checks(mapped_df, confirmation_session.final_mappings)
        
        quality_issues = len([check for check in quality_report if not check.is_suitable])
        print(f"   ✅ Quality report: {len(quality_report)} columns checked, {quality_issues} issues found")
        
        # Step 3: Determine feasible analytics
        feasible_analytics = self._determine_feasible_analytics(mapped_df, quality_report)
        
        print(f"2️⃣ Feasible analytics: {len(feasible_analytics)}/5 analytics ready")
        for analytic in feasible_analytics:
            print(f"   ✅ {analytic.value.replace('_', ' ').title()}")
        
        # Step 4: Execute analytics
        print("3️⃣ Executing analytics...")
        executed_analytics = []
        failed_analytics = []
        
        for analytic_type in feasible_analytics:
            try:
                result = self._execute_analytic(analytic_type, mapped_df, quality_report)
                executed_analytics.append(result)
                print(f"   ✅ {analytic_type.value.replace('_', ' ').title()} completed ({result.execution_time:.2f}s)")
            except Exception as e:
                failed_analytics.append((analytic_type, str(e)))
                print(f"   ❌ {analytic_type.value.replace('_', ' ').title()} failed: {e}")
        
        # Step 5: Generate business insights
        print("4️⃣ Generating business insights...")
        business_insights = self._generate_business_insights(executed_analytics, mapped_df)
        
        print(f"   ✅ Generated {len(business_insights)} business insights")
        
        # Step 6: Create executive summary
        executive_summary = self._create_executive_summary(executed_analytics, business_insights)
        
        # Step 7: Calculate value metrics
        value_metrics = self._calculate_value_metrics(executed_analytics, confirmation_session)
        mapping_roi = self._calculate_mapping_roi(confirmation_session, executed_analytics)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AnalyticsActivationResult(
            final_mappings=confirmation_session.final_mappings,
            data_quality_report=quality_report,
            executed_analytics=executed_analytics,
            failed_analytics=failed_analytics,
            business_insights=business_insights,
            executive_summary=executive_summary,
            value_metrics=value_metrics,
            mapping_roi=mapping_roi,
            activation_timestamp=start_time,
            total_processing_time=processing_time,
            analytics_engine_version=self.engine_version
        )
    
    def _prepare_mapped_dataset(self, df: pd.DataFrame, mappings: Dict[str, str]) -> pd.DataFrame:
        """Prepare dataset with canonical column names."""
        
        mapped_df = df.copy()
        
        # Handle potential duplicate canonical names by selecting only the first mapping
        used_canonical = set()
        final_mappings = {}
        
        for original_col, canonical_type in mappings.items():
            if original_col in df.columns and canonical_type not in used_canonical:
                final_mappings[original_col] = canonical_type
                used_canonical.add(canonical_type)
        
        # Select only the columns we're going to use
        selected_columns = list(final_mappings.keys())
        mapped_df = mapped_df[selected_columns].copy()
        
        # Rename columns to canonical names
        mapped_df = mapped_df.rename(columns=final_mappings)
        
        # Convert data types (safely)
        try:
            mapped_df = self._convert_data_types(mapped_df)
        except Exception as e:
            print(f"   ⚠️ Data type conversion warning: {e}")
        
        return mapped_df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types based on canonical schema."""
        
        for col in df.columns:
            try:
                if col == CanonicalColumnType.DATE.value:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                elif col in [CanonicalColumnType.SALES.value, CanonicalColumnType.AMOUNT.value]:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                elif col == CanonicalColumnType.QUANTITY.value:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                print(f"   ⚠️ Could not convert {col}: {e}")
        
        return df
    
    def _perform_data_quality_checks(
        self, 
        df: pd.DataFrame, 
        mappings: Dict[str, str]
    ) -> List[DataQualityCheck]:
        """Perform comprehensive data quality checks."""
        
        quality_checks = []
        
        for canonical_type in mappings.values():
            if canonical_type in df.columns:
                check = self._check_column_quality(df, canonical_type)
                quality_checks.append(check)
        
        return quality_checks
    
    def _check_column_quality(self, df: pd.DataFrame, canonical_type: str) -> DataQualityCheck:
        """Check quality of a specific column."""
        
        col_data = df[canonical_type]
        
        # Basic metrics
        total_rows = len(col_data)
        
        # Handle potential Series vs scalar issue
        notna_sum = col_data.notna().sum()
        non_null_rows = int(notna_sum.iloc[0] if hasattr(notna_sum, 'iloc') else notna_sum)
        
        null_percentage = (total_rows - non_null_rows) / total_rows * 100
        
        nunique_result = col_data.nunique()
        unique_values = int(nunique_result.iloc[0] if hasattr(nunique_result, 'iloc') else nunique_result)
        
        uniqueness_ratio = unique_values / non_null_rows if non_null_rows > 0 else 0
        
        # Type validation
        expected_type = self._get_expected_type(canonical_type)
        actual_type = str(col_data.dtype)
        type_match = self._validate_type_match(canonical_type, actual_type)
        
        # Value validation
        validation_issues = []
        has_valid_values = True
        
        if canonical_type == CanonicalColumnType.DATE.value:
            if pd.api.types.is_datetime64_any_dtype(col_data):
                invalid_dates = col_data.isna().sum() - (len(col_data) - non_null_rows)
                if invalid_dates > 0:
                    validation_issues.append(f"{invalid_dates} invalid dates")
                    has_valid_values = invalid_dates < total_rows * 0.1  # Allow 10% invalid
            else:
                validation_issues.append("Not datetime format")
                has_valid_values = False
        
        elif canonical_type in [CanonicalColumnType.SALES.value, CanonicalColumnType.AMOUNT.value]:
            if pd.api.types.is_numeric_dtype(col_data):
                negative_values = int((col_data < 0).sum())
                if negative_values > 0:
                    validation_issues.append(f"{negative_values} negative values")
                zero_values = int((col_data == 0).sum())
                if zero_values > total_rows * 0.5:
                    validation_issues.append(f"Many zero values ({zero_values})")
            else:
                validation_issues.append("Not numeric format")
                has_valid_values = False
        
        # Sample values (safe)
        sample_values = col_data.dropna().head(3).tolist() if non_null_rows > 0 else []
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            null_percentage, type_match, has_valid_values, len(validation_issues)
        )
        
        is_suitable = quality_score >= 0.7 and null_percentage < 50
        
        return DataQualityCheck(
            column_name=canonical_type,
            canonical_type=canonical_type,
            total_rows=total_rows,
            non_null_rows=non_null_rows,
            null_percentage=null_percentage,
            unique_values=unique_values,
            uniqueness_ratio=uniqueness_ratio,
            expected_type=expected_type,
            actual_type=actual_type,
            type_match=type_match,
            has_valid_values=has_valid_values,
            sample_values=sample_values,
            validation_issues=validation_issues,
            quality_score=quality_score,
            is_suitable=is_suitable
        )
    
    def _determine_feasible_analytics(
        self, 
        df: pd.DataFrame, 
        quality_report: List[DataQualityCheck]
    ) -> List[AnalyticType]:
        """Determine which analytics can be executed based on available data."""
        
        available_columns = set(df.columns)
        suitable_columns = {
            check.canonical_type for check in quality_report 
            if check.is_suitable
        }
        
        feasible_analytics = []
        
        for analytic_type, requirement in self.canonical_schema.analytic_requirements.items():
            can_execute = True
            
            for col_req in requirement.required_columns:
                required_col = col_req.canonical_type.value
                alternatives = [alt.value for alt in col_req.alternatives]
                
                has_required = required_col in suitable_columns
                has_alternative = any(alt in suitable_columns for alt in alternatives)
                
                if col_req.is_required and not (has_required or has_alternative):
                    can_execute = False
                    break
                
                # For flexible requirements (either/or)
                if not col_req.is_required and col_req.alternatives:
                    if not (has_required or has_alternative):
                        can_execute = False
                        break
            
            if can_execute:
                feasible_analytics.append(analytic_type)
        
        return feasible_analytics
    
    def _execute_analytic(
        self, 
        analytic_type: AnalyticType, 
        df: pd.DataFrame,
        quality_report: List[DataQualityCheck]
    ) -> AnalyticsResult:
        """Execute a specific analytic and return results."""
        
        start_time = datetime.now()
        
        if analytic_type == AnalyticType.SALES_SUMMARY:
            result = self._execute_sales_summary(df)
        elif analytic_type == AnalyticType.PRODUCT_PERFORMANCE:
            result = self._execute_product_performance(df)
        elif analytic_type == AnalyticType.REGIONAL_SALES:
            result = self._execute_regional_analysis(df)
        elif analytic_type == AnalyticType.SALES_FORECASTING:
            result = self._execute_sales_forecasting(df)
        elif analytic_type == AnalyticType.DEMAND_FORECASTING:
            result = self._execute_demand_forecasting(df)
        else:
            raise ValueError(f"Unknown analytic type: {analytic_type}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        result.execution_time = execution_time
        result.generated_at = start_time
        
        return result
    
    def _execute_sales_summary(self, df: pd.DataFrame) -> AnalyticsResult:
        """Execute Sales Summary Report analytics."""
        
        # Determine which columns to use
        date_col = CanonicalColumnType.DATE.value if CanonicalColumnType.DATE.value in df.columns else None
        sales_col = (CanonicalColumnType.SALES.value if CanonicalColumnType.SALES.value in df.columns 
                    else CanonicalColumnType.AMOUNT.value if CanonicalColumnType.AMOUNT.value in df.columns 
                    else None)
        
        if not date_col or not sales_col:
            raise ValueError("Missing required columns for Sales Summary")
        
        # Clean data
        analysis_df = df[[date_col, sales_col]].dropna()
        rows_processed = len(analysis_df)
        
        if rows_processed == 0:
            raise ValueError("No valid data for analysis")
        
        # Calculate metrics
        total_sales = analysis_df[sales_col].sum()
        average_sales = analysis_df[sales_col].mean()
        median_sales = analysis_df[sales_col].median()
        
        # Time-based analysis
        analysis_df = analysis_df.copy()
        analysis_df['date'] = pd.to_datetime(analysis_df[date_col])
        analysis_df = analysis_df.sort_values('date')
        
        date_range = (analysis_df['date'].min(), analysis_df['date'].max())
        
        # Monthly summary
        monthly_sales = analysis_df.groupby(analysis_df['date'].dt.to_period('M'))[sales_col].sum()
        best_month = monthly_sales.idxmax() if len(monthly_sales) > 0 else None
        worst_month = monthly_sales.idxmin() if len(monthly_sales) > 0 else None
        
        # Growth analysis (if multiple months)
        growth_rate = 0
        if len(monthly_sales) >= 2:
            first_month = monthly_sales.iloc[0]
            last_month = monthly_sales.iloc[-1]
            months_diff = len(monthly_sales) - 1
            if first_month > 0 and months_diff > 0:
                growth_rate = ((last_month - first_month) / first_month) / months_diff * 100
        
        # Generate insights
        insights = [
            f"Total sales: ${total_sales:,.2f}",
            f"Average daily sales: ${average_sales:,.2f}",
            f"Median sales: ${median_sales:,.2f}",
            f"Data period: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}"
        ]
        
        if best_month:
            insights.append(f"Best month: {best_month} (${monthly_sales[best_month]:,.2f})")
        
        if growth_rate != 0:
            trend = "growth" if growth_rate > 0 else "decline"
            insights.append(f"Monthly {trend}: {abs(growth_rate):.1f}%")
        
        # Recommendations
        recommendations = []
        if growth_rate > 0:
            recommendations.append("Positive sales trend - consider scaling successful strategies")
        elif growth_rate < -5:
            recommendations.append("Declining sales trend - investigate causes and implement corrective measures")
        
        if monthly_sales.std() / monthly_sales.mean() > 0.3:
            recommendations.append("High sales volatility - consider smoothing demand strategies")
        
        # Create visualization specs
        visualizations = [
            {
                "type": "line_chart",
                "title": "Sales Trend Over Time",
                "data": monthly_sales.to_dict(),
                "x_axis": "Month",
                "y_axis": "Sales ($)"
            },
            {
                "type": "summary_cards",
                "title": "Key Metrics",
                "cards": [
                    {"label": "Total Sales", "value": f"${total_sales:,.2f}", "trend": "neutral"},
                    {"label": "Average Sales", "value": f"${average_sales:,.2f}", "trend": "neutral"},
                    {"label": "Growth Rate", "value": f"{growth_rate:+.1f}%/month", "trend": "positive" if growth_rate > 0 else "negative"}
                ]
            }
        ]
        
        return AnalyticsResult(
            analytic_type=AnalyticType.SALES_SUMMARY,
            status=AnalyticsStatus.READY,
            columns_used=[date_col, sales_col],
            rows_processed=rows_processed,
            data_period=date_range,
            key_insights=insights,
            metrics={
                "total_sales": total_sales,
                "average_sales": average_sales,
                "median_sales": median_sales,
                "growth_rate": growth_rate,
                "best_month": str(best_month) if best_month else None,
                "monthly_sales": monthly_sales.to_dict()
            },
            visualizations=visualizations,
            recommendations=recommendations,
            execution_time=0.0,
            generated_at=datetime.now(),
            confidence_level="high" if rows_processed > 30 else "medium"
        )
    
    def _execute_product_performance(self, df: pd.DataFrame) -> AnalyticsResult:
        """Execute Product Performance Analysis."""
        
        product_col = CanonicalColumnType.PRODUCT.value
        sales_col = (CanonicalColumnType.SALES.value if CanonicalColumnType.SALES.value in df.columns 
                    else CanonicalColumnType.QUANTITY.value if CanonicalColumnType.QUANTITY.value in df.columns 
                    else None)
        
        if product_col not in df.columns or not sales_col:
            raise ValueError("Missing required columns for Product Performance")
        
        analysis_df = df[[product_col, sales_col]].dropna()
        
        # Product performance metrics
        product_performance = analysis_df.groupby(product_col)[sales_col].agg(['sum', 'mean', 'count']).round(2)
        product_performance.columns = ['total', 'average', 'transactions']
        product_performance = product_performance.sort_values('total', ascending=False)
        
        # Top and bottom performers
        top_products = product_performance.head(5)
        bottom_products = product_performance.tail(3)
        
        insights = [
            f"Analyzed {len(product_performance)} products",
            f"Top product: {top_products.index[0]} (${top_products.iloc[0]['total']:,.2f})",
            f"Total product revenue: ${product_performance['total'].sum():,.2f}",
            f"Average revenue per product: ${product_performance['total'].mean():,.2f}"
        ]
        
        visualizations = [
            {
                "type": "bar_chart",
                "title": "Top 10 Products by Sales",
                "data": top_products.head(10)['total'].to_dict(),
                "x_axis": "Product",
                "y_axis": "Sales ($)"
            }
        ]
        
        recommendations = [
            f"Focus on top performers: {', '.join(top_products.head(3).index.tolist())}",
            f"Review underperforming products: {', '.join(bottom_products.index.tolist())}"
        ]
        
        return AnalyticsResult(
            analytic_type=AnalyticType.PRODUCT_PERFORMANCE,
            status=AnalyticsStatus.READY,
            columns_used=[product_col, sales_col],
            rows_processed=len(analysis_df),
            data_period=None,
            key_insights=insights,
            metrics={
                "top_products": top_products.to_dict(),
                "bottom_products": bottom_products.to_dict(),
                "total_products": len(product_performance)
            },
            visualizations=visualizations,
            recommendations=recommendations,
            execution_time=0.0,
            generated_at=datetime.now(),
            confidence_level="high"
        )
    
    def _execute_regional_analysis(self, df: pd.DataFrame) -> AnalyticsResult:
        """Execute Regional Sales Analysis."""
        
        region_col = CanonicalColumnType.REGION.value
        sales_col = (CanonicalColumnType.SALES.value if CanonicalColumnType.SALES.value in df.columns 
                    else CanonicalColumnType.AMOUNT.value if CanonicalColumnType.AMOUNT.value in df.columns 
                    else None)
        
        if region_col not in df.columns or not sales_col:
            raise ValueError("Missing required columns for Regional Analysis")
        
        analysis_df = df[[region_col, sales_col]].dropna()
        
        # Regional performance
        regional_performance = analysis_df.groupby(region_col)[sales_col].agg(['sum', 'mean', 'count']).round(2)
        regional_performance.columns = ['total_sales', 'average_sales', 'transactions']
        regional_performance = regional_performance.sort_values('total_sales', ascending=False)
        
        # Calculate market share
        total_sales = regional_performance['total_sales'].sum()
        regional_performance['market_share'] = (regional_performance['total_sales'] / total_sales * 100).round(1)
        
        top_region = regional_performance.index[0]
        bottom_region = regional_performance.index[-1]
        
        insights = [
            f"Analyzed {len(regional_performance)} regions",
            f"Top region: {top_region} ({regional_performance.loc[top_region, 'market_share']:.1f}% market share)",
            f"Total regional sales: ${total_sales:,.2f}",
            f"Average sales per region: ${regional_performance['total_sales'].mean():,.2f}"
        ]
        
        # Simple recommendations
        recommendations = []
        if regional_performance['market_share'].max() > 50:
            recommendations.append(f"Heavy dependence on {top_region} region - consider diversification")
        
        if regional_performance['market_share'].min() < 10:
            recommendations.append(f"Opportunity to grow in {bottom_region} region")
        
        return AnalyticsResult(
            analytic_type=AnalyticType.REGIONAL_SALES,
            status=AnalyticsStatus.READY,
            columns_used=[region_col, sales_col],
            rows_processed=len(analysis_df),
            data_period=None,
            key_insights=insights,
            metrics=regional_performance.to_dict(),
            visualizations=[],
            recommendations=recommendations,
            execution_time=0.0,
            generated_at=datetime.now(),
            confidence_level="high"
        )
    
    def _execute_sales_forecasting(self, df: pd.DataFrame) -> AnalyticsResult:
        """Execute Sales Forecasting (simplified implementation)."""
        
        # Simplified forecasting - just trend analysis
        date_col = CanonicalColumnType.DATE.value
        sales_col = (CanonicalColumnType.SALES.value if CanonicalColumnType.SALES.value in df.columns 
                    else CanonicalColumnType.AMOUNT.value if CanonicalColumnType.AMOUNT.value in df.columns 
                    else None)
        
        if date_col not in df.columns or not sales_col:
            raise ValueError("Missing required columns for Sales Forecasting")
        
        analysis_df = df[[date_col, sales_col]].dropna()
        analysis_df['date'] = pd.to_datetime(analysis_df[date_col])
        
        # Simple trend calculation
        monthly_sales = analysis_df.groupby(analysis_df['date'].dt.to_period('M'))[sales_col].sum()
        
        if len(monthly_sales) < 2:
            raise ValueError("Insufficient data for forecasting")
        
        # Linear trend
        trend = np.polyfit(range(len(monthly_sales)), monthly_sales.values, 1)[0]
        
        # Simple forecast (next 3 months)
        last_value = monthly_sales.iloc[-1]
        forecasts = [last_value + trend * (i + 1) for i in range(3)]
        
        insights = [
            f"Historical data: {len(monthly_sales)} months",
            f"Monthly trend: ${trend:+,.2f}",
            f"Next month forecast: ${forecasts[0]:,.2f}",
            f"3-month outlook: {'positive' if trend > 0 else 'negative'}"
        ]
        
        recommendations = [
            "Forecast based on linear trend - consider seasonal factors",
            "Monitor actual vs predicted for model accuracy"
        ]
        
        return AnalyticsResult(
            analytic_type=AnalyticType.SALES_FORECASTING,
            status=AnalyticsStatus.READY,
            columns_used=[date_col, sales_col],
            rows_processed=len(analysis_df),
            data_period=(analysis_df['date'].min(), analysis_df['date'].max()),
            key_insights=insights,
            metrics={
                "trend": trend,
                "forecasts": forecasts,
                "historical_months": len(monthly_sales)
            },
            visualizations=[],
            recommendations=recommendations,
            execution_time=0.0,
            generated_at=datetime.now(),
            confidence_level="medium"
        )
    
    def _execute_demand_forecasting(self, df: pd.DataFrame) -> AnalyticsResult:
        """Execute Demand Forecasting (simplified implementation)."""
        
        # Required columns
        required_cols = [
            CanonicalColumnType.DATE.value,
            CanonicalColumnType.PRODUCT.value,
            CanonicalColumnType.QUANTITY.value
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        analysis_df = df[required_cols].dropna()
        
        # Product demand analysis
        product_demand = analysis_df.groupby(CanonicalColumnType.PRODUCT.value)[CanonicalColumnType.QUANTITY.value].sum().sort_values(ascending=False)
        
        insights = [
            f"Demand analysis for {len(product_demand)} products",
            f"Highest demand: {product_demand.index[0]} ({product_demand.iloc[0]} units)",
            f"Total demand: {product_demand.sum():,.0f} units",
            f"Average product demand: {product_demand.mean():,.0f} units"
        ]
        
        recommendations = [
            f"Stock up on high-demand products: {', '.join(product_demand.head(3).index.tolist())}",
            "Consider inventory optimization for slow-moving items"
        ]
        
        return AnalyticsResult(
            analytic_type=AnalyticType.DEMAND_FORECASTING,
            status=AnalyticsStatus.READY,
            columns_used=required_cols,
            rows_processed=len(analysis_df),
            data_period=None,
            key_insights=insights,
            metrics={"product_demand": product_demand.to_dict()},
            visualizations=[],
            recommendations=recommendations,
            execution_time=0.0,
            generated_at=datetime.now(),
            confidence_level="medium"
        )
    
    def _generate_business_insights(
        self, 
        analytics_results: List[AnalyticsResult], 
        df: pd.DataFrame
    ) -> List[BusinessInsight]:
        """Generate high-level business insights from analytics results."""
        
        insights = []
        
        # Cross-analytics insights
        if len(analytics_results) >= 2:
            insights.append(BusinessInsight(
                insight_type="integration",
                title="Multi-Dimensional Analysis Available",
                description=f"Successfully integrated {len(analytics_results)} analytics for comprehensive business view",
                impact_level="high",
                evidence=[result.analytic_type.value for result in analytics_results],
                recommendations=["Use integrated insights for strategic planning", "Monitor all metrics regularly"],
                priority=1
            ))
        
        # Sales performance insights
        sales_results = [r for r in analytics_results if r.analytic_type == AnalyticType.SALES_SUMMARY]
        if sales_results:
            sales_result = sales_results[0]
            growth_rate = sales_result.metrics.get('growth_rate', 0)
            
            if growth_rate > 5:
                insights.append(BusinessInsight(
                    insight_type="growth",
                    title="Strong Sales Growth Detected",
                    description=f"Sales are growing at {growth_rate:.1f}% per month",
                    impact_level="high",
                    evidence=[f"Monthly growth rate: {growth_rate:.1f}%"],
                    recommendations=["Scale successful strategies", "Invest in capacity expansion"],
                    priority=2
                ))
            elif growth_rate < -3:
                insights.append(BusinessInsight(
                    insight_type="decline",
                    title="Sales Decline Requires Attention",
                    description=f"Sales are declining at {abs(growth_rate):.1f}% per month",
                    impact_level="high",
                    evidence=[f"Monthly decline rate: {growth_rate:.1f}%"],
                    recommendations=["Investigate root causes", "Implement recovery strategies"],
                    priority=1
                ))
        
        return insights
    
    def _create_executive_summary(
        self, 
        analytics_results: List[AnalyticsResult],
        business_insights: List[BusinessInsight]
    ) -> str:
        """Create executive summary of analytics results."""
        
        summary_parts = []
        
        summary_parts.append(f"TANAW Analytics Report - {datetime.now().strftime('%B %Y')}")
        summary_parts.append("=" * 50)
        
        if analytics_results:
            summary_parts.append(f"✅ Successfully executed {len(analytics_results)} analytics modules")
            
            for result in analytics_results:
                analytic_name = result.analytic_type.value.replace('_', ' ').title()
                summary_parts.append(f"• {analytic_name}: {len(result.key_insights)} insights generated")
        
        if business_insights:
            summary_parts.append(f"\n🎯 Key Business Insights ({len(business_insights)}):")
            for insight in business_insights[:3]:  # Top 3 insights
                summary_parts.append(f"• {insight.title}")
        
        summary_parts.append(f"\n📊 Data Quality: Analytics ready and reliable")
        summary_parts.append(f"⏱️ Report generated in real-time")
        
        return "\n".join(summary_parts)
    
    def _calculate_value_metrics(
        self, 
        analytics_results: List[AnalyticsResult],
        confirmation_session: UserConfirmationSession
    ) -> Dict[str, Any]:
        """Calculate value metrics from analytics execution."""
        
        return {
            "analytics_enabled": len(analytics_results),
            "total_analytics": 5,
            "analytics_coverage": len(analytics_results) / 5 * 100,
            "insights_generated": sum(len(r.key_insights) for r in analytics_results),
            "recommendations_provided": sum(len(r.recommendations) for r in analytics_results),
            "data_rows_analyzed": sum(r.rows_processed for r in analytics_results),
            "business_value": "high" if len(analytics_results) >= 3 else "medium" if len(analytics_results) >= 1 else "low"
        }
    
    def _calculate_mapping_roi(
        self,
        confirmation_session: UserConfirmationSession,
        analytics_results: List[AnalyticsResult]
    ) -> Dict[str, Any]:
        """Calculate ROI of the mapping effort."""
        
        # Simple ROI calculation
        original_evaluation = confirmation_session.escalation_result.original_evaluation
        
        effort_investment = {
            "columns_processed": len(original_evaluation.column_decisions),
            "user_confirmations": len(confirmation_session.user_selections),
            "processing_time": confirmation_session.escalation_result.total_processing_time,
            "gpt_cost": confirmation_session.escalation_result.estimated_cost
        }
        
        business_value = {
            "analytics_unlocked": len(analytics_results),
            "insights_generated": sum(len(r.key_insights) for r in analytics_results),
            "recommendations_count": sum(len(r.recommendations) for r in analytics_results),
            "data_quality_score": "high"
        }
        
        # ROI score (simplified)
        effort_score = effort_investment["user_confirmations"] + effort_investment["processing_time"]
        value_score = business_value["analytics_unlocked"] * 20 + business_value["insights_generated"] * 2
        
        roi_ratio = value_score / max(effort_score, 1)
        
        return {
            "effort_investment": effort_investment,
            "business_value": business_value,
            "roi_score": roi_ratio,
            "roi_category": "excellent" if roi_ratio > 5 else "good" if roi_ratio > 2 else "fair"
        }
    
    # Helper methods
    def _get_expected_type(self, canonical_type: str) -> str:
        """Get expected data type for canonical column."""
        type_map = {
            CanonicalColumnType.DATE.value: "datetime64[ns]",
            CanonicalColumnType.SALES.value: "numeric",
            CanonicalColumnType.AMOUNT.value: "numeric",
            CanonicalColumnType.QUANTITY.value: "numeric",
            CanonicalColumnType.PRODUCT.value: "object",
            CanonicalColumnType.REGION.value: "object",
            CanonicalColumnType.CUSTOMER.value: "object",
            CanonicalColumnType.TRANSACTION_ID.value: "object"
        }
        return type_map.get(canonical_type, "object")
    
    def _validate_type_match(self, canonical_type: str, actual_type: str) -> bool:
        """Validate if actual type matches expected type."""
        expected = self._get_expected_type(canonical_type)
        
        if expected == "numeric":
            return "int" in actual_type or "float" in actual_type
        elif expected == "datetime64[ns]":
            return "datetime" in actual_type
        else:
            return "object" in actual_type or "string" in actual_type
    
    def _calculate_quality_score(
        self, 
        null_percentage: float, 
        type_match: bool, 
        has_valid_values: bool, 
        issue_count: int
    ) -> float:
        """Calculate overall quality score for a column."""
        
        score = 1.0
        
        # Null penalty
        score -= (null_percentage / 100) * 0.5
        
        # Type mismatch penalty
        if not type_match:
            score -= 0.3
        
        # Invalid values penalty
        if not has_valid_values:
            score -= 0.4
        
        # Issue penalty
        score -= issue_count * 0.1
        
        return max(0.0, score)

# Global instance for easy access
analytics_engine = AnalyticsEngine()
