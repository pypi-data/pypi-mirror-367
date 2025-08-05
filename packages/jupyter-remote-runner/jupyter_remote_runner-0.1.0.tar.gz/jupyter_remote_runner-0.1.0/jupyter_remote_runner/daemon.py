import os
import sys
import json
import time
import signal
import threading
from pathlib import Path
from typing import Optional
import platformdirs
from .kernel import JupyterKernelExecutor


class KernelDaemon:
    """Background daemon that manages a persistent JupyterKernelExecutor."""
    
    def __init__(self):
        self.app_name = "jupyter-remote-runner"
        self.runtime_dir = Path(platformdirs.user_runtime_dir(self.app_name))
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        
        self.pid_file = self.runtime_dir / "daemon.pid"
        self.command_fifo = self.runtime_dir / "command.fifo"
        self.output_fifo = self.runtime_dir / "output.fifo"
        
        self.executor: Optional[JupyterKernelExecutor] = None
        self.running = False
        
    def is_running(self) -> bool:
        """Check if daemon is already running."""
        if not self.pid_file.exists():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running (Windows compatible)
            if sys.platform == 'win32':
                import subprocess
                try:
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                          capture_output=True, text=True)
                    return str(pid) in result.stdout
                except:
                    return False
            else:
                # Unix-like systems
                os.kill(pid, 0)
                return True
        except (OSError, ValueError, ProcessLookupError):
            # Process doesn't exist, clean up stale pid file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def start(self, output_mode: str = "stream") -> bool:
        """Start the daemon process."""
        if self.is_running():
            return False
            
        # Create named pipes for communication
        try:
            if self.command_fifo.exists():
                self.command_fifo.unlink()
            if self.output_fifo.exists():
                self.output_fifo.unlink()
                
            os.mkfifo(str(self.command_fifo))
            os.mkfifo(str(self.output_fifo))
        except OSError:
            # Fall back to files if FIFOs not supported (Windows)
            pass
        
        # Fork daemon process
        pid = os.fork() if hasattr(os, 'fork') else 0
        
        if pid == 0:  # Child process (daemon) or Windows
            self._run_daemon(output_mode)
        else:  # Parent process
            # Write PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(pid))
            return True
    
    def stop(self) -> bool:
        """Stop the daemon process."""
        if not self.is_running():
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if sys.platform == 'win32':
                # Windows process termination
                import subprocess
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True)
                except:
                    pass
            else:
                # Unix-like systems
                os.kill(pid, signal.SIGTERM)
                
                # Wait for process to exit
                for _ in range(50):  # 5 second timeout
                    try:
                        os.kill(pid, 0)
                        time.sleep(0.1)
                    except ProcessLookupError:
                        break
                else:
                    # Force kill if still running
                    os.kill(pid, signal.SIGKILL)
            
            # Clean up files
            if self.pid_file.exists():
                self.pid_file.unlink()
            if self.command_fifo.exists():
                self.command_fifo.unlink()
            if self.output_fifo.exists():
                self.output_fifo.unlink()
                
            return True
        except (OSError, ValueError):
            return False
    
    def send_command(self, command_data: dict) -> str:
        """Send command to daemon and get response."""
        if not self.is_running():
            return "Error: Daemon not running. Use 'start' command first."
        
        try:
            # Send command
            command_json = json.dumps(command_data)
            
            # Use file-based communication for cross-platform compatibility
            command_file = self.runtime_dir / "command.json"
            output_file = self.runtime_dir / "output.json"
            
            with open(command_file, 'w') as f:
                f.write(command_json)
            
            # Wait for response with timeout
            start_time = time.time()
            timeout = command_data.get('timeout', 60) + 5  # Add 5s buffer
            
            while time.time() - start_time < timeout:
                if output_file.exists():
                    try:
                        with open(output_file, 'r') as f:
                            result = json.loads(f.read())
                        output_file.unlink()
                        return result.get('output', '')
                    except (json.JSONDecodeError, IOError):
                        pass
                time.sleep(0.1)
            
            return "Error: Command timeout"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _run_daemon(self, output_mode: str = "stream"):
        """Main daemon loop."""
        self.running = True
        
        # Initialize kernel executor with streaming callback
        def output_callback(output: str):
            # Stream output in real-time
            sys.stdout.write(output)
            sys.stdout.flush()
        
        self.executor = JupyterKernelExecutor(
            output_callback=output_callback,
            output_mode=output_mode
        )
        
        # Write PID file for Windows
        if not hasattr(os, 'fork'):
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        
        # Set up signal handlers (only if in main thread)
        try:
            def signal_handler(signum, frame):
                self.running = False
                if self.executor:
                    self.executor.shutdown()
                sys.exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        except ValueError:
            # Signal handlers can only be set in main thread
            # On Windows with threading, we'll handle cleanup differently
            pass
        
        # Main command processing loop
        command_file = self.runtime_dir / "command.json"
        output_file = self.runtime_dir / "output.json"
        
        while self.running:
            try:
                if command_file.exists():
                    try:
                        with open(command_file, 'r') as f:
                            command_data = json.loads(f.read())
                        
                        command_file.unlink()
                        
                        # Execute command
                        code = command_data.get('code', '')
                        timeout = command_data.get('timeout', 60)
                        is_input = command_data.get('is_input', False)
                        
                        result = self.executor.run_command(code, timeout, is_input)
                        
                        # Write response
                        with open(output_file, 'w') as f:
                            json.dump({'output': result}, f)
                            
                    except (json.JSONDecodeError, IOError):
                        pass
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
        
        # Cleanup
        if self.executor:
            self.executor.shutdown()
        if self.pid_file.exists():
            self.pid_file.unlink()