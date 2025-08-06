from urllib.parse import urljoin

from licitpy.core.models import Tender
from licitpy.core.provider.tender import BaseTenderProvider
from licitpy.core.services.attachments import AttachmentServices
from licitpy.countries.cl.parser import ChileTenderParser
from licitpy.core.http import AsyncHttpClient


class MercadoPublicoChileProvider(BaseTenderProvider):
    name = "cl"
    BASE_URL = "https://www.mercadopublico.cl"

    def __init__(
        self,
        downloader: AsyncHttpClient,
        parser: ChileTenderParser | None = None,
        attachment: AttachmentServices | None = None,
    ) -> None:
        self.downloader = downloader
        self.parser = parser or ChileTenderParser()
        self.attachment = attachment or AttachmentServices(downloader=self.downloader)

    async def get_url_by_code(self, code: str) -> str:
        """
        Retrieve the full URL for a tender based on its code.

        This method constructs the initial URL using the tender code, sends a HEAD request
        to check for redirection, and returns the final resolved URL.

        Args:
            code (str): The unique identifier for the tender.

        Returns:
            str: The resolved URL pointing to the tender details.
        """

        url = f"{self.BASE_URL}/Procurement/Modules/RFB/DetailsAcquisition.aspx?idlicitacion={code}"

        response = await self.downloader.session.head(
            url, timeout=30, allow_redirects=False
        )

        if "Location" not in response.headers:
            raise ValueError(f"No redirection found for tender code: {code}")

        return urljoin(self.BASE_URL, response.headers["Location"])

    async def get_by_code(self, code: str) -> Tender:
        
        if not code.strip():
            raise ValueError("Tender code cannot be empty or whitespace.")

        url = await self.get_url_by_code(code)
        html = await self.downloader.get_html_by_url(url)

        title = self.parser.get_title(html)
        closing_date = self.parser.get_closing_date(html)

        attachment_url = self.parser.get_attachment_url(html)
        attachment_html = await self.downloader.get_html_by_url(attachment_url)
        attachments = await self.attachment.get_attachments(
            attachment_url, attachment_html
        )

        return Tender(
            code=code,
            title=title,
            closing_date=closing_date,
            attachment_url=attachment_url,
            attachments=attachments,
        )
