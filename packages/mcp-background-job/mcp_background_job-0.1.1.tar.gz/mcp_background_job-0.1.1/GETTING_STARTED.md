# Getting Started with MCP Background Job Server

This guide will walk you through setting up and using the MCP Background Job Server with Claude Code for asynchronous command execution.

## What You'll Achieve

By the end of this guide, you'll be able to:
- Execute long-running commands in the background while continuing to work with Claude
- Monitor command progress and output in real-time
- Interact with running processes (send input to stdin)
- Manage multiple concurrent background jobs
- Kill or control running processes as needed

## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured

## Step 1: Install the MCP Background Job Server

### 1.1 Clone or Navigate to the Project

If you don't already have the project:
```bash
git clone <repository-url>
cd mcp-background-job
```

Or if you already have it:
```bash
cd path/to/mcp-background-job
```

### 1.2 Install Dependencies

```bash
# Install all dependencies and set up the virtual environment
uv sync

# Verify installation works
uv run python -c "import mcp_background_job; print('✅ Installation successful')"
```

### 1.3 Test the Server (Optional)

```bash
# Run tests to ensure everything works
uv run pytest tests/unit/test_models.py -v

# You should see: "10 passed" if everything is working
```

## Step 2: Configure Claude Code to Use the MCP Server

### 2.1 Add Server to Claude Code Configuration

Add the MCP Background Job Server to your Claude Code configuration. The exact method depends on your setup:

**Option A: Using Claude Code Desktop**
1. Open Claude Code settings/preferences
2. Navigate to MCP Servers section
3. Add a new server with:
   - **Name**: `background-job`
   - **Command**: `uv`
   - **Args**: `["run", "python", "-m", "mcp_background_job"]`
   - **Working Directory**: `/path/to/mcp-background-job`

**Option B: Using Configuration File**
Add to your Claude Code configuration file (typically `~/.claude/config.json` or similar):
```json
{
  "mcpServers": {
    "background-job": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_background_job"],
      "cwd": "/path/to/mcp-background-job"
    }
  }
}
```

**Option C: Direct Command Line (for testing)**
```bash
# Run the server directly (useful for debugging)
cd /path/to/mcp-background-job
uv run python -m mcp_background_job
```

### 2.2 Restart Claude Code

After adding the server configuration, restart Claude Code to load the new MCP server.

### 2.3 Verify Connection

In Claude Code, you should now see the background job tools available. You can verify by asking Claude:

> "What MCP tools do you have available for background jobs?"

Claude should respond with information about these 7 tools:
- `execute` - Start new background job
- `list` - List all background jobs
- `status` - Get job status
- `output` - Get complete job output
- `tail` - Get recent output lines
- `interact` - Send input to job
- `kill` - Terminate job

## Step 3: Basic Usage Examples

### 3.1 Execute Your First Background Job

Ask Claude to run a simple command:

> "Please execute 'echo Hello from background job' as a background job and show me the result"

Claude will:
1. Use the `execute` tool to start the job
2. Get a job ID back (e.g., `abc123-def456-...`)
3. Check the job status
4. Retrieve and show you the output

### 3.2 Run a Long-Running Command

Try something that takes time:

> "Start a background job that sleeps for 10 seconds, then prints 'Done sleeping'. Monitor its progress."

Claude will:
1. Execute: `sleep 10 && echo 'Done sleeping'`
2. Show you the job ID
3. Monitor the status over time
4. Show you the final output when complete

### 3.3 Monitor Multiple Jobs

> "Start three background jobs: one that counts to 10, one that lists files, and one that shows the current date. List all running jobs and their status."

### 3.4 Interactive Process Example

> "Start a Python REPL as a background job, then send it some Python code to execute"

Claude will:
1. Start: `python -i`
2. Use the `interact` tool to send Python commands
3. Show you the responses

## Step 4: Advanced Usage Patterns

### 4.1 Development Server Workflow

> "I want to start my development server in the background and monitor it. Start 'npm run dev' and show me the startup logs."

This is perfect for:
- Starting development servers (React, Node.js, etc.)
- Running build processes
- Monitoring file watchers

### 4.2 Long-Running Build Process

> "Start a Docker build in the background and periodically check its progress: 'docker build -t myapp .'"

### 4.3 File Processing Tasks

> "Process all .txt files in the current directory with a background job that counts words in each file"

### 4.4 Testing and CI Tasks

> "Run my test suite in the background and let me know when it's done: 'npm test'"

## Step 5: Configuration Options

### 5.1 Environment Variables

You can customize the server behavior with these environment variables:

```bash
# Maximum concurrent jobs (default: 10)
export MCP_BG_MAX_JOBS=20

# Maximum output buffer per job (default: 10MB)
export MCP_BG_MAX_OUTPUT_SIZE=20971520  # 20MB in bytes
# or with MB suffix:
export MCP_BG_MAX_OUTPUT_SIZE=20MB

# Job timeout in seconds (default: no timeout)
export MCP_BG_JOB_TIMEOUT=3600  # 1 hour

# Cleanup interval for completed jobs (default: 300 seconds)
export MCP_BG_CLEANUP_INTERVAL=600  # 10 minutes

# Allowed command patterns (optional security restriction)
export MCP_BG_ALLOWED_COMMANDS="^npm ,^python ,^echo ,^ls"

# Working directory for jobs (default: current directory)
export MCP_BG_WORKING_DIR="/path/to/project"
```

### 5.2 Security Configuration

For additional security, you can restrict which commands are allowed:

```bash
# Only allow specific command patterns
export MCP_BG_ALLOWED_COMMANDS="^npm run,^python script,^echo,^ls,^pwd$"
```

When this is set, only commands matching these patterns will be allowed to execute.

## Step 6: Troubleshooting

### Common Issues

**Issue**: "No MCP tools available" or "background-job server not found"
**Solution**:
- Check that the server path in your configuration is correct
- Ensure `uv sync` was run in the project directory
- Restart Claude Code after configuration changes

**Issue**: "ModuleNotFoundError: No module named 'mcp_background_job'"
**Solution**:
```bash
cd /path/to/mcp-background-job
uv sync
```

**Issue**: Commands are being blocked unexpectedly
**Solution**: Check if you have `MCP_BG_ALLOWED_COMMANDS` set. If so, ensure your command patterns match.

**Issue**: Jobs seem to hang or not respond
**Solution**:
- Use the `kill` tool to terminate stuck jobs
- Check job limits with environment variables
- Use `tail` tool to see recent output

### Debug Mode

To see detailed logging:
```bash
# Run server with debug logging
PYTHONPATH=/path/to/mcp-background-job uv run python -m mcp_background_job
```

### Testing Individual Tools

You can test the server directly:
```bash
cd /path/to/mcp-background-job
uv run python -c "
import asyncio
from mcp_background_job.service import JobManager

async def test():
    manager = JobManager()
    job_id = await manager.execute_command('echo test')
    print(f'Job ID: {job_id}')
    await asyncio.sleep(1)
    output = await manager.get_job_output(job_id)
    print(f'Output: {output.stdout}')

asyncio.run(test())
"
```

## Step 7: Best Practices

### 7.1 Command Safety
- The server blocks dangerous commands like `rm -rf /`, but always be cautious
- Use specific commands rather than complex shell scripts when possible
- Test commands in a safe environment first

### 7.2 Resource Management
- Monitor long-running jobs periodically
- Kill jobs you no longer need to free resources
- Be aware of the concurrent job limit (default: 10)

### 7.3 Output Management
- Use `tail` for monitoring progress instead of always getting full output
- Large outputs are automatically limited by buffer size (10MB default)
- For very verbose commands, consider redirecting output to files

### 7.4 Development Workflow
- Start development servers as background jobs
- Use interactive jobs for REPLs and debugging
- Monitor build processes without blocking Claude interactions
- Run tests in background while continuing development discussions

## Step 8: Example Conversation Flows

### Development Server Setup
```
You: "Help me start my React development server and monitor it"

Claude: "I'll start your React development server in the background and monitor its startup."

[Claude executes: npm run dev]
[Shows job ID and startup logs]
[Monitors until server is ready]

Claude: "Your development server is now running on http://localhost:3000. The job ID is abc123-def456 if you need to control it later."
```

### Build Process Monitoring
```
You: "Start building my Docker image and let me know when it's done"

Claude: "I'll start the Docker build process and monitor its progress."

[Executes: docker build -t myapp .]
[Periodically shows progress]
[Reports completion with final status]
```

### Testing Workflow
```
You: "Run my test suite in the background while we discuss the architecture"

Claude: "I'll start your test suite running in the background."

[Starts: npm test]
[Continues architecture discussion]
[Periodically checks test progress]
[Reports final test results when complete]
```

## Next Steps

- Explore the full API by asking Claude to demonstrate different tools
- Set up environment variables for your specific workflow needs
- Integrate with your development processes (CI/CD, testing, builds)
- Use background jobs for any long-running tasks that would otherwise block your Claude conversation

## Getting Help

- Check the main [README.md](README.md) for detailed technical information
- Review [SPEC.md](SPEC.md) for complete API specification
- Look at the test files in `tests/` for usage examples
- Ask Claude to help you with specific use cases - it can demonstrate the tools in real-time!

---

🎉 **You're ready to use background jobs with Claude Code!** Start by asking Claude to execute a simple command and explore from there.
