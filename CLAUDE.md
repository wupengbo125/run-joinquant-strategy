# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python automation tool for running quantitative trading strategies on JoinQuant (聚宽) platform. The tool uses Playwright to automate browser interactions, managing login state and extracting error messages from strategy executions.

## Architecture

The project consists of several interconnected components:

### Core Scripts
- `login_save.py` - Handles initial authentication and stores login state in `auth_state.json`
- `access_algorithm.py` - Main automation script that runs strategies and extracts error messages
- `browser_utils.py` - Browser management utilities with Chrome detection and isolated browser creation
- `browser_manager.py` - CLI tool for managing browser data (backup, restore, reset)

### Browser Architecture
The system creates an isolated browser instance using user's Chrome browser with a dedicated data directory (`joinquant_browser_data/`). This ensures:
- Separation from user's daily browser
- Persistent login state across runs
- Cross-platform Chrome detection (Windows, macOS, Linux)

### Strategy Execution Flow
1. Load saved authentication state from `auth_state.json`
2. Create isolated browser context using user's Chrome
3. Navigate to JoinQuant algorithm page
4. Paste strategy code into Ace Editor using multiple fallback methods
5. Click compile/run button
6. Wait 20 seconds for execution
7. Extract only error messages using JavaScript injection
8. Auto-close browser

## Common Commands

### Setup
```bash
pip install -r requirements.txt
playwright install chromium
```

**Dependencies**: Only requires `playwright>=1.40.0`. The system uses the user's existing Chrome browser installation rather than downloading a separate browser.

### First-time Authentication
```bash
python login_save.py
# User manually logs in, then types 'y' to confirm
```

### Run Strategy
```bash
python access_algorithm.py strategy_file.py
```

### Browser Management
```bash
python browser_manager.py info    # View browser info and data directory
python browser_manager.py reset   # Reset browser data (requires 'yes' confirmation)
python browser_manager.py backup  # Backup browser data to timestamped directory
python browser_manager.py restore # Restore browser data from backup
python browser_manager.py clean   # Clean cache and temporary files
```

## Key Technical Details

### Authentication State
- Stored in `auth_state.json` (excluded by .gitignore)
- Contains cookies and local storage data
- Persistent across browser sessions

### Browser Isolation
- Uses `joinquant_browser_data/` directory (excluded by .gitignore)
- Cross-platform Chrome executable detection in `get_user_chrome_executable()`:
  - Windows: Checks registry paths and common locations
  - macOS: Searches `/Applications/` and standard paths
  - Linux: Looks in standard binary paths and common locations
- Launches Chrome with specific args for automation compatibility including `--no-sandbox`, `--disable-blink-features=AutomationControlled`

### Code Injection Strategy
The `paste_strategy_to_editor()` function uses multiple methods:
1. Direct Ace Editor API access via hidden textarea
2. Keyboard input through ace_text-input
3. JavaScript direct value setting
4. Clipboard-based fallback

### Error Extraction
The `read_execution_logs()` function uses JavaScript injection to:
- Target specific error containers (#log, #daily-logs-tab)
- Extract Traceback and AttributeError patterns using regex filtering
- Filter out non-error content from page using text content analysis
- Return clean error messages only, stripping execution success messages
- Uses `page.evaluate()` to execute custom JavaScript in browser context

## Strategy File Format

Strategy files must be valid Python with JoinQuant API conventions:
- `initialize(context)` - Initialization function
- `handle_data(context, data)` - Main trading logic
- Use `data[stock]['close']` instead of `data.current(stock, 'price')`
- Global variable `g` for state management

## File Structure and Data Handling

### Sensitive Data (excluded by .gitignore)
- `auth_state.json` - Browser cookies and localStorage for authentication
- `joinquant_browser_data/` - Isolated Chrome profile directory
- `chrome_debug_data/`, `browser_data/` - Alternative browser data directories
- `*.log`, `logs/` - Execution logs and temporary files

### Execution Model
- No build system - direct Python script execution
- Each script runs independently with full browser lifecycle
- Browser data persistence allows state preservation between runs
- Error messages extracted purely from browser DOM, no API calls to JoinQuant
- All browser instances auto-close after task completion