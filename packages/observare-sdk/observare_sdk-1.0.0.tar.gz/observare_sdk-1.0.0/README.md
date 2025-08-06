# Observare SDK

**Enterprise LLM Safety & Observability Platform**

Zero-config integration for comprehensive LLM safety, including PII redaction, hallucination detection, and real-time observability for your AI applications.

## 🚀 Quick Start

Transform any LangChain application into a secure, observable system with **one line of code**:

```python
from observare_llm import ObservareChat
from observare_config import SafetyPolicy
from langchain_openai import ChatOpenAI

# Before: Standard LangChain usage
llm = ChatOpenAI(model="gpt-4o-mini")

# After: Enterprise-grade safety wrapper
safe_llm = ObservareChat(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    policy=SafetyPolicy.BALANCED,           # STRICT, BALANCED, or PERMISSIVE
    api_key="your-observare-api-key"
)

# Use exactly like your original LangChain model
response = safe_llm.invoke([HumanMessage(content="Hello!")])

# All safety features are now active ✨
```

## 🛡️ Enterprise Safety Features

### **PII Redaction & Compliance**
Automatic detection and redaction of sensitive data before it reaches LLM providers:

```python
# Input with PII
user_input = "My email is john.doe@company.com and SSN is 123-45-6789"

# Automatically redacted before sending to OpenAI
# → "My email is [EMAIL_REDACTED] and SSN is [SSN_REDACTED]"
```

**Supported PII Types:**
- Email addresses
- Phone numbers  
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses
- Custom patterns via configuration

### **Hallucination Detection**
Multi-method hallucination detection with confidence scoring:

```python
# Automatic analysis of every LLM response
response = safe_llm.invoke([HumanMessage(content="What is the capital of Mars?")])

# Real-time hallucination probability: 0.95 (HIGH RISK)
# Confidence level: HIGH
# Detection method: consistency_check
```

**Detection Methods:**
- **Consistency Checking**: Multiple inference validation
- **Chain of Verification (CoVe)**: Question-based fact checking  
- **Uncertainty Quantification**: Confidence-based analysis
- **Custom Rules**: Configurable domain-specific validation

### **Configurable Safety Policies**

```python
# STRICT: Maximum security for sensitive applications
safe_llm.apply_policy(SafetyPolicy.STRICT)
# - Block high-risk responses (hallucination > 0.7)
# - Aggressive PII redaction
# - Comprehensive logging

# BALANCED: Production-ready balance (default)
safe_llm.apply_policy(SafetyPolicy.BALANCED) 
# - Warn on medium-risk responses
# - Standard PII protection
# - Performance optimized

# PERMISSIVE: Development/testing environments
safe_llm.apply_policy(SafetyPolicy.PERMISSIVE)
# - Log-only mode
# - Minimal redaction
# - Maximum performance
```

## 📊 Real-Time Observability

### **Comprehensive Event Streaming**

All safety and performance events are automatically sent to your `/v1/events` endpoint:

```json
{
  "event_type": "pii_detection",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:45Z",
  "data": {
    "total_redactions": 2,
    "redaction_summary": {"email": 1, "ssn": 1},
    "original_content_preview": "My email is john.doe@company.com...",
    "redacted_content_preview": "My email is [EMAIL_REDACTED]...",
    "compliance_data": {
      "audit_log": true,
      "policy": "balanced"
    }
  }
}
```

### **Event Correlation System**

Link all safety events to their originating conversations:

```sql
-- Query all events for a specific conversation
SELECT * FROM events 
WHERE correlation_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY timestamp;

-- Find high-risk hallucinations with original prompts
SELECT 
  prompt_preview,
  response_preview, 
  hallucination_probability
FROM events
WHERE event_type = 'hallucination_detection' 
  AND data->>'hallucination_probability' > '0.7';
```

### **Performance Metrics**

```python
# Get comprehensive safety statistics
stats = safe_llm.get_stats()

{
  "total_requests": 1247,
  "pii_redactions": 89,
  "hallucination_detections": 12,
  "safety_violations": 3,
  "policy_changes": 2,
  "avg_processing_time_ms": 245.7,
  "compliance_metrics": {
    "gdpr_scans": 1247,
    "pii_categories_detected": ["email", "phone", "ssn"],
    "redaction_success_rate": 0.998
  }
}
```

## 🔧 Advanced Configuration

### **Custom Safety Policies**

```python
from observare_config import SafetyConfiguration

custom_config = SafetyConfiguration(
    policy="custom",
    pii=PIIConfiguration(
        enabled=True,
        strategies=["regex", "ml_based", "custom_rules"],
        min_confidence_threshold=0.8,
        custom_patterns={
            "employee_id": r"EMP-\d{6}",
            "project_code": r"PROJ-[A-Z]{3}-\d{4}"
        }
    ),
    hallucination=HallucinationConfiguration(
        enabled=True,
        detection_method="multi_method",
        block_threshold=0.8,
        warn_threshold=0.5,
        consistency_samples=3
    )
)

safe_llm = ObservareChat(llm=base_llm, config=custom_config)
```

### **Runtime Policy Updates**

```python
# Change safety settings without redeployment
safe_llm.apply_policy(SafetyPolicy.STRICT)  # Increase security
safe_llm.apply_policy(SafetyPolicy.PERMISSIVE)  # Reduce for testing

# Apply custom configurations
safe_llm.update_config({
    "hallucination.block_threshold": 0.9,
    "pii.min_confidence_threshold": 0.85
})
```

## 🏗️ Enterprise Integration

### **Zero-Config Agent Integration**

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from observare_sdk import AutoTelemetryHandler

# Existing agent code
agent = create_openai_functions_agent(safe_llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[AutoTelemetryHandler(api_key="your-api-key")]
)

# Now includes:
# ✅ Tool execution safety
# ✅ Multi-step conversation tracking  
# ✅ Agent decision auditing
# ✅ Complete conversation correlation
```

### **Production Monitoring**

The SDK provides enterprise-grade monitoring capabilities:

**Event Types Captured:**
- `agent_start` / `agent_finish` - Conversation lifecycle
- `pii_detection` - Sensitive data redaction events
- `hallucination_detection` - AI safety assessments
- `tool_execution` - Agent tool usage
- `safety_violations` - Policy enforcement actions

**Correlation & Traceability:**
- Each conversation gets a unique `correlation_id`
- All safety events link back to originating prompts
- Full audit trail for compliance requirements
- Real-time alerting on safety thresholds

## 📈 Enterprise Benefits

### **Compliance & Security**
- **GDPR/HIPAA/CCPA** compliance through automatic PII redaction
- **Data residency** - sensitive data never leaves your infrastructure
- **Audit trails** - comprehensive logging for regulatory requirements
- **Access controls** - configurable safety policies per environment

### **Risk Mitigation**
- **Hallucination prevention** - multi-method AI safety validation
- **Content filtering** - block inappropriate or dangerous responses
- **Fail-safe operations** - graceful degradation on safety system errors
- **Real-time alerting** - immediate notification of safety violations

### **Operational Excellence**
- **Zero-config deployment** - works with existing LangChain applications
- **Performance monitoring** - comprehensive metrics and observability
- **Cost optimization** - token usage tracking and cost analysis
- **Scalable architecture** - handles high-volume production workloads

## 🔗 API Integration

### **Events Endpoint**

The SDK sends all events to your configured endpoint:

```bash
POST /v1/events
Content-Type: application/json

{
  "event_type": "hallucination_detection",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "production-agent-1",
  "timestamp": "2024-01-15T10:30:45Z",
  "data": {
    "hallucination_probability": 0.15,
    "confidence_level": "high",
    "detection_method": "consistency_check",
    "prompt_preview": "What is the capital of France?",
    "response_preview": "The capital of France is Paris...",
    "processing_time_ms": 1250.5
  }
}
```

### **Webhook Configuration**

```python
safe_llm = ObservareChat(
    llm=base_llm,
    api_key="your-api-key",
    api_endpoint="https://your-domain.com/v1/events",  # Custom endpoint
    telemetry_enabled=True
)
```

## 🚦 Getting Started

### **1. Installation**

```bash
pip install observare-sdk
```

### **2. Basic Setup**

```python
from observare_llm import ObservareChat
from observare_config import SafetyPolicy
from langchain_openai import ChatOpenAI

safe_llm = ObservareChat(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    policy=SafetyPolicy.BALANCED,
    api_key="your-observare-api-key"
)
```

### **3. Production Deployment**

```python
# Production configuration
safe_llm = ObservareChat(
    llm=ChatOpenAI(model="gpt-4"),
    policy=SafetyPolicy.STRICT,
    api_key=os.getenv("OBSERVARE_API_KEY"),
    api_endpoint=os.getenv("OBSERVARE_ENDPOINT"),
    fail_safe=True  # Continue operation even if safety checks fail
)
```

## 📋 Requirements

- **Python 3.8+**
- **LangChain 0.1.0+**
- **LangChain OpenAI** (for OpenAI model support)
- **Requests** (for API communication)

## 🆘 Support

- **Documentation**: [docs.observare.ai](https://docs.observare.ai)
- **API Reference**: [api.observare.ai](https://api.observare.ai)
- **Enterprise Support**: enterprise@observare.ai
- **Community**: [github.com/observare/sdk](https://github.com/observare/sdk)

---

**Ready to secure your AI applications?** Start with our [Quick Start Guide](https://docs.observare.ai/quickstart) or contact our team for enterprise deployment assistance.