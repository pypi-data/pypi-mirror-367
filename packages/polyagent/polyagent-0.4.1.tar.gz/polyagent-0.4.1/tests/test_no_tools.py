#!/usr/bin/env python3
"""Test no-tools mode for OpenSourceAgent"""

from polycli.agent import OpenSourceAgent
from pydantic import BaseModel, Field

# Test 1: Basic no-tools conversation
print("=== Test 1: Basic no-tools conversation ===")
agent = OpenSourceAgent(debug=True)

result = agent.run("What is 2+2?", model="gpt-4o", cli="no-tools")
print(f"Result: {result}")
if result['status'] == 'success':
    print(f"Response: {result['message']['content']}")
print()

# Test 2: Conversation memory
print("=== Test 2: Conversation memory ===")
result = agent.run("What did I just ask you?", model="gpt-4o", cli="no-tools")
if result['status'] == 'success':
    print(f"Response: {result['message']['content']}")
print()

# Test 3: Error handling
print("=== Test 3: Error handling ===")
result = agent.run("Test", model="invalid-model", cli="no-tools")
print(f"Error result: {result}")
print()

# Test 4: Structured output
print("=== Test 4: Structured output ===")

class MathResult(BaseModel):
    calculation: str = Field(description="The calculation performed")
    result: int = Field(description="The result of the calculation")

agent2 = OpenSourceAgent(debug=True)
result = agent2.run(
    "Calculate 5 * 8",
    model="gpt-4o", 
    cli="no-tools",
    schema_cls=MathResult
)
print(f"Structured result: {result}")
if result['status'] == 'success':
    print(f"Result data: {result['result']}")
    print(f"Type: {result['type']}")
    print(f"Schema: {result['schema']}")

# Test 5: Switch to glm model
print("\n=== Test 5: GLM model test ===")
result = agent2.run("What is the capital of France?", model="glm-4.5", cli="no-tools")
if result['status'] == 'success':
    print(f"GLM Response: {result['message']['content']}")