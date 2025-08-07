"""
This module manages the discovery, execution, and communication with Spex plugins.

It ensures a stable connection by waiting for the plugin's gRPC server to be
ready and correctly handles gRPC's process forking requirements.
"""

import logging
import os
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Optional

import grpc

# Import the generated gRPC client stub
from boot.generated import plugin_pb2_grpc
from boot.utils.helpers import get_local_plugins_dir  # Add this


class PluginManager:
    """
    Finds, runs, and connects to a language plugin.
    This class handles the lifecycle of a plugin subprocess, including starting it,
    establishing a gRPC connection, and cleaning up the process on exit.
    """

    def __init__(self, plugin_name: str):
        """
        Initializes the PluginManager.

        Args:
            plugin_name: The name of the plugin executable,
                               e.g., "boot-pyspark".
        """
        self.plugin_name = plugin_name
        # Add type parameter `str` to Popen because `text=True` is used, meaning
        # stdout/stderr will be strings.
        self.process: Optional[Popen[str]] = None
        self.channel: Optional[grpc.Channel] = None
        self.client_stub: Optional[plugin_pb2_grpc.BootCodePluginStub] = None

    def start(self) -> None:
        """
        Finds the plugin, runs it as a subprocess, and establishes a gRPC connection.
        This method implements a handshake protocol where it waits for the plugin's
        gRPC server to be fully initialized before creating a client stub.
        It also
        sets the GRPC_PYTHON_FORK_SUPPORT environment variable to prevent runtime
        segmentation faults on systems like macOS.
        Raises:
            FileNotFoundError: If the plugin executable cannot be found in the system's PATH.
            ConnectionError: If the plugin fails to start or the gRPC connection times out.
        """
        log_file = Path.cwd() / "boot_debug.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            filename=str(log_file),
            filemode="w",
        )

        plugin_executable = self._find_plugin()
        if not plugin_executable:
            raise FileNotFoundError(
                f"Plugin executable not found: {self.plugin_name}. "
                "Ensure it is installed and available in your system's PATH."
            )

        plugin_env = os.environ.copy()
        plugin_env["GRPC_PYTHON_FORK_SUPPORT"] = "1"

        logging.info(f"Starting plugin: {plugin_executable}")
        logging.info(
            "Subprocess environment includes GRPC_PYTHON_FORK_SUPPORT="
            f"{plugin_env.get('GRPC_PYTHON_FORK_SUPPORT')}"
        )

        self.process = Popen(
            [plugin_executable],
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            env=plugin_env,
        )

        handshake = (
            self.process.stdout.readline().strip() if self.process.stdout else ""
        )
        if not handshake:
            stderr_output = (
                self.process.stderr.read()
                if self.process.stderr
                else "No stderr output."
            )
            logging.error(
                f"Plugin {self.plugin_name} failed to start. Stderr: {stderr_output}"
            )
            raise ConnectionError(
                f"Plugin {self.plugin_name} failed to start. Error: {stderr_output}"
            )

        # Error logging for handshake
        parts = handshake.split("|")
        if len(parts) != 5:
            stderr_preview = self.process.stderr.read() if self.process.stderr else ""
            raise ConnectionError(
                f"Invalid handshake from {self.plugin_name}: {handshake!r}. "
                "Expected '1|1|tcp|HOST:PORT|grpc'. "
                f"Stderr: {stderr_preview[:800]}"
            )

        _, _, _, addr, _ = handshake.split("|")

        logging.info(f"Connecting to plugin at gRPC address: {addr}")
        self.channel = grpc.insecure_channel(addr)

        try:
            grpc.channel_ready_future(self.channel).result(timeout=10)
            logging.info("Plugin gRPC channel is ready.")
        except grpc.FutureTimeoutError as e:
            self.stop()
            raise ConnectionError(
                f"Timed out waiting for plugin {self.plugin_name} to become ready."
            ) from e

        # Ignore the mypy error for calling an untyped function from our generated
        self.client_stub = plugin_pb2_grpc.BootCodePluginStub(self.channel)  # type: ignore[no-untyped-call]

    def stop(self) -> None:
        """
        Cleans up the gRPC connection and terminates the plugin subprocess.
        """
        if self.channel:
            self.channel.close()
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except TimeoutExpired:
                self.process.kill()
        logging.info(f"Stopped plugin: {self.plugin_name}")

    def _find_plugin(self) -> Optional[str]:
        """
        Finds the plugin executable, searching the local managed directory first,
        then the system's PATH.
        """
        # 1. Search in the local managed directory
        local_plugin_path = get_local_plugins_dir() / self.plugin_name
        if local_plugin_path.is_file() and os.access(local_plugin_path, os.X_OK):
            logging.info(f"Found managed plugin at: {local_plugin_path}")
            return str(local_plugin_path)

        # 2. Fallback to searching the system PATH
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for path_dir in path_dirs:
            plugin_path = Path(path_dir) / self.plugin_name
            if plugin_path.is_file() and os.access(plugin_path, os.X_OK):
                logging.info(f"Found plugin in PATH at: {plugin_path}")
                return str(plugin_path)

        return None
