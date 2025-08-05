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
        self._output_callback = output_callback
        self._output_mode = output_mode

        # Ensure IPython magics and bash support loaded
        self.run_command("%load_ext autoreload", timeout=2)
        self.run_command("%autoreload 2", timeout=2)

    def _drain_output(self, stop_event: threading.Event):
        while not stop_event.is_set():
            try:
                msg = self.kc.get_iopub_msg(timeout=0.5)
                if msg["msg_type"] in {"stream", "display_data", "execute_result", "error"}:
                    content = msg["content"]
                    output = self._format_output(content)
                    if output:
                        # Handle output based on configured mode
                        if self._output_mode in ["collected", "both"]:
                            self._output_queue.put(output)
                        
                        if self._output_mode in ["stream", "both"]:
                            if self._output_callback:
                                self._output_callback(output)
            except Exception:
                continue

    def _format_output(self, content: dict) -> str:
        if "text" in content:
            return content["text"]
        if "data" in content:
            return content["data"].get("text/plain", "")
        if "traceback" in content:
            return "\n".join(content["traceback"])
        return str(content)

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

        if is_input:
            self.kc.input(code)
            time.sleep(0.2)
            return ""

        if code in SUPPORTED_SIGNALS:
            if code == " ":
                if not self._last_msg_id:
                    return "ℹ️ No previous command to resume."
                msg_id = self._last_msg_id
            elif code == "C-c":
                self.km.interrupt_kernel()
                return "🛑 Interrupt signal sent to kernel (C-c)."
        else:
            if self._is_busy:
                return (
                    "⚠️ Kernel is already running a command.\n"
                    "✔ Send ' ' (single space) to continue retrieving output.\n"
                    "✖ Cannot run a new command until the current one finishes.\n"
                    "💡 Send 'C-c' to interrupt if needed."
                )
            self._is_busy = True
            msg_id = self.kc.execute(code)
            self._last_msg_id = msg_id

        # Output collection thread
        stop_event = threading.Event()
        thread = threading.Thread(target=self._drain_output, args=(stop_event,))
        thread.start()

        start = time.time()
        execution_finished = False

        try:
            while True:
                if time.time() - start >= timeout:
                    break
                try:
                    reply = self.kc.get_shell_msg(timeout=0.5)
                    if reply["parent_header"].get("msg_id") == msg_id:
                        execution_finished = True
                        break
                except Exception:
                    continue
        finally:
            stop_event.set()
            thread.join()
            self._is_busy = not execution_finished

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