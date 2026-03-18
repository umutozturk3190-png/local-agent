# Local-Agent 🦞

An open-source, local-only personal AI assistant inspired by OpenClaw. The assistant runs entirely on your own machine using local LLMs (via Ollama). It grants the AI safe access to your system, file management, browser control, and UI automation.

## Features
- **Privacy First**: Uses local models (Llama 3, Mistral, Qwen etc).
- **System Control**: Can execute bash commands, manage files.
- **UI Automation**: Safe keyboard and mouse control (`pyautogui`).
- **Browser Automation**: Ability to browse the web using `playwright`.
- **Persistent Memory**: SQLite based conversation history persistence.
- **Interfaces**: Features a colorful, interactive CLI and an optional Telegram Bot integration.

## Prerequisites
- Linux, macOS, or Windows
- Python 3.10+
- [Ollama](https://ollama.com) installed and running with at least the `llama3.2` model.
*(Note: To use a different model, set `OLLAMA_MODEL=mistral` before running the agent.)*

## Installation 

Run the automated installer:
```bash
chmod +x install.sh
./install.sh
```
This script will set up a Python virtual environment (`venv/`), install the required Python packages, and set up `playwright` for browser control.

## Usage

### CLI Interface
To start the rich terminal experience:
```bash
source venv/bin/activate
python main.py
```

### Telegram Bot
To run the telegram bot, set your Bot Token in the environment:
```bash
source venv/bin/activate
export TELEGRAM_BOT_TOKEN="your_bot_token"
python interfaces/telegram_bot.py
```

---
**License**: GNU General Public License v3.0 (GPLv3)
