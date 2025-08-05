import httpx
from pydantic import BaseModel

from ...types.field import Field, resolve_default
from ...types.file import File
from ...utils import _platform_api_call


class Uploader(BaseModel):
    content_url: str
    """The url where the file will be available."""
    upload_method: str 
    """The http method to use to upload the file."""
    upload_uri: str 
    """The url to use to upload the file."""
    upload_headers: dict[str, str]
    """The headers to add to the upload request."""
    

async def upload_file(
    org_id: str = Field(description="The organization ID."),
    file: File = Field(description="The file to upload."),
) -> str:
    """
    Upload a file that can be used across various endpoints.

    Args:
        org_id (str): The organization ID.
        file (File): The file to upload.

    Returns:
        str: The URL where the file will be available.
    """
    org_id = resolve_default("org_id", org_id)
    file = resolve_default("file", file)

    file = file if isinstance(file, File) else File.validate(file)

    file.seek(0)
    content = file.read()
    size = len(content)

    path = f"orgs/{org_id}/files"
    payload = {
        "name": file.name,
        "content_type": file.__content_type__,
        "content_length": size,
    }

    res = await _platform_api_call("POST", path, json=payload)
    uploader = Uploader.model_validate(res.json().get("uploader", {}))

    async with httpx.AsyncClient() as client:
        res = await client.request(
            uploader.upload_method,
            uploader.upload_uri,
            headers=uploader.upload_headers,
            content=content,
        )
        res.raise_for_status()

    return uploader.content_url


if __name__ == "__main__":
    import asyncio
    res = asyncio.run(upload_file(
        org_id="1",
        file="./ROADMAP_V2.md",
    ))
    print(res)
