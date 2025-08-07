"""
Observare LLM Safety Wrapper

Provides LLM wrappers with integrated PII redaction, hallucination detection,
and comprehensive observability while maintaining full LangChain compatibility.
"""

import asyncio
import time
import warnings
import logging
from typing import Dict, List, Any, Optional, Union, Iterator, AsyncIterator, Callable
from datetime import datetime
from pydantic import Field

# Suppress noisy logs from this module
logging.getLogger(__name__).setLevel(logging.WARNING)

# LangChain imports
try:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.language_models.llms import BaseLLM
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from langchain_core.outputs import ChatResult, LLMResult, ChatGeneration, Generation
    from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
    from langchain_core.runnables import RunnableConfig
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    try:
        from langchain.schema.language_model import BaseChatModel, BaseLLM
        from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
        from langchain.schema.output import ChatResult, LLMResult, ChatGeneration, Generation
        from langchain.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
        LANGCHAIN_CORE_AVAILABLE = False
    except ImportError:
        raise ImportError("LangChain is required for ObservareChat. Please install langchain or langchain-core.")

# Import our safety modules
try:
    from .pii import PIIRedactionEngine, PIIRedactionResult
    from .hallucination import HallucinationDetectionEngine, HallucinationDetection, HallucinationMethod
    from .config import SafetyConfiguration, SafetyConfigurationManager, SafetyPolicy
    from .sdk import AutoTelemetryHandler, TelemetryEvent
    OBSERVARE_MODULES_AVAILABLE = True
except ImportError:
    OBSERVARE_MODULES_AVAILABLE = False
    warnings.warn("Observare safety modules not available. Safety features will be disabled.")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafetyViolationError(Exception):
    """Raised when safety thresholds are exceeded."""
    pass


class ObservareChat(BaseChatModel):
    """
    LangChain-compatible chat model wrapper with integrated safety features.
    
    Provides PII redaction, hallucination detection, and comprehensive telemetry
    while maintaining full compatibility with LangChain's BaseChatModel interface.
    """
    
    # Declare pydantic fields for all instance attributes
    fail_safe: bool = Field(default=True, description="Continue operation if safety checks fail")
    config_manager: Any = Field(default=None, description="Safety configuration manager")
    pii_engine: Any = Field(default=None, description="PII redaction engine")
    hallucination_engine: Any = Field(default=None, description="Hallucination detection engine")
    telemetry_handler: Any = Field(default=None, description="Telemetry handler")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Statistics tracking")
    underlying_llm: Any = Field(default=None, description="Underlying LLM")
    
    def __init__(
        self,
        llm: BaseChatModel,
        config: Optional[Union[SafetyConfiguration, str, Dict[str, Any]]] = None,
        api_key: Optional[str] = None,
        telemetry_enabled: bool = True,
        fail_safe: bool = True,
        debug_mode: bool = False,
        **kwargs
    ):
        """
        Initialize ObservareChat wrapper.
        
        Args:
            llm: Underlying LangChain chat model to wrap
            config: Safety configuration (object, file path, or dict)
            api_key: Observare API key for telemetry
            telemetry_enabled: Whether to enable telemetry
            fail_safe: Continue operation if safety checks fail
            **kwargs: Additional arguments passed to BaseChatModel
        """
        # Initialize pydantic model with default values
        super().__init__(
            fail_safe=fail_safe,
            config_manager=SafetyConfigurationManager(),
            pii_engine=None,
            hallucination_engine=None,
            telemetry_handler=None,
            stats={
                'total_requests': 0,
                'pii_redactions': 0,
                'hallucination_detections': 0,
                'safety_violations': 0,
                'processing_time_ms': 0.0
            },
            underlying_llm=llm,
            **kwargs
        )
        
        # Handle configuration after initialization
        if isinstance(config, str):
            # Config file path
            self.config_manager.load_from_file(config)
        elif isinstance(config, dict):
            # Config dictionary - convert to SafetyConfiguration
            self.config_manager.config = SafetyConfiguration(**config)
        elif isinstance(config, SafetyConfiguration):
            # Direct configuration object
            self.config_manager.config = config
        elif config is None:
            # Use default balanced configuration
            self.config_manager.apply_policy(SafetyPolicy.BALANCED)
        
        # Override API key if provided
        if api_key:
            self.config_manager.config.telemetry.api_key = api_key
        
        if OBSERVARE_MODULES_AVAILABLE:
            try:
                # Initialize PII redaction engine
                if self.config_manager.config.pii.enabled:
                    pii_config = {
                        'enabled': self.config_manager.config.pii.enabled,
                        'strategies': self.config_manager.config.pii.strategies,
                        'min_confidence': self.config_manager.config.pii.min_confidence_threshold,
                        'preserve_structure': self.config_manager.config.pii.preserve_structure,
                        'hash_salt': self.config_manager.config.pii.hash_salt
                    }
                    self.pii_engine = PIIRedactionEngine(pii_config)
                
                # Initialize hallucination detection engine
                if self.config_manager.config.hallucination.enabled:
                    logger.debug("🧠 Initializing hallucination detection engine...")
                    hallucination_config = {
                        'enabled': self.config_manager.config.hallucination.enabled,
                        'method': self.config_manager.config.hallucination.detection_method,
                        'thresholds': self.config_manager.config.hallucination.confidence_thresholds,
                        'consistency_samples': self.config_manager.config.hallucination.consistency_samples,
                        'consistency_temperature': self.config_manager.config.hallucination.consistency_temperature,
                        'enable_cove': self.config_manager.config.hallucination.enable_chain_of_verification,
                        'enable_uqlm': self.config_manager.config.hallucination.enable_uqlm,
                        'timeout_seconds': self.config_manager.config.hallucination.timeout_seconds
                    }
                    self.hallucination_engine = HallucinationDetectionEngine(self.underlying_llm, hallucination_config)
                    logger.debug(f"✅ Hallucination detection enabled with method: {self.config_manager.config.hallucination.detection_method}")
                else:
                    logger.debug("⚠️  Hallucination detection disabled")
                
            except Exception as e:
                logger.debug(f"Failed to initialize safety engines: {e}")
                if not getattr(self, 'fail_safe', True):
                    raise
        
        # Initialize telemetry handler
        if telemetry_enabled and self.config_manager.config.telemetry.enabled:
            try:
                self.telemetry_handler = AutoTelemetryHandler(
                    api_key=self.config_manager.config.telemetry.api_key,
                    agent_id=f"observare_chat_{int(time.time())}",
                    debug_mode=debug_mode
                )
            except Exception as e:
                logger.debug(f"Failed to initialize telemetry: {e}")
                if not getattr(self, 'fail_safe', True):
                    raise
    
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this LLM type."""
        try:
            return f"observare_chat_{self.underlying_llm._llm_type}"
        except AttributeError:
            return "observare_chat"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get identifying parameters."""
        try:
            underlying_params = self.underlying_llm._identifying_params if hasattr(self.underlying_llm, '_identifying_params') else {}
        except AttributeError:
            underlying_params = {}
            
        params = {
            'underlying_llm': underlying_params,
            'pii_enabled': self.config_manager.config.pii.enabled,
            'hallucination_enabled': self.config_manager.config.hallucination.enabled,
            'safety_policy': self.config_manager.config.policy,
            'fail_safe': getattr(self, 'fail_safe', True)
        }
        return params
    
    # Additional LangChain compatibility properties
    @property
    def model_name(self) -> str:
        """Get model name for compatibility."""
        try:
            return getattr(self.underlying_llm, 'model_name', getattr(self.underlying_llm, 'model', 'observare_chat'))
        except AttributeError:
            return 'observare_chat'
    
    @property
    def llm(self):
        """Access to underlying LLM for compatibility."""
        return self.underlying_llm
    
    @llm.setter
    def llm(self, value):
        """Set underlying LLM."""
        self.underlying_llm = value
    
    def invoke(self, input, config=None, **kwargs):
        """Override invoke to ensure safety processing for all calls."""
        # ObservareChat invoke called
        
        # Handle different input formats
        if isinstance(input, str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=input)]
        elif isinstance(input, list) and all(hasattr(msg, 'content') for msg in input):
            messages = input
        else:
            # For non-standard inputs, fall back to parent class
            # Using parent invoke for non-standard input
            return super().invoke(input, config=config, **kwargs)
        
        # Use _generate with safety processing
        result = self._generate(messages, **kwargs)
        return result.generations[0].message if result.generations else None
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response with safety processing."""
        # ObservareChat _generate called
        start_time = time.time()
        
        # Use conversation-level correlation_id from telemetry handler, fallback to run_id
        import uuid
        correlation_id = (
            self.telemetry_handler.get_conversation_correlation_id() 
            if self.telemetry_handler and self.telemetry_handler.get_conversation_correlation_id()
            else (str(run_manager.run_id) if run_manager and hasattr(run_manager, 'run_id') else str(uuid.uuid4()))
        )
        
        try:
            # Step 1: Pre-process messages for PII redaction
            processed_messages, pii_results = self._preprocess_messages(messages, correlation_id)
            
            # Log message processing (NEVER log original content for security)
            logger.debug(f"🔍 Processing {len(messages)} messages for PII detection")
            
            logger.debug("🛡️  Processed messages (after PII redaction):")
            for i, msg in enumerate(processed_messages):
                logger.debug(f"   {i+1}. [{type(msg).__name__}] {msg.content}")
            
            if pii_results:
                logger.debug(f"🔒 PII redactions applied: {sum(r.total_redactions for r in pii_results)}")
            
            # Step 2: Generate response using underlying LLM
            # Ensure telemetry handler gets the callbacks by adding it to the underlying LLM
            if self.telemetry_handler and hasattr(self.underlying_llm, 'callbacks'):
                # Add telemetry handler to underlying LLM callbacks if not already present
                if not hasattr(self.underlying_llm.callbacks, '__iter__'):
                    self.underlying_llm.callbacks = []
                if self.telemetry_handler not in self.underlying_llm.callbacks:
                    self.underlying_llm.callbacks.append(self.telemetry_handler)
            
            chat_result = self.underlying_llm._generate(
                processed_messages, 
                stop=stop, 
                run_manager=run_manager,
                **kwargs
            )
            
            # Step 3: Post-process response for hallucination detection
            # Starting hallucination detection
            enhanced_result = self._postprocess_response(
                messages, processed_messages, chat_result, pii_results, correlation_id
            )
            # Hallucination detection completed
            
            # Step 4: Calculate processing time and extract token usage
            processing_time = (time.time() - start_time) * 1000
            self._extract_and_emit_token_usage(chat_result, correlation_id, processing_time)
            
            # Step 4.5: Emit LLM conversation event with prompt and response
            self._emit_llm_conversation_event(processed_messages, chat_result, correlation_id, processing_time)
            
            # Step 5: Update statistics and telemetry
            self._update_stats(processing_time, pii_results, None)
            
            return enhanced_result
            
        except Exception as e:
            # Handle errors according to fail_safe setting
            processing_time = (time.time() - start_time) * 1000
            self._log_error("_generate", e, processing_time)
            
            if getattr(self, 'fail_safe', True):
                # Return original LLM response without safety processing
                return self.underlying_llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
            else:
                raise
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate chat response with safety processing."""
        start_time = time.time()
        
        # Use conversation-level correlation_id from telemetry handler, fallback to run_id
        import uuid
        correlation_id = (
            self.telemetry_handler.get_conversation_correlation_id() 
            if self.telemetry_handler and self.telemetry_handler.get_conversation_correlation_id()
            else (str(run_manager.run_id) if run_manager and hasattr(run_manager, 'run_id') else str(uuid.uuid4()))
        )
        
        try:
            # Step 1: Pre-process messages for PII redaction
            processed_messages, pii_results = self._preprocess_messages(messages, correlation_id)
            
            # Log message processing (NEVER log original content for security)
            logger.debug(f"🔍 Processing {len(messages)} messages for PII detection (async)")
            
            logger.debug("🛡️  Processed messages (after PII redaction):")
            for i, msg in enumerate(processed_messages):
                logger.debug(f"   {i+1}. [{type(msg).__name__}] {msg.content}")
            
            if pii_results:
                logger.debug(f"🔒 PII redactions applied: {sum(r.total_redactions for r in pii_results)}")
            
            # Step 2: Generate response using underlying LLM
            # Ensure telemetry handler gets the callbacks by adding it to the underlying LLM
            if self.telemetry_handler and hasattr(self.underlying_llm, 'callbacks'):
                # Add telemetry handler to underlying LLM callbacks if not already present
                if not hasattr(self.underlying_llm.callbacks, '__iter__'):
                    self.underlying_llm.callbacks = []
                if self.telemetry_handler not in self.underlying_llm.callbacks:
                    self.underlying_llm.callbacks.append(self.telemetry_handler)
            
            if hasattr(self.underlying_llm, '_agenerate'):
                chat_result = await self.underlying_llm._agenerate(
                    processed_messages, 
                    stop=stop, 
                    run_manager=run_manager,
                    **kwargs
                )
            else:
                # Fallback to sync method
                chat_result = self.underlying_llm._generate(
                    processed_messages, 
                    stop=stop, 
                    run_manager=None,  # Can't pass async manager to sync method
                    **kwargs
                )
            
            # Step 3: Post-process response for hallucination detection
            enhanced_result = await self._apostprocess_response(
                messages, processed_messages, chat_result, pii_results, correlation_id
            )
            
            # Step 4: Calculate processing time and extract token usage
            processing_time = (time.time() - start_time) * 1000
            self._extract_and_emit_token_usage(chat_result, correlation_id, processing_time)
            
            # Step 4.5: Emit LLM conversation event with prompt and response
            self._emit_llm_conversation_event(processed_messages, chat_result, correlation_id, processing_time)
            
            # Step 5: Update statistics and telemetry
            self._update_stats(processing_time, pii_results, None)
            
            return enhanced_result
            
        except Exception as e:
            # Handle errors according to fail_safe setting
            processing_time = (time.time() - start_time) * 1000
            self._log_error("_agenerate", e, processing_time)
            
            if getattr(self, 'fail_safe', True):
                # Return original LLM response without safety processing
                if hasattr(self.underlying_llm, '_agenerate'):
                    return await self.underlying_llm._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                else:
                    return self.underlying_llm._generate(messages, stop=stop, run_manager=None, **kwargs)
            else:
                raise
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGeneration]:
        """Stream chat response with safety processing."""
        start_time = time.time()
        
        # Use conversation-level correlation_id from telemetry handler, fallback to run_id
        import uuid
        correlation_id = (
            self.telemetry_handler.get_conversation_correlation_id() 
            if self.telemetry_handler and self.telemetry_handler.get_conversation_correlation_id()
            else (str(run_manager.run_id) if run_manager and hasattr(run_manager, 'run_id') else str(uuid.uuid4()))
        )
        
        try:
            # Pre-process messages for PII redaction
            processed_messages, pii_results = self._preprocess_messages(messages, correlation_id)
            
            # Check if underlying LLM supports streaming
            if hasattr(self.underlying_llm, '_stream'):
                # Collect streamed response for post-processing
                collected_content = ""
                generations = []
                
                for generation in self.underlying_llm._stream(
                    processed_messages, 
                    stop=stop, 
                    run_manager=run_manager,
                    **kwargs
                ):
                    collected_content += generation.message.content
                    generations.append(generation)
                    yield generation
                
                # Post-process complete response for hallucination detection
                if collected_content and self.hallucination_engine:
                    try:
                        # Create a simple prompt from messages for hallucination detection
                        prompt = self._messages_to_prompt(messages)
                        
                        # Run hallucination detection in proper async context
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                # If loop is running, create a task
                                asyncio.create_task(
                                    self._detect_and_log_hallucination(prompt, collected_content)
                                )
                            else:
                                # If no loop is running, run it directly
                                asyncio.run(self._detect_and_log_hallucination(prompt, collected_content))
                        except RuntimeError:
                            # No event loop available, run in new one
                            asyncio.run(self._detect_and_log_hallucination(prompt, collected_content))
                    except Exception as e:
                        logger.debug(f"Hallucination detection failed in streaming: {e}")
                
                # Update statistics
                processing_time = (time.time() - start_time) * 1000
                self._update_stats(processing_time, pii_results, None)
                
            else:
                # Fallback to non-streaming generation
                chat_result = self._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                for generation in chat_result.generations:
                    yield generation
                    
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._log_error("_stream", e, processing_time)
            
            if getattr(self, 'fail_safe', True):
                # Fallback to original LLM streaming
                if hasattr(self.underlying_llm, '_stream'):
                    for generation in self.underlying_llm._stream(messages, stop=stop, run_manager=run_manager, **kwargs):
                        yield generation
                else:
                    chat_result = self.underlying_llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                    for generation in chat_result.generations:
                        yield generation
            else:
                raise
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGeneration]:
        """Async stream chat response with safety processing."""
        start_time = time.time()
        
        # Use conversation-level correlation_id from telemetry handler, fallback to run_id
        import uuid
        correlation_id = (
            self.telemetry_handler.get_conversation_correlation_id() 
            if self.telemetry_handler and self.telemetry_handler.get_conversation_correlation_id()
            else (str(run_manager.run_id) if run_manager and hasattr(run_manager, 'run_id') else str(uuid.uuid4()))
        )
        
        try:
            # Pre-process messages for PII redaction
            processed_messages, pii_results = self._preprocess_messages(messages, correlation_id)
            
            # Check if underlying LLM supports async streaming
            if hasattr(self.underlying_llm, '_astream'):
                # Collect streamed response for post-processing
                collected_content = ""
                
                async for generation in self.underlying_llm._astream(
                    processed_messages, 
                    stop=stop, 
                    run_manager=run_manager,
                    **kwargs
                ):
                    collected_content += generation.message.content
                    yield generation
                
                # Post-process complete response for hallucination detection
                if collected_content and self.hallucination_engine:
                    try:
                        prompt = self._messages_to_prompt(messages)
                        await self._detect_and_log_hallucination(prompt, collected_content)
                    except Exception as e:
                        logger.debug(f"Async hallucination detection failed in streaming: {e}")
                
                # Update statistics
                processing_time = (time.time() - start_time) * 1000
                self._update_stats(processing_time, pii_results, None)
                
            else:
                # Fallback to non-streaming async generation
                chat_result = await self._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                for generation in chat_result.generations:
                    yield generation
                    
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            self._log_error("_astream", e, processing_time)
            
            if getattr(self, 'fail_safe', True):
                # Fallback to original LLM streaming
                if hasattr(self.underlying_llm, '_astream'):
                    async for generation in self.underlying_llm._astream(messages, stop=stop, run_manager=run_manager, **kwargs):
                        yield generation
                else:
                    chat_result = await self._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                    for generation in chat_result.generations:
                        yield generation
            else:
                raise
    
    def _preprocess_messages(
        self, 
        messages: List[BaseMessage],
        correlation_id: str = None
    ) -> tuple[List[BaseMessage], List[PIIRedactionResult]]:
        """Pre-process messages for PII redaction."""
        if not self.pii_engine or not self.config_manager.config.pii.enabled:
            return messages, []
        
        processed_messages = []
        pii_results = []
        
        for message in messages:
            try:
                # Redact PII from message content
                redaction_result = self.pii_engine.redact_text(message.content)
                pii_results.append(redaction_result)
                
                # Create new message with redacted content
                if isinstance(message, HumanMessage):
                    processed_message = HumanMessage(
                        content=redaction_result.redacted_text,
                        additional_kwargs=message.additional_kwargs
                    )
                elif isinstance(message, AIMessage):
                    processed_message = AIMessage(
                        content=redaction_result.redacted_text,
                        additional_kwargs=message.additional_kwargs
                    )
                elif isinstance(message, SystemMessage):
                    processed_message = SystemMessage(
                        content=redaction_result.redacted_text,
                        additional_kwargs=message.additional_kwargs
                    )
                else:
                    # Fallback for other message types
                    processed_message = message.__class__(
                        content=redaction_result.redacted_text,
                        **{k: v for k, v in message.__dict__.items() if k != 'content'}
                    )
                
                processed_messages.append(processed_message)
                
                # Log PII detection telemetry (NEVER pass original content for security)
                if self.telemetry_handler and redaction_result.total_redactions > 0:
                    self._log_pii_event(redaction_result, redaction_result.redacted_text, correlation_id)
                    
            except Exception as e:
                logger.debug(f"PII redaction failed for message: {e}")
                if getattr(self, 'fail_safe', True):
                    processed_messages.append(message)
                    pii_results.append(None)
                else:
                    raise
        
        return processed_messages, pii_results
    
    def _postprocess_response(
        self,
        original_messages: List[BaseMessage],
        processed_messages: List[BaseMessage],
        chat_result: ChatResult,
        pii_results: List[PIIRedactionResult],
        correlation_id: str = None
    ) -> ChatResult:
        """Post-process response for hallucination detection."""
        # Check hallucination engine and config
        
        if not self.hallucination_engine or not self.config_manager.config.hallucination.enabled:
            # Skipping hallucination detection
            return chat_result
        
        try:
            # Extract response content
            if chat_result.generations and len(chat_result.generations) > 0:
                response_content = chat_result.generations[0].message.content
                # Checking response for hallucination
                prompt = self._messages_to_prompt(original_messages)
                
                # Detect response type first
                response_type = self._detect_response_type(prompt, response_content)
                
                # Run hallucination detection (sync version)
                # Note: This is a simplified sync version for compatibility
                # In production, you might want to use async detection
                
                # Run basic hallucination detection if engine available
                if self.hallucination_engine:
                    try:
                        # Use async detection in sync context (simplified)
                        import asyncio
                        try:
                            loop = asyncio.get_event_loop()
                            detection_result = loop.run_until_complete(
                                self.hallucination_engine.detect_hallucination(prompt, response_content)
                            )
                        except RuntimeError:
                            # No event loop, create new one
                            detection_result = asyncio.run(
                                self.hallucination_engine.detect_hallucination(prompt, response_content)
                            )
                    except Exception:
                        detection_result = None
                else:
                    detection_result = None
                
                if detection_result:
                    # Adjust probability based on response type
                    adjusted_probability = self._adjust_hallucination_probability(
                        detection_result.hallucination_probability, response_type
                    )
                    
                    # Update the detection result with adjusted probability
                    detection_result.hallucination_probability = adjusted_probability
                    detection_result.metadata['response_type'] = response_type
                    detection_result.metadata['original_probability'] = detection_result.hallucination_probability
                    
                    # Log hallucination detection telemetry
                    if self.telemetry_handler:
                        self._log_hallucination_event(detection_result, prompt, response_content, correlation_id)
                    
                    # Check if response should be blocked (using adjusted probability)
                    if (adjusted_probability > 
                        self.config_manager.config.hallucination.block_threshold):
                        
                        if not getattr(self, 'fail_safe', True):
                            raise SafetyViolationError(
                                f"Response blocked due to high hallucination probability: "
                                f"{adjusted_probability:.3f}"
                            )
                        else:
                            # Log warning but continue
                            logger.debug(
                                f"High hallucination probability detected: "
                                f"{adjusted_probability:.3f}"
                            )
                            self.stats['safety_violations'] += 1
            
        except Exception as e:
            logger.debug(f"Hallucination detection failed: {e}")
            if not self.fail_safe:
                raise
        
        return chat_result
    
    async def _apostprocess_response(
        self,
        original_messages: List[BaseMessage],
        processed_messages: List[BaseMessage],
        chat_result: ChatResult,
        pii_results: List[PIIRedactionResult],
        correlation_id: str = None
    ) -> ChatResult:
        """Async post-process response for hallucination detection."""
        if not self.hallucination_engine or not self.config_manager.config.hallucination.enabled:
            return chat_result
        
        try:
            # Extract response content
            if chat_result.generations and len(chat_result.generations) > 0:
                response_content = chat_result.generations[0].message.content
                prompt = self._messages_to_prompt(original_messages)
                
                # Detect response type first
                response_type = self._detect_response_type(prompt, response_content)
                
                # Run async hallucination detection
                detection_result = await self.hallucination_engine.detect_hallucination(
                    prompt=prompt,
                    response=response_content,
                    method=HallucinationMethod(self.config_manager.config.hallucination.detection_method)
                )
                
                if detection_result:
                    # Adjust probability based on response type
                    adjusted_probability = self._adjust_hallucination_probability(
                        detection_result.hallucination_probability, response_type
                    )
                    
                    # Update the detection result with adjusted probability
                    detection_result.hallucination_probability = adjusted_probability
                    detection_result.metadata['response_type'] = response_type
                    detection_result.metadata['original_probability'] = detection_result.hallucination_probability
                    
                    # Log hallucination detection telemetry
                    if self.telemetry_handler:
                        self._log_hallucination_event(detection_result, prompt, response_content, correlation_id)
                    
                    # Check if response should be blocked (using adjusted probability)
                    if (adjusted_probability > 
                        self.config_manager.config.hallucination.block_threshold):
                        
                        if not getattr(self, 'fail_safe', True):
                            raise SafetyViolationError(
                                f"Response blocked due to high hallucination probability: "
                                f"{adjusted_probability:.3f}"
                            )
                        else:
                            # Log warning but continue
                            logger.debug(
                                f"High hallucination probability detected: "
                                f"{adjusted_probability:.3f}"
                            )
                            self.stats['safety_violations'] += 1
            
        except Exception as e:
            logger.debug(f"Async hallucination detection failed: {e}")
            if not self.fail_safe:
                raise
        
        return chat_result
    
    async def _detect_and_log_hallucination(self, prompt: str, response: str):
        """Detect hallucination in background and log results."""
        try:
            logger.debug(f"🧠 Starting hallucination detection...")
            logger.debug(f"   Prompt: {prompt[:100]}...")
            logger.debug(f"   Response: {response[:100]}...")
            
            detection_result = await self.hallucination_engine.detect_hallucination(
                prompt=prompt,
                response=response
            )
            
            logger.debug(f"🎯 Hallucination detection complete:")
            logger.debug(f"   Probability: {detection_result.hallucination_probability:.3f}")
            
            # Handle confidence_level safely (could be enum or string)
            confidence_str = (
                detection_result.confidence_level.value 
                if hasattr(detection_result.confidence_level, 'value') 
                else str(detection_result.confidence_level)
            )
            logger.debug(f"   Confidence: {confidence_str}")
            logger.debug(f"   Method: {detection_result.detection_method}")
            logger.debug(f"   Processing time: {detection_result.processing_time_ms:.1f}ms")
            
            if detection_result.hallucination_probability > 0.6:
                logger.debug(f"⚠️  HIGH hallucination risk detected! (probability: {detection_result.hallucination_probability:.3f})")
            elif detection_result.hallucination_probability > 0.2:
                logger.debug(f"⚠️  MEDIUM hallucination risk detected (probability: {detection_result.hallucination_probability:.3f})")
            else:
                logger.debug(f"✅ LOW hallucination risk (probability: {detection_result.hallucination_probability:.3f})")
            
            if self.telemetry_handler:
                self._log_hallucination_event(detection_result, prompt, response)
                
        except Exception as e:
            logger.debug(f"Background hallucination detection failed: {e}")
            # Hallucination detection error
            logger.debug(f"Hallucination detection traceback: {traceback.format_exc()}")
    
    def _quick_hallucination_check(self, prompt: str, response: str) -> Optional[HallucinationDetection]:
        """Content-based hallucination check using LLM analysis."""
        start_time = time.time()
        
        try:
            # Use the underlying LLM to analyze the response for hallucinations
            analysis_prompt = f"""Analyze the following response for potential hallucinations, inaccuracies, or fabricated information.

Original Prompt: {prompt}
Response to Analyze: {response}

Evaluate the response on these criteria:
1. Factual accuracy (are any claims verifiably false?)
2. Logical consistency (does the response contradict itself?)
3. Appropriateness to the prompt (does it answer what was asked?)
4. Fabrication indicators (specific dates, numbers, or facts that seem made up?)

Respond with a JSON object containing:
- "hallucination_probability": a number from 0.0 to 1.0
- "confidence": "high", "medium", or "low" 
- "reasoning": brief explanation of your assessment
- "risk_factors": list of any concerning elements found

Example: {{"hallucination_probability": 0.1, "confidence": "high", "reasoning": "Response is factual and appropriate", "risk_factors": []}}"""

            try:
                # Use the underlying LLM for analysis
                from langchain_core.messages import SystemMessage, HumanMessage
                
                analysis_result = self.underlying_llm.invoke([
                    SystemMessage(content="You are an expert at detecting hallucinations and inaccuracies in AI responses. Always respond with valid JSON."),
                    HumanMessage(content=analysis_prompt)
                ])
                
                # Parse the JSON response
                import json
                import re
                
                # Extract JSON from response
                analysis_text = analysis_result.content if hasattr(analysis_result, 'content') else str(analysis_result)
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                
                if json_match:
                    analysis_data = json.loads(json_match.group())
                    probability = float(analysis_data.get('hallucination_probability', 0.1))
                    confidence = analysis_data.get('confidence', 'medium')
                    reasoning = analysis_data.get('reasoning', 'LLM-based analysis')
                    risk_factors = analysis_data.get('risk_factors', [])
                else:
                    # Fallback if JSON parsing fails
                    probability = 0.1  # Default to low risk
                    confidence = 'low'
                    reasoning = 'JSON parsing failed, defaulting to low risk'
                    risk_factors = ['parsing_error']
                
            except Exception as e:
                # Fallback for LLM analysis failure
                logger.debug(f"LLM analysis failed: {e}")
                
                # Improved content analysis fallback
                risk_score = 0.05  # Base low risk
                
                # Analyze response characteristics
                response_lower = response.lower()
                
                # Low risk indicators
                if any(word in response_lower for word in ['error', 'cannot', 'unable', 'sorry', 'i don\'t know']):
                    risk_score = 0.02  # Very low risk for honest limitations
                elif any(word in response_lower for word in ['yes', 'no', 'help', 'assist', 'can', 'will']):
                    risk_score = 0.05  # Low risk for simple confirmations
                
                # Medium risk indicators
                elif any(word in response_lower for word in ['definitely', 'absolutely', 'certainly', 'guarantee']):
                    risk_score = 0.25  # Higher risk for overconfident language
                elif len(response) > 500:  # Very long responses
                    risk_score = 0.15  # Slightly higher risk for verbosity
                
                # Check for specific dates, numbers, or facts that could be fabricated
                import re
                if re.search(r'\d{4}|\d+\.\d+|\$\d+', response):  # Years, decimals, prices
                    risk_score += 0.1  # Add risk for specific claims
                
                probability = min(risk_score, 0.4)  # Cap at 0.4 for fallback
                
                confidence = 'low'
                reasoning = f'Fallback analysis due to LLM error: {str(e)}'
                risk_factors = ['llm_analysis_failed']
            
            # Map confidence to enum
            from .hallucination import HallucinationDetection, ConfidenceLevel
            
            confidence_mapping = {
                'high': ConfidenceLevel.HIGH_CONFIDENCE,
                'medium': ConfidenceLevel.MEDIUM_CONFIDENCE,
                'low': ConfidenceLevel.LOW_CONFIDENCE
            }
            confidence_level = confidence_mapping.get(confidence, ConfidenceLevel.LOW_CONFIDENCE)
            
            processing_time = (time.time() - start_time) * 1000
            
            return HallucinationDetection(
                original_response=response,
                hallucination_probability=probability,
                confidence_level=confidence_level,
                detection_method="llm_content_analysis",
                supporting_evidence={
                    'reasoning': reasoning,
                    'risk_factors': risk_factors,
                    'analysis_method': 'llm_powered'
                },
                recommendations=self._generate_recommendations(probability, risk_factors),
                processing_time_ms=processing_time,
                metadata={'content_analysis': True}
            )
            
        except Exception as e:
            logger.debug(f"Content-based hallucination check failed: {e}")
            return None
    
    def _generate_recommendations(self, probability: float, risk_factors: list) -> list:
        """Generate recommendations based on hallucination analysis."""
        recommendations = []
        
        if probability > 0.7:
            recommendations.append("HIGH RISK: Manual review strongly recommended")
            recommendations.append("Consider regenerating response with different parameters")
        elif probability > 0.3:
            recommendations.append("MEDIUM RISK: Review for accuracy")
            recommendations.append("Verify any specific claims or facts")
        else:
            recommendations.append("LOW RISK: Response appears appropriate")
        
        if 'overconfident_language' in risk_factors:
            recommendations.append("Monitor for overconfident assertions")
        if 'specific_claims' in risk_factors:
            recommendations.append("Fact-check specific claims and numbers")
        if 'llm_analysis_failed' in risk_factors:
            recommendations.append("LLM analysis unavailable - consider manual review")
            
        return recommendations
    
    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """Convert messages to a simple prompt string for hallucination detection."""
        prompt_parts = []
        for message in messages:
            if isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"AI: {message.content}")
            elif isinstance(message, SystemMessage):
                prompt_parts.append(f"System: {message.content}")
            else:
                prompt_parts.append(f"Message: {message.content}")
        
        return "\n".join(prompt_parts)
    
    def _detect_response_type(self, prompt: str, response: str) -> str:
        """Detect the type of response to adjust hallucination thresholds."""
        prompt_lower = prompt.lower()
        response_lower = response.lower()
        
        # Mathematical responses
        if any(indicator in prompt_lower for indicator in [
            'calculate', 'compute', 'what is', 'solve', 'math', 
            'equation', 'formula', '+', '-', '*', '/', '='
        ]) and any(char.isdigit() for char in response):
            return 'mathematical'
        
        # Definitions and factual queries
        if any(indicator in prompt_lower for indicator in [
            'define', 'what is', 'what are', 'explain what', 'meaning of',
            'definition', 'describe'
        ]) and len(response.split()) < 100:
            return 'definition'
        
        # Simple confirmations or denials
        if len(response.split()) < 10 and any(word in response_lower for word in [
            'yes', 'no', 'correct', 'incorrect', 'true', 'false',
            'i can', 'i cannot', 'i will', 'i won\'t', 'sure', 'okay'
        ]):
            return 'confirmation'
        
        # Lists and enumerations
        if any(indicator in prompt_lower for indicator in [
            'list', 'name', 'enumerate', 'what are the', 'give me',
            'provide examples', 'mention'
        ]) and ('\n' in response or 
                any(response.count(item) > 2 for item in ['•', '-', '1.', '2.', '3.'])):
            return 'enumeration'
        
        # Code or technical responses
        if ('```' in response or 
            any(lang in response_lower for lang in ['python', 'javascript', 'java', 'code', 'function', 'class']) or
            response.count('{') > 2 or response.count('(') > 5):
            return 'technical'
        
        # Error or limitation responses
        if any(phrase in response_lower for phrase in [
            'i cannot', 'i don\'t', 'i am unable', 'sorry', 'apologize',
            'don\'t have access', 'can\'t provide', 'not able to'
        ]):
            return 'limitation'
        
        # Default to creative/conversational
        return 'creative'
    
    def _adjust_hallucination_probability(self, original_prob: float, response_type: str) -> float:
        """Adjust hallucination probability based on response type."""
        # Define multipliers for different response types
        # Lower multiplier = less likely to be flagged as hallucination
        type_multipliers = {
            'mathematical': 0.3,      # Math is usually precise
            'definition': 0.5,        # Definitions are factual
            'confirmation': 0.2,      # Simple yes/no very unlikely to hallucinate
            'enumeration': 0.6,       # Lists can be partially correct
            'technical': 0.7,         # Code can have bugs but not hallucinations
            'limitation': 0.1,        # Admitting limitations is not hallucination
            'creative': 1.0           # Full sensitivity for creative responses
        }
        
        multiplier = type_multipliers.get(response_type, 1.0)
        adjusted_prob = original_prob * multiplier
        
        # Log the adjustment for debugging
        if original_prob != adjusted_prob:
            logger.debug(
                f"Hallucination probability adjusted: {original_prob:.3f} -> {adjusted_prob:.3f} "
                f"(type: {response_type}, multiplier: {multiplier})"
            )
        
        return min(adjusted_prob, 1.0)  # Cap at 1.0
    
    def _log_pii_event(self, pii_result: PIIRedactionResult, redacted_content: str = None, correlation_id: str = None):
        """Log PII redaction event to telemetry."""
        if not self.telemetry_handler:
            return
        
        try:
            event_data = {
                "total_redactions": pii_result.total_redactions,
                "redaction_summary": pii_result.redaction_summary,
                "processing_time_ms": pii_result.processing_time_ms,
                "original_length": len(pii_result.original_text),
                "redacted_length": len(pii_result.redacted_text),
                "redaction_types": list(pii_result.redaction_summary.keys()),
                "compliance_data": {
                    "audit_log": True,
                    "policy": self.config_manager.config.policy
                }
            }
            
            # Add correlation ID if provided
            if correlation_id:
                event_data["correlation_id"] = correlation_id
            
            # Add redacted content preview only (NEVER original content for security)
            if redacted_content:
                event_data["redacted_content_preview"] = redacted_content[:100] + "..." if len(redacted_content) > 100 else redacted_content
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="pii_detection",
                agent_id=self.telemetry_handler.agent_id,
                data=event_data
            )
            
            self.telemetry_handler.telemetry_sdk.process_event(event)
            self.stats['pii_redactions'] += pii_result.total_redactions
            
        except Exception as e:
            logger.debug(f"Failed to log PII event: {e}")
    
    def _log_hallucination_event(self, detection_result: HallucinationDetection, prompt: str = None, response: str = None, correlation_id: str = None):
        """Log hallucination detection event to telemetry."""
        if not self.telemetry_handler:
            return
        
        try:
            event_data = {
                "hallucination_probability": detection_result.hallucination_probability,
                "confidence_level": (
                    detection_result.confidence_level.value 
                    if hasattr(detection_result.confidence_level, 'value') 
                    else str(detection_result.confidence_level)
                ),
                "detection_method": detection_result.detection_method,
                "processing_time_ms": detection_result.processing_time_ms,
                "recommendations": detection_result.recommendations,
                "supporting_evidence": detection_result.supporting_evidence,
                "safety_thresholds": {
                    "block_threshold": self.config_manager.config.hallucination.block_threshold,
                    "warn_threshold": self.config_manager.config.hallucination.warn_threshold
                },
                "policy": self.config_manager.config.policy
            }
            
            # Add correlation ID if provided
            if correlation_id:
                event_data["correlation_id"] = correlation_id
            
            # Add content snippets for correlation (truncated for analysis)
            if prompt:
                event_data["prompt_preview"] = prompt[:200] + "..." if len(prompt) > 200 else prompt
            if response:
                event_data["response_preview"] = response[:200] + "..." if len(response) > 200 else response
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="hallucination_detection",
                agent_id=self.telemetry_handler.agent_id,
                data=event_data
            )
            
            self.telemetry_handler.telemetry_sdk.process_event(event)
            self.stats['hallucination_detections'] += 1
            
        except Exception as e:
            logger.debug(f"Failed to log hallucination event: {e}")
    
    def _update_stats(
        self, 
        processing_time: float, 
        pii_results: List[PIIRedactionResult], 
        hallucination_result: Optional[HallucinationDetection]
    ):
        """Update internal statistics."""
        self.stats['total_requests'] += 1
        self.stats['processing_time_ms'] += processing_time
        
        if pii_results:
            total_pii_redactions = sum(
                result.total_redactions for result in pii_results if result
            )
            self.stats['pii_redactions'] += total_pii_redactions
        
        if hallucination_result:
            self.stats['hallucination_detections'] += 1
    
    def _log_error(self, method: str, error: Exception, processing_time: float):
        """Log error with telemetry."""
        logger.error(f"Error in {method}: {error}")
        
        if self.telemetry_handler:
            try:
                event = TelemetryEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type="safety_error",
                    agent_id=self.telemetry_handler.agent_id,
                    data={
                        "error_method": method,
                        "error_message": str(error),
                        "error_type": type(error).__name__,
                        "processing_time_ms": processing_time,
                        "fail_safe_enabled": getattr(self, 'fail_safe', True),
                        "config_policy": self.config_manager.config.policy
                    }
                )
                
                self.telemetry_handler.telemetry_sdk.process_event(event)
            except Exception as e:
                logger.debug(f"Failed to log error event: {e}")
    
    def _extract_and_emit_token_usage(self, chat_result: ChatResult, correlation_id: str, processing_time: float):
        """Extract token usage from LLM response and emit token event."""
        if not self.telemetry_handler:
            return
        
        try:
            token_usage = {}
            
            # Method 1: Check for token usage in llm_output
            if hasattr(chat_result, 'llm_output') and chat_result.llm_output:
                if 'token_usage' in chat_result.llm_output:
                    usage = chat_result.llm_output['token_usage']
                    token_usage = {
                        "total_tokens": usage.get("total_tokens", 0),
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "model": usage.get("model", self.model_name),
                        "capture_method": "llm_output"
                    }
            
            # Method 2: Check for usage_metadata in response_metadata
            if not token_usage and hasattr(chat_result, 'response_metadata'):
                if 'token_usage' in chat_result.response_metadata:
                    usage = chat_result.response_metadata['token_usage']
                    token_usage = {
                        "total_tokens": usage.get("total_tokens", 0),
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "model": self.model_name,
                        "capture_method": "response_metadata"
                    }
            
            # Method 3: Check generations for usage_metadata
            if not token_usage and hasattr(chat_result, 'generations') and chat_result.generations:
                for generation in chat_result.generations:
                    if hasattr(generation, 'generation_info') and generation.generation_info:
                        if 'token_usage' in generation.generation_info:
                            usage = generation.generation_info['token_usage']
                            token_usage = {
                                "total_tokens": usage.get("total_tokens", 0),
                                "prompt_tokens": usage.get("prompt_tokens", 0),
                                "completion_tokens": usage.get("completion_tokens", 0),
                                "model": self.model_name,
                                "capture_method": "generation_info"
                            }
                            break
            
            # If we found token usage, emit the event
            if token_usage.get("total_tokens", 0) > 0:
                # Calculate cost estimate
                cost_estimate = self._calculate_cost_estimate(token_usage.get("model", self.model_name), token_usage)
                
                event_data = {
                    "correlation_id": correlation_id,
                    "model": token_usage.get("model", self.model_name),
                    "total_tokens": token_usage["total_tokens"],
                    "prompt_tokens": token_usage["prompt_tokens"],
                    "completion_tokens": token_usage["completion_tokens"],
                    "processing_time_ms": processing_time,
                    "capture_method": token_usage.get("capture_method", "unknown"),
                    "cost_estimate": cost_estimate,
                    "tokens_per_second": token_usage["total_tokens"] / (processing_time / 1000) if processing_time > 0 else 0
                }
                
                event = TelemetryEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type="token_usage",
                    agent_id=self.telemetry_handler.agent_id,
                    data=event_data
                )
                
                self.telemetry_handler.telemetry_sdk.process_event(event)
                logger.debug(f"💰 Token usage captured: {token_usage['total_tokens']} tokens (method: {token_usage.get('capture_method', 'unknown')})")
            else:
                logger.debug(f"🔍 No token usage found in ChatResult - likely handled by AutoTelemetryHandler for streaming")
                
        except Exception as e:
            logger.debug(f"Failed to extract and emit token usage: {e}")
    
    def _calculate_cost_estimate(self, model_name: str, token_usage: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost estimate based on model and token usage."""
        # Simplified pricing model (per 1K tokens)
        pricing = {
            "gpt-4o": {"prompt": 0.005, "completion": 0.015},
            "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
            "gpt-4": {"prompt": 0.03, "completion": 0.06},
            "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002}
        }
        
        # Normalize model name for pricing lookup
        model_key = None
        for key in pricing.keys():
            if key in model_name.lower():
                model_key = key
                break
        
        if not model_key or not token_usage:
            return {"prompt_cost": 0.0, "completion_cost": 0.0, "total_cost": 0.0}
        
        prompt_cost = token_usage.get('prompt_tokens', 0) * pricing[model_key]["prompt"] / 1000
        completion_cost = token_usage.get('completion_tokens', 0) * pricing[model_key]["completion"] / 1000
        
        return {
            "prompt_cost": round(prompt_cost, 6),
            "completion_cost": round(completion_cost, 6),
            "total_cost": round(prompt_cost + completion_cost, 6)
        }
    
    def _emit_llm_conversation_event(self, messages: List[BaseMessage], chat_result: ChatResult, correlation_id: str, processing_time: float):
        """Emit an event containing the full LLM conversation (prompt and response)."""
        if not self.telemetry_handler:
            return
        
        try:
            # Extract prompt from messages
            prompt = self._messages_to_prompt(messages)
            
            # Extract response from chat result
            response = ""
            if chat_result.generations:
                response = chat_result.generations[0].message.content if hasattr(chat_result.generations[0], 'message') else str(chat_result.generations[0].text)
            
            # Create conversation event
            event_data = {
                "correlation_id": correlation_id,
                "prompt": prompt,
                "response": response,
                "model": self.model_name,
                "message_count": len(messages),
                "processing_time_ms": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="llm_conversation",
                agent_id=self.telemetry_handler.agent_id,
                data=event_data
            )
            
            self.telemetry_handler.telemetry_sdk.process_event(event)
            logger.debug(f"💬 LLM conversation captured: {len(prompt)} chars prompt, {len(response)} chars response")
            
        except Exception as e:
            logger.debug(f"Failed to emit LLM conversation event: {e}")
    
    # Configuration management methods
    def update_config(self, config: Union[SafetyConfiguration, Dict[str, Any]]):
        """Update safety configuration at runtime."""
        if isinstance(config, dict):
            # Update specific config values
            for key, value in config.items():
                if hasattr(self.config_manager.config, key):
                    setattr(self.config_manager.config, key, value)
        elif isinstance(config, SafetyConfiguration):
            self.config_manager.config = config
        else:
            raise ValueError("Config must be SafetyConfiguration object or dict")
        
        # Reinitialize engines with new config
        self._reinitialize_engines()
    
    def apply_policy(self, policy: SafetyPolicy):
        """Apply a predefined safety policy."""
        self.config_manager.apply_policy(policy)
        self._reinitialize_engines()
    
    def _reinitialize_engines(self):
        """Reinitialize safety engines with updated configuration."""
        try:
            # Reinitialize PII engine
            if self.config_manager.config.pii.enabled and OBSERVARE_MODULES_AVAILABLE:
                pii_config = {
                    'enabled': self.config_manager.config.pii.enabled,
                    'strategies': self.config_manager.config.pii.strategies,
                    'min_confidence': self.config_manager.config.pii.min_confidence_threshold,
                    'preserve_structure': self.config_manager.config.pii.preserve_structure,
                    'hash_salt': self.config_manager.config.pii.hash_salt
                }
                self.pii_engine = PIIRedactionEngine(pii_config)
            else:
                self.pii_engine = None
            
            # Reinitialize hallucination engine
            if self.config_manager.config.hallucination.enabled and OBSERVARE_MODULES_AVAILABLE:
                hallucination_config = {
                    'enabled': self.config_manager.config.hallucination.enabled,
                    'method': self.config_manager.config.hallucination.detection_method,
                    'thresholds': self.config_manager.config.hallucination.confidence_thresholds,
                    'consistency_samples': self.config_manager.config.hallucination.consistency_samples,
                    'consistency_temperature': self.config_manager.config.hallucination.consistency_temperature,
                    'enable_cove': self.config_manager.config.hallucination.enable_chain_of_verification,
                    'enable_uqlm': self.config_manager.config.hallucination.enable_uqlm,
                    'timeout_seconds': self.config_manager.config.hallucination.timeout_seconds
                }
                self.hallucination_engine = HallucinationDetectionEngine(self.underlying_llm, hallucination_config)
            else:
                self.hallucination_engine = None
                
        except Exception as e:
            logger.debug(f"Failed to reinitialize engines: {e}")
            if not self.fail_safe:
                raise
    
    # Statistics and monitoring methods
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        stats = self.stats.copy()
        
        # Add configuration info
        stats['config'] = {
            'policy': self.config_manager.config.policy,
            'pii_enabled': self.config_manager.config.pii.enabled,
            'hallucination_enabled': self.config_manager.config.hallucination.enabled,
            'telemetry_enabled': self.config_manager.config.telemetry.enabled
        }
        
        # Add engine stats if available
        if self.pii_engine:
            stats['pii_engine_stats'] = self.pii_engine.get_stats()
        
        if self.hallucination_engine:
            stats['hallucination_engine_stats'] = self.hallucination_engine.get_stats()
        
        # Calculate derived metrics
        if stats['total_requests'] > 0:
            stats['avg_processing_time_ms'] = stats['processing_time_ms'] / stats['total_requests']
            stats['pii_redaction_rate'] = stats['pii_redactions'] / stats['total_requests']
            stats['hallucination_detection_rate'] = stats['hallucination_detections'] / stats['total_requests']
            stats['safety_violation_rate'] = stats['safety_violations'] / stats['total_requests']
        
        return stats
    
    def export_config(self, file_path: str):
        """Export current configuration to file."""
        self.config_manager.save_to_file(file_path)
    
    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            'total_requests': 0,
            'pii_redactions': 0,
            'hallucination_detections': 0,
            'safety_violations': 0,
            'processing_time_ms': 0.0
        }


# Backward compatibility alias
ObservareLLM = ObservareChat


# Convenience functions for easy integration
def wrap_chat_model(
    llm: BaseChatModel,
    policy: Union[SafetyPolicy, str] = SafetyPolicy.BALANCED,
    api_key: Optional[str] = None,
    **kwargs
) -> ObservareChat:
    """
    Convenience function to wrap any LangChain chat model with safety features.
    
    Args:
        llm: LangChain chat model to wrap
        policy: Safety policy to apply
        api_key: Observare API key
        **kwargs: Additional arguments for ObservareChat
        
    Returns:
        ObservareChat wrapper with safety features
    """
    if isinstance(policy, str):
        policy = SafetyPolicy(policy)
    
    config = SafetyConfiguration()
    config.apply_policy(policy)
    
    return ObservareChat(
        llm=llm,
        config=config,
        api_key=api_key,
        **kwargs
    )


# Production module - test code removed