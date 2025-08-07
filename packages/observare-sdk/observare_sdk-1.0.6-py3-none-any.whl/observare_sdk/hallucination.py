"""
Hallucination Detection Engine for Observare SDK

Implements multiple hallucination detection methods:
- Self-consistency checking
- Chain of Verification (CoVe)
- UQLM integration for uncertainty quantification
- Confidence scoring with semantic similarity
"""

import asyncio
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict

# Suppress noisy logs from this module
logging.getLogger(__name__).setLevel(logging.WARNING)
from datetime import datetime
from enum import Enum
import hashlib
import time

# LangChain imports for Chain of Verification
try:
    from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain.schema.language_model import BaseLanguageModel
    from langchain.prompts import ChatPromptTemplate, PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseLanguageModel = None

# Optional UQLM integration
try:
    import uqlm
    UQLM_AVAILABLE = True
except ImportError:
    UQLM_AVAILABLE = False

# Semantic similarity for consistency checking
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        SKLEARN_AVAILABLE = True
    except ImportError:
        SKLEARN_AVAILABLE = False
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class HallucinationMethod(Enum):
    """Available hallucination detection methods."""
    SELF_CONSISTENCY = "self_consistency"
    CHAIN_OF_VERIFICATION = "cove"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    HYBRID = "hybrid"


class ConfidenceLevel(Enum):
    """Confidence levels for hallucination detection."""
    HIGH_CONFIDENCE = "high"      # < 0.2 hallucination probability
    MEDIUM_CONFIDENCE = "medium"  # 0.2 - 0.5 hallucination probability
    LOW_CONFIDENCE = "low"        # 0.5 - 0.8 hallucination probability
    VERY_LOW_CONFIDENCE = "very_low"  # > 0.8 hallucination probability


@dataclass
class HallucinationDetection:
    """Result of hallucination detection analysis."""
    original_response: str
    hallucination_probability: float
    confidence_level: ConfidenceLevel
    detection_method: str
    supporting_evidence: Dict[str, Any]
    recommendations: List[str]
    processing_time_ms: float
    metadata: Dict[str, Any]


@dataclass
class ConsistencyCheckResult:
    """Result of self-consistency checking."""
    responses: List[str]
    consistency_score: float
    semantic_similarity_scores: List[float]
    outlier_responses: List[str]
    consensus_response: str
    disagreement_areas: List[str]


@dataclass
class VerificationResult:
    """Result of Chain of Verification process."""
    original_claim: str
    verification_questions: List[str]
    verification_answers: List[str]
    consistency_score: float
    contradictions: List[str]
    verified_facts: List[str]
    unverified_claims: List[str]


class SemanticSimilarityCalculator:
    """Calculate semantic similarity between texts using available libraries."""
    
    def __init__(self):
        self.method = None
        self.model = None
        
        # Try sentence transformers first (most accurate)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.method = "sentence_transformers"
            except Exception:
                self.model = None
        
        # Fallback to sklearn TF-IDF
        if self.model is None and SKLEARN_AVAILABLE:
            self.model = TfidfVectorizer()
            self.method = "tfidf"
        
        # Final fallback to simple text overlap
        if self.model is None:
            self.method = "text_overlap"
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not text1 or not text2:
            return 0.0
        
        try:
            if self.method == "sentence_transformers":
                embeddings = self.model.encode([text1, text2])
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
            
            elif self.method == "tfidf":
                tfidf_matrix = self.model.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            
            else:
                # Simple text overlap fallback
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                return len(intersection) / len(union) if union else 0.0
        
        except Exception:
            return 0.0
    
    def calculate_batch_similarity(self, reference_text: str, texts: List[str]) -> List[float]:
        """Calculate similarity between reference text and a batch of texts."""
        similarities = []
        for text in texts:
            similarity = self.calculate_similarity(reference_text, text)
            similarities.append(similarity)
        return similarities


class SelfConsistencyChecker:
    """Implements self-consistency checking for hallucination detection."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm
        self.similarity_calculator = SemanticSimilarityCalculator()
    
    async def check_consistency(
        self, 
        prompt: str, 
        num_samples: int = 3,
        temperature: float = 0.7
    ) -> ConsistencyCheckResult:
        """
        Generate multiple responses and check their consistency.
        
        Args:
            prompt: The original prompt/question
            num_samples: Number of response samples to generate
            temperature: Temperature for response generation
            
        Returns:
            ConsistencyCheckResult with consistency analysis
        """
        if not self.llm:
            raise ValueError("LLM not available for consistency checking")
        
        # Generate multiple responses
        responses = []
        for i in range(num_samples):
            try:
                if hasattr(self.llm, 'agenerate'):
                    # Async generation if available
                    result = await self.llm.agenerate([prompt])
                    response = result.generations[0][0].text
                else:
                    # Synchronous fallback
                    response = self.llm.generate([prompt]).generations[0][0].text
                
                responses.append(response.strip())
            except Exception as e:
                # If generation fails, skip this sample
                continue
        
        if len(responses) < 2:
            # Not enough responses for consistency checking
            return ConsistencyCheckResult(
                responses=responses,
                consistency_score=0.0,
                semantic_similarity_scores=[],
                outlier_responses=[],
                consensus_response=responses[0] if responses else "",
                disagreement_areas=["Insufficient responses for consistency analysis"]
            )
        
        # Calculate pairwise semantic similarities
        similarity_scores = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = self.similarity_calculator.calculate_similarity(
                    responses[i], responses[j]
                )
                similarity_scores.append(similarity)
        
        # Calculate overall consistency score
        consistency_score = np.mean(similarity_scores) if similarity_scores else 0.0
        
        # Identify outlier responses (those with low similarity to others)
        outlier_responses = []
        for i, response in enumerate(responses):
            similarities_to_others = []
            for j, other_response in enumerate(responses):
                if i != j:
                    sim = self.similarity_calculator.calculate_similarity(response, other_response)
                    similarities_to_others.append(sim)
            
            avg_similarity = np.mean(similarities_to_others) if similarities_to_others else 0.0
            if avg_similarity < 0.5:  # Threshold for outlier detection
                outlier_responses.append(response)
        
        # Find consensus response (most similar to all others on average)
        consensus_response = responses[0]
        if len(responses) > 1:
            best_avg_similarity = 0
            for response in responses:
                avg_sim = np.mean([
                    self.similarity_calculator.calculate_similarity(response, other)
                    for other in responses if other != response
                ])
                if avg_sim > best_avg_similarity:
                    best_avg_similarity = avg_sim
                    consensus_response = response
        
        # Identify disagreement areas (simplified)
        disagreement_areas = []
        if consistency_score < 0.7:
            disagreement_areas.append("Low overall consistency between responses")
        if len(outlier_responses) > 0:
            disagreement_areas.append(f"Found {len(outlier_responses)} outlier response(s)")
        if len(set(responses)) == len(responses):
            disagreement_areas.append("All responses are unique - no clear consensus")
        
        return ConsistencyCheckResult(
            responses=responses,
            consistency_score=consistency_score,
            semantic_similarity_scores=similarity_scores,
            outlier_responses=outlier_responses,
            consensus_response=consensus_response,
            disagreement_areas=disagreement_areas
        )


class ChainOfVerificationChecker:
    """Implements Chain of Verification (CoVe) for hallucination detection."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None):
        self.llm = llm
        
        # CoVe prompts
        self.question_generation_prompt = PromptTemplate(
            input_variables=["response"],
            template="""
Given this response, generate 3-5 specific verification questions that would help fact-check the claims made:

Response: {response}

Generate verification questions that are:
1. Specific and factual
2. Can be answered with concrete information
3. Cover the main claims in the response

Verification Questions:
"""
        )
        
        self.verification_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
Answer this verification question with factual information. Be specific and cite sources if possible:

Question: {question}

Answer:
"""
        )
        
        self.consistency_check_prompt = PromptTemplate(
            input_variables=["original_response", "verification_qa"],
            template="""
Compare the original response with the verification question-answer pairs. Identify any contradictions or inconsistencies:

Original Response: {original_response}

Verification Q&A:
{verification_qa}

Analysis:
1. Are there any contradictions between the original response and the verification answers?
2. Which facts from the original response are supported by the verification?
3. Which claims remain unverified or contradicted?

Provide a structured analysis:
"""
        )
    
    async def verify_response(self, response: str) -> VerificationResult:
        """
        Perform Chain of Verification on a response.
        
        Args:
            response: The LLM response to verify
            
        Returns:
            VerificationResult with verification analysis
        """
        if not self.llm or not LANGCHAIN_AVAILABLE:
            # Return minimal result if dependencies not available
            return VerificationResult(
                original_claim=response,
                verification_questions=[],
                verification_answers=[],
                consistency_score=0.5,  # Neutral score
                contradictions=["Verification not available - missing dependencies"],
                verified_facts=[],
                unverified_claims=[response]
            )
        
        try:
            # Step 1: Generate verification questions
            question_chain = self.question_generation_prompt | self.llm
            questions_result = await question_chain.ainvoke({"response": response})
            questions_response = questions_result.content if hasattr(questions_result, 'content') else str(questions_result)
            
            # Parse questions (simple parsing - could be improved)
            verification_questions = [
                q.strip() for q in questions_response.split('\n') 
                if q.strip() and not q.strip().startswith('Verification Questions:')
            ][:5]  # Limit to 5 questions
            
            # Step 2: Answer verification questions
            verification_answers = []
            verification_chain = self.verification_prompt | self.llm
            
            for question in verification_questions:
                try:
                    answer_result = await verification_chain.ainvoke({"question": question})
                    answer = answer_result.content if hasattr(answer_result, 'content') else str(answer_result)
                    verification_answers.append(answer.strip())
                except Exception:
                    verification_answers.append("Could not generate verification answer")
            
            # Step 3: Check consistency
            verification_qa = "\n".join([
                f"Q: {q}\nA: {a}\n"
                for q, a in zip(verification_questions, verification_answers)
            ])
            
            consistency_chain = self.consistency_check_prompt | self.llm
            consistency_result = await consistency_chain.ainvoke({
                "original_response": response,
                "verification_qa": verification_qa
            })
            consistency_analysis = consistency_result.content if hasattr(consistency_result, 'content') else str(consistency_result)
            
            # Parse consistency analysis (simplified - could use structured output)
            contradictions = []
            verified_facts = []
            unverified_claims = []
            
            # Simple parsing of the analysis
            lines = consistency_analysis.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if 'contradiction' in line.lower():
                    current_section = 'contradictions'
                elif 'supported' in line.lower() or 'verified' in line.lower():
                    current_section = 'verified'
                elif 'unverified' in line.lower():
                    current_section = 'unverified'
                elif line and not line.startswith(('1.', '2.', '3.', 'Analysis:')):
                    if current_section == 'contradictions':
                        contradictions.append(line)
                    elif current_section == 'verified':
                        verified_facts.append(line)
                    elif current_section == 'unverified':
                        unverified_claims.append(line)
            
            # Calculate consistency score based on contradictions vs verified facts
            total_claims = len(verified_facts) + len(contradictions) + len(unverified_claims)
            if total_claims > 0:
                consistency_score = len(verified_facts) / total_claims
            else:
                consistency_score = 0.5  # Neutral if no clear analysis
            
            return VerificationResult(
                original_claim=response,
                verification_questions=verification_questions,
                verification_answers=verification_answers,
                consistency_score=consistency_score,
                contradictions=contradictions,
                verified_facts=verified_facts,
                unverified_claims=unverified_claims
            )
        
        except Exception as e:
            # Fallback result on error
            return VerificationResult(
                original_claim=response,
                verification_questions=[],
                verification_answers=[],
                consistency_score=0.5,
                contradictions=[f"Verification failed: {str(e)}"],
                verified_facts=[],
                unverified_claims=[response]
            )


# UQLM integration removed - placeholder implementation


class HallucinationDetectionEngine:
    """Main hallucination detection engine combining multiple methods."""
    
    def __init__(self, llm: Optional[BaseLanguageModel] = None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize hallucination detection engine.
        
        Args:
            llm: Language model for verification and consistency checking
            config: Configuration for detection methods and thresholds
        """
        self.llm = llm
        self.config = config or self._default_config()
        
        # Initialize detection components
        self.consistency_checker = SelfConsistencyChecker(llm)
        self.cove_checker = ChainOfVerificationChecker(llm)
        
        # Statistics tracking
        self.stats = {
            'total_detections': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'very_low_confidence': 0,
            'methods_used': {method.value: 0 for method in HallucinationMethod}
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for hallucination detection."""
        return {
            'enabled': True,
            'method': HallucinationMethod.HYBRID.value,
            'thresholds': {
                'high_confidence': 0.2,
                'medium_confidence': 0.5,
                'low_confidence': 0.8
            },
            'consistency_samples': 3,
            'consistency_temperature': 0.7,
            'enable_cove': True,
            'enable_uqlm': True,
            'timeout_seconds': 30
        }
    
    async def detect_hallucination(
        self, 
        prompt: str, 
        response: str, 
        method: Optional[HallucinationMethod] = None
    ) -> HallucinationDetection:
        """
        Detect potential hallucinations in an LLM response.
        
        Args:
            prompt: Original prompt/question
            response: LLM response to analyze
            method: Detection method to use (defaults to config method)
            
        Returns:
            HallucinationDetection with analysis results
        """
        start_time = time.time()
        
        if not self.config.get('enabled', True):
            return self._create_neutral_result(prompt, response, start_time)
        
        method = method or HallucinationMethod(self.config.get('method', 'hybrid'))
        
        # Track method usage
        self.stats['methods_used'][method.value] += 1
        
        try:
            if method == HallucinationMethod.SELF_CONSISTENCY:
                result = await self._detect_via_consistency(prompt, response)
            elif method == HallucinationMethod.CHAIN_OF_VERIFICATION:
                result = await self._detect_via_cove(prompt, response)
            elif method == HallucinationMethod.UQLM_UNCERTAINTY:
                result = await self._detect_via_uqlm(prompt, response)
            elif method == HallucinationMethod.SEMANTIC_SIMILARITY:
                result = await self._detect_via_semantic_similarity(prompt, response)
            elif method == HallucinationMethod.HYBRID:
                result = await self._detect_via_hybrid(prompt, response)
            else:
                result = await self._detect_via_hybrid(prompt, response)
        
        except Exception as e:
            # Fallback to neutral result on error
            result = self._create_neutral_result(prompt, response, start_time)
            result.supporting_evidence['error'] = str(e)
            result.recommendations.append("Detection failed due to error - manual review recommended")
        
        # Update statistics
        self.stats['total_detections'] += 1
        confidence_key = (
            result.confidence_level.value 
            if hasattr(result.confidence_level, 'value') 
            else str(result.confidence_level)
        )
        
        # Handle confidence key mapping for stats
        if confidence_key in self.stats:
            self.stats[confidence_key] += 1
        else:
            # Map simple confidence levels to stats keys
            confidence_mapping = {
                'high': 'high_confidence',
                'medium': 'medium_confidence', 
                'low': 'low_confidence',
                'very_low': 'very_low_confidence'
            }
            stats_key = confidence_mapping.get(confidence_key, 'low_confidence')  # default fallback
            if stats_key not in self.stats:
                self.stats[stats_key] = 0
            self.stats[stats_key] += 1
        
        return result
    
    async def _detect_via_consistency(self, prompt: str, response: str) -> HallucinationDetection:
        """Detect hallucinations using self-consistency checking."""
        start_time = time.time()
        
        consistency_result = await self.consistency_checker.check_consistency(
            prompt=prompt,
            num_samples=self.config.get('consistency_samples', 3),
            temperature=self.config.get('consistency_temperature', 0.7)
        )
        
        # Calculate hallucination probability from consistency score
        # Low consistency = high hallucination probability
        hallucination_prob = 1.0 - consistency_result.consistency_score
        
        confidence_level = self._calculate_confidence_level(hallucination_prob)
        
        recommendations = []
        if hallucination_prob > 0.8:
            recommendations.append("High hallucination risk - response shows low consistency")
            recommendations.append("Consider regenerating response or seeking additional verification")
        elif hallucination_prob > 0.5:
            recommendations.append("Medium hallucination risk - some inconsistencies detected")
            recommendations.append("Cross-check important facts before using this response")
        else:
            recommendations.append("Low hallucination risk - response shows good consistency")
        
        if len(consistency_result.outlier_responses) > 0:
            recommendations.append(f"Found {len(consistency_result.outlier_responses)} outlier responses")
        
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=hallucination_prob,
            confidence_level=confidence_level,
            detection_method="self_consistency",
            supporting_evidence={
                'consistency_score': consistency_result.consistency_score,
                'num_responses': len(consistency_result.responses),
                'similarity_scores': consistency_result.semantic_similarity_scores,
                'outlier_count': len(consistency_result.outlier_responses),
                'disagreement_areas': consistency_result.disagreement_areas
            },
            recommendations=recommendations,
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={
                'consensus_response': consistency_result.consensus_response,
                'all_responses': consistency_result.responses
            }
        )
    
    async def _detect_via_cove(self, prompt: str, response: str) -> HallucinationDetection:
        """Detect hallucinations using Chain of Verification."""
        start_time = time.time()
        
        verification_result = await self.cove_checker.verify_response(response)
        
        # Calculate hallucination probability from verification results
        total_claims = (
            len(verification_result.verified_facts) + 
            len(verification_result.contradictions) + 
            len(verification_result.unverified_claims)
        )
        
        if total_claims > 0:
            # High contradictions = high hallucination probability
            contradiction_ratio = len(verification_result.contradictions) / total_claims
            unverified_ratio = len(verification_result.unverified_claims) / total_claims
            hallucination_prob = contradiction_ratio + (unverified_ratio * 0.5)
        else:
            hallucination_prob = 0.5  # Neutral if no clear verification
        
        confidence_level = self._calculate_confidence_level(hallucination_prob)
        
        recommendations = []
        if len(verification_result.contradictions) > 0:
            recommendations.append(f"Found {len(verification_result.contradictions)} contradictions in verification")
            recommendations.append("High hallucination risk - response contradicts verification")
        
        if len(verification_result.unverified_claims) > 0:
            recommendations.append(f"Found {len(verification_result.unverified_claims)} unverified claims")
            recommendations.append("Some claims could not be verified - proceed with caution")
        
        if len(verification_result.verified_facts) > 0:
            recommendations.append(f"Verified {len(verification_result.verified_facts)} factual claims")
        
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=hallucination_prob,
            confidence_level=confidence_level,
            detection_method="chain_of_verification",
            supporting_evidence={
                'verification_questions': verification_result.verification_questions,
                'verification_answers': verification_result.verification_answers,
                'consistency_score': verification_result.consistency_score,
                'contradictions': verification_result.contradictions,
                'verified_facts': verification_result.verified_facts,
                'unverified_claims': verification_result.unverified_claims
            },
            recommendations=recommendations,
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={
                'verification_method': 'cove',
                'total_claims_analyzed': total_claims
            }
        )
    
    async def _detect_via_uqlm(self, prompt: str, response: str) -> HallucinationDetection:
        """Detect hallucinations using UQLM uncertainty quantification."""
        start_time = time.time()
        
        uncertainty_metrics = self.uqlm_detector.calculate_uncertainty(prompt, response, self.llm)
        
        # Use total uncertainty as hallucination probability
        hallucination_prob = uncertainty_metrics.get('total_uncertainty', 0.5)
        confidence_level = self._calculate_confidence_level(hallucination_prob)
        
        recommendations = []
        if uncertainty_metrics.get('semantic_uncertainty', 0) > 0.7:
            recommendations.append("High semantic uncertainty detected")
            recommendations.append("Response may contain inconsistent or contradictory information")
        
        if uncertainty_metrics.get('epistemic_uncertainty', 0) > 0.7:
            recommendations.append("High epistemic uncertainty - model may lack knowledge in this domain")
        
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=hallucination_prob,
            confidence_level=confidence_level,
            detection_method="uqlm_uncertainty",
            supporting_evidence=uncertainty_metrics,
            recommendations=recommendations,
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={
                'uqlm_available': self.uqlm_detector.available,
                'uncertainty_method': 'sampling_based'
            }
        )
    
    async def _detect_via_semantic_similarity(self, prompt: str, response: str) -> HallucinationDetection:
        """Detect hallucinations using semantic similarity analysis."""
        start_time = time.time()
        
        # This is a simplified implementation
        # In practice, you'd compare against known facts or trusted sources
        
        # For now, we'll generate alternative responses and check similarity
        alternatives = []
        if self.llm:
            try:
                for _ in range(3):
                    alt_response = self.llm.generate([prompt]).generations[0][0].text
                    alternatives.append(alt_response)
            except Exception:
                pass
        
        if alternatives:
            similarity_calculator = SemanticSimilarityCalculator()
            similarities = similarity_calculator.calculate_batch_similarity(response, alternatives)
            avg_similarity = np.mean(similarities) if similarities else 0.5
            hallucination_prob = 1.0 - avg_similarity
        else:
            hallucination_prob = 0.5  # Neutral if no alternatives
        
        confidence_level = self._calculate_confidence_level(hallucination_prob)
        
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=hallucination_prob,
            confidence_level=confidence_level,
            detection_method="semantic_similarity",
            supporting_evidence={
                'alternative_responses': alternatives,
                'similarity_scores': similarities if alternatives else [],
                'avg_similarity': avg_similarity if alternatives else 0.5
            },
            recommendations=["Semantic similarity analysis completed"],
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={
                'num_alternatives': len(alternatives),
                'similarity_method': similarity_calculator.method
            }
        )
    
    async def _detect_via_hybrid(self, prompt: str, response: str) -> HallucinationDetection:
        """Detect hallucinations using hybrid approach combining multiple methods."""
        start_time = time.time()
        
        # Run multiple detection methods in parallel if possible
        methods_to_run = []
        
        if self.llm:
            methods_to_run.extend([
                self._detect_via_consistency(prompt, response),
                self._detect_via_semantic_similarity(prompt, response)
            ])
            
            if self.config.get('enable_cove', True):
                methods_to_run.append(self._detect_via_cove(prompt, response))
        
        if self.config.get('enable_uqlm', True):
            methods_to_run.append(self._detect_via_uqlm(prompt, response))
        
        # Run all methods
        results = []
        for method in methods_to_run:
            try:
                result = await method
                results.append(result)
            except Exception:
                continue
        
        if not results:
            return self._create_neutral_result(prompt, response, start_time)
        
        # Combine results
        hallucination_probs = [r.hallucination_probability for r in results]
        combined_prob = np.mean(hallucination_probs)
        confidence_level = self._calculate_confidence_level(combined_prob)
        
        # Combine supporting evidence
        combined_evidence = {}
        all_recommendations = []
        
        for result in results:
            combined_evidence[f"{result.detection_method}_result"] = {
                'probability': result.hallucination_probability,
                'evidence': result.supporting_evidence
            }
            all_recommendations.extend(result.recommendations)
        
        # Remove duplicate recommendations
        unique_recommendations = list(set(all_recommendations))
        
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=combined_prob,
            confidence_level=confidence_level,
            detection_method="hybrid",
            supporting_evidence=combined_evidence,
            recommendations=unique_recommendations,
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={
                'methods_used': [r.detection_method for r in results],
                'individual_probabilities': hallucination_probs,
                'num_methods': len(results)
            }
        )
    
    def _calculate_confidence_level(self, hallucination_prob: float) -> ConfidenceLevel:
        """Calculate confidence level from hallucination probability."""
        thresholds = self.config.get('thresholds', {})
        
        if hallucination_prob <= thresholds.get('high_confidence', 0.2):
            return ConfidenceLevel.HIGH_CONFIDENCE
        elif hallucination_prob <= thresholds.get('medium_confidence', 0.5):
            return ConfidenceLevel.MEDIUM_CONFIDENCE
        elif hallucination_prob <= thresholds.get('low_confidence', 0.8):
            return ConfidenceLevel.LOW_CONFIDENCE
        else:
            return ConfidenceLevel.VERY_LOW_CONFIDENCE
    
    def _create_neutral_result(self, prompt: str, response: str, start_time: float) -> HallucinationDetection:
        """Create a neutral result when detection is not possible."""
        return HallucinationDetection(
            original_response=response,
            hallucination_probability=0.5,
            confidence_level=ConfidenceLevel.MEDIUM_CONFIDENCE,
            detection_method="fallback",
            supporting_evidence={'status': 'detection_unavailable'},
            recommendations=["Hallucination detection unavailable - manual review recommended"],
            processing_time_ms=(time.time() - start_time) * 1000,
            metadata={'fallback_reason': 'detection_method_unavailable'}
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get hallucination detection statistics."""
        return self.stats.copy()


# Convenience functions
async def detect_hallucination(
    prompt: str, 
    response: str, 
    llm: Optional[BaseLanguageModel] = None,
    method: HallucinationMethod = HallucinationMethod.HYBRID,
    config: Optional[Dict[str, Any]] = None
) -> HallucinationDetection:
    """Convenience function for hallucination detection."""
    engine = HallucinationDetectionEngine(llm, config)
    return await engine.detect_hallucination(prompt, response, method)


# Production module - test code removed