"""
Configuration for yaapp static analysis.
"""

from typing import Set, List, Dict, Any
from dataclasses import dataclass


@dataclass
class AnalysisConfig:
    """Configuration for static analysis rules."""
    
    # Foreign libraries that are allowed in try/except blocks
    allowed_foreign_libraries: Set[str] = None
    
    # Internal yaapp modules (try/except around these is forbidden)
    internal_modules: Set[str] = None
    
    # Specific exceptions that are always allowed
    allowed_exceptions: Set[str] = None
    
    # Files/directories to exclude from analysis
    exclude_patterns: List[str] = None
    
    # Whether to allow bare except clauses
    allow_bare_except: bool = False
    
    # Whether to allow broad Exception catching
    allow_broad_except: bool = False
    
    def __post_init__(self):
        """Initialize default values."""
        if self.allowed_foreign_libraries is None:
            self.allowed_foreign_libraries = {
                # HTTP/Network libraries
                'requests', 'httpx', 'aiohttp', 'urllib', 'urllib3',
                
                # Web frameworks
                'fastapi', 'flask', 'django', 'starlette',
                
                # CLI libraries  
                'click', 'typer', 'argparse',
                
                # Data libraries
                'json', 'yaml', 'toml', 'csv', 'xml',
                
                # System libraries
                'os', 'sys', 'subprocess', 'pathlib', 'shutil',
                
                # Async libraries
                'asyncio', 'concurrent.futures', 'threading',
                
                # Database libraries
                'sqlite3', 'psycopg2', 'pymongo', 'redis',
                
                # Other common libraries
                'datetime', 'time', 'random', 'uuid', 'hashlib',
                'logging', 'configparser', 'tempfile', 'zipfile',
                
                # Third-party packages
                'pydantic', 'sqlalchemy', 'alembic', 'celery',
                'pytest', 'unittest', 'mock',
            }
        
        if self.internal_modules is None:
            self.internal_modules = {
                'yaapp', 'yaapp.core', 'yaapp.app', 'yaapp.config',
                'yaapp.reflection', 'yaapp.exposers', 'yaapp.runners',
                'yaapp.plugins', 'yaapp.result', 'yaapp.async_compat',
                'yaapp.unified_cli_builder', 'yaapp.cli_builder',
            }
        
        if self.allowed_exceptions is None:
            self.allowed_exceptions = {
                # System exceptions that should always be allowed
                'KeyboardInterrupt', 'SystemExit', 'GeneratorExit',
                
                # Import exceptions (for optional dependencies)
                'ImportError', 'ModuleNotFoundError',
                
                # File system exceptions (for external file operations)
                'FileNotFoundError', 'PermissionError', 'OSError', 'IOError',
                
                # Network exceptions (for external API calls)
                'ConnectionError', 'TimeoutError', 'socket.error',
                
                # JSON/parsing exceptions (for external data)
                'json.JSONDecodeError', 'ValueError', 'TypeError',
                
                # HTTP exceptions (for external API calls)
                'requests.RequestException', 'httpx.RequestError',
            }
        
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                'tests/*',           # Test files can have more relaxed rules
                'examples/*',        # Example files can have more relaxed rules
                'tools/*',           # Tool files can have more relaxed rules
                '**/test_*.py',      # Test files
                '**/*_test.py',      # Test files
                'setup.py',          # Setup script
                'conftest.py',       # Pytest configuration
            ]


# Default configuration instance
DEFAULT_CONFIG = AnalysisConfig()


def load_config(config_file: str = None) -> AnalysisConfig:
    """Load configuration from file or return default."""
    if config_file:
        # TODO: Implement config file loading (YAML/JSON)
        pass
    
    return DEFAULT_CONFIG