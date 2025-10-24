"""
Enhanced GPT Column Mapper with domain-aware mapping.
Uses domain-specific schemas and business intelligence for accurate column mapping.
"""

import json
import re
import sqlite3
import openai
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from domain_detector import DomainDetector

@dataclass
class MappingResult:
    """Result of column mapping operation."""
    success: bool
    mapped_columns: List[Dict[str, Any]]
    uncertain_columns: List[Dict[str, Any]]
    unmapped_columns: List[Dict[str, Any]]
    domain: str
    total_cost: float
    cache_hits: int
    processing_time: float
    error_message: Optional[str] = None

class EnhancedGPTColumnMapper:
    """
    Domain-aware GPT column mapper with business intelligence.
    
    Features:
    - Automatic domain detection
    - Domain-specific canonical schemas
    - Built-in duplicate prevention
    - Structured JSON output
    - Intelligent fallbacks
    """
    
    def __init__(self, api_key: str, db_path: str = "tanaw_enhanced_mapping_cache.db"):
        self.api_key = api_key
        self.db_path = db_path
        self.client = openai.OpenAI(api_key=api_key)
        self.domain_detector = DomainDetector()
        
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
                domain TEXT,
                original_column TEXT,
                mapped_to TEXT,
                confidence REAL,
                reasoning TEXT,
                canonical_type TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def build_gpt_prompt(self, domain: str, headers: List[str], canonical_schema: List[Dict]) -> Dict:
        """
        Builds a strict domain-aware GPT mapping prompt for TANAW.
        Ensures no ambiguity, duplicates, or schema mismatches.
        """
        
        # Get domain description
        domain_description = self.domain_detector.get_domain_description(domain)
        
        # Build canonical field descriptions
        schema_desc = "\n".join([
            f"- {f['field']}: {f['desc']}"
            for f in canonical_schema
        ])
        
        # Construct the GPT messages
        system_msg = f"""
You are a JSON-only column mapping assistant for the TANAW analytics engine.
Follow these STRICT RULES:
1. You must output a single valid JSON object and nothing else.
2. Each input column must map to at most ONE canonical field.
3. Each canonical field must appear only once (no duplicates).
4. If a column is unrelated or ambiguous, map it to "Ignore".
5. Never create new canonical fields that aren't in the provided schema.
6. Always include: original, mapped_to, confidence (0–100), reason, canonical_type, role.
7. confidence reflects how sure you are based on column *name semantics* (not data values).
8. If unsure, confidence < 50 and mapped_to = "Ignore".
9. Output must be strictly valid JSON, no comments or explanations outside it.
10. Use lowercase for canonical_type (e.g., "text", "numeric", "date").
        """
        
        user_msg = f"""
Dataset domain: {domain.upper()}
Description: {domain_description}

Canonical schema for this domain:
{schema_desc}

Input column headers:
{json.dumps(headers, ensure_ascii=False)}

TASK:
Map each input column to its correct canonical field, or "Ignore" if unrelated.

Return ONLY JSON in the exact format below:

{{
  "mappings": [
    {{
      "original": "ColumnName",
      "mapped_to": "CanonicalField or Ignore",
      "confidence": 95,
      "reason": "Short explanation of the match decision.",
      "canonical_type": "text|numeric|date|category|id",
      "role": "attribute|metric|identifier|timestamp"
    }}
  ]
}}
        """
        
        return {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_msg.strip()},
                {"role": "user", "content": user_msg.strip()},
            ],
            "temperature": 0.1,
            "max_tokens": 500,
            "response_format": {"type": "json_object"}
        }
    
    def map_columns(self, columns: List[str], dataset_context: str = "retail") -> MappingResult:
        """
        Map columns using domain-aware GPT approach.
        
        Args:
            columns: List of column names to map
            dataset_context: Context hint for domain detection
            
        Returns:
            MappingResult with mapped columns and metadata
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Detect domain
            domain = self.domain_detector.detect_domain(None, columns)
            print(f"🔍 Detected domain: {domain}")
            
            # Step 2: Get canonical schema for domain
            canonical_schema = self.domain_detector.get_canonical_schema(domain)
            if not canonical_schema:
                return MappingResult(
                    success=False,
                    mapped_columns=[],
                    uncertain_columns=[],
                    unmapped_columns=[],
                    domain=domain,
                    total_cost=0.0,
                    cache_hits=0,
                    processing_time=0.0,
                    error_message=f"No canonical schema found for domain: {domain}"
                )
            
            # Step 3: Check cache for existing mappings
            cached_mappings = self._get_cached_mappings(columns, domain)
            uncached_columns = [col for col in columns if col not in cached_mappings]
            
            print(f"📋 Cache hits: {len(cached_mappings)}/{len(columns)}")
            print(f"📋 Uncached columns: {uncached_columns}")
            
            # Step 4: Get GPT mappings for uncached columns
            gpt_mappings = []
            if uncached_columns:
                gpt_mappings = self._get_gpt_mappings(uncached_columns, domain, canonical_schema)
            
            # Step 5: Combine cached and GPT mappings
            all_mappings = {**cached_mappings, **gpt_mappings}
            
            # Step 6: Process results
            mapped_columns = []
            uncertain_columns = []
            unmapped_columns = []
            
            for column in columns:
                if column in all_mappings:
                    mapping = all_mappings[column]
                    if mapping['mapped_to'] == 'Ignore':
                        unmapped_columns.append({
                            'original_column': column,
                            'confidence': mapping['confidence'],
                            'reason': mapping['reason']
                        })
                    elif mapping['confidence'] < 70:
                        uncertain_columns.append({
                            'original_column': column,
                            'mapped_column': mapping['mapped_to'],
                            'confidence': mapping['confidence'],
                            'reasoning': mapping['reason']
                        })
                    else:
                        mapped_columns.append({
                            'original_column': column,
                            'mapped_column': mapping['mapped_to'],
                            'confidence': mapping['confidence'],
                            'reasoning': mapping['reason']
                        })
                else:
                    unmapped_columns.append({
                        'original_column': column,
                        'confidence': 0,
                        'reason': 'No mapping found'
                    })
            
            # Step 7: Apply business logic to prevent duplicates
            mapped_columns = self._apply_business_logic(mapped_columns, domain)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MappingResult(
                success=True,
                mapped_columns=mapped_columns,
                uncertain_columns=uncertain_columns,
                unmapped_columns=unmapped_columns,
                domain=domain,
                total_cost=self.total_cost,
                cache_hits=len(cached_mappings),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return MappingResult(
                success=False,
                mapped_columns=[],
                uncertain_columns=[],
                unmapped_columns=[],
                domain="unknown",
                total_cost=self.total_cost,
                cache_hits=self.cache_hits,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _get_cached_mappings(self, columns: List[str], domain: str) -> Dict[str, Dict]:
        """Get cached mappings for columns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cached_mappings = {}
        for column in columns:
            column_hash = self._hash_column(column, domain)
            cursor.execute(
                "SELECT * FROM column_mappings WHERE column_hash = ?",
                (column_hash,)
            )
            result = cursor.fetchone()
            if result:
                cached_mappings[column] = {
                    'mapped_to': result[3],
                    'confidence': result[4],
                    'reason': result[5],
                    'canonical_type': result[6],
                    'role': result[7]
                }
                self.cache_hits += 1
        
        conn.close()
        return cached_mappings
    
    def _get_gpt_mappings(self, columns: List[str], domain: str, canonical_schema: List[Dict]) -> Dict[str, Dict]:
        """Get GPT mappings for uncached columns."""
        if not columns:
            return {}
        
        try:
            # Build prompt
            prompt = self.build_gpt_prompt(domain, columns, canonical_schema)
            
            # Call GPT
            response = self.client.chat.completions.create(**prompt)
            result = response.choices[0].message.content
            
            # Parse JSON response
            try:
                mappings_data = json.loads(result)
                mappings = mappings_data.get("mappings", [])
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                match = re.search(r'\{[\s\S]+\}', result)
                if match:
                    mappings_data = json.loads(match.group(0))
                    mappings = mappings_data.get("mappings", [])
                else:
                    mappings = []
            
            # Convert to dictionary format and cache
            gpt_mappings = {}
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for mapping in mappings:
                original = mapping.get('original')
                mapped_to = mapping.get('mapped_to')
                confidence = mapping.get('confidence', 0)
                reason = mapping.get('reason', '')
                canonical_type = mapping.get('canonical_type', 'text')
                role = mapping.get('role', 'attribute')
                
                if original:
                    gpt_mappings[original] = {
                        'mapped_to': mapped_to,
                        'confidence': confidence,
                        'reason': reason,
                        'canonical_type': canonical_type,
                        'role': role
                    }
                    
                    # Cache the mapping
                    column_hash = self._hash_column(original, domain)
                    cursor.execute('''
                        INSERT OR REPLACE INTO column_mappings 
                        (column_hash, domain, original_column, mapped_to, confidence, reasoning, canonical_type, role)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (column_hash, domain, original, mapped_to, confidence, reason, canonical_type, role))
            
            conn.commit()
            conn.close()
            
            # Track cost
            if hasattr(response, 'usage'):
                self.total_cost += response.usage.total_tokens * 0.0000005  # Approximate cost
            
            return gpt_mappings
            
        except Exception as e:
            print(f"⚠️ GPT mapping error: {e}")
            return {}
    
    def _apply_business_logic(self, mapped_columns: List[Dict], domain: str) -> List[Dict]:
        """Apply business logic to prevent duplicate mappings."""
        # Group by mapped_column
        grouped = {}
        for mapping in mapped_columns:
            mapped_col = mapping['mapped_column']
            if mapped_col not in grouped:
                grouped[mapped_col] = []
            grouped[mapped_col].append(mapping)
        
        # For each canonical type, keep only the highest confidence mapping
        final_mappings = []
        for canonical_type, mappings in grouped.items():
            if len(mappings) > 1:
                # Sort by confidence and keep the best one
                best_mapping = max(mappings, key=lambda x: x['confidence'])
                final_mappings.append(best_mapping)
                print(f"🔧 Resolved duplicate {canonical_type}: kept {best_mapping['original_column']} (confidence: {best_mapping['confidence']})")
            else:
                final_mappings.extend(mappings)
        
        return final_mappings
    
    def _hash_column(self, column: str, domain: str) -> str:
        """Generate hash for column caching."""
        import hashlib
        return hashlib.md5(f"{domain}:{column}".encode()).hexdigest()

# Test the enhanced mapper
if __name__ == "__main__":
    # Test with sample data
    mapper = EnhancedGPTColumnMapper("your-api-key-here")
    
    # Test sales domain
    sales_columns = ["Product_ID", "Sale_Date", "Sales_Amount", "Quantity_Sold", "Region"]
    result = mapper.map_columns(sales_columns)
    print(f"Sales mapping result: {result.success}")
    print(f"Mapped columns: {len(result.mapped_columns)}")
    print(f"Domain: {result.domain}")
