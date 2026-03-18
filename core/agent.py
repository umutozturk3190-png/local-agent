import ollama
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
        while True:
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None
            )
            msg = response["message"]
            messages.append(msg)
            
            # If no tool calls, this is the final final response to the user
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
