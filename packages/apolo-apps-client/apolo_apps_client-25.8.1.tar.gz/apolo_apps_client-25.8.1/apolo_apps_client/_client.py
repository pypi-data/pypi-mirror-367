import logging
from types import TracebackType

import aiohttp
from yarl import URL

from ._config import AppsClientConfig
from ._exceptions import AppsApiException
from ._models import AppInstance


LOGGER = logging.getLogger(__name__)


class AppsApiClient:
    def __init__(
        self,
        config: AppsClientConfig,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
        trace_configs: list[aiohttp.TraceConfig] | None = None,
    ):
        self._url = URL(config.url)
        self._token = config.token
        self._timeout = timeout
        self._trace_configs = trace_configs

    def _base_version_url(self, version: str) -> URL:
        return self._url / "apis" / "apps" / version

    def _get_apps_url(self, version: str) -> URL:
        return self._base_version_url(version) / "instances"

    def _get_app_url(self, instance_id: str, version: str) -> URL:
        return self._get_apps_url(version) / instance_id

    async def __aenter__(self) -> "AppsApiClient":
        self._client = self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    def _create_http_client(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            timeout=self._timeout,
            trace_configs=self._trace_configs,
            raise_for_status=_raise_for_status,
        )

    async def aclose(self) -> None:
        assert self._client
        await self._client.close()

    def _create_default_headers(self, token: str | None) -> dict[str, str]:
        result = {}
        if token or self._token:
            result["Authorization"] = f"Bearer {token or self._token}"
        return result

    async def get_app(
        self,
        app_instance_id: str,
        token: str | None = None,
    ) -> AppInstance:
        async with self._client.get(
            self._get_app_url(instance_id=app_instance_id, version="v2"),
            headers=self._create_default_headers(token),
        ) as response:
            response_json = await response.json()
            return AppInstance(**response_json)

    async def get_app_by_name(
        self,
        app_instance_name: str,
        token: str | None = None,
    ) -> AppInstance:
        async with self._client.get(
            self._get_apps_url(version="v2"),
            headers=self._create_default_headers(token),
            params={"name": app_instance_name},
        ) as response:
            response_json = await response.json()
            if len(response_json["items"]) != 1:
                exc_txt = f"App instance with name '{app_instance_name}' not found."
                raise AppsApiException(
                    code=404,
                    message=exc_txt,
                )
            return AppInstance(**response_json["items"][0])


async def _raise_for_status(response: aiohttp.ClientResponse) -> None:
    exc_text = None
    match response.status:
        case 401:
            exc_text = "Platform-apps: Unauthorized"
        case 402:
            exc_text = "Platform-apps: Payment Required"
        case 403:
            exc_text = "Platform-apps: Forbidden"
        case 404:
            exc_text = "Platform-apps: Not Found"
        case _ if not 200 <= response.status < 300:
            text = await response.text()
            exc_text = (
                f"Platform-apps api response status is not 2xx. "
                f"Status: {response.status} Response: {text}"
            )
    if exc_text:
        raise AppsApiException(code=response.status, message=exc_text)
    return
