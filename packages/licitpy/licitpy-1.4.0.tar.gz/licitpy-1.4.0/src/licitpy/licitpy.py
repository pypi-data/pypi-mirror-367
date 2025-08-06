from datetime import timedelta
from types import TracebackType
from typing import Optional, Type

from licitpy.core.http import AsyncHttpClient
from licitpy.countries.cl.provider import MercadoPublicoChileProvider
from licitpy.countries.eu.provider import EUTenderProvider


class Licitpy:
    def __init__(
        self,
        use_cache: bool = True,
        cache_expire_after: timedelta = timedelta(hours=1),
    ):
        self.downloader = AsyncHttpClient(
            use_cache=use_cache,
            cache_expire_after=cache_expire_after,
        )

        self._cl_provider: Optional[MercadoPublicoChileProvider] = None
        self._eu_provider: Optional[EUTenderProvider] = None

    async def __aenter__(self) -> "Licitpy":
        """Async context manager entry point."""
        await self.downloader.open()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Closes async resources when exiting an async context."""
        await self.downloader.close()

    @property
    def cl(self) -> MercadoPublicoChileProvider:
        """Lazy property for the Chile tender provider."""
        if self._cl_provider is None:
            self._cl_provider = MercadoPublicoChileProvider(self.downloader)

        return self._cl_provider

    @property
    def eu(self) -> EUTenderProvider:
        """Lazy property for the EU tender provider."""
        if self._eu_provider is None:
            self._eu_provider = EUTenderProvider(self.downloader)

        return self._eu_provider
