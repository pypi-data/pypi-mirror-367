"""
Observare SDK - Zero-config telemetry and safety for LangChain agents

This SDK provides comprehensive observability, PII redaction, and hallucination detection
for LangChain applications with minimal configuration required.

Basic Usage:
    from observare_sdk import AutoTelemetryHandler
    
    handler = AutoTelemetryHandler(api_key="your-api-key")
    executor = AgentExecutor(agent=agent, tools=tools, callbacks=[handler])

Advanced Usage:
    from observare_sdk import ObservareChat, SafetyPolicy
    
    safe_llm = ObservareChat(llm=base_llm, api_key="your-api-key")
    safe_llm.apply_policy(SafetyPolicy.BALANCED)
"""

# Configure logging to suppress noisy third-party logs
from .logging_config import configure_sdk_logging
configure_sdk_logging()

__version__ = "1.0.3"
__author__ = "Observare"
__email__ = "support@observare.ai"

# Core telemetry components
from .sdk import (
    AutoTelemetryHandler,
    TelemetrySDK,
    TelemetryEvent,
)

# Safety wrapper
from .llm import ObservareChat

# Configuration system
from .config import (
    SafetyPolicy,
    SafetyConfiguration,
    SafetyConfigurationManager,
    PIIConfiguration,
    HallucinationConfiguration,
    TelemetryConfiguration,
    create_strict_config,
    create_balanced_config,
    create_permissive_config,
)

# PII detection (optional import)
try:
    from .pii import (
        PIIType,
        RedactionStrategy,
        PIIDetection,
        PIIRedactionResult,
        PIIRedactionEngine,
        detect_pii,
        redact_pii,
    )
    PII_AVAILABLE = True
except ImportError:
    PII_AVAILABLE = False

# Hallucination detection (optional import)
try:
    from .hallucination import (
        HallucinationMethod,
        ConfidenceLevel,
        HallucinationResult,
        HallucinationDetectionEngine,
    )
    HALLUCINATION_AVAILABLE = True
except ImportError:
    HALLUCINATION_AVAILABLE = False

# Public API
__all__ = [
    # Core telemetry
    "AutoTelemetryHandler",
    "TelemetrySDK", 
    "TelemetryEvent",
    
    # Safety wrapper
    "ObservareChat",
    
    # Configuration
    "SafetyPolicy",
    "SafetyConfiguration",
    "SafetyConfigurationManager",
    "PIIConfiguration",
    "HallucinationConfiguration", 
    "TelemetryConfiguration",
    "create_strict_config",
    "create_balanced_config",
    "create_permissive_config",
    
    # Version info
    "__version__",
]

# Conditionally add PII exports
if PII_AVAILABLE:
    __all__.extend([
        "PIIType",
        "RedactionStrategy", 
        "PIIDetection",
        "PIIRedactionResult",
        "PIIRedactionEngine",
        "detect_pii",
        "redact_pii",
    ])

# Conditionally add hallucination exports
if HALLUCINATION_AVAILABLE:
    __all__.extend([
        "HallucinationMethod",
        "ConfidenceLevel",
        "HallucinationResult", 
        "HallucinationDetectionEngine",
    ])

# Provide feature availability info
def get_available_features():
    """Get information about available optional features."""
    return {
        "pii_detection": PII_AVAILABLE,
        "hallucination_detection": HALLUCINATION_AVAILABLE,
        "version": __version__,
    }