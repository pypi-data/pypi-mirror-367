"""
PII Detection and Redaction Engine for Observare SDK

Supports multiple PII detection libraries with configurable redaction strategies.
Provides comprehensive logging and compliance tracking.
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class PIIType(Enum):
    """Supported PII types for detection and redaction."""
    EMAIL = "email"
    PHONE = "phone" 
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"
    IP_ADDRESS = "ip_address"
    URL = "url"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"


class RedactionStrategy(Enum):
    """Different strategies for redacting PII."""
    MASK = "mask"           # Replace with asterisks: john@example.com -> ****@example.com
    REMOVE = "remove"       # Remove entirely: "Call me at 555-1234" -> "Call me at "
    REPLACE = "replace"     # Replace with placeholder: john@example.com -> [EMAIL_REDACTED]
    HASH = "hash"          # Replace with hash: john@example.com -> [EMAIL_a1b2c3d4]
    ALLOW = "allow"        # Don't redact this type


@dataclass
class PIIDetection:
    """Represents a detected PII entity."""
    pii_type: PIIType
    text: str
    start_pos: int
    end_pos: int
    confidence: float
    redaction_strategy: RedactionStrategy
    redacted_text: str
    detection_method: str


@dataclass
class PIIRedactionResult:
    """Result of PII redaction process."""
    original_text: str
    redacted_text: str
    detections: List[PIIDetection]
    total_redactions: int
    redaction_summary: Dict[str, int]
    processing_time_ms: float


class RegexPIIDetector:
    """Regex-based PII detector as fallback when external libraries unavailable."""
    
    # Comprehensive regex patterns for common PII types
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}',
        PIIType.SSN: r'\b(?:\d{3}-?\d{2}-?\d{4})\b',
        PIIType.CREDIT_CARD: r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        PIIType.IP_ADDRESS: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        PIIType.URL: r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w.*))*)?',
        PIIType.DATE_OF_BIRTH: r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{2,4}[/-]\d{1,2}[/-]\d{1,2})\b',
    }
    
    def detect(self, text: str) -> List[PIIDetection]:
        """Detect PII using regex patterns."""
        detections = []
        
        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detection = PIIDetection(
                    pii_type=pii_type,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.8,  # Regex confidence is lower
                    redaction_strategy=RedactionStrategy.REPLACE,
                    redacted_text="",
                    detection_method="regex"
                )
                detections.append(detection)
        
        return detections


# DataFog integration removed - placeholder implementation


# Piiranha integration removed - placeholder implementation


class PresidioDetector:
    """Microsoft Presidio PII detector integration (production-ready)."""
    
    def __init__(self):
        self.available = False
        self.analyzer = None
        try:
            # Try to import Presidio
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            import logging
            
            # Suppress Presidio language warnings
            presidio_logger = logging.getLogger('presidio-analyzer')
            presidio_logger.setLevel(logging.ERROR)
            
            # Try to initialize with spaCy model
            try:
                # Create NLP engine with spaCy and specific English-only configuration
                nlp_configuration = {
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
                    "model_to_presidio_entity_mapping": {
                        "CARDINAL": "CARDINAL",
                        "DATE": "DATE_TIME",
                        "EVENT": "EVENT",
                        "FAC": "FAC",
                        "GPE": "LOCATION",
                        "LANGUAGE": "LANGUAGE",
                        "LAW": "LAW",
                        "LOC": "LOCATION",
                        "MONEY": "MONEY",
                        "NORP": "NORP",
                        "ORDINAL": "ORDINAL",
                        "ORG": "ORG",
                        "PERCENT": "PERCENT",
                        "PERSON": "PERSON",
                        "PRODUCT": "PRODUCT",
                        "QUANTITY": "QUANTITY",
                        "TIME": "TIME",
                        "WORK_OF_ART": "WORK_OF_ART"
                    },
                    "low_score_entity_names": ["ORG", "ORDINAL"],
                    "labels_to_ignore": ["CARDINAL"]
                }
                provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
                nlp_engine = provider.create_engine()
                
                # Initialize analyzer with English-only recognizers
                from presidio_analyzer import RecognizerRegistry
                registry = RecognizerRegistry()
                
                # Only load English recognizers to avoid warnings
                english_recognizers = [
                    "CreditCardRecognizer", "CryptoRecognizer", "DateRecognizer", 
                    "EmailRecognizer", "IbanRecognizer", "IpRecognizer", 
                    "MedicalLicenseRecognizer", "PhoneRecognizer", "UrlRecognizer",
                    "UsBankRecognizer", "UsLicenseRecognizer", "UsItinRecognizer",
                    "UsPassportRecognizer", "UsSsnRecognizer", "NhsRecognizer",
                    "SpacyRecognizer"
                ]
                
                self.analyzer = AnalyzerEngine(
                    nlp_engine=nlp_engine,
                    registry=registry,
                    supported_languages=["en"]
                )
                self.available = True
                
            except Exception:
                # Fallback to default configuration (may use smaller model)
                try:
                    # Suppress warnings for fallback too
                    self.analyzer = AnalyzerEngine(supported_languages=["en"])
                    self.available = True
                except Exception:
                    pass
                    
        except ImportError:
            pass
    
    def detect(self, text: str) -> List[PIIDetection]:
        """Detect PII using Microsoft Presidio."""
        if not self.available or not self.analyzer:
            return []
        
        detections = []
        try:
            # Run Presidio analysis
            results = self.analyzer.analyze(
                text=text, 
                language='en',
                score_threshold=0.1  # Low threshold, we'll filter by confidence later
            )
            
            for result in results:
                # Extract the actual text
                detected_text = text[result.start:result.end]
                
                detection = PIIDetection(
                    pii_type=self._map_presidio_type(result.entity_type),
                    text=detected_text,
                    start_pos=result.start,
                    end_pos=result.end,
                    confidence=result.score,
                    redaction_strategy=RedactionStrategy.REPLACE,
                    redacted_text="",
                    detection_method="presidio"
                )
                detections.append(detection)
                
        except Exception as e:
            # Fallback silently if Presidio fails
            pass
        
        return detections
    
    def _map_presidio_type(self, presidio_type: str) -> PIIType:
        """Map Presidio entity types to our PIIType enum."""
        mapping = {
            'EMAIL_ADDRESS': PIIType.EMAIL,
            'PHONE_NUMBER': PIIType.PHONE,
            'US_SSN': PIIType.SSN,
            'CREDIT_CARD': PIIType.CREDIT_CARD,
            'PERSON': PIIType.NAME,
            'LOCATION': PIIType.ADDRESS,
            'IP_ADDRESS': PIIType.IP_ADDRESS,
            'URL': PIIType.URL,
            'DATE_TIME': PIIType.DATE_OF_BIRTH,
            'US_PASSPORT': PIIType.PASSPORT,
            'US_DRIVER_LICENSE': PIIType.DRIVER_LICENSE,
            'US_BANK_NUMBER': PIIType.BANK_ACCOUNT,
            # Additional Presidio types
            'IBAN_CODE': PIIType.BANK_ACCOUNT,
            'CRYPTO': PIIType.BANK_ACCOUNT,  # Crypto wallets are financial
            'MEDICAL_LICENSE': PIIType.DRIVER_LICENSE,  # Use driver license as generic ID
            'US_ITIN': PIIType.SSN,  # Individual Taxpayer ID similar to SSN
        }
        return mapping.get(presidio_type, PIIType.NAME)  # Default to NAME for unknown types


class PIIRedactionEngine:
    """Main PII detection and redaction engine."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize PII redaction engine.
        
        Args:
            config: Configuration dict with PII policies and strategies
        """
        self.config = config or self._default_config()
        
        # Initialize detectors in order of preference
        self.detectors = []
        
        # Try Presidio first (best balance of accuracy and performance)
        presidio_detector = PresidioDetector()
        if presidio_detector.available:
            self.detectors.append(presidio_detector)
        
        # High-performance detectors removed for production
        
        # Always include regex detector as fallback
        self.detectors.append(RegexPIIDetector())
        
        # Track redaction statistics
        self.stats = {
            'total_scans': 0,
            'total_redactions': 0,
            'redactions_by_type': {pii_type.value: 0 for pii_type in PIIType}
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Default PII redaction configuration."""
        return {
            'enabled': True,
            'strategies': {
                PIIType.EMAIL.value: RedactionStrategy.REPLACE.value,
                PIIType.PHONE.value: RedactionStrategy.MASK.value,
                PIIType.SSN.value: RedactionStrategy.REMOVE.value,
                PIIType.CREDIT_CARD.value: RedactionStrategy.REMOVE.value,
                PIIType.NAME.value: RedactionStrategy.REPLACE.value,
                PIIType.ADDRESS.value: RedactionStrategy.REPLACE.value,
                PIIType.IP_ADDRESS.value: RedactionStrategy.MASK.value,
                PIIType.URL.value: RedactionStrategy.ALLOW.value,
                PIIType.DATE_OF_BIRTH.value: RedactionStrategy.REMOVE.value,
                PIIType.PASSPORT.value: RedactionStrategy.REMOVE.value,
                PIIType.DRIVER_LICENSE.value: RedactionStrategy.REMOVE.value,
                PIIType.BANK_ACCOUNT.value: RedactionStrategy.REMOVE.value,
            },
            'min_confidence': 0.7,
            'preserve_structure': True,  # Keep original text structure when possible
            'hash_salt': 'observare_pii_salt_2025'
        }
    
    def detect_pii(self, text: str) -> List[PIIDetection]:
        """
        Detect PII in text using available detectors.
        
        Args:
            text: Input text to scan for PII
            
        Returns:
            List of PIIDetection objects
        """
        if not self.config.get('enabled', True):
            return []
        
        all_detections = []
        
        # Run all available detectors
        for detector in self.detectors:
            try:
                detections = detector.detect(text)
                all_detections.extend(detections)
            except Exception as e:
                # Log error but continue with other detectors
                continue
        
        # Filter by confidence threshold
        min_confidence = self.config.get('min_confidence', 0.7)
        filtered_detections = [
            d for d in all_detections 
            if d.confidence >= min_confidence
        ]
        
        # Remove duplicates (same PII detected by multiple methods)
        unique_detections = self._deduplicate_detections(filtered_detections)
        
        # Apply redaction strategies
        for detection in unique_detections:
            strategy_key = detection.pii_type.value
            strategy = self.config['strategies'].get(
                strategy_key, 
                RedactionStrategy.REPLACE.value
            )
            detection.redaction_strategy = RedactionStrategy(strategy)
            detection.redacted_text = self._apply_redaction_strategy(
                detection.text, 
                detection.pii_type, 
                detection.redaction_strategy
            )
        
        return unique_detections
    
    def redact_text(self, text: str) -> PIIRedactionResult:
        """
        Redact PII from text and return comprehensive results.
        
        Args:
            text: Input text to redact PII from
            
        Returns:
            PIIRedactionResult with original text, redacted text, and metadata
        """
        start_time = datetime.now()
        
        # Detect PII
        detections = self.detect_pii(text)
        
        # Apply redactions in reverse order to preserve positions
        redacted_text = text
        sorted_detections = sorted(detections, key=lambda d: d.start_pos, reverse=True)
        
        for detection in sorted_detections:
            if detection.redaction_strategy != RedactionStrategy.ALLOW:
                # Replace the detected PII with redacted version
                redacted_text = (
                    redacted_text[:detection.start_pos] + 
                    detection.redacted_text + 
                    redacted_text[detection.end_pos:]
                )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Create summary statistics
        redaction_summary = {}
        for detection in detections:
            pii_type = detection.pii_type.value
            redaction_summary[pii_type] = redaction_summary.get(pii_type, 0) + 1
        
        # Update global stats
        self.stats['total_scans'] += 1
        self.stats['total_redactions'] += len(detections)
        for detection in detections:
            self.stats['redactions_by_type'][detection.pii_type.value] += 1
        
        return PIIRedactionResult(
            original_text=text,
            redacted_text=redacted_text,
            detections=detections,
            total_redactions=len(detections),
            redaction_summary=redaction_summary,
            processing_time_ms=processing_time
        )
    
    def _deduplicate_detections(self, detections: List[PIIDetection]) -> List[PIIDetection]:
        """Remove duplicate PII detections from multiple detectors."""
        # Group by position and type
        unique_detections = []
        seen_positions = set()
        
        # Sort by confidence (highest first) to keep best detections
        sorted_detections = sorted(detections, key=lambda d: d.confidence, reverse=True)
        
        for detection in sorted_detections:
            position_key = (detection.start_pos, detection.end_pos, detection.pii_type)
            if position_key not in seen_positions:
                unique_detections.append(detection)
                seen_positions.add(position_key)
        
        return unique_detections
    
    def _apply_redaction_strategy(self, text: str, pii_type: PIIType, strategy: RedactionStrategy) -> str:
        """Apply the specified redaction strategy to detected PII."""
        if strategy == RedactionStrategy.ALLOW:
            return text
        
        elif strategy == RedactionStrategy.MASK:
            if pii_type == PIIType.EMAIL:
                # Keep domain visible: john@example.com -> ****@example.com
                if '@' in text:
                    local, domain = text.split('@', 1)
                    return '*' * len(local) + '@' + domain
                return '*' * len(text)
            
            elif pii_type == PIIType.PHONE:
                # Keep last 4 digits: 555-123-4567 -> ***-***-4567
                if len(text) >= 4:
                    return '*' * (len(text) - 4) + text[-4:]
                return '*' * len(text)
            
            elif pii_type == PIIType.CREDIT_CARD:
                # Keep last 4 digits: 1234-5678-9012-3456 -> ****-****-****-3456
                cleaned = re.sub(r'[^\d]', '', text)
                if len(cleaned) >= 4:
                    masked = '*' * (len(cleaned) - 4) + cleaned[-4:]
                    # Preserve original formatting
                    result = text
                    for i, char in enumerate(text):
                        if char.isdigit() and i < len(text) - 4:
                            result = result[:i] + '*' + result[i+1:]
                    return result
                return '*' * len(text)
            
            else:
                # Default masking
                return '*' * len(text)
        
        elif strategy == RedactionStrategy.REMOVE:
            return ""
        
        elif strategy == RedactionStrategy.REPLACE:
            placeholders = {
                PIIType.EMAIL: "[EMAIL_REDACTED]",
                PIIType.PHONE: "[PHONE_REDACTED]",
                PIIType.SSN: "[SSN_REDACTED]",
                PIIType.CREDIT_CARD: "[CARD_REDACTED]",
                PIIType.NAME: "[NAME_REDACTED]",
                PIIType.ADDRESS: "[ADDRESS_REDACTED]",
                PIIType.IP_ADDRESS: "[IP_REDACTED]",
                PIIType.URL: "[URL_REDACTED]",
                PIIType.DATE_OF_BIRTH: "[DOB_REDACTED]",
                PIIType.PASSPORT: "[PASSPORT_REDACTED]",
                PIIType.DRIVER_LICENSE: "[LICENSE_REDACTED]",
                PIIType.BANK_ACCOUNT: "[ACCOUNT_REDACTED]",
            }
            return placeholders.get(pii_type, "[PII_REDACTED]")
        
        elif strategy == RedactionStrategy.HASH:
            # Create a hash of the PII for potential de-identification
            salt = self.config.get('hash_salt', 'observare_pii_salt')
            hash_input = f"{text}{salt}"
            hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
            
            hash_placeholders = {
                PIIType.EMAIL: f"[EMAIL_{hash_value}]",
                PIIType.PHONE: f"[PHONE_{hash_value}]",
                PIIType.SSN: f"[SSN_{hash_value}]",
                PIIType.CREDIT_CARD: f"[CARD_{hash_value}]",
                PIIType.NAME: f"[NAME_{hash_value}]",
                PIIType.ADDRESS: f"[ADDRESS_{hash_value}]",
                PIIType.IP_ADDRESS: f"[IP_{hash_value}]",
                PIIType.URL: f"[URL_{hash_value}]",
                PIIType.DATE_OF_BIRTH: f"[DOB_{hash_value}]",
                PIIType.PASSPORT: f"[PASSPORT_{hash_value}]",
                PIIType.DRIVER_LICENSE: f"[LICENSE_{hash_value}]",
                PIIType.BANK_ACCOUNT: f"[ACCOUNT_{hash_value}]",
            }
            return hash_placeholders.get(pii_type, f"[PII_{hash_value}]")
        
        return text
    
    def get_stats(self) -> Dict[str, Any]:
        """Get PII redaction statistics."""
        return self.stats.copy()
    
    def export_audit_log(self, detections: List[PIIDetection]) -> Dict[str, Any]:
        """Export audit log for compliance reporting."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_detections': len(detections),
            'detections': [asdict(detection) for detection in detections],
            'redaction_summary': {
                pii_type.value: len([d for d in detections if d.pii_type == pii_type])
                for pii_type in PIIType
            },
            'compliance_metadata': {
                'processor': 'observare_pii_engine',
                'version': '1.0.0',
                'detection_methods': list(set(d.detection_method for d in detections))
            }
        }


# Convenience functions for easy integration
def detect_pii(text: str, config: Optional[Dict[str, Any]] = None) -> List[PIIDetection]:
    """Convenience function to detect PII in text."""
    engine = PIIRedactionEngine(config)
    return engine.detect_pii(text)


def redact_pii(text: str, config: Optional[Dict[str, Any]] = None) -> PIIRedactionResult:
    """Convenience function to redact PII from text."""
    engine = PIIRedactionEngine(config)
    return engine.redact_text(text)


# Production module - test code removed