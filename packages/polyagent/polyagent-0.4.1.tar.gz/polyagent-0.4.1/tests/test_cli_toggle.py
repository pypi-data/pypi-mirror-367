from polycli.agent import OpenSourceAgent

# Create agent
agent = OpenSourceAgent(debug=True)

# Test 1: Start with qwen-code using gpt-4o
print("=== Test 1: qwen-code with gpt-4o ===")
result = agent.run("Remember this number: 42", model="gpt-4o", cli="qwen-code")
print(f"Response: {result['message']['content']}\n")

# Test 2: Switch to mini-swe with glm-4.5
print("=== Test 2: mini-swe with glm-4.5 ===")
result = agent.run("What number did I ask you to remember?", model="glm-4.5", cli="mini-swe")
print(f"Response: {result['message']['content']}\n")

# Test 3: Back to qwen-code with glm-4.5
print("=== Test 3: qwen-code with glm-4.5 ===")
result = agent.run("Add 8 to the number I told you", model="glm-4.5", cli="qwen-code")
print(f"Response: {result['message']['content']}\n")

# Test 4: Switch to mini-swe with gpt-4o
print("=== Test 4: mini-swe with gpt-4o ===")
result = agent.run("What's our conversation been about so far?", model="gpt-4o", cli="mini-swe")
print(f"Response: {result['message']['content']}\n")

# Test 5: Final check with qwen-code
print("=== Test 5: qwen-code with gpt-4o ===")
result = agent.run("List all the numbers mentioned in our conversation", model="gpt-4o", cli="qwen-code")
print(f"Response: {result['message']['content']}\n")

# Show final message count
print(f"Total messages in memory: {len(agent.messages)}")