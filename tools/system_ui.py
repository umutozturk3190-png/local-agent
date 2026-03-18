import pyautogui

# Fail-safe feature: If the mouse goes to one of the four corners of the screen, raise a FailSafeException
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

SYSTEM_UI_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "control_ui",
        "description": "Control the computer's mouse and keyboard. Can click, type text, or press keys. WARNING: Move the mouse to a corner to trigger a Fail-Safe abort.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform: 'move', 'click', 'type', or 'press'."
                },
                "x": {
                    "type": "integer",
                    "description": "X coordinate for move/click."
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate for move/click."
                },
                "text": {
                    "type": "string",
                    "description": "Text to type."
                },
                "key": {
                    "type": "string",
                    "description": "Key to press (e.g., 'enter', 'win', 'ctrl', 'space', etc.)."
                }
            },
            "required": ["action"]
        }
    }
}

def control_ui(action: str, x: int | None = None, y: int | None = None, text: str | None = None, key: str | None = None) -> str:
    try:
        if action == "move":
            if x is None or y is None:
                return "Error: x and y required for move."
            pyautogui.moveTo(x, y, duration=0.5)
            return f"Mouse moved to {x},{y}"
            
        elif action == "click":
            if x is not None and y is not None:
                pyautogui.click(x, y)
                return f"Mouse clicked at {x},{y}"
            else:
                pyautogui.click()
                return "Mouse clicked at current position."
                
        elif action == "type":
            if not text:
                return "Error: text required for type action."
            pyautogui.write(text, interval=0.05)
            return f"Typed text: '{text}'"
            
        elif action == "press":
            if not key:
                return "Error: key required for press action."
            pyautogui.press(key)
            return f"Pressed key: '{key}'"
            
        else:
            return f"Error: unknown action '{action}'"
            
    except pyautogui.FailSafeException:
        return "Fail-safe triggered! Mouse moved to the corner of the screen by user."
    except Exception as e:
        return f"UI Control Error: {e}"
