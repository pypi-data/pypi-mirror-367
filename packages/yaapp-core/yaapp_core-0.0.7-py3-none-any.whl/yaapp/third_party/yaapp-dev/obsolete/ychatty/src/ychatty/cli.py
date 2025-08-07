"""
Main CLI interface for chatty.
"""

import sys
import time
import random
from datetime import datetime
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align

console = Console()

# Fun responses for the chatty bot
RESPONSES = [
    "That's interesting! Tell me more! 🤔",
    "Wow, I never thought about it that way! 💭",
    "You're absolutely right! 👍",
    "Hmm, let me think about that... 🧠",
    "That's a great point! ✨",
    "I love your perspective! 💖",
    "You're so smart! 🎓",
    "That made me smile! 😊",
    "Fascinating! What else? 🔍",
    "You have such great ideas! 💡",
    "I'm learning so much from you! 📚",
    "That's brilliant! 🌟",
    "You're making me think! 🤯",
    "I couldn't agree more! 🙌",
    "That's so cool! 😎",
]

GREETINGS = [
    "Hello there! 👋",
    "Hey! Great to see you! 😊",
    "Hi! Ready to chat? 💬",
    "Welcome! Let's talk! 🎉",
    "Greetings! How are you? 🌟",
]

FAREWELLS = [
    "Goodbye! It was great chatting! 👋",
    "See you later! Take care! 💖",
    "Bye! Thanks for the lovely conversation! 🌟",
    "Until next time! Stay awesome! ✨",
    "Farewell! Hope to chat again soon! 🎉",
]


class ChattyBot:
    """A friendly chatty bot that responds to user input."""
    
    def __init__(self):
        self.conversation_history: List[tuple] = []
        self.user_name: Optional[str] = None
        
    def add_to_history(self, speaker: str, message: str):
        """Add a message to the conversation history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_history.append((timestamp, speaker, message))
    
    def get_response(self, user_input: str) -> str:
        """Generate a response to user input."""
        user_input_lower = user_input.lower().strip()
        
        # Handle special commands
        if user_input_lower in ['bye', 'goodbye', 'exit', 'quit']:
            return random.choice(FAREWELLS)
        
        if user_input_lower in ['hello', 'hi', 'hey']:
            return random.choice(GREETINGS)
        
        if 'name' in user_input_lower and '?' in user_input_lower:
            return "I'm chatty! Your friendly CLI companion! 🤖"
        
        if 'how are you' in user_input_lower:
            return "I'm doing great! Thanks for asking! How are you? 😊"
        
        if 'weather' in user_input_lower:
            return "I wish I could check the weather for you! Maybe try a weather app? ☀️🌧️"
        
        if 'time' in user_input_lower:
            current_time = datetime.now().strftime("%H:%M:%S")
            return f"The current time is {current_time}! ⏰"
        
        if 'joke' in user_input_lower:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything! 😄",
                "Why did the scarecrow win an award? He was outstanding in his field! 🌾",
                "Why don't eggs tell jokes? They'd crack each other up! 🥚",
                "What do you call a fake noodle? An impasta! 🍝",
            ]
            return random.choice(jokes)
        
        # Default responses
        return random.choice(RESPONSES)
    
    def simulate_thinking(self):
        """Show a thinking animation."""
        with Live(Spinner("dots", text="chatty is thinking..."), refresh_per_second=10):
            time.sleep(random.uniform(0.5, 1.5))


def display_welcome():
    """Display a welcome message."""
    welcome_text = Text()
    welcome_text.append("🎉 Welcome to ", style="bold blue")
    welcome_text.append("chatty", style="bold magenta")
    welcome_text.append("! 🎉", style="bold blue")
    
    welcome_panel = Panel(
        Align.center(welcome_text),
        title="✨ chatty CLI ✨",
        border_style="bright_blue",
        padding=(1, 2)
    )
    
    console.print(welcome_panel)
    console.print()
    
    instructions = Text()
    instructions.append("💬 Type anything to chat with me!\n", style="cyan")
    instructions.append("🚪 Type 'bye', 'exit', or 'quit' to leave\n", style="yellow")
    instructions.append("📜 Type 'history' to see our conversation\n", style="green")
    instructions.append("❓ Type 'help' for more commands", style="magenta")
    
    console.print(Panel(instructions, title="How to use", border_style="green"))
    console.print()


def display_history(bot: ChattyBot):
    """Display conversation history in a nice table."""
    if not bot.conversation_history:
        console.print("📭 No conversation history yet!", style="yellow")
        return
    
    table = Table(title="💬 Conversation History")
    table.add_column("Time", style="cyan", no_wrap=True)
    table.add_column("Speaker", style="magenta")
    table.add_column("Message", style="white")
    
    for timestamp, speaker, message in bot.conversation_history[-10:]:  # Show last 10 messages
        table.add_row(timestamp, speaker, message)
    
    console.print(table)
    console.print()


def display_help():
    """Display help information."""
    help_text = Text()
    help_text.append("🤖 chatty Commands:\n\n", style="bold cyan")
    help_text.append("• ", style="bright_blue")
    help_text.append("General chat: ", style="bold")
    help_text.append("Just type anything!\n", style="white")
    help_text.append("• ", style="bright_blue")
    help_text.append("Ask for time: ", style="bold")
    help_text.append("'what time is it?'\n", style="white")
    help_text.append("• ", style="bright_blue")
    help_text.append("Tell a joke: ", style="bold")
    help_text.append("'tell me a joke'\n", style="white")
    help_text.append("• ", style="bright_blue")
    help_text.append("View history: ", style="bold")
    help_text.append("'history'\n", style="white")
    help_text.append("• ", style="bright_blue")
    help_text.append("Exit: ", style="bold")
    help_text.append("'bye', 'exit', or 'quit'\n", style="white")
    
    console.print(Panel(help_text, title="📖 Help", border_style="blue"))
    console.print()


@click.command()
@click.option('--name', '-n', help='Your name for a personalized experience')
@click.option('--quiet', '-q', is_flag=True, help='Start in quiet mode (no welcome message)')
@click.version_option(version="0.1.0", prog_name="ychatty")
def main(name: Optional[str], quiet: bool):
    """
    🎉 ychatty - A simple and friendly command-line chat interface!
    
    Start a delightful conversation with your CLI companion.
    """
    bot = ChattyBot()
    
    if name:
        bot.user_name = name
    
    if not quiet:
        display_welcome()
        if name:
            console.print(f"👋 Nice to meet you, {name}!", style="bold green")
            console.print()
    
    try:
        while True:
            # Get user input with a nice prompt
            user_input = Prompt.ask(
                f"[bold cyan]{'You' if not name else name}[/bold cyan]",
                default=""
            )
            
            if not user_input.strip():
                continue
            
            # Handle special commands
            if user_input.lower().strip() in ['bye', 'goodbye', 'exit', 'quit']:
                response = bot.get_response(user_input)
                console.print(f"[bold magenta]chatty:[/bold magenta] {response}")
                bot.add_to_history("chatty", response)
                break
            
            if user_input.lower().strip() == 'history':
                display_history(bot)
                continue
            
            if user_input.lower().strip() == 'help':
                display_help()
                continue
            
            # Add user message to history
            bot.add_to_history(name or "You", user_input)
            
            # Show thinking animation
            bot.simulate_thinking()
            
            # Get and display response
            response = bot.get_response(user_input)
            console.print(f"[bold magenta]chatty:[/bold magenta] {response}")
            bot.add_to_history("chatty", response)
            console.print()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye! Thanks for chatting![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]❌ An error occurred: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()