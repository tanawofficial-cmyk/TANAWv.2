"""
TANAW Domain Detection System
Automatically classifies datasets into business domains for appropriate analytics.
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class DomainClassification:
    domain: str
    confidence: float
    indicators: List[str]
    suggested_analytics: List[str]

class TANAWDomainDetector:
    """
    Intelligent domain detection system for TANAW.
    Classifies datasets into: Sales, Inventory, Finance, Customer domains.
    """
    
    def __init__(self):
        self.domain_patterns = self._initialize_domain_patterns()
        self.analytics_registry = self._initialize_analytics_registry()
    
    def _initialize_domain_patterns(self) -> Dict[str, Dict]:
        """Initialize domain-specific column patterns and keywords."""
        return {
            'sales': {
                'primary_indicators': [
                    'sales', 'revenue', 'amount', 'price', 'cost', 'profit', 'margin',
                    'transaction', 'order', 'purchase', 'payment', 'total', 'subtotal'
                ],
                'secondary_indicators': [
                    'product', 'item', 'sku', 'category', 'region', 'territory',
                    'customer', 'client', 'date', 'time', 'period', 'quarter'
                ],
                'column_patterns': [
                    r'sales', r'revenue', r'amount', r'price', r'cost', r'profit',
                    r'transaction', r'order', r'purchase', r'payment'
                ]
            },
            'inventory': {
                'primary_indicators': [
                    'stock', 'inventory', 'quantity', 'units', 'warehouse', 'location',
                    'supplier', 'vendor', 'reorder', 'threshold', 'minimum', 'maximum'
                ],
                'secondary_indicators': [
                    'product', 'item', 'sku', 'category', 'date', 'time',
                    'location', 'warehouse', 'shelf', 'bin'
                ],
                'column_patterns': [
                    r'stock', r'inventory', r'quantity', r'units', r'warehouse',
                    r'supplier', r'reorder', r'threshold'
                ]
            },
            'customer': {
                'primary_indicators': [
                    'customer', 'client', 'user', 'member', 'segment', 'demographic',
                    'lifetime', 'value', 'churn', 'retention', 'satisfaction'
                ],
                'secondary_indicators': [
                    'name', 'email', 'phone', 'address', 'age', 'gender',
                    'date', 'time', 'activity', 'engagement'
                ],
                'column_patterns': [
                    r'customer', r'client', r'user', r'member', r'segment',
                    r'lifetime', r'value', r'churn', r'retention'
                ]
            }
        }
    
    def _initialize_analytics_registry(self) -> Dict[str, List[str]]:
        """Initialize analytics registry for each domain."""
        return {
            'sales': [
                'Sales Summary Report',
                'Product Performance Analysis', 
                'Regional Sales Analysis',
                'Sales Forecasting',
                'Demand Forecasting',
                # Financial analytics (when Expense column is available)
                'Revenue and Expense Trend',
                'Profit Margin Analysis',
                'Cash Flow Forecast'
            ],
            'inventory': [
                'Stock Level Analysis',
                'Inventory Turnover Report',
                'Reorder Point Analysis',
                'Location-based Inventory',
                'Supplier Performance Analysis'
            ],
            'customer': [
                'Customer Segmentation Analysis',
                'Customer Purchase Frequency',
                'Customer Lifetime Value',
                'Churn Analysis',
                'Customer Satisfaction Trends'
            ],
            'mixed': [
                # Mixed domain gets analytics from all detected domains
                # This will be populated dynamically in detect_domain()
            ]
        }
    
    def detect_domain(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> DomainClassification:
        """
        Detect the business domain of a dataset.
        
        Args:
            df: The dataset DataFrame
            column_mapping: Mapping of original columns to canonical types
            
        Returns:
            DomainClassification with domain, confidence, and suggested analytics
        """
        print(f"🔍 TANAW Domain Detection: Analyzing {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Get column names (both original and mapped)
        original_columns = [str(col).lower() for col in df.columns]
        mapped_columns = list(column_mapping.keys())
        
        # Calculate domain scores
        domain_scores = {}
        domain_indicators = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0
            indicators = []
            
            # Check primary indicators (higher weight)
            for indicator in patterns['primary_indicators']:
                for col in original_columns + mapped_columns:
                    if indicator in col.lower():
                        score += 3
                        indicators.append(f"Primary: {indicator} in {col}")
            
            # Check secondary indicators (lower weight)
            for indicator in patterns['secondary_indicators']:
                for col in original_columns + mapped_columns:
                    if indicator in col.lower():
                        score += 1
                        indicators.append(f"Secondary: {indicator} in {col}")
            
            # Check column patterns
            for pattern in patterns['column_patterns']:
                for col in original_columns + mapped_columns:
                    if re.search(pattern, col.lower()):
                        score += 2
                        indicators.append(f"Pattern: {pattern} matches {col}")
            
            domain_scores[domain] = score
            domain_indicators[domain] = indicators
        
        # ==================== EXCLUSIVE DOMAIN BONUSES ====================
        # Add bonuses for domain-exclusive indicator combinations
        
        # 📊 SALES Exclusive Bonuses (including financial data)
        has_revenue = any('revenue' in col or 'income' in col for col in original_columns)
        has_expense = any('expense' in col or 'expenditure' in col for col in original_columns)
        has_payment_method = any('payment' in col and 'method' in col for col in original_columns)
        has_customer_name = any(('customer' in col or 'buyer' in col) and 'name' in col for col in original_columns)
        has_quantity_sold = any('quantity' in col and ('sold' in col or 'sale' in col) for col in original_columns)
        has_invoice = any('invoice' in col or 'order_id' in col for col in original_columns)
        
        if has_payment_method or has_invoice:
            domain_scores['sales'] += 10
            domain_indicators['sales'].append("🎯 BONUS +10: Has Payment_Method or Invoice")
            print("   📊 Sales Exclusive Bonus +10: Payment_Method or Invoice")
        
        if has_quantity_sold:
            domain_scores['sales'] += 5
            domain_indicators['sales'].append("🎯 BONUS +5: Has Quantity_Sold")
            print("   📊 Sales Exclusive Bonus +5: Quantity_Sold column")
        
        # 📦 INVENTORY Exclusive Bonuses
        has_reorder = any('reorder' in col for col in original_columns)
        has_warehouse = any('warehouse' in col or 'storage' in col for col in original_columns)
        has_supplier = any('supplier' in col or 'vendor' in col for col in original_columns)
        
        if has_reorder:
            domain_scores['inventory'] += 10
            domain_indicators['inventory'].append("🎯 BONUS +10: Has Reorder_Level")
            print("   📦 Inventory Exclusive Bonus +10: Reorder column")
        
        if has_warehouse and has_supplier:
            domain_scores['inventory'] += 10
            domain_indicators['inventory'].append("🎯 BONUS +10: Has Warehouse AND Supplier")
            print("   📦 Inventory Exclusive Bonus +10: Warehouse + Supplier combination")
        
        # 👥 CUSTOMER Exclusive Bonuses
        has_customer_segment = any('segment' in col or 'tier' in col for col in original_columns)
        has_lifetime_value = any('lifetime' in col or 'ltv' in col for col in original_columns)
        has_churn = any('churn' in col or 'retention' in col for col in original_columns)
        
        if has_customer_segment:
            domain_scores['customer'] += 10
            domain_indicators['customer'].append("🎯 BONUS +10: Has Customer_Segment")
            print("   👥 Customer Exclusive Bonus +10: Customer_Segment column")
        
        if has_lifetime_value or has_churn:
            domain_scores['customer'] += 10
            domain_indicators['customer'].append("🎯 BONUS +10: Has LTV or Churn metrics")
            print("   👥 Customer Exclusive Bonus +10: LTV/Churn column")
        
        print(f"\n📊 Final Domain Scores (after bonuses):")
        for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"   {domain.upper()}: {score} points")
        # ==================== END EXCLUSIVE BONUSES ====================
        
        # Find the domain with highest score
        if not domain_scores or max(domain_scores.values()) == 0:
            # Default to sales if no clear indicators
            detected_domain = 'sales'
            confidence = 0.3
            indicators = ['Default fallback to sales domain']
        else:
            # Get top 2 domain scores
            sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
            top_domain = sorted_domains[0]
            second_domain = sorted_domains[1] if len(sorted_domains) > 1 else None
            
            detected_domain = top_domain[0]
            max_score = top_domain[1]
            
            # Check for MIXED domain (if multiple domains have significant scores)
            if second_domain and second_domain[1] > 0:
                # Calculate score ratio
                score_ratio = second_domain[1] / max_score if max_score > 0 else 0
                
                # If second domain has >= 60% of top domain score, consider it MIXED
                if score_ratio >= 0.6:
                    detected_domain = 'mixed'
                    confidence = min((max_score + second_domain[1]) / (len(original_columns) * 10), 0.95)
                    indicators = [
                        f"Primary domain: {top_domain[0]} (score: {max_score})",
                        f"Secondary domain: {second_domain[0]} (score: {second_domain[1]})",
                        "Dataset contains characteristics of multiple domains"
                    ]
                    # Combine analytics from both domains
                    suggested_analytics = (
                        self.analytics_registry.get(top_domain[0], []) +
                        self.analytics_registry.get(second_domain[0], [])
                    )
                    
                    print(f"🎯 Detected MIXED Domain: {top_domain[0].upper()} + {second_domain[0].upper()}")
                    print(f"   Primary: {top_domain[0]} (score: {max_score})")
                    print(f"   Secondary: {second_domain[0]} (score: {second_domain[1]})")
                    print(f"   Score ratio: {score_ratio:.2%}")
                else:
                    # Single domain
                    total_possible = len(original_columns) * 5
                    confidence = min(max_score / total_possible, 1.0)
                    indicators = domain_indicators[detected_domain]
                    suggested_analytics = self.analytics_registry.get(detected_domain, [])
            else:
                # Single domain
                total_possible = len(original_columns) * 5
                confidence = min(max_score / total_possible, 1.0)
                indicators = domain_indicators[detected_domain]
                suggested_analytics = self.analytics_registry.get(detected_domain, [])
        
        print(f"🎯 Detected Domain: {detected_domain.upper()} (confidence: {confidence:.2f})")
        print(f"📊 Suggested Analytics: {len(suggested_analytics)} available")
        
        return DomainClassification(
            domain=detected_domain,
            confidence=confidence,
            indicators=indicators,
            suggested_analytics=suggested_analytics
        )
    
    def get_domain_analytics(self, domain: str) -> List[str]:
        """Get available analytics for a specific domain."""
        return self.analytics_registry.get(domain, [])
    
    def get_all_domains(self) -> List[str]:
        """Get all supported domains."""
        return list(self.analytics_registry.keys())
    
    # ==================== DOMAIN-SPECIFIC VALIDATORS ====================
    
    def has_finance_indicators(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> bool:
        """
        Check if dataset has sufficient finance-related data for meaningful finance charts.
        
        Returns True if dataset contains ANY of:
        - Direct Revenue/Income column
        - Direct Expense/Cost column  
        - Budget-related columns
        - Price + Volume columns (to calculate revenue)
        - Account/Ledger columns
        
        Args:
            df: Dataset DataFrame
            column_mapping: Column mapping dictionary
            
        Returns:
            True if finance charts would be meaningful
        """
        finance_score = 0
        
        # Check for direct finance columns
        finance_columns = ['revenue', 'income', 'expense', 'expenses', 'cost', 'costs',
                          'budget', 'budgeted', 'cash', 'flow', 'balance', 'account',
                          'ledger', 'debit', 'credit', 'asset', 'liability', 'profit']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(fin_col in col_lower for fin_col in finance_columns):
                finance_score += 3
                print(f"   💰 Finance indicator found: {col}")
        
        # Check canonical mappings
        for orig_col, canon_col in column_mapping.items():
            canon_lower = str(canon_col).lower()
            if any(fin_col in canon_lower for fin_col in finance_columns):
                finance_score += 2
                print(f"   💰 Finance indicator in mapping: {orig_col} → {canon_col}")
        
        # Check if we can CALCULATE revenue (Price × Volume)
        has_price = self._has_column_pattern(df, column_mapping, ['price', 'unit_price', 'cost', 'rate', 'amount'])
        has_volume = self._has_column_pattern(df, column_mapping, ['sales_volume', 'quantity', 'volume', 'qty', 'units'])
        
        if has_price and has_volume:
            finance_score += 1  # Lower score - can calculate but not pure finance data
            print(f"   💰 Can calculate revenue from Price × Volume")
        
        # Threshold: Need score >= 3 for meaningful finance charts
        # (Direct finance column OR calculable revenue + something else)
        has_finance = finance_score >= 3
        print(f"   💰 Finance score: {finance_score} → {'✅ Sufficient' if has_finance else '❌ Insufficient'}")
        
        return has_finance
    
    def has_inventory_indicators(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> bool:
        """
        Check if dataset has inventory-related data for meaningful inventory charts.
        
        Returns True if dataset contains ANY of:
        - Stock/Quantity column
        - Reorder level column
        - Warehouse/Location column
        - Supplier/Vendor column
        
        Args:
            df: Dataset DataFrame
            column_mapping: Column mapping dictionary
            
        Returns:
            True if inventory charts would be meaningful
        """
        inventory_score = 0
        
        # Check for inventory-specific columns
        inventory_columns = ['stock', 'inventory', 'warehouse', 'location', 'supplier',
                           'vendor', 'reorder', 'threshold', 'minimum', 'maximum',
                           'bin', 'shelf', 'aisle']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(inv_col in col_lower for inv_col in inventory_columns):
                inventory_score += 3
                print(f"   📦 Inventory indicator found: {col}")
        
        # Check canonical mappings
        for orig_col, canon_col in column_mapping.items():
            canon_lower = str(canon_col).lower()
            if any(inv_col in canon_lower for inv_col in inventory_columns):
                inventory_score += 2
                print(f"   📦 Inventory indicator in mapping: {orig_col} → {canon_col}")
        
        # Quantity alone is not enough - need at least one inventory-specific indicator
        has_quantity = self._has_column_pattern(df, column_mapping, ['quantity', 'stock', 'units'])
        has_inventory_specific = inventory_score >= 3
        
        has_inventory = has_quantity and has_inventory_specific
        print(f"   📦 Inventory score: {inventory_score} → {'✅ Sufficient' if has_inventory else '❌ Insufficient'}")
        
        return has_inventory
    
    def has_customer_indicators(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> bool:
        """
        Check if dataset has customer-related data for meaningful customer charts.
        
        Returns True if dataset contains:
        - Customer/Client column
        - Customer type/segment column
        - Customer demographic data
        
        Args:
            df: Dataset DataFrame
            column_mapping: Column mapping dictionary
            
        Returns:
            True if customer charts would be meaningful
        """
        customer_score = 0
        
        # Check for customer-specific columns
        customer_columns = ['customer', 'client', 'user', 'member', 'buyer', 'shopper',
                          'segment', 'demographic', 'lifetime', 'ltv', 'churn',
                          'retention', 'satisfaction', 'feedback', 'rating']
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(cust_col in col_lower for cust_col in customer_columns):
                customer_score += 3
                print(f"   👥 Customer indicator found: {col}")
        
        # Check canonical mappings
        for orig_col, canon_col in column_mapping.items():
            canon_lower = str(canon_col).lower()
            if any(cust_col in canon_lower for cust_col in customer_columns):
                customer_score += 2
                print(f"   👥 Customer indicator in mapping: {orig_col} → {canon_col}")
        
        # Threshold: Need score >= 3 for meaningful customer charts
        has_customer = customer_score >= 3
        print(f"   👥 Customer score: {customer_score} → {'✅ Sufficient' if has_customer else '❌ Insufficient'}")
        
        return has_customer
    
    def _has_column_pattern(self, df: pd.DataFrame, column_mapping: Dict[str, str], patterns: List[str]) -> bool:
        """
        Helper method to check if any column matches the given patterns.
        
        Args:
            df: Dataset DataFrame
            column_mapping: Column mapping dictionary
            patterns: List of patterns to search for
            
        Returns:
            True if any column matches any pattern
        """
        # Check DataFrame columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(pattern.lower() in col_lower for pattern in patterns):
                return True
        
        # Check canonical mappings
        for orig_col, canon_col in column_mapping.items():
            canon_lower = str(canon_col).lower()
            if any(pattern.lower() in canon_lower for pattern in patterns):
                return True
        
        return False