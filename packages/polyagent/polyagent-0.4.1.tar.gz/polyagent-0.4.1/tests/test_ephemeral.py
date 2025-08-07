#!/usr/bin/env python3
"""Test ephemeral mode for OpenSourceAgent"""

from polycli.agent import OpenSourceAgent

# Test 1: Ephemeral with no-tools
print("=== Test 1: Ephemeral with no-tools ===")
agent = OpenSourceAgent(debug=True)

# Non-ephemeral: should be saved
result = agent.run("Remember the number 99", model="gpt-4o", cli="no-tools")
print(f"Response: {result['message']['content']}")
print(f"Messages in memory: {len(agent.messages)}")

# Ephemeral: should NOT be saved
result = agent.run("What is 2+2?", model="gpt-4o", cli="no-tools", ephemeral=True)
print(f"Ephemeral response: {result['message']['content']}")
print(f"Messages in memory (should be same): {len(agent.messages)}")

# Check if memory was preserved
result = agent.run("What number did I ask you to remember?", model="gpt-4o", cli="no-tools")
print(f"Memory check: {result['message']['content']}")
print()

# Test 2: Ephemeral with qwen-code
print("=== Test 2: Ephemeral with qwen-code ===")
agent2 = OpenSourceAgent(debug=True)

result = agent2.run("Remember the color blue", model="gpt-4o", cli="qwen-code")
print(f"Messages before ephemeral: {len(agent2.messages)}")

result = agent2.run("What is the capital of France?", model="gpt-4o", cli="qwen-code", ephemeral=True)
print(f"Messages after ephemeral (should be same): {len(agent2.messages)}")
print()

# Test 3: Ephemeral with mini-swe
print("=== Test 3: Ephemeral with mini-swe ===")
agent3 = OpenSourceAgent(debug=True)

result = agent3.run("Remember my name is Alice", model="gpt-4o", cli="mini-swe")
print(f"Messages before ephemeral: {len(agent3.messages)}")

result = agent3.run("List current directory", model="gpt-4o", cli="mini-swe", ephemeral=True)
print(f"Messages after ephemeral (should be same): {len(agent3.messages)}")

# Verify memory
result = agent3.run("What is my name?", model="gpt-4o", cli="mini-swe")
print(f"Memory check: Should remember Alice")