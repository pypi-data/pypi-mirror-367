"""
Safety Configuration System for Observare SDK

Provides unified configuration management for PII redaction and hallucination detection
with support for policy presets, runtime updates, and enterprise deployment.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path

# Import our safety modules
try:
    from .pii import PIIType, RedactionStrategy
    from .hallucination import HallucinationMethod, ConfidenceLevel
    PII_AVAILABLE = True
except ImportError:
    PII_AVAILABLE = False

try:
    from pydantic import BaseModel, validator, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


class SafetyPolicy(Enum):
    """Predefined safety policy levels."""
    STRICT = "strict"           # Maximum safety, aggressive redaction/detection
    BALANCED = "balanced"       # Balance between safety and usability
    PERMISSIVE = "permissive"   # Minimal safety restrictions
    CUSTOM = "custom"           # User-defined configuration


class ConfigurationFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    ENV = "env"


@dataclass
class PIIConfiguration:
    """Configuration for PII detection and redaction."""
    enabled: bool = True
    detection_libraries: List[str] = field(default_factory=lambda: ["datafog", "piiranha", "regex"])
    min_confidence_threshold: float = 0.7
    preserve_structure: bool = True
    hash_salt: str = "observare_pii_salt_2025"
    
    # PII type specific strategies
    strategies: Dict[str, str] = field(default_factory=lambda: {
        "email": "replace",
        "phone": "mask", 
        "ssn": "remove",
        "credit_card": "remove",
        "name": "replace",
        "address": "replace",
        "location": "allow",
        "money": "allow",
        "ip_address": "mask",
        "url": "allow",
        "date_of_birth": "remove",
        "passport": "remove",
        "driver_license": "remove",
        "bank_account": "remove"
    })
    
    # Custom patterns for additional PII types
    custom_patterns: Dict[str, str] = field(default_factory=dict)
    
    # Audit and compliance settings
    audit_logging: bool = True
    compliance_mode: str = "gdpr"  # gdpr, hipaa, ccpa, custom
    
    def validate(self) -> List[str]:
        """Validate PII configuration and return any errors."""
        errors = []
        
        if not isinstance(self.enabled, bool):
            errors.append("PII enabled must be boolean")
        
        if not 0.0 <= self.min_confidence_threshold <= 1.0:
            errors.append("PII confidence threshold must be between 0.0 and 1.0")
        
        if PII_AVAILABLE:
            valid_strategies = [s.value for s in RedactionStrategy]
            for pii_type, strategy in self.strategies.items():
                if strategy not in valid_strategies:
                    errors.append(f"Invalid redaction strategy '{strategy}' for PII type '{pii_type}'")
        
        return errors


@dataclass
class HallucinationConfiguration:
    """Configuration for hallucination detection."""
    enabled: bool = True
    detection_method: str = "hybrid"
    confidence_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "high_confidence": 0.2,
        "medium_confidence": 0.5,
        "low_confidence": 0.8
    })
    
    # Method-specific settings
    consistency_samples: int = 3
    consistency_temperature: float = 0.7
    enable_chain_of_verification: bool = True
    enable_uqlm: bool = True
    enable_semantic_similarity: bool = True
    
    # Performance settings
    timeout_seconds: int = 30
    max_verification_questions: int = 5
    
    # Action thresholds
    block_threshold: float = 0.9        # Block responses above this threshold
    warn_threshold: float = 0.7         # Warn for responses above this threshold
    
    def validate(self) -> List[str]:
        """Validate hallucination configuration and return any errors."""
        errors = []
        
        if not isinstance(self.enabled, bool):
            errors.append("Hallucination detection enabled must be boolean")
        
        valid_methods = ["self_consistency", "chain_of_verification", "uqlm", "semantic_similarity", "hybrid"]
        if self.detection_method not in valid_methods:
            errors.append(f"Invalid detection method '{self.detection_method}'. Must be one of: {valid_methods}")
        
        # Validate thresholds
        for threshold_name, threshold_value in self.confidence_thresholds.items():
            if not 0.0 <= threshold_value <= 1.0:
                errors.append(f"Confidence threshold '{threshold_name}' must be between 0.0 and 1.0")
        
        if not 1 <= self.consistency_samples <= 10:
            errors.append("Consistency samples must be between 1 and 10")
        
        if not 0.0 <= self.consistency_temperature <= 2.0:
            errors.append("Consistency temperature must be between 0.0 and 2.0")
        
        if not 0.0 <= self.block_threshold <= 1.0:
            errors.append("Block threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.warn_threshold <= 1.0:
            errors.append("Warn threshold must be between 0.0 and 1.0")
        
        return errors


@dataclass
class TelemetryConfiguration:
    """Configuration for telemetry and observability."""
    enabled: bool = True
    api_key: str = ""
    api_endpoint: str = "https://observare-backend.fly.dev"
    
    # Event types to track
    track_pii_events: bool = True
    track_hallucination_events: bool = True
    track_performance_metrics: bool = True
    track_usage_metrics: bool = True
    
    # Data export settings
    export_redacted_content: bool = False  # Whether to include redacted content in telemetry
    export_original_content: bool = False  # Whether to include original content (security risk)
    
    # Batch processing
    batch_size: int = 100
    batch_timeout_seconds: int = 30
    
    def validate(self) -> List[str]:
        """Validate telemetry configuration and return any errors."""
        errors = []
        
        if not isinstance(self.enabled, bool):
            errors.append("Telemetry enabled must be boolean")
        
        if self.enabled and not self.api_key:
            errors.append("API key required when telemetry is enabled")
        
        if self.batch_size <= 0:
            errors.append("Batch size must be positive")
        
        if self.batch_timeout_seconds <= 0:
            errors.append("Batch timeout must be positive")
        
        return errors


@dataclass
class SafetyConfiguration:
    """Main safety configuration combining all safety features."""
    policy: str = SafetyPolicy.BALANCED.value
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Component configurations
    pii: PIIConfiguration = field(default_factory=PIIConfiguration)
    hallucination: HallucinationConfiguration = field(default_factory=HallucinationConfiguration)
    telemetry: TelemetryConfiguration = field(default_factory=TelemetryConfiguration)
    
    # Global settings
    fail_safe_mode: bool = True         # Continue operation even if safety checks fail
    performance_mode: bool = False       # Optimize for speed over accuracy
    debug_mode: bool = False            # Enable detailed logging
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate entire configuration and return errors by component."""
        validation_errors = {}
        
        # Validate policy
        valid_policies = [p.value for p in SafetyPolicy]
        if self.policy not in valid_policies:
            validation_errors["policy"] = [f"Invalid policy '{self.policy}'. Must be one of: {valid_policies}"]
        
        # Validate components
        pii_errors = self.pii.validate()
        if pii_errors:
            validation_errors["pii"] = pii_errors
        
        hallucination_errors = self.hallucination.validate()
        if hallucination_errors:
            validation_errors["hallucination"] = hallucination_errors
        
        telemetry_errors = self.telemetry.validate()
        if telemetry_errors:
            validation_errors["telemetry"] = telemetry_errors
        
        return validation_errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        errors = self.validate()
        return len(errors) == 0
    
    def apply_policy(self, policy: SafetyPolicy):
        """Apply a predefined safety policy."""
        self.policy = policy.value
        self.updated_at = datetime.now().isoformat()
        
        if policy == SafetyPolicy.STRICT:
            self._apply_strict_policy()
        elif policy == SafetyPolicy.BALANCED:
            self._apply_balanced_policy()
        elif policy == SafetyPolicy.PERMISSIVE:
            self._apply_permissive_policy()
        # CUSTOM policy doesn't change settings
    
    def _apply_strict_policy(self):
        """Apply strict safety policy - maximum security."""
        # PII: Remove/redact everything aggressively
        self.pii.enabled = True
        self.pii.min_confidence_threshold = 0.5
        self.pii.strategies.update({
            "email": "remove",
            "phone": "remove",
            "ssn": "remove", 
            "credit_card": "remove",
            "name": "remove",
            "address": "remove",
            "location": "allow",
            "money": "allow",
            "ip_address": "remove",
            "url": "remove",
            "date_of_birth": "remove",
            "passport": "remove",
            "driver_license": "remove",
            "bank_account": "remove"
        })
        
        # Hallucination: Very conservative thresholds
        self.hallucination.enabled = True
        self.hallucination.detection_method = "hybrid"
        self.hallucination.confidence_thresholds.update({
            "high_confidence": 0.1,
            "medium_confidence": 0.3,
            "low_confidence": 0.6
        })
        self.hallucination.consistency_samples = 5
        self.hallucination.block_threshold = 0.7
        self.hallucination.warn_threshold = 0.5
        
        # Telemetry: Full tracking but no sensitive data
        self.telemetry.enabled = True
        self.telemetry.track_pii_events = True
        self.telemetry.track_hallucination_events = True
        self.telemetry.export_redacted_content = False
        self.telemetry.export_original_content = False
    
    def _apply_balanced_policy(self):
        """Apply balanced safety policy - good balance of security and usability."""
        # PII: Intelligent redaction with some preservation
        self.pii.enabled = True
        self.pii.min_confidence_threshold = 0.7
        self.pii.strategies.update({
            "email": "replace",
            "phone": "mask",
            "ssn": "remove",
            "credit_card": "remove", 
            "name": "replace",
            "address": "replace",
            "location": "allow",
            "money": "allow",
            "ip_address": "mask",
            "url": "allow",
            "date_of_birth": "mask",
            "passport": "remove",
            "driver_license": "remove",
            "bank_account": "remove"
        })
        
        # Hallucination: Moderate thresholds
        self.hallucination.enabled = True
        self.hallucination.detection_method = "hybrid"
        self.hallucination.confidence_thresholds.update({
            "high_confidence": 0.2,
            "medium_confidence": 0.5,
            "low_confidence": 0.8
        })
        self.hallucination.consistency_samples = 3
        self.hallucination.block_threshold = 0.9
        self.hallucination.warn_threshold = 0.7
        
        # Telemetry: Full tracking with redacted content
        self.telemetry.enabled = True
        self.telemetry.track_pii_events = True
        self.telemetry.track_hallucination_events = True
        self.telemetry.export_redacted_content = True
        self.telemetry.export_original_content = False
    
    def _apply_permissive_policy(self):
        """Apply permissive safety policy - minimal restrictions."""
        # PII: Light redaction, mostly warnings
        self.pii.enabled = True
        self.pii.min_confidence_threshold = 0.9
        self.pii.strategies.update({
            "email": "allow",
            "phone": "allow",
            "ssn": "replace",
            "credit_card": "mask",
            "name": "allow",
            "address": "allow",
            "location": "allow",
            "money": "allow",
            "ip_address": "allow",
            "url": "allow",
            "date_of_birth": "allow",
            "passport": "replace",
            "driver_license": "replace",
            "bank_account": "remove"
        })
        
        # Hallucination: Lenient thresholds
        self.hallucination.enabled = True
        self.hallucination.detection_method = "self_consistency"
        self.hallucination.confidence_thresholds.update({
            "high_confidence": 0.3,
            "medium_confidence": 0.6,
            "low_confidence": 0.9
        })
        self.hallucination.consistency_samples = 2
        self.hallucination.block_threshold = 0.95
        self.hallucination.warn_threshold = 0.8
        
        # Telemetry: Minimal tracking
        self.telemetry.enabled = True
        self.telemetry.track_pii_events = False
        self.telemetry.track_hallucination_events = True
        self.telemetry.export_redacted_content = True
        self.telemetry.export_original_content = False


class SafetyConfigurationManager:
    """Manages safety configuration with file I/O, validation, and runtime updates."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.config = SafetyConfiguration()
        self._load_from_environment()
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Telemetry settings from environment
        if api_key := os.getenv("OBSERVARE_API_KEY"):
            self.config.telemetry.api_key = api_key
        
        if api_endpoint := os.getenv("OBSERVARE_API_ENDPOINT"):
            self.config.telemetry.api_endpoint = api_endpoint
        
        # Policy from environment
        if policy := os.getenv("OBSERVARE_SAFETY_POLICY"):
            try:
                self.config.apply_policy(SafetyPolicy(policy))
            except ValueError:
                pass  # Invalid policy, keep default
        
        # PII settings
        if os.getenv("OBSERVARE_PII_ENABLED", "").lower() in ("false", "0", "no"):
            self.config.pii.enabled = False
        
        if confidence := os.getenv("OBSERVARE_PII_CONFIDENCE"):
            try:
                self.config.pii.min_confidence_threshold = float(confidence)
            except ValueError:
                pass
        
        # Hallucination settings
        if os.getenv("OBSERVARE_HALLUCINATION_ENABLED", "").lower() in ("false", "0", "no"):
            self.config.hallucination.enabled = False
        
        if method := os.getenv("OBSERVARE_HALLUCINATION_METHOD"):
            if method in ["self_consistency", "chain_of_verification", "uqlm", "semantic_similarity", "hybrid"]:
                self.config.hallucination.detection_method = method
        
        # Debug mode
        if os.getenv("OBSERVARE_DEBUG", "").lower() in ("true", "1", "yes"):
            self.config.debug_mode = True
    
    def load_from_file(self, file_path: str, format_type: Optional[ConfigurationFormat] = None):
        """
        Load configuration from file.
        
        Args:
            file_path: Path to configuration file
            format_type: File format (auto-detected if None)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        # Auto-detect format if not specified
        if format_type is None:
            ext = Path(file_path).suffix.lower()
            if ext == ".json":
                format_type = ConfigurationFormat.JSON
            # YAML support removed for production
            else:
                raise ValueError(f"Cannot auto-detect format for file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                if format_type == ConfigurationFormat.JSON:
                    data = json.load(f)
                # YAML support removed
                else:
                    raise ValueError(f"Unsupported format: {format_type}")
            
            # Create configuration from data
            self.config = self._dict_to_config(data)
            self.config_path = file_path
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {file_path}: {e}")
    
    def save_to_file(self, file_path: Optional[str] = None, format_type: Optional[ConfigurationFormat] = None):
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save file (uses current path if None)
            format_type: File format (auto-detected if None)
        """
        file_path = file_path or self.config_path
        if not file_path:
            raise ValueError("No file path specified and no current path set")
        
        # Auto-detect format if not specified
        if format_type is None:
            ext = Path(file_path).suffix.lower()
            if ext == ".json":
                format_type = ConfigurationFormat.JSON
            # YAML support removed for production
            else:
                format_type = ConfigurationFormat.JSON  # Default to JSON
                file_path += ".json"
        
        # Update timestamp
        self.config.updated_at = datetime.now().isoformat()
        
        # Convert to dict
        config_dict = asdict(self.config)
        
        try:
            with open(file_path, 'w') as f:
                if format_type == ConfigurationFormat.JSON:
                    json.dump(config_dict, f, indent=2, default=str)
                # YAML support removed
                else:
                    raise ValueError(f"Unsupported format: {format_type}")
            
            self.config_path = file_path
            
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {file_path}: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> SafetyConfiguration:
        """Convert dictionary to SafetyConfiguration object."""
        # Handle nested structures
        if 'pii' in data and isinstance(data['pii'], dict):
            data['pii'] = PIIConfiguration(**data['pii'])
        
        if 'hallucination' in data and isinstance(data['hallucination'], dict):
            data['hallucination'] = HallucinationConfiguration(**data['hallucination'])
        
        if 'telemetry' in data and isinstance(data['telemetry'], dict):
            data['telemetry'] = TelemetryConfiguration(**data['telemetry'])
        
        return SafetyConfiguration(**data)
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate current configuration."""
        return self.config.validate()
    
    def apply_policy(self, policy: SafetyPolicy):
        """Apply a predefined safety policy."""
        self.config.apply_policy(policy)
    
    def update_pii_strategy(self, pii_type: str, strategy: str):
        """Update PII redaction strategy for a specific type."""
        if PII_AVAILABLE:
            valid_strategies = [s.value for s in RedactionStrategy]
            if strategy not in valid_strategies:
                raise ValueError(f"Invalid strategy '{strategy}'. Must be one of: {valid_strategies}")
        
        self.config.pii.strategies[pii_type] = strategy
        self.config.updated_at = datetime.now().isoformat()
    
    def update_hallucination_threshold(self, threshold_name: str, threshold_value: float):
        """Update hallucination detection threshold."""
        if not 0.0 <= threshold_value <= 1.0:
            raise ValueError("Threshold value must be between 0.0 and 1.0")
        
        self.config.hallucination.confidence_thresholds[threshold_name] = threshold_value
        self.config.updated_at = datetime.now().isoformat()
    
    def export_config_template(self, file_path: str, format_type: ConfigurationFormat = ConfigurationFormat.JSON):
        """Export a configuration template with comments and examples."""
        template = {
            "_comment": "Observare SDK Safety Configuration Template",
            "_version": "1.0.0",
            "_policies": ["strict", "balanced", "permissive", "custom"],
            
            "policy": "balanced",
            "version": "1.0.0",
            "fail_safe_mode": True,
            "performance_mode": False,
            "debug_mode": False,
            
            "pii": {
                "_comment": "PII Detection and Redaction Settings",
                "enabled": True,
                "detection_libraries": ["datafog", "piiranha", "regex"],
                "min_confidence_threshold": 0.7,
                "preserve_structure": True,
                "audit_logging": True,
                "compliance_mode": "gdpr",
                
                "strategies": {
                    "_comment": "Redaction strategies: allow, mask, replace, remove, hash",
                    "email": "replace",
                    "phone": "mask",
                    "ssn": "remove",
                    "credit_card": "remove",
                    "name": "replace",
                    "address": "replace",
                    "ip_address": "mask",
                    "url": "allow"
                }
            },
            
            "hallucination": {
                "_comment": "Hallucination Detection Settings",
                "enabled": True,
                "detection_method": "hybrid",
                "consistency_samples": 3,
                "consistency_temperature": 0.7,
                "enable_chain_of_verification": True,
                "enable_uqlm": True,
                "timeout_seconds": 30,
                
                "confidence_thresholds": {
                    "_comment": "Thresholds for confidence levels (0.0-1.0)",
                    "high_confidence": 0.2,
                    "medium_confidence": 0.5,
                    "low_confidence": 0.8
                },
                
                "block_threshold": 0.9,
                "warn_threshold": 0.7
            },
            
            "telemetry": {
                "_comment": "Observability and Telemetry Settings",
                "enabled": True,
                "api_key": "${OBSERVARE_API_KEY}",
                "api_endpoint": "https://observare-backend.fly.dev",
                "track_pii_events": True,
                "track_hallucination_events": True,
                "export_redacted_content": True,
                "export_original_content": False,
                "batch_size": 100,
                "batch_timeout_seconds": 30
            }
        }
        
        try:
            with open(file_path, 'w') as f:
                if format_type == ConfigurationFormat.JSON:
                    json.dump(template, f, indent=2)
                # YAML support removed
                else:
                    raise ValueError(f"Unsupported format: {format_type}")
                    
        except Exception as e:
            raise ValueError(f"Failed to export template to {file_path}: {e}")
    
    def get_current_config(self) -> SafetyConfiguration:
        """Get current configuration (copy)."""
        return SafetyConfiguration(**asdict(self.config))


# Convenience functions for common operations
def load_config(file_path: str) -> SafetyConfiguration:
    """Load configuration from file."""
    manager = SafetyConfigurationManager()
    manager.load_from_file(file_path)
    return manager.get_current_config()


def create_strict_config() -> SafetyConfiguration:
    """Create a strict safety configuration."""
    config = SafetyConfiguration()
    config.apply_policy(SafetyPolicy.STRICT)
    return config


def create_balanced_config() -> SafetyConfiguration:
    """Create a balanced safety configuration."""
    config = SafetyConfiguration()
    config.apply_policy(SafetyPolicy.BALANCED)
    return config


def create_permissive_config() -> SafetyConfiguration:
    """Create a permissive safety configuration."""
    config = SafetyConfiguration()
    config.apply_policy(SafetyPolicy.PERMISSIVE)
    return config


# Production module - test code removed