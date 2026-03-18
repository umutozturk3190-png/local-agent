import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.skills import load_skills
from memory.database import MemoryDB
from interfaces.cli import print_assistant, print_system, print_tool_call, get_user_input
from dotenv import load_dotenv

load_dotenv()

def main():
    print_system("Initializing Local-Agent...")
    
    # Initialize DB (memory)
    db = MemoryDB("memory.db")
    session_id = "default_session"
    
    # Initialize Agent
    agent_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    agent = Agent(model=agent_model)
    
    # Register Tools dynamically based on .env
    load_skills(agent)
    
    print_system(f"Agent ready using model '{agent_model}'! Type 'exit' to quit.")
    
    messages = []
    
    while True:
        try:
            user_text = get_user_input()
            if not user_text.strip():
                continue
            if user_text.lower() in ["exit", "quit"]:
                break
                
            messages.append({"role": "user", "content": user_text})
            db.add_message(session_id, {"role": "user", "content": user_text})
            
            starting_len = len(messages)
            
            print_system("Thinking...")
            response_text = agent.chat(messages)
            
            for new_msg in messages[starting_len:]:
                db.add_message(session_id, new_msg)
                
                if new_msg.get("role") == "tool":
                    name = new_msg.get("name")
                    if name:
                        print_tool_call(name, "executed")
                
            print_assistant(response_text)
            
        except KeyboardInterrupt:
            print_system("\nExiting...")
            break
        except Exception as e:
            print_system(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
