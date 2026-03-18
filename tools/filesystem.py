import os

READ_FILE_DEF = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file at the given absolute or relative path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file."
                }
            },
            "required": ["path"]
        }
    }
}

WRITE_FILE_DEF = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write text content to a file. Overwrites the file if it exists, creates it if not. Make sure directories exist before writing.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write."
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write into the file."
                }
            },
            "required": ["path", "content"]
        }
    }
}

def read_file(path: str) -> str:
    try:
        if not os.path.exists(path):
            return f"Error: File does not exist at {path}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    try:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written successfully to {path}"
    except Exception as e:
        return f"Error writing file: {e}"
