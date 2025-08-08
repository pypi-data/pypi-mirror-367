#!/usr/bin/env python3
"""Minimal pattern-based orchestration - the essence"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from src.polycli.agent import OpenSourceAgent

# Pattern = list of (agent_id, prompt) pairs to run in parallel
patterns = {
    "analyze": [
        ("agent1", "List all Python files in current directory"),
        ("agent2", "What's the current time?"),
    ],
    "summarize": [
        ("agent1", "Count the number of files you found"),
        ("agent2", "What day is it?"),
    ],
}

# Persistent agents
agents = {
    "agent1": OpenSourceAgent(),
    "agent2": OpenSourceAgent(),
}

def run_pattern(pattern_name):
    """Execute a pattern - all agents run in parallel"""
    print(f"\n▶ Pattern: {pattern_name}")
    tasks = patterns[pattern_name]
    
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {
            executor.submit(agents[aid].run, prompt): aid 
            for aid, prompt in tasks
        }
        
        for future in as_completed(futures):
            agent_id = futures[future]
            result = future.result()
            print(f"  {agent_id}: Done")

# Run a flow
flow = ["analyze", "summarize", "analyze"]
for pattern_name in flow:
    run_pattern(pattern_name)

print(f"\nAgent1 memory has {len(agents['agent1'].messages)} messages")
print(f"Agent2 memory has {len(agents['agent2'].messages)} messages")