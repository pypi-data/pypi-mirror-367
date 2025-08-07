"""Simple port availability checking."""

import socket
from .result import Result, Ok


def find_available_port(start_port: int = 8000, end_port: int = 9000, host: str = 'localhost') -> Result[int]:
    """Find first available port in range."""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((host, port))
                return Ok(port)
        except (socket.error, OSError):
            continue
    return Result.error(f"No available ports in range {start_port}-{end_port}")