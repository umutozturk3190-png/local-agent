import os

from tools.bash import BASH_TOOL_DEF, execute_bash
from tools.filesystem import READ_FILE_DEF, WRITE_FILE_DEF, read_file, write_file

def load_skills(agent):
    # Core Skills
    if os.getenv("ENABLE_BASH", "True") == "True":
        agent.add_tool(BASH_TOOL_DEF, execute_bash)
    if os.getenv("ENABLE_FILESYSTEM", "True") == "True":
        agent.add_tool(READ_FILE_DEF, read_file)
        agent.add_tool(WRITE_FILE_DEF, write_file)
        
    # Optional Skills
    if os.getenv("ENABLE_BROWSER") == "True":
        try:
            from tools.browser import BROWSER_TOOL_DEF, browse_webpage
            agent.add_tool(BROWSER_TOOL_DEF, browse_webpage)
            print("🦞 Skill Enabled: Browser Automation")
        except ImportError:
            pass
            
    if os.getenv("ENABLE_SYSTEM_UI") == "True":
        try:
            from tools.system_ui import SYSTEM_UI_TOOL_DEF, control_ui
            agent.add_tool(SYSTEM_UI_TOOL_DEF, control_ui)
            print("🦞 Skill Enabled: System UI Control")
        except ImportError:
            pass
