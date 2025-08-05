# MultiAgents Framework

**🚀 LLM-Powered Multi-Agent Orchestration Framework** 

A hybrid event-driven orchestration framework designed specifically for **LLM agents and AI developers**. Build intelligent, conversational, and autonomous multi-agent systems with built-in DSPy integration, real-time collaboration, and production-ready tooling.

⚠️ **Experimental**: This framework is in active development. APIs may change between versions.

## 🎯 Built for LLM Agents

**Perfect for AI developers building:**
- 🤖 **Conversational AI Systems** - Multi-agent chat with intelligent routing
- 🔍 **Research Assistants** - Collaborative research with specialized agents  
- 🧠 **LLM-Driven Workflows** - Dynamic orchestration with real-time decisions
- 🛠️ **Tool-Using Agents** - Multi-modal agents with external integrations
- 📊 **Data Analysis Pipelines** - Intelligent data processing with LLM insights

## ✨ Key Features

- **🧠 LLM-First Design**: Built-in DSPy integration with Gemini, GPT, Claude support
- **💬 Conversational AI**: Intelligent routing between conversation and task execution
- **🔧 Tool Integration**: Easy integration with web search, calculators, APIs
- **🎭 Multi-Agent Collaboration**: Specialized agents working together seamlessly
- **📊 Production Monitoring**: Complete observability designed for LLM workflows
- **🔄 Event-Driven**: Scalable async communication perfect for AI workloads
- **🛡️ Fault Tolerance**: Built-in compensation and rollback for complex workflows

## Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Redis Server** (for event bus and state storage)

Start Redis:
```bash
# macOS with Homebrew
brew services start redis

# Ubuntu/Debian
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### Installation

**Install from PyPI (Recommended):**
```bash
# Install the framework
pip install multiagents-framework

# Or with uv (faster)
uv add multiagents-framework
```

**Development Installation:**
```bash
1. Clone the repository:
git clone https://github.com/xavierau/multiagents.git
cd multiagents

2. Create virtual environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

3. Install in development mode:
pip install -e .
```

**Verify Installation:**
```bash
multiagents --version
multiagents --help
```

### 🚀 Quick Start Examples

**Run Interactive Examples:**
```bash
# Interactive example menu
python run_examples.py

# Or run specific examples:
multiagents --examples
```

**Available Examples:**
1. **💬 Smart Research Assistant** - LLM-powered conversational research with web search
2. **🤖 Interactive Chatbot** - Multi-personality conversational AI with DSPy
3. **🛒 E-commerce Workflow** - Complete order processing with compensations  
4. **📊 Monitoring Demo** - Production-ready observability features

**Try the Smart Research Assistant:**
```bash
# Navigate to example (if installed from source)
cd examples/smart_research_assistant
python cli.py

# Ask questions like:
# "What are the latest trends in renewable energy?"
# "Calculate compound interest on $5000 at 8% for 3 years"
# "Hi!" (conversational mode)
```

## Framework Overview

### Core Components

1. **Orchestrator**: Manages workflow state and coordinates activities
2. **Workers**: Stateless task executors created with simple decorators
3. **Event Bus**: Decoupled communication layer (Redis Pub/Sub)
4. **Monitoring**: Comprehensive observability and debugging

### Basic Usage

```python
from multiagents import (
    Orchestrator, WorkflowBuilder, WorkerManager, worker
)
from multiagents.event_bus.redis_bus import RedisEventBus

# Define workers
@worker("process_data")
async def process_data_worker(context):
    data = context["input_data"]
    # Process the data
    return {"processed": data, "timestamp": "2024-01-01T00:00:00Z"}

# Create workflow
workflow = (WorkflowBuilder("data_processing")
    .add_step("process", "process_data")
    .build())

# Set up framework
event_bus = RedisEventBus()
worker_manager = WorkerManager(event_bus)
orchestrator = Orchestrator(workflow, event_bus)

# Register worker and start
worker_manager.register(process_data_worker)
await event_bus.start()
await worker_manager.start()
await orchestrator.start()

# Execute workflow
transaction_id = await orchestrator.execute_workflow(
    "data_processing",
    {"input_data": "example data"}
)
```

### Monitoring & Observability

The framework includes comprehensive monitoring:

```python
from multiagents.monitoring import MonitoringConfig, EventMonitor, WorkerMonitor

# Setup monitoring
config = MonitoringConfig()
logger = config.create_logger()
event_monitor = EventMonitor(logger=logger)
worker_monitor = WorkerMonitor(logger=logger)

# Integrate with framework
event_bus = RedisEventBus(event_monitor=event_monitor, logger=logger)
worker_manager = WorkerManager(event_bus, worker_monitor=worker_monitor, logger=logger)
```

**Monitoring Features:**
- **Event Lifecycle Tracking**: Complete event journey from dispatch to completion
- **Worker Performance**: Success rates, processing times, health monitoring
- **Structured Logging**: JSON logs with automatic rotation
- **Error Tracking**: Detailed error context and failure patterns
- **Real-time Metrics**: Performance dashboards and alerting

**Configuration (monitoring.yaml):**
```yaml
logging:
  default_logger: "file"
  level: "INFO"
  file_path: "./logs/multiagents.log"

event_monitoring:
  enabled: true
  trace_retention_hours: 24

worker_monitoring:
  enabled: true
  health_check_interval_seconds: 30
```

## 📋 Example Applications

### 1. 💬 Smart Research Assistant  
**LLM-powered conversational research system**
- Intelligent routing between conversation and research
- Multi-agent collaboration (Coordinator, Researcher, Analyst, Formatter)
- Real Google Custom Search API integration
- Gemini LLM with DSPy optimization
- Production-ready configuration system

### 2. 🤖 Interactive Chatbot
**Multi-personality conversational AI**
- DSPy-powered natural conversations
- Configurable personalities and responses  
- Context-aware conversation management
- Real-time interaction with memory

### 3. 🛒 E-commerce Order Processing
**Production-ready order workflow**
- Multi-step order validation and processing
- Intelligent inventory and payment handling
- Automatic compensation and rollback
- LLM-generated confirmations and notifications

### 4. 📊 Production Monitoring
**Enterprise-grade observability**
- Real-time agent performance monitoring
- Event lifecycle tracking and debugging
- Structured logging with automatic rotation
- Error pattern analysis and alerting

## Development

### Project Structure
```
multiagents/
├── orchestrator/          # Workflow orchestration
├── worker_sdk/           # Worker development SDK
├── event_bus/            # Event bus implementations
├── monitoring/           # Observability system
├── core/                 # Core utilities
└── examples/             # Example implementations
```

### Key Design Principles
- **SOLID Principles**: Clean, maintainable architecture
- **Event-Driven**: Fully decoupled communication
- **Fault Tolerance**: Built-in compensation and rollback
- **Observability**: Comprehensive monitoring and debugging
- **Developer Experience**: Simple, intuitive APIs

### Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run examples
python run_examples.py

# Run tests (when available)
pytest

# Format code
black .
ruff check --fix .

# Type checking
mypy multiagents/
```

## Architecture

The framework follows a hybrid orchestration/choreography pattern:

- **Orchestration**: Centralized workflow management with state machine
- **Choreography**: Decoupled event-driven communication between components
- **Saga Pattern**: Distributed transaction management with compensations
- **Event Sourcing**: Complete audit trail of all activities

This approach provides the benefits of both patterns:
- **Centralized Logic**: Easy to understand and debug workflows
- **Decoupled Components**: Scalable and resilient architecture
- **Fault Tolerance**: Automatic compensation and recovery
- **Observability**: Complete visibility into system behavior

## Contributing

1. Follow SOLID principles and clean code practices
2. Add comprehensive monitoring to all components
3. Include tests for new functionality
4. Update documentation and examples

## 🔗 LLM Agent Integration

**Claude Code Integration:**
This framework includes specialized Claude Code subagents for enhanced development:

```bash
# Auto-install Claude subagent (when using Claude Code)
multiagents install-agent claude-code

# Or manually copy the agent
cp multiagents/agents/multiagents.md ~/.claude/agents/
```

**llms.txt Support:**
This project includes `llms.txt` for LLM consumption with documentation pointers to GitHub for always up-to-date information.

## 🌐 Community & Support

- **GitHub**: [https://github.com/xavierau/multiagents](https://github.com/xavierau/multiagents)
- **PyPI**: [https://pypi.org/project/multiagents-framework/](https://pypi.org/project/multiagents-framework/)
- **Issues**: [Report bugs and request features](https://github.com/xavierau/multiagents/issues)
- **Discussions**: [Community discussions and help](https://github.com/xavierau/multiagents/discussions)

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the LLM agent community**  
*Making multi-agent AI systems accessible, reliable, and production-ready.*