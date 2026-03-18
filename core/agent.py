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
        api_messages = [system_msg] + messages
        
        while True:
            response = ollama.chat(
                model=self.model,
                messages=api_messages,
                tools=self.tools if self.tools else None
            )
            msg = response["message"]
            
            # Fallback for models that output raw JSON string instead of native tool calls
            content = msg.get("content", "").strip()
            if not msg.get("tool_calls") and content.startswith("{") and content.endswith("}") and '"name"' in content:
                import json
                try:
                    parsed = json.loads(content)
                    if "name" in parsed and "arguments" in parsed:
                        msg["tool_calls"] = [{"function": parsed}]
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
                name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]
                
                if name in self.tool_map:
                    try:
                        result = self.tool_map[name](**args)
                        messages.append({
                            "role": "tool",
                            "name": name,
                            "content": str(result)
                        })
                    except Exception as e:
                        messages.append({
                            "role": "tool",
                            "name": name,
                            "content": f"Error executing tool {name}: {str(e)}"
                        })
                else:
                    messages.append({
                        "role": "tool",
                        "name": name,
                        "content": f"Error: Unknown tool {name}"
                    })
