import asyncio
from datetime import datetime

import dateparser

from licitpy.core.http import AsyncHttpClient
from licitpy.core.provider.tender import BaseTenderProvider
from licitpy.countries.eu.downloader import EUTenderDownloader
from licitpy.countries.eu.parser import EUTenderParser


class EUTenderProvider(BaseTenderProvider):
    name = "eu"

    def __init__(
        self,
        downloader: AsyncHttpClient,
        parser: EUTenderParser | None = None,
    ) -> None:
        self.downloader = EUTenderDownloader(downloader)
        self.parser = parser or EUTenderParser()

    async def get_by_code(self, code: str) -> None:
        raise NotImplementedError(
            "The EU provider does not support fetching tenders by code."
        )

    async def download_monthly_bulk_file(
        self, when: datetime | str
    ) -> dict[str, str | int | float]:
        """
        Download the monthly bulk file for the EU tenders.
        """

        if when is None:
            raise ValueError(
                "Invalid date format. Please provide a valid datetime object."
            )

        if isinstance(when, str):
            parsed_when = dateparser.parse(when)

            if parsed_when is None:
                raise ValueError(
                    "Invalid date string. Please provide a valid date string."
                )

            when = parsed_when

        if not isinstance(when, datetime):
            raise ValueError(
                "Invalid date format. Please provide a valid date string or datetime object."
            )

        url = self.downloader.get_url_by_month(when)
        file_name = f"{when.year}-{when.month}.tar.gz"

        return await self.downloader.download_file(url, file_name)

    async def download_yearly_bulk_file(self, year: str) -> list[dict[str, str | int | float]]:
        """
        Download the entire year bulk file for the EU tenders.
        """

        if not year.isdigit() or len(year) != 4:
            raise ValueError("Year must be a 4-digit string.")

        if int(year) < 2015:
            raise ValueError("Year must be 2015 or later.")

        when = dateparser.parse(f"{year}-01-01")
        
        if when is None:
            raise ValueError("Invalid year format. Please provide a valid year string.")
        
        # Create a list of tasks for each month in the year
        tasks = [
            self.download_monthly_bulk_file(when.replace(month=month))
            for month in range(1, 13)
        ]

        # Execute all download tasks concurrently
        return await asyncio.gather(*tasks)

