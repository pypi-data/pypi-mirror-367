# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pycaddy** is a Python automation toolkit with utilities for experiment tracking, parameter sweeping, and structured file organization. The codebase is organized into distinct modules for different automation tasks.

## Key Architecture Components

### Core Modules

- **Project/Session System** (`src/pycaddy/project/`): Provides a structured way to organize experiments with automatic folder creation and metadata tracking
- **Ledger** (`src/pycaddy/ledger/`): JSON-based experiment tracking system that maintains run records with status, parameters, and file artifacts
- **Sweeper** (`src/pycaddy/sweeper/`): Parameter space exploration tools for generating combinations of experiment configurations
- **Dictionary Utilities** (`src/pycaddy/dict_utils/`): Utilities for flattening, unflattening, hashing, and manipulating nested dictionaries
- **Load/Save Utilities** (`src/pycaddy/load/`, `src/pycaddy/save/`): File I/O helpers for JSON and figure saving

### Key Design Patterns

- **Singleton Pattern**: The Ledger uses `PerPathSingleton` to ensure one instance per metadata file per process
- **Pydantic Models**: Extensive use of Pydantic for data validation and serialization (Project, Session, RunRecord)
- **Context Managers**: File locking and data editing operations use context managers for safe concurrent access
- **Strategy Pattern**: Sweeper module uses pluggable strategies for parameter combination generation

### Data Flow

1. **Project** creates structured folders and manages a shared **Ledger**
2. **Session** represents individual experiment runs with unique UIDs
3. **Ledger** persists run metadata to `metadata.json` with file-based locking
4. **Sweeper** generates parameter combinations for batch experiments
5. Status tracking: `PENDING` → `RUNNING` → `DONE`/`ERROR`

## Development Commands

### Testing
```bash
python -m pytest tests/
python -m pytest tests/test_specific_module.py  # Run specific test file
python -m pytest -v  # Verbose output
```

### Package Installation
```bash
pip install -e .  # Development installation
```

The project uses pytest for testing with fixtures defined in `tests/conftest.py` for Ledger and Project instances.

## Important Implementation Details

- **File Locking**: Ledger uses `filelock.FileLock` for concurrent access safety
- **Path Handling**: All paths are normalized and made absolute internally
- **Storage Modes**: Sessions support `SUBFOLDER` (default) or `PREFIX` file organization
- **Resume Logic**: Projects can automatically resume existing runs based on parameter hashes
- **UID Generation**: Uses zero-padded counters for unique run identifiers within each (identifier, relpath) scope

## Dependencies

Core dependencies include `pydantic>=2.6.4`, `filelock>=3.18.0`, `matplotlib`, `pint`, and `pytest`.