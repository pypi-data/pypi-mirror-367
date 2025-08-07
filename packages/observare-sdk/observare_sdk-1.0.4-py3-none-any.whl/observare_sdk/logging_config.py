"""
Logging configuration for Observare SDK

Suppresses noisy third-party logs while preserving user's logging setup.
"""

import logging
import warnings


def configure_sdk_logging():
    """Configure logging to suppress noisy third-party logs."""
    
    # Suppress httpx logs (from OpenAI API calls)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Suppress OpenAI client logs
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._client").setLevel(logging.WARNING)
    
    # Suppress LangChain noisy logs
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("langchain_core").setLevel(logging.WARNING)
    logging.getLogger("langchain_openai").setLevel(logging.WARNING)
    logging.getLogger("langchain_community").setLevel(logging.WARNING)
    
    # Suppress spaCy/Presidio logs
    logging.getLogger("spacy").setLevel(logging.WARNING)
    logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
    logging.getLogger("presidio-anonymizer").setLevel(logging.ERROR)
    
    # Suppress transformers/model loading logs (if present)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers.modeling_utils").setLevel(logging.WARNING)
    
    # Suppress urllib3 debug logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    
    # Suppress requests logs
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)
    
    # Suppress asyncio debug logs
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Suppress hallucination detection internal logs
    logging.getLogger("observare.hallucination").setLevel(logging.WARNING)
    logging.getLogger("observare_hallucination").setLevel(logging.WARNING)
    
    # Suppress general ML/AI library logs
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.getLogger("numpy").setLevel(logging.WARNING)
    
    # Suppress warnings that users can't control
    warnings.filterwarnings("ignore", category=UserWarning, module="presidio")
    warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
    
    # Suppress SDK's own logs unless critical errors
    logging.getLogger("observare_sdk").setLevel(logging.ERROR)
    logging.getLogger("observare_sdk.llm").setLevel(logging.ERROR)
    logging.getLogger("observare_sdk.hallucination").setLevel(logging.ERROR)
    logging.getLogger("observare_sdk.pii").setLevel(logging.ERROR)
    logging.getLogger("observare_sdk.sdk").setLevel(logging.ERROR)


def get_sdk_logger(name: str) -> logging.Logger:
    """Get a logger for SDK components that respects user's logging setup."""
    logger = logging.getLogger(f"observare_sdk.{name}")
    
    # Don't add handlers if they already exist (user may have configured logging)
    if not logger.handlers and not logging.getLogger().handlers:
        # Only add handler if no logging is configured at all
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[Observare] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)  # Only show warnings and errors by default
    
    return logger


# Configure logging when module is imported
configure_sdk_logging()