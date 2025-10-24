"""
TANAW Semantic Detector
-----------------------
Uses OpenAI to intelligently detect business context (Sales vs Inventory)
by analyzing sample data and column relationships.

This solves the "quantity ambiguity" problem where the same column name
can mean different things in different contexts:
- Sales context: quantity = items sold
- Inventory context: quantity = stock on hand
"""

import pandas as pd
from openai import OpenAI
import json
from typing import Dict, Any, Optional
import os


class TANAWSemanticDetector:
    """
    Intelligent context detection for business datasets
    
    Uses OpenAI GPT-4o-mini to analyze dataset samples and determine
    whether data represents Sales transactions or Inventory levels.
    Includes rule-based fallback for robustness.
    """
    
    def __init__(self, openai_api_key: str = None):
        """
        Initialize semantic detector
        
        Args:
            openai_api_key: OpenAI API key (optional, can use env var)
        """
        # Get API key from parameter or environment
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            print("⚠️ No OpenAI API key found, will use rule-based detection only")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                print("✅ OpenAI client initialized for semantic detection")
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}")
                self.client = None
        
        # Fallback detection keywords
        self.sales_keywords = [
            # Transaction-related
            'transaction', 'sale', 'order', 'invoice', 'receipt', 'purchase',
            # Money-related
            'price', 'amount', 'revenue', 'payment', 'total', 'subtotal', 'discount',
            # Customer-related
            'customer', 'buyer', 'client', 'patron', 'guest',
            # Sales-specific
            'sold', 'promo', 'campaign', 'cashier', 'pos'
        ]
        
        self.inventory_keywords = [
            # Stock-related
            'stock', 'inventory', 'warehouse', 'storage', 'on_hand', 'available',
            # Reorder-related
            'reorder', 'min_stock', 'max_stock', 'threshold', 'safety_stock',
            # Supply chain
            'supplier', 'shipment', 'delivery', 'receiving', 'vendor',
            # Inventory-specific
            'turnover', 'sku', 'bin', 'location', 'shelf', 'aisle'
        ]
    
    def detect_context(self, df: pd.DataFrame, column_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Detect business context using OpenAI + rule-based fallback
        
        Args:
            df: DataFrame to analyze
            column_mapping: Optional mapping from original to canonical column names
            
        Returns:
            {
                "context": "SALES" | "INVENTORY" | "MIXED" | "UNKNOWN",
                "confidence": 0.0 to 1.0,
                "method": "openai" | "rules" | "default",
                "reasoning": "explanation"
            }
        """
        print("\n" + "="*80)
        print("🧠 SEMANTIC CONTEXT DETECTION")
        print("="*80)
        
        # TIER 1: Try OpenAI Detection (Most Accurate)
        if self.client:
            try:
                print("🤖 Attempting OpenAI-powered detection...")
                result = self._openai_detect(df, column_mapping)
                
                if result["confidence"] >= 0.7:
                    print(f"✅ OpenAI detection successful!")
                    print(f"   Context: {result['context']}")
                    print(f"   Confidence: {result['confidence']:.2%}")
                    print(f"   Reasoning: {result['reasoning']}")
                    return result
                else:
                    print(f"⚠️ OpenAI confidence too low ({result['confidence']:.2%}), trying fallback...")
                    
            except Exception as e:
                print(f"❌ OpenAI detection failed: {e}")
                print("   Falling back to rule-based detection...")
        
        # TIER 2: Rule-Based Detection (Fallback)
        print("📋 Using rule-based detection...")
        result = self._rule_based_detect(df, column_mapping)
        
        if result["context"] != "UNKNOWN":
            print(f"✅ Rule-based detection successful!")
            print(f"   Context: {result['context']}")
            print(f"   Reasoning: {result['reasoning']}")
            return result
        
        # TIER 3: Default (Unable to determine)
        print("⚠️ Unable to determine context clearly")
        print("   Will generate all possible charts")
        return {
            "context": "UNKNOWN",
            "confidence": 0.0,
            "method": "default",
            "reasoning": "Could not determine business context from column names or data patterns"
        }
    
    def _openai_detect(self, df: pd.DataFrame, column_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Use OpenAI to detect context by analyzing sample data
        
        Args:
            df: DataFrame to analyze
            column_mapping: Original to canonical column mapping
            
        Returns:
            Detection result dictionary
        """
        # Extract sample data (5-10 rows)
        sample_size = min(10, len(df))
        sample_df = df.sample(n=sample_size, random_state=42) if len(df) > sample_size else df.copy()
        
        # Convert sample to readable format
        sample_data = sample_df.head(5).to_dict('records')
        columns = list(df.columns)
        
        # Get original column names if available
        original_columns = list(column_mapping.keys()) if column_mapping else columns
        
        # Build detection prompt
        prompt = self._build_detection_prompt(columns, original_columns, sample_data)
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert data analyst specializing in business intelligence and dataset classification."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        result = json.loads(response_text)
        
        # Add metadata
        result["method"] = "openai"
        result["confidence"] = float(result.get("confidence", 0.0))
        
        return result
    
    def _build_detection_prompt(self, columns: list, original_columns: list, sample_data: list) -> str:
        """
        Build OpenAI prompt for context detection
        
        Args:
            columns: Current column names (after mapping)
            original_columns: Original column names (before mapping)
            sample_data: Sample rows from dataset
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
Analyze this dataset and determine its business context.

**ORIGINAL COLUMN NAMES:**
{', '.join(original_columns)}

**CURRENT COLUMN NAMES (after mapping):**
{', '.join(columns)}

**SAMPLE DATA (first 5 rows):**
{json.dumps(sample_data, indent=2, default=str)}

**CONTEXT DEFINITIONS:**

1. **SALES** - Transaction-level data about items sold to customers
   - Indicators: transaction_id, order_id, sale_date, customer, price, payment, receipt
   - "quantity" means: items sold in this transaction
   - Example: Restaurant sales, retail transactions, e-commerce orders

2. **INVENTORY** - Stock-level data about items available in warehouse/storage
   - Indicators: stock_level, warehouse, reorder_point, supplier, on_hand, available
   - "quantity" means: current stock on hand
   - Example: Warehouse inventory, stock management, supply chain data

3. **MIXED** - Contains both sales AND inventory columns
   - Has both transaction data and stock levels
   - Example: Integrated business system export

**TASK:**
Determine if this dataset represents SALES, INVENTORY, or MIXED context.

**RESPOND IN JSON FORMAT:**
{{
  "context": "SALES" | "INVENTORY" | "MIXED",
  "confidence": 0.0 to 1.0,
  "reasoning": "Brief explanation of why you classified it this way (1-2 sentences)"
}}

**IMPORTANT:**
- Look at the ORIGINAL column names - they contain the real business meaning
- Consider the data values and their relationships
- If you see transaction-related columns (order_id, transaction_amount, customer), it's likely SALES
- If you see stock-related columns (stock_level, warehouse, reorder_point), it's likely INVENTORY
- If "quantity" appears with "transaction" or "sale", it means items sold (SALES)
- If "quantity" appears with "stock" or "warehouse", it means stock on hand (INVENTORY)
"""
        return prompt
    
    def _rule_based_detect(self, df: pd.DataFrame, column_mapping: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Rule-based context detection using keyword matching
        
        Args:
            df: DataFrame to analyze
            column_mapping: Original to canonical column mapping
            
        Returns:
            Detection result dictionary
        """
        # Get all column names (original + current)
        all_columns = set()
        
        if column_mapping:
            all_columns.update(str(col).lower() for col in column_mapping.keys())
        
        all_columns.update(str(col).lower() for col in df.columns)
        
        # Join all column names into single string for matching
        columns_text = ' '.join(all_columns)
        
        # Count keyword matches
        sales_score = sum(1 for keyword in self.sales_keywords if keyword in columns_text)
        inventory_score = sum(1 for keyword in self.inventory_keywords if keyword in columns_text)
        
        print(f"   Sales indicators: {sales_score}")
        print(f"   Inventory indicators: {inventory_score}")
        
        # Determine context based on scores
        if sales_score > inventory_score and sales_score >= 2:
            return {
                "context": "SALES",
                "confidence": min(0.9, 0.5 + (sales_score * 0.1)),
                "method": "rules",
                "reasoning": f"Found {sales_score} sales-related keywords in column names (e.g., transaction, price, customer)"
            }
        elif inventory_score > sales_score and inventory_score >= 2:
            return {
                "context": "INVENTORY",
                "confidence": min(0.9, 0.5 + (inventory_score * 0.1)),
                "method": "rules",
                "reasoning": f"Found {inventory_score} inventory-related keywords in column names (e.g., stock, warehouse, reorder)"
            }
        elif sales_score >= 2 and inventory_score >= 2:
            return {
                "context": "MIXED",
                "confidence": 0.7,
                "method": "rules",
                "reasoning": f"Found both sales ({sales_score}) and inventory ({inventory_score}) indicators"
            }
        else:
            return {
                "context": "UNKNOWN",
                "confidence": 0.0,
                "method": "rules",
                "reasoning": "Insufficient keyword matches to determine context"
            }


# Standalone test function
def test_semantic_detector():
    """Test the semantic detector with sample data"""
    print("\n🧪 Testing TANAW Semantic Detector\n")
    
    # Create sample sales data (like Balaji)
    sales_data = pd.DataFrame({
        'order_id': [1, 2, 3, 4, 5],
        'date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
        'item_name': ['Burger', 'Pizza', 'Burger', 'Salad', 'Pizza'],
        'quantity': [2, 1, 3, 1, 2],
        'price': [10, 15, 10, 8, 15],
        'transaction_amount': [20, 15, 30, 8, 30]
    })
    
    # Create sample inventory data
    inventory_data = pd.DataFrame({
        'product': ['Widget A', 'Widget B', 'Widget C'],
        'stock_level': [100, 50, 75],
        'reorder_point': [20, 15, 25],
        'warehouse': ['WH1', 'WH1', 'WH2']
    })
    
    # Test detector
    detector = TANAWSemanticDetector()
    
    print("=" * 80)
    print("TEST 1: Sales Dataset (Balaji-style)")
    print("=" * 80)
    result1 = detector.detect_context(sales_data)
    print(f"\nResult: {json.dumps(result1, indent=2)}\n")
    
    print("=" * 80)
    print("TEST 2: Inventory Dataset")
    print("=" * 80)
    result2 = detector.detect_context(inventory_data)
    print(f"\nResult: {json.dumps(result2, indent=2)}\n")


if __name__ == "__main__":
    test_semantic_detector()

