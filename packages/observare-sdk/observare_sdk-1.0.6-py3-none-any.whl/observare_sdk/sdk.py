import json
import os
import time
import sys
import platform
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from uuid import UUID

# Suppress noisy logs from this module
logging.getLogger(__name__).setLevel(logging.WARNING)

# For API integration
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult
from langchain.schema.messages import BaseMessage

# Import LangChain's usage metadata tracking
try:
    from langchain_core.callbacks import UsageMetadataCallbackHandler
    USAGE_METADATA_AVAILABLE = True
except ImportError:
    try:
        from langchain.callbacks import UsageMetadataCallbackHandler
        USAGE_METADATA_AVAILABLE = True
    except ImportError:
        USAGE_METADATA_AVAILABLE = False
        # Fallback base class
        class UsageMetadataCallbackHandler:
            def __init__(self):
                self.usage_metadata = {}


@dataclass
class TelemetryEvent:
    timestamp: str
    event_type: str
    agent_id: str
    data: Dict[str, Any]
    duration_ms: float = 0


class TelemetrySDK:
    def __init__(self, api_key: str, debug_mode: bool = False):
        self.api_key = api_key
        self.api_endpoint = "https://observare-backend.fly.dev"  # Hardcoded - users cannot override
        self.debug_mode = debug_mode
        
        # Initialize metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "tool_usage": {}
        }
        self.events_log = []
        
        # API integration setup
        self.api_enabled = True
        self.session_id = f"session_{int(time.time())}"
        
        # All events now processed synchronously for reliability
    
    def _send_event_to_api(self, event: TelemetryEvent):
        """Send event to API with timing."""
        start_time = time.time()
        
        payload = {
            "agent_id": event.agent_id,
            "session_id": self.session_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "data": event.data,
            "duration_ms": event.duration_ms
        }

        headers = {
            "X-API-Key": f"{self.api_key}",
            "Content-Type": "application/json"
        }

        url = "https://observare-backend.fly.dev/v1/events"
        
        # Make actual API call if requests is available
        if REQUESTS_AVAILABLE:
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=5)
                api_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    if self.debug_mode:
                        print(f"⚡ API call ({event.event_type}): {api_time:.1f}ms")
                elif response.status_code == 401:
                    if self.debug_mode:
                        print(f"❌ Observare API: Invalid API key (401)")
                elif response.status_code == 403:
                    if self.debug_mode:
                        print(f"❌ Observare API: Access forbidden (403)")
                else:
                    if self.debug_mode:
                        print(f"⚠️  Observare API: HTTP {response.status_code} ({event.event_type})")
            except requests.exceptions.RequestException as e:
                api_time = (time.time() - start_time) * 1000
                if self.debug_mode:
                    print(f"⚠️  Observare API: Connection error - {str(e)[:50]}...")
                if self.debug_mode:
                    print(f"⚡ API call failed ({event.event_type}): {api_time:.1f}ms")
                pass  # Silently handle connection errors

    def process_event(self, event: TelemetryEvent):
        """Process event synchronously for guaranteed delivery."""
        process_start = time.time()
        self.events_log.append(event)
        
        # Send to API immediately (blocking)
        if self.api_enabled:
            self._send_event_to_api(event)
            
        total_time = (time.time() - process_start) * 1000
        if self.debug_mode:
            print(f"✅ Event sent ({event.event_type}): {total_time:.1f}ms (blocking)")
    
    def update_metrics(self, event: TelemetryEvent):
        """Update metrics based on event type."""
        if event.event_type == "agent_start":
            self.metrics["total_requests"] += 1
        
        elif event.event_type == "agent_completion":
            if event.data.get("success"):
                self.metrics["successful_requests"] += 1
            self._update_response_time(event.duration_ms)
        
        elif event.event_type == "agent_error":
            self.metrics["failed_requests"] += 1
            self._update_response_time(event.duration_ms)
        
        elif event.event_type == "tool_execution":
            tool_name = event.data.get("tool_name")
            if tool_name:
                if tool_name not in self.metrics["tool_usage"]:
                    self.metrics["tool_usage"][tool_name] = {
                        "count": 0,
                        "avg_duration": 0,
                        "total_duration": 0
                    }
                
                tool_metrics = self.metrics["tool_usage"][tool_name]
                tool_metrics["count"] += 1
                tool_metrics["total_duration"] += event.duration_ms
                tool_metrics["avg_duration"] = tool_metrics["total_duration"] / tool_metrics["count"]
        
        # Handle new event types from AutoTelemetryHandler
        elif event.event_type == "llm_call":
            # Track LLM performance and token usage metrics
            token_usage = event.data.get("token_usage", {})
            if "llm_metrics" not in self.metrics:
                self.metrics["llm_metrics"] = {
                    "total_calls": 0,
                    "total_tokens": 0,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "avg_tokens_per_call": 0
                }
            
            llm_metrics = self.metrics["llm_metrics"]
            llm_metrics["total_calls"] += 1
            llm_metrics["total_tokens"] += token_usage.get("total_tokens", 0)
            llm_metrics["prompt_tokens"] += token_usage.get("prompt_tokens", 0)
            llm_metrics["completion_tokens"] += token_usage.get("completion_tokens", 0)
            
            if llm_metrics["total_calls"] > 0:
                llm_metrics["avg_tokens_per_call"] = llm_metrics["total_tokens"] / llm_metrics["total_calls"]
        
        elif event.event_type == "chat_model_completion":
            # Track comprehensive chat model metrics
            self._process_chat_model_metrics(event)
        
        elif event.event_type == "agent_action":
            # Track agent decision patterns and tool usage
            self._process_agent_action_metrics(event)
        
        elif event.event_type == "agent_finish":
            # Track execution flow and conversation metrics
            self._process_agent_finish_metrics(event)
        
        
        elif event.event_type == "agent_completion":
            # Check for token usage in agent completion events
            token_usage = event.data.get("token_usage", {})
            if token_usage.get("total_tokens"):
                self._process_token_usage_metrics(event, token_usage)
        
        elif event.event_type == "token_usage":
            # Process comprehensive token usage data
            token_usage = event.data.get("token_usage", {})
            if token_usage.get("total_tokens"):
                self._process_token_usage_metrics(event, token_usage)
        
        # New safety event types
        elif event.event_type == "pii_detection":
            # Track PII detection and redaction metrics
            self._process_pii_detection_metrics(event)
        
        elif event.event_type == "hallucination_detection":
            # Track hallucination detection metrics
            self._process_hallucination_detection_metrics(event)
        
        elif event.event_type == "safety_error":
            # Track safety system errors
            self._process_safety_error_metrics(event)
            
    def _process_chat_model_metrics(self, event: TelemetryEvent):
        """Process comprehensive chat model metrics."""
        if "chat_model_metrics" not in self.metrics:
            self.metrics["chat_model_metrics"] = {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "avg_response_time": 0,
                "models_used": {},
                "content_analysis": {
                    "avg_input_length": 0,
                    "avg_output_length": 0,
                    "total_conversations": 0
                }
            }
        
        chat_metrics = self.metrics["chat_model_metrics"]
        token_usage = event.data.get("token_usage", {})
        cost_estimate = event.data.get("cost_estimate", {})
        model_name = event.data.get("model", "unknown")
        
        # Update basic metrics
        chat_metrics["total_calls"] += 1
        chat_metrics["total_tokens"] += token_usage.get("total_tokens", 0)
        chat_metrics["total_cost"] += cost_estimate.get("estimated_cost", 0)
        
        # Track models used
        if model_name not in chat_metrics["models_used"]:
            chat_metrics["models_used"][model_name] = {"count": 0, "tokens": 0, "cost": 0}
        
        model_stats = chat_metrics["models_used"][model_name]
        model_stats["count"] += 1
        model_stats["tokens"] += token_usage.get("total_tokens", 0)
        model_stats["cost"] += cost_estimate.get("estimated_cost", 0)
        
        # Update averages
        if chat_metrics["total_calls"] > 0:
            total_time = chat_metrics["avg_response_time"] * (chat_metrics["total_calls"] - 1) + event.duration_ms
            chat_metrics["avg_response_time"] = total_time / chat_metrics["total_calls"]
    
    def _process_agent_action_metrics(self, event: TelemetryEvent):
        """Process agent action and decision patterns."""
        if "decision_metrics" not in self.metrics:
            self.metrics["decision_metrics"] = {
                "total_decisions": 0,
                "tool_selection_patterns": {},
                "decision_complexity": 0,
                "avg_sequence_length": 0
            }
        
        decision_metrics = self.metrics["decision_metrics"]
        tool_name = event.data.get("tool", "unknown")
        tool_history = event.data.get("tool_history", [])
        
        decision_metrics["total_decisions"] += 1
        
        # Track tool selection patterns
        if tool_name not in decision_metrics["tool_selection_patterns"]:
            decision_metrics["tool_selection_patterns"][tool_name] = {
                "count": 0,
                "avg_position": 0,
                "contexts": []
            }
        
        tool_stats = decision_metrics["tool_selection_patterns"][tool_name]
        tool_stats["count"] += 1
        
        # Update sequence analysis
        if len(tool_history) > 0:
            total_sequences = sum(stats["count"] for stats in decision_metrics["tool_selection_patterns"].values())
            total_length = sum(len(event.data.get("tool_history", [])) for event in self.events_log if event.event_type == "agent_action")
            if total_sequences > 0:
                decision_metrics["avg_sequence_length"] = total_length / total_sequences
    
    def _process_agent_finish_metrics(self, event: TelemetryEvent):
        """Process execution flow and conversation completion metrics."""
        if "execution_metrics" not in self.metrics:
            self.metrics["execution_metrics"] = {
                "total_completions": 0,
                "avg_tools_per_completion": 0,
                "avg_execution_complexity": 0,
                "conversation_analysis": {
                    "avg_turns": 0,
                    "content_quality_scores": []
                }
            }
        
        exec_metrics = self.metrics["execution_metrics"]
        execution_analysis = event.data.get("execution_analysis", {})
        
        exec_metrics["total_completions"] += 1
        
        # Update execution complexity
        tools_used = execution_analysis.get("total_tools_used", 0)
        complexity = execution_analysis.get("execution_path_complexity", 0)
        
        # Calculate running averages
        if exec_metrics["total_completions"] > 0:
            prev_total = exec_metrics["avg_tools_per_completion"] * (exec_metrics["total_completions"] - 1)
            exec_metrics["avg_tools_per_completion"] = (prev_total + tools_used) / exec_metrics["total_completions"]
            
            prev_complexity = exec_metrics["avg_execution_complexity"] * (exec_metrics["total_completions"] - 1)
            exec_metrics["avg_execution_complexity"] = (prev_complexity + complexity) / exec_metrics["total_completions"]
    
    
    def _process_token_usage_metrics(self, event: TelemetryEvent, token_usage: Dict[str, Any]):
        """Process token usage from any source."""
        if "token_metrics" not in self.metrics:
            self.metrics["token_metrics"] = {
                "total_tokens": 0,
                "total_calls": 0,
                "total_cost": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "avg_tokens_per_call": 0,
                "models_used": {}
            }
        
        token_metrics = self.metrics["token_metrics"]
        model_name = token_usage.get("model", "unknown")
        cost_data = token_usage.get("cost_estimate", {})
        
        # Update totals
        token_metrics["total_calls"] += 1
        token_metrics["total_tokens"] += token_usage.get("total_tokens", 0)
        token_metrics["prompt_tokens"] += token_usage.get("prompt_tokens", 0)
        token_metrics["completion_tokens"] += token_usage.get("completion_tokens", 0)
        token_metrics["total_cost"] += cost_data.get("estimated_cost", 0)
        
        # Track per-model usage
        if model_name not in token_metrics["models_used"]:
            token_metrics["models_used"][model_name] = {
                "calls": 0,
                "tokens": 0,
                "cost": 0
            }
        
        model_stats = token_metrics["models_used"][model_name]
        model_stats["calls"] += 1
        model_stats["tokens"] += token_usage.get("total_tokens", 0)
        model_stats["cost"] += cost_data.get("estimated_cost", 0)
        
        # Update averages
        if token_metrics["total_calls"] > 0:
            token_metrics["avg_tokens_per_call"] = token_metrics["total_tokens"] / token_metrics["total_calls"]
    
    def _process_pii_detection_metrics(self, event: TelemetryEvent):
        """Process PII detection and redaction metrics."""
        if "pii_metrics" not in self.metrics:
            self.metrics["pii_metrics"] = {
                "total_scans": 0,
                "total_redactions": 0,
                "redactions_by_type": {},
                "avg_processing_time_ms": 0,
                "total_processing_time_ms": 0,
                "compliance_scans": 0,
                "redaction_strategies": {},
                "high_risk_detections": 0
            }
        
        pii_metrics = self.metrics["pii_metrics"]
        event_data = event.data
        
        # Update basic metrics
        pii_metrics["total_scans"] += 1
        pii_metrics["total_redactions"] += event_data.get("total_redactions", 0)
        
        processing_time = event_data.get("processing_time_ms", 0)
        pii_metrics["total_processing_time_ms"] += processing_time
        if pii_metrics["total_scans"] > 0:
            pii_metrics["avg_processing_time_ms"] = pii_metrics["total_processing_time_ms"] / pii_metrics["total_scans"]
        
        # Track redactions by type
        redaction_summary = event_data.get("redaction_summary", {})
        for pii_type, count in redaction_summary.items():
            if pii_type not in pii_metrics["redactions_by_type"]:
                pii_metrics["redactions_by_type"][pii_type] = 0
            pii_metrics["redactions_by_type"][pii_type] += count
        
        # Track compliance metrics
        if event_data.get("compliance_data", {}).get("audit_log"):
            pii_metrics["compliance_scans"] += 1
        
        # Track high-risk detections (multiple PII types in single scan)
        if len(redaction_summary) > 2:
            pii_metrics["high_risk_detections"] += 1
    
    def _process_hallucination_detection_metrics(self, event: TelemetryEvent):
        """Process hallucination detection metrics."""
        if "hallucination_metrics" not in self.metrics:
            self.metrics["hallucination_metrics"] = {
                "total_detections": 0,
                "confidence_levels": {
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "very_low": 0
                },
                "detection_methods": {},
                "avg_hallucination_probability": 0,
                "total_hallucination_probability": 0,
                "avg_processing_time_ms": 0,
                "total_processing_time_ms": 0,
                "blocked_responses": 0,
                "warned_responses": 0,
                "policy_violations": 0
            }
        
        hallucination_metrics = self.metrics["hallucination_metrics"]
        event_data = event.data
        
        # Update basic metrics
        hallucination_metrics["total_detections"] += 1
        
        # Track confidence levels
        confidence_level = event_data.get("confidence_level", "medium")
        if confidence_level in hallucination_metrics["confidence_levels"]:
            hallucination_metrics["confidence_levels"][confidence_level] += 1
        
        # Track detection methods
        detection_method = event_data.get("detection_method", "unknown")
        if detection_method not in hallucination_metrics["detection_methods"]:
            hallucination_metrics["detection_methods"][detection_method] = 0
        hallucination_metrics["detection_methods"][detection_method] += 1
        
        # Track hallucination probabilities
        probability = event_data.get("hallucination_probability", 0)
        hallucination_metrics["total_hallucination_probability"] += probability
        if hallucination_metrics["total_detections"] > 0:
            hallucination_metrics["avg_hallucination_probability"] = (
                hallucination_metrics["total_hallucination_probability"] / 
                hallucination_metrics["total_detections"]
            )
        
        # Track processing time
        processing_time = event_data.get("processing_time_ms", 0)
        hallucination_metrics["total_processing_time_ms"] += processing_time
        if hallucination_metrics["total_detections"] > 0:
            hallucination_metrics["avg_processing_time_ms"] = (
                hallucination_metrics["total_processing_time_ms"] / 
                hallucination_metrics["total_detections"]
            )
        
        # Track safety threshold violations
        safety_thresholds = event_data.get("safety_thresholds", {})
        block_threshold = safety_thresholds.get("block_threshold", 1.0)
        warn_threshold = safety_thresholds.get("warn_threshold", 1.0)
        
        if probability >= block_threshold:
            hallucination_metrics["blocked_responses"] += 1
            hallucination_metrics["policy_violations"] += 1
        elif probability >= warn_threshold:
            hallucination_metrics["warned_responses"] += 1
    
    def _process_safety_error_metrics(self, event: TelemetryEvent):
        """Process safety system error metrics."""
        if "safety_error_metrics" not in self.metrics:
            self.metrics["safety_error_metrics"] = {
                "total_errors": 0,
                "error_types": {},
                "error_methods": {},
                "fail_safe_activations": 0,
                "avg_error_recovery_time_ms": 0,
                "total_error_recovery_time_ms": 0,
                "policy_related_errors": 0,
                "recent_errors": []  # Keep last 10 errors for debugging
            }
        
        safety_error_metrics = self.metrics["safety_error_metrics"]
        event_data = event.data
        
        # Update basic metrics
        safety_error_metrics["total_errors"] += 1
        
        # Track error types
        error_type = event_data.get("error_type", "unknown")
        if error_type not in safety_error_metrics["error_types"]:
            safety_error_metrics["error_types"][error_type] = 0
        safety_error_metrics["error_types"][error_type] += 1
        
        # Track error methods (where the error occurred)
        error_method = event_data.get("error_method", "unknown")
        if error_method not in safety_error_metrics["error_methods"]:
            safety_error_metrics["error_methods"][error_method] = 0
        safety_error_metrics["error_methods"][error_method] += 1
        
        # Track fail-safe activations
        if event_data.get("fail_safe_enabled"):
            safety_error_metrics["fail_safe_activations"] += 1
        
        # Track error recovery time
        processing_time = event_data.get("processing_time_ms", 0)
        safety_error_metrics["total_error_recovery_time_ms"] += processing_time
        if safety_error_metrics["total_errors"] > 0:
            safety_error_metrics["avg_error_recovery_time_ms"] = (
                safety_error_metrics["total_error_recovery_time_ms"] / 
                safety_error_metrics["total_errors"]
            )
        
        # Track policy-related errors
        if "policy" in event_data.get("error_message", "").lower():
            safety_error_metrics["policy_related_errors"] += 1
        
        # Keep recent errors for debugging (last 10)
        error_record = {
            "timestamp": event.timestamp,
            "error_type": error_type,
            "error_method": error_method,
            "error_message": event_data.get("error_message", ""),
            "config_policy": event_data.get("config_policy", "unknown")
        }
        
        safety_error_metrics["recent_errors"].append(error_record)
        if len(safety_error_metrics["recent_errors"]) > 10:
            safety_error_metrics["recent_errors"].pop(0)
    
    def _update_response_time(self, duration_ms: float):
        completed_requests = self.metrics["successful_requests"] + self.metrics["failed_requests"]
        if completed_requests > 0:
            current_total = self.metrics["avg_response_time"] * (completed_requests - 1)
            self.metrics["avg_response_time"] = (current_total + duration_ms) / completed_requests
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.copy()
    
    def get_events(self) -> List[Dict[str, Any]]:
        return [asdict(event) for event in self.events_log]
    
    def stop_api_worker(self):
        """No-op - session completion removed."""
        pass


class AutoTelemetryHandler(BaseCallbackHandler):
    """Zero-config telemetry handler that automatically captures comprehensive LangChain telemetry with usage metadata."""
    
    def __init__(self, api_key: str = None, agent_id: str = None, debug_mode: bool = False):
        super().__init__()
        self.agent_id = agent_id or f"agent_{int(time.time())}"
        self.api_key = api_key or os.environ.get("OBSERVARE_API_KEY", "")
        self.debug_mode = debug_mode
        self.start_times: Dict[UUID, float] = {}
        self._tool_info: Dict[UUID, Dict[str, Any]] = {}
        
        # Initialize TelemetrySDK with API configuration
        self.telemetry_sdk = TelemetrySDK(
            api_key=self.api_key,
            debug_mode=debug_mode
        )
        
        # Pass agent_id to TelemetrySDK for API calls
        self.telemetry_sdk._current_agent_id = self.agent_id
        
        # Enhanced tracking
        self.model_info: Dict[str, Any] = {}
        self.conversation_context: List[Dict] = []
        self.tool_sequences: List[Dict] = []
        self.current_prompt_length = 0
        self.system_metadata = self._collect_system_metadata()
        
        # Token usage tracking via LangChain usage metadata
        self._token_usage_data: List[Dict] = []
        self.usage_metadata = {}  # Compatibility with UsageMetadataCallbackHandler
        self._setup_usage_metadata_tracking()
        
        # Streaming token tracking variables
        self._streaming_tokens = 0
        self._current_stream_run_id = None
        self._stream_start_time = None
        
        # Conversation-level correlation tracking
        self._conversation_correlation_id = None
        
        # Setup context manager methods for advanced tracking
        self._setup_context_manager_tracking()
    
    def set_conversation_correlation_id(self, correlation_id: str):
        """Set the conversation-level correlation ID for all events in this conversation."""
        self._conversation_correlation_id = correlation_id
    
    def get_conversation_correlation_id(self) -> Optional[str]:
        """Get the current conversation-level correlation ID."""
        return self._conversation_correlation_id
        
        # Setup OpenAI API interception as last resort (disabled for now)
        # self._setup_openai_interception()
    
    def _setup_usage_metadata_tracking(self):
        """Set up LangChain's usage metadata tracking."""
        pass
    
    def _setup_context_manager_tracking(self):
        """Set up context manager methods for token tracking."""
        try:
            from langchain_core.callbacks import get_usage_metadata_callback
            self._get_usage_metadata_callback = get_usage_metadata_callback
            self._context_manager_available = True
        except ImportError:
            try:
                from langchain.callbacks import get_usage_metadata_callback
                self._get_usage_metadata_callback = get_usage_metadata_callback
                self._context_manager_available = True
            except ImportError:
                self._context_manager_available = False
                # Fallback to OpenAI callback
                try:
                    from langchain_community.callbacks import get_openai_callback
                    self._get_openai_callback = get_openai_callback
                    self._openai_callback_available = True
                except ImportError:
                    self._openai_callback_available = False
    
    def _extract_usage_metadata_from_response(self, response) -> Dict[str, Any]:
        """Extract usage metadata from LLM response."""
        usage_data = {}
        
        # Method 1: Direct usage_metadata attribute (for chat models like gpt-4o-mini)
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            metadata = response.usage_metadata
            usage_data = {
                "input_tokens": metadata.get("input_tokens", 0),
                "output_tokens": metadata.get("output_tokens", 0),
                "total_tokens": metadata.get("total_tokens", 0),
                "capture_method": "usage_metadata_direct"
            }
        
        # Method 2: Check response_metadata.token_usage (OpenAI format)
        elif hasattr(response, 'response_metadata') and response.response_metadata:
            token_usage = response.response_metadata.get('token_usage', {})
            if token_usage.get('total_tokens'):
                usage_data = {
                    "input_tokens": token_usage.get("prompt_tokens", 0),
                    "output_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0),
                    "model_name": response.response_metadata.get("model_name", "unknown"),
                    "capture_method": "response_metadata"
                }
        
        # Method 3: Check if it's an LLMResult with usage metadata
        elif hasattr(response, 'llm_output') and response.llm_output:
            llm_output = response.llm_output
            if 'token_usage' in llm_output:
                token_usage = llm_output['token_usage']
                usage_data = {
                    "input_tokens": token_usage.get("prompt_tokens", 0),
                    "output_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0),
                    "capture_method": "llm_output"
                }
        
        # Method 4: Check for dict-like outputs with token_usage
        elif isinstance(response, dict) and 'token_usage' in response:
            token_usage = response['token_usage']
            usage_data = {
                "input_tokens": token_usage.get("prompt_tokens", 0),
                "output_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
                "capture_method": "dict_token_usage"
            }
        
        # Method 5: Check our callback's usage_metadata
        elif hasattr(self, 'usage_metadata') and self.usage_metadata:
            metadata = self.usage_metadata
            usage_data = {
                "input_tokens": metadata.get("input_tokens", 0),
                "output_tokens": metadata.get("output_tokens", 0),
                "total_tokens": metadata.get("total_tokens", 0),
                "capture_method": "callback_metadata"
            }
        
        return usage_data
    
    def _wrap_with_token_tracking(self, func, *args, **kwargs):
        """Wrap function execution with comprehensive token tracking."""
        # Method 1: Try context manager approach
        if self._context_manager_available:
            try:
                with self._get_usage_metadata_callback() as cb:
                    result = func(*args, **kwargs)
                    
                    if cb.usage_metadata and cb.usage_metadata.get("total_tokens", 0) > 0:
                        self._process_context_manager_usage(cb.usage_metadata)
                    
                    return result
            except Exception as e:
                pass
        
        # Method 2: Try OpenAI callback fallback
        if hasattr(self, '_openai_callback_available') and self._openai_callback_available:
            try:
                with self._get_openai_callback() as cb:
                    result = func(*args, **kwargs)
                    
                    if cb.total_tokens > 0:
                        self._process_openai_callback_usage(cb)
                    
                    return result
            except Exception as e:
                pass
        
        # Method 3: Direct execution with response parsing
        result = func(*args, **kwargs)
        self._extract_tokens_from_result(result)
        return result
    
    def _process_context_manager_usage(self, usage_metadata: Dict[str, Any]):
        """Process usage metadata from context manager."""
        token_data = {
            "timestamp": datetime.now().isoformat(),
            "input_tokens": usage_metadata.get("input_tokens", 0),
            "output_tokens": usage_metadata.get("output_tokens", 0),
            "total_tokens": usage_metadata.get("total_tokens", 0),
            "capture_method": "usage_metadata_context"
        }
        
        self._token_usage_data.append(token_data)
        self._emit_token_event(token_data)
    
    def _process_openai_callback_usage(self, callback):
        """Process usage from OpenAI callback."""
        token_data = {
            "timestamp": datetime.now().isoformat(),
            "input_tokens": callback.prompt_tokens,
            "output_tokens": callback.completion_tokens,
            "total_tokens": callback.total_tokens,
            "total_cost": callback.total_cost,
            "successful_requests": callback.successful_requests,
            "capture_method": "openai_callback"
        }
        
        self._token_usage_data.append(token_data)
        self._emit_token_event(token_data)
    
    def _process_context_manager_usage_direct(self, usage_metadata: Dict[str, Any]):
        """Process usage metadata from context manager (called directly from main.py)."""
        # Process context manager usage data
        
        # Handle both single model and multi-model format
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        
        if isinstance(usage_metadata, dict):
            # Check if it's multi-model format (keyed by model name)
            for key, value in usage_metadata.items():
                if isinstance(value, dict) and 'total_tokens' in value:
                    total_tokens += value.get('total_tokens', 0)
                    input_tokens += value.get('input_tokens', 0)
                    output_tokens += value.get('output_tokens', 0)
            
            # If no multi-model data found, check if it's direct format
            if total_tokens == 0 and 'total_tokens' in usage_metadata:
                total_tokens = usage_metadata.get('total_tokens', 0)
                input_tokens = usage_metadata.get('input_tokens', 0)
                output_tokens = usage_metadata.get('output_tokens', 0)
        
        if total_tokens > 0:
            token_data = {
                "timestamp": datetime.now().isoformat(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "capture_method": "context_manager_direct"
            }
            
            self._token_usage_data.append(token_data)
            self._emit_token_event(token_data)
    
    def _process_openai_callback_usage_direct(self, callback):
        """Process usage from OpenAI callback (called directly from main.py)."""
        token_data = {
            "timestamp": datetime.now().isoformat(),
            "input_tokens": callback.prompt_tokens,
            "output_tokens": callback.completion_tokens,
            "total_tokens": callback.total_tokens,
            "total_cost": callback.total_cost,
            "successful_requests": callback.successful_requests,
            "capture_method": "openai_callback_direct"
        }
        
        self._token_usage_data.append(token_data)
        self._emit_token_event(token_data)
    
    # OpenAI interception methods removed for production
    
    def process_context_tokens(self, usage_metadata: Dict[str, Any]):
        """Process token usage from get_usage_metadata_callback context manager."""
        
        # Handle multi-model format (model name as key)
        total_tokens = 0
        input_tokens = 0 
        output_tokens = 0
        model_name = "unknown"
        
        for key, value in usage_metadata.items():
            if isinstance(value, dict) and 'total_tokens' in value:
                # This is model data
                model_name = key
                total_tokens += value.get('total_tokens', 0)
                input_tokens += value.get('input_tokens', 0)
                output_tokens += value.get('output_tokens', 0)
        
        if total_tokens > 0:
            token_data = {
                "timestamp": datetime.now().isoformat(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "model": model_name,
                "capture_method": "context_manager",
                "total_cost": self._estimate_cost(model_name, input_tokens, output_tokens)
            }
            
            self._token_usage_data.append(token_data)
            self._emit_token_event(token_data)
    
    def process_openai_tokens(self, callback):
        """Process token usage from get_openai_callback."""
        token_data = {
            "timestamp": datetime.now().isoformat(),
            "input_tokens": callback.prompt_tokens,
            "output_tokens": callback.completion_tokens, 
            "total_tokens": callback.total_tokens,
            "model": "unknown",  # OpenAI callback doesn't provide model
            "capture_method": "openai_callback",
            "total_cost": callback.total_cost
        }
        
        self._token_usage_data.append(token_data)
        self._emit_token_event(token_data)
    
    def _estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model and token usage."""
        # Current pricing (2025)
        pricing = {
            "gpt-4o": {"input": 0.0025/1000, "output": 0.01/1000},
            "gpt-4o-mini": {"input": 0.000075/1000, "output": 0.0003/1000},
            "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
            "gpt-3.5-turbo": {"input": 0.0005/1000, "output": 0.0015/1000},
            "o1-preview": {"input": 0.015/1000, "output": 0.06/1000},
            "o1-mini": {"input": 0.003/1000, "output": 0.012/1000},
        }
        
        # Find matching model (case insensitive)
        model_name_lower = model_name.lower() if model_name else ""
        for model_key, rates in pricing.items():
            if model_key in model_name_lower:
                cost = (input_tokens * rates["input"]) + (output_tokens * rates["output"])
                return cost
        
        # Default to gpt-4o-mini pricing
        default_rates = pricing["gpt-4o-mini"]
        cost = (input_tokens * default_rates["input"]) + (output_tokens * default_rates["output"])
        return cost
    
    def _emit_token_event(self, token_data: Dict[str, Any]):
        """Emit a telemetry event for token usage."""
        # Calculate cost if not already present
        if not token_data.get("total_cost") and token_data.get("total_tokens", 0) > 0:
            model_name = token_data.get("model", self.model_info.get("model_name", "gpt-4o-mini"))
            estimated_cost = self._estimate_cost(
                model_name,
                token_data.get("input_tokens", 0),
                token_data.get("output_tokens", 0)
            )
            token_data["total_cost"] = estimated_cost
        
        # Prepare event data
        event_data = {
            "token_usage": {
                "input_tokens": token_data.get("input_tokens", 0),
                "output_tokens": token_data.get("output_tokens", 0),
                "total_tokens": token_data.get("total_tokens", 0),
                "model": token_data.get("model", "unknown")
            },
            "cost_data": {
                "total_cost": token_data.get("total_cost", 0),
                "currency": "USD"
            },
            "capture_method": token_data.get("capture_method", "unknown"),
            "successful_requests": token_data.get("successful_requests", 1)
        }
        
        # Add correlation_id if present
        if "correlation_id" in token_data:
            event_data["correlation_id"] = token_data["correlation_id"]
        
        event = TelemetryEvent(
            timestamp=token_data["timestamp"],
            event_type="token_usage",
            agent_id=self.agent_id,
            data=event_data
        )
        
        self.telemetry_sdk.process_event(event)
        
        # Update our usage_metadata for compatibility
        self.usage_metadata = {
            "input_tokens": token_data.get("input_tokens", 0),
            "output_tokens": token_data.get("output_tokens", 0),
            "total_tokens": token_data.get("total_tokens", 0),
            "total_cost": token_data.get("total_cost", 0)
        }
    
    def _extract_tokens_from_result(self, result):
        """Extract tokens from execution result."""
        
        if result:
            # Check if result has usage information
            usage_data = self._extract_usage_metadata_from_response(result)
            if usage_data.get("total_tokens", 0) > 0:
                self._token_usage_data.append({
                    **usage_data,
                    "timestamp": datetime.now().isoformat()
                })
                self._emit_token_event({
                    **usage_data,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Also check if result is a dict with output containing usage
            elif isinstance(result, dict) and 'output' in result:
                output = result['output']
                usage_data = self._extract_usage_metadata_from_response(output)
                if usage_data.get("total_tokens", 0) > 0:
                    self._token_usage_data.append({
                        **usage_data,
                        "timestamp": datetime.now().isoformat()
                    })
                    self._emit_token_event({
                        **usage_data,
                        "timestamp": datetime.now().isoformat()
                    })
    
    
    
    def _collect_system_metadata(self) -> Dict[str, Any]:
        """Collect comprehensive system and environment metadata."""
        try:
            import langchain
            langchain_version = langchain.__version__
        except:
            langchain_version = "unknown"
        
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "langchain_version": langchain_version,
            "timestamp": datetime.now().isoformat(),
            "sdk_version": "1.0.0"  # Your SDK version
        }
    
    def _extract_model_info(self, serialized: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive model information from serialized data."""
        model_info = {}
        
        
        # Ensure serialized is not None
        if not serialized:
            return model_info
        
        # Extract from different serialization formats
        if "kwargs" in serialized:
            kwargs = serialized["kwargs"]
            model_info.update({
                "model_name": kwargs.get("model_name", kwargs.get("model", "unknown")),
                "temperature": kwargs.get("temperature"),
                "max_tokens": kwargs.get("max_tokens"),
                "top_p": kwargs.get("top_p"),
                "frequency_penalty": kwargs.get("frequency_penalty"),
                "presence_penalty": kwargs.get("presence_penalty")
            })
        
        # Try other common serialization patterns
        if "id" in serialized:
            for key in serialized["id"]:
                if key == "model":
                    model_info["model_name"] = serialized["id"][key]
                elif key in ["temperature", "max_tokens", "top_p"]:
                    model_info[key] = serialized["id"][key]
        
        # Extract from repr or type info
        class_name = serialized.get("name", serialized.get("_type", "")) or ""
        if class_name and "openai" in class_name.lower():
            model_info["provider"] = "OpenAI"
        elif class_name and "anthropic" in class_name.lower():
            model_info["provider"] = "Anthropic"
        else:
            model_info["provider"] = "Unknown"
        
        # Try to extract from verbose output in LangChain
        if "repr" in serialized and serialized["repr"]:
            repr_str = serialized["repr"]
            # Parse model name from repr string
            if "model=" in repr_str:
                import re
                model_match = re.search(r"model='([^']+)'", repr_str)
                if model_match:
                    model_info["model_name"] = model_match.group(1)
            
            # Parse other parameters
            for param in ["temperature", "max_tokens", "top_p"]:
                if f"{param}=" in repr_str:
                    param_match = re.search(rf"{param}=([^,\)]+)", repr_str)
                    if param_match:
                        try:
                            model_info[param] = float(param_match.group(1))
                        except:
                            model_info[param] = param_match.group(1)
            
        return {k: v for k, v in model_info.items() if v is not None}
    
    def _parse_usage_from_verbose_output(self, verbose_text: str) -> Dict[str, Any]:
        """Parse token usage from LangChain verbose output as fallback."""
        usage_info = {}
        
        # Look for common patterns in verbose output
        import re
        
        # Pattern for token usage in verbose logs
        token_patterns = [
            r"prompt_tokens[:=]\s*(\d+)",
            r"completion_tokens[:=]\s*(\d+)", 
            r"total_tokens[:=]\s*(\d+)",
            r"usage.*?prompt_tokens.*?(\d+)",
            r"usage.*?completion_tokens.*?(\d+)",
            r"tokens.*?(\d+)"
        ]
        
        for pattern in token_patterns:
            matches = re.findall(pattern, verbose_text, re.IGNORECASE)
            if matches:
                # Extract token numbers
                for match in matches:
                    if "prompt" in pattern:
                        usage_info["prompt_tokens"] = int(match)
                    elif "completion" in pattern:
                        usage_info["completion_tokens"] = int(match)
                    elif "total" in pattern:
                        usage_info["total_tokens"] = int(match)
        
        # Look for model information
        model_patterns = [
            r"model[:=]\s*['\"]([^'\"]+)['\"]",
            r"gpt-[34]\.?[0-9]*[-\w]*",
            r"text-davinci-\d+",
            r"claude-\w+"
        ]
        
        for pattern in model_patterns:
            match = re.search(pattern, verbose_text, re.IGNORECASE)
            if match:
                usage_info["model"] = match.group(1) if match.groups() else match.group(0)
                break
                
        return usage_info
    
    def _calculate_content_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate comprehensive content analysis metrics."""
        # Ensure content is a string and not None
        content = str(content) if content is not None else ""
        if not content:
            return {}
            
        words = content.split()
        sentences = content.split('.')
        
        return {
            "char_count": len(content),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "has_code": any(marker in content for marker in ['```', 'def ', 'class ', 'import ']),
            "has_urls": 'http' in content.lower(),
            "complexity_score": len(set(words)) / len(words) if words else 0  # Unique word ratio
        }
        
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], 
                      *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture agent/chain start events."""
        if parent_run_id is None:  # Top-level chain (agent start)
            # Set conversation correlation ID for the entire conversation
            if not self._conversation_correlation_id:
                self._conversation_correlation_id = str(run_id)
                
            self.start_times[run_id] = time.time()
            
            # Extract and store model information (handle None serialized)
            model_info = {}
            if serialized is not None:
                model_info = self._extract_model_info(serialized)
                if model_info:
                    self.model_info.update(model_info)
            
            # Analyze input content
            input_text = str(inputs.get("input", inputs.get("question", ""))) if inputs else ""
            content_metrics = self._calculate_content_metrics(input_text)
            self.current_prompt_length = content_metrics.get("char_count", 0)
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="agent_start",
                agent_id=self.agent_id,
                data={
                    "inputs": inputs or {},
                    "chain_type": serialized.get("name", "unknown") if serialized else "unknown",
                    "model_info": model_info,
                    "content_metrics": content_metrics,
                    "system_metadata": self.system_metadata,
                    "correlation_id": self._conversation_correlation_id
                }
            )
            self.telemetry_sdk.process_event(event)
    
    def on_chain_end(self, outputs: Dict[str, Any], *, run_id: UUID, 
                    parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture agent/chain completion events."""
        # Chain ended
        
        if parent_run_id is None and run_id in self.start_times:  # Top-level chain
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            # Try to extract token usage from outputs or verbose logs
            token_usage = self._extract_token_usage_from_response(outputs)
            
            # Extract usage metadata from outputs
            usage_metadata = self._extract_usage_metadata_from_response(outputs)
            if usage_metadata.get("total_tokens", 0) > 0:
                token_usage.update(usage_metadata)
            
            # Merge with callback usage metadata if available
            if hasattr(self, 'usage_metadata') and self.usage_metadata and not token_usage.get("total_tokens"):
                metadata = self.usage_metadata
                token_usage.update({
                    "total_tokens": metadata.get("total_tokens", 0),
                    "input_tokens": metadata.get("input_tokens", 0),
                    "output_tokens": metadata.get("output_tokens", 0),
                    "capture_method": "callback_usage_metadata"
                })
            
            # Check recent token usage data
            if self._token_usage_data and not token_usage.get("total_tokens"):
                latest_token_data = self._token_usage_data[-1]
                if latest_token_data.get("total_tokens"):
                    token_usage.update({
                        "total_tokens": latest_token_data["total_tokens"],
                        "input_tokens": latest_token_data.get("input_tokens", 0),
                        "output_tokens": latest_token_data.get("output_tokens", 0),
                        "total_cost": latest_token_data.get("total_cost", 0),
                        "capture_method": latest_token_data.get("capture_method", "recent_data")
                    })
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="agent_completion",
                agent_id=self.agent_id,
                data={
                    "outputs": outputs,
                    "success": True,
                    "token_usage": token_usage,
                    "model_info": self.model_info,
                    "correlation_id": self._conversation_correlation_id or str(run_id)
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
            
            # Reset conversation correlation ID after completion for next conversation
            # Only reset if this run_id matches our current correlation ID
            if self._conversation_correlation_id == str(run_id):
                self._conversation_correlation_id = None
    
    def _extract_token_usage_from_response(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract token usage from LangChain response outputs."""
        token_data = {}
        # Check if outputs contain token usage information
        if isinstance(outputs, dict):
            # Look for common token usage keys
            for key in ["token_usage", "usage", "llm_output", "metadata"]:
                if key in outputs and outputs[key]:
                    usage_info = outputs[key]
                    if isinstance(usage_info, dict):
                        # Extract standard token fields
                        for token_key in ["prompt_tokens", "completion_tokens", "total_tokens"]:
                            if token_key in usage_info:
                                token_data[token_key] = usage_info[token_key]
                        
                        # Extract model info
                        for model_key in ["model", "model_name"]:
                            if model_key in usage_info:
                                token_data["model"] = usage_info[model_key]
                                
            # Look in output text for usage patterns (fallback)
            output_text = str(outputs.get("output", ""))
            if output_text and not token_data:
                parsed_usage = self._parse_usage_from_verbose_output(output_text)
                token_data.update(parsed_usage)
        
        # If we found token data, estimate costs
        if token_data.get("total_tokens"):
            model_name = token_data.get("model", "gpt-3.5-turbo")
            cost_estimate = self._calculate_cost_estimate(model_name, token_data)
            token_data["cost_estimate"] = cost_estimate
        
        return token_data
    
    def on_chain_error(self, error: BaseException, *, run_id: UUID, 
                      parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture agent/chain error events."""
        if parent_run_id is None and run_id in self.start_times:  # Top-level chain
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="agent_error",
                agent_id=self.agent_id,
                data={
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "success": False,
                    "correlation_id": self._conversation_correlation_id or str(run_id)
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, 
                     *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture tool execution start events."""
        # Tool started
        self.start_times[run_id] = time.time()
        
        # Store tool info for use in on_tool_end
        tool_name = serialized.get('name', serialized.get('id', 'unknown_tool'))
        self._tool_info[run_id] = {
            'name': tool_name,
            'input': input_str,
            'serialized': serialized
        }
        # Store tool info for correlation
    
    def on_tool_end(self, output: Any, *, run_id: UUID, 
                   parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture tool execution completion events."""
        # Tool completed
        if run_id in self.start_times:
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            # Get tool info from stored data
            tool_info = self._tool_info.pop(run_id, {})
            tool_name = tool_info.get('name', 'unknown_tool')
            tool_input = tool_info.get('input', '')
            
            # Create tool execution event
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="tool_execution",
                agent_id=self.agent_id,
                data={
                    "tool_name": tool_name,
                    "input": str(tool_input)[:500],  # Limit input size
                    "output": str(output)[:1000],  # Limit output size
                    "correlation_id": self._conversation_correlation_id or str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "duration_ms": duration
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
            # Tool execution event sent
    
    def on_tool_error(self, error: BaseException, *, run_id: UUID, 
                     parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture tool execution error events."""
        if run_id in self.start_times:
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            # Get tool info from stored data
            tool_info = self._tool_info.pop(run_id, {})
            tool_name = tool_info.get('name', 'unknown_tool')
            tool_input = tool_info.get('input', '')
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="tool_execution",
                agent_id=self.agent_id,
                data={
                    "tool_name": tool_name,
                    "input": str(tool_input)[:500],  # Limit input size
                    "output": f"Error: {str(error)}",
                    "error": True,
                    "correlation_id": self._conversation_correlation_id or str(run_id),
                    "parent_run_id": str(parent_run_id) if parent_run_id else None,
                    "duration_ms": duration
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
    
    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], 
                           *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture chat model start events for reliable token tracking."""
        self.start_times[run_id] = time.time()
        
        # Extract model info from chat model
        model_info = self._extract_model_info(serialized)
        if model_info:
            self.model_info.update(model_info)
        
        # Analyze message content
        total_content = ""
        message_analysis = []
        
        for message_list in messages:
            for message in message_list:
                content = getattr(message, 'content', str(message))
                total_content += content + " "
                
                message_analysis.append({
                    "type": getattr(message, 'type', type(message).__name__),
                    "length": len(content),
                    "metrics": self._calculate_content_metrics(content)
                })
        
        event = TelemetryEvent(
            timestamp=datetime.now().isoformat(),
            event_type="chat_model_start",
            agent_id=self.agent_id,
            data={
                "model_info": model_info,
                "message_count": sum(len(msg_list) for msg_list in messages),
                "total_content_length": len(total_content.strip()),
                "message_analysis": message_analysis,
                "content_metrics": self._calculate_content_metrics(total_content),
                "run_id": str(run_id)
            }
        )
        self.telemetry_sdk.process_event(event)
    
    def on_chat_model_end(self, response: LLMResult, *, run_id: UUID, 
                         parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture chat model completion with comprehensive token usage."""
        
        # Finalize streaming tokens if applicable
        self._finalize_streaming_tokens(run_id)
        
        if run_id in self.start_times:
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            # Extract comprehensive token usage
            token_usage = {}
            model_name = "unknown"
            
            # Try to get usage metadata first (newer method)
            usage_metadata = self._extract_usage_metadata_from_response(response)
            if usage_metadata.get("total_tokens", 0) > 0:
                token_usage = {
                    "total_tokens": usage_metadata["total_tokens"],
                    "prompt_tokens": usage_metadata.get("input_tokens", 0),
                    "completion_tokens": usage_metadata.get("output_tokens", 0)
                }
            # Fallback to llm_output method
            elif hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {})
                model_name = response.llm_output.get('model_name', model_name)
            
            # Check callback usage metadata
            if not token_usage.get("total_tokens") and hasattr(self, 'usage_metadata') and self.usage_metadata:
                metadata = self.usage_metadata
                token_usage = {
                    "total_tokens": metadata.get("total_tokens", 0),
                    "prompt_tokens": metadata.get("input_tokens", 0),
                    "completion_tokens": metadata.get("output_tokens", 0)
                }
            
            # Store token usage when found
            if token_usage.get("total_tokens", 0) > 0:
                self._emit_token_event({
                    "timestamp": datetime.now().isoformat(),
                    "input_tokens": token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0)),
                    "output_tokens": token_usage.get("completion_tokens", token_usage.get("output_tokens", 0)),
                    "total_tokens": token_usage.get("total_tokens", 0),
                    "capture_method": "chat_model_end",
                    "correlation_id": self._conversation_correlation_id or str(run_id)  # Use conversation correlation_id if available
                })
            
            # Calculate cost estimates (approximate for OpenAI models)
            cost_estimate = self._calculate_cost_estimate(model_name, token_usage)
            
            # Analyze response content
            response_content = ""
            generation_analysis = []
            
            for generation in response.generations:
                for gen in generation:
                    content = getattr(gen, 'text', str(gen))
                    response_content += content + " "
                    
                    generation_analysis.append({
                        "length": len(content),
                        "metrics": self._calculate_content_metrics(content)
                    })
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="chat_model_completion",
                agent_id=self.agent_id,
                data={
                    "model": model_name,
                    "token_usage": token_usage,
                    "cost_estimate": cost_estimate,
                    "generations_count": len(response.generations),
                    "response_content_length": len(response_content.strip()),
                    "generation_analysis": generation_analysis,
                    "content_metrics": self._calculate_content_metrics(response_content),
                    "performance": {
                        "duration_ms": duration,
                        "tokens_per_second": token_usage.get('total_tokens', 0) / (duration / 1000) if duration > 0 else 0
                    },
                    "correlation_id": self._conversation_correlation_id or str(run_id)
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
    
    def _calculate_cost_estimate(self, model_name: str, token_usage: Dict[str, Any]) -> Dict[str, float]:
        """Calculate approximate cost estimates for different models."""
        # Updated pricing estimates (as of 2025)
        pricing = {
            "gpt-4o": {"prompt": 0.0025/1000, "completion": 0.01/1000},
            "gpt-4o-mini": {"prompt": 0.000075/1000, "completion": 0.0003/1000},
            "gpt-4": {"prompt": 0.03/1000, "completion": 0.06/1000},
            "gpt-4-turbo": {"prompt": 0.01/1000, "completion": 0.03/1000},
            "gpt-3.5-turbo": {"prompt": 0.0005/1000, "completion": 0.0015/1000},
            "gpt-3.5-turbo-16k": {"prompt": 0.003/1000, "completion": 0.004/1000},
            "o1-preview": {"prompt": 0.015/1000, "completion": 0.06/1000},
            "o1-mini": {"prompt": 0.003/1000, "completion": 0.012/1000}
        }
        
        model_name_lower = model_name.lower() if model_name else ""
        model_key = next((k for k in pricing.keys() if k in model_name_lower), None)
        
        if not model_key or not token_usage:
            return {"estimated_cost": 0, "currency": "USD"}
        
        prompt_cost = token_usage.get('prompt_tokens', token_usage.get('input_tokens', 0)) * pricing[model_key]["prompt"]
        completion_cost = token_usage.get('completion_tokens', token_usage.get('output_tokens', 0)) * pricing[model_key]["completion"]
        total_cost = prompt_cost + completion_cost
        
        return {
            "estimated_cost": total_cost,
            "prompt_cost": prompt_cost,
            "completion_cost": completion_cost,
            "currency": "USD",
            "model_pricing": pricing[model_key]
        }
    
    def on_agent_action(self, action: AgentAction, *, run_id: UUID, 
                       parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture agent action decisions (tool selection)."""
        # Agent action triggered
        
        # Store tool info for use in tool callbacks
        self._current_tool_name = action.tool
        self._current_tool_input = action.tool_input
        
        # HACK: Since tool callbacks aren't firing and tool wrappers aren't called,
        # let's create tool_execution events directly from agent actions
        # Create tool execution from agent action
        
        # Create a tool execution event immediately
        event = TelemetryEvent(
            timestamp=datetime.now().isoformat(),
            event_type="tool_execution",
            agent_id=self.agent_id,
            data={
                "tool_name": action.tool,
                "input": str(action.tool_input)[:500],
                "output": "EXECUTING...",  # We'll update this later if possible
                "correlation_id": self._conversation_correlation_id or str(run_id),
                "parent_run_id": str(parent_run_id) if parent_run_id else None,
                "duration_ms": 0,  # Will be updated if we can capture completion
                "capture_method": "agent_action_direct",
                "status": "started"
            },
            duration_ms=0
        )
        
        self.telemetry_sdk.process_event(event)
        # Tool execution event created
        
        # Still store start time in case we can capture completion elsewhere
        tool_execution_id = f"{action.tool}_{run_id}"
        self.start_times[tool_execution_id] = time.time()
        # Started tracking tool execution
        
        # Track tool sequence for execution context
        tool_sequence_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": action.tool,
            "input": action.tool_input,
            "run_id": str(run_id),
            "sequence_position": len(self.tool_sequences)
        }
        self.tool_sequences.append(tool_sequence_entry)
        
        # Analyze tool input content
        input_metrics = self._calculate_content_metrics(str(action.tool_input))
        
        event = TelemetryEvent(
            timestamp=datetime.now().isoformat(),
            event_type="agent_action",
            agent_id=self.agent_id,
            data={
                "tool": action.tool,
                "tool_input": action.tool_input,
                "log": action.log,
                "input_metrics": input_metrics,
                "sequence_position": len(self.tool_sequences) - 1,
                "tool_history": [t["tool"] for t in self.tool_sequences],
                "decision_context": {
                    "previous_tools": [t["tool"] for t in self.tool_sequences[-3:]] if len(self.tool_sequences) > 1 else [],
                    "conversation_length": len(self.conversation_context)
                },
                "run_id": str(run_id)
            }
        )
        self.telemetry_sdk.process_event(event)
    
    def on_agent_finish(self, finish: AgentFinish, *, run_id: UUID, 
                       parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture agent completion events with comprehensive analysis."""
        # Analyze final output
        output_text = str(finish.return_values.get("output", ""))
        output_metrics = self._calculate_content_metrics(output_text)
        
        # Add to conversation context
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response",
            "content": output_text,
            "metrics": output_metrics,
            "run_id": str(run_id)
        }
        self.conversation_context.append(conversation_entry)
        
        # Execution flow analysis
        execution_analysis = {
            "total_tools_used": len(self.tool_sequences),
            "unique_tools": len(set(t["tool"] for t in self.tool_sequences)),
            "tool_sequence": [t["tool"] for t in self.tool_sequences],
            "conversation_turns": len(self.conversation_context),
            "execution_path_complexity": len(set(t["tool"] for t in self.tool_sequences)) / max(1, len(self.tool_sequences))
        }
        
        # Include latest token usage data if available
        token_usage = {}
        
        # Check usage metadata from callback
        if hasattr(self, 'usage_metadata') and self.usage_metadata:
            metadata = self.usage_metadata
            token_usage = {
                "total_tokens": metadata.get("total_tokens", 0),
                "input_tokens": metadata.get("input_tokens", 0),
                "output_tokens": metadata.get("output_tokens", 0),
                "capture_method": "callback_usage_metadata"
            }
        
        # Check recent token usage data
        elif self._token_usage_data:
            latest_token_data = self._token_usage_data[-1]
            token_usage = {
                "total_tokens": latest_token_data.get("total_tokens", 0),
                "input_tokens": latest_token_data.get("input_tokens", 0),
                "output_tokens": latest_token_data.get("output_tokens", 0),
                "total_cost": latest_token_data.get("total_cost", 0),
                "capture_method": latest_token_data.get("capture_method", "recent_data")
            }

        event = TelemetryEvent(
            timestamp=datetime.now().isoformat(),
            event_type="agent_finish",
            agent_id=self.agent_id,
            data={
                "output": finish.return_values,
                "log": finish.log,
                "output_metrics": output_metrics,
                "execution_analysis": execution_analysis,
                "tool_sequences": self.tool_sequences,
                "conversation_context": self.conversation_context[-5:],  # Last 5 entries
                "model_info": self.model_info,
                "token_usage": token_usage,
                "run_id": str(run_id)
            }
        )
        self.telemetry_sdk.process_event(event)
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], 
                    *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture LLM call start events."""
        self.start_times[run_id] = time.time()
    
    def on_llm_end(self, response: LLMResult, *, run_id: UUID, 
                  parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture LLM call completion events."""
        
        # Finalize streaming tokens if applicable
        self._finalize_streaming_tokens(run_id)
        
        if run_id in self.start_times:
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            # Extract token usage if available
            token_usage = {}
            model_name = 'unknown'
            if hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {})
                model_name = response.llm_output.get('model_name', 'unknown')
            
            # Calculate cost estimate if we have token usage
            cost_estimate = None
            estimated_cost_usd = None
            if token_usage:
                cost_estimate = self._calculate_cost_estimate(model_name, token_usage)
                estimated_cost_usd = cost_estimate.get('total_cost', 0) if cost_estimate else 0
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="llm_call",
                agent_id=self.agent_id,
                data={
                    "model": model_name,
                    "token_usage": token_usage,
                    "generations_count": len(response.generations),
                    "correlation_id": self._conversation_correlation_id or str(run_id),
                    "estimated_cost_usd": estimated_cost_usd,
                    "cost_estimate": cost_estimate
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
    
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], *, run_id: UUID, 
                    parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture LLM call error events."""
        if run_id in self.start_times:
            duration = (time.time() - self.start_times.pop(run_id)) * 1000
            
            event = TelemetryEvent(
                timestamp=datetime.now().isoformat(),
                event_type="llm_error",
                agent_id=self.agent_id,
                data={
                    "error": str(error),
                    "error_type": type(error).__name__,
                    "correlation_id": self._conversation_correlation_id or str(run_id)
                },
                duration_ms=duration
            )
            self.telemetry_sdk.process_event(event)
    
    def on_llm_new_token(self, token: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs) -> None:
        """Capture individual tokens during streaming - enables real-time token counting."""
        # Track streaming tokens for current run
        if self._current_stream_run_id != run_id:
            # New stream started
            self._current_stream_run_id = run_id
            self._streaming_tokens = 0
            self._stream_start_time = time.time()
        
        self._streaming_tokens += 1
    
    def _finalize_streaming_tokens(self, run_id: UUID):
        """Finalize streaming token count and emit telemetry event."""
        if self._current_stream_run_id == run_id and self._streaming_tokens > 0:
            duration = (time.time() - self._stream_start_time) * 1000 if self._stream_start_time else 0
            
            # Create token usage event for streaming
            token_data = {
                "timestamp": datetime.now().isoformat(),
                "input_tokens": 0,  # We only count output tokens during streaming
                "output_tokens": self._streaming_tokens,
                "total_tokens": self._streaming_tokens,
                "model": self.model_info.get("model_name", "unknown"),
                "capture_method": "streaming",
                "stream_duration_ms": duration,
                "correlation_id": self._conversation_correlation_id or str(run_id)  # Use conversation correlation_id if available
            }
            
            self._token_usage_data.append(token_data)
            self._emit_token_event(token_data)
            
            # Reset streaming state
            self._streaming_tokens = 0
            self._current_stream_run_id = None
            self._stream_start_time = None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from the telemetry SDK."""
        return self.telemetry_sdk.get_metrics()
    
    def stop(self):
        """Stop the telemetry handler and clean up API connections."""
        self.telemetry_sdk.stop_api_worker()