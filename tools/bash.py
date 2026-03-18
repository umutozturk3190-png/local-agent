import os
import subprocess

# Global state for persistent terminal sessions
CURRENT_DIR = os.getcwd()

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
    global CURRENT_DIR
    
    safe_mode = os.getenv("SAFE_MODE", "True") == "True"
    if safe_mode:
        dangerous_keywords = ["rm -rf", "sudo ", "mkfs", "dd ", "> /dev/", "chmod -R", "chown -R"]
        for kw in dangerous_keywords:
            if kw in command:
                return f"Command blocked by SAFE_MODE. You are not allowed to use '{kw}'. Find a safer alternative."
                
    try:
        # Wrap command to output the new directory at the end, so we can track 'cd' changes
        wrapped_command = f"{command}\npwd"
        
        result = subprocess.run(
            wrapped_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=CURRENT_DIR,
            timeout=120
        )
        
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if result.returncode == 0 and stdout:
            lines = stdout.split('\n')
            new_cwd = lines[-1].strip()
            if os.path.isdir(new_cwd):
                CURRENT_DIR = new_cwd
            # Remove the pwd output from what the model sees
            actual_stdout = '\n'.join(lines[:-1]).strip()
            output = actual_stdout if actual_stdout else "Command executed successfully with no output."
        else:
            output = stdout if stdout else "Command executed successfully with no output."
            
        if stderr:
            output += f"\n\nStandard Error:\n{stderr}"
            
        return output
    except Exception as e:
        return f"Error executing bash: {str(e)}"
