#!/usr/bin/env python3
"""Test script for get_status functionality"""

from polycli.agent import OpenSourceAgent

# Create an agent
agent = OpenSourceAgent(debug=True)

# Do some work to create history
print("=== Doing some work to create conversation history ===")

agent.run("What is 2+2?", model="gpt-4o")
agent.run("List the files in the current directory", model="gpt-4o")
agent.run("What's the weather like?", model="gpt-4o")

print(f"\nAgent has {len(agent.messages)} messages in history")

# Test the status report
print("\n=== Getting status report ===")
status = agent.get_status(n_exchanges=2)
print("Status Report:")
print(status)

print("\n=== Testing with different parameters ===")
status2 = agent.get_status(n_exchanges=1, model="gpt-4o")
print("Status Report (1 exchange, gpt-4o):")
print(status2)
