# FILE: boot/core/spec_loader.py
import httpx
from pathlib import Path
from boot.errors import SpecValidationError

HUB_URI_PREFIX = "hub:"


async def get_spec_content(
    spec_identifier: str, supabase_url: str, supabase_anon_key: str
) -> str:
    """
    Fetches spec content from a local file path or the Community Hub.

    Args:
        spec_identifier: A local file path or a hub URI (e.g., "hub:uuid-goes-here").
        supabase_url: The base URL for the Supabase project.
        supabase_anon_key: The public anon key for Supabase API access.

    Returns:
        The raw string content of the TOML spec.
    """
    if spec_identifier.startswith(HUB_URI_PREFIX):
        if not supabase_anon_key:
            raise SpecValidationError("Supabase anon key is not configured.")

        spec_id = spec_identifier[len(HUB_URI_PREFIX) :]
        headers = {
            "Authorization": f"Bearer {supabase_anon_key}",
            "apikey": supabase_anon_key,
        }
        url = f"{supabase_url}/functions/v1/get-spec"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params={"id": spec_id}, headers=headers
                )
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as e:
            raise SpecValidationError(
                f"Failed to fetch spec '{spec_id}' from hub: {e}"
            ) from e
    else:
        spec_path = Path(spec_identifier)
        if not spec_path.is_file():
            raise SpecValidationError(f"Specification file not found at: {spec_path}")
        return spec_path.read_text("utf-8")
