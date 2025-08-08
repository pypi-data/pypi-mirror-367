#!/usr/bin/env python3
"""
A reusable Python module for a stateful AI agent that interacts with the Claude CLI
or other LLMs via configurable endpoints.

This version includes:
- Model configuration via models.json file
- Fake user messages that append to existing ones
- Routing to different models via unified API
- System prompt support (default and per-run)
- Auto-skip permissions for Claude Code
- Ephemeral messages for LLM runs (not added to messages)
"""

import json
import subprocess
import os
import sys
from pathlib import Path
import shutil
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Type, Callable
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from .utils.serializers import default_json_serializer, json_list_serializer
from .utils.llm_client import get_llm_client
import copy

# Load environment variables from .env file
load_dotenv()

from abc import ABC, abstractmethod
from .adapters import RunResult

def Agent(*args, **kwargs):
    return ClaudeAgent(*args, **kwargs)

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    @abstractmethod
    def run(self, prompt: str, **kwargs):
        """Execute a prompt and return the result."""
        pass
    
    def save_state(self, file_path: str):
        """Saves the conversation history to a file."""
        raise NotImplementedError("This agent does not support saving state.")

    def load_state(self, file_path: str):
        """Loads the conversation history from a file."""
        raise NotImplementedError("This agent does not support loading state.")
    
    def get_status(self, n_exchanges: int = 3, model: str = "openai/gpt-oss-120b"):
        """
        Generate a status report of the agent's recent work.
        
        Args:
            n_exchanges: Number of recent user interactions to summarize.
            model: Model to use for generating the report.
        
        Returns:
            A structured status report.
        """
        prompt = f"""Analyze and summarize your work on the last {n_exchanges} user interactions (<5 sentences).

Structure your response as:
Analysis: [What types of tasks were worked on, any patterns or challenges encountered]
Key Outcomes: [What was accomplished, created, fixed, or discovered]
Current Status: [Any pending items, next steps, or relevant context]"""
        
        return self.run(prompt, model=model, ephemeral=True)

class OpenSourceAgent(BaseAgent):
    def __init__(self, debug=False, system_prompt=None, cwd=None) -> None:
        self.cwd = cwd
        self.messages = []
        self.system_prompt = system_prompt
        self.debug = debug
        # We separate system prompt and normal message, so the following is commented out
        # if system_prompt:
        #     self.messages.append({"role": "system", "content": system_prompt})
    
    def save_state(self, file_path: str):
        """Save conversation history to a JSON file in Qwen format"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to Qwen format before saving
        qwen_messages = self._convert_to_qwen_format(self.messages)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(qwen_messages, f, ensure_ascii=False, indent=2)
        
        if self.debug:
            print(f"[DEBUG] Saved {len(qwen_messages)} messages to {path}")
    
    def load_state(self, file_path: str):
        """Load conversation history from a JSON file"""
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                # Load directly - format will be converted on-demand when needed
                self.messages = json.load(f)
            
            if self.debug:
                print(f"[DEBUG] Loaded {len(self.messages)} messages from {path}")

    def _convert_to_qwen_format(self, messages):
        """Convert messages to Qwen format (role/parts structure)"""
        qwen_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                # Check if already in Qwen format
                if "parts" in msg:
                    qwen_messages.append(msg)
                else:
                    # Convert from simple format to Qwen format
                    role = msg.get("role", "user")
                    # Map assistant to model for Qwen
                    if role == "assistant":
                        role = "model"
                    content = msg.get("content", "")
                    qwen_messages.append({
                        "role": role,
                        "parts": [{"text": content}]
                    })
        return qwen_messages
    
    def _run_with_qwen(self, prompt: str, model: str, system_prompt: Optional[str] = None, ephemeral: bool = False):
        """Run using Qwen Code CLI"""
        import tempfile
        import hashlib
        
        # Get model config
        from .utils.model_config import get_model_config
        model_cfg = get_model_config().get_model(model)
        if not model_cfg:
            return RunResult({"status": "error", "message": f"Model '{model}' not found in configuration"})
        
        # Find qwen command
        qwen_cmd = shutil.which('qwen')
        if not qwen_cmd:
            return RunResult({"status": "error", "message": "Qwen command not found. Please ensure it's in your PATH."})
        
        # Get project root (current working directory)
        project_root = os.path.abspath(self.cwd if self.cwd else os.getcwd())
        
        # Calculate SHA256 hash of project root (same as Qwen does)
        project_hash = hashlib.sha256(project_root.encode()).hexdigest()
        
        # Create checkpoint file if we have history
        checkpoint_file = None
        effective_system_prompt = system_prompt or self.system_prompt
        
        # Prepare messages with system prompt injection
        messages_to_save = self.messages.copy() if self.messages else []
        
        # If we have a system prompt, inject it at the beginning
        system_prompt_injected = False
        if effective_system_prompt:
            # Create the system prompt exchange
            system_user_msg = {"role": "user", "parts": [{"text": f"[System]: {effective_system_prompt}"}]}
            system_model_msg = {"role": "model", "parts": [{"text": "I understand and will follow these instructions."}]}
            
            # Check if we need to update or inject
            if len(messages_to_save) >= 2:
                # Check if first two messages are our system prompt
                first_msg = messages_to_save[0]
                if (first_msg.get('role') == 'user' and 
                    first_msg.get('parts') and 
                    '[System]:' in str(first_msg.get('parts', [{}])[0].get('text', ''))):
                    # Replace existing system prompt
                    messages_to_save[0] = system_user_msg
                    messages_to_save[1] = system_model_msg
                else:
                    # Insert new system prompt at beginning
                    messages_to_save = [system_user_msg, system_model_msg] + messages_to_save
            else:
                # Insert new system prompt at beginning
                messages_to_save = [system_user_msg, system_model_msg] + messages_to_save
            system_prompt_injected = True
        
        # Convert and save if we have messages
        if messages_to_save:
            # Convert to Qwen format
            qwen_messages = self._convert_to_qwen_format(messages_to_save)
            
            # Save to temporary checkpoint file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(qwen_messages, f, ensure_ascii=False)
                checkpoint_file = f.name
        
        # Generate unique tag to avoid conflicts
        save_tag = f"polycli-{uuid.uuid4().hex[:8]}"
        
        try:
            # Build command with all CLI arguments
            cmd = [
                qwen_cmd,
                '--prompt', prompt,
                '--save', save_tag,
                '--yolo',
                '--openai-api-key', model_cfg['api_key'],
                '--openai-base-url', model_cfg['endpoint'],
                '--model', model_cfg['model']
            ]
            
            # Add resume if we have history
            if checkpoint_file:
                cmd.extend(['--resume', checkpoint_file])
            
            # Handle system prompt - removed since we'll handle it via history injection
            
            # Debug: print command
            if self.debug:
                print(f"[DEBUG] Running command: {' '.join(cmd)}")
            
            # Set environment variables as well (qwen seems to prioritize env vars)
            env = os.environ.copy()
            env['OPENAI_MODEL'] = model_cfg['model']
            env['OPENAI_API_KEY'] = model_cfg['api_key']
            env['OPENAI_BASE_URL'] = model_cfg['endpoint']
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root,
                env=env,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # Load the saved checkpoint from Qwen's location
                qwen_dir = Path.home() / ".qwen" / "tmp" / project_hash
                saved_checkpoint = qwen_dir / f"checkpoint-{save_tag}.json"
                
                if saved_checkpoint.exists():
                    # Load the conversation
                    with open(saved_checkpoint, 'r', encoding='utf-8') as f:
                        new_messages = json.load(f)
                    
                    # Clean up the saved checkpoint
                    saved_checkpoint.unlink()
                    
                    # Only update messages if not ephemeral
                    if not ephemeral:
                        # If we injected a system prompt earlier, remove it from the saved messages
                        # to avoid polluting the conversation history
                        if system_prompt_injected and len(new_messages) >= 2:
                            first_msg = new_messages[0]
                            if (first_msg.get('role') == 'user' and 
                                first_msg.get('parts') and 
                                '[System]:' in str(first_msg.get('parts', [{}])[0].get('text', ''))):
                                # Remove the injected system prompt messages
                                new_messages = new_messages[2:]
                        self.messages = new_messages
                    
                    # Extract last model response
                    last_response = ""
                    for msg in reversed(new_messages):
                        if msg.get("role") == "model":
                            parts = msg.get("parts", [])
                            if parts and isinstance(parts[0], dict) and "text" in parts[0]:
                                last_response = parts[0]["text"]
                                break
                    
                    if self.debug:
                        print(f"[DEBUG] Loaded conversation from {saved_checkpoint}")
                        if ephemeral:
                            print(f"[DEBUG] Ephemeral mode: conversation not saved to messages")
                        else:
                            print(f"[DEBUG] Total messages: {len(self.messages)}")
                    
                    return RunResult({
                        "status": "success",
                        "message": {"role": "assistant", "content": last_response},
                        "type": "assistant"
                    })
                else:
                    return RunResult({
                        "status": "error",
                        "message": f"Checkpoint file not found at {saved_checkpoint}"
                    })
            else:
                return RunResult({
                    "status": "error",
                    "message": f"Qwen command failed: {result.stderr}"
                })
                
        finally:
            # Clean up temporary checkpoint file
            if checkpoint_file and os.path.exists(checkpoint_file):
                os.unlink(checkpoint_file)
    
    def _run_no_tools(self, prompt: str, model: str, system_prompt: Optional[str] = None, 
                      schema_cls: Optional[Type[BaseModel]] = None, 
                      memory_serializer: Optional[Callable[[BaseModel], str]] = None,
                      ephemeral: bool = False):
        """Run using direct LLM API without tools (similar to Claude Code with non-Claude models)"""
        # Get LLM client
        try:
            llm_client, actual_model_name = get_llm_client(model)
        except Exception as e:
            return RunResult({"status": "error", "message": str(e)})
        
        if self.debug:
            print(f"[DEBUG] Running no-tools mode with model: {model}")
        
        # Prepare messages for the LLM
        messages = []
        
        # Use provided system prompt, fall back to default
        effective_system_prompt = system_prompt or self.system_prompt
        if effective_system_prompt:
            messages.append({"role": "system", "content": effective_system_prompt})
        
        # Convert existing messages to standard format and add to messages
        for msg in self.messages:
            if "parts" in msg:
                # Qwen format - extract text from parts
                role = msg.get("role", "user")
                if role == "model":
                    role = "assistant"
                text = ""
                for part in msg.get("parts", []):
                    if isinstance(part, dict) and "text" in part:
                        text += part["text"]
                if text:
                    messages.append({"role": role, "content": text})
            else:
                # Already in simple format
                messages.append(msg)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Make API call
        try:
            if schema_cls:
                # Structured response
                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Serialize for messages
                serializer = memory_serializer or default_json_serializer
                response_text = serializer(result)
                
                # Update messages only if not ephemeral
                if not ephemeral:
                    self.messages.append({"role": "user", "content": prompt})
                    self.messages.append({"role": "assistant", "content": f"[Structured response ({schema_cls.__name__})]\n{response_text}"})
                
                if self.debug:
                    if ephemeral:
                        print(f"[DEBUG] No-tools mode completed with structured output (ephemeral)")
                    else:
                        print(f"[DEBUG] No-tools mode completed with structured output. Total messages: {len(self.messages)}")
                
                return RunResult({
                    "status": "success",
                    "result": result.model_dump(),
                    "type": "structured",
                    "schema": schema_cls.__name__
                })
            else:
                # Plain text response - use Instructor with simple response model
                class LLMResponse(BaseModel):
                    response: str = Field(description="The AI assistant's response")
                
                result = llm_client.chat.completions.create(
                    response_model=LLMResponse,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Extract response content
                response_content = result.response
                
                # Update messages only if not ephemeral
                if not ephemeral:
                    self.messages.append({"role": "user", "content": prompt})
                    self.messages.append({"role": "assistant", "content": response_content})
                
                if self.debug:
                    if ephemeral:
                        print(f"[DEBUG] No-tools mode completed (ephemeral)")
                    else:
                        print(f"[DEBUG] No-tools mode completed. Total messages: {len(self.messages)}")
                
                return RunResult({
                    "status": "success",
                    "message": {"role": "assistant", "content": response_content},
                    "type": "assistant"
                })
            
        except Exception as e:
            error_msg = f"Error calling {model}: {str(e)}"
            if self.debug:
                print(f"[DEBUG] {error_msg}")
            return RunResult({"status": "error", "message": error_msg})
    
    def run(self, prompt: str, model="gpt-4o", system_prompt=None, cli="qwen-code", 
            schema_cls: Optional[Type[BaseModel]] = None, 
            memory_serializer: Optional[Callable[[BaseModel], str]] = None,
            ephemeral: bool = False):
        if cli == "mini-swe":
            # Import mini-swe dependencies only when needed
            from minisweagent.agents.default import DefaultAgent
            from minisweagent.environments.local import LocalEnvironment
            from .utils.llm_client import CustomMiniSweModel
            
            temp_agent = DefaultAgent(
                CustomMiniSweModel(model_name=model),
                LocalEnvironment(cwd=self.cwd if self.cwd else ""),
            )
            
            # Set step limit to prevent infinite loops
            temp_agent.config.step_limit = 10
            
            if system_prompt:
                temp_agent.config.system_template = system_prompt
            else:
                # Use a better default system template for mini-swe
                temp_agent.config.system_template = """You are a helpful AI assistant that can execute shell commands.

When you need to run a command, provide EXACTLY ONE action in triple backticks like this:
```bash
echo "Hello World"
```

After running the command, you will see the output. To complete a task, make sure the FIRST LINE of your command output is 'MINI_SWE_AGENT_FINAL_OUTPUT'."""        

            if self.messages:
                # Convert messages to mini-swe format
                converted_messages = []
                for msg in self.messages:
                    if "parts" in msg:
                        # Qwen format - extract text from parts
                        role = msg.get("role", "user")
                        if role == "model":
                            role = "assistant"
                        text = ""
                        for part in msg.get("parts", []):
                            if isinstance(part, dict) and "text" in part:
                                text += part["text"]
                        if text:
                            converted_messages.append({"role": role, "content": text})
                    else:
                        # Already in simple format
                        converted_messages.append(msg)
                
                input_text = json_list_serializer(converted_messages) + "\nuser (current task): " + prompt
            else:
                input_text = prompt
            status, message = temp_agent.run(input_text)

            # Store in simple format for mini-swe only if not ephemeral
            if not ephemeral:
                self.messages = self.messages + [{"role": "user", "content": prompt}] + copy.deepcopy(temp_agent.messages[2:])
            
            if self.debug and ephemeral:
                print(f"[DEBUG] Ephemeral mode: response not added to messages")

            return RunResult({"status": status, "message": {"role": "assistant", "content": message}, "type": "assistant"})
        elif cli == "qwen-code":
            return self._run_with_qwen(prompt, model, system_prompt, ephemeral)
        elif cli == "no-tools":
            return self._run_no_tools(prompt, model, system_prompt, schema_cls, memory_serializer, ephemeral)
        else:
            return RunResult({"status": "error", "message": f"CLI '{cli}' not supported."})

class ClaudeAgent(BaseAgent):
    """
    Manages a conversation with the Claude CLI or other LLMs, handling state and session resumption.

    The agent's state is stored entirely in the `self.messages` list. When continuing
    a conversation with existing history, the agent creates a new session file with
    the conversation history and uses the --resume flag to replay it.
    """

    def __init__(self, debug=False, system_prompt=None, cwd=None):
        """Initializes a new Agent.

        Args:
            debug (bool): If True, prints detailed diagnostic information.
            system_prompt (str): Default system prompt to use for all runs unless overridden.
            cwd (str|Path): Working directory for Claude Code execution. If None, uses current directory.
        """
        self.messages = []
        self.debug = debug
        self.default_system_prompt = system_prompt
        self.cwd = str(Path(cwd)) if cwd else None
        self._claude_cmd = self._find_claude_command()
        self._claude_projects_dir = Path.home() / ".claude" / "projects"
        
        # Model configuration will be loaded on demand from models.json

    def _find_claude_command(self):
        claude_cmd = shutil.which('claude')
        if not claude_cmd:
            raise FileNotFoundError("Claude command not found. Please ensure it's in your PATH.")
        return claude_cmd

    def _encode_path(self, path_str: str) -> str:
        """Replicates Claude's path encoding for session files."""
        if sys.platform == "win32" and ":" in path_str:
            drive, rest = path_str.split(":", 1)
            rest = rest.lstrip(os.path.sep)
            path_str = f"{drive}--{rest}"
        return path_str.replace(os.path.sep, '-')

    def load_state(self, file_path):
        """Loads conversation history from a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to load from.
        """
        self.messages = []
        path = Path(file_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.messages.append(json.loads(line))

    def save_state(self, file_path):
        """Saves conversation history to a JSONL file.
        
        Args:
            file_path (str|Path): Path to the JSONL file to save to.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            for msg in self.messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        if self.debug:
            print(f"[DEBUG] Persisted {len(self.messages)} messages to {path}")

    def _create_user_message(self, text_content: str, session_id: str, parent_uuid: str | None) -> dict:
        """
        Creates a user message dictionary.
        Always uses list-of-dicts for content, as per ground truth examples.
        """
        now_iso = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        message_content = [{"type": "text", "text": text_content}]
        message_body = {"role": "user", "content": message_content}

        message = {
            "parentUuid": parent_uuid, "isSidechain": False, "userType": "external",
            "cwd": self.cwd if self.cwd else os.getcwd(),
            "sessionId": session_id, "version": "1.0.64",
            "gitBranch": "", "type": "user", "message": message_body,
            "uuid": str(uuid.uuid4()), "timestamp": now_iso
        }
        return message

    def add_user_message(self, user_text: str):
        """
        Adds a user message. If the last message is already from the user,
        appends to it with a newline. Otherwise, creates a new message.
        """
        if self.messages and self.messages[-1].get('type') == 'user':
            # Last message is already a user message - append to it
            last_message = self.messages[-1]
            
            # Get the content array from the message
            content = last_message['message']['content']
            
            # Find the last text content item and append to it
            for i in range(len(content) - 1, -1, -1):
                if content[i]['type'] == 'text':
                    # Append with a newline
                    content[i]['text'] += '\nUser: ' + user_text
                    break
            else:
                # No text content found (shouldn't happen), add new text content
                content.append({"type": "text", "text": user_text})
            
            # Update timestamp to current time
            last_message['timestamp'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            if self.debug:
                print(f"[DEBUG] Appended to existing user message. Messages size: {len(self.messages)}")
        else:
            # Last message is not a user message or messages list is empty - create new message
            last_message = self.messages[-1] if self.messages else {}
            session_id = last_message.get('sessionId') or str(uuid.uuid4())
            parent_uuid = last_message.get('uuid')
            user_message = self._create_user_message(user_text, session_id, parent_uuid)
            self.messages.append(user_message)
            if self.debug:
                print(f"[DEBUG] Created new user message. Messages size: {len(self.messages)}")

    def _extract_conversation_history(self) -> List[Dict[str, str]]:
        """Extract meaningful text content from the conversation history for LLM consumption."""
        conversation = []
        
        for entry in self.messages:
            msg_type = entry.get('type')
            message = entry.get('message', {})
            role = message.get('role')
            content_list = message.get('content', [])
            
            # Skip only if no role AND no content
            if not role:
                continue
            
            # Extract all content types
            text_parts = []
            for content_item in content_list:
                if isinstance(content_item, dict):
                    content_type = content_item.get('type')
                    
                    if content_type == 'text':
                        text = content_item.get('text', '').strip()
                        if text and text != '[Request interrupted by user]':
                            text_parts.append(text)
                    
                    elif content_type == 'tool_use':
                        # Include tool use information
                        tool_name = content_item.get('name', 'unknown_tool')
                        tool_input = content_item.get('input', {})
                        text_parts.append(f"[Tool Use: {tool_name}]")
                        
                        # Extract key information from each tool
                        if tool_name == 'Write':
                            file_path = tool_input.get('file_path', '')
                            text_parts.append(f"Writing to: {file_path}")
                        elif tool_name == 'Bash':
                            command = tool_input.get('command', '')
                            text_parts.append(f"Running command: {command}")
                        elif tool_name == 'Edit':
                            file_path = tool_input.get('file_path', '')
                            text_parts.append(f"Editing file: {file_path}")
                        elif tool_name == 'Read':
                            file_path = tool_input.get('file_path', '')
                            text_parts.append(f"Reading file: {file_path}")
                        elif tool_name == 'Task':
                            description = tool_input.get('description', '')
                            text_parts.append(f"Task: {description}")
                        elif tool_name == 'TodoWrite':
                            todos = tool_input.get('todos', [])
                            text_parts.append(f"Managing {len(todos)} todo items")
                        elif tool_name == 'Grep':
                            pattern = tool_input.get('pattern', '')
                            path = tool_input.get('path', '.')
                            text_parts.append(f"Searching for '{pattern}' in {path}")
                        elif tool_name == 'LS':
                            path = tool_input.get('path', '')
                            text_parts.append(f"Listing directory: {path}")
                        # Add more tool-specific formatting as needed
                    
                    elif content_type == 'tool_result':
                        # Include tool results
                        result = content_item.get('content', '')
                        if isinstance(result, str):
                            result = result.strip()
                            if result:
                                text_parts.append(f"[Tool Result: {result}]")
                        elif isinstance(result, list):
                            # Handle list content (sometimes tool results are lists)
                            for item in result:
                                if isinstance(item, str):
                                    item = item.strip()
                                    if item:
                                        text_parts.append(f"[Tool Result: {item}]")
            
            # If we have any content (text, tools, or results), add to conversation
            if text_parts:
                combined_text = '\n'.join(text_parts)
                conversation.append({
                    'role': role,
                    'content': combined_text
                })
            elif content_list and role == 'user':
                # Handle user messages that only contain tool results (no text)
                # These are critical for understanding what actually happened
                placeholder_parts = []
                for content_item in content_list:
                    if isinstance(content_item, dict):
                        content_type = content_item.get('type')
                        if content_type == 'tool_result':
                            # Even empty tool results indicate successful execution
                            tool_use_id = content_item.get('tool_use_id', 'unknown')
                            result = content_item.get('content', '')
                            if isinstance(result, str) and not result:
                                placeholder_parts.append("[Tool completed successfully]")
                            elif isinstance(result, str):
                                placeholder_parts.append(f"[Tool Result: {result}]")
                
                if placeholder_parts:
                    conversation.append({
                        'role': role,
                        'content': '\n'.join(placeholder_parts)
                    })
        
        return conversation

    def _run_with_llm(self, prompt: str, model: str, system_prompt: Optional[str] = None, ephemeral: bool = False, schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None):
        """Run the prompt using an external LLM.
        
        Args:
            prompt: The prompt to send
            model: Model name to use
            system_prompt: Optional system prompt for this run
            ephemeral: If True, the prompt and response won't be added to messages
        """
        # Get client for this model
        try:
            llm_client, actual_model_name = get_llm_client(model)
        except Exception as e:
            return RunResult({"error": str(e)})
        
        if self.debug:
            print(f"[DEBUG] Running with LLM model: {model} (ephemeral: {ephemeral})")
        
        # Extract current conversation history
        history = self._extract_conversation_history()
        
        # Prepare messages for the LLM
        messages = []
        
        # Use provided system prompt, fall back to default, or use a basic one
        effective_system_prompt = system_prompt or self.default_system_prompt or \
            "You are a helpful AI assistant. The following is a conversation history. Please provide a helpful response to the latest query."
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": effective_system_prompt
        })
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Add the current prompt as a user message (in messages list, not persisted)
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Define response model
        class LLMResponse(BaseModel):
            response: str = Field(description="The AI assistant's response")
        
        try:
            if schema_cls:
                # Structured response path
                result = llm_client.chat.completions.create(
                    response_model=schema_cls,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Only add to messages if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Serialize for messages
                    serializer = memory_serializer or default_json_serializer
                    mem_text = serializer(result)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Structured response ({schema_cls.__name__})]\n{mem_text}"
                    self.add_user_message(response_text)
                
                # Return structured response
                return RunResult({
                    "result": result.model_dump(),
                    "session_id": self.messages[-1].get('sessionId') if self.messages else None,
                    "model": model,
                    "ephemeral": ephemeral
                })
            else:
                # Plain text response path (existing behavior)
                # Define response model for plain text
                class LLMResponse(BaseModel):
                    response: str = Field(description="The AI assistant's response")
                
                result = llm_client.chat.completions.create(
                    response_model=LLMResponse,
                    model=actual_model_name,
                    messages=messages
                )
                
                # Only add to messages if not ephemeral
                if not ephemeral:
                    # Add the user's prompt as a user message
                    self.add_user_message(prompt)
                    
                    # Add the LLM's response as a user message with clear attribution
                    response_text = f"\n[Following is {model}'s response]\n{result.response}"
                    self.add_user_message(response_text)
                
                # Return standardized format
                return RunResult({
                    "result": result.response,
                    "session_id": self.messages[-1].get('sessionId') if self.messages else None,
                    "model": model,
                    "ephemeral": ephemeral
                })
            
        except Exception as e:
            error_msg = f"Error calling {model}: {str(e)}"
            if self.debug:
                print(f"[DEBUG] {error_msg}")
            return RunResult({"error": error_msg})

    def _run_with_claude(self, prompt: str, system_prompt: Optional[str] = None):
        """Run the prompt using Claude Code (original implementation)."""
        if self.debug: print("\n--- AGENT RUN (Claude) ---")

        current_dir = self.cwd if self.cwd else os.getcwd()
        cwd_encoded = self._encode_path(current_dir)
        session_dir = self._claude_projects_dir / cwd_encoded
        use_shell = sys.platform == 'win32'
        
        session_file_we_made = None
        session_file_claude_made = None

        try:
            # Determine the resume ID from messages. No messages means no resume ID.
            resume_id = self.messages[-1].get('sessionId') if self.messages else None

            # Build base command with required flags
            base_cmd = [self._claude_cmd, prompt, '-p', '--output-format', 'json', '--dangerously-skip-permissions']
            
            # Add system prompt if provided (use run-specific or fall back to default)
            effective_system_prompt = system_prompt or self.default_system_prompt
            if effective_system_prompt:
                base_cmd.extend(['--system-prompt', effective_system_prompt])

            if not resume_id:
                # --- Path 1: NEW CONVERSATION ---
                if self.debug: print("[DEBUG] STRATEGY: New conversation. Letting Claude handle state.")
                cmd = base_cmd
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")
            else:
                # --- Path 2: RESUME CONVERSATION ---
                if self.debug: print(f"[DEBUG] STRATEGY: Resuming with Session ID: {resume_id}")
                
                session_file_we_made = session_dir / f"{resume_id}.jsonl"
                session_dir.mkdir(parents=True, exist_ok=True)
                with open(session_file_we_made, 'w', encoding='utf-8') as f:
                    for msg in self.messages:
                        f.write(json.dumps(msg) + '\n')
                if self.debug: print(f"[DEBUG] Wrote {len(self.messages)} messages to temp file: {session_file_we_made}")

                cmd = base_cmd + ['--resume', resume_id]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=use_shell, cwd=current_dir, check=False, encoding="utf-8")

            # --- Process Result (Same for both paths) ---
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                # Use the new session ID from the response to load the updated history
                new_session_id = response_data.get('session_id')
                if new_session_id:
                    session_file_claude_made = session_dir / f"{new_session_id}.jsonl"
                    if self.debug: print(f"[DEBUG] Command successful. Loading updated history from NEW session file: {session_file_claude_made}")
                    
                    # Load a new messages state from the file Claude just created
                    new_messages = []
                    if session_file_claude_made.exists():
                        with open(session_file_claude_made, 'r', encoding='utf-8') as f:
                             for line in f:
                                if line.strip(): new_messages.append(json.loads(line))
                    self.messages = new_messages
                
                # Standardize response format to match OpenRouter format
                return RunResult({
                    "result": response_data.get('result'),
                    "session_id": response_data.get('session_id'),
                    "model": "claude-code",
                    "ephemeral": False,
                    # Keep original Claude metadata for advanced users
                    "_claude_metadata": response_data
                })
            else:
                error_details = f"Exit Code: {result.returncode}\n--- STDERR ---\n{result.stderr or 'No stderr.'}\n--- STDOUT ---\n{result.stdout or 'No stdout.'}\n"
                return RunResult({"error": error_details})

        finally:
            # Clean up both temporary session files
            if session_file_we_made and session_file_we_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up temp file we made: {session_file_we_made}")
                session_file_we_made.unlink()
            if session_file_claude_made and session_file_claude_made.exists():
                if self.debug: print(f"[DEBUG] Cleaning up file Claude made: {session_file_claude_made}")
                session_file_claude_made.unlink()

    def run(self, prompt: str, model: Optional[str] = None, system_prompt: Optional[str] = None, 
            ephemeral: bool = False, messages_cutoff: Optional[int] = None, 
            schema_cls: Optional[Type[BaseModel]] = None, memory_serializer: Optional[Callable[[BaseModel], str]] = None):
        """
        Runs a prompt, automatically handling session state, and returns the result.
        
        Args:
            prompt: The prompt to run
            model: Optional model name. If not provided, uses Claude Code.
                   If provided, uses the specified model from models.json configuration.
            system_prompt: Optional system prompt for this specific run.
                          If not provided, uses the default system prompt from __init__.
            ephemeral: If True and using a non-Claude model, the interaction won't be saved to messages.
                      This parameter is ignored for Claude Code calls.
            messages_cutoff: Maximum number of items to keep in messages. When exceeded, oldest items 
                          are removed. Default is 50. Set to None to disable cutoff.
        
        Returns:
            Dictionary with the response result
        """
        # Run the prompt with the appropriate method
        if model:
            result = self._run_with_llm(prompt, model, system_prompt, ephemeral, schema_cls, memory_serializer)
        else:
            if ephemeral and self.debug:
                print("[DEBUG] Warning: ephemeral parameter ignored for Claude Code calls")
            if schema_cls and self.debug:
                print("[DEBUG] Warning: schema_cls parameter ignored for Claude Code calls")
            result = self._run_with_claude(prompt, system_prompt)
        
        # Apply messages cutoff if enabled
        if messages_cutoff is not None and len(self.messages) > messages_cutoff:
            items_to_remove = len(self.messages) - messages_cutoff
            if self.debug:
                print(f"[DEBUG] Messages cutoff reached ({len(self.messages)} > {messages_cutoff}). "
                      f"Removing {items_to_remove} oldest items.")
            self.messages = self.messages[items_to_remove:]
        
        return result

