"""
Configuration Manager for TANAW
Centralized configuration loading from environment variables and .env files

This module handles:
- Loading configuration from .env files
- Environment variable management
- API key validation
- Configuration validation and defaults
- Secure credential handling
- Phase 0: Global config & conventions implementation
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import warnings

# Try to import python-dotenv for .env file support
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    warnings.warn("python-dotenv not installed. Using environment variables only.")

@dataclass
class FileProcessingConfig:
    """File processing configuration for Phase 1."""
    max_file_size_mb: int
    sample_rows_limit: int
    sample_min: int
    max_columns_per_gpt: int
    encoding_fallbacks: List[str]
    
@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: Optional[str]
    model: str
    fallback_model: str
    max_tokens: int
    temperature: float
    timeout_seconds: int
    max_retries: int
    enabled: bool
    
    def is_configured(self) -> bool:
        """Check if OpenAI is properly configured."""
        return self.enabled and bool(self.api_key and self.api_key != "sk-your-openai-api-key-here")

@dataclass
class MongoDBConfig:
    """MongoDB configuration."""
    uri: str
    database: str
    collection: str
    timeout: int
    enabled: bool
    
    def is_configured(self) -> bool:
        """Check if MongoDB is properly configured."""
        return self.enabled and self.uri != "mongodb://localhost:27017/"

@dataclass
class TANAWSystemConfig:
    """TANAW system configuration."""
    environment: str
    enable_gpt: bool
    enable_caching: bool
    enable_learning: bool
    enable_cross_user_learning: bool
    auto_map_threshold: float
    suggested_threshold: float
    gpt_escalation_threshold: float
    cache_ttl_sec: int

@dataclass
class SecurityConfig:
    """Security and API configuration."""
    flask_secret_key: str
    allowed_origins: list
    rate_limit_per_minute: int

class ConfigurationManager:
    """
    Centralized configuration manager for TANAW.
    
    Features:
    - Loads from .env file if available
    - Falls back to environment variables
    - Provides sensible defaults
    - Validates critical configurations
    - Secure API key handling
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            env_file: Path to .env file (defaults to .env in current directory)
        """
        # Load YAML config first
        self._load_yaml_config()
        
        # Load environment variables from .env file
        self._load_env_file(env_file)
        
        # Load all configurations
        self.file_processing = self._load_file_processing_config()
        self.openai = self._load_openai_config()
        self.mongodb = self._load_mongodb_config()
        self.tanaw_system = self._load_tanaw_config()
        self.security = self._load_security_config()
        
        # Additional settings
        self.knowledge_base_type = os.getenv('KNOWLEDGE_BASE_TYPE', 'sqlite')
        self.knowledge_base_path = os.getenv('KNOWLEDGE_BASE_PATH', 'tanaw_mapping_kb.db')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_yaml_config(self):
        """Load configuration from config.yml file."""
        config_path = Path(__file__).parent / 'config.yml'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.yaml_config = yaml.safe_load(f)
                print(f"✅ Loaded YAML configuration from {config_path}")
            except Exception as e:
                print(f"⚠️ Error loading YAML config: {e}")
                self.yaml_config = {}
        else:
            print(f"💡 No config.yml found at {config_path}")
            self.yaml_config = {}
    
    def _load_file_processing_config(self) -> FileProcessingConfig:
        """Load file processing configuration."""
        return FileProcessingConfig(
            max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', self.yaml_config.get('MAX_FILE_SIZE_MB', 50))),
            sample_rows_limit=int(os.getenv('SAMPLE_ROWS_LIMIT', self.yaml_config.get('SAMPLE_ROWS_LIMIT', 1000))),
            sample_min=int(os.getenv('SAMPLE_MIN', self.yaml_config.get('SAMPLE_MIN', 50))),
            max_columns_per_gpt=int(os.getenv('MAX_COLUMNS_PER_GPT', self.yaml_config.get('MAX_COLUMNS_PER_GPT', 10))),
            encoding_fallbacks=os.getenv('ENCODING_FALLBACKS', self.yaml_config.get('ENCODING_FALLBACKS', ["utf-8", "utf-16", "latin-1", "cp1252"])).split(',') if isinstance(os.getenv('ENCODING_FALLBACKS', self.yaml_config.get('ENCODING_FALLBACKS', ["utf-8", "utf-16", "latin-1", "cp1252"])), str) else self.yaml_config.get('ENCODING_FALLBACKS', ["utf-8", "utf-16", "latin-1", "cp1252"])
        )
    
    def _load_env_file(self, env_file: Optional[str]):
        """Load environment variables from .env file."""
        
        if not DOTENV_AVAILABLE:
            print("💡 Tip: Install python-dotenv to use .env files: pip install python-dotenv")
            return
        
        # Determine .env file path - check multiple locations
        env_paths = []
        
        if env_file:
            env_paths.append(Path(env_file))
        else:
            # Check current directory first
            env_paths.append(Path(__file__).parent / '.env')
            # Check parent directory (backend/.env)
            env_paths.append(Path(__file__).parent.parent / '.env')
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✅ Loaded configuration from {env_path}")
                env_loaded = True
                break
        
        if not env_loaded:
            print(f"💡 No .env file found in any of these locations:")
            for path in env_paths:
                print(f"   - {path}")
            print(f"   Create one from .env.example for easier configuration")
            print(f"   Or set environment variables directly")
    
    def _load_openai_config(self) -> OpenAIConfig:
        """Load OpenAI configuration."""
        
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Check if API key is set and valid
        if api_key and api_key != "sk-your-openai-api-key-here":
            print(f"✅ OpenAI API key detected (ends with: ...{api_key[-4:]})")
        else:
            print(f"⚠️ OpenAI API key not set - will use mock responses")
            print(f"   To enable GPT: Set OPENAI_API_KEY environment variable")
        
        return OpenAIConfig(
            api_key=api_key,
            model=os.getenv('OPENAI_MODEL', self.yaml_config.get('GPT_MODEL_DEFAULT', 'gpt-4o-mini')),
            fallback_model=os.getenv('OPENAI_FALLBACK_MODEL', self.yaml_config.get('GPT_FALLBACK_MODEL', 'gpt-4o')),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', self.yaml_config.get('GPT_MAX_TOKENS', 500))),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.1')),
            timeout_seconds=int(os.getenv('OPENAI_TIMEOUT_SECONDS', self.yaml_config.get('GPT_TIMEOUT_SEC', 20))),
            max_retries=int(os.getenv('OPENAI_MAX_RETRIES', self.yaml_config.get('GPT_MAX_RETRIES', 3))),
            enabled=str(os.getenv('TANAW_ENABLE_GPT', self.yaml_config.get('ENABLE_GPT', 'true'))).lower() == 'true'
        )
    
    def _load_mongodb_config(self) -> MongoDBConfig:
        """Load MongoDB configuration."""
        
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        
        if uri != 'mongodb://localhost:27017/':
            print(f"✅ MongoDB URI configured")
        else:
            print(f"💡 MongoDB using default URI (or SQLite if not available)")
        
        return MongoDBConfig(
            uri=uri,
            database=os.getenv('MONGODB_DATABASE', 'tanaw_knowledge_base'),
            collection=os.getenv('MONGODB_COLLECTION', 'mapping_records'),
            timeout=int(os.getenv('MONGODB_TIMEOUT', '5000')),
            enabled=os.getenv('KNOWLEDGE_BASE_TYPE', 'sqlite').lower() == 'mongodb'
        )
    
    def _load_tanaw_config(self) -> TANAWSystemConfig:
        """Load TANAW system configuration."""
        
        return TANAWSystemConfig(
            environment=os.getenv('TANAW_ENVIRONMENT', self.yaml_config.get('ENVIRONMENT', 'development')),
            enable_gpt=str(os.getenv('TANAW_ENABLE_GPT', self.yaml_config.get('ENABLE_GPT', 'true'))).lower() == 'true',
            enable_caching=str(os.getenv('TANAW_ENABLE_CACHING', self.yaml_config.get('ENABLE_CACHING', 'true'))).lower() == 'true',
            enable_learning=str(os.getenv('TANAW_ENABLE_LEARNING', self.yaml_config.get('ENABLE_LEARNING', 'true'))).lower() == 'true',
            enable_cross_user_learning=str(os.getenv('TANAW_ENABLE_CROSS_USER_LEARNING', self.yaml_config.get('ENABLE_CROSS_USER_LEARNING', 'false'))).lower() == 'true',
            auto_map_threshold=float(os.getenv('TANAW_AUTO_MAP_THRESHOLD', self.yaml_config.get('AUTO_MAP_CONF', 0.90))),
            suggested_threshold=float(os.getenv('TANAW_SUGGESTED_THRESHOLD', self.yaml_config.get('SUGGEST_CONF_MIN', 0.70))),
            gpt_escalation_threshold=float(os.getenv('TANAW_GPT_ESCALATION_THRESHOLD', self.yaml_config.get('GPT_ESCALATE_CONF', 0.70))),
            cache_ttl_sec=int(os.getenv('CACHE_TTL_SEC', self.yaml_config.get('CACHE_TTL_SEC', 3600)))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration."""
        
        secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
        
        if secret_key == 'dev-secret-key-change-in-production':
            print(f"⚠️ Using default Flask secret key - change for production!")
        
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
        
        return SecurityConfig(
            flask_secret_key=secret_key,
            allowed_origins=allowed_origins,
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
        )
    
    def _validate_configuration(self):
        """Validate configuration and warn about issues."""
        
        issues = []
        warnings_list = []
        
        # Validate thresholds
        if not (0.0 <= self.tanaw_system.auto_map_threshold <= 1.0):
            issues.append("auto_map_threshold must be between 0.0 and 1.0")
        
        if not (0.0 <= self.tanaw_system.suggested_threshold <= 1.0):
            issues.append("suggested_threshold must be between 0.0 and 1.0")
        
        if self.tanaw_system.auto_map_threshold < self.tanaw_system.suggested_threshold:
            issues.append("auto_map_threshold should be >= suggested_threshold")
        
        # Validate OpenAI config if enabled
        if self.tanaw_system.enable_gpt and not self.openai.is_configured():
            warnings_list.append("GPT enabled but API key not configured - will use mock responses")
        
        # Validate MongoDB config if enabled
        if self.mongodb.enabled and not self.mongodb.is_configured():
            warnings_list.append("MongoDB enabled but not properly configured - will fall back to SQLite")
        
        # Report issues
        if issues:
            print(f"\n❌ Configuration Errors:")
            for issue in issues:
                print(f"   • {issue}")
            raise ValueError("Invalid configuration - please fix errors above")
        
        if warnings_list:
            print(f"\n⚠️ Configuration Warnings:")
            for warning in warnings_list:
                print(f"   • {warning}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive configuration status report."""
        
        return {
            "environment": self.tanaw_system.environment,
            "features": {
                "openai_gpt": {
                    "enabled": self.tanaw_system.enable_gpt,
                    "configured": self.openai.is_configured(),
                    "model": self.openai.model if self.openai.is_configured() else "mock",
                    "status": "✅ Ready" if self.openai.is_configured() else "⚠️ Using mock (no API key)"
                },
                "mongodb": {
                    "enabled": self.mongodb.enabled,
                    "configured": self.mongodb.is_configured(),
                    "status": "✅ Ready" if self.mongodb.is_configured() else "💾 Using SQLite"
                },
                "caching": {
                    "enabled": self.tanaw_system.enable_caching,
                    "status": "✅ Enabled" if self.tanaw_system.enable_caching else "❌ Disabled"
                },
                "learning": {
                    "enabled": self.tanaw_system.enable_learning,
                    "cross_user": self.tanaw_system.enable_cross_user_learning,
                    "status": "✅ Active"
                }
            },
            "thresholds": {
                "auto_map": self.tanaw_system.auto_map_threshold,
                "suggested": self.tanaw_system.suggested_threshold,
                "gpt_escalation": self.tanaw_system.gpt_escalation_threshold
            },
            "storage": {
                "type": self.knowledge_base_type,
                "path": self.knowledge_base_path if self.knowledge_base_type == 'sqlite' else self.mongodb.uri
            },
            "security": {
                "secret_key_set": self.security.flask_secret_key != 'dev-secret-key-change-in-production',
                "allowed_origins": len(self.security.allowed_origins),
                "rate_limit": self.security.rate_limit_per_minute
            }
        }
    
    def print_status_report(self):
        """Print formatted configuration status report."""
        
        print("\n" + "=" * 60)
        print("🔧 TANAW CONFIGURATION STATUS")
        print("=" * 60)
        
        status = self.get_status_report()
        
        print(f"\n📊 Environment: {status['environment'].upper()}")
        
        print(f"\n🎯 Features Status:")
        for feature_name, feature_info in status['features'].items():
            status_indicator = feature_info['status']
            print(f"   {status_indicator} {feature_name.replace('_', ' ').title()}")
            
            if 'model' in feature_info and feature_info['configured']:
                print(f"      Model: {feature_info['model']}")
        
        print(f"\n⚖️ Confidence Thresholds:")
        print(f"   Auto-map: {status['thresholds']['auto_map']:.2f} (≥{status['thresholds']['auto_map']:.0%} confidence)")
        print(f"   Suggested: {status['thresholds']['suggested']:.2f} ({status['thresholds']['suggested']:.0%}-{status['thresholds']['auto_map']:.0%} confidence)")
        print(f"   GPT Escalation: <{status['thresholds']['gpt_escalation']:.2f} (send to AI)")
        
        print(f"\n💾 Storage Configuration:")
        print(f"   Type: {status['storage']['type'].upper()}")
        print(f"   Location: {status['storage']['path']}")
        
        print(f"\n🔒 Security:")
        secret_status = "✅ Custom key set" if status['security']['secret_key_set'] else "⚠️ Using default (change for production)"
        print(f"   Secret Key: {secret_status}")
        print(f"   CORS Origins: {status['security']['allowed_origins']} configured")
        print(f"   Rate Limit: {status['security']['rate_limit']}/minute")
        
        print(f"\n📁 File Processing:")
        print(f"   Max File Size: {self.file_processing.max_file_size_mb}MB")
        print(f"   Sample Limit: {self.file_processing.sample_rows_limit} rows")
        print(f"   Encoding Fallbacks: {len(self.file_processing.encoding_fallbacks)} encodings")
        
        print("\n" + "=" * 60)
    
    def emit_config_metrics(self):
        """Emit configuration metrics for observability."""
        try:
            # This would integrate with your monitoring system
            metrics = {
                "config.load.status": "success",
                "config.environment": self.tanaw_system.environment,
                "config.features.gpt_enabled": self.tanaw_system.enable_gpt,
                "config.features.caching_enabled": self.tanaw_system.enable_caching,
                "config.thresholds.auto_map": self.tanaw_system.auto_map_threshold,
                "config.thresholds.suggested": self.tanaw_system.suggested_threshold,
                "config.file_processing.max_size_mb": self.file_processing.max_file_size_mb,
                "config.file_processing.sample_limit": self.file_processing.sample_rows_limit
            }
            
            # In a real implementation, you would send these to your metrics system
            print(f"📊 Config metrics: {metrics}")
            return metrics
            
        except Exception as e:
            print(f"⚠️ Error emitting config metrics: {e}")
            return {"config.load.status": "error", "config.error": str(e)}
    
    def generate_setup_checklist(self) -> List[str]:
        """Generate setup checklist for user."""
        
        checklist = []
        
        # Check OpenAI
        if self.tanaw_system.enable_gpt:
            if self.openai.is_configured():
                checklist.append("✅ OpenAI API key configured")
            else:
                checklist.append("⚠️ OpenAI API key not set (optional - using mock)")
        
        # Check MongoDB
        if self.knowledge_base_type == 'mongodb':
            if self.mongodb.is_configured():
                checklist.append("✅ MongoDB configured")
            else:
                checklist.append("⚠️ MongoDB not configured (using SQLite)")
        else:
            checklist.append("✅ Using SQLite for knowledge base")
        
        # Check security
        if self.security.flask_secret_key != 'dev-secret-key-change-in-production':
            checklist.append("✅ Flask secret key configured")
        else:
            checklist.append("⚠️ Using default secret key (change for production)")
        
        # Check .env file
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            checklist.append("✅ .env file exists")
        else:
            checklist.append("💡 No .env file (using environment variables)")
        
        return checklist
    
    def save_current_config(self, filepath: str = "current_config.json"):
        """Save current configuration to JSON file for reference."""
        
        import json
        
        config_dict = {
            "openai": {
                "enabled": self.openai.enabled,
                "configured": self.openai.is_configured(),
                "model": self.openai.model,
                "max_tokens": self.openai.max_tokens,
                "temperature": self.openai.temperature
            },
            "mongodb": {
                "enabled": self.mongodb.enabled,
                "configured": self.mongodb.is_configured(),
                "database": self.mongodb.database
            },
            "tanaw_system": {
                "environment": self.tanaw_system.environment,
                "enable_gpt": self.tanaw_system.enable_gpt,
                "enable_caching": self.tanaw_system.enable_caching,
                "enable_learning": self.tanaw_system.enable_learning,
                "thresholds": {
                    "auto_map": self.tanaw_system.auto_map_threshold,
                    "suggested": self.tanaw_system.suggested_threshold,
                    "gpt_escalation": self.tanaw_system.gpt_escalation_threshold
                }
            },
            "storage": {
                "type": self.knowledge_base_type,
                "path": self.knowledge_base_path
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        print(f"💾 Configuration saved to {filepath}")

# Global configuration instance
config_manager = ConfigurationManager()

def get_config() -> ConfigurationManager:
    """Get global configuration instance."""
    return config_manager

def reload_config():
    """Reload configuration from environment."""
    global config_manager
    config_manager = ConfigurationManager()
    return config_manager

