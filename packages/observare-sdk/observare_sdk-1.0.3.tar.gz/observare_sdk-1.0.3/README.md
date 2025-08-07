# Observare SDK

**Zero-config telemetry and safety for LangChain agents**

Add comprehensive observability, PII redaction, and hallucination detection to your LangChain applications with minimal setup.

## 🚀 Quick Start

### Installation
```bash
pip install observare-sdk
```

### Basic Telemetry
```python
from observare_sdk import AutoTelemetryHandler
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor

# Add telemetry to any LangChain agent
handler = AutoTelemetryHandler(api_key="your-api-key")
executor = AgentExecutor(
    agent=agent, 
    tools=tools,
    callbacks=[handler]  # One line integration!
)

# All agent activity is now tracked automatically
result = executor.invoke({"input": "What's the weather?"})
```

### Safety Features
```python
from observare_sdk import ObservareChat, SafetyPolicy
from langchain_openai import ChatOpenAI

# Wrap any LLM with safety features
safe_llm = ObservareChat(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    api_key="your-api-key"
)

# Apply safety policy
safe_llm.apply_policy(SafetyPolicy.BALANCED)

# PII is automatically redacted, hallucinations detected
response = safe_llm.invoke([HumanMessage(content="My SSN is 123-45-6789")])
# → "My SSN is [SSN_REDACTED]"
```

## ✨ Features

### 📊 **Zero-Config Telemetry**
- **Agent lifecycle tracking** - Start, completion, errors
- **Tool execution monitoring** - Performance and usage
- **LLM call metrics** - Token usage, costs, latency  
- **Automatic correlation** - Link related events together

### 🛡️ **Enterprise Safety**
- **PII Redaction** - Emails, phones, SSNs, credit cards
- **Hallucination Detection** - Multi-method AI safety validation
- **Configurable Policies** - STRICT, BALANCED, PERMISSIVE
- **Real-time Monitoring** - Live safety alerts

### 🔧 **Production Ready**
- **Fail-safe operation** - Never breaks your app
- **High performance** - Minimal latency overhead
- **Comprehensive logging** - Full audit trails
- **Easy integration** - Works with existing code

## ⚙️ Configuration

### Environment Variables
```bash
export OBSERVARE_API_KEY="your-api-key"
```

### Safety Policies
```python
# Maximum security
safe_llm.apply_policy(SafetyPolicy.STRICT)

# Balanced (default) 
safe_llm.apply_policy(SafetyPolicy.BALANCED)

# Minimal restrictions
safe_llm.apply_policy(SafetyPolicy.PERMISSIVE)
```

### Debug Mode
```python
# See API errors during development
handler = AutoTelemetryHandler(api_key="your-key", debug_mode=True)
```

## 🆘 Support

- **Documentation**: [docs.observare.ai](https://docs.observare.ai)
- **Issues**: [github.com/observare/sdk/issues](https://github.com/observare/sdk/issues)
- **Email**: support@observare.ai

## 📄 License

Proprietary - See LICENSE file for details.

---

**Get started in 2 minutes:** Add one line to your LangChain app and gain complete visibility into your AI systems.