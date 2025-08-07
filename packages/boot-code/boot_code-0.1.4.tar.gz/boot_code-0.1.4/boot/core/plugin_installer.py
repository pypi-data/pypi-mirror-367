# boot/core/plugin_installer.py
import asyncio
import io
import platform
import shutil
import stat
import zipfile
from typing import Any, Dict, cast

import httpx

from boot.models.config import get_settings
from boot.utils.helpers import get_local_plugins_dir


class PluginInstaller:
    """
    Handles the fetching and local installation of language plugins,
    supporting both compiled binaries (Rust) and pipx packages (Python).
    """

    def __init__(self) -> None:
        """Initializes the installer and loads application settings."""
        self.settings = get_settings()

    async def install(self, plugin_name: str) -> None:
        """
        Fetches plugin metadata and installs it using the appropriate method
        based on the plugin's language.
        """
        plugin_info = await self._get_plugin_info(plugin_name)
        language = plugin_info.get("language")

        if language == "python":
            await self._install_python_plugin(plugin_info)
        else:
            # Default to binary installation for Rust and other compiled languages
            await self._install_binary_plugin(plugin_info)

    async def _install_python_plugin(self, plugin_info: Dict[str, Any]) -> None:
        """
        Installs a Python plugin from its GitHub repository using pipx.
        """
        plugin_name = plugin_info["name"]
        github_url = plugin_info["github_url"]
        git_install_url = f"git+{github_url}.git"

        print(f"Installing Python plugin '{plugin_name}' with pipx...")

        if not shutil.which("pipx"):
            raise FileNotFoundError(
                "Error: 'pipx' is not installed or not in your PATH.\n"
                "pipx is required to install Python-based plugins safely.\n"
                "Please install it by running: python3 -m pip install pipx"
            )

        process = await asyncio.create_subprocess_exec(
            "pipx",
            "install",
            git_install_url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print(f"✅ Plugin '{plugin_name}' installed successfully via pipx.")
        else:
            raise RuntimeError(
                f"Failed to install plugin '{plugin_name}'.\n"
                f"pipx stderr:\n{stderr.decode()}"
            )

    async def _install_binary_plugin(self, plugin_info: Dict[str, Any]) -> None:
        """
        Installs a compiled binary plugin from a GitHub release asset.
        """
        plugin_name = plugin_info["name"]
        download_url = plugin_info["download_url"]

        print(f"Downloading from {download_url}...")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(download_url)
            response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            binary_name_in_zip = z.namelist()[0]
            binary_content = z.read(binary_name_in_zip)

            install_path = get_local_plugins_dir() / plugin_name
            install_path.write_bytes(binary_content)
            install_path.chmod(install_path.stat().st_mode | stat.S_IEXEC)
            print(f"✅ Plugin '{plugin_name}' installed successfully to {install_path}")

    async def _get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Retrieves all necessary plugin metadata from the Supabase Edge Function."""
        if not self.settings.supabase_anon_key:
            raise ValueError(
                "Supabase anon key not configured. "
                "Please set SPEX_SUPABASE_ANON_KEY in your .env file or environment."
            )

        system = platform.system().lower()
        arch = platform.machine().lower()
        if system == "darwin":
            system = "apple-darwin"

        params = {
            "name": plugin_name,
            "os": system,
            "arch": arch,
        }

        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.settings.supabase_anon_key}",
            "apikey": self.settings.supabase_anon_key,
        }

        # Use the full URL from settings
        url = f"{self.settings.supabase_url}/functions/v1/get-plugin-info"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return cast(Dict[str, Any], response.json())
            except httpx.HTTPStatusError as e:
                # Provide more detailed error information
                error_detail = ""
                try:
                    error_json = e.response.json()
                    error_detail = f": {error_json.get('error', 'Unknown error')}"
                except (ValueError, AttributeError):
                    error_detail = f": {e.response.text}"

                raise RuntimeError(
                    f"Failed to fetch plugin info from Supabase{error_detail}"
                ) from e
