# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stash VRoom is a Python library and Stash plugin that provides HereSphere support for Stash VR content. It serves as a bridge between Stash (a media organizer) and HereSphere (a VR video player), allowing users to browse their VR collection through HereSphere's interface.

## Build System and Dependencies

- Uses `setuptools` with both `pyproject.toml` and `setup.cfg` configuration
- Python 3.6+ required
- Main dependencies: `flask>=3.1.0`, `httpx>=0.28.1`, `Pillow>=11.0.0`, `psygnal>=0.13.0`, `pydantic>=2.11.7`
- Dev dependencies: `ariadne-codegen>=0.14.0`, `pytest>=8.3`
- Documentation: `sphinx>=4.0.0`, `sphinx-autobuild`

### Common Commands

**Install package in development mode:**
```bash
pip install -e .
```

**Install with dev dependencies:**
```bash
pip install -e .[dev]
```

**Run tests:**
```bash
pytest tests/
```

**Run single test:**
```bash
pytest tests/tests_jav.py::test_get_jav_info
```

**Build documentation:**
```bash
cd doc && make html
```

**Generate GraphQL client:**
```bash
ariadne-codegen
```
Regenerates the Stash GraphQL client in `stash_vroom/stash_client/` from `stash_vroom/queries.graphql`. Requires a running Stash instance at `http://localhost:9999` and `STASH_API_KEY` environment variable set.

## Architecture

### Core Modules

**`stash_vroom/heresphere.py`** - Main Flask-like interface for building HereSphere services
- Provides decorators for handling HereSphere events (`on_play`, `on_pause`, `on_stars`, etc.)
- Manages scene filters, libraries, and tag mapping
- Uses `psygnal` for event handling

**`stash_vroom/stash.py`** - Stash API integration
- Handles connection to Stash GraphQL API
- Manages API keys and authentication
- Provides utilities for Stash data access

**`stash_vroom/jav.py`** - JAV (Japanese Adult Video) file detection and parsing
- Pattern matching for JAV filenames (e.g., "CBIKMV-068", "DANDYHQVR-011-B")
- Extracts studio, series numbers, and part information
- Excludes year-based false positives (2010-2030)

**`stash_vroom/slr.py`** - SLR network file detection
- Identifies files downloaded from SLR and related VR sites
- Extracts metadata from SLR download filenames

**`stash_vroom/util.py`** - Common utilities
- Video file pattern matching (`get_vid_re()`)
- General helper functions

**`stash_vroom/stash_client/`** - Generated GraphQL client
- Auto-generated from `queries.graphql` using `ariadne-codegen`
- Contains all Stash API interaction code

**`plugin/`** - Stash plugin implementation
- `plugin/py/runner.py` - Main plugin entry point
- `plugin/ui/` - React-based UI components for Stash plugin interface

### Data Flow

1. **Stash Integration**: Plugin connects to Stash GraphQL API using generated client
2. **Content Mapping**: Stash Saved Filters → HereSphere Libraries, Scene Tags → HereSphere Tags
3. **File Processing**: JAV and SLR modules detect and parse specialized video file formats
4. **HereSphere Service**: Flask-based service serves content in HereSphere-compatible format

### Key Design Principles

- **Transparency**: HereSphere reflects Stash content directly - no separate database
- **Event-driven**: Uses `psygnal` for handling user interactions (play, pause, rating, etc.)
- **Plugin Architecture**: Designed as a Stash plugin for easy installation
- **File Format Support**: Specialized handling for JAV and SLR VR content

## Testing

Tests are in `tests/` directory:
- `tests_jav.py` - JAV filename parsing tests with extensive test cases
- `tests_util.py` - Utility function tests

Test files include comprehensive examples of expected JAV filename patterns and edge cases.

## Documentation

- Full documentation built with Sphinx in `doc/` directory
- Published at https://zyquon.github.io/stash-vroom/
- Includes design philosophy, user guide, and API cookbook