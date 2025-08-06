# MCP Background Job Server

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An MCP (Model Context Protocol) server that enables coding agents to execute long-running shell commands asynchronously with full process management capabilities.

## Overview

The MCP Background Job Server provides a robust solution for running shell commands in the background, allowing agents to start processes, monitor their status, interact with them, and manage their lifecycle. This is particularly useful for development workflows involving build processes, test suites, servers, or any long-running operations.

## Features

- **Asynchronous Process Execution**: Execute shell commands as background jobs with unique job IDs
- **Process Lifecycle Management**: Start, monitor, interact with, and terminate background processes  
- **Real-time Output Monitoring**: Capture and retrieve stdout/stderr with buffering and tailing capabilities
- **Interactive Process Support**: Send input to running processes via stdin
- **Resource Management**: Configurable job limits and automatic cleanup of completed processes
- **MCP Protocol Integration**: Full integration with Model Context Protocol for agent interactions

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

1. **Clone and navigate to the project directory:**
   ```bash
   cd mcp-background-job
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Install in development mode:**
   ```bash
   uv add -e .
   ```

## Quick Start

### Running the Server

```bash
# Run with stdio transport (most common)
uv run python -m mcp_background_job

# Or run the server module directly
uv run python src/mcp_background_job/server.py
```

### Basic Usage Example

```python
# 1. Execute a long-running command
execute_result = await execute_command("npm run dev")
job_id = execute_result.job_id

# 2. Check job status
status = await get_job_status(job_id)
print(f"Job status: {status.status}")

# 3. Get recent output
output = await tail_job_output(job_id, lines=20)
print("Recent output:", output.stdout)

# 4. Interact with the process
interaction = await interact_with_job(job_id, "some input\n")
print("Process response:", interaction.stdout)

# 5. Kill the job when done
result = await kill_job(job_id)
print(f"Kill result: {result.status}")
```

## MCP Tools Reference

The server exposes 7 MCP tools for process management:

### Read-only Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `list` | List all background jobs | None | `{jobs: [JobSummary]}` |
| `status` | Get job status | `job_id: str` | `{status: JobStatus}` |
| `output` | Get complete job output | `job_id: str` | `{stdout: str, stderr: str}` |
| `tail` | Get recent output lines | `job_id: str, lines: int` | `{stdout: str, stderr: str}` |

### Interactive Tools

| Tool | Description | Parameters | Returns |
|------|-------------|------------|---------|
| `execute` | Start new background job | `command: str` | `{job_id: str}` |
| `interact` | Send input to job stdin | `job_id: str, input: str` | `{stdout: str, stderr: str}` |
| `kill` | Terminate running job | `job_id: str` | `{status: str}` |

### Job Status Values

- `running` - Process is currently executing
- `completed` - Process finished successfully
- `failed` - Process terminated with error
- `killed` - Process was terminated by user

## Configuration

### Environment Variables

Configure the server behavior using these environment variables:

```bash
# Maximum concurrent jobs (default: 10)
export MCP_BG_MAX_JOBS=10

# Maximum output buffer per job (default: 10MB)
export MCP_BG_MAX_OUTPUT_SIZE=10485760

# Default job timeout in seconds (default: no timeout)
export MCP_BG_JOB_TIMEOUT=3600

# Cleanup interval for completed jobs in seconds (default: 300)
export MCP_BG_CLEANUP_INTERVAL=300
```

### Programmatic Configuration

```python
from mcp_background_job.config import BackgroundJobConfig

config = BackgroundJobConfig(
    max_concurrent_jobs=20,
    max_output_size_bytes=20 * 1024 * 1024,  # 20MB
    default_job_timeout=7200,  # 2 hours
    cleanup_interval_seconds=600  # 10 minutes
)
```

## Architecture

The server is built with a modular architecture:

- **JobManager**: Central service for job lifecycle management
- **ProcessWrapper**: Abstraction layer for subprocess handling with I/O buffering
- **FastMCP Server**: MCP protocol implementation with tool definitions
- **Pydantic Models**: Type-safe data validation and serialization

### Key Components

```
src/mcp_background_job/
├── server.py          # FastMCP server and tool definitions
├── service.py         # JobManager service implementation  
├── process.py         # ProcessWrapper for subprocess management
├── models.py          # Pydantic data models
├── config.py          # Configuration management
└── logging_config.py  # Logging setup
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run unit tests only
uv run pytest tests/unit/ -v

# Run integration tests only  
uv run pytest tests/integration/ -v
```

### Code Formatting

```bash
# Format code with ruff
uv run ruff format

# Run type checking
uv run mypy src/
```

### Development Workflow

1. Make your changes
2. Run tests: `uv run pytest tests/`
3. Format code: `uv run ruff format`
4. Commit changes

## Examples

### Development Server Workflow

```bash
# Start a development server
job_id=$(echo '{"command": "npm run dev"}' | mcp-tool execute)

# Monitor the startup
mcp-tool tail --job_id "$job_id" --lines 10

# Check if server is ready
mcp-tool status --job_id "$job_id"

# Stop the server
mcp-tool kill --job_id "$job_id"
```

### Long-running Build Process

```bash
# Start a build process
job_id=$(echo '{"command": "docker build -t myapp ."}' | mcp-tool execute)

# Monitor build progress
while true; do
  status=$(mcp-tool status --job_id "$job_id")
  if [[ "$status" != "running" ]]; then break; fi
  mcp-tool tail --job_id "$job_id" --lines 5
  sleep 10
done

# Get final build output
mcp-tool output --job_id "$job_id"
```

### Interactive Process Example

```bash
# Start Python REPL
job_id=$(echo '{"command": "python -i"}' | mcp-tool execute)

# Send Python code
mcp-tool interact --job_id "$job_id" --input "print('Hello, World!')\n"

# Send more commands
mcp-tool interact --job_id "$job_id" --input "import sys; print(sys.version)\n"

# Exit REPL
mcp-tool interact --job_id "$job_id" --input "exit()\n"
```

## Security Considerations

- **Process Isolation**: Each job runs as a separate subprocess
- **Resource Limits**: Configurable limits on concurrent jobs and memory usage  
- **Input Validation**: All parameters are validated using Pydantic models
- **Command Restrictions**: Consider implementing command allowlists in production
- **Output Sanitization**: Be aware that process output may contain sensitive information

## Transport Support

The server supports multiple MCP transports:

- **stdio**: Default transport for local development and agent integration
- **HTTP**: For remote access (requires additional setup)

For stdio transport, ensure logging goes to stderr only to avoid protocol conflicts.

## Troubleshooting

### Common Issues

**Import Errors**: Ensure the package is installed in development mode:
```bash
uv add -e .
```

**Tests Not Running**: Install the package first, then run tests:
```bash
uv sync
uv add -e .
uv run pytest tests/
```

**Permission Errors**: Ensure proper permissions for the commands you're trying to execute.

**Memory Issues**: Adjust `MCP_BG_MAX_OUTPUT_SIZE` if dealing with processes that generate large amounts of output.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite and formatting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.1.0
- Initial implementation with full MCP tool support
- Process lifecycle management
- Configurable resource limits
- Comprehensive test suite

---

Built with ❤️ using [FastMCP](https://github.com/jlowin/fastmcp) and Python 3.12+