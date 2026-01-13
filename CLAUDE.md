# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Stash VRoom is a multi-language library (Python and TypeScript) and Stash plugin that provides HereSphere support for Stash VR content. It serves as a bridge between Stash (a media organizer) and HereSphere (a VR video player), allowing users to browse their VR collection through HereSphere's interface.

The project provides utilities in both Python (`stash_vroom/`) and TypeScript (`js/`) for detecting and parsing VR video file formats (JAV, SLR).

## Build System and Dependencies

### Python (`stash_vroom/`)

- Uses `setuptools` with both `pyproject.toml` and `setup.cfg` configuration
- Python 3.6+ required
- Main dependencies: `flask>=3.1.0`, `httpx>=0.28.1`, `Pillow>=11.0.0`, `psygnal>=0.13.0`, `pydantic>=2.11.7`
- Dev dependencies: `ariadne-codegen>=0.14.0`, `pytest>=8.3`
- Documentation: `sphinx>=4.0.0`, `sphinx-autobuild`

### TypeScript (`js/`)

- npm package named `stash-vroom`
- ES modules (`"type": "module"`)
- Dev dependencies: `typescript>=5.3.0`, `vitest>=2.0.0`
- Builds to `js/dist/` with `.js` and `.d.ts` type declarations

### Common Commands (Python)

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

### Common Commands (TypeScript)

**Install dependencies:**
```bash
cd js && npm install
```

**Run tests:**
```bash
cd js && npm test
```

**Run tests in watch mode:**
```bash
cd js && npm run test:watch
```

**Build package:**
```bash
cd js && npm run build
```
Compiles TypeScript to `js/dist/` with type declarations.

**Build browser bundle:**
```bash
cd js && npm run build:browser
```
Creates `js/dist/stash-vroom.browser.js` - a standalone IIFE bundle for use in browsers and extensions. This file exposes `window.StashVroom` with all exports.

**Build everything:**
```bash
cd js && npm run build:all
```
Runs both TypeScript compilation and browser bundle generation.

### Browser Bundle

The browser bundle (`js/dist/stash-vroom.browser.js`) is a self-contained file for non-module environments like Chrome extensions. It:

- Combines all modules (util, slr, jav) into a single file
- Wraps everything in an IIFE to avoid polluting global scope
- Exposes `window.StashVroom` with these functions:
  - `getJavInfo(filepath)` - Extract JAV metadata
  - `getIsJav(filepath)` - Check if file is JAV
  - `matchJavFilename(filename)` - Low-level JAV regex matching
  - `getSlrInfo(filepath)` - Extract SLR metadata
  - `getIsSlr(filepath)` - Check if file is SLR
  - `getSlrRe(options)` - Generate SLR regex
  - `getVidRe(extensions)` - Video extension regex
  - `basename(filepath)` - Cross-platform basename

**Downstream usage (e.g., companion project):**
```bash
cp /path/to/stash-vroom/js/dist/stash-vroom.browser.js extension/stash-vroom.js
```

The browser bundle should be regenerated whenever the TypeScript source changes.

## Architecture

### Core Modules (Python)

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

### Core Modules (TypeScript)

**`js/src/jav.ts`** - JAV file detection and parsing (TypeScript port of `jav.py`)
- `getJavInfo(filepath)` - Extract JAV metadata from filename
- `getIsJav(filepath)` - Check if file is a JAV
- `matchJavFilename(filename)` - Low-level regex matching

**`js/src/slr.ts`** - SLR network file detection (TypeScript port of `slr.py`)
- `getSlrInfo(filepath)` - Extract SLR metadata from filename
- `getIsSlr(filepath)` - Check if file is an SLR download
- `getSlrRe(options)` - Generate SLR matching regex

**`js/src/util.ts`** - Common utilities
- `getVidRe(extensions)` - Video file extension regex
- `basename(filepath)` - Cross-platform path basename

**`js/src/index.ts`** - Public API re-exports all modules

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

### Python Tests

Tests are in `tests/` directory:
- `tests_jav.py` - JAV filename parsing tests with extensive test cases
- `tests_util.py` - Utility function tests

### TypeScript Tests

Tests are in `js/tests/` directory:
- `jav.test.ts` - JAV filename parsing tests (mirrors `tests_jav.py`)

Both test suites cover the same 38 JAV filename test cases to ensure parity between Python and TypeScript implementations.

## Documentation

- Full documentation built with Sphinx in `doc/` directory
- Published at https://zyquon.github.io/stash-vroom/
- Includes design philosophy, user guide, and API cookbook