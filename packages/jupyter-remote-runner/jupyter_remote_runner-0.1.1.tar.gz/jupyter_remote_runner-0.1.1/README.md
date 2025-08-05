# Jupyter Remote Runner

A CLI interface to a persistent Jupyter kernel for code execution with timeout handling and streaming output.

## Installation

Install using pipx (recommended):

```bash
pipx install .
```

Or using pip:

```bash
pip install .
```

## Usage

### Commands

- `jupyter-remote-runner --help` - Show help
- `jupyter-remote-runner start` - Start the Jupyter kernel daemon
- `jupyter-remote-runner stop` - Stop the daemon
- `jupyter-remote-runner status` - Check daemon status
- `jupyter-remote-runner run <code>` - Execute code in the persistent kernel

### Run Command Options

- `--timeout <seconds>` - Set execution timeout (default: 60)
- `--is-input` - Send code as input to Python input() prompt

### Examples

```bash
# Start the daemon
jupyter-remote-runner start

# Execute Python code
jupyter-remote-runner run "print('Hello World')"

# Execute shell command
jupyter-remote-runner run "!ls -la"

# Execute bash magic
jupyter-remote-runner run "%%bash\necho 'Hello from bash'"

# Continue previous command output
jupyter-remote-runner run " "

# Interrupt running command
jupyter-remote-runner run "C-c"

# Execute with custom timeout
jupyter-remote-runner run "import time; time.sleep(10)" --timeout 15

# Check status
jupyter-remote-runner status

# Stop the daemon
jupyter-remote-runner stop
```

## Features

- **Persistent Kernel**: Maintains state between commands
- **Streaming Output**: Real-time output streaming
- **Timeout Support**: Configurable execution timeouts
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Background Daemon**: Runs kernel in background process
- **Signal Handling**: Support for interrupting long-running commands
- **Input Support**: Handle Python input() calls

## Development

Run tests:

```bash
python test_cli.py
```

Run directly from source:

```bash
python -m jupyter_remote_runner --help
```