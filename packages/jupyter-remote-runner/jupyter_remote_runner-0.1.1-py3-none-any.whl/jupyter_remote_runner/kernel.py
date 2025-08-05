import time
import threading
import queue
from jupyter_client import KernelManager
from typing import Optional, Callable


class JupyterKernelExecutor:
    """
    Executes Python, shell (!) and bash magic (%%bash) commands via a persistent Jupyter kernel.
    Supports Python input() calls via stdin. Does not support interactive shell or subprocess input.
    """
    def __init__(self, output_callback: Optional[Callable[[str], None]] = None, output_mode: str = "stream"):
        """
        Initialize JupyterKernelExecutor.
        
        Args:
            output_callback: Optional callback for real-time output streaming
            output_mode: Output behavior mode:
                - "stream": Only real-time streaming via callback
                - "collected": Collect all output and return at end
                - "both": Stream + collect (for debugging)
        """
        self.km = KernelManager(kernel_name="python3")
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()
        self._output_queue = queue.Queue()
        self._last_msg_id = None
        self._is_busy = False
        self._kernel_idle = True
        self._output_callback = output_callback
        self._output_mode = output_mode

        # Ensure IPython magics and bash support loaded
        self.run_command("%load_ext autoreload", timeout=2)
        self.run_command("%autoreload 2", timeout=2)
        
        # Clear any leftover state from initialization
        self._is_busy = False
        self._last_msg_id = None
        self._kernel_idle = True

    def _drain_output(self, stop_event: threading.Event):
        while not stop_event.is_set():
            # Check iopub for main output
            try:
                msg = self.kc.get_iopub_msg(timeout=0.05)
                msg_type = msg.get("msg_type", "")
                content = msg.get("content", {})
                
                # Handle different message types
                if msg_type == "status":
                    # Track kernel execution state
                    execution_state = content.get("execution_state", "")
                    if execution_state == "idle":
                        self._kernel_idle = True
                elif msg_type in ["stream", "display_data", "execute_result", "error"]:
                    # Handle output content
                    output = self._format_output(content, msg_type)
                    if output:
                        if self._output_mode in ["collected", "both"]:
                            self._output_queue.put(output)
                        if self._output_mode in ["stream", "both"]:
                            if self._output_callback:
                                self._output_callback(output)
                # elif msg_type == "execute_input":
                #     # Show code being executed
                #     if "code" in content:
                #         code_display = f">>> {content['code']}\n"
                #         if self._output_mode in ["collected", "both"]:
                #             self._output_queue.put(code_display)
                #         if self._output_mode in ["stream", "both"]:
                #             if self._output_callback:
                #                 self._output_callback(code_display)
            except Exception:
                pass
            
            # Check stdin for input prompts (separate try block)
            try:
                stdin_msg = self.kc.get_stdin_msg(timeout=0.05)
                if stdin_msg.get("msg_type") == "input_request":
                    prompt = stdin_msg.get("content", {}).get("prompt", "")
                    if prompt:
                        if self._output_mode in ["collected", "both"]:
                            self._output_queue.put(prompt)
                        if self._output_mode in ["stream", "both"]:
                            if self._output_callback:
                                self._output_callback(prompt)
            except Exception:
                pass


    def _format_output(self, content: dict, msg_type: str = "") -> str:
        # Handle all content types generically
        if "text" in content:
            return content["text"]
        if "data" in content:
            if isinstance(content["data"], dict):
                return content["data"].get("text/plain", "")
            return str(content["data"])
        if "traceback" in content:
            return "\n".join(content["traceback"])
        if "prompt" in content:  # input_request
            return content["prompt"]
        if "code" in content:  # execute_input
            return f">>> {content['code']}\n"
        
        return ""

    def run_command(self, code: str, timeout: int = 60, is_input: bool = False) -> str:
        """
        Executes or continues output streaming from code in a persistent Jupyter kernel.

        Parameters:
            code (str): 
                - Normal: Python, shell (!), or bash (%%bash) code.
                - " " (space): Special signal to continue retrieving output from a prior command.
                - "C-c": Interrupts the currently running command in the kernel.
                - If is_input=True: text to send to Python's `input()` prompt (see below).

            timeout (int):
                - How long to wait for output.
                - If execution is not complete in time, output can be resumed later with `" "`.

            is_input (bool):
                - True when sending response to a Python `input()` call.
                - Input support only works for Python code using `input()` — not bash or shell commands.

        Returns:
            str: Combined stdout and stderr, or status message.

        Notes:
            - Only one command can execute at a time.
            - Use `" "` to resume incomplete execution and stream remaining output.
            - Send `"C-c"` to interrupt long-running or stalled code.
        """

        output_parts = []
        SUPPORTED_SIGNALS = [" ", "C-c"]

        # Handle different command types with clean flag logic
        if code == "C-c":
            # Always allow interrupt
            self.km.interrupt_kernel()
            self._is_busy = False
            self._last_msg_id = None
            return "🛑 Interrupt signal sent to kernel (C-c)."
        
        if is_input:
            # Input: only if something is running
            if not self._is_busy:
                return "ℹ️ No running command to send input to."
            self.kc.input(code + "\n")
            msg_id = self._last_msg_id  # Continue with existing command
        elif code == " ":
            # Space: only if something is running  
            if not self._is_busy:
                return "ℹ️ No previous command to resume."
            msg_id = self._last_msg_id  # Continue with existing command
        else:
            # New command: only if nothing is running
            if self._is_busy:
                return (
                    "⚠️ Kernel is already running a command.\n"
                    "✔ Send ' ' (single space) to continue retrieving output.\n"
                    "✖ Cannot run a new command until the current one finishes.\n"
                    "💡 Send 'C-c' to interrupt if needed."
                )
            # Start new command - set flag to running
            self._is_busy = True
            msg_id = self.kc.execute(code)
            self._last_msg_id = msg_id

        # Output collection thread
        stop_event = threading.Event()
        thread = threading.Thread(target=self._drain_output, args=(stop_event,))
        thread.start()

        start = time.time()
        execution_finished = False

        # Reset kernel idle state and wait for completion  
        self._kernel_idle = False
        
        try:
            while True:
                if time.time() - start >= timeout:
                    break
                    
                # Check if kernel became idle (execution complete)
                if self._kernel_idle:
                    execution_finished = True
                    break
                    
                time.sleep(0.1)
        finally:
            stop_event.set()
            thread.join()
            
            # Clean flag handling: set to false ONLY if execution completed
            if execution_finished:
                self._is_busy = False
            # If timeout/incomplete: leave _is_busy = True (can continue with " ")

        # Collect output only if in collected mode
        if self._output_mode in ["collected", "both"]:
            while not self._output_queue.empty():
                output_parts.append(self._output_queue.get())

        if not execution_finished:
            status_msg = (
                "\n⏳ The command is still running.\n"
                "💡 Send ' ' (space) to continue retrieving output.\n"
                "🛑 Or send 'C-c' to interrupt it manually.\n"
            )
            if self._output_mode in ["collected", "both"]:
                output_parts.append(status_msg)
            elif self._output_mode == "stream" and self._output_callback:
                self._output_callback(status_msg)

        # Return output based on mode
        if self._output_mode == "stream":
            return ""  # No return value, already streamed
        else:
            return "".join(output_parts)

    def shutdown(self):
        """Shut down kernel and channels cleanly."""
        self.kc.stop_channels()
        self.km.shutdown_kernel()