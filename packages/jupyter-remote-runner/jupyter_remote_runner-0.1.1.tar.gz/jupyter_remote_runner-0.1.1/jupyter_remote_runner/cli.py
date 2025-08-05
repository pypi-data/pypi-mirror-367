#!/usr/bin/env python3
"""
Jupyter Remote Runner CLI

A CLI interface to a persistent Jupyter kernel for code execution with timeout handling.
"""

import sys
import os
import click
from .daemon import KernelDaemon


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """
    Jupyter Remote Runner - CLI interface to persistent Jupyter kernel.
    
    USAGE:
      jupyter-remote-runner start [--output-mode MODE]  # Start daemon
      jupyter-remote-runner run "CODE" [OPTIONS]        # Execute code
      jupyter-remote-runner stop                        # Stop daemon
      jupyter-remote-runner status                      # Check status
    
    OUTPUT MODES:
      stream     - Real-time output streaming (default, no duplicates)
      collected  - Return all output at command end
      both       - Stream + collect (for debugging)
    
    EXAMPLES:
      # Start with real-time streaming (default)
      jupyter-remote-runner start
      
      # Start with collected output mode
      jupyter-remote-runner start --output-mode collected
      
      # Execute Python code
      jupyter-remote-runner run "print('Hello World')"
      
      # Execute with timeout
      jupyter-remote-runner run "import time; time.sleep(3)" --timeout 5
      
      # Continue previous command output
      jupyter-remote-runner run " "
      
      # Interrupt running command
      jupyter-remote-runner run "C-c"
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.option('--output-mode', '-o', 
              type=click.Choice(['stream', 'collected', 'both']), 
              default='stream',
              help='Output mode: stream (real-time), collected (return at end), both (debug)')
def start(output_mode):
    """
    Start the Jupyter kernel daemon in the background.
    
    Output modes:
    - stream: Real-time output streaming (default, no duplicates)
    - collected: Return all output at command end
    - both: Stream + collect (for debugging)
    """
    daemon = KernelDaemon()
    
    if daemon.is_running():
        click.echo("Daemon is already running.")
        return
    
    click.echo(f"Starting Jupyter kernel daemon in '{output_mode}' mode...")
    
    if hasattr(sys, 'platform') and sys.platform == 'win32':
        # On Windows, start daemon as subprocess
        import subprocess
        
        # Start daemon as separate process
        script = [
            sys.executable, 
            "-c",
            f"import sys; sys.path.insert(0, '.'); from jupyter_remote_runner.daemon import KernelDaemon; d = KernelDaemon(); d._run_daemon(output_mode='{output_mode}')"
        ]
        
        try:
            proc = subprocess.Popen(script, cwd=os.getcwd())
            
            # Write PID file
            with open(daemon.pid_file, 'w') as f:
                f.write(str(proc.pid))
            
            click.echo("Daemon started successfully.")
            click.echo(f"Daemon PID: {proc.pid}")
            
        except Exception as e:
            click.echo(f"Failed to start daemon: {e}", err=True)
            sys.exit(1)
    else:
        # Unix-like systems can fork
        if daemon.start(output_mode):
            click.echo("Daemon started successfully.")
        else:
            click.echo("Failed to start daemon.", err=True)
            sys.exit(1)


@main.command()
def stop():
    """Stop the Jupyter kernel daemon."""
    daemon = KernelDaemon()
    
    if not daemon.is_running():
        click.echo("Daemon is not running.")
        return
    
    click.echo("Stopping Jupyter kernel daemon...")
    
    if daemon.stop():
        click.echo("Daemon stopped successfully.")
    else:
        click.echo("Failed to stop daemon.", err=True)
        sys.exit(1)


@main.command()
@click.argument('code')
@click.option('--timeout', '-t', default=60, type=int, 
              help='Timeout in seconds (default: 60)')
@click.option('--is-input', is_flag=True, 
              help='Send code as input to Python input() prompt')
def run(code, timeout, is_input):
    """
    Execute code in the persistent Jupyter kernel.
    
    CODE: Python code, shell command (!), or bash magic (%%bash) to execute.
    
    Special commands:
    - " " (space): Continue retrieving output from previous command
    - "C-c": Interrupt currently running command
    
    Examples:
    - jupyter-remote-runner run "print('Hello World')"
    - jupyter-remote-runner run "!ls -la" --timeout 30
    - jupyter-remote-runner run "%%bash\\necho 'Hello from bash'"
    - jupyter-remote-runner run " "  # Continue previous command
    - jupyter-remote-runner run "C-c"  # Interrupt running command
    """
    daemon = KernelDaemon()
    
    if not daemon.is_running():
        click.echo("Error: Daemon not running. Start it first with 'jupyter-remote-runner start'", err=True)
        sys.exit(1)
    
    command_data = {
        'code': code,
        'timeout': timeout,
        'is_input': is_input
    }
    
    result = daemon.send_command(command_data)
    
    if result.startswith("Error:"):
        click.echo(result, err=True)
        sys.exit(1)
    else:
        click.echo(result, nl=False)


@main.command()
def status():
    """Check the status of the Jupyter kernel daemon."""
    daemon = KernelDaemon()
    
    if daemon.is_running():
        click.echo("Daemon is running.")
        try:
            with open(daemon.pid_file, 'r') as f:
                pid = f.read().strip()
            click.echo(f"PID: {pid}")
            click.echo(f"Runtime directory: {daemon.runtime_dir}")
        except Exception:
            pass
    else:
        click.echo("Daemon is not running.")


if __name__ == '__main__':
    main()