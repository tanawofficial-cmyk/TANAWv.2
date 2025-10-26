# Analytics Service Cleanup Plan

## 🎯 Objective
Reduce deployment size by removing unused files from analytics_service folder.

## ✅ CORE FILES TO KEEP (22 Python files + config)

### Main Application
- `app_clean.py` - Main Flask API endpoint

### Core Analytics Modules (imported by app_clean.py)
- `robust_file_parser.py`
- `gpt_column_mapper.py`
- `config_manager.py`
- `domain_detector.py`
- `inventory_analytics.py`
- `finance_analytics.py`
- `customer_analytics.py`
- `narrative_insights.py`
- `conversational_insights.py`
- `anomaly_detector.py`
- `predictive_analytics.py`
- `data_profiler.py`
- `axis_resolver.py`
- `transformer.py`
- `chart_validator.py`
- `bar_chart_generator.py`
- `line_chart_generator.py`
- `semantic_detector.py`
- `sales_forecast_generator.py`
- `stock_forecast_generator.py`

### Configuration & Models
- `__init__.py`
- `config.yml`
- `requirements.txt`
- `analytics_type_classifier.pkl` (trained ML model)
- `analytics_vectorizer.pkl` (trained ML model)
- `tanaw_mapping_cache.db` (cache database)
- `tanaw_canonical_schema.py` (schema definitions)

### Potentially Needed (check imports)
- `gpt_config.py` (GPT configuration)
- `data_validator.py` (data validation)
- `data_cleaner.py` (data cleaning)
- `column_mapper.py` (column mapping)
- `visualization_engine.py` (chart generation)

## ❌ FILES TO DELETE

### Test Files (10+ files)
- `test_bar_charts.py`
- `test_data_processing.py`
- `test_frontend_integration.py`
- `test_gpt_mapping.py`
- `test_multi_domain.py`
- `test_sample.csv`
- `test_upload.py`

### Debug Files
- `debug_analytics.py`
- `debug_full_pipeline.py`

### Documentation Files (30+ .md files)
- `ANALYSIS_AND_FIXES.md`
- `AUTO_COMPUTE_SALES_FEATURE.md`
- `AVAILABLE_CHARTS_AND_ANALYTICS.md`
- `BAR_CHART_MAPPING_FIX.md`
- `CLEAN_ARCHITECTURE.md`
- `COMPREHENSIVE_COLUMN_PRIORITIZATION_FIX.md`
- `CONVERSATIONAL_INSIGHTS_DOCUMENTATION.md`
- `FALLBACK_HANDLING_SYSTEM.md`
- `FALLBACK_SYSTEM_DOCUMENTATION.md`
- `final_deployment_checklist.md`
- `FORMULA_IMPLEMENTATION_PLAN.md`
- `FORMULA_VERIFICATION_REPORT.md`
- `GPT_MAPPING_README.md`
- `IMPROVED_PROMPT_CHANGELOG.md`
- `INVENTORY_CHARTS_FIX.md`
- `INVENTORY_TURNOVER_FIX.md`
- `LABEL_VERIFICATION_REPORT.md`
- `LINE_CHART_IMPLEMENTATION.md`
- `MULTI_DOMAIN_BAR_CHARTS_COMPLETE.md`
- `NARRATIVE_INSIGHTS_FLOW.md`
- `OPENAI_SETUP_COMPLETE_GUIDE.md`
- `OPTIMIZED_MAPPING_UPDATE.md`
- `PREDICTIVE_ANALYTICS_DATA_REQUIREMENTS.md`
- `REGION_TO_LOCATION_CHANGES.md`
- `SAMPLE_OPENAI_PROMPT.md`
- `SEMANTIC_DETECTION_PLAN.md`
- `SERIES_AMBIGUITY_FIXES.md`

### Unused Python Files
- `app_enhanced.py` (not used, app_clean.py is active)
- `start_clean.py` (startup script)
- `analytics_activation.py`
- `analytics_config.py`
- `analytics_engine.py`
- `analytics_executor.py`
- `analytics_readiness_checker.py`
- `analytics_requirements.py`
- `chart_styling.py`
- `column_conflict_resolver.py`
- `confidence_evaluator.py`
- `data_transformer.py`
- `dataset_scanner.py`
- `deployment_guardrails.py`
- `descriptive_analytics.py`
- `enhanced_gpt_mapper.py`
- `error_handler.py`
- `fallback_column_mapper.py`
- `fallback_handler.py`
- `feedback_system.py`
- `file_preprocessor.py`
- `flexible_column_mapper.py`
- `gpt_escalation.py`
- `gpt_escalator.py`
- `header_normalizer.py`
- `hybrid_mapping_config.py`
- `knowledge_base.py`
- `local_analyzer.py`
- `mapping_merger.py`
- `observability_system.py`
- `semantic_column_mapper.py`
- `simplified_mapper.py`
- `universal_column_mapper.py`
- `user_confirmation.py`
- `ux_remediation.py`
- `value_analyzer.py`
- `visualization_generator.py`

### Folders
- `cache_backup_20251024_202354/` (old cache backup)
- `test_data/` (test files)
- `test_results/` (test outputs)
- `schemas/` (if not used)
- `__pycache__/` (Python cache, auto-regenerated)

### Other Files
- `env_example.txt`

## 📊 Expected Size Reduction
- Current: ~100+ files
- After cleanup: ~30 essential files
- **Size reduction: ~70% fewer files**

## ⚠️ Safety Notes
1. Keep backup before deleting (or use git)
2. Test system after cleanup
3. Keep .pkl model files (trained models)
4. Keep requirements.txt (dependency list)
5. Keep config.yml (configuration)

