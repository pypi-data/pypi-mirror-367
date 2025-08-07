#!/usr/bin/env python3
"""
Demo script to showcase ychatty functionality.
"""

import subprocess
import sys
import time


def run_ychatty_command(args, input_text=None):
    """Run ychatty with given arguments and input."""
    cmd = ["uv", "run", "ychatty"] + args
    
    try:
        if input_text:
            result = subprocess.run(
                cmd, 
                input=input_text, 
                text=True, 
                capture_output=True, 
                timeout=10
            )
        else:
            result = subprocess.run(
                cmd, 
                text=True, 
                capture_output=True, 
                timeout=10
            )
        
        print(f"Command: {' '.join(cmd)}")
        if input_text:
            print(f"Input: {repr(input_text)}")
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        print("-" * 50)
        
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(cmd)}")
    except Exception as e:
        print(f"Error running command: {e}")


def main():
    """Run demo commands."""
    print("🎉 ychatty Demo")
    print("=" * 50)
    print()
    
    # Show help
    print("📖 Help Command:")
    run_ychatty_command(["--help"])
    
    # Show version
    print("📋 Version Command:")
    run_ychatty_command(["--version"])
    
    # Show quiet mode with name
    print("🤫 Quiet Mode with Name:")
    run_ychatty_command(
        ["--quiet", "--name", "Demo"], 
        "hello\\nwhat time is it?\\ntell me a joke\\nbye\\n"
    )
    
    print("✨ Demo completed!")
    print()
    print("To try ychatty interactively, run:")
    print("  uv run ychatty")
    print("  uv run ychatty --name YourName")


if __name__ == "__main__":
    main()