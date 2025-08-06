from datetime import datetime
from urllib.parse import urljoin

from licitpy.core.http import AsyncHttpClient


class EUTenderDownloader:
    monthly_url = "https://ted.europa.eu/packages/monthly/"

    def __init__(self, downloader: AsyncHttpClient):
        self.downloader = downloader

    def get_url_by_month(self, when: datetime) -> str:
        """
        Constructs the URL for the EU tender package based on a datetime object.
        Args:
            when (datetime): The datetime object representing the date of the tender package.
            Returns:
            str: The constructed URL for the tender package.
        """

        return urljoin(self.monthly_url, f"{when.year}-{when.month}")

    async def download_file(
        self, url: str, file_name: str
    ) -> dict[str, str | int | float]:
        """
        Downloads a file from the given URL and saves it with the specified file name.
        """

        return await self.downloader.download_file(url, file_name)
