import os
import subprocess

BASH_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "execute_bash",
        "description": "Execute a bash command on the local system and return its output. This allows full automation of the machine.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute."
                }
            },
            "required": ["command"],
        },
    },
}

def execute_bash(command: str) -> str:
    safe_mode = os.getenv("SAFE_MODE", "True") == "True"
    if safe_mode:
        dangerous_keywords = ["rm -rf", "sudo ", "mkfs", "dd ", "> /dev/", "chmod -R", "chown -R"]
        for kw in dangerous_keywords:
            if kw in command:
                return f"Command blocked by SAFE_MODE. You are not allowed to use '{kw}'. Find a safer alternative."
                
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if not output.strip():
            return "Command executed successfully with no output."
        return output
    except Exception as e:
        return f"Exception while running command: {e}"
