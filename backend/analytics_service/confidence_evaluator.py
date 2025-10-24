"""
Confidence Evaluator - Phase 4: Confidence Evaluation
Categorizes columns by confidence levels and determines appropriate actions

This module takes local analysis results and creates a structured decision pipeline
for the hybrid mapping system, determining which columns should be:
- Auto-mapped (high confidence)
- Suggested for review (medium confidence)  
- Sent to GPT (low confidence)
- Presented to user for manual confirmation
"""

from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

try:
    from .local_analyzer import LocalAnalysisResult, ColumnAnalysis
    from .tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from .file_preprocessor import FileMetadata
except ImportError:
    from local_analyzer import LocalAnalysisResult, ColumnAnalysis
    from tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config
    from file_preprocessor import FileMetadata

class ConfidenceCategory(Enum):
    """Confidence level categories for column mappings."""
    AUTO_MAP = "auto_map"           # ≥ 0.90: Auto-map silently
    SUGGESTED = "suggested"         # 0.70-0.89: Suggest mapping (optional review)
    UNCERTAIN = "uncertain"         # < 0.70: Require confirmation or GPT
    
class ActionType(Enum):
    """Available actions for column mappings."""
    AUTO_APPLY = "auto_apply"               # Apply mapping automatically
    SUGGEST_REVIEW = "suggest_review"       # Suggest but allow user review
    SEND_TO_GPT = "send_to_gpt"            # Escalate to GPT analysis
    USER_CONFIRMATION = "user_confirmation" # Require manual user input
    IGNORE_COLUMN = "ignore_column"         # Skip column (not needed for analytics)

@dataclass
class ColumnDecision:
    """Decision made for a single column mapping."""
    original_header: str
    normalized_header: str
    
    # Local analysis results
    local_confidence: float
    local_recommendation: Optional[str]
    local_alternatives: Dict[str, float]
    
    # Confidence categorization
    confidence_category: ConfidenceCategory
    confidence_reasoning: str
    
    # Action determination
    recommended_action: ActionType
    action_reasoning: str
    
    # Additional metadata
    priority_level: int  # 1=high, 2=medium, 3=low
    analytics_impact: List[str]  # Which analytics this column enables
    user_guidance: str  # Helpful message for user

@dataclass
class MappingStrategy:
    """Overall mapping strategy for the dataset."""
    total_columns: int
    
    # Confidence distribution
    auto_map_count: int
    suggested_count: int
    uncertain_count: int
    
    # Action plan
    auto_apply_columns: List[str]
    gpt_escalation_columns: List[str]
    user_review_columns: List[str]
    user_confirmation_columns: List[str]
    
    # Analytics readiness
    immediate_analytics: List[str]  # Analytics available with auto-mapped columns
    potential_analytics: List[str]  # Analytics possible after all mappings
    missing_for_analytics: Dict[str, List[str]]  # What's needed for each analytic
    
    # Cost and efficiency metrics
    estimated_gpt_cost_reduction: float  # Percentage of columns not sent to GPT
    estimated_processing_time: float     # Seconds
    user_interaction_required: bool

@dataclass
class EvaluationResult:
    """Complete confidence evaluation results."""
    file_metadata: FileMetadata
    local_analysis: LocalAnalysisResult
    column_decisions: List[ColumnDecision]
    mapping_strategy: MappingStrategy
    
    # Processing metadata
    evaluation_timestamp: str
    evaluator_version: str
    configuration_used: Dict[str, Any]

class ConfidenceEvaluator:
    """
    Confidence evaluator for the hybrid mapping pipeline.
    
    Analyzes local mapping results and creates a structured decision plan
    that balances automation, cost-efficiency, and user control.
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.canonical_schema = tanaw_schema
        self.evaluator_version = "1.0.0"
    
    def evaluate_confidence(
        self, 
        local_analysis: LocalAnalysisResult,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Evaluate confidence levels and determine mapping strategy.
        
        Args:
            local_analysis: Results from Phase 3 local analyzer
            user_preferences: Optional user preferences for decision making
            
        Returns:
            Complete evaluation with decisions and strategy
        """
        # Process each column decision
        column_decisions = []
        
        for analysis in local_analysis.column_analyses:
            decision = self._evaluate_column_confidence(analysis, user_preferences)
            column_decisions.append(decision)
        
        # Create overall mapping strategy
        mapping_strategy = self._create_mapping_strategy(column_decisions, local_analysis)
        
        # Create final result
        result = EvaluationResult(
            file_metadata=local_analysis.file_metadata,
            local_analysis=local_analysis,
            column_decisions=column_decisions,
            mapping_strategy=mapping_strategy,
            evaluation_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            evaluator_version=self.evaluator_version,
            configuration_used=self._get_config_snapshot()
        )
        
        return result
    
    def _evaluate_column_confidence(
        self, 
        analysis: ColumnAnalysis, 
        user_preferences: Optional[Dict[str, Any]]
    ) -> ColumnDecision:
        """Evaluate confidence and determine action for a single column."""
        
        # Categorize confidence
        confidence_category, confidence_reasoning = self._categorize_confidence(
            analysis.final_confidence
        )
        
        # Determine recommended action
        recommended_action, action_reasoning = self._determine_action(
            confidence_category, analysis, user_preferences
        )
        
        # Calculate priority level
        priority_level = self._calculate_priority(analysis, confidence_category)
        
        # Determine analytics impact
        analytics_impact = self._analyze_analytics_impact(analysis.recommended_mapping)
        
        # Generate user guidance
        user_guidance = self._generate_user_guidance(
            analysis, confidence_category, recommended_action
        )
        
        return ColumnDecision(
            original_header=analysis.original_header,
            normalized_header=analysis.normalized_header,
            local_confidence=analysis.final_confidence,
            local_recommendation=analysis.recommended_mapping,
            local_alternatives=analysis.final_scores,
            confidence_category=confidence_category,
            confidence_reasoning=confidence_reasoning,
            recommended_action=recommended_action,
            action_reasoning=action_reasoning,
            priority_level=priority_level,
            analytics_impact=analytics_impact,
            user_guidance=user_guidance
        )
    
    def _categorize_confidence(self, confidence: float) -> Tuple[ConfidenceCategory, str]:
        """Categorize confidence level and provide reasoning."""
        
        if confidence >= self.config.thresholds.auto_map:
            return (
                ConfidenceCategory.AUTO_MAP,
                f"High confidence ({confidence:.1%}) - strong agreement across all analysis methods"
            )
        elif confidence >= self.config.thresholds.suggested_min:
            return (
                ConfidenceCategory.SUGGESTED,
                f"Medium confidence ({confidence:.1%}) - good match but may benefit from review"
            )
        else:
            return (
                ConfidenceCategory.UNCERTAIN,
                f"Low confidence ({confidence:.1%}) - ambiguous mapping requiring additional analysis"
            )
    
    def _determine_action(
        self, 
        category: ConfidenceCategory, 
        analysis: ColumnAnalysis,
        user_preferences: Optional[Dict[str, Any]]
    ) -> Tuple[ActionType, str]:
        """Determine the recommended action based on confidence and context."""
        
        # Get user preferences
        prefs = user_preferences or {}
        auto_apply_threshold = prefs.get("auto_apply_threshold", self.config.thresholds.auto_map)
        prefer_gpt_over_user = prefs.get("prefer_gpt_over_user", True)
        
        if category == ConfidenceCategory.AUTO_MAP:
            if analysis.final_confidence >= auto_apply_threshold:
                return (
                    ActionType.AUTO_APPLY,
                    f"Confidence {analysis.final_confidence:.1%} exceeds auto-apply threshold"
                )
            else:
                return (
                    ActionType.SUGGEST_REVIEW,
                    "High confidence but below user's auto-apply threshold"
                )
                
        elif category == ConfidenceCategory.SUGGESTED:
            # Check if this column is critical for analytics
            if self._is_critical_for_analytics(analysis.recommended_mapping):
                if prefer_gpt_over_user:
                    return (
                        ActionType.SEND_TO_GPT,
                        "Medium confidence for critical column - GPT analysis recommended"
                    )
                else:
                    return (
                        ActionType.USER_CONFIRMATION,
                        "Medium confidence for critical column - user confirmation requested"
                    )
            else:
                return (
                    ActionType.SUGGEST_REVIEW,
                    "Medium confidence for non-critical column - suggest with review option"
                )
                
        else:  # UNCERTAIN
            # Always escalate uncertain columns
            if self._has_reasonable_alternatives(analysis.final_scores):
                return (
                    ActionType.SEND_TO_GPT,
                    "Low confidence with reasonable alternatives - GPT can disambiguate"
                )
            else:
                return (
                    ActionType.USER_CONFIRMATION,
                    "Low confidence with no clear alternatives - user input required"
                )
    
    def _calculate_priority(
        self, 
        analysis: ColumnAnalysis, 
        category: ConfidenceCategory
    ) -> int:
        """Calculate priority level (1=high, 2=medium, 3=low)."""
        
        # High priority: Critical for analytics or high confidence
        if (self._is_critical_for_analytics(analysis.recommended_mapping) or 
            category == ConfidenceCategory.AUTO_MAP):
            return 1
        
        # Medium priority: Suggested mappings
        elif category == ConfidenceCategory.SUGGESTED:
            return 2
        
        # Low priority: Uncertain mappings
        else:
            return 3
    
    def _analyze_analytics_impact(self, recommended_mapping: Optional[str]) -> List[str]:
        """Determine which analytics this column mapping enables."""
        if not recommended_mapping:
            return []
        
        enabled_analytics = []
        
        # Check each analytic type requirement
        for analytic_type, requirement in self.canonical_schema.analytic_requirements.items():
            for col_req in requirement.required_columns:
                if (col_req.canonical_type.value == recommended_mapping or 
                    recommended_mapping in [alt.value for alt in col_req.alternatives]):
                    enabled_analytics.append(analytic_type.value)
                    break
        
        return enabled_analytics
    
    def _generate_user_guidance(
        self, 
        analysis: ColumnAnalysis, 
        category: ConfidenceCategory,
        action: ActionType
    ) -> str:
        """Generate helpful guidance message for the user."""
        
        if action == ActionType.AUTO_APPLY:
            return f"Will automatically map '{analysis.original_header}' to '{analysis.recommended_mapping}' (high confidence)"
        
        elif action == ActionType.SUGGEST_REVIEW:
            alternatives = list(analysis.final_scores.keys())[:2]  # Top 2 alternatives
            alt_text = f" (alternatives: {', '.join(alternatives)})" if len(alternatives) > 1 else ""
            return f"Suggests mapping '{analysis.original_header}' to '{analysis.recommended_mapping}'{alt_text}"
        
        elif action == ActionType.SEND_TO_GPT:
            return f"Will send '{analysis.original_header}' to AI for analysis (ambiguous mapping)"
        
        elif action == ActionType.USER_CONFIRMATION:
            return f"Needs your decision for '{analysis.original_header}' - multiple possibilities"
        
        else:
            return f"Column '{analysis.original_header}' will be processed"
    
    def _create_mapping_strategy(
        self, 
        decisions: List[ColumnDecision], 
        local_analysis: LocalAnalysisResult
    ) -> MappingStrategy:
        """Create overall mapping strategy from individual decisions."""
        
        # Count by action type
        auto_apply = [d.original_header for d in decisions if d.recommended_action == ActionType.AUTO_APPLY]
        gpt_escalation = [d.original_header for d in decisions if d.recommended_action == ActionType.SEND_TO_GPT]
        user_review = [d.original_header for d in decisions if d.recommended_action == ActionType.SUGGEST_REVIEW]
        user_confirmation = [d.original_header for d in decisions if d.recommended_action == ActionType.USER_CONFIRMATION]
        
        # Count by confidence category
        auto_map_count = len([d for d in decisions if d.confidence_category == ConfidenceCategory.AUTO_MAP])
        suggested_count = len([d for d in decisions if d.confidence_category == ConfidenceCategory.SUGGESTED])
        uncertain_count = len([d for d in decisions if d.confidence_category == ConfidenceCategory.UNCERTAIN])
        
        # Analyze analytics readiness
        immediate_analytics, potential_analytics, missing_analytics = self._analyze_analytics_readiness(decisions)
        
        # Calculate metrics
        gpt_cost_reduction = (1 - len(gpt_escalation) / len(decisions)) * 100
        processing_time = self._estimate_processing_time(decisions)
        user_interaction = bool(user_review or user_confirmation)
        
        return MappingStrategy(
            total_columns=len(decisions),
            auto_map_count=auto_map_count,
            suggested_count=suggested_count,
            uncertain_count=uncertain_count,
            auto_apply_columns=auto_apply,
            gpt_escalation_columns=gpt_escalation,
            user_review_columns=user_review,
            user_confirmation_columns=user_confirmation,
            immediate_analytics=immediate_analytics,
            potential_analytics=potential_analytics,
            missing_for_analytics=missing_analytics,
            estimated_gpt_cost_reduction=gpt_cost_reduction,
            estimated_processing_time=processing_time,
            user_interaction_required=user_interaction
        )
    
    def _analyze_analytics_readiness(
        self, 
        decisions: List[ColumnDecision]
    ) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        """Analyze which analytics are immediately available vs potentially available."""
        
        # Get mappings from auto-apply decisions (immediate)
        immediate_mappings = {}
        for decision in decisions:
            if decision.recommended_action == ActionType.AUTO_APPLY and decision.local_recommendation:
                # Convert to CanonicalColumnType
                for canonical_type in CanonicalColumnType:
                    if canonical_type.value == decision.local_recommendation:
                        immediate_mappings[decision.original_header] = canonical_type
                        break
        
        # Get all potential mappings (including suggested/uncertain)
        potential_mappings = {}
        for decision in decisions:
            if decision.local_recommendation:
                for canonical_type in CanonicalColumnType:
                    if canonical_type.value == decision.local_recommendation:
                        potential_mappings[decision.original_header] = canonical_type
                        break
        
        # Check analytics feasibility
        immediate_feasible = self.canonical_schema.check_analytic_feasibility(immediate_mappings)
        potential_feasible = self.canonical_schema.check_analytic_feasibility(potential_mappings)
        
        immediate_analytics = [
            analytic.value for analytic, feasible in immediate_feasible.items() if feasible
        ]
        
        potential_analytics = [
            analytic.value for analytic, feasible in potential_feasible.items() if feasible
        ]
        
        # Find missing requirements for each analytic
        missing_analytics = {}
        for analytic_type, requirement in self.canonical_schema.analytic_requirements.items():
            if not potential_feasible.get(analytic_type, False):
                missing_cols = []
                for col_req in requirement.required_columns:
                    has_required = col_req.canonical_type in potential_mappings.values()
                    has_alternative = bool(col_req.alternatives & set(potential_mappings.values()))
                    
                    if col_req.is_required and not (has_required or has_alternative):
                        missing_cols.append(col_req.canonical_type.value)
                    elif not col_req.is_required and col_req.alternatives and not (has_required or has_alternative):
                        alternatives_list = [alt.value for alt in col_req.alternatives]
                        missing_cols.append(f"{col_req.canonical_type.value} OR {' OR '.join(alternatives_list)}")
                
                if missing_cols:
                    missing_analytics[analytic_type.value] = missing_cols
        
        return immediate_analytics, potential_analytics, missing_analytics
    
    def _is_critical_for_analytics(self, mapping: Optional[str]) -> bool:
        """Check if a mapping is critical for enabling analytics."""
        if not mapping:
            return False
        
        # Critical mappings are those required for multiple analytics
        critical_types = {
            CanonicalColumnType.DATE.value,    # Required for 3/5 analytics
            CanonicalColumnType.SALES.value,   # Required for 4/5 analytics
            CanonicalColumnType.AMOUNT.value   # Alternative for sales
        }
        
        return mapping in critical_types
    
    def _has_reasonable_alternatives(self, scores: Dict[str, float]) -> bool:
        """Check if there are reasonable alternative mappings."""
        if len(scores) < 2:
            return False
        
        sorted_scores = sorted(scores.values(), reverse=True)
        top_score = sorted_scores[0]
        second_score = sorted_scores[1]
        
        # Reasonable if second best is within 30% of top score
        return second_score >= top_score * 0.7
    
    def _estimate_processing_time(self, decisions: List[ColumnDecision]) -> float:
        """Estimate total processing time in seconds."""
        
        # Base processing time
        base_time = 0.1  # seconds
        
        # GPT escalation time (estimated)
        gpt_columns = len([d for d in decisions if d.recommended_action == ActionType.SEND_TO_GPT])
        gpt_time = gpt_columns * 2.0  # 2 seconds per GPT request (estimated)
        
        # User interaction time (estimated)
        user_columns = len([d for d in decisions if d.recommended_action in [ActionType.SUGGEST_REVIEW, ActionType.USER_CONFIRMATION]])
        user_time = user_columns * 5.0  # 5 seconds per user decision (estimated)
        
        return base_time + gpt_time + user_time
    
    def _get_config_snapshot(self) -> Dict[str, Any]:
        """Get snapshot of configuration used for evaluation."""
        return {
            "auto_map_threshold": self.config.thresholds.auto_map,
            "suggested_threshold": self.config.thresholds.suggested_min,
            "uncertain_threshold": self.config.thresholds.uncertain,
            "rule_weight": self.config.local_analyzer.rule_weight,
            "fuzzy_weight": self.config.local_analyzer.fuzzy_weight,
            "type_weight": self.config.local_analyzer.type_weight
        }
    
    def get_evaluation_summary(self, result: EvaluationResult) -> Dict[str, Any]:
        """Generate a user-friendly evaluation summary."""
        
        strategy = result.mapping_strategy
        
        summary = {
            "overview": {
                "total_columns": strategy.total_columns,
                "confidence_distribution": {
                    "auto_map": strategy.auto_map_count,
                    "suggested": strategy.suggested_count,
                    "uncertain": strategy.uncertain_count
                },
                "efficiency_metrics": {
                    "gpt_cost_reduction": f"{strategy.estimated_gpt_cost_reduction:.1f}%",
                    "processing_time": f"{strategy.estimated_processing_time:.1f}s",
                    "user_interaction_required": strategy.user_interaction_required
                }
            },
            "action_plan": {
                "auto_apply": len(strategy.auto_apply_columns),
                "gpt_analysis": len(strategy.gpt_escalation_columns),
                "user_review": len(strategy.user_review_columns),
                "user_confirmation": len(strategy.user_confirmation_columns)
            },
            "analytics_readiness": {
                "immediately_available": strategy.immediate_analytics,
                "potentially_available": strategy.potential_analytics,
                "missing_requirements": strategy.missing_for_analytics
            },
            "next_steps": self._generate_next_steps(strategy),
            "recommendations": self._generate_recommendations(result)
        }
        
        return summary
    
    def _generate_next_steps(self, strategy: MappingStrategy) -> List[Dict[str, Any]]:
        """Generate ordered list of next steps."""
        steps = []
        
        if strategy.auto_apply_columns:
            steps.append({
                "step": 1,
                "action": "auto_apply",
                "description": f"Auto-apply {len(strategy.auto_apply_columns)} high-confidence mappings",
                "columns": strategy.auto_apply_columns,
                "time_estimate": "< 1 second"
            })
        
        if strategy.gpt_escalation_columns:
            steps.append({
                "step": len(steps) + 1,
                "action": "gpt_analysis", 
                "description": f"Send {len(strategy.gpt_escalation_columns)} uncertain columns for AI analysis",
                "columns": strategy.gpt_escalation_columns,
                "time_estimate": f"~{len(strategy.gpt_escalation_columns) * 2} seconds"
            })
        
        if strategy.user_review_columns:
            steps.append({
                "step": len(steps) + 1,
                "action": "user_review",
                "description": f"Review {len(strategy.user_review_columns)} suggested mappings",
                "columns": strategy.user_review_columns,
                "time_estimate": "User-dependent"
            })
        
        if strategy.user_confirmation_columns:
            steps.append({
                "step": len(steps) + 1,
                "action": "user_confirmation",
                "description": f"Manually confirm {len(strategy.user_confirmation_columns)} ambiguous mappings",
                "columns": strategy.user_confirmation_columns,
                "time_estimate": "User-dependent"
            })
        
        return steps
    
    def _generate_recommendations(self, result: EvaluationResult) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        strategy = result.mapping_strategy
        
        # Efficiency recommendations
        if strategy.estimated_gpt_cost_reduction >= 70:
            recommendations.append("✅ Excellent cost efficiency - most mappings resolved locally")
        elif strategy.estimated_gpt_cost_reduction >= 50:
            recommendations.append("⚠️ Good cost efficiency - consider improving local rules for ambiguous columns")
        else:
            recommendations.append("❌ Low cost efficiency - many columns require external analysis")
        
        # Analytics recommendations
        if len(strategy.immediate_analytics) >= 3:
            recommendations.append("🎯 Strong analytics readiness - multiple analytics available immediately")
        elif strategy.potential_analytics:
            recommendations.append("📊 Good analytics potential - complete mappings to unlock more analytics")
        else:
            recommendations.append("📈 Limited analytics potential - consider adding key columns (Date, Sales, Product)")
        
        # User experience recommendations
        if not strategy.user_interaction_required:
            recommendations.append("🚀 Fully automated processing - no user interaction needed")
        elif len(strategy.user_review_columns + strategy.user_confirmation_columns) <= 3:
            recommendations.append("👍 Minimal user interaction required")
        else:
            recommendations.append("⏰ Significant user interaction needed - consider relaxing confidence thresholds")
        
        return recommendations

# Global instance for easy access
confidence_evaluator = ConfidenceEvaluator()
