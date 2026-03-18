import os
from playwright.sync_api import sync_playwright

BROWSER_TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "browse_webpage",
        "description": "Fetch the text content of a webpage. Useful for searching the web or reading documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to read."
                }
            },
            "required": ["url"]
        }
    }
}

def browse_webpage(url: str) -> str:
    engine = os.getenv("PLAYWRIGHT_BROWSER", "chromium").lower()
    try:
        with sync_playwright() as p:
            if engine == "chrome":
                browser = p.chromium.launch(channel="chrome", headless=True)
            elif engine == "firefox":
                browser = p.firefox.launch(headless=True)
            elif engine == "brave":
                # Typical brave path on linux
                browser = p.chromium.launch(executable_path="/usr/bin/brave-browser", headless=True)
            else:
                browser = p.chromium.launch(headless=True)
                
            page = browser.new_page()
            page.goto(url, timeout=30000)
            text = page.locator("body").inner_text()
            browser.close()
            # Truncate to avoid context window explosion
            return text[:5000]
    except Exception as e:
        return f"Browser error: {e}"
