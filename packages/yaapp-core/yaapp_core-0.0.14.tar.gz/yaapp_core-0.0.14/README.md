# yaapp-core

**Universal function interface** - write once, use everywhere

yaapp transforms Python functions into multiple interfaces. Currently generates CLI from function signatures, with web APIs planned.

## Value Proposition

Instead of writing separate CLI scripts and web endpoints, write functions once and expose them through any interface. yaapp handles argument parsing, validation, and execution - you focus on business logic.

## Implementation Status

**Working**: CLI generation via Click ([`src/yaapp/`](src/yaapp/))  
**Planned**: FastAPI web APIs, enhanced plugins, additional runners

## Resources

- **[`docs/`](docs/)** - Architecture and design documentation
- **[`src/yaapp/`](src/yaapp/)** - Core implementation
- **[Current state](docs/current-state.md)** - What works vs what's planned

## Quick Setup

```bash
uv sync && python -m yaapp --help
```