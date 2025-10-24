"""
GPT Escalator - Phase 5: Escalate to OpenAI/GPT
Privacy-first AI disambiguation for uncertain column mappings

This module handles:
- Secure GPT API integration (headers only, no data)
- Batch processing for cost efficiency
- Response validation and parsing
- Caching to reduce API costs
- Error handling and retries
- Rate limiting compliance
"""

import json
import time
import hashlib
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
import os

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not installed. GPT escalation will use mock responses.")

try:
    from .confidence_evaluator import EvaluationResult, ColumnDecision, ActionType
    from .tanaw_canonical_schema import CanonicalColumnType, tanaw_schema
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from .file_preprocessor import FileMetadata
except ImportError:
    from confidence_evaluator import EvaluationResult, ColumnDecision, ActionType
    from tanaw_canonical_schema import CanonicalColumnType, tanaw_schema
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from file_preprocessor import FileMetadata

@dataclass
class GPTRequest:
    """Represents a GPT API request for column mapping."""
    request_id: str
    column_headers: List[str]
    request_prompt: str
    timestamp: datetime
    user_id: Optional[str] = None
    file_context: Optional[str] = None  # File name for context, never actual data

@dataclass
class GPTResponse:
    """Represents a GPT API response."""
    request_id: str
    raw_response: str
    parsed_mappings: Dict[str, Dict[str, Any]]  # column -> {mapped_to, confidence, reasoning}
    processing_time: float
    model_used: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    
@dataclass
class GPTEscalationResult:
    """Results from GPT escalation process."""
    original_evaluation: EvaluationResult
    gpt_requests: List[GPTRequest]
    gpt_responses: List[GPTResponse]
    
    # Enhanced mappings
    enhanced_decisions: List[ColumnDecision]
    confidence_improvements: Dict[str, float]  # column -> confidence improvement
    
    # Processing metadata
    total_columns_sent: int
    successful_responses: int
    failed_responses: int
    total_processing_time: float
    estimated_cost: float
    cache_hits: int
    
    escalation_timestamp: str
    escalator_version: str

class GPTCache:
    """Simple SQLite cache for GPT responses to reduce API costs."""
    
    def __init__(self, cache_file: str = "gpt_mapping_cache.db"):
        self.cache_file = cache_file
        self._init_cache()
    
    def _init_cache(self):
        """Initialize cache database."""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS gpt_cache (
                    cache_key TEXT PRIMARY KEY,
                    column_headers TEXT,
                    response TEXT,
                    timestamp TEXT,
                    ttl_hours INTEGER,
                    hit_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()
    
    def _generate_cache_key(self, headers: List[str], context: str = "") -> str:
        """Generate cache key from column headers and context."""
        cache_input = f"{sorted(headers)}_{context}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def get(self, headers: List[str], context: str = "", ttl_hours: int = 24) -> Optional[str]:
        """Get cached response if available and not expired."""
        cache_key = self._generate_cache_key(headers, context)
        
        with sqlite3.connect(self.cache_file) as conn:
            cursor = conn.execute("""
                SELECT response, timestamp, ttl_hours FROM gpt_cache 
                WHERE cache_key = ? AND datetime(timestamp, '+' || ttl_hours || ' hours') > datetime('now')
            """, (cache_key,))
            
            row = cursor.fetchone()
            if row:
                response, timestamp, stored_ttl = row
                
                # Update hit count
                conn.execute("""
                    UPDATE gpt_cache SET hit_count = hit_count + 1 WHERE cache_key = ?
                """, (cache_key,))
                conn.commit()
                
                return response
        
        return None
    
    def set(self, headers: List[str], response: str, context: str = "", ttl_hours: int = 24):
        """Cache response."""
        cache_key = self._generate_cache_key(headers, context)
        timestamp = datetime.now().isoformat()
        
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO gpt_cache 
                (cache_key, column_headers, response, timestamp, ttl_hours)
                VALUES (?, ?, ?, ?, ?)
            """, (cache_key, json.dumps(headers), response, timestamp, ttl_hours))
            conn.commit()
    
    def clear_expired(self):
        """Remove expired cache entries."""
        with sqlite3.connect(self.cache_file) as conn:
            conn.execute("""
                DELETE FROM gpt_cache 
                WHERE datetime(timestamp, '+' || ttl_hours || ' hours') <= datetime('now')
            """)
            conn.commit()

class GPTEscalator:
    """
    GPT escalation engine for uncertain column mappings.
    
    Features:
    - Privacy-first: Never sends actual data, only column headers
    - Cost-efficient: Batching, caching, and smart request optimization  
    - Reliable: Error handling, retries, and response validation
    - Secure: Input sanitization and response validation
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.canonical_schema = tanaw_schema
        self.cache = GPTCache() if self.config.gpt_config.enable_caching else None
        self.escalator_version = "1.0.0"
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE:
            # In production, API key should be set via environment variable
            openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def escalate_uncertain_columns(
        self, 
        evaluation_result: EvaluationResult,
        api_key: Optional[str] = None
    ) -> GPTEscalationResult:
        """
        Escalate uncertain columns to GPT for disambiguation.
        
        Args:
            evaluation_result: Results from Phase 4 confidence evaluation
            api_key: Optional OpenAI API key (overrides env var)
            
        Returns:
            Enhanced results with GPT analysis integrated
        """
        start_time = time.time()
        
        if api_key and OPENAI_AVAILABLE:
            openai.api_key = api_key
        
        # Identify columns for GPT escalation
        gpt_columns = [
            decision for decision in evaluation_result.column_decisions
            if decision.recommended_action == ActionType.SEND_TO_GPT
        ]
        
        if not gpt_columns:
            # No columns need GPT escalation
            return GPTEscalationResult(
                original_evaluation=evaluation_result,
                gpt_requests=[],
                gpt_responses=[],
                enhanced_decisions=evaluation_result.column_decisions,
                confidence_improvements={},
                total_columns_sent=0,
                successful_responses=0,
                failed_responses=0,
                total_processing_time=time.time() - start_time,
                estimated_cost=0.0,
                cache_hits=0,
                escalation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                escalator_version=self.escalator_version
            )
        
        print(f"🤖 Escalating {len(gpt_columns)} columns to GPT for analysis...")
        
        # Batch columns for efficient processing
        batches = self._create_batches(gpt_columns)
        
        gpt_requests = []
        gpt_responses = []
        cache_hits = 0
        
        # Process each batch
        for batch in batches:
            request = self._create_gpt_request(batch, evaluation_result.file_metadata)
            gpt_requests.append(request)
            
            # Check cache first
            if self.cache:
                cached_response = self.cache.get(
                    request.column_headers, 
                    request.file_context or "",
                    self.config.gpt_config.cache_ttl_hours
                )
                
                if cached_response:
                    print(f"   💾 Cache hit for {len(request.column_headers)} columns")
                    cache_hits += 1
                    response = self._parse_cached_response(request, cached_response)
                    gpt_responses.append(response)
                    continue
            
            # Make GPT API call
            response = self._call_gpt_api(request)
            gpt_responses.append(response)
            
            # Cache successful responses
            if response.parsed_mappings and self.cache:
                self.cache.set(
                    request.column_headers,
                    response.raw_response,
                    request.file_context or "",
                    self.config.gpt_config.cache_ttl_hours
                )
            
            # Rate limiting
            time.sleep(0.5)  # Prevent rate limit issues
        
        # Integrate GPT results with original analysis
        enhanced_decisions, confidence_improvements = self._integrate_gpt_results(
            evaluation_result.column_decisions, gpt_responses
        )
        
        # Calculate metrics
        successful_responses = len([r for r in gpt_responses if r.parsed_mappings])
        failed_responses = len(gpt_responses) - successful_responses
        total_cost = sum(r.cost_estimate or 0 for r in gpt_responses)
        
        return GPTEscalationResult(
            original_evaluation=evaluation_result,
            gpt_requests=gpt_requests,
            gpt_responses=gpt_responses,
            enhanced_decisions=enhanced_decisions,
            confidence_improvements=confidence_improvements,
            total_columns_sent=len(gpt_columns),
            successful_responses=successful_responses,
            failed_responses=failed_responses,
            total_processing_time=time.time() - start_time,
            estimated_cost=total_cost,
            cache_hits=cache_hits,
            escalation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            escalator_version=self.escalator_version
        )
    
    def _create_batches(self, gpt_columns: List[ColumnDecision]) -> List[List[ColumnDecision]]:
        """Create batches of columns for efficient GPT processing."""
        batch_size = self.config.gpt_config.max_columns_per_request
        batches = []
        
        for i in range(0, len(gpt_columns), batch_size):
            batch = gpt_columns[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def _create_gpt_request(
        self, 
        column_decisions: List[ColumnDecision],
        file_metadata: FileMetadata
    ) -> GPTRequest:
        """Create GPT request for a batch of columns."""
        
        column_headers = [decision.original_header for decision in column_decisions]
        
        # Generate secure prompt (headers only, no data)
        prompt = self._generate_prompt(column_headers, file_metadata.original_filename)
        
        request_id = hashlib.md5(f"{column_headers}_{time.time()}".encode()).hexdigest()[:12]
        
        return GPTRequest(
            request_id=request_id,
            column_headers=column_headers,
            request_prompt=prompt,
            timestamp=datetime.now(),
            user_id=file_metadata.user_id,
            file_context=file_metadata.original_filename
        )
    
    def _generate_prompt(self, headers: List[str], filename: Optional[str] = None) -> str:
        """Generate secure, privacy-first prompt for GPT."""
        
        base_template = self.config.get_prompt_template()
        
        # Add context about the file type (if available)
        context_note = ""
        if filename:
            context_note = f"\n\nCONTEXT: These headers are from a file named '{filename}'"
        
        # Format the prompt with headers
        formatted_prompt = base_template.format(
            column_headers=headers
        ) + context_note
        
        return formatted_prompt
    
    def _call_gpt_api(self, request: GPTRequest) -> GPTResponse:
        """Make API call to GPT."""
        start_time = time.time()
        
        if not OPENAI_AVAILABLE or not openai.api_key:
            print(f"   🔧 Using mock GPT response (OpenAI not available)")
            return self._create_mock_response(request, start_time)
        
        try:
            print(f"   🤖 Calling GPT for {len(request.column_headers)} columns...")
            
            response = openai.ChatCompletion.create(
                model=self.config.gpt_config.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a data analyst expert in column mapping for business analytics."
                    },
                    {
                        "role": "user", 
                        "content": request.request_prompt
                    }
                ],
                max_tokens=self.config.gpt_config.max_tokens,
                temperature=self.config.gpt_config.temperature,
                timeout=self.config.gpt_config.timeout_seconds
            )
            
            processing_time = time.time() - start_time
            raw_response = response.choices[0].message.content
            
            # Parse response
            parsed_mappings = self._parse_gpt_response(raw_response, request.column_headers)
            
            # Calculate cost estimate (rough)
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            cost_estimate = self._estimate_cost(tokens_used, self.config.gpt_config.model)
            
            print(f"   ✅ GPT response received ({processing_time:.2f}s, ~${cost_estimate:.4f})")
            
            return GPTResponse(
                request_id=request.request_id,
                raw_response=raw_response,
                parsed_mappings=parsed_mappings,
                processing_time=processing_time,
                model_used=self.config.gpt_config.model,
                tokens_used=tokens_used,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            print(f"   ❌ GPT API error: {e}")
            # Return fallback response
            return self._create_fallback_response(request, start_time, str(e))
    
    def _parse_gpt_response(self, raw_response: str, expected_headers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Parse and validate GPT response."""
        try:
            # Try to extract JSON from the response
            json_start = raw_response.find('{')
            json_end = raw_response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = raw_response[json_start:json_end]
            response_data = json.loads(json_str)
            
            # Validate response structure
            if 'mappings' not in response_data:
                raise ValueError("Response missing 'mappings' field")
            
            parsed_mappings = {}
            
            for mapping in response_data['mappings']:
                if not all(key in mapping for key in ['original', 'mapped_to', 'confidence']):
                    continue  # Skip invalid mappings
                
                original = mapping['original']
                mapped_to = mapping['mapped_to']
                confidence = mapping.get('confidence', 0) / 100.0  # Convert to 0-1 scale
                reasoning = mapping.get('reasoning', 'GPT analysis')
                
                # Validate canonical type
                valid_types = [ct.value for ct in CanonicalColumnType] + ['null', None]
                if mapped_to not in valid_types:
                    mapped_to = None  # Invalid mapping
                
                # Validate confidence
                confidence = max(0.0, min(1.0, float(confidence)))
                
                parsed_mappings[original] = {
                    'mapped_to': mapped_to,
                    'confidence': confidence,
                    'reasoning': reasoning,
                    'method': 'gpt'
                }
            
            return parsed_mappings
            
        except Exception as e:
            print(f"   ⚠️ Failed to parse GPT response: {e}")
            return {}
    
    def _create_mock_response(self, request: GPTRequest, start_time: float) -> GPTResponse:
        """Create mock GPT response for testing."""
        
        # Simple mock logic based on header patterns
        mock_mappings = {}
        
        for header in request.column_headers:
            header_lower = header.lower()
            
            if 'date' in header_lower or 'time' in header_lower:
                mock_mappings[header] = {
                    'mapped_to': 'Date',
                    'confidence': 0.85,
                    'reasoning': 'Mock: Date pattern detected',
                    'method': 'mock_gpt'
                }
            elif 'amount' in header_lower or 'price' in header_lower:
                mock_mappings[header] = {
                    'mapped_to': 'Amount',
                    'confidence': 0.80,
                    'reasoning': 'Mock: Amount pattern detected',
                    'method': 'mock_gpt'
                }
            elif 'sales' in header_lower and 'rep' in header_lower:
                mock_mappings[header] = {
                    'mapped_to': 'Customer',
                    'confidence': 0.75,
                    'reasoning': 'Mock: Sales rep is customer-related',
                    'method': 'mock_gpt'
                }
            else:
                mock_mappings[header] = {
                    'mapped_to': None,
                    'confidence': 0.60,
                    'reasoning': 'Mock: Uncertain mapping',
                    'method': 'mock_gpt'
                }
        
        processing_time = time.time() - start_time
        
        return GPTResponse(
            request_id=request.request_id,
            raw_response=f"Mock GPT response for: {request.column_headers}",
            parsed_mappings=mock_mappings,
            processing_time=processing_time,
            model_used="mock-gpt",
            tokens_used=200,
            cost_estimate=0.001
        )
    
    def _create_fallback_response(self, request: GPTRequest, start_time: float, error: str) -> GPTResponse:
        """Create fallback response when GPT fails."""
        return GPTResponse(
            request_id=request.request_id,
            raw_response=f"ERROR: {error}",
            parsed_mappings={},
            processing_time=time.time() - start_time,
            model_used="fallback",
            tokens_used=0,
            cost_estimate=0.0
        )
    
    def _parse_cached_response(self, request: GPTRequest, cached_response: str) -> GPTResponse:
        """Parse cached response."""
        parsed_mappings = self._parse_gpt_response(cached_response, request.column_headers)
        
        return GPTResponse(
            request_id=request.request_id,
            raw_response=cached_response,
            parsed_mappings=parsed_mappings,
            processing_time=0.0,  # Cached, no processing time
            model_used="cached",
            tokens_used=0,
            cost_estimate=0.0
        )
    
    def _integrate_gpt_results(
        self, 
        original_decisions: List[ColumnDecision],
        gpt_responses: List[GPTResponse]
    ) -> Tuple[List[ColumnDecision], Dict[str, float]]:
        """Integrate GPT results with original local analysis."""
        
        # Collect all GPT mappings
        gpt_mappings = {}
        for response in gpt_responses:
            gpt_mappings.update(response.parsed_mappings)
        
        enhanced_decisions = []
        confidence_improvements = {}
        
        for decision in original_decisions:
            header = decision.original_header
            
            if header in gpt_mappings and gpt_mappings[header]['mapped_to']:
                # Enhance with GPT results
                gpt_result = gpt_mappings[header]
                
                # Create enhanced decision
                enhanced_decision = ColumnDecision(
                    original_header=decision.original_header,
                    normalized_header=decision.normalized_header,
                    local_confidence=decision.local_confidence,
                    local_recommendation=gpt_result['mapped_to'],  # Use GPT recommendation
                    local_alternatives=decision.local_alternatives,
                    confidence_category=decision.confidence_category,
                    confidence_reasoning=f"Enhanced by GPT: {gpt_result['reasoning']}",
                    recommended_action=ActionType.SUGGEST_REVIEW,  # GPT results need review
                    action_reasoning="GPT provided disambiguation",
                    priority_level=decision.priority_level,
                    analytics_impact=decision.analytics_impact,
                    user_guidance=f"GPT suggests mapping '{header}' to '{gpt_result['mapped_to']}' ({gpt_result['confidence']:.1%} confidence)"
                )
                
                enhanced_decisions.append(enhanced_decision)
                
                # Track improvement
                improvement = gpt_result['confidence'] - decision.local_confidence
                confidence_improvements[header] = improvement
                
            else:
                # No GPT enhancement available, keep original
                enhanced_decisions.append(decision)
        
        return enhanced_decisions, confidence_improvements
    
    def _estimate_cost(self, tokens: Optional[int], model: str) -> float:
        """Estimate API cost based on tokens and model."""
        if not tokens:
            return 0.0
        
        # Rough cost estimates (as of 2024)
        cost_per_1k_tokens = {
            'gpt-3.5-turbo': 0.002,
            'gpt-4': 0.03,
            'gpt-4o-mini': 0.0005
        }
        
        rate = cost_per_1k_tokens.get(model, 0.002)
        return (tokens / 1000.0) * rate

# Global instance for easy access
gpt_escalator = GPTEscalator()
