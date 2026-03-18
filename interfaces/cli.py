from rich.console import Console
from rich.markdown import Markdown

console = Console()

def print_assistant(message: str):
    console.print("\n[bold cyan]🦞 OpenClaw (Local):[/bold cyan]")
    if message.strip():
        console.print(Markdown(message))
    else:
        console.print("[italic]No text response (likely executed a tool)[/italic]")
    
def print_system(message: str):
    console.print(f"[bold yellow]System:[/bold yellow] {message}")

def print_tool_call(tool_name: str, args: dict):
    console.print(f"[bold magenta]⚒️  Tool Call:[/bold magenta] {tool_name}({args})")

def get_user_input() -> str:
    console.print("\n[bold green]You:[/bold green] ", end="")
    try:
        return input()
    except EOFError:
        return "exit"
