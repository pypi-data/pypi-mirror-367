import base64
import os

from licitpy.core.enums import Attachment
from licitpy.core.exceptions import AttachmentDownloadError


async def save_attachment(
    attachment: Attachment,
    content: str | None = None,
    path: str = ".",
    filename: str | None = None,
) -> str:
    # If content is not provided, fetch it from the attachment
    if content is None:
        # this triggers the download of the attachment content
        content = await attachment.content

    if not content:
        raise AttachmentDownloadError(
            f"Failed to download attachment: {attachment.name}"
        )

    # If filename is not provided, use the attachment's name
    filename = filename or attachment.name

    full_path = os.path.join(path, filename)

    # if folder does not exist , raise an error
    if not os.path.exists(path):
        raise FileNotFoundError(f"Directory does not exist: {path}")

    with open(full_path, "wb") as file:
        file.write(base64.b64decode(content))

    return full_path
