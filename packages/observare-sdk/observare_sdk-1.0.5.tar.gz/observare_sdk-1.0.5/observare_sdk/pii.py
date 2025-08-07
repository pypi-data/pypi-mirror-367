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
    LOCATION = "location"  # Geographic locations (cities, countries, states)
    MONEY = "money"  # Monetary amounts (prices, salaries, etc.)
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
    
    # Comprehensive regex patterns for common PII types - ordered by specificity
    PATTERNS = {
        # Most specific patterns first to avoid conflicts
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.SSN: r'\b\d{3}-?\d{2}-?\d{4}\b|\b\d{9}(?!\d)',
        # Improved credit card patterns - handles formatted and run-together cards
        PIIType.CREDIT_CARD: r'\b(?:4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}|3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}|6(?:011|5\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b|(?<!\d)(?:4\d{15}|5[1-5]\d{14}|3[47]\d{13})(?!\d)',
        # Phone pattern - area code must start with 2-9, handles various formats  
        PIIType.PHONE: r'\b[2-9]\d{2}[-.\s]?\d{3}[-.\s]?\d{4}|\b\([2-9]\d{2}\)\s?\d{3}[-.\s]?\d{4}|\b[2-9]\d{9}(?!\d)',
        PIIType.IP_ADDRESS: r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        PIIType.URL: r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w.*))*)?',
        PIIType.DATE_OF_BIRTH: r'\b\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}\b|\b(?:19|20)\d{2}[/-]\d{1,2}[/-]\d{1,2}\b',
        # Address pattern: number + street name + (optional suite/apt) - includes Unicode
        PIIType.ADDRESS: r'\b\d+\s+[\w\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct)(?:\s*,?\s*(?:Suite|Apt|Apartment|Unit|#)\s*\d+)?\b',
    }
    
    def detect(self, text: str) -> List[PIIDetection]:
        """Detect PII using regex patterns in order of specificity."""
        detections = []
        
        # Process patterns in order (most specific first)
        for pii_type, pattern in self.PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                detection = PIIDetection(
                    pii_type=pii_type,
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,  # Higher confidence for improved patterns
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
                
                # Map Presidio type to our PIIType
                pii_type = self._map_presidio_type(result.entity_type)
                
                # Skip if we don't recognize this entity type
                if pii_type is None:
                    continue
                
                # Filter out false positive date detections
                if pii_type == PIIType.DATE_OF_BIRTH:
                    # Skip if it looks like a credit card, order number, SSN, or just a year
                    digits_only = detected_text.replace('-', '').replace('/', '').replace(' ', '')
                    if (len(digits_only) > 10 or  # Too long for date
                        detected_text.isdigit() and len(digits_only) == 4 or  # Just a year
                        len(digits_only) == 9 or  # Likely SSN
                        'card' in text.lower() or 'order' in text.lower() or 'ssn' in text.lower()):  # Context suggests not a date
                        continue
                
                # Filter out invalid phone numbers
                if pii_type == PIIType.PHONE:
                    # Skip phone numbers that don't start with valid area codes (2-9)
                    digits_only = ''.join(c for c in detected_text if c.isdigit())
                    if len(digits_only) >= 10 and digits_only[0] not in '23456789':
                        continue
                
                # Special handling for PERSON entities - check if they're actually addresses
                if pii_type == PIIType.NAME:
                    if self._looks_like_address(detected_text):
                        pii_type = PIIType.ADDRESS
                
                detection = PIIDetection(
                    pii_type=pii_type,
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
            'LOCATION': PIIType.LOCATION,
            'MONEY': PIIType.MONEY,
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
        
        # Don't default to NAME - ignore unknown types instead
        return mapping.get(presidio_type)
    
    def _looks_like_address(self, text: str) -> bool:
        """Check if text that was classified as PERSON is actually an address."""
        address_indicators = [
            # Street types
            r'\b\d+\s+[A-Za-z\s]+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl|Court|Ct)\b',
            # Suite/apartment indicators  
            r'\b(Suite|Apt|Apartment|Unit|#)\s*\d+\b',
            # Common address patterns
            r'\b\d+\s+[A-Za-z]+\s+(Street|Ave|Road)\b'
        ]
        
        for pattern in address_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


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
        
        # Add regex detector first to prioritize our address detection
        self.detectors.append(RegexPIIDetector())
        
        # Try Presidio second (for complex PII types regex can't handle)
        presidio_detector = PresidioDetector()
        if presidio_detector.available:
            self.detectors.append(presidio_detector)
        
        # High-performance detectors removed for production
        
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
                PIIType.LOCATION.value: RedactionStrategy.ALLOW.value,
                PIIType.MONEY.value: RedactionStrategy.ALLOW.value,
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
        unique_detections = []
        seen_spans = set()
        
        # Sort by priority: More specific types first, then by confidence
        def detection_priority(detection):
            # Prioritize specific types over generic ones - updated priority
            type_priority = {
                PIIType.SSN: 1,         # Most specific
                PIIType.CREDIT_CARD: 1, # Most specific  
                PIIType.EMAIL: 1,       # Most specific
                PIIType.ADDRESS: 2,     # Specific
                PIIType.IP_ADDRESS: 2,  # Specific
                PIIType.PHONE: 3,       # Can be ambiguous
                PIIType.NAME: 4,        # Generic, lower priority
                PIIType.LOCATION: 5,    # Very generic
            }
            priority = type_priority.get(detection.pii_type, 6)
            method_priority = 1 if detection.detection_method == "regex" else 2
            return (priority, method_priority, -detection.confidence)  # Lower numbers = higher priority
        
        sorted_detections = sorted(detections, key=detection_priority)
        
        for detection in sorted_detections:
            # Check for overlapping spans - be more strict about overlaps
            span = (detection.start_pos, detection.end_pos)
            overlaps = False
            
            for seen_span in seen_spans:
                # Two detections overlap if they share any characters
                if (detection.start_pos < seen_span[1] and detection.end_pos > seen_span[0]):
                    # Additional check: if this is a phone number that's contained within
                    # a credit card number, skip it
                    if (detection.pii_type == PIIType.PHONE and 
                        detection.start_pos >= seen_span[0] and 
                        detection.end_pos <= seen_span[1]):
                        overlaps = True
                        break
                    # General overlap
                    elif detection.start_pos < seen_span[1] and detection.end_pos > seen_span[0]:
                        overlaps = True
                        break
            
            if not overlaps:
                unique_detections.append(detection)
                seen_spans.add(span)
        
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
                PIIType.LOCATION: "[LOCATION_REDACTED]",
                PIIType.MONEY: "[MONEY_REDACTED]",
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
                PIIType.LOCATION: f"[LOCATION_{hash_value}]",
                PIIType.MONEY: f"[MONEY_{hash_value}]",
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