"""
TANAW Anomaly Detection System
Detects unusual patterns and anomalies in business data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class TANAWAnomalyDetector:
    """
    Detects anomalies and unusual patterns in business data
    """
    
    def __init__(self):
        """Initialize anomaly detection system"""
        self.anomaly_threshold = 0.1  # 10% threshold for anomaly detection
        self.z_score_threshold = 2.5  # Z-score threshold for statistical anomalies
        
    def detect_anomalies(self, df: pd.DataFrame, domain: str = "sales") -> Dict[str, Any]:
        """
        Detect anomalies in the dataset
        
        Args:
            df: DataFrame to analyze
            domain: Business domain for context-specific detection
            
        Returns:
            Dict containing anomaly detection results
        """
        try:
            anomalies = {
                "total_anomalies": 0,
                "anomaly_types": [],
                "critical_alerts": [],
                "warnings": [],
                "data_quality_issues": [],
                "detection_summary": {}
            }
            
            # Domain-specific anomaly detection
            if domain == "sales":
                anomalies.update(self._detect_sales_anomalies(df))
            elif domain == "inventory":
                anomalies.update(self._detect_inventory_anomalies(df))
            elif domain == "finance":
                anomalies.update(self._detect_finance_anomalies(df))
            elif domain == "customer":
                anomalies.update(self._detect_customer_anomalies(df))
            else:
                anomalies.update(self._detect_general_anomalies(df))
            
            # Calculate total anomalies
            anomalies["total_anomalies"] = (
                len(anomalies["critical_alerts"]) + 
                len(anomalies["warnings"]) + 
                len(anomalies["data_quality_issues"])
            )
            
            # Generate detection summary
            anomalies["detection_summary"] = self._generate_detection_summary(anomalies)
            
            logger.info(f"Detected {anomalies['total_anomalies']} anomalies in {domain} data")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            return {
                "total_anomalies": 0,
                "anomaly_types": ["detection_error"],
                "critical_alerts": [{"type": "system_error", "message": str(e)}],
                "warnings": [],
                "data_quality_issues": [],
                "detection_summary": {"status": "error", "message": str(e)}
            }
    
    def _detect_sales_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect sales-specific anomalies"""
        anomalies = {
            "anomaly_types": ["sales_anomalies"],
            "critical_alerts": [],
            "warnings": [],
            "data_quality_issues": []
        }
        
        try:
            # Check for Sales column
            if 'Sales' in df.columns:
                sales_data = pd.to_numeric(df['Sales'], errors='coerce').dropna()
                
                if len(sales_data) > 0:
                    # Statistical anomalies
                    z_scores = np.abs(stats.zscore(sales_data))
                    outliers = sales_data[z_scores > self.z_score_threshold]
                    
                    if len(outliers) > 0:
                        anomalies["critical_alerts"].append({
                            "type": "statistical_outlier",
                            "message": f"Found {len(outliers)} extreme sales values",
                            "severity": "high",
                            "affected_records": len(outliers),
                            "outlier_values": outliers.tolist()[:5]  # Show first 5
                        })
                    
                    # Trend anomalies
                    if len(sales_data) > 7:  # Need at least a week of data
                        trend_anomalies = self._detect_trend_anomalies(sales_data)
                        anomalies["warnings"].extend(trend_anomalies)
                    
                    # Seasonal anomalies
                    if 'Date' in df.columns:
                        seasonal_anomalies = self._detect_seasonal_anomalies(df, 'Sales')
                        anomalies["warnings"].extend(seasonal_anomalies)
            
            # Zero or negative sales
            if 'Sales' in df.columns:
                negative_sales = df[df['Sales'] < 0]
                if len(negative_sales) > 0:
                    anomalies["critical_alerts"].append({
                        "type": "negative_sales",
                        "message": f"Found {len(negative_sales)} records with negative sales",
                        "severity": "critical",
                        "affected_records": len(negative_sales)
                    })
                
                zero_sales = df[df['Sales'] == 0]
                if len(zero_sales) > len(df) * 0.1:  # More than 10% zero sales
                    anomalies["warnings"].append({
                        "type": "excessive_zero_sales",
                        "message": f"High percentage ({len(zero_sales)/len(df)*100:.1f}%) of zero sales",
                        "severity": "medium"
                    })
            
        except Exception as e:
            logger.error(f"Error detecting sales anomalies: {str(e)}")
            anomalies["critical_alerts"].append({
                "type": "detection_error",
                "message": f"Sales anomaly detection failed: {str(e)}",
                "severity": "medium"
            })
        
        return anomalies
    
    def _detect_inventory_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect inventory-specific anomalies"""
        anomalies = {
            "anomaly_types": ["inventory_anomalies"],
            "critical_alerts": [],
            "warnings": [],
            "data_quality_issues": []
        }
        
        try:
            # Stock level anomalies
            stock_columns = [col for col in df.columns if 'stock' in col.lower() or 'quantity' in col.lower()]
            
            for col in stock_columns:
                stock_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(stock_data) > 0:
                    # Negative stock
                    negative_stock = stock_data[stock_data < 0]
                    if len(negative_stock) > 0:
                        anomalies["critical_alerts"].append({
                            "type": "negative_stock",
                            "message": f"Found {len(negative_stock)} records with negative stock in {col}",
                            "severity": "critical",
                            "column": col
                        })
                    
                    # Zero stock
                    zero_stock = stock_data[stock_data == 0]
                    if len(zero_stock) > len(stock_data) * 0.2:  # More than 20% zero stock
                        anomalies["warnings"].append({
                            "type": "high_zero_stock",
                            "message": f"High percentage of zero stock in {col}",
                            "severity": "medium",
                            "column": col
                        })
                    
                    # Stock level anomalies using isolation forest
                    if len(stock_data) > 10:
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        stock_reshaped = stock_data.values.reshape(-1, 1)
                        anomaly_labels = iso_forest.fit_predict(stock_reshaped)
                        anomalies_found = stock_data[anomaly_labels == -1]
                        
                        if len(anomalies_found) > 0:
                            anomalies["warnings"].append({
                                "type": "stock_anomaly",
                                "message": f"Found {len(anomalies_found)} unusual stock levels in {col}",
                                "severity": "medium",
                                "column": col,
                                "anomaly_values": anomalies_found.tolist()[:5]
                            })
            
        except Exception as e:
            logger.error(f"Error detecting inventory anomalies: {str(e)}")
            anomalies["critical_alerts"].append({
                "type": "detection_error",
                "message": f"Inventory anomaly detection failed: {str(e)}",
                "severity": "medium"
            })
        
        return anomalies
    
    def _detect_finance_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect finance-specific anomalies"""
        anomalies = {
            "anomaly_types": ["finance_anomalies"],
            "critical_alerts": [],
            "warnings": [],
            "data_quality_issues": []
        }
        
        try:
            # Revenue anomalies
            revenue_columns = [col for col in df.columns if 'revenue' in col.lower() or 'income' in col.lower()]
            
            for col in revenue_columns:
                revenue_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(revenue_data) > 0:
                    # Negative revenue
                    negative_revenue = revenue_data[revenue_data < 0]
                    if len(negative_revenue) > 0:
                        anomalies["critical_alerts"].append({
                            "type": "negative_revenue",
                            "message": f"Found {len(negative_revenue)} records with negative revenue in {col}",
                            "severity": "critical",
                            "column": col
                        })
                    
                    # Revenue volatility
                    if len(revenue_data) > 5:
                        cv = revenue_data.std() / revenue_data.mean() if revenue_data.mean() != 0 else 0
                        if cv > 1.0:  # Coefficient of variation > 1
                            anomalies["warnings"].append({
                                "type": "high_revenue_volatility",
                                "message": f"High revenue volatility detected in {col} (CV: {cv:.2f})",
                                "severity": "medium",
                                "column": col
                            })
            
            # Expense anomalies
            expense_columns = [col for col in df.columns if 'expense' in col.lower() or 'cost' in col.lower()]
            
            for col in expense_columns:
                expense_data = pd.to_numeric(df[col], errors='coerce').dropna()
                
                if len(expense_data) > 0:
                    # Unusually high expenses
                    if len(expense_data) > 5:
                        q99 = expense_data.quantile(0.99)
                        high_expenses = expense_data[expense_data > q99]
                        
                        if len(high_expenses) > 0:
                            anomalies["warnings"].append({
                                "type": "high_expenses",
                                "message": f"Found {len(high_expenses)} unusually high expenses in {col}",
                                "severity": "medium",
                                "column": col
                            })
        
        except Exception as e:
            logger.error(f"Error detecting finance anomalies: {str(e)}")
            anomalies["critical_alerts"].append({
                "type": "detection_error",
                "message": f"Finance anomaly detection failed: {str(e)}",
                "severity": "medium"
            })
        
        return anomalies
    
    def _detect_customer_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect customer-specific anomalies"""
        anomalies = {
            "anomaly_types": ["customer_anomalies"],
            "critical_alerts": [],
            "warnings": [],
            "data_quality_issues": []
        }
        
        try:
            # Customer behavior anomalies
            if 'Customer' in df.columns:
                customer_counts = df['Customer'].value_counts()
                
                # Customers with unusually high activity
                if len(customer_counts) > 0:
                    mean_activity = customer_counts.mean()
                    std_activity = customer_counts.std()
                    threshold = mean_activity + 2 * std_activity
                    
                    high_activity_customers = customer_counts[customer_counts > threshold]
                    if len(high_activity_customers) > 0:
                        anomalies["warnings"].append({
                            "type": "high_activity_customers",
                            "message": f"Found {len(high_activity_customers)} customers with unusually high activity",
                            "severity": "low",
                            "customers": high_activity_customers.head().to_dict()
                        })
            
            # Churn indicators
            if 'Date' in df.columns and 'Customer' in df.columns:
                churn_anomalies = self._detect_churn_anomalies(df)
                anomalies["warnings"].extend(churn_anomalies)
        
        except Exception as e:
            logger.error(f"Error detecting customer anomalies: {str(e)}")
            anomalies["critical_alerts"].append({
                "type": "detection_error",
                "message": f"Customer anomaly detection failed: {str(e)}",
                "severity": "medium"
            })
        
        return anomalies
    
    def _detect_general_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect general data anomalies"""
        anomalies = {
            "anomaly_types": ["general_anomalies"],
            "critical_alerts": [],
            "warnings": [],
            "data_quality_issues": []
        }
        
        try:
            # Missing data anomalies
            missing_data = df.isnull().sum()
            high_missing = missing_data[missing_data > len(df) * 0.5]  # More than 50% missing
            
            if len(high_missing) > 0:
                anomalies["data_quality_issues"].append({
                    "type": "high_missing_data",
                    "message": f"Columns with >50% missing data: {list(high_missing.index)}",
                    "severity": "high",
                    "columns": list(high_missing.index)
                })
            
            # Duplicate records
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                anomalies["data_quality_issues"].append({
                    "type": "duplicate_records",
                    "message": f"Found {duplicates} duplicate records",
                    "severity": "medium",
                    "count": duplicates
                })
            
            # Data type anomalies
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Check for mixed data types
                    numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                    if numeric_count > 0 and numeric_count < len(df[col]):
                        anomalies["data_quality_issues"].append({
                            "type": "mixed_data_types",
                            "message": f"Column '{col}' has mixed data types",
                            "severity": "low",
                            "column": col
                        })
        
        except Exception as e:
            logger.error(f"Error detecting general anomalies: {str(e)}")
            anomalies["critical_alerts"].append({
                "type": "detection_error",
                "message": f"General anomaly detection failed: {str(e)}",
                "severity": "medium"
            })
        
        return anomalies
    
    def _detect_trend_anomalies(self, data: pd.Series) -> List[Dict[str, Any]]:
        """Detect trend anomalies in time series data"""
        anomalies = []
        
        try:
            if len(data) < 7:
                return anomalies
            
            # Calculate rolling mean and detect sudden changes
            window = min(7, len(data) // 2)
            rolling_mean = data.rolling(window=window).mean()
            
            # Detect sudden drops or spikes
            pct_change = rolling_mean.pct_change()
            sudden_changes = pct_change[abs(pct_change) > 0.5]  # 50% change threshold
            
            if len(sudden_changes) > 0:
                anomalies.append({
                    "type": "sudden_trend_change",
                    "message": f"Detected {len(sudden_changes)} sudden trend changes",
                    "severity": "medium",
                    "changes": sudden_changes.tolist()
                })
        
        except Exception as e:
            logger.error(f"Error detecting trend anomalies: {str(e)}")
        
        return anomalies
    
    def _detect_seasonal_anomalies(self, df: pd.DataFrame, value_column: str) -> List[Dict[str, Any]]:
        """Detect seasonal anomalies"""
        anomalies = []
        
        try:
            if 'Date' not in df.columns:
                return anomalies
            
            # Convert date column
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df_with_date = df.dropna(subset=['Date'])
            
            if len(df_with_date) < 30:  # Need at least 30 days
                return anomalies
            
            # Group by day of week and detect anomalies
            df_with_date['day_of_week'] = df_with_date['Date'].dt.dayofweek
            daily_avg = df_with_date.groupby('day_of_week')[value_column].mean()
            
            # Detect unusual day-of-week patterns
            overall_avg = df_with_date[value_column].mean()
            unusual_days = daily_avg[abs(daily_avg - overall_avg) > overall_avg * 0.3]
            
            if len(unusual_days) > 0:
                anomalies.append({
                    "type": "seasonal_anomaly",
                    "message": f"Unusual day-of-week patterns detected",
                    "severity": "low",
                    "unusual_days": unusual_days.to_dict()
                })
        
        except Exception as e:
            logger.error(f"Error detecting seasonal anomalies: {str(e)}")
        
        return anomalies
    
    def _detect_churn_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect customer churn anomalies"""
        anomalies = []
        
        try:
            if 'Customer' not in df.columns or 'Date' not in df.columns:
                return anomalies
            
            # Convert date column
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df_with_date = df.dropna(subset=['Date'])
            
            if len(df_with_date) < 30:
                return anomalies
            
            # Find customers who haven't been active recently
            latest_date = df_with_date['Date'].max()
            cutoff_date = latest_date - timedelta(days=30)
            
            recent_customers = df_with_date[df_with_date['Date'] > cutoff_date]['Customer'].unique()
            all_customers = df_with_date['Customer'].unique()
            
            churned_customers = set(all_customers) - set(recent_customers)
            
            if len(churned_customers) > 0:
                churn_rate = len(churned_customers) / len(all_customers)
                if churn_rate > 0.2:  # More than 20% churn
                    anomalies.append({
                        "type": "high_churn_rate",
                        "message": f"High customer churn rate: {churn_rate:.1%}",
                        "severity": "high",
                        "churn_rate": churn_rate,
                        "churned_customers": len(churned_customers)
                    })
        
        except Exception as e:
            logger.error(f"Error detecting churn anomalies: {str(e)}")
        
        return anomalies
    
    def _generate_detection_summary(self, anomalies: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of anomaly detection results"""
        try:
            total_anomalies = anomalies["total_anomalies"]
            critical_count = len(anomalies["critical_alerts"])
            warning_count = len(anomalies["warnings"])
            quality_count = len(anomalies["data_quality_issues"])
            
            if total_anomalies == 0:
                status = "clean"
                message = "No anomalies detected. Data appears to be in good condition."
            elif critical_count > 0:
                status = "critical"
                message = f"Critical issues detected: {critical_count} alerts require immediate attention."
            elif warning_count > 0:
                status = "warning"
                message = f"Warning conditions detected: {warning_count} items need review."
            else:
                status = "info"
                message = f"Data quality issues detected: {quality_count} items to address."
            
            return {
                "status": status,
                "message": message,
                "total_anomalies": total_anomalies,
                "critical_alerts": critical_count,
                "warnings": warning_count,
                "data_quality_issues": quality_count,
                "recommendations": self._generate_recommendations(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Error generating detection summary: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating summary: {str(e)}",
                "total_anomalies": 0
            }
    
    def _generate_recommendations(self, anomalies: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on detected anomalies"""
        recommendations = []
        
        try:
            # Critical alerts recommendations
            if anomalies["critical_alerts"]:
                recommendations.append("🚨 Address critical alerts immediately - these may indicate data errors or serious business issues")
            
            # Warning recommendations
            if anomalies["warnings"]:
                recommendations.append("⚠️ Review warning conditions - investigate unusual patterns or trends")
            
            # Data quality recommendations
            if anomalies["data_quality_issues"]:
                recommendations.append("🔧 Improve data quality - address missing data, duplicates, and data type issues")
            
            # General recommendations
            if anomalies["total_anomalies"] > 0:
                recommendations.append("📊 Consider implementing automated monitoring for these anomaly types")
                recommendations.append("👥 Consult with data analysts or business experts for complex anomalies")
            else:
                recommendations.append("✅ Data appears clean - continue regular monitoring")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            recommendations.append("❌ Error generating recommendations")
        
        return recommendations
