# PolyCLI

A unified interface for stateful conversations with CLI-based AI agents.

## Installation

```bash
pip install polyagent
```

### CLI Tools Setup

**Claude Code**: Follow official Anthropic installation

**Qwen Code**: 
```bash
# Remove original version if installed
npm uninstall -g @qwen-code/qwen-code

# Install special version with --save/--resume support
npm install -g @lexicalmathical/qwen-code@0.0.4-resume.1
```

**Mini-SWE Agent**: 
```bash
pip install mini-swe-agent
```

## Quick Start

```python
from polycli import Agent

# Basic usage
agent = Agent()
result = agent.run("What is 2+2?")
print(result.content)  # 4
print(f"Success: {result.is_success}")

# Multi-model support via models.json
result = agent.run("Explain recursion", model="gpt-4o")
if result:  # Check success
    print(result.content)

# Access Claude-specific metadata
if result.get_claude_cost():
    print(f"Cost: ${result.get_claude_cost()}")

# Structured outputs with Pydantic
from pydantic import BaseModel, Field

class MathResult(BaseModel):
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Step-by-step explanation")

result = agent.run("What is 15+27?", model="gpt-4o", schema_cls=MathResult)
if result.has_data():  # Check for structured data
    print(result.data['answer'])  # 42
    print(result.content)  # Formatted JSON string

# System prompts
agent_with_prompt = Agent(system_prompt="You are a helpful Python tutor")
result = agent_with_prompt.run("Explain list comprehensions")

# Override system prompt for specific calls
result = agent.run(
    "Translate to French", 
    system_prompt="You are a French translator. Respond only in French."
)

# State persistence
agent.save_state("conversation.jsonl")
agent.load_state("conversation.jsonl")
```

## Configuration

Create `models.json` in project root:
```json
{
  "models": {
    "gpt-4o": {
      "endpoint": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "model": "gpt-4o"
    }
  }
}
```

## Architecture

### Agents

**ClaudeAgent** (default)
- No model specified → Claude CLI with full tool access
- Model specified → Any LLM via models.json (single round, no tools)

**OpenSourceAgent**
- `cli="qwen-code"` → Production-ready for all tasks including code (default)
- `cli="mini-swe"` → Experimental, lightweight, suitable for testing
- `cli="no-tools"` → Direct LLM API calls without code execution (supports structured output)

### Tech Stack
- **LLM Client**: Instructor + OpenAI client (no litellm)
- **Message Formats**: Auto-conversion between Claude (JSONL), Mini-SWE (role/content), Qwen (role/parts)
- **State**: JSON/JSONL with seamless format switching

## RunResult Interface

All agent `.run()` calls return a `RunResult` object with a clean, unified interface:

```python
from polycli.agent import OpenSourceAgent

agent = OpenSourceAgent()
result = agent.run("Calculate 5 * 8", model="gpt-4o", cli="no-tools", schema_cls=MathResult)

# Basic usage
print(result.content)        # Always a string (for display)
print(result.is_success)     # Boolean success status
if not result:               # Pythonic error checking
    print(result.error_message)

# Structured data access
if result.has_data():        # Check for structured response
    calc = result.data['calculation']  # Raw dictionary access
    answer = result.data['result']

# Metadata access
print(result.get_claude_cost())    # Cost for Claude calls
print(result.get_claude_tokens())  # Token usage details
print(result.get_session_id())     # Session tracking

# Status reports
status = agent.get_status(n_exchanges=3)  # Summarize recent work
if status:
    print(status.content)  # AI-generated status report
```

## Advanced Usage

### OpenSourceAgent - Toggle CLIs
```python
from polycli.agent import OpenSourceAgent

agent = OpenSourceAgent()

# Start with qwen-code
agent.run("Remember the number 42", model="gpt-4o", cli="qwen-code")

# Switch to mini-swe (maintains conversation)
agent.run("Create a file with that number", model="gpt-4o", cli="mini-swe")

# Back to qwen-code
agent.run("What file did we create?", model="gpt-4o", cli="qwen-code")

# Use no-tools mode for simple Q&A
agent.run("What's the meaning of that number?", model="gpt-4o", cli="no-tools")
```

## Requirements
- Python 3.8+
- One or more CLI tools installed
- models.json for LLM configuration

## Roadmap
- [x] Mini SWE-agent Integration
- [x] Qwen Code Integration
- [ ] Native Multi-agent Orchestration

---

*Simple. Stateful. Universal.*