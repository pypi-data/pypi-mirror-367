#!/usr/bin/env python3
"""
File Processor - A comprehensive example using YAPP

This example demonstrates:
- File operations (read, write, transform)
- Class-based processors
- Dictionary tree organization
- Both CLI and web interfaces
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import yaapp
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

# Create yapp application
app = Yaapp()


# File utilities as individual functions
@app.expose
def read_file(filepath: str) -> str:
    """Read content from a text file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@app.expose
def write_file(filepath: str, content: str) -> str:
    """Write content to a text file."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to '{filepath}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@app.expose
def list_files(directory: str = ".", pattern: str = "*") -> List[str]:
    """List files in a directory matching a pattern."""
    try:
        path = Path(directory)
        if not path.exists():
            return [f"Error: Directory '{directory}' does not exist"]

        files = [str(f) for f in path.glob(pattern) if f.is_file()]
        return (
            files
            if files
            else [f"No files matching '{pattern}' found in '{directory}'"]
        )
    except Exception as e:
        return [f"Error listing files: {str(e)}"]


# Text processor class
@app.expose
class TextProcessor:
    """Advanced text processing operations."""

    def word_count(self, text: str) -> Dict[str, int]:
        """Count words in text."""
        words = text.lower().split()
        word_count = {}
        for word in words:
            # Remove basic punctuation
            clean_word = word.strip('.,!?;:"()[]')
            if clean_word:
                word_count[clean_word] = word_count.get(clean_word, 0) + 1
        return word_count

    def line_count(self, text: str) -> int:
        """Count lines in text."""
        return len(text.splitlines())

    def char_count(self, text: str, include_spaces: bool = True) -> int:
        """Count characters in text."""
        return len(text) if include_spaces else len(text.replace(" ", ""))

    def reverse_text(self, text: str) -> str:
        """Reverse the text."""
        return text[::-1]

    def upper_case(self, text: str) -> str:
        """Convert text to uppercase."""
        return text.upper()

    def title_case(self, text: str) -> str:
        """Convert text to title case."""
        return text.title()


# File format converters
def json_to_csv(json_data: str) -> str:
    """Convert JSON data to CSV format."""
    try:
        data = json.loads(json_data)
        if not isinstance(data, list):
            return "Error: JSON must be a list of objects for CSV conversion"

        if not data:
            return "Error: Empty data"

        # Get headers from first object
        headers = list(data[0].keys())

        # Create CSV
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

        return output.getvalue()
    except json.JSONDecodeError:
        return "Error: Invalid JSON format"
    except Exception as e:
        return f"Error converting JSON to CSV: {str(e)}"


def csv_to_json(csv_data: str) -> str:
    """Convert CSV data to JSON format."""
    try:
        import io

        input_stream = io.StringIO(csv_data)
        reader = csv.DictReader(input_stream)

        result = []
        for row in reader:
            result.append(dict(row))

        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error converting CSV to JSON: {str(e)}"


def text_statistics(content: str) -> Dict[str, Any]:
    """Generate comprehensive text statistics."""
    lines = content.splitlines()
    words = content.split()

    return {
        "total_characters": len(content),
        "total_characters_no_spaces": len(content.replace(" ", "")),
        "total_words": len(words),
        "total_lines": len(lines),
        "average_words_per_line": len(words) / len(lines) if lines else 0,
        "longest_line": max(len(line) for line in lines) if lines else 0,
        "shortest_line": min(len(line) for line in lines) if lines else 0,
        "unique_words": len(set(word.lower().strip('.,!?;:"()[]') for word in words)),
    }


# Expose additional functionality via dictionary tree
app.expose(
    {
        "converters": {
            "json_to_csv": json_to_csv,
            "csv_to_json": csv_to_json,
        },
        "analysis": {
            "text_stats": text_statistics,
            "word_frequency": lambda text: dict(
                sorted(
                    TextProcessor().word_count(text).items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
            ),  # Top 10 most frequent words
        },
        "batch": {
            "process_directory": lambda directory, operation: f"Would process all files in {directory} with {operation}",
            "backup_files": lambda source, destination: f"Would backup {source} to {destination}",
        },
    }
)

if __name__ == "__main__":
    app.run()
