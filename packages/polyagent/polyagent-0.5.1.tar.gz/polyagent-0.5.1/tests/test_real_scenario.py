#!/usr/bin/env python3
"""
REAL-WORLD TEST: Claude does work, then grok evaluates it
Using only public agent.run() API like actual users would
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.polycli.agent import ClaudeAgent

def test_real_scenario():
    """Real-world test: Claude does work, then grok evaluates using only public API"""
    
    print(f"🌍 REAL-WORLD SCENARIO TEST")
    print("Claude Code does work → grok evaluates using only public agent.run() API")
    print("=" * 70)
    
    try:
        # Step 1: Claude Code Agent does actual work
        print("\n1️⃣  CLAUDE CODE: Doing actual work...")
        claude_agent = ClaudeAgent(debug=False, cwd="/tmp")
        
        # Real task that requires tool use
        claude_task = "Create a Python script called calculator.py with add(a,b) and multiply(a,b) functions. Then test it by reading the file and show me the content."
        print(f"📋 Claude task: {claude_task}")
        
        claude_result = claude_agent.run(claude_task)
        print(f"✅ Claude completed: {claude_result.get('result', 'No result')[:100]}...")
        
        # Verify actual file creation
        test_file = "/tmp/calculator.py"
        file_exists = os.path.exists(test_file)
        print(f"📄 File exists: {file_exists}")
        if file_exists:
            with open(test_file, 'r') as f:
                content = f.read()
                print(f"📄 File size: {len(content)} chars")
                print(f"   Preview: {content[:80]}...")
        
        print(f"💾 Claude session: {len(claude_agent.memory)} messages in memory")
        
        # Step 2: grok Agent evaluates Claude's work (using public API only)
        print(f"\n2️⃣  GROK EVALUATION: Assessing Claude's work...")
        grok_agent = ClaudeAgent(debug=False, cwd="/tmp") 
        
        # Give grok the SAME session history that Claude has
        grok_agent.memory = claude_agent.memory
        
        # grok evaluates using only public API
        evaluation_questions = [
            "What specific tools did Claude use to complete the task? Be detailed.",
            "What files did Claude create? Include exact paths and names.",
            "Can you see the step-by-step process of what Claude actually did?",
            "What confirmations or results did Claude receive from the tools?"
        ]
        
        grok_responses = []
        
        for i, question in enumerate(evaluation_questions):
            print(f"\n❓ Question {i+1}: {question}")
            
            # grok uses public API to evaluate
            grok_result = grok_agent.run(question, model="gpt-4o", ephemeral=True)
            response = grok_result.get("result", "No response")
            grok_responses.append(response)
            
            print(f"🤖 grok: {response}")
            
            # Analysis of what grok can see
            resp_lower = response.lower()
            sees_tools = any(tool in resp_lower for tool in ['write', 'read', 'tool use', '[tool use]'])
            sees_files = 'calculator.py' in resp_lower or '.py' in resp_lower
            sees_results = any(word in resp_lower for word in ['successfully', 'created', 'confirmed', 'result'])
            sees_process = any(word in resp_lower for word in ['step', 'first', 'then', 'after'])
            
            visibility = []
            if sees_tools: visibility.append("✅ Tools")
            if sees_files: visibility.append("✅ Files") 
            if sees_results: visibility.append("✅ Results")
            if sees_process: visibility.append("✅ Process")
            
            print(f"📊 grok can see: {', '.join(visibility) if visibility else '❌ Limited info'}")
        
        # Step 3: Overall assessment
        print(f"\n3️⃣  ASSESSMENT:")
        print("=" * 70)
        
        all_responses = ' '.join(grok_responses).lower()
        
        key_indicators = {
            'Sees tool usage': 'tool' in all_responses or 'write' in all_responses or 'read' in all_responses,
            'Sees file creation': 'calculator.py' in all_responses or 'created' in all_responses,
            'Sees tool results': 'successfully' in all_responses or 'confirmed' in all_responses,
            'Sees file content': 'add' in all_responses or 'multiply' in all_responses or 'function' in all_responses,
            'Sees step-by-step process': ('first' in all_responses or 'then' in all_responses) and 'step' in all_responses
        }
        
        success_count = sum(key_indicators.values())
        
        print(f"📈 EVALUATION SUCCESS METRICS:")
        for indicator, success in key_indicators.items():
            status = "✅" if success else "❌"
            print(f"   {status} {indicator}")
        
        success_rate = success_count / len(key_indicators)
        print(f"\n🎯 Overall Success Rate: {success_rate:.1%} ({success_count}/{len(key_indicators)})")
        
        if success_rate >= 0.8:
            print("🎉 EXCELLENT: grok can see Claude's actual work!")
        elif success_rate >= 0.6:
            print("✅ GOOD: grok has decent visibility")
        else:
            print("❌ POOR: grok has limited visibility")
        
        return success_rate >= 0.6
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
        
    finally:
        # Cleanup test file
        test_file = "/tmp/calculator.py"
        if os.path.exists(test_file):
            print(f"\n🧹 Cleaning up: {test_file}")
            os.remove(test_file)

if __name__ == "__main__":
    success = test_real_scenario()
    print(f"\n{'='*70}")
    if success:
        print("🎉 SUCCESS: Real-world test passed!")
        print("   grok can see Claude Code's actual work using public API!")
    else:
        print("❌ FAILED: grok has limited visibility into Claude's work")
        print("   This suggests the extraction fix may need improvement")