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

echo "Available local Ollama models:"
if command -v ollama &> /dev/null; then
    ollama list | awk 'NR>1 {print "  - " $1}'
else
    echo "  (Ollama not found in PATH or not running)"
fi
echo ""

read -p "Which Ollama model do you want to use? (default: llama3.2): " model
model=${model:-llama3.2}

read -p "Enter Telegram Bot Token (leave blank to skip): " tgtok

echo ""
echo "--- Agent Personality ---"
echo "1) Default (Helpful AI)"
echo "2) Developer (Concise, Code-focused)"
echo "3) Sarcastic (Funny, Witty)"
echo "4) Pirate (Speaks like a pirate)"
read -p "Choose a personality [1-4] (default: 1): " p_choice

persona="You are Local-Agent, a helpful AI assistant."
if [ "$p_choice" == "2" ]; then persona="You are Local-Agent, a senior software engineer. Be highly concise and code-focused."; fi
if [ "$p_choice" == "3" ]; then persona="You are Local-Agent, a highly sarcastic and witty AI. Use dry humor."; fi
if [ "$p_choice" == "4" ]; then persona="You are Local-Agent, a pirate. Speak entirely in pirate slang, matey!"; fi

echo ""
read -p "Enable Browser Tool? (Playwright) [y/N]: " browser
b_engine="chromium"
if [[ "$browser" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Which browser engine should the agent use?"
    echo "1) Chromium (Default inside Playwright)"
    echo "2) Google Chrome (Must be installed on your PC)"
    echo "3) Mozilla Firefox (Must be installed on your PC)"
    echo "4) Brave (Must be installed on your PC)"
    read -p "Select browser [1-4] (default: 1): " b_choice
    if [ "$b_choice" == "2" ]; then b_engine="chrome"; fi
    if [ "$b_choice" == "3" ]; then b_engine="firefox"; fi
    if [ "$b_choice" == "4" ]; then b_engine="brave"; fi
fi

echo ""
# Detect Wayland
is_wayland=false
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ "$WAYLAND_DISPLAY" != "" ]; then
    is_wayland=true
fi

if [ "$is_wayland" = true ]; then
    echo "⚠️  Wayland Display Detected! PyAutoGUI (System UI) usually fails on Wayland."
    read -p "Enable System UI Control anyway? (Not recommended) [y/N]: " sysui
else
    read -p "Enable System UI Control? (PyAutoGUI) [y/N]: " sysui
fi

# Write explicitly to .env
echo "OLLAMA_MODEL=\"$model\"" > $env_file
echo "TELEGRAM_BOT_TOKEN=\"$tgtok\"" >> $env_file
echo "AGENT_PERSONA=\"$persona\"" >> $env_file

if [[ "$browser" =~ ^[Yy]$ ]]; then
    echo "ENABLE_BROWSER=True" >> $env_file
    echo "PLAYWRIGHT_BROWSER=\"$b_engine\"" >> $env_file
    echo "Installing Playwright core dependencies..."
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
echo "ENABLE_EDITOR=True" >> $env_file

read -p "Enable ULTRA SAFE MODE (Blocks rm -rf, sudo, mkfs etc)? [Y/n]: " smode
if [[ ! "$smode" =~ ^[Nn]$ ]]; then
    echo "SAFE_MODE=True" >> $env_file
else
    echo "SAFE_MODE=False" >> $env_file
fi

echo "✅ Configuration saved to .env"
echo "✅ Setup Complete! Run 'source venv/bin/activate && python main.py' to start."
