"""
Phase 4: GPT Escalation (Headers Only) - Safe, Structured
Implements safe LLM consultation for column mapping when local inference is insufficient.
Only sends normalized headers, never raw data.

Features:
- Batch column processing for efficient GPT usage
- Strict prompt templates with system messages
- Robust JSON parsing and validation
- Retry logic with exponential backoff
- Failure modes and fallbacks
- Comprehensive observability
"""

import json
import re
import time
import random
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
import warnings

# Try to import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    warnings.warn("OpenAI not available. Install with: pip install openai")

# Import existing configuration
from config_manager import get_config

@dataclass
class GPTMapping:
    """Represents a GPT mapping result."""
    original: str
    mapped_to: str
    confidence: int
    reason: str

@dataclass
class GPTBatchResult:
    """Results from GPT batch processing."""
    mappings: List[GPTMapping]
    processing_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class GPTEscalationResult:
    """Results from GPT escalation process."""
    escalated_columns: Dict[str, GPTMapping]
    local_fallbacks: Dict[str, Any]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class GPTEscalation:
    """
    Phase 4: GPT Escalation system for column mapping.
    
    Features:
    - Safe header-only processing (no raw data)
    - Batch processing for efficiency
    - Strict prompt templates
    - Robust JSON parsing
    - Retry logic with exponential backoff
    - Failure modes and fallbacks
    - Comprehensive observability
    """
    
    def __init__(self, config=None):
        """Initialize GPT escalation with configuration."""
        self.config = config or get_config()
        self.escalation_version = "4.0.0"
        
        # Initialize OpenAI client if available
        self.client = None
        if OPENAI_AVAILABLE:
            try:
                self.client = openai.OpenAI(api_key=self.config.llm.openai_api_key)
            except Exception as e:
                warnings.warn(f"Failed to initialize OpenAI client: {e}")
        
        # Canonical schema for mapping
        self.canonical_schema = [
            "Date", "Sales", "Amount", "Product", "Quantity", 
            "Region", "Customer", "Transaction_ID"
        ]
        
        # Analytics requirements
        self.analytics_requirements = {
            "Date": "Time-based data for temporal analysis",
            "Sales": "Revenue and sales metrics",
            "Amount": "Monetary values and financial data",
            "Product": "Product information and categorization",
            "Quantity": "Numeric quantities and volumes",
            "Region": "Geographic and location data",
            "Customer": "Customer information and demographics",
            "Transaction_ID": "Unique identifiers for transactions"
        }
        
        # Metrics tracking
        self.metrics = {
            'gpt_call_count': 0,
            'gpt_success_rate': 0.0,
            'gpt_parse_errors': 0,
            'gpt_retry_count': 0,
            'average_response_time_ms': 0.0,
            'columns_escalated': 0,
            'local_fallbacks': 0,
            'processing_time_ms': 0.0
        }
    
    def escalate_columns(self, column_inferences: Dict[str, Any], 
                        local_confidence_threshold: float = 75.0) -> GPTEscalationResult:
        """
        Escalate columns to GPT when local inference is insufficient.
        
        Args:
            column_inferences: Results from Phase 3 value analysis
            local_confidence_threshold: Minimum confidence for local mapping
            
        Returns:
            GPTEscalationResult with escalated mappings
        """
        start_time = time.time()
        
        try:
            # Identify columns that need escalation
            columns_to_escalate = []
            local_fallbacks = {}
            
            for col, inference in column_inferences.items():
                if inference.get('local_confidence', 0) < local_confidence_threshold:
                    columns_to_escalate.append(col)
                else:
                    # Keep local result as fallback
                    local_fallbacks[col] = {
                        'best_candidate': inference.get('best_candidate'),
                        'local_confidence': inference.get('local_confidence'),
                        'source': 'local'
                    }
            
            if not columns_to_escalate:
                return GPTEscalationResult(
                    escalated_columns={},
                    local_fallbacks=local_fallbacks,
                    processing_time_seconds=time.time() - start_time,
                    metrics=self.metrics.copy(),
                    success=True
                )
            
            # Batch columns for GPT processing
            batches = self._create_column_batches(columns_to_escalate)
            escalated_columns = {}
            
            for batch in batches:
                try:
                    batch_result = self._process_gpt_batch(batch)
                    if batch_result.success:
                        for mapping in batch_result.mappings:
                            escalated_columns[mapping.original] = mapping
                    else:
                        # Fallback to local results for this batch
                        for col in batch:
                            if col in column_inferences:
                                inference = column_inferences[col]
                                local_fallbacks[col] = {
                                    'best_candidate': inference.get('best_candidate'),
                                    'local_confidence': inference.get('local_confidence', 0) * 0.8,  # Reduce confidence
                                    'source': 'local_fallback'
                                }
                except Exception as e:
                    print(f"⚠️ Error processing batch {batch}: {e}")
                    # Fallback to local results
                    for col in batch:
                        if col in column_inferences:
                            inference = column_inferences[col]
                            local_fallbacks[col] = {
                                'best_candidate': inference.get('best_candidate'),
                                'local_confidence': inference.get('local_confidence', 0) * 0.8,
                                'source': 'local_fallback'
                            }
            
            processing_time = time.time() - start_time
            self.metrics['processing_time_ms'] = processing_time * 1000
            self.metrics['columns_escalated'] = len(escalated_columns)
            self.metrics['local_fallbacks'] = len(local_fallbacks)
            
            return GPTEscalationResult(
                escalated_columns=escalated_columns,
                local_fallbacks=local_fallbacks,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return GPTEscalationResult(
                escalated_columns={},
                local_fallbacks={},
                processing_time_seconds=time.time() - start_time,
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _create_column_batches(self, columns: List[str]) -> List[List[str]]:
        """Create batches of columns for GPT processing."""
        max_columns = self.config.llm.max_columns_per_gpt
        batches = []
        
        for i in range(0, len(columns), max_columns):
            batch = columns[i:i + max_columns]
            batches.append(batch)
        
        return batches
    
    def _process_gpt_batch(self, columns: List[str]) -> GPTBatchResult:
        """Process a batch of columns with GPT."""
        if not self.client:
            raise Exception("OpenAI client not available")
        
        start_time = time.time()
        retry_count = 0
        max_retries = self.config.llm.max_retries
        
        while retry_count <= max_retries:
            try:
                # Build prompt
                prompt = self._build_prompt(columns)
                
                # Call GPT
                response = self._call_gpt(prompt)
                
                # Parse response
                mappings = self._parse_gpt_response(response)
                
                processing_time = time.time() - start_time
                self.metrics['gpt_call_count'] += 1
                self.metrics['average_response_time_ms'] = processing_time * 1000
                
                return GPTBatchResult(
                    mappings=mappings,
                    processing_time_seconds=processing_time,
                    success=True
                )
                
            except Exception as e:
                retry_count += 1
                self.metrics['gpt_retry_count'] += 1
                
                if retry_count <= max_retries:
                    # Exponential backoff
                    backoff_time = (2 ** retry_count) + random.uniform(0, 1)
                    time.sleep(backoff_time)
                    print(f"⚠️ GPT call failed, retrying {retry_count}/{max_retries}: {e}")
                else:
                    raise e
        
        # Should not reach here
        raise Exception("Max retries exceeded")
    
    def _build_prompt(self, columns: List[str]) -> str:
        """Build strict prompt for GPT."""
        system_message = (
            "You are a mapping assistant. Your role is to map column headers to canonical fields. "
            "You will NEVER receive actual user data, only normalized column headers. "
            "Return ONLY valid JSON with no additional text."
        )
        
        canonical_fields = ', '.join([f'"{field}"' for field in self.canonical_schema])
        column_headers = ', '.join([f'"{col}"' for col in columns])
        
        prompt = f"""You are a mapping assistant. Map these headers: [{column_headers}] to canonical fields [{canonical_fields}].

Return ONLY JSON:
{{ "mappings": [{{"original":"header_name", "mapped_to":"canonical_field", "confidence":87, "reason":"brief explanation"}}] }}

Do NOT output any other text."""
        
        return prompt
    
    def _call_gpt(self, prompt: str) -> str:
        """Call GPT with the prompt."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=[
                    {"role": "system", "content": "You are a mapping assistant. Your role is to map column headers to canonical fields. You will NEVER receive actual user data, only normalized column headers. Return ONLY valid JSON with no additional text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"GPT API call failed: {e}")
    
    def _parse_gpt_response(self, response: str) -> List[GPTMapping]:
        """Parse GPT response with robust JSON extraction."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Handle different response formats
            if isinstance(data, list):
                mappings_data = data
            elif isinstance(data, dict) and 'mappings' in data:
                mappings_data = data['mappings']
            else:
                raise Exception("Invalid response format")
            
            # Validate and convert mappings
            mappings = []
            for mapping_data in mappings_data:
                if not isinstance(mapping_data, dict):
                    continue
                
                # Validate required fields
                if not all(key in mapping_data for key in ['original', 'mapped_to', 'confidence', 'reason']):
                    continue
                
                # Convert types and validate
                original = str(mapping_data['original'])
                mapped_to = str(mapping_data['mapped_to'])
                confidence = int(mapping_data['confidence'])
                reason = str(mapping_data['reason'])
                
                # Validate confidence range
                if not (0 <= confidence <= 100):
                    confidence = max(0, min(100, confidence))
                
                mappings.append(GPTMapping(
                    original=original,
                    mapped_to=mapped_to,
                    confidence=confidence,
                    reason=reason
                ))
            
            return mappings
            
        except json.JSONDecodeError as e:
            self.metrics['gpt_parse_errors'] += 1
            raise Exception(f"JSON parsing failed: {e}")
        except Exception as e:
            self.metrics['gpt_parse_errors'] += 1
            raise Exception(f"Response parsing failed: {e}")
    
    def _calculate_success_rate(self):
        """Calculate GPT success rate."""
        if self.metrics['gpt_call_count'] > 0:
            self.metrics['gpt_success_rate'] = (
                (self.metrics['gpt_call_count'] - self.metrics['gpt_parse_errors']) / 
                self.metrics['gpt_call_count']
            ) * 100
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        self._calculate_success_rate()
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'gpt_call_count': 0,
            'gpt_success_rate': 0.0,
            'gpt_parse_errors': 0,
            'gpt_retry_count': 0,
            'average_response_time_ms': 0.0,
            'columns_escalated': 0,
            'local_fallbacks': 0,
            'processing_time_ms': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "gpt.call_count": self.metrics['gpt_call_count'],
                "gpt.success_rate": self.metrics['gpt_success_rate'],
                "gpt.parse_errors": self.metrics['gpt_parse_errors'],
                "gpt.retry_count": self.metrics['gpt_retry_count'],
                "gpt.average_response_time_ms": self.metrics['average_response_time_ms'],
                "gpt.columns_escalated": self.metrics['columns_escalated'],
                "gpt.local_fallbacks": self.metrics['local_fallbacks'],
                "gpt.processing_time_ms": self.metrics['processing_time_ms']
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 GPT escalation metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting GPT escalation metrics: {e}")
            return {"gpt.metrics_error": str(e)}

# Global escalation instance
gpt_escalation = GPTEscalation()

def escalate_columns(column_inferences: Dict[str, Any], 
                    local_confidence_threshold: float = 75.0) -> GPTEscalationResult:
    """
    Convenience function to escalate columns to GPT.
    
    Args:
        column_inferences: Results from Phase 3 value analysis
        local_confidence_threshold: Minimum confidence for local mapping
        
    Returns:
        GPTEscalationResult with escalated mappings
    """
    return gpt_escalation.escalate_columns(column_inferences, local_confidence_threshold)

if __name__ == "__main__":
    # Test the GPT escalation system
    print("🧪 Testing GPT Escalation System")
    print("=" * 50)
    
    # Create test column inferences
    test_inferences = {
        'Transaction_Date': {
            'best_candidate': 'Date',
            'local_confidence': 90.0,
            'weighted_score': 0.9
        },
        'Sales_Amount': {
            'best_candidate': 'Sales',
            'local_confidence': 85.0,
            'weighted_score': 0.85
        },
        'Product_ID': {
            'best_candidate': 'Product',
            'local_confidence': 60.0,  # Low confidence - should escalate
            'weighted_score': 0.6
        },
        'Customer_Region': {
            'best_candidate': 'Region',
            'local_confidence': 70.0,  # Low confidence - should escalate
            'weighted_score': 0.7
        }
    }
    
    result = escalate_columns(test_inferences, local_confidence_threshold=75.0)
    
    if result.success:
        print(f"✅ Successfully processed {len(result.escalated_columns)} escalated columns")
        print(f"✅ {len(result.local_fallbacks)} local fallbacks")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        for col, mapping in result.escalated_columns.items():
            print(f"\n📊 {col}:")
            print(f"   Mapped to: {mapping.mapped_to}")
            print(f"   Confidence: {mapping.confidence}%")
            print(f"   Reason: {mapping.reason}")
    else:
        print(f"❌ Error: {result.error_message}")
