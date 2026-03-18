import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.skills import load_skills
from memory.database import MemoryDB
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello 🦞! I am Local-Agent, your private completely local assistant. Send me a message and I can browse the web, control your PC, or act on your files.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    session_id = f"tg_{update.effective_chat.id}"
    
    db = MemoryDB("memory.db")
    
    agent_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    agent = Agent(model=agent_model)
    
    load_skills(agent)

    # Load history for this telegram chat
    messages = db.get_messages(session_id)
    messages.append({"role": "user", "content": user_text})
    db.add_message(session_id, {"role": "user", "content": user_text})
    
    starting_len = len(messages)
    
    status_msg = await update.message.reply_text("Thinking... 🦞")
    
    try:
        response_text = agent.chat(messages)
        tool_feedback = ""
        for new_msg in messages[starting_len:]:
            db.add_message(session_id, new_msg)
            if new_msg.get("role") == "tool":
                name = new_msg.get('name')
                if name:
                    tool_feedback += f"[Used Tool: {name}]\n"
                
        final_msg = f"{tool_feedback}\n{response_text}" if tool_feedback else response_text
        if not final_msg.strip():
            final_msg = "Command executed successfully. (No text output)"
            
        await status_msg.edit_text(final_msg)
        
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}")

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Please set TELEGRAM_BOT_TOKEN environment variable (e.g. export TELEGRAM_BOT_TOKEN='your_token').")
        sys.exit(1)
        
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Telegram bot started! Send a message to your bot. Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
