"""
Phase 2: Header Normalization & Candidate Generation
Implements comprehensive header normalization and candidate generation with:
- Unicode normalization and ASCII conversion
- Exact alias lookup with local rules
- Fuzzy similarity matching with RapidFuzz
- SBERT semantic vector matching (optional)
- Failure modes and fallbacks
- Comprehensive observability
"""

import re
import unicodedata
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import warnings

# Try to import optional dependencies
try:
    from unidecode import unidecode
    UNIDECODE_AVAILABLE = True
except ImportError:
    UNIDECODE_AVAILABLE = False
    warnings.warn("unidecode not available. Install with: pip install unidecode")

try:
    from rapidfuzz import fuzz, process as fuzz_process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    warnings.warn("rapidfuzz not available. Install with: pip install rapidfuzz")

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    warnings.warn("sentence-transformers not available. Install with: pip install sentence-transformers")

# Import existing configuration
from config_manager import get_config

@dataclass
class HeaderCandidate:
    """Represents a candidate mapping for a normalized header."""
    canonical_type: str
    score: float
    source: str  # 'rule', 'fuzzy', 'semantic', 'fallback'
    reasoning: str
    confidence: float

@dataclass
class NormalizedHeader:
    """Represents a normalized header with original mapping."""
    original_header: str
    normalized_header: str
    candidates: List[HeaderCandidate]
    best_candidate: Optional[HeaderCandidate]
    processing_time_ms: float
    normalization_method: str

@dataclass
class HeaderNormalizationResult:
    """Results from header normalization and candidate generation."""
    normalized_headers: Dict[str, NormalizedHeader]
    processing_time_seconds: float
    metrics: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None

class HeaderNormalizer:
    """
    Phase 2: Header normalization and candidate generation system.
    
    Features:
    - Unicode normalization with ASCII conversion
    - Exact alias lookup with local rules
    - Fuzzy similarity matching
    - SBERT semantic matching (optional)
    - Failure modes and fallbacks
    - Comprehensive observability
    """
    
    def __init__(self, config=None):
        """Initialize header normalizer with configuration."""
        self.config = config or get_config()
        self.normalizer_version = "2.0.0"
        
        # Initialize local rules dictionary
        self.local_rules = self._build_local_rules()
        
        # Initialize fuzzy matching targets
        self.fuzzy_targets = self._prepare_fuzzy_targets()
        
        # Initialize semantic model (optional)
        self.semantic_model = None
        if SBERT_AVAILABLE:
            try:
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Header normalizer: SBERT semantic matching enabled")
            except Exception as e:
                print(f"⚠️ Header normalizer: SBERT initialization failed: {e}")
        
        # Metrics tracking
        self.metrics = {
            'headers_processed': 0,
            'rule_matches': 0,
            'fuzzy_matches': 0,
            'semantic_matches': 0,
            'fallback_matches': 0,
            'normalization_errors': 0,
            'processing_time_ms': 0.0
        }
    
    def normalize_headers(self, headers: List[str]) -> HeaderNormalizationResult:
        """
        Normalize headers and generate candidate mappings.
        
        Args:
            headers: List of original column headers
            
        Returns:
            HeaderNormalizationResult with normalized headers and candidates
        """
        start_time = datetime.now()
        
        try:
            normalized_headers = {}
            
            for header in headers:
                try:
                    normalized_header = self._normalize_single_header(header)
                    candidates = self._generate_candidates(normalized_header)
                    
                    # Find best candidate
                    best_candidate = self._select_best_candidate(candidates)
                    
                    normalized_headers[header] = NormalizedHeader(
                        original_header=header,
                        normalized_header=normalized_header,
                        candidates=candidates,
                        best_candidate=best_candidate,
                        processing_time_ms=0.0,  # Will be calculated per header
                        normalization_method="unicode_ascii"
                    )
                    
                    self.metrics['headers_processed'] += 1
                    
                except Exception as e:
                    print(f"⚠️ Error normalizing header '{header}': {e}")
                    self.metrics['normalization_errors'] += 1
                    
                    # Create fallback normalized header
                    normalized_headers[header] = NormalizedHeader(
                        original_header=header,
                        normalized_header=header.lower().strip(),
                        candidates=[],
                        best_candidate=None,
                        processing_time_ms=0.0,
                        normalization_method="fallback"
                    )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics['processing_time_ms'] = processing_time * 1000
            
            return HeaderNormalizationResult(
                normalized_headers=normalized_headers,
                processing_time_seconds=processing_time,
                metrics=self.metrics.copy(),
                success=True
            )
            
        except Exception as e:
            return HeaderNormalizationResult(
                normalized_headers={},
                processing_time_seconds=0.0,
                metrics=self.metrics.copy(),
                success=False,
                error_message=str(e)
            )
    
    def _normalize_single_header(self, header: str) -> str:
        """
        Normalize a single header using unicode normalization and ASCII conversion.
        
        Args:
            header: Original header string
            
        Returns:
            Normalized header string
        """
        try:
            # Step 1: Unicode normalization
            normalized = unicodedata.normalize('NFKD', header)
            
            # Step 2: ASCII conversion (if unidecode available)
            if UNIDECODE_AVAILABLE:
                normalized = unidecode(normalized)
            
            # Step 3: Lowercase conversion
            normalized = normalized.lower()
            
            # Step 4: Remove punctuation and extra spaces
            normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
            normalized = re.sub(r'\s+', ' ', normalized)     # Replace multiple spaces with single
            normalized = normalized.strip()                  # Remove leading/trailing spaces
            
            # Step 5: Replace underscores and dots with spaces
            normalized = normalized.replace('_', ' ').replace('.', '')
            
            return normalized
            
        except Exception as e:
            print(f"⚠️ Error normalizing header '{header}': {e}")
            # Fallback to simple normalization
            return header.lower().strip().replace('_', ' ').replace('.', '')
    
    def _generate_candidates(self, normalized_header: str) -> List[HeaderCandidate]:
        """
        Generate candidate mappings for a normalized header.
        
        Args:
            normalized_header: Normalized header string
            
        Returns:
            List of HeaderCandidate objects
        """
        candidates = []
        
        # Step 1: Exact alias lookup (local rules)
        rule_candidates = self._exact_alias_lookup(normalized_header)
        candidates.extend(rule_candidates)
        
        # Step 2: Fuzzy similarity matching
        if RAPIDFUZZ_AVAILABLE:
            fuzzy_candidates = self._fuzzy_similarity_matching(normalized_header)
            candidates.extend(fuzzy_candidates)
        
        # Step 3: SBERT semantic matching (optional)
        if self.semantic_model:
            semantic_candidates = self._semantic_vector_matching(normalized_header)
            candidates.extend(semantic_candidates)
        
        # Step 4: Fallback matching for concatenated headers
        if not candidates:
            fallback_candidates = self._fallback_matching(normalized_header)
            candidates.extend(fallback_candidates)
        
        # Sort candidates by score (descending)
        candidates.sort(key=lambda x: x.score, reverse=True)
        
        return candidates
    
    def _exact_alias_lookup(self, normalized_header: str) -> List[HeaderCandidate]:
        """Exact alias lookup using local rules."""
        candidates = []
        
        for canonical_type, aliases in self.local_rules.items():
            if normalized_header in aliases:
                candidates.append(HeaderCandidate(
                    canonical_type=canonical_type,
                    score=1.0,
                    source='rule',
                    reasoning=f"Exact match in local rules: '{normalized_header}'",
                    confidence=100.0
                ))
                self.metrics['rule_matches'] += 1
        
        return candidates
    
    def _fuzzy_similarity_matching(self, normalized_header: str) -> List[HeaderCandidate]:
        """Fuzzy similarity matching using RapidFuzz."""
        candidates = []
        
        try:
            # Use token sort ratio for better matching
            results = fuzz_process.extract(
                normalized_header,
                self.fuzzy_targets,
                scorer=fuzz.token_sort_ratio,
                limit=5
            )
            
            for target, score in results:
                if score >= 75:  # Threshold for candidate inclusion
                    canonical_type = self._get_canonical_type_from_target(target)
                    candidates.append(HeaderCandidate(
                        canonical_type=canonical_type,
                        score=score / 100.0,  # Convert to 0-1 scale
                        source='fuzzy',
                        reasoning=f"Fuzzy match: {score}% similarity to '{target}'",
                        confidence=score
                    ))
                    self.metrics['fuzzy_matches'] += 1
        
        except Exception as e:
            print(f"⚠️ Fuzzy matching error: {e}")
            # Fallback to simple substring matching
            candidates.extend(self._simple_substring_matching(normalized_header))
        
        return candidates
    
    def _semantic_vector_matching(self, normalized_header: str) -> List[HeaderCandidate]:
        """SBERT semantic vector matching for tricky headers."""
        candidates = []
        
        try:
            # Get header embedding
            header_embedding = self.semantic_model.encode([normalized_header])
            
            # Compare with canonical embeddings
            best_match = None
            best_score = 0.0
            
            for canonical_type, canonical_embedding in self._get_canonical_embeddings().items():
                # Calculate cosine similarity
                similarity = self._cosine_similarity(header_embedding[0], canonical_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = canonical_type
            
            if best_match and best_score >= 0.7:  # Semantic similarity threshold
                candidates.append(HeaderCandidate(
                    canonical_type=best_match,
                    score=best_score,
                    source='semantic',
                    reasoning=f"Semantic similarity: {best_score:.2f} to '{best_match}'",
                    confidence=best_score * 100
                ))
                self.metrics['semantic_matches'] += 1
        
        except Exception as e:
            print(f"⚠️ Semantic matching error: {e}")
        
        return candidates
    
    def _fallback_matching(self, normalized_header: str) -> List[HeaderCandidate]:
        """Fallback matching for concatenated headers."""
        candidates = []
        
        # Check for concatenated headers (region_and_sales_rep)
        delimiters = ['_', 'and', '&', '|']
        parts = []
        
        for delimiter in delimiters:
            if delimiter in normalized_header:
                parts = normalized_header.split(delimiter)
                break
        
        if parts:
            # Map each part separately
            for part in parts:
                part = part.strip()
                if len(part) > 2:  # Minimum length for meaningful matching
                    part_candidates = self._exact_alias_lookup(part)
                    candidates.extend(part_candidates)
        
        # Simple prefix/suffix matching as last resort
        if not candidates:
            candidates.extend(self._simple_substring_matching(normalized_header))
            self.metrics['fallback_matches'] += 1
        
        return candidates
    
    def _simple_substring_matching(self, normalized_header: str) -> List[HeaderCandidate]:
        """Simple substring matching as fallback."""
        candidates = []
        
        for canonical_type, aliases in self.local_rules.items():
            for alias in aliases:
                if alias in normalized_header or normalized_header in alias:
                    # Calculate simple similarity
                    similarity = len(alias) / max(len(normalized_header), len(alias))
                    
                    if similarity >= 0.5:
                        candidates.append(HeaderCandidate(
                            canonical_type=canonical_type,
                            score=similarity,
                            source='fallback',
                            reasoning=f"Substring match: '{alias}' in '{normalized_header}'",
                            confidence=similarity * 100
                        ))
        
        return candidates
    
    def _select_best_candidate(self, candidates: List[HeaderCandidate]) -> Optional[HeaderCandidate]:
        """Select the best candidate from the list."""
        if not candidates:
            return None
        
        # Sort by score and return the best one
        return max(candidates, key=lambda x: x.score)
    
    def _build_local_rules(self) -> Dict[str, List[str]]:
        """Build local rules dictionary for exact alias lookup."""
        return {
            'Date': [
                'date', 'time', 'timestamp', 'datetime', 'created_at', 'updated_at',
                'order_date', 'transaction_date', 'purchase_date', 'sale_date',
                'invoice_date', 'period', 'day', 'month', 'year', 'dt'
            ],
            'Sales': [
                'sales', 'revenue', 'income', 'earnings', 'turnover', 'gross_sales',
                'net_sales', 'total_sales', 'sale_amount', 'sales_amount'
            ],
            'Amount': [
                'amount', 'amt', 'total', 'total_amount', 'price', 'value',
                'cost', 'total_price', 'sum', 'grand_total'
            ],
            'Product': [
                'product', 'item', 'sku', 'product_name', 'item_name', 'product_id',
                'item_id', 'goods', 'merchandise', 'article', 'product_code', 'prod'
            ],
            'Quantity': [
                'quantity', 'qty', 'units', 'volume', 'count', 'pieces', 'items',
                'number', 'amount_sold', 'units_sold', 'sold', 'stock'
            ],
            'Region': [
                'region', 'area', 'territory', 'zone', 'district', 'location',
                'city', 'state', 'country', 'province', 'market', 'geo'
            ]
        }
    
    def _prepare_fuzzy_targets(self) -> List[str]:
        """Prepare targets for fuzzy matching."""
        targets = []
        for aliases in self.local_rules.values():
            targets.extend(aliases)
        return targets
    
    def _get_canonical_type_from_target(self, target: str) -> str:
        """Get canonical type from fuzzy target."""
        for canonical_type, aliases in self.local_rules.items():
            if target in aliases:
                return canonical_type
        return 'Unknown'
    
    def _get_canonical_embeddings(self) -> Dict[str, Any]:
        """Get precomputed canonical embeddings for semantic matching."""
        # This would be implemented with precomputed embeddings
        # For now, return empty dict
        return {}
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset metrics."""
        self.metrics = {
            'headers_processed': 0,
            'rule_matches': 0,
            'fuzzy_matches': 0,
            'semantic_matches': 0,
            'fallback_matches': 0,
            'normalization_errors': 0,
            'processing_time_ms': 0.0
        }
    
    def emit_metrics(self):
        """Emit metrics for observability."""
        try:
            metrics = {
                "header.candidates_count": sum(len(nh.candidates) for nh in self.normalized_headers.values()) if hasattr(self, 'normalized_headers') else 0,
                "header.rule_matches": self.metrics['rule_matches'],
                "header.fuzzy_matches": self.metrics['fuzzy_matches'],
                "header.semantic_matches": self.metrics['semantic_matches'],
                "header.fallback_matches": self.metrics['fallback_matches'],
                "header.normalization_errors": self.metrics['normalization_errors'],
                "header.processing_time_ms": self.metrics['processing_time_ms'],
                "header.success_rate": (self.metrics['headers_processed'] - self.metrics['normalization_errors']) / max(self.metrics['headers_processed'], 1) * 100
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Header normalizer metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting header metrics: {e}")
            return {"header.metrics_error": str(e)}

# Global normalizer instance
header_normalizer = HeaderNormalizer()

def normalize_headers(headers: List[str]) -> HeaderNormalizationResult:
    """
    Convenience function to normalize headers and generate candidates.
    
    Args:
        headers: List of original column headers
        
    Returns:
        HeaderNormalizationResult with normalized headers and candidates
    """
    return header_normalizer.normalize_headers(headers)

if __name__ == "__main__":
    # Test the header normalizer
    print("🧪 Testing Header Normalizer")
    print("=" * 50)
    
    test_headers = [
        "Transaction_Date",
        "Sales_Amount", 
        "Product_ID",
        "Customer_Region",
        "Quantity_Sold",
        "Revenue",
        "Item_Name",
        "Location"
    ]
    
    result = normalize_headers(test_headers)
    
    if result.success:
        print(f"✅ Successfully processed {len(result.normalized_headers)} headers")
        print(f"⏱️ Processing time: {result.processing_time_seconds:.3f}s")
        
        for original, normalized in result.normalized_headers.items():
            print(f"\n📝 {original} → {normalized.normalized_header}")
            if normalized.best_candidate:
                print(f"   🎯 Best: {normalized.best_candidate.canonical_type} ({normalized.best_candidate.confidence:.1f}%)")
                print(f"   📊 Source: {normalized.best_candidate.source}")
            else:
                print(f"   ❌ No candidates found")
    else:
        print(f"❌ Error: {result.error_message}")
