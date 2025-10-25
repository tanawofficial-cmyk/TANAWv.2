"""
GPT-Based Column Mapper for TANAW Retail Analytics
Optimized for retail datasets with cost-effective OpenAI integration.

Features:
- Retail-specific column mapping
- Cost optimization through minimal token usage
- Caching system to reduce API calls
- Fallback to local rules when needed
"""

import openai
import json
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib
import re

@dataclass
class ColumnMapping:
    """Represents a column mapping result."""
    original_column: str
    mapped_to: str
    confidence: float
    reasoning: str
    source: str = "gpt"  # "gpt", "cache", "fallback"

@dataclass
class MappingResult:
    """Complete mapping result for a dataset."""
    mappings: List[ColumnMapping]
    total_cost: float
    cache_hits: int
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class GPTColumnMapper:
    """
    OpenAI-powered column mapper optimized for multi-domain business analytics.
    
    Supports 4 business domains with 5 canonical types:
    - SALES: Product Performance, Regional Sales, Sales Trends
    - FINANCE: Expense Distribution, Profit Margins, Cash Flow
    - INVENTORY: Stock Levels, Reorder Points, Turnover
    - CUSTOMER: Segmentation, Lifetime Value, Churn
    
    Canonical Types (domain-agnostic semantic mapping):
    1. Date: Any temporal column across all domains
    2. Sales: Any numeric value (Sales, Expense, Balance, Stock_Value, etc.)
    3. Product: Any entity identifier (Product, Account, Item, Customer, etc.)
    4. Region: Any grouping (Region, Department, Warehouse, Segment, etc.)
    5. Quantity: Any count/volume (Qty_Sold, Stock_Level, Transaction_Count, etc.)
    """
    
    def __init__(self, api_key: str, db_path: str = "tanaw_mapping_cache.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=api_key)
        
        # TANAW's canonical types for multi-domain analytics
        self.canonical_types = [
            'Date',      # Time series data
            'Sales',     # Monetary values (general)
            'Product',   # Product/Entity identifiers
            'Region',    # Geographic/Department grouping
            'Quantity',  # Volume metrics
            'Revenue',   # Income/Revenue (Finance-specific)
            'Expense',   # Costs/Expenses (Finance-specific)
            'Customer',  # Customer identifiers
            'Price'      # Unit pricing
        ]
        
        # Initialize cache database
        self._init_cache_db()
        
        # Cost tracking
        self.total_cost = 0.0
        self.cache_hits = 0
        
    def _init_cache_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS column_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_hash TEXT UNIQUE,
                original_column TEXT,
                mapped_to TEXT,
                confidence REAL,
                reasoning TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def map_columns(self, columns: List[str], dataset_context: str = "retail") -> MappingResult:
        """
        Map dataset columns to TANAW canonical types using GPT.
        
        Args:
            columns: List of column names from the dataset
            dataset_context: Context about the dataset (default: "retail")
            
        Returns:
            MappingResult with all mappings and metadata
        """
        start_time = datetime.now()
        
        try:
            # Ensure all columns are strings
            columns = [str(col) for col in columns]
            
            # Step 1: Check cache first
            cached_mappings = self._check_cache(columns)
            cached_column_names = {m.original_column for m in cached_mappings}
            uncached_columns = [col for col in columns if col not in cached_column_names]
            
            # Step 2: Get GPT mappings for uncached columns
            gpt_mappings = []
            if uncached_columns:
                gpt_mappings = self._get_gpt_mappings(uncached_columns, dataset_context)
                
                # Store in cache
                self._store_in_cache(gpt_mappings)
            
            # Step 3: Combine results
            all_mappings = cached_mappings + gpt_mappings
            
            # Step 4: Validate and clean mappings
            validated_mappings = self._validate_mappings(all_mappings, columns)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MappingResult(
                mappings=validated_mappings,
                total_cost=self.total_cost,
                cache_hits=len(cached_mappings),
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            return MappingResult(
                mappings=[],
                total_cost=self.total_cost,
                cache_hits=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                success=False,
                error_message=str(e)
            )
    
    def _check_cache(self, columns: List[str]) -> List[ColumnMapping]:
        """Check cache for existing mappings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cached_mappings = []
        for column in columns:
            column_hash = self._hash_column(column)
            cursor.execute(
                'SELECT original_column, mapped_to, confidence, reasoning FROM column_mappings WHERE column_hash = ?',
                (column_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                cached_mappings.append(ColumnMapping(
                    original_column=result[0],
                    mapped_to=result[1],
                    confidence=result[2],
                    reasoning=result[3],
                    source="cache"
                ))
                self.cache_hits += 1
                
                # Update usage count
                cursor.execute(
                    'UPDATE column_mappings SET usage_count = usage_count + 1 WHERE column_hash = ?',
                    (column_hash,)
                )
        
        conn.commit()
        conn.close()
        
        return cached_mappings
    
    def _get_gpt_mappings(self, columns: List[str], context: str) -> List[ColumnMapping]:
        """Get column mappings from GPT-4o-mini."""
        
        # Create business-optimized multi-domain prompt
        prompt = self._create_business_prompt(columns, context)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are TANAW Analytics AI - expert at mapping business columns intelligently. Choose ONE column per type, mark duplicates as Ignore. Keep reasoning concise (<100 chars). Return valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=600,   # Optimized for concise responses
                response_format={"type": "json_object"}
            )
            
            # Parse response with better error handling
            response_text = response.choices[0].message.content
            
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error: {e}")
                print(f"📄 Raw response (first 500 chars): {response_text[:500]}")
                # Try to fix common JSON issues
                try:
                    # Remove any trailing commas, fix quotes
                    cleaned = response_text.replace(',]', ']').replace(',}', '}')
                    result = json.loads(cleaned)
                    print(f"✅ Fixed JSON and parsed successfully")
                except:
                    print(f"❌ Could not fix JSON, using fallback")
                    raise
            
            # Calculate cost (approximate)
            input_tokens = len(prompt.split()) * 1.3  # Rough estimate
            output_tokens = len(response_text.split()) * 1.3
            total_tokens = input_tokens + output_tokens
            cost = total_tokens * 0.00015 / 1000  # gpt-4o-mini pricing
            self.total_cost += cost
            
            # Convert to ColumnMapping objects
            mappings = []
            for mapping in result.get('mappings', []):
                mappings.append(ColumnMapping(
                    original_column=mapping['original'],
                    mapped_to=mapping['mapped_to'],
                    confidence=mapping['confidence'],
                    reasoning=mapping['reasoning'],
                    source="gpt"
                ))
            
            return mappings
            
        except Exception as e:
            print(f"❌ GPT mapping failed: {e}")
            return self._fallback_mappings(columns)
    
    def _create_business_prompt(self, columns: List[str], context: str) -> str:
        """Create optimized prompt balancing context and brevity for reliable JSON responses."""
        
        return f"""
You are TANAW Analytics AI mapping columns for {context} business analytics.

GOAL: Map columns to generate accurate charts. Wrong mappings create duplicate or misleading charts!

COLUMNS: {', '.join(columns)}

TANAW GENERATES THESE CHARTS:
• Product Performance (Bar) - needs Product + Sales
• Regional Sales (Bar) - needs Location + Sales  
• Sales Trend (Line) - needs Date + Sales
• Sales Forecast (AI) - needs Date + Sales
• Stock Levels (Bar) - needs Product + Stock
• Inventory Forecast (AI) - needs Date + Stock

DECISION RULES:

1. DATES - Choose transaction date, ignore system dates
   • "Date", "Order_Date", "Sale_Date" → Date
   • "Date_Created", "Updated_At" → Ignore (system metadata)

2. SALES - Choose most explicit transaction amount
   • "Sales", "Sales_Amount" → Sales (BEST)
   • "Amount" → Sales (good)
   • "Revenue" → Sales (accounting, less preferred)
   • "Value", "Total" → Ignore (too generic)
   • "Price" → Price (unit price, NOT total)

3. PRODUCTS - Choose specific product identifier
   • "Product_Name", "Product", "Item" → Product (specific)
   • "Category" → Ignore (grouping, not specific)

4. LOCATIONS - Choose primary business location
   • "Branch", "Location", "Region" → Region (primary)
   • "Location2", "Area", "Zone" → Ignore (secondary)

5. QUANTITIES - Choose based on context
   • "Quantity", "Qty" → Quantity (items sold/in stock)
   • "Units", "Count" → Quantity (if clear)
   • "Stock", "Stock_Level" → Quantity (inventory)

RELATIONSHIP INTELLIGENCE:
💡 If you see Quantity + Price columns → expect Sales = Quantity × Price
💡 If you see Revenue + Cost columns → expect Profit = Revenue − Cost
💡 Product often belongs to Category (Product is more specific, Category is grouping)
💡 Customer relates to transactions (Customer ≠ Sales Rep or Employee)
💡 Transaction dates (Order/Sale Date) are more relevant than system dates (Created/Updated)

Use these relationship hints to improve confidence scores and reasoning.

CRITICAL: Map ONLY ONE column per type! If multiple candidates exist:
→ Choose MOST EXPLICIT name (Sales_Amount > Amount > Value)
→ Mark others as "Ignore" with reason

CONFIDENCE GUIDE:
• 90-100: Perfect match (Sales_Amount → Sales)
• 75-89: Good match (Amount → Sales)
• 60-74: Acceptable (Value → Sales)
• <60: Too uncertain - mark as "Ignore"

EXAMPLE: [Date1, Date2, Amount, Total, Location1, Location2]
{{
  "mappings": [
    {{"original": "Date1", "mapped_to": "Date", "confidence": 85, "reasoning": "Primary date column for transaction date"}},
    {{"original": "Date2", "mapped_to": "Ignore", "confidence": 80, "reasoning": "Secondary date, Date1 is primary"}},
    {{"original": "Amount", "mapped_to": "Sales", "confidence": 85, "reasoning": "Transaction amount, more explicit than Total"}},
    {{"original": "Total", "mapped_to": "Ignore", "confidence": 75, "reasoning": "Calculated field, Amount is primary"}},
    {{"original": "Location1", "mapped_to": "Region", "confidence": 85, "reasoning": "Primary location for regional analysis"}},
    {{"original": "Location2", "mapped_to": "Ignore", "confidence": 80, "reasoning": "Secondary location, Location1 is primary"}}
  ]
}}

NOW MAP: {', '.join(columns)}

Return ONLY valid JSON in the format above. Keep reasoning under 100 characters.
"""
    
    def _fallback_mappings(self, columns: List[str]) -> List[ColumnMapping]:
        """
        Intelligent fallback mapper with duplicate prevention.
        Enforces ONLY ONE column per canonical type rule.
        """
        print(f"🔧 Fallback Mapper: Processing {len(columns)} columns with smart prioritization")
        
        # Step 1: Score all columns for each canonical type
        candidates = {
            'Date': [],
            'Sales': [],
            'Product': [],
            'Region': [],
            'Quantity': [],
            'Revenue': [],
            'Expense': [],
            'Customer': [],
            'Price': []
        }
        
        for column in columns:
            if not isinstance(column, str):
                column = str(column)
            
            col_lower = column.lower()
            
            # Date patterns (prefer transaction dates, not system metadata)
            if any(kw in col_lower for kw in ['date', 'time', 'order']):
                score = 75.0
                if col_lower == 'date' or col_lower == 'date1':
                    score = 90.0  # Simple "Date" or "Date1" is best
                elif 'order' in col_lower or 'sale' in col_lower or 'transaction' in col_lower:
                    score = 85.0  # Transaction dates are good
                elif 'created' in col_lower or 'updated' in col_lower:
                    score = 50.0  # System metadata - deprioritize
                candidates['Date'].append((column, score, "Date column"))
            
            # Sales patterns (prefer explicit names over generic)
            if any(kw in col_lower for kw in ['sales', 'amount', 'revenue', 'value', 'total']):
                score = 65.0
                if 'sales' in col_lower and 'amount' in col_lower:
                    score = 95.0  # "Sales_Amount" is perfect
                elif 'sales' in col_lower:
                    score = 90.0  # "Sales" is excellent
                elif 'amount' in col_lower:
                    score = 85.0  # "Amount" is good
                elif 'revenue' in col_lower:
                    score = 80.0  # "Revenue" is okay
                elif 'value' in col_lower:
                    score = 70.0  # "Value" is generic
                elif 'total' in col_lower:
                    score = 60.0  # "Total" is calculated field
                candidates['Sales'].append((column, score, "Sales/Amount"))
            
            # Product patterns (prefer specific identifiers)
            if any(kw in col_lower for kw in ['product', 'item', 'sku', 'name']):
                score = 70.0
                if 'product' in col_lower and 'name' in col_lower:
                    score = 95.0  # "Product_Name" is perfect
                elif 'product' in col_lower:
                    score = 90.0  # "Product" is excellent
                elif 'item' in col_lower:
                    score = 85.0  # "Item" is good
                elif col_lower == 'name':
                    score = 75.0  # Generic "Name" might be product
                elif 'sku' in col_lower:
                    score = 90.0  # "SKU" is good
                if 'category' in col_lower:
                    score = 60.0  # "Category" is grouping
                candidates['Product'].append((column, score, "Product"))
            
            # Region patterns (prefer primary locations, avoid secondaries)
            if any(kw in col_lower for kw in ['region', 'location', 'branch', 'store', 'city', 'area']):
                score = 70.0
                if 'branch' in col_lower:
                    score = 90.0  # "Branch" is best for retail
                elif 'location' in col_lower and '1' in column:
                    score = 85.0  # "Location1" is primary
                elif 'location' in col_lower and '2' not in column:
                    score = 80.0  # Generic "Location"
                elif 'region' in col_lower:
                    score = 80.0  # "Region" is good
                # Penalize numbered secondaries
                if '2' in column or 'secondary' in col_lower:
                    score = 50.0  # "Location2" is secondary
                candidates['Region'].append((column, score, "Location"))
            
            # Quantity patterns (prefer explicit quantity terms)
            if any(kw in col_lower for kw in ['quantity', 'qty', 'units', 'stock', 'count']):
                score = 70.0
                if 'qty' in col_lower or 'quantity' in col_lower:
                    score = 90.0  # "Qty" or "Quantity" is best
                elif 'stock' in col_lower:
                    score = 85.0  # "Stock" is good for inventory
                elif 'units' in col_lower:
                    score = 80.0  # "Units" is okay
                elif 'count' in col_lower:
                    score = 65.0  # "Count" is generic, could be location count
                candidates['Quantity'].append((column, score, "Quantity"))
        
        # Step 2: Select BEST candidate for each type (ONLY ONE per type!)
        mappings = []
        used_columns = set()
        
        for canonical_type, column_candidates in candidates.items():
            if column_candidates:
                # Sort by score (highest first)
                column_candidates.sort(key=lambda x: x[1], reverse=True)
                
                # Take the BEST one only
                best_column, best_score, reasoning = column_candidates[0]
                
                mappings.append(ColumnMapping(
                    original_column=best_column,
                    mapped_to=canonical_type,
                    confidence=best_score,
                    reasoning=f"{reasoning} (best match)",
                    source="fallback"
                ))
                used_columns.add(best_column)
                
                print(f"   ✅ {best_column} → {canonical_type} (score: {best_score:.0f}, selected from {len(column_candidates)} candidates)")
                
                # Mark other candidates as Ignore
                for other_column, other_score, other_reason in column_candidates[1:]:
                    mappings.append(ColumnMapping(
                        original_column=other_column,
                        mapped_to="Ignore",
                        confidence=other_score - 10.0,
                        reasoning=f"Duplicate - {best_column} is primary",
                        source="fallback"
                    ))
                    used_columns.add(other_column)
                    print(f"   ⏭️ {other_column} → Ignore (duplicate, {best_column} chosen)")
        
        # Step 3: Mark any unmapped columns as Ignore
        for column in columns:
            if not isinstance(column, str):
                column = str(column)
            
            if column not in used_columns:
                mappings.append(ColumnMapping(
                    original_column=column,
                    mapped_to="Ignore",
                    confidence=50.0,
                    reasoning="No clear business purpose",
                    source="fallback"
                ))
                print(f"   ⏭️ {column} → Ignore (no pattern match)")
        
        print(f"✅ Fallback complete: {len([m for m in mappings if m.mapped_to != 'Ignore'])} mapped, {len([m for m in mappings if m.mapped_to == 'Ignore'])} ignored")
        
        return mappings
    
    def _validate_mappings(self, mappings: List[ColumnMapping], original_columns: List[str]) -> List[ColumnMapping]:
        """Validate and clean mapping results."""
        
        # Remove duplicates (keep highest confidence)
        mapping_dict = {}
        for mapping in mappings:
            key = mapping.original_column
            if key not in mapping_dict or mapping.confidence > mapping_dict[key].confidence:
                mapping_dict[key] = mapping
        
        # Ensure all original columns are covered
        validated = list(mapping_dict.values())
        mapped_columns = {m.original_column for m in validated}
        
        for column in original_columns:
            # Ensure column is a string
            column_str = str(column)
            if column_str not in mapped_columns:
                # Add as "Ignore" if not mapped
                validated.append(ColumnMapping(
                    original_column=column_str,
                    mapped_to="Ignore",
                    confidence=0.0,
                    reasoning="No clear mapping found",
                    source="fallback"
                ))
        
        return validated
    
    def _store_in_cache(self, mappings: List[ColumnMapping]):
        """Store GPT mappings in cache database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for mapping in mappings:
            if mapping.source == "gpt":  # Only cache GPT results
                column_hash = self._hash_column(mapping.original_column)
                cursor.execute('''
                    INSERT OR REPLACE INTO column_mappings 
                    (column_hash, original_column, mapped_to, confidence, reasoning)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    column_hash,
                    mapping.original_column,
                    mapping.mapped_to,
                    mapping.confidence,
                    mapping.reasoning
                ))
        
        conn.commit()
        conn.close()
    
    def _hash_column(self, column: str) -> str:
        """Create hash for column name for caching."""
        return hashlib.md5(column.lower().encode()).hexdigest()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM column_mappings')
        total_cached = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(usage_count) FROM column_mappings')
        total_usage = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_cached_mappings": total_cached,
            "total_usage_count": total_usage,
            "cache_hit_rate": self.cache_hits / max(1, self.cache_hits + len([m for m in self.mappings if m.source == "gpt"])),
            "total_cost": self.total_cost
        }
