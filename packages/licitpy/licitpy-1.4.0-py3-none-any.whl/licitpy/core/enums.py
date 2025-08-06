from enum import Enum
from typing import Awaitable, Callable, Optional

from pydantic import BaseModel, PrivateAttr


class FileType(Enum):
    DOC = "doc"
    DOCX = "docx"
    DWG = "dwg"
    JPEG = "jpeg"
    JPG = "jpg"
    KMZ = "kmz"
    ODT = "odt"
    PDF = "pdf"
    PNG = "png"
    RAR = "rar"
    RTF = "rtf"
    XLS = "xls"
    XLSX = "xlsx"
    ZIP = "zip"


class ContentStatus(Enum):
    """
    Enum representing the content's download status.

    Attributes:
        PENDING_DOWNLOAD: Content is ready to be downloaded. Access `.content` to trigger the download.
        AVAILABLE: Content has been downloaded and is ready to use.
    """

    PENDING_DOWNLOAD = "Pending download"
    AVAILABLE = "Downloaded"


class Attachment(BaseModel):
    id: str
    name: str
    type: str
    description: str | None
    size: int
    upload_date: str
    file_type: FileType
    _download_fn: Callable[[], Awaitable[str]] = PrivateAttr()
    _content: Optional[str] = PrivateAttr(default=None)

    @property
    async def content(self) -> Optional[str]:
        if self._content is None:
            self._content = await self._download_fn()

        return self._content

    @property
    def content_status(self) -> ContentStatus:
        if self._content is None:
            return ContentStatus.PENDING_DOWNLOAD

        return ContentStatus.AVAILABLE
