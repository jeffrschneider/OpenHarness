# Open Harness Multi-Adapter Demo

A demonstration of the unified Open Harness API across multiple AI agent harnesses.

## Overview

This demo showcases how Open Harness provides a single, consistent API for interacting with different AI agent frameworks:

| Adapter | Harness | Key Features |
|---------|---------|--------------|
| `anthropic` | Anthropic Agent SDK | Tool use, streaming, extended thinking |
| `letta` | Letta | Memory blocks, agent lifecycle, persistence |
| `goose` | Goose | MCP integration, 25+ models, sessions |
| `deepagent` | LangChain Deep Agent | Todo planning, subagents, file operations |

## Installation

```bash
# Install the demo with all adapters
pip install -e ".[all]"

# Or install individual adapters
pip install openharness-letta openharness-goose openharness-deepagent
```

## Prerequisites

Each adapter has its own prerequisites:

### Anthropic Agent SDK
```bash
export ANTHROPIC_API_KEY=your-api-key
```

### Letta
```bash
# Start Letta server
letta server
```

### Goose
```bash
# Start Goose server
goose-server
```

### Deep Agent
```bash
export ANTHROPIC_API_KEY=your-api-key  # or other provider
```

## Usage

### List Available Adapters

```bash
harness-demo list
```

Shows which adapters are installed and ready to use.

### View Adapter Capabilities

```bash
harness-demo capabilities letta
harness-demo capabilities goose
harness-demo capabilities deepagent
```

### Run a Single Message

```bash
# Stream response (default)
harness-demo run letta -m "What is the weather like?"

# Without streaming
harness-demo run goose -m "Hello!" --no-stream
```

### Interactive Chat

```bash
harness-demo chat letta
harness-demo chat deepagent
```

### Compare Adapters

Send the same prompt to multiple adapters and compare responses:

```bash
# Compare all available adapters
harness-demo compare -m "Explain recursion in one sentence"

# Compare specific adapters
harness-demo compare -m "Hello" -a letta -a goose
```

## Code Example

```python
from demo.adapters import create_adapter, get_available_adapters
from openharness import ExecuteRequest

# See what's available
available = get_available_adapters()
print(f"Available: {available}")

# Create an adapter
adapter = create_adapter("letta")

# Check capabilities
print(f"Supports streaming: {adapter.capabilities.streaming}")
print(f"Supports memory: {adapter.capabilities.memory}")

# Execute a request
import asyncio

async def main():
    # Streaming
    async for event in adapter.execute_stream(ExecuteRequest(message="Hello!")):
        if event.type == "text":
            print(event.content, end="")

    # Synchronous
    result = await adapter.execute(ExecuteRequest(message="What is 2+2?"))
    print(result.content)

asyncio.run(main())
```

## The Open Harness Advantage

The key benefit of Open Harness is **write once, run anywhere**:

```python
# Same code works with any adapter
async def process_request(adapter, message: str):
    """Works with Anthropic, Letta, Goose, or Deep Agent."""
    async for event in adapter.execute_stream(ExecuteRequest(message=message)):
        if event.type == "text":
            yield event.content

# Switch adapters without changing application code
adapter = create_adapter("letta")      # Memory-first
adapter = create_adapter("goose")      # MCP-first
adapter = create_adapter("deepagent")  # Planning-first
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Application                      │
├─────────────────────────────────────────────────────────┤
│                   Open Harness API                       │
│  ExecuteRequest → HarnessAdapter → ExecutionEvent       │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Anthropic│  Letta   │  Goose   │  Deep    │   Your      │
│  Agent   │ Adapter  │ Adapter  │  Agent   │  Adapter    │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│ Claude   │  Letta   │  Goose   │ LangChain│   ???       │
│   API    │  Server  │  Server  │   SDK    │             │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
```

## License

MIT
