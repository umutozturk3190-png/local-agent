#!/bin/bash
set -e

echo "======================================"
echo "🦞 Local-Agent Setup 🦞"
echo "======================================"

echo "Creating Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "Installing Requirements..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

env_file=".env"
echo ""
echo "--- Configuration ---"

read -p "Which Ollama model do you want to use? (default: llama3.2): " model
model=${model:-llama3.2}

read -p "Enter Telegram Bot Token (leave blank to skip): " tgtok

read -p "Enable Browser Tool? (Playwright) [y/N]: " browser
read -p "Enable System UI Control? (PyAutoGUI) [y/N]: " sysui

echo "OLLAMA_MODEL=\"$model\"" > $env_file
echo "TELEGRAM_BOT_TOKEN=\"$tgtok\"" >> $env_file

if [[ "$browser" =~ ^[Yy]$ ]]; then
    echo "ENABLE_BROWSER=True" >> $env_file
    echo "Installing Playwright chromium..."
    playwright install chromium
else
    echo "ENABLE_BROWSER=False" >> $env_file
fi

if [[ "$sysui" =~ ^[Yy]$ ]]; then
    echo "ENABLE_SYSTEM_UI=True" >> $env_file
    if command -v apt-get &> /dev/null; then
        echo "Installing Linux UI dependencies..."
        sudo apt-get install -y python3-tk python3-dev python3-xlib scrot x11-utils xdotool || true
    fi
else
    echo "ENABLE_SYSTEM_UI=False" >> $env_file
fi

echo "ENABLE_BASH=True" >> $env_file
echo "ENABLE_FILESYSTEM=True" >> $env_file

echo ""
echo "✅ Configuration saved to .env"
echo "✅ Setup Complete! Run 'source venv/bin/activate && python main.py' to start."
