# CLAUDE.md

#Enviroment

Python3.10+
venv must always be used
follow modern python coding standards
commit frequently with well documented messages

## Commands

 Available Tools:
1. scratchpad-multi.sh - Task tracking with multi-agent support (use --agent <name> for agent-specific work)
2. knowledge.sh - Knowledge base with private/shared storage (use --agent <name> for agent-specific work)
3. codemap.sh - Lightweight code intelligence for instant roadmaps
4. context.sh - Context gathering for debugging issues
5. researcher.sh - Online research and multimodal analysis via OpenRouter API

📖 Full workflow guide: see llm-agent-tools/agent_tools_prompt.xml

For new feature YOU MUST folow this flow

- **Start outside-in:** write a failing acceptance test that expresses the user story before any implementation.
- **Go green fast:** add the bare-minimum code to pass that test, nothing more.
- **Drive design with micro tests:** for every behavior (validation, calc, expiry, limits) add a failing unit test, then implement until green.
- **Refactor on green:** once all tests pass, split messy code into clear components (service, repo, calculator, tracker) while keeping the suite green.
- **Edge-case first mindset:** write tests for expiry, usage caps, and discount > total _before_ handling them; implementation follows the tests.
- **Rinse & repeat:** keep iterations small, commit only green code, and let the tests guard future changes.


# Run linting (ruff)
make lint

# Run tests
make test                    # Run all tests via Makefile
pytest tests/                # Run all tests directly
pytest tests/test_import.py  # Run single test file
pytest -k "test_name"        # Run specific test by name
pytest -m "not slow"         # Skip slow tests

# Run tests with coverage
make coverage

# Build distribution packages
make build

# Clean build artifacts
make clean

# Run the application
make run                     # Or: python -m tunacode
```

#
## Architecture

TunaCode is a CLI tool that provides an AI-powered coding assistant using pydantic-ai. Key architectural decisions:

### Agent System

- Uses `pydantic-ai` for LLM agent implementation
- Central agent in `src/tunacode/core/agents/main.py` with retryable tools
- Supports multiple LLM providers (Anthropic, OpenAI, Google, OpenRouter) through unified interface
- Model format: `provider:model-name` (e.g., `openai:gpt-4`, `anthropic:claude-3-opus`)
- Background task management via `core/background/manager.py`

### Tool System

Seven internal tools with confirmation UI:

1. `read_file` - Read file contents with line numbers
2. `write_file` - Create new files (fails if exists)
3. `update_file` - Update existing files with target/patch pattern
4. `run_command` - Execute shell commands
5. `bash` - Execute bash commands with enhanced capabilities
6. `grep` - Fast file content searching using regex patterns (3-second first match deadline)
7. `list_dir` - Efficient directory listing without shell commands

Tools extend `BaseTool` or `FileBasedTool` base classes. External tools supported via MCP (Model Context Protocol) through `services/mcp.py`.

### State Management

- `StateManager` (core/state.py) maintains all session state
- Includes user config, agent instances, message history, costs, permissions
- Single source of truth passed throughout the application
- Code indexing system in `core/code_index.py` for codebase understanding

### Command System

- Command registry pattern in `cli/commands.py`
- Commands implement `BaseCommand` with `matches()` and `execute()` methods
- Registered via `@CommandRegistry.register` decorator
- Shell command execution with `!` prefix (e.g., `!ls`)
- Available commands: `/help`, `/model`, `/clear`, `/compact`, `/branch`, `/yolo`, `/update`, `/exit`, `/thoughts`

### Parallel Tool Execution

- Read-only tools (read_file, grep, list_dir) execute in parallel for 3x performance improvement
- Write/execute tools remain sequential for safety
- Enhanced visual feedback when `/thoughts on` is enabled:
  - Clear batch headers: "🚀 PARALLEL BATCH #X: Executing Y read-only tools concurrently"
  - Detailed tool listing with arguments for each batch
  - Sequential warnings for write/execute tools: "⚠️ SEQUENTIAL: tool_name (write/execute tool)"
  - Completion confirmations: "✅ Parallel batch completed successfully"
- Controlled by `TUNACODE_MAX_PARALLEL` environment variable (defaults to CPU count)
- Automatic batching of consecutive read-only tools
- Read-only tools skip confirmation prompts automatically

### Setup Coordinator

Modular setup with validation steps:

1. Environment detection (API keys)
2. Model validation
3. Configuration setup (`~/.config/tunacode.json`)
4. Git safety checks
   Each step implements `BaseSetupStep` interface.

### UI Components

- REPL uses `prompt_toolkit` for multiline input with syntax highlighting
- Output formatting via `rich` library
- Tool confirmations show diffs for file operations
- Spinner during agent processing

## Testing

### Test Organization

- Unit tests for individual components
- Integration tests for system interactions
- Characterization tests for capturing existing behavior
- Async tests using `@pytest.mark.asyncio`



### User Configuration

Location: `~/.config/tunacode.json`

```json
{
  "default_model": "provider:model-name",
  "env": {
    "ANTHROPIC_API_KEY": "...",
    "OPENAI_API_KEY": "..."
  }
}
```


## Key Design Patterns

### Error Handling

- Custom exceptions in `exceptions.py`
- `ModelRetry` from pydantic-ai for retryable errors
- Graceful degradation for missing features

### Permissions

- File operation permissions tracked per session
- "Yolo mode" to skip confirmations: `/yolo`
- Permissions stored in StateManager

### Async Architecture

- All agent operations are async
- Tool executions use async/await
- REPL handles async with prompt_toolkit integration

### Performance Optimizations

- Grep tool uses fast-glob prefiltering with MAX_GLOB limit
- 3-second deadline for first match in searches
- Background task management for non-blocking operations
