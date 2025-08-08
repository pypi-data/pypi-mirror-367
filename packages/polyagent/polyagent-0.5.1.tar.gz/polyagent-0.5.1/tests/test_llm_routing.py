#!/usr/bin/env python3
"""Example: Using polyagent with multiple LLM providers"""

from pathlib import Path
from polycli import Agent

# Define where to save the conversation state
agent_state_file = Path.home() / ".polyagent-llm-routing.jsonl"

# Initialize the agent with a default system prompt
print(f"Initializing agent. State will be persisted to: {agent_state_file}")
my_agent = Agent(
    debug=True,
    system_prompt="You are a helpful coding assistant specializing in Python development."
)

# Load previous state if it exists
if agent_state_file.exists():
    print("Loading previous state...")
    my_agent.load_state(agent_state_file)

# Example: Regular (persistent) LLM call
print("\n>>> Regular GLM call (will be saved)")
response = my_agent.run("What is recursion?", model="glm-4.5")
if response:
    print(f"GLM says: {response.content[:100]}...")

# Example: Ephemeral LLM call (won't be saved)
print("\n>>> Ephemeral GLM call (won't be saved)")
response = my_agent.run(
    "Tell me a joke about programming", 
    model="glm-4.5",
    ephemeral=True
)
if response:
    print(f"GLM says: {response.content}")

# Check memory - the joke won't be there
print(f"\nMessages size before save: {len(my_agent.messages)}")

# Save state
my_agent.save_state(agent_state_file)
print(f"State saved to: {agent_state_file}")