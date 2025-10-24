# descriptive_analytics.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
import warnings
warnings.filterwarnings('ignore')

class DescriptiveAnalytics:
    """
    Advanced descriptive analytics logic for TANAW.
    Implements correlation analysis, anomaly detection, trend analysis, and comprehensive summaries.
    """
    
    def __init__(self):
        self.anomaly_detectors = {
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'local_outlier_factor': LocalOutlierFactor(n_neighbors=20, contamination=0.1)
        }
    
    def generate_descriptive_analytics(self, df: pd.DataFrame, 
                                     column_mapping: Dict[str, Any] = None,
                                     analytics_type: str = None) -> Dict[str, Any]:
        """
        Generate descriptive analytics for specific analytics type or comprehensive analysis.
        
        Args:
            df: Cleaned DataFrame
            column_mapping: Column mapping information
            analytics_type: Specific analytics type to generate
            
        Returns:
            Dict containing descriptive analytics results
        """
        if analytics_type:
            return self._generate_specific_analytics(df, column_mapping, analytics_type)
        else:
            return self.generate_comprehensive_analysis(df, column_mapping)
    
    def generate_comprehensive_analysis(self, df: pd.DataFrame, 
                                      column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive descriptive analytics for the dataset.
        
        Args:
            df: Cleaned DataFrame
            column_mapping: Column mapping information
            
        Returns:
            Dict containing all descriptive analytics results
        """
        analysis_results = {
            'summary_statistics': {},
            'trend_analysis': {},
            'correlation_analysis': {},
            'anomaly_detection': {},
            'distribution_analysis': {},
            'categorical_analysis': {},
            'temporal_analysis': {},
            'insights': [],
            'recommendations': []
        }
        
        try:
            # 1. Summary Statistics
            analysis_results['summary_statistics'] = self._generate_summary_statistics(df)
            
            # 2. Trend Analysis
            analysis_results['trend_analysis'] = self._analyze_trends(df, column_mapping)
            
            # 3. Correlation Analysis
            analysis_results['correlation_analysis'] = self._analyze_correlations(df)
            
            # 4. Anomaly Detection
            analysis_results['anomaly_detection'] = self._detect_anomalies(df, column_mapping)
            
            # 5. Distribution Analysis
            analysis_results['distribution_analysis'] = self._analyze_distributions(df)
            
            # 6. Categorical Analysis
            analysis_results['categorical_analysis'] = self._analyze_categorical_data(df, column_mapping)
            
            # 7. Temporal Analysis
            analysis_results['temporal_analysis'] = self._analyze_temporal_patterns(df, column_mapping)
            
            # 8. Generate Insights and Recommendations
            analysis_results['insights'] = self._generate_insights(analysis_results)
            analysis_results['recommendations'] = self._generate_recommendations(analysis_results)
            
        except Exception as e:
            analysis_results['error'] = f"Analytics generation failed: {str(e)}"
        
        return analysis_results
    
    def _generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        summary = {
            'dataset_overview': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'data_types': df.dtypes.value_counts().to_dict()
            },
            'numeric_summary': {},
            'categorical_summary': {},
            'missing_data_summary': {}
        }
        
        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
            
            # Additional numeric metrics
            for col in numeric_cols:
                summary['numeric_summary'][col]['skewness'] = float(stats.skew(df[col].dropna()))
                summary['numeric_summary'][col]['kurtosis'] = float(stats.kurtosis(df[col].dropna()))
                summary['numeric_summary'][col]['coefficient_of_variation'] = float(
                    df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
                )
        
        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            summary['categorical_summary'] = {}
            for col in categorical_cols:
                summary['categorical_summary'][col] = {
                    'unique_count': df[col].nunique(),
                    'most_frequent': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                    'frequency_of_most_frequent': float(df[col].value_counts().iloc[0]) if len(df[col]) > 0 else 0,
                    'top_5_values': df[col].value_counts().head(5).to_dict()
                }
        
        # Missing data summary
        missing_data = df.isnull().sum()
        summary['missing_data_summary'] = {
            'columns_with_missing': missing_data[missing_data > 0].to_dict(),
            'total_missing_percentage': float((missing_data.sum() / (len(df) * len(df.columns))) * 100)
        }
        
        return summary
    
    def _analyze_trends(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze trends in the data."""
        trend_analysis = {
            'time_series_trends': {},
            'growth_rates': {},
            'seasonal_patterns': {}
        }
        
        # Find temporal columns
        temporal_cols = self._get_temporal_columns(df, column_mapping)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if temporal_cols and len(numeric_cols) > 0:
            for date_col in temporal_cols:
                for num_col in numeric_cols:
                    # Ensure date column is datetime
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    df_temp = df_temp.dropna(subset=[date_col, num_col])
                    
                    if len(df_temp) > 1:
                        # Sort by date
                        df_temp = df_temp.sort_values(date_col)
                        
                        # Calculate trend
                        x = np.arange(len(df_temp))
                        y = df_temp[num_col].values
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                        
                        trend_analysis['time_series_trends'][f"{date_col}_{num_col}"] = {
                            'slope': float(slope),
                            'r_squared': float(r_value ** 2),
                            'p_value': float(p_value),
                            'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                            'trend_strength': 'strong' if abs(r_value) > 0.7 else 'moderate' if abs(r_value) > 0.3 else 'weak'
                        }
                        
                        # Calculate growth rate
                        if len(df_temp) > 1:
                            first_value = df_temp[num_col].iloc[0]
                            last_value = df_temp[num_col].iloc[-1]
                            if first_value != 0:
                                growth_rate = ((last_value - first_value) / first_value) * 100
                                trend_analysis['growth_rates'][f"{date_col}_{num_col}"] = {
                                    'total_growth_percentage': float(growth_rate),
                                    'first_value': float(first_value),
                                    'last_value': float(last_value)
                                }
        
        return trend_analysis
    
    def _get_temporal_columns(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> List[str]:
        """Get temporal columns from the dataset."""
        temporal_cols = []
        
        if column_mapping:
            for col in df.columns:
                mapped_type = column_mapping.get(col, {}).get('mapped_column', '').lower()
                if mapped_type in ['date', 'timestamp', 'time']:
                    temporal_cols.append(col)
        
        # Fallback: detect temporal columns by name
        if not temporal_cols:
            for col in df.columns:
                if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'created', 'updated']):
                    temporal_cols.append(col)
        
        return temporal_cols
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlations between numeric variables."""
        correlation_analysis = {
            'correlation_matrix': {},
            'strong_correlations': [],
            'correlation_insights': []
        }
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) > 1:
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr()
            correlation_analysis['correlation_matrix'] = corr_matrix.to_dict()
            
            # Find strong correlations (|r| > 0.7)
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'variable1': corr_matrix.columns[i],
                            'variable2': corr_matrix.columns[j],
                            'correlation': float(corr_value),
                            'strength': 'very_strong' if abs(corr_value) > 0.9 else 'strong'
                        })
            
            correlation_analysis['strong_correlations'] = strong_correlations
            
            # Generate correlation insights
            if strong_correlations:
                correlation_analysis['correlation_insights'].append(
                    f"Found {len(strong_correlations)} strong correlations between variables"
                )
                
                for corr in strong_correlations[:3]:  # Top 3 correlations
                    direction = "positive" if corr['correlation'] > 0 else "negative"
                    correlation_analysis['correlation_insights'].append(
                        f"Strong {direction} correlation ({corr['correlation']:.3f}) between {corr['variable1']} and {corr['variable2']}"
                    )
        
        return correlation_analysis
    
    def _detect_anomalies(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect anomalies in the dataset."""
        anomaly_analysis = {
            'statistical_anomalies': {},
            'ml_based_anomalies': {},
            'business_rule_anomalies': {},
            'anomaly_summary': {}
        }
        
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) > 0:
            # Statistical anomaly detection (Z-score and IQR)
            for col in numeric_df.columns:
                z_scores = np.abs(stats.zscore(numeric_df[col].dropna()))
                iqr_anomalies = self._detect_iqr_anomalies(numeric_df[col])
                
                anomaly_analysis['statistical_anomalies'][col] = {
                    'z_score_anomalies': int((z_scores > 3).sum()),
                    'iqr_anomalies': int(iqr_anomalies.sum()),
                    'total_statistical_anomalies': int((z_scores > 3).sum() + iqr_anomalies.sum())
                }
            
            # ML-based anomaly detection
            if len(numeric_df) > 10:  # Need sufficient data for ML
                try:
                    # Isolation Forest
                    iso_forest = IsolationForest(contamination=0.1, random_state=42)
                    iso_anomalies = iso_forest.fit_predict(numeric_df.fillna(numeric_df.median()))
                    
                    # Local Outlier Factor
                    lof = LocalOutlierFactor(n_neighbors=min(20, len(numeric_df)//2), contamination=0.1)
                    lof_anomalies = lof.fit_predict(numeric_df.fillna(numeric_df.median()))
                    
                    anomaly_analysis['ml_based_anomalies'] = {
                        'isolation_forest_anomalies': int((iso_anomalies == -1).sum()),
                        'local_outlier_factor_anomalies': int((lof_anomalies == -1).sum()),
                        'consensus_anomalies': int(((iso_anomalies == -1) & (lof_anomalies == -1)).sum())
                    }
                except Exception as e:
                    anomaly_analysis['ml_based_anomalies']['error'] = str(e)
        
        # Business rule anomalies
        anomaly_analysis['business_rule_anomalies'] = self._detect_business_anomalies(df, column_mapping)
        
        # Generate anomaly summary
        anomaly_analysis['anomaly_summary'] = self._generate_anomaly_summary(anomaly_analysis)
        
        return anomaly_analysis
    
    def _detect_iqr_anomalies(self, series: pd.Series) -> pd.Series:
        """Detect anomalies using IQR method."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    def _detect_business_anomalies(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect business rule violations."""
        business_anomalies = {}
        
        if column_mapping:
            # Check price columns for negative values
            price_cols = self._get_columns_by_type(df, column_mapping, ['price', 'amount', 'cost', 'revenue'])
            for col in price_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    negative_prices = (df[col] < 0).sum()
                    if negative_prices > 0:
                        business_anomalies[f"{col}_negative_values"] = {
                            'count': int(negative_prices),
                            'rule': 'prices_should_be_positive',
                            'severity': 'high'
                        }
            
            # Check quantity columns for negative values
            quantity_cols = self._get_columns_by_type(df, column_mapping, ['quantity', 'qty', 'units'])
            for col in quantity_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    negative_quantities = (df[col] < 0).sum()
                    if negative_quantities > 0:
                        business_anomalies[f"{col}_negative_values"] = {
                            'count': int(negative_quantities),
                            'rule': 'quantities_should_be_positive',
                            'severity': 'high'
                        }
        
        return business_anomalies
    
    def _get_columns_by_type(self, df: pd.DataFrame, column_mapping: Dict[str, Any], 
                           types: List[str]) -> List[str]:
        """Get columns that match specified types."""
        if not column_mapping:
            return []
        
        matching_columns = []
        for col in df.columns:
            mapped_type = column_mapping.get(col, {}).get('mapped_column', '').lower()
            if mapped_type in types:
                matching_columns.append(col)
        
        return matching_columns
    
    def _generate_anomaly_summary(self, anomaly_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all detected anomalies."""
        summary = {
            'total_anomalies': 0,
            'high_severity_anomalies': 0,
            'anomaly_types': [],
            'recommendations': []
        }
        
        # Count statistical anomalies
        for col, anomalies in anomaly_analysis.get('statistical_anomalies', {}).items():
            total = anomalies.get('total_statistical_anomalies', 0)
            summary['total_anomalies'] += total
            if total > 0:
                summary['anomaly_types'].append(f"Statistical anomalies in {col}")
        
        # Count ML anomalies
        ml_anomalies = anomaly_analysis.get('ml_based_anomalies', {})
        if 'consensus_anomalies' in ml_anomalies:
            summary['total_anomalies'] += ml_anomalies['consensus_anomalies']
            if ml_anomalies['consensus_anomalies'] > 0:
                summary['anomaly_types'].append("ML-detected anomalies")
        
        # Count business rule anomalies
        for anomaly_name, details in anomaly_analysis.get('business_rule_anomalies', {}).items():
            summary['total_anomalies'] += details.get('count', 0)
            if details.get('severity') == 'high':
                summary['high_severity_anomalies'] += details.get('count', 0)
            summary['anomaly_types'].append(f"Business rule violation: {details.get('rule', 'unknown')}")
        
        # Generate recommendations
        if summary['total_anomalies'] > 0:
            summary['recommendations'].append("Review detected anomalies for data quality issues")
        if summary['high_severity_anomalies'] > 0:
            summary['recommendations'].append("Address high-severity anomalies immediately")
        
        return summary
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze distributions of numeric variables."""
        distribution_analysis = {
            'distribution_types': {},
            'normality_tests': {},
            'distribution_insights': []
        }
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                # Determine distribution type
                distribution_type = self._classify_distribution(series)
                distribution_analysis['distribution_types'][col] = distribution_type
                
                # Normality test (if sample size is sufficient)
                if len(series) >= 8:  # Minimum sample size for Shapiro-Wilk
                    try:
                        shapiro_stat, shapiro_p = stats.shapiro(series.head(5000))  # Limit for performance
                        distribution_analysis['normality_tests'][col] = {
                            'shapiro_wilk_statistic': float(shapiro_stat),
                            'shapiro_wilk_p_value': float(shapiro_p),
                            'is_normal': shapiro_p > 0.05
                        }
                    except Exception as e:
                        distribution_analysis['normality_tests'][col] = {'error': str(e)}
        
        # Generate distribution insights
        normal_cols = [col for col, test in distribution_analysis['normality_tests'].items() 
                      if test.get('is_normal', False)]
        if normal_cols:
            distribution_analysis['distribution_insights'].append(
                f"Columns with approximately normal distributions: {', '.join(normal_cols)}"
            )
        
        return distribution_analysis
    
    def _classify_distribution(self, series: pd.Series) -> str:
        """Classify the type of distribution."""
        skewness = stats.skew(series)
        kurtosis = stats.kurtosis(series)
        
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return 'approximately_normal'
        elif skewness > 1:
            return 'highly_right_skewed'
        elif skewness < -1:
            return 'highly_left_skewed'
        elif skewness > 0.5:
            return 'moderately_right_skewed'
        elif skewness < -0.5:
            return 'moderately_left_skewed'
        elif kurtosis > 3:
            return 'heavy_tailed'
        elif kurtosis < -1:
            return 'light_tailed'
        else:
            return 'approximately_symmetric'
    
    def _analyze_categorical_data(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze categorical data patterns."""
        categorical_analysis = {
            'category_distributions': {},
            'category_insights': [],
            'cross_category_analysis': {}
        }
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            
            categorical_analysis['category_distributions'][col] = {
                'unique_categories': df[col].nunique(),
                'most_frequent_category': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_frequent_percentage': float((value_counts.iloc[0] / len(df)) * 100) if len(value_counts) > 0 else 0,
                'top_5_categories': value_counts.head(5).to_dict(),
                'category_balance': self._calculate_category_balance(value_counts)
            }
        
        # Cross-category analysis for multiple categorical columns
        if len(categorical_cols) > 1:
            categorical_analysis['cross_category_analysis'] = self._analyze_category_relationships(df, categorical_cols)
        
        return categorical_analysis
    
    def _calculate_category_balance(self, value_counts: pd.Series) -> str:
        """Calculate how balanced the categories are."""
        if len(value_counts) == 0:
            return 'empty'
        
        # Calculate Gini coefficient as a measure of balance
        n = len(value_counts)
        if n <= 1:
            return 'single_category'
        
        proportions = value_counts.values / value_counts.sum()
        gini = 1 - sum(p**2 for p in proportions)
        
        if gini > 0.7:
            return 'highly_imbalanced'
        elif gini > 0.5:
            return 'moderately_imbalanced'
        elif gini > 0.3:
            return 'somewhat_balanced'
        else:
            return 'well_balanced'
    
    def _analyze_category_relationships(self, df: pd.DataFrame, categorical_cols: List[str]) -> Dict[str, Any]:
        """Analyze relationships between categorical variables."""
        relationships = {}
        
        # Analyze top combinations
        for i, col1 in enumerate(categorical_cols):
            for col2 in categorical_cols[i+1:]:
                crosstab = pd.crosstab(df[col1], df[col2])
                
                # Calculate Cramér's V (measure of association)
                try:
                    chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
                    n = crosstab.sum().sum()
                    cramers_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
                    
                    relationships[f"{col1}_vs_{col2}"] = {
                        'cramers_v': float(cramers_v),
                        'chi2_p_value': float(p_value),
                        'association_strength': 'strong' if cramers_v > 0.5 else 'moderate' if cramers_v > 0.3 else 'weak',
                        'top_combination': self._get_top_combination(crosstab)
                    }
                except Exception as e:
                    relationships[f"{col1}_vs_{col2}"] = {'error': str(e)}
        
        return relationships
    
    def _get_top_combination(self, crosstab: pd.DataFrame) -> Dict[str, Any]:
        """Get the most frequent combination in a crosstab."""
        max_idx = crosstab.stack().idxmax()
        max_value = crosstab.loc[max_idx[0], max_idx[1]]
        
        return {
            'category1': max_idx[0],
            'category2': max_idx[1],
            'count': int(max_value),
            'percentage': float((max_value / crosstab.sum().sum()) * 100)
        }
    
    def _analyze_temporal_patterns(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze temporal patterns in the data."""
        temporal_analysis = {
            'temporal_coverage': {},
            'seasonality_analysis': {},
            'temporal_insights': []
        }
        
        temporal_cols = self._get_temporal_columns(df, column_mapping)
        
        for date_col in temporal_cols:
            try:
                df_temp = df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                df_temp = df_temp.dropna(subset=[date_col])
                
                if len(df_temp) > 0:
                    temporal_analysis['temporal_coverage'][date_col] = {
                        'earliest_date': df_temp[date_col].min().isoformat(),
                        'latest_date': df_temp[date_col].max().isoformat(),
                        'date_range_days': (df_temp[date_col].max() - df_temp[date_col].min()).days,
                        'total_records': len(df_temp)
                    }
                    
                    # Analyze frequency patterns
                    freq_analysis = self._analyze_temporal_frequency(df_temp[date_col])
                    temporal_analysis['seasonality_analysis'][date_col] = freq_analysis
                    
            except Exception as e:
                temporal_analysis['temporal_coverage'][date_col] = {'error': str(e)}
        
        return temporal_analysis
    
    def _analyze_temporal_frequency(self, date_series: pd.Series) -> Dict[str, Any]:
        """Analyze temporal frequency patterns."""
        try:
            # Sort by date
            sorted_dates = date_series.sort_values()
            
            # Calculate time differences
            time_diffs = sorted_dates.diff().dropna()
            
            # Analyze frequency
            freq_analysis = {
                'median_interval_days': float(time_diffs.median().total_seconds() / 86400),
                'interval_consistency': 'high' if time_diffs.std() < time_diffs.mean() * 0.5 else 'low',
                'detected_frequency': str(pd.infer_freq(sorted_dates)) if len(sorted_dates) > 3 else None
            }
            
            return freq_analysis
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate business insights from the analysis."""
        insights = []
        
        # Summary insights
        summary = analysis_results.get('summary_statistics', {})
        if summary:
            dataset_info = summary.get('dataset_overview', {})
            insights.append(f"Dataset contains {dataset_info.get('total_rows', 0)} records across {dataset_info.get('total_columns', 0)} columns")
            
            missing_data = summary.get('missing_data_summary', {})
            missing_pct = missing_data.get('total_missing_percentage', 0)
            if missing_pct > 10:
                insights.append(f"⚠️ High missing data percentage: {missing_pct:.1f}%")
            elif missing_pct > 0:
                insights.append(f"Missing data percentage: {missing_pct:.1f}%")
        
        # Trend insights
        trends = analysis_results.get('trend_analysis', {})
        growth_rates = trends.get('growth_rates', {})
        if growth_rates:
            for metric, growth in growth_rates.items():
                growth_pct = growth.get('total_growth_percentage', 0)
                direction = "increased" if growth_pct > 0 else "decreased"
                insights.append(f"📈 {metric} {direction} by {abs(growth_pct):.1f}% over the time period")
        
        # Correlation insights
        correlations = analysis_results.get('correlation_analysis', {})
        strong_corrs = correlations.get('strong_correlations', [])
        if strong_corrs:
            insights.append(f"🔗 Found {len(strong_corrs)} strong correlations between variables")
        
        # Anomaly insights
        anomalies = analysis_results.get('anomaly_detection', {})
        anomaly_summary = anomalies.get('anomaly_summary', {})
        total_anomalies = anomaly_summary.get('total_anomalies', 0)
        if total_anomalies > 0:
            insights.append(f"🚨 Detected {total_anomalies} anomalies requiring attention")
        
        return insights
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Data quality recommendations
        summary = analysis_results.get('summary_statistics', {})
        missing_data = summary.get('missing_data_summary', {})
        missing_pct = missing_data.get('total_missing_percentage', 0)
        
        if missing_pct > 20:
            recommendations.append("Consider data collection improvements to reduce missing values")
        elif missing_pct > 5:
            recommendations.append("Review data collection processes for missing value patterns")
        
        # Anomaly recommendations
        anomalies = analysis_results.get('anomaly_detection', {})
        anomaly_summary = anomalies.get('anomaly_summary', {})
        high_severity = anomaly_summary.get('high_severity_anomalies', 0)
        
        if high_severity > 0:
            recommendations.append("Immediately investigate and resolve high-severity anomalies")
        
        # Distribution recommendations
        distributions = analysis_results.get('distribution_analysis', {})
        distribution_types = distributions.get('distribution_types', {})
        
        skewed_cols = [col for col, dist_type in distribution_types.items() 
                      if 'skewed' in dist_type]
        if skewed_cols:
            recommendations.append(f"Consider data transformation for skewed variables: {', '.join(skewed_cols)}")
        
        # Categorical recommendations
        categorical = analysis_results.get('categorical_analysis', {})
        category_distributions = categorical.get('category_distributions', {})
        
        imbalanced_cols = [col for col, dist in category_distributions.items() 
                          if dist.get('category_balance') in ['highly_imbalanced', 'moderately_imbalanced']]
        if imbalanced_cols:
            recommendations.append(f"Review imbalanced categorical variables for potential bias: {', '.join(imbalanced_cols)}")
        
        return recommendations
    
    def _generate_specific_analytics(self, df: pd.DataFrame, 
                                   column_mapping: Dict[str, Any],
                                   analytics_type: str) -> Dict[str, Any]:
        """
        Generate specific analytics based on the analytics type.
        
        Args:
            df: Cleaned DataFrame
            column_mapping: Column mapping information
            analytics_type: Type of analytics to generate
            
        Returns:
            Dict containing specific analytics results
        """
        try:
            if analytics_type == 'sales_summary':
                return self._generate_sales_summary_analytics(df, column_mapping)
            elif analytics_type == 'product_performance':
                return self._generate_product_performance_analytics(df, column_mapping)
            elif analytics_type == 'regional_analysis':
                return self._generate_regional_analysis(df, column_mapping)
            elif analytics_type == 'correlation_analysis':
                return self._generate_correlation_analysis(df, column_mapping)
            elif analytics_type == 'anomaly_detection':
                return self._generate_anomaly_detection(df, column_mapping)
            else:
                # Default to comprehensive analysis for unknown types
                return self.generate_comprehensive_analysis(df, column_mapping)
                
        except Exception as e:
            return {
                'error': f"Failed to generate {analytics_type} analytics: {str(e)}",
                'analytics_type': analytics_type,
                'status': 'failed'
            }
    
    def _generate_sales_summary_analytics(self, df: pd.DataFrame, 
                                        column_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales summary analytics."""
        # Extract mapped columns
        date_col = self._find_mapped_column(df, column_mapping, ['date', 'timestamp', 'time'])
        sales_col = self._find_mapped_column(df, column_mapping, ['sales', 'amount', 'revenue'])
        product_col = self._find_mapped_column(df, column_mapping, ['product', 'item', 'sku'])
        region_col = self._find_mapped_column(df, column_mapping, ['region', 'location', 'area'])
        
        results = {
            'analytics_type': 'sales_summary',
            'summary_metrics': {},
            'trend_analysis': {},
            'breakdowns': {},
            'insights': [],
            'charts': []
        }
        
        try:
            if sales_col:
                # Basic sales metrics
                total_sales = df[sales_col].sum()
                avg_sales = df[sales_col].mean()
                median_sales = df[sales_col].median()
                
                results['summary_metrics'] = {
                    'total_sales': float(total_sales),
                    'average_sales': float(avg_sales),
                    'median_sales': float(median_sales),
                    'total_transactions': len(df)
                }
                
                # Product breakdown
                if product_col:
                    product_sales = df.groupby(product_col)[sales_col].agg(['sum', 'count', 'mean']).reset_index()
                    product_sales = product_sales.sort_values('sum', ascending=False)
                    
                    results['breakdowns']['product_performance'] = {
                        'top_products': product_sales.head(10).to_dict('records'),
                        'total_products': product_sales.shape[0]
                    }
                
                # Regional breakdown
                if region_col:
                    regional_sales = df.groupby(region_col)[sales_col].agg(['sum', 'count', 'mean']).reset_index()
                    regional_sales = regional_sales.sort_values('sum', ascending=False)
                    
                    results['breakdowns']['regional_performance'] = {
                        'top_regions': regional_sales.head(10).to_dict('records'),
                        'total_regions': regional_sales.shape[0]
                    }
                
                # Time trend analysis
                if date_col:
                    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                    df_clean = df.dropna(subset=[date_col])
                    
                    if len(df_clean) > 0:
                        df_clean['year_month'] = df_clean[date_col].dt.to_period('M')
                        monthly_sales = df_clean.groupby('year_month')[sales_col].sum().reset_index()
                        
                        results['trend_analysis'] = {
                            'monthly_trend': monthly_sales.to_dict('records'),
                            'growth_rate': self._calculate_growth_rate(monthly_sales[sales_col])
                        }
                
                # Generate insights
                results['insights'] = self._generate_sales_insights(results)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _generate_product_performance_analytics(self, df: pd.DataFrame, 
                                             column_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product performance analytics."""
        product_col = self._find_mapped_column(df, column_mapping, ['product', 'item', 'sku'])
        sales_col = self._find_mapped_column(df, column_mapping, ['sales', 'amount', 'revenue'])
        quantity_col = self._find_mapped_column(df, column_mapping, ['quantity', 'qty', 'units'])
        
        results = {
            'analytics_type': 'product_performance',
            'product_rankings': {},
            'performance_metrics': {},
            'insights': [],
            'charts': []
        }
        
        try:
            if product_col and sales_col:
                # Product performance metrics
                product_perf = df.groupby(product_col).agg({
                    sales_col: ['sum', 'mean', 'count'],
                    quantity_col: ['sum', 'mean'] if quantity_col else []
                }).round(2)
                
                # Flatten column names
                product_perf.columns = ['_'.join(col).strip() for col in product_perf.columns]
                product_perf = product_perf.reset_index()
                
                # Rankings
                results['product_rankings'] = {
                    'top_by_sales': product_perf.nlargest(10, f'{sales_col}_sum').to_dict('records'),
                    'top_by_quantity': product_perf.nlargest(10, f'{quantity_col}_sum').to_dict('records') if quantity_col else []
                }
                
                # Performance metrics
                results['performance_metrics'] = {
                    'total_products': product_perf.shape[0],
                    'best_performing_product': product_perf.loc[product_perf[f'{sales_col}_sum'].idxmax(), product_col],
                    'worst_performing_product': product_perf.loc[product_perf[f'{sales_col}_sum'].idxmin(), product_col]
                }
                
                results['insights'] = self._generate_product_insights(results)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _generate_regional_analysis(self, df: pd.DataFrame, 
                                  column_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Generate regional analysis."""
        region_col = self._find_mapped_column(df, column_mapping, ['region', 'location', 'area', 'territory'])
        sales_col = self._find_mapped_column(df, column_mapping, ['sales', 'amount', 'revenue'])
        
        results = {
            'analytics_type': 'regional_analysis',
            'regional_metrics': {},
            'geographic_distribution': {},
            'insights': [],
            'charts': []
        }
        
        try:
            if region_col and sales_col:
                regional_data = df.groupby(region_col)[sales_col].agg(['sum', 'count', 'mean']).reset_index()
                regional_data = regional_data.sort_values('sum', ascending=False)
                
                results['regional_metrics'] = {
                    'total_regions': regional_data.shape[0],
                    'top_region': regional_data.iloc[0][region_col],
                    'regional_performance': regional_data.to_dict('records')
                }
                
                # Calculate regional concentration
                total_sales = regional_data['sum'].sum()
                regional_data['percentage'] = (regional_data['sum'] / total_sales * 100).round(2)
                
                results['geographic_distribution'] = {
                    'concentration_analysis': regional_data.to_dict('records'),
                    'top_3_regions_share': regional_data.head(3)['percentage'].sum()
                }
                
                results['insights'] = self._generate_regional_insights(results)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _generate_correlation_analysis(self, df: pd.DataFrame, 
                                     column_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correlation analysis."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {
            'analytics_type': 'correlation_analysis',
            'correlation_matrix': {},
            'strong_correlations': {},
            'insights': [],
            'charts': []
        }
        
        try:
            if len(numeric_cols) > 1:
                # Calculate correlation matrix
                corr_matrix = df[numeric_cols].corr()
                
                # Find strong correlations
                strong_corrs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.7:  # Strong correlation threshold
                            strong_corrs.append({
                                'variable1': corr_matrix.columns[i],
                                'variable2': corr_matrix.columns[j],
                                'correlation': float(corr_val)
                            })
                
                results['correlation_matrix'] = corr_matrix.to_dict()
                results['strong_correlations'] = strong_corrs
                
                results['insights'] = self._generate_correlation_insights(results)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _generate_anomaly_detection(self, df: pd.DataFrame, 
                                  column_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Generate anomaly detection analysis."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {
            'analytics_type': 'anomaly_detection',
            'anomaly_summary': {},
            'anomalies_by_column': {},
            'insights': [],
            'charts': []
        }
        
        try:
            if len(numeric_cols) > 0:
                # Use existing anomaly detection logic
                anomaly_results = self.detect_anomalies(df, numeric_cols)
                
                results['anomaly_summary'] = anomaly_results.get('anomaly_summary', {})
                results['anomalies_by_column'] = anomaly_results.get('anomalies_by_column', {})
                
                results['insights'] = self._generate_anomaly_insights(results)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _find_mapped_column(self, df: pd.DataFrame, column_mapping: Dict[str, Any], 
                          target_types: List[str]) -> Optional[str]:
        """Find a column mapped to any of the target types."""
        if not column_mapping:
            return None
        
        mapped_columns = column_mapping.get('mapped_columns', [])
        
        for col_info in mapped_columns:
            if col_info.get('status') == 'mapped':
                mapped_type = col_info.get('mapped_column', '').lower()
                if mapped_type in [t.lower() for t in target_types]:
                    return col_info.get('original_column')
        
        return None
    
    def _calculate_growth_rate(self, series: pd.Series) -> float:
        """Calculate growth rate for a time series."""
        if len(series) < 2:
            return 0.0
        
        first_value = series.iloc[0]
        last_value = series.iloc[-1]
        
        if first_value == 0:
            return 0.0
        
        return float((last_value - first_value) / first_value * 100)
    
    def _generate_sales_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights for sales summary analytics."""
        insights = []
        
        summary = results.get('summary_metrics', {})
        if summary:
            insights.append(f"📊 Total sales: ${summary.get('total_sales', 0):,.2f}")
            insights.append(f"💰 Average transaction: ${summary.get('average_sales', 0):,.2f}")
            insights.append(f"🛒 Total transactions: {summary.get('total_transactions', 0):,}")
        
        breakdowns = results.get('breakdowns', {})
        if breakdowns.get('product_performance'):
            insights.append("🏆 Product performance analysis available")
        
        if breakdowns.get('regional_performance'):
            insights.append("🌍 Regional performance analysis available")
        
        trend = results.get('trend_analysis', {})
        if trend.get('growth_rate'):
            growth_rate = trend['growth_rate']
            if growth_rate > 0:
                insights.append(f"📈 Sales showing {growth_rate:.1f}% growth trend")
            elif growth_rate < 0:
                insights.append(f"📉 Sales showing {abs(growth_rate):.1f}% decline trend")
        
        return insights
    
    def _generate_product_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights for product performance analytics."""
        insights = []
        
        metrics = results.get('performance_metrics', {})
        if metrics:
            insights.append(f"🏆 Best performing product: {metrics.get('best_performing_product', 'N/A')}")
            insights.append(f"📊 Total products analyzed: {metrics.get('total_products', 0)}")
        
        rankings = results.get('product_rankings', {})
        if rankings.get('top_by_sales'):
            insights.append("💎 Top 10 products by sales identified")
        
        return insights
    
    def _generate_regional_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights for regional analysis."""
        insights = []
        
        metrics = results.get('regional_metrics', {})
        if metrics:
            insights.append(f"🏆 Top performing region: {metrics.get('top_region', 'N/A')}")
            insights.append(f"🌍 Total regions analyzed: {metrics.get('total_regions', 0)}")
        
        distribution = results.get('geographic_distribution', {})
        if distribution.get('top_3_regions_share'):
            share = distribution['top_3_regions_share']
            insights.append(f"📊 Top 3 regions account for {share:.1f}% of total sales")
        
        return insights
    
    def _generate_correlation_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights for correlation analysis."""
        insights = []
        
        strong_corrs = results.get('strong_correlations', [])
        if strong_corrs:
            insights.append(f"🔗 Found {len(strong_corrs)} strong correlations")
            for corr in strong_corrs[:3]:  # Show top 3
                insights.append(f"📈 {corr['variable1']} ↔ {corr['variable2']}: {corr['correlation']:.2f}")
        else:
            insights.append("📊 No strong correlations found between variables")
        
        return insights
    
    def _generate_anomaly_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate insights for anomaly detection."""
        insights = []
        
        summary = results.get('anomaly_summary', {})
        if summary:
            total_anomalies = summary.get('total_anomalies', 0)
            high_severity = summary.get('high_severity_anomalies', 0)
            
            insights.append(f"🚨 Total anomalies detected: {total_anomalies}")
            if high_severity > 0:
                insights.append(f"⚠️ High severity anomalies: {high_severity}")
        
        return insights
