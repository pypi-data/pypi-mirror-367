# boot/core/plugin_installer.py
import httpx
import platform
import zipfile
import io
import stat
from typing import Dict, Any, cast

from boot.utils.helpers import get_local_plugins_dir
from boot.models.config import get_settings

# This should be your actual Supabase project URL
SUPABASE_GET_PLUGIN_URL = (
    "https://fgcuyeytouwpsehhoisf.supabase.co/functions/v1/get-plugin-info"
)


class PluginInstaller:
    """
    Handles the fetching and local installation of language plugins.
    """

    def __init__(self) -> None:
        """
        Initializes the installer and loads application settings.
        """
        self.settings = get_settings()

    async def install(self, plugin_name: str) -> None:
        """
        Fetches a plugin binary from its GitHub release, unzips it, and installs
        it into the local boot plugins directory, making it executable.

        Args:
            plugin_name: The name of the plugin to install (e.g., "boot-rust").
        """
        plugin_info = await self._get_plugin_info(plugin_name)
        release_url = self._construct_release_url(plugin_info)

        print(f"Downloading from {release_url}...")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(release_url)
            response.raise_for_status()

        # Unzip and install the binary
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Assuming the binary is the only file in the zip
            binary_name_in_zip = z.namelist()[0]
            binary_content = z.read(binary_name_in_zip)

            install_path = get_local_plugins_dir() / plugin_name
            install_path.write_bytes(binary_content)

            # Make the file executable
            install_path.chmod(install_path.stat().st_mode | stat.S_IEXEC)
            print(f"✅ Plugin '{plugin_name}' installed successfully to {install_path}")

    async def _get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """
        Retrieves plugin metadata from the Supabase Edge Function.

        Args:
            plugin_name: The name of the plugin.

        Returns:
            A dictionary containing the plugin's metadata (name, version, etc.).
        """
        if not self.settings.supabase_anon_key:
            raise ValueError(
                "Supabase anon key is not configured. Please set SPEX_SUPABASE_ANON_KEY."
            )

        # Prepare the authentication headers with explicit string types
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.settings.supabase_anon_key}",
            "apikey": self.settings.supabase_anon_key,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                SUPABASE_GET_PLUGIN_URL, params={"name": plugin_name}, headers=headers
            )
            response.raise_for_status()
            # Cast the response to the expected type to satisfy mypy
            return cast(Dict[str, Any], response.json())

    def _construct_release_url(self, plugin_info: Dict[str, Any]) -> str:
        """
        Constructs the correct GitHub release URL for the current OS/architecture.

        Args:
            plugin_info: The metadata dictionary for the plugin.

        Returns:
            The full URL to the downloadable release asset.
        """
        repo_url = plugin_info["github_url"]
        version = plugin_info["version"]
        name = plugin_info["name"]

        # Determine OS and architecture to build the asset name
        system = platform.system().lower()
        arch = platform.machine().lower()
        if system == "darwin":
            system = "apple-darwin"

        asset_name = f"{name}-{arch}-{system}.zip"
        return f"{repo_url}/releases/download/v{version}/{asset_name}"
