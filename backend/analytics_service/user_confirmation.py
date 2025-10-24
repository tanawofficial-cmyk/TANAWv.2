"""
User Confirmation - Phase 6: Dropdown User Confirmation
Interactive UI for manual column mapping when both local and GPT are uncertain

This module handles:
- Intelligent dropdown generation with top suggestions
- User interaction simulation and validation
- Integration of user selections back into the pipeline
- Analytics impact preview
- Mapping confirmation and storage
"""

from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

try:
    from .gpt_escalator import GPTEscalationResult
    from .confidence_evaluator import EvaluationResult, ColumnDecision, ActionType
    from .tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from .hybrid_mapping_config import HybridMappingConfig, hybrid_config
except ImportError:
    from gpt_escalator import GPTEscalationResult
    from confidence_evaluator import EvaluationResult, ColumnDecision, ActionType
    from tanaw_canonical_schema import CanonicalColumnType, AnalyticType, tanaw_schema
    from hybrid_mapping_config import HybridMappingConfig, hybrid_config

class UserAction(Enum):
    """User actions for column mapping."""
    SELECT_MAPPING = "select_mapping"
    IGNORE_COLUMN = "ignore_column"
    REQUEST_HELP = "request_help"
    SKIP_FOR_NOW = "skip_for_now"

@dataclass
class DropdownOption:
    """Represents a single dropdown option."""
    canonical_type: str
    display_name: str
    confidence: float
    source: str  # 'local', 'gpt', 'combined'
    reasoning: str
    analytics_impact: List[str]
    is_recommended: bool

@dataclass
class DropdownConfiguration:
    """Configuration for a single column dropdown."""
    original_header: str
    normalized_header: str
    
    # Current best suggestions
    top_options: List[DropdownOption]
    ignore_option: DropdownOption
    
    # Context information
    current_confidence: float
    data_type_hint: str
    sample_patterns: List[str]
    
    # User guidance
    guidance_text: str
    help_text: str
    priority_level: int
    
    # Analytics context
    analytics_enabled_by_mapping: Dict[str, List[str]]  # mapping -> analytics list
    critical_for_analytics: bool

@dataclass
class UserSelection:
    """Represents a user's selection for a column."""
    original_header: str
    selected_mapping: Optional[str]  # None if ignored
    user_action: UserAction
    confidence_override: Optional[float]  # User can adjust confidence
    user_notes: Optional[str]
    selection_timestamp: str

@dataclass
class UserConfirmationSession:
    """Manages a complete user confirmation session."""
    session_id: str
    escalation_result: GPTEscalationResult
    dropdown_configurations: List[DropdownConfiguration]
    
    # User selections
    user_selections: List[UserSelection]
    completed_columns: Set[str]
    remaining_columns: Set[str]
    
    # Session metadata
    session_started: str
    last_activity: str
    estimated_time_remaining: float
    
    # Final results
    final_mappings: Dict[str, str]  # column -> canonical_type
    analytics_preview: Dict[str, Any]

class UserConfirmationEngine:
    """
    User confirmation engine for the hybrid mapping pipeline.
    
    Features:
    - Intelligent dropdown generation with analytics context
    - User-friendly interface simulation
    - Smart prioritization and guidance
    - Real-time analytics impact preview
    - Confirmation validation and integration
    """
    
    def __init__(self, config: Optional[HybridMappingConfig] = None):
        self.config = config or hybrid_config
        self.canonical_schema = tanaw_schema
        self.engine_version = "1.0.0"
    
    def create_confirmation_session(
        self, 
        escalation_result: GPTEscalationResult,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> UserConfirmationSession:
        """
        Create user confirmation session with dropdown configurations.
        
        Args:
            escalation_result: Results from Phase 5 GPT escalation
            user_preferences: Optional user preferences for UI behavior
            
        Returns:
            Complete confirmation session ready for user interaction
        """
        
        # Identify columns needing user confirmation
        confirmation_columns = [
            decision for decision in escalation_result.enhanced_decisions
            if decision.recommended_action in [ActionType.USER_CONFIRMATION, ActionType.SUGGEST_REVIEW]
        ]
        
        if not confirmation_columns:
            # No user confirmation needed
            return self._create_empty_session(escalation_result)
        
        print(f"🎮 Creating user confirmation session for {len(confirmation_columns)} columns...")
        
        # Generate dropdown configurations
        dropdown_configs = []
        for decision in confirmation_columns:
            config = self._create_dropdown_configuration(decision, escalation_result)
            dropdown_configs.append(config)
        
        # Sort by priority
        dropdown_configs.sort(key=lambda x: (x.priority_level, not x.critical_for_analytics, x.original_header))
        
        # Create session
        session = UserConfirmationSession(
            session_id=self._generate_session_id(),
            escalation_result=escalation_result,
            dropdown_configurations=dropdown_configs,
            user_selections=[],
            completed_columns=set(),
            remaining_columns={config.original_header for config in dropdown_configs},
            session_started=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            last_activity=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            estimated_time_remaining=self._estimate_session_time(dropdown_configs),
            final_mappings={},
            analytics_preview={}
        )
        
        return session
    
    def _create_dropdown_configuration(
        self, 
        decision: ColumnDecision, 
        escalation_result: GPTEscalationResult
    ) -> DropdownConfiguration:
        """Create dropdown configuration for a single column."""
        
        # Gather all available options from different sources
        all_options = []
        
        # Add local analysis options
        if decision.local_alternatives:
            for canonical_type, confidence in decision.local_alternatives.items():
                if confidence > 0.3:  # Only include reasonable options
                    option = DropdownOption(
                        canonical_type=canonical_type,
                        display_name=self._get_display_name(canonical_type),
                        confidence=confidence,
                        source="local",
                        reasoning=f"Local analysis match ({confidence:.1%} confidence)",
                        analytics_impact=self._get_analytics_impact(canonical_type),
                        is_recommended=(canonical_type == decision.local_recommendation)
                    )
                    all_options.append(option)
        
        # Add GPT suggestions if available
        gpt_mappings = self._extract_gpt_mappings_for_column(
            decision.original_header, escalation_result
        )
        
        for mapping_info in gpt_mappings:
            if mapping_info['mapped_to'] and mapping_info['confidence'] > 0.5:
                option = DropdownOption(
                    canonical_type=mapping_info['mapped_to'],
                    display_name=self._get_display_name(mapping_info['mapped_to']),
                    confidence=mapping_info['confidence'],
                    source="gpt",
                    reasoning=f"AI analysis: {mapping_info['reasoning']}",
                    analytics_impact=self._get_analytics_impact(mapping_info['mapped_to']),
                    is_recommended=True  # GPT suggestions are generally recommended
                )
                all_options.append(option)
        
        # Merge and deduplicate options
        merged_options = self._merge_duplicate_options(all_options)
        
        # Select top options
        top_options = sorted(merged_options, key=lambda x: (-x.confidence, -x.is_recommended))[:3]
        
        # Create ignore option
        ignore_option = DropdownOption(
            canonical_type="IGNORE",
            display_name="Ignore this column",
            confidence=1.0,
            source="system",
            reasoning="Column not needed for analytics",
            analytics_impact=[],
            is_recommended=False
        )
        
        # Generate guidance
        guidance_text = self._generate_guidance_text(decision, top_options)
        help_text = self._generate_help_text(decision)
        
        # Determine analytics impact
        analytics_impact_by_mapping = {}
        for option in top_options:
            analytics_impact_by_mapping[option.canonical_type] = option.analytics_impact
        
        # Get file metadata for additional context
        file_metadata = escalation_result.original_evaluation.file_metadata
        data_type_hint = file_metadata.column_data_types.get(decision.original_header, "unknown")
        sample_patterns = file_metadata.sample_values.get(decision.original_header, [])
        
        return DropdownConfiguration(
            original_header=decision.original_header,
            normalized_header=decision.normalized_header,
            top_options=top_options,
            ignore_option=ignore_option,
            current_confidence=decision.local_confidence,
            data_type_hint=data_type_hint,
            sample_patterns=sample_patterns,
            guidance_text=guidance_text,
            help_text=help_text,
            priority_level=decision.priority_level,
            analytics_enabled_by_mapping=analytics_impact_by_mapping,
            critical_for_analytics=decision.priority_level == 1
        )
    
    def simulate_user_interaction(
        self, 
        session: UserConfirmationSession,
        automated_selections: Optional[Dict[str, str]] = None
    ) -> UserConfirmationSession:
        """
        Simulate user interaction with confirmation dropdowns.
        
        In a real application, this would be replaced by actual UI components.
        For testing, we simulate intelligent user choices.
        
        Args:
            session: User confirmation session
            automated_selections: Optional pre-defined selections for testing
            
        Returns:
            Updated session with user selections
        """
        
        print(f"\n🎮 USER CONFIRMATION SIMULATION")
        print("=" * 70)
        print(f"Session: {session.session_id}")
        print(f"Columns to confirm: {len(session.dropdown_configurations)}")
        print(f"Estimated time: {session.estimated_time_remaining:.1f} minutes")
        
        for config in session.dropdown_configurations:
            print(f"\n📋 Column: {config.original_header}")
            print(f"   Data Type: {config.data_type_hint}")
            if config.sample_patterns:
                print(f"   Sample Patterns: {', '.join(config.sample_patterns[:3])}")
            print(f"   Priority: {config.priority_level} | Critical: {config.critical_for_analytics}")
            print(f"   Guidance: {config.guidance_text}")
            
            print(f"\n   Available Options:")
            for i, option in enumerate(config.top_options, 1):
                rec_marker = " [RECOMMENDED]" if option.is_recommended else ""
                impact = f" → Enables: {', '.join(option.analytics_impact)}" if option.analytics_impact else ""
                print(f"   {i}. {option.display_name} ({option.confidence:.1%}){rec_marker}")
                print(f"      {option.reasoning}{impact}")
            
            print(f"   {len(config.top_options)+1}. {config.ignore_option.display_name}")
            
            # Simulate user choice
            if automated_selections and config.original_header in automated_selections:
                selected_mapping = automated_selections[config.original_header]
                print(f"   👤 Automated selection: {selected_mapping}")
            else:
                selected_mapping = self._simulate_smart_user_choice(config)
                print(f"   🤖 Simulated selection: {selected_mapping}")
            
            # Create user selection
            user_selection = UserSelection(
                original_header=config.original_header,
                selected_mapping=selected_mapping if selected_mapping != "IGNORE" else None,
                user_action=UserAction.IGNORE_COLUMN if selected_mapping == "IGNORE" else UserAction.SELECT_MAPPING,
                confidence_override=None,
                user_notes=None,
                selection_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            session.user_selections.append(user_selection)
            session.completed_columns.add(config.original_header)
            session.remaining_columns.discard(config.original_header)
        
        # Update session metadata
        session.last_activity = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.estimated_time_remaining = 0.0
        
        # Generate final mappings
        session.final_mappings = self._generate_final_mappings(session)
        
        # Generate analytics preview
        session.analytics_preview = self._generate_analytics_preview(session)
        
        print(f"\n✅ User confirmation session completed!")
        print(f"   Final mappings: {len(session.final_mappings)}")
        print(f"   Ignored columns: {len([s for s in session.user_selections if s.user_action == UserAction.IGNORE_COLUMN])}")
        
        return session
    
    def _simulate_smart_user_choice(self, config: DropdownConfiguration) -> str:
        """Simulate intelligent user choice based on context."""
        
        # If there's a highly confident option, choose it
        for option in config.top_options:
            if option.confidence >= 0.80 and option.is_recommended:
                return option.canonical_type
        
        # If there's an option that enables multiple analytics, prefer it
        best_analytics_option = None
        max_analytics_count = 0
        
        for option in config.top_options:
            analytics_count = len(option.analytics_impact)
            if analytics_count > max_analytics_count:
                max_analytics_count = analytics_count
                best_analytics_option = option
        
        if best_analytics_option and max_analytics_count >= 2:
            return best_analytics_option.canonical_type
        
        # If it's not critical and confidence is low, ignore
        if not config.critical_for_analytics and config.current_confidence < 0.5:
            return "IGNORE"
        
        # Default to first (highest confidence) option
        if config.top_options:
            return config.top_options[0].canonical_type
        
        # Fallback to ignore
        return "IGNORE"
    
    def _merge_duplicate_options(self, options: List[DropdownOption]) -> List[DropdownOption]:
        """Merge duplicate options from different sources."""
        merged = {}
        
        for option in options:
            key = option.canonical_type
            
            if key not in merged:
                merged[key] = option
            else:
                # Combine information from multiple sources
                existing = merged[key]
                
                # Use higher confidence
                if option.confidence > existing.confidence:
                    existing.confidence = option.confidence
                
                # Combine sources
                if option.source not in existing.source:
                    existing.source = f"{existing.source}+{option.source}"
                
                # Combine reasoning
                if option.reasoning not in existing.reasoning:
                    existing.reasoning = f"{existing.reasoning}; {option.reasoning}"
                
                # Mark as recommended if either source recommends
                existing.is_recommended = existing.is_recommended or option.is_recommended
        
        return list(merged.values())
    
    def _extract_gpt_mappings_for_column(
        self, 
        column_header: str, 
        escalation_result: GPTEscalationResult
    ) -> List[Dict[str, Any]]:
        """Extract GPT mappings for a specific column."""
        gpt_mappings = []
        
        for response in escalation_result.gpt_responses:
            if column_header in response.parsed_mappings:
                gpt_mappings.append(response.parsed_mappings[column_header])
        
        return gpt_mappings
    
    def _get_display_name(self, canonical_type: str) -> str:
        """Get user-friendly display name for canonical type."""
        display_names = {
            "Date": "📅 Date/Time",
            "Sales": "💰 Sales Amount", 
            "Amount": "💵 Monetary Amount",
            "Product": "📦 Product/Item",
            "Quantity": "🔢 Quantity/Count",
            "Region": "🌍 Region/Location",
            "Customer": "👤 Customer",
            "Transaction_ID": "🔖 Transaction ID"
        }
        
        return display_names.get(canonical_type, canonical_type)
    
    def _get_analytics_impact(self, canonical_type: str) -> List[str]:
        """Get list of analytics enabled by this canonical type."""
        enabled_analytics = []
        
        for analytic_type, requirement in self.canonical_schema.analytic_requirements.items():
            for col_req in requirement.required_columns:
                if (col_req.canonical_type.value == canonical_type or 
                    canonical_type in [alt.value for alt in col_req.alternatives]):
                    enabled_analytics.append(analytic_type.value.replace('_', ' ').title())
                    break
        
        return enabled_analytics
    
    def _generate_guidance_text(self, decision: ColumnDecision, top_options: List[DropdownOption]) -> str:
        """Generate helpful guidance text for the user."""
        
        if decision.priority_level == 1:
            guidance = f"🔥 High Priority: '{decision.original_header}' is important for analytics."
        elif decision.priority_level == 2:
            guidance = f"📊 Medium Priority: '{decision.original_header}' would enhance your analytics."
        else:
            guidance = f"💡 Optional: '{decision.original_header}' could provide additional insights."
        
        if top_options:
            best_option = top_options[0]
            if best_option.confidence >= 0.8:
                guidance += f" We're confident this is '{best_option.display_name}'."
            elif best_option.confidence >= 0.6:
                guidance += f" This likely represents '{best_option.display_name}'."
            else:
                guidance += f" Please help us identify what this represents."
        
        return guidance
    
    def _generate_help_text(self, decision: ColumnDecision) -> str:
        """Generate detailed help text."""
        
        help_parts = []
        
        # Data type context
        if hasattr(decision, 'data_type_hint'):
            help_parts.append(f"Data type appears to be {decision.data_type_hint}")
        
        # Analytics context
        if decision.analytics_impact:
            analytics_list = ', '.join(decision.analytics_impact)
            help_parts.append(f"Could enable: {analytics_list}")
        
        # Confidence context
        if decision.local_confidence:
            help_parts.append(f"Local analysis confidence: {decision.local_confidence:.1%}")
        
        return " | ".join(help_parts) if help_parts else "No additional context available"
    
    def _generate_final_mappings(self, session: UserConfirmationSession) -> Dict[str, str]:
        """Generate final column mappings from user selections."""
        final_mappings = {}
        
        # Start with auto-applied mappings from original evaluation
        for decision in session.escalation_result.original_evaluation.column_decisions:
            if decision.recommended_action == ActionType.AUTO_APPLY and decision.local_recommendation:
                final_mappings[decision.original_header] = decision.local_recommendation
        
        # Add user-confirmed mappings
        for selection in session.user_selections:
            if selection.selected_mapping:
                final_mappings[selection.original_header] = selection.selected_mapping
        
        return final_mappings
    
    def _generate_analytics_preview(self, session: UserConfirmationSession) -> Dict[str, Any]:
        """Generate analytics preview based on final mappings."""
        
        # Convert to canonical types for schema checking
        canonical_mappings = {}
        for column, mapping in session.final_mappings.items():
            for canonical_type in CanonicalColumnType:
                if canonical_type.value == mapping:
                    canonical_mappings[column] = canonical_type
                    break
        
        # Check analytics feasibility
        feasible_analytics = self.canonical_schema.check_analytic_feasibility(canonical_mappings)
        
        # Get analytics summary
        analytics_summary = self.canonical_schema.get_analytics_summary(canonical_mappings)
        
        return {
            "feasible_analytics": {
                analytic.value: feasible 
                for analytic, feasible in feasible_analytics.items()
            },
            "analytics_summary": analytics_summary,
            "total_mapped_columns": len(session.final_mappings),
            "analytics_enabled": len([a for a in feasible_analytics.values() if a])
        }
    
    def _create_empty_session(self, escalation_result: GPTEscalationResult) -> UserConfirmationSession:
        """Create empty session when no user confirmation needed."""
        return UserConfirmationSession(
            session_id=self._generate_session_id(),
            escalation_result=escalation_result,
            dropdown_configurations=[],
            user_selections=[],
            completed_columns=set(),
            remaining_columns=set(),
            session_started=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            last_activity=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            estimated_time_remaining=0.0,
            final_mappings={},
            analytics_preview={}
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import hashlib
        import time
        return hashlib.md5(f"session_{time.time()}".encode()).hexdigest()[:12]
    
    def _estimate_session_time(self, dropdown_configs: List[DropdownConfiguration]) -> float:
        """Estimate time needed for user confirmation in minutes."""
        
        # Base time per column
        base_time = 0.5  # 30 seconds per column
        
        # Additional time for complex columns
        complex_time = 0
        for config in dropdown_configs:
            if config.critical_for_analytics:
                complex_time += 0.5  # Extra 30 seconds for critical columns
            if len(config.top_options) < 2:
                complex_time += 0.3  # Extra time when few options
        
        return base_time * len(dropdown_configs) + complex_time
    
    def get_confirmation_summary(self, session: UserConfirmationSession) -> Dict[str, Any]:
        """Generate user-friendly confirmation summary."""
        
        selections_by_action = {}
        for action in UserAction:
            selections_by_action[action.value] = [
                s.original_header for s in session.user_selections 
                if s.user_action == action
            ]
        
        return {
            "session_info": {
                "session_id": session.session_id,
                "started": session.session_started,
                "completed": session.last_activity,
                "columns_processed": len(session.completed_columns)
            },
            "user_selections": selections_by_action,
            "final_mappings": session.final_mappings,
            "analytics_preview": session.analytics_preview,
            "efficiency_metrics": {
                "total_columns_in_file": len(session.escalation_result.original_evaluation.column_decisions),
                "user_confirmations_needed": len(session.dropdown_configurations),
                "final_mapped_columns": len(session.final_mappings),
                "confirmation_efficiency": f"{(1 - len(session.dropdown_configurations) / len(session.escalation_result.original_evaluation.column_decisions)) * 100:.1f}%"
            }
        }

# Global instance for easy access
user_confirmation_engine = UserConfirmationEngine()
