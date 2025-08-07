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
response = agent.run("What is 2+2?")
print(response['result'])  # 4

# Multi-model support via models.json
response = agent.run("Explain recursion", model="gpt-4o")

# Structured outputs with Pydantic
from pydantic import BaseModel, Field

class MathResult(BaseModel):
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Step-by-step explanation")

response = agent.run("What is 15+27?", model="gpt-4o", schema_cls=MathResult)
print(response['result']['answer'])  # 42

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