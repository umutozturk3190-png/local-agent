import ollama
import os
from typing import List, Dict, Any, Callable

class Agent:
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.tools = []
        self.tool_map = {}
        
    def add_tool(self, tool_def: Dict[str, Any], func: Callable):
        self.tools.append(tool_def)
        self.tool_map[tool_def["function"]["name"]] = func

    def chat(self, messages: List[Dict[str, Any]]) -> str:
        """
        Sends messages to the local model, handles tool calls automatically,
        and returns the final text response.
        Updates the messages list in-place with tool calls and outputs.
        """
        system_content = os.getenv("AGENT_PERSONA", "You are Local-Agent, a helpful AI assistant.")
        system_msg = {
            "role": "system",
            "content": f"{system_content} You have terminal and system tools. IMPORTANT: If the user asks a conversational question, reply naturally. But if the user asks you to perform ANY computer action (like listing directories, exploring files), YOU MUST use the tool immediately. Do not ask for permission. Do not output raw JSON, use the native tool API."
        }
        
        # We pass a copy to the API to avoid polluting the DB with the system prompt repeatedly
        api_messages = [{"role": m["role"], "content": m.get("content", "")} for m in messages]
        api_messages.insert(0, system_msg)
        
        while True:
            # Aggressive Reminder for Legacy Mode
            if not getattr(self, "native_tools_supported", True) and len(api_messages) > 1:
                if api_messages[-1]["role"] == "user":
                    reminder = "\n\n[SYSTEM REMINDER: You are an agent with tools. Do NOT write code to answer this if the user wants you to run a command. To run a command or use a tool, you MUST output EXACTLY and ONLY the JSON format: [{\"function\": {\"name\": \"execute_bash\", \"arguments\": {\"command\": \"...\"}}}]]"
                    # Prevent duplicating the reminder if loop retries
                    if "[SYSTEM REMINDER" not in api_messages[-1]["content"]:
                        api_messages[-1]["content"] += reminder

            try:
                if getattr(self, "native_tools_supported", True):
                    response = ollama.chat(
                        model=self.model,
                        messages=api_messages,
                        tools=self.tools if self.tools else None
                    )
                else:
                    response = ollama.chat(
                        model=self.model,
                        messages=api_messages
                    )
            except Exception as e:
                # Catch 400 error for unsupported tools
                if "does not support tools" in str(e).lower() or "400" in str(e):
                    self.native_tools_supported = False
                    
                    import json
                    def clean_tool(t_def: Dict[str, Any]) -> Dict[str, Any]:
                        return {
                            "name": t_def["function"]["name"], 
                            "description": t_def["function"]["description"], 
                            "parameters": t_def["function"]["parameters"]
                        }
                        
                    clean_tools = [clean_tool(t) for t in self.tools]
                    tools_text = json.dumps(clean_tools, indent=2)
                    
                    fallback_system_msg = {
                        "role": "system",
                        "content": f"{system_content} You have terminal and system tools. IMPORTANT: Because your brain doesn't support the native tools API, you MUST output raw JSON to call a tool, in EXACTLY this format: [{{\"function\": {{\"name\": \"execute_bash\", \"arguments\": {{\"command\": \"ls\"}}}}}}]. DO NOT output anything else if you want to use a tool. Available tools: {tools_text}"
                    }
                    api_messages[0] = fallback_system_msg
                    continue
                else:
                    raise e

            msg = response["message"]
            
            # Fallback for models that output raw JSON string instead of native tool calls
            content = msg.get("content", "").strip()
            if not msg.get("tool_calls"):
                import re
                import json
                
                # Check for list of functions format (from fallback prompt)
                match = re.search(r'\[\s*\{\s*"function"\s*:\s*\{.*?\}\s*\}\s*\]', content, re.DOTALL)
                if match:
                    try:
                        parsed = json.loads(match.group(0))
                        msg["tool_calls"] = parsed
                        msg["content"] = ""
                    except Exception:
                        pass
                else:
                    # Check for direct object format (raw unprompted output)
                    match_obj = re.search(r'\{\s*"name"\s*:\s*".*?",\s*"arguments"\s*:\s*\{.*?\}\s*\}', content, re.DOTALL)
                    if match_obj:
                        try:
                            parsed_obj = json.loads(match_obj.group(0))
                            msg["tool_calls"] = [{"function": parsed_obj}]
                            msg["content"] = ""
                        except Exception:
                            pass
            
            messages.append(msg)
            api_messages.append(msg)
            
            # If no tool calls, this is the final response to the user
            if not msg.get("tool_calls"):
                return msg.get("content", "")
                
            # If there are tool calls, execute them
            for tool_call in msg["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                
                tool_result = None
                if tool_name in self.tool_map:
                    try:
                        tool_result = self.tool_map[tool_name](**tool_args)
                    except Exception as e:
                        tool_result = f"Error executing tool {tool_name}: {str(e)}"
                else:
                    tool_result = f"Error: Unknown tool {tool_name}"
                
                # Format tool execution response smartly based on Native vs Legacy modes
                if getattr(self, "native_tools_supported", True):
                    tool_msg = {
                        "role": "tool",
                        "content": str(tool_result),
                        "name": tool_name
                    }
                else:
                    # Legacy fallback models will CRASH or LOOP if sent a 'tool' role.
                    # Send the result back as an invisible system-like user prompt.
                    tool_msg = {
                        "role": "user",
                        "content": f"[SYSTEM NOTIFICATION RE-ENTRY] The tool '{tool_name}' was executed successfully by your request. Here is the raw terminal/system output:\n\n{str(tool_result)}\n\nPlease read this output and provide a natural language response to the user. DO NOT output JSON anymore unless the user asks you to run another command."
                    }
                    
                messages.append(tool_msg)
                api_messages.append(tool_msg)
                
        # Final safety catch-all
        return "I completed the action but lost my train of thought."
