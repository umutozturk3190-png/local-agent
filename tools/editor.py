import os

EDITOR_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "An advanced file editor that can find, replace, insert, and delete lines in files.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"},
                "action": {"type": "string", "description": "The action to perform: 'replace_line', 'insert_line', 'delete_line', 'search_replace'"},
                "line_number": {"type": "integer", "description": "Line number to modify (1-indexed). Required for line actions."},
                "text": {"type": "string", "description": "New text to insert or replace with."},
                "search_text": {"type": "string", "description": "Text to search for (used only in search_replace action)."}
            },
            "required": ["path", "action"]
        }
    }
}

def edit_file(path: str, action: str, line_number: int | None = None, text: str | None = None, search_text: str | None = None) -> str:
    if not os.path.exists(path):
        return f"Error: File '{path}' does not exist."
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if action in ["replace_line", "insert_line", "delete_line"] and line_number is None:
            return "Error: line_number is required for line actions."
            
        if action in ["replace_line", "insert_line"] and text is None:
            return "Error: text is required for this action."
            
        if action == "replace_line":
            if line_number < 1 or line_number > len(lines):
                return "Error: line_number out of range."
            lines[line_number - 1] = str(text) + "\n"
        elif action == "insert_line":
            if line_number < 1 or line_number > len(lines) + 1:
                return "Error: line_number out of range."
            lines.insert(line_number - 1, str(text) + "\n")
        elif action == "delete_line":
            if line_number < 1 or line_number > len(lines):
                return "Error: line_number out of range."
            del lines[line_number - 1]
        elif action == "search_replace":
            if not search_text or text is None:
                return "Error: search_text and text are required for search_replace."
            content = "".join(lines)
            content = content.replace(search_text, text)
            lines = [line + "\n" for line in content.split("\n")]
            # Clean up trailing newline artifacts from split
            lines = lines[:-1] if lines and lines[-1] == "\n" else lines
        else:
            return f"Error: unknown action '{action}'"
            
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
        return f"File '{path}' successfully edited using action: {action}."
    except Exception as e:
        return f"Editor error: {e}"
