import logging
import os
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union

import httpx
from tenacity import (
    RetryError,
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from synthera.utils import get_version

if TYPE_CHECKING:
    from synthera.fixed_income import FixedIncome

_logger: logging.Logger = logging.getLogger(__name__)

httpx_logger: logging.Logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

ENV_VAR_PREFIX: str = "SYNTHERA"
USER_AGENT_HEADER_PREFIX: str = "Synthera-Python-SDK"
API_KEY_HEADER: str = "X-API-Key"
APPLICATION_JSON_CONTENT_TYPE: str = "application/json"
SYNTHERA_API_HOST: str = "https://api.synthera.ai"
SYNTHERA_API_PORT: int = 443
SYNTHERA_API_VERSION: str = "v1"
SYNTHERA_API_TIMEOUT_SECS: int = 30
SYNTHERA_API_HEALTH_STATUS_ENDPOINT: str = "health/status"
SYNTHERA_API_HTTP_RETRIES: int = 5
SYNTHERA_API_HTTP_RETRY_WAIT_SECS: int = 2
SYNTHERA_API_HTTP_RETRY_EXCEPTIONS: tuple[type[Exception], ...] = (
    httpx.RequestError,
    httpx.HTTPStatusError,
)


class OutputFormat(Enum):
    TEXT = "text"
    JSON = "json"


class SyntheraClientError(Exception):
    pass


def should_retry(exception: BaseException) -> bool:
    """Determine if the request should be retried based on the exception."""
    if isinstance(exception, httpx.HTTPStatusError):
        # Don't retry on 400 Bad Request errors
        if exception.response.status_code == 400:
            return False
    return True


class SyntheraClient:
    host: str = SYNTHERA_API_HOST
    port: int = SYNTHERA_API_PORT
    api_version: str = SYNTHERA_API_VERSION
    api_key: str = ""
    timeout_secs: int = SYNTHERA_API_TIMEOUT_SECS
    _fixed_income: Optional["FixedIncome"] = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout_secs: Optional[int] = None,
    ) -> None:
        # Check for API key first
        env_api_key = os.getenv(f"{ENV_VAR_PREFIX}_API_KEY")
        if not api_key and not env_api_key:
            raise SyntheraClientError("API key is required")
        if api_key:
            self.api_key: str = api_key
        elif env_api_key:
            self.api_key: str = env_api_key

        env_host = os.getenv(f"{ENV_VAR_PREFIX}_API_HOST")
        if host:
            self.host: str = host
        elif env_host:
            self.host: str = env_host

        env_port = os.getenv(f"{ENV_VAR_PREFIX}_API_PORT")
        if port is not None:
            self.port: int = port
        elif env_port:
            self.port: int = int(env_port)

        try:
            self.port = int(self.port)
        except ValueError:
            raise SyntheraClientError("Port must be an integer")

        if self.port < 1 or self.port > 65535:
            raise SyntheraClientError("Port must be between 1 and 65535")

        env_timeout_secs = os.getenv(f"{ENV_VAR_PREFIX}_API_TIMEOUT_SECS")
        if timeout_secs is not None:
            self.timeout_secs = timeout_secs
        elif env_timeout_secs:
            self.timeout_secs = int(env_timeout_secs)

        try:
            self.timeout_secs = int(self.timeout_secs)
        except ValueError:
            raise SyntheraClientError("Timeout must be an integer")

        if self.timeout_secs < 1:
            raise SyntheraClientError("Timeout must be greater than 0")

        self.base_url: str = f"{self.host}:{self.port}"
        self.api_url: str = f"{self.base_url}/{self.api_version}"

        self.headers: dict[str, str] = {
            "User-Agent": self._get_user_agent(),
            API_KEY_HEADER: self.api_key,
            "Content-Type": APPLICATION_JSON_CONTENT_TYPE,
            "Accept": APPLICATION_JSON_CONTENT_TYPE,
        }

        _logger.info(f"Initialized Client with base url: {self.base_url}")

    def _get_user_agent(self) -> str:
        """Get the user agent header."""
        return f"{USER_AGENT_HEADER_PREFIX}/{get_version()}"

    @property
    def fixed_income(self) -> "FixedIncome":
        """Initialization of FixedIncome instance."""
        if self._fixed_income is None:
            from synthera.fixed_income import FixedIncome

            self._fixed_income = FixedIncome(self)
        return self._fixed_income

    def make_get_request(
        self,
        endpoint: str,
        include_version: bool = True,
        params: dict[str, Any] = {},
        output_format: OutputFormat = OutputFormat.JSON,
    ) -> Union[dict[str, Any], str]:
        """Centralized method to make HTTP GET requests."""
        if include_version:
            url: str = f"{self.base_url}/{self.api_version}/{endpoint}"
        else:
            url: str = f"{self.base_url}/{endpoint}"

        _logger.debug(f"Making GET request to {url}")

        try:
            response: httpx.Response = httpx.get(
                url, headers=self.headers, timeout=self.timeout_secs, params=params
            )
            response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
            if output_format == OutputFormat.TEXT:
                return response.text
            elif output_format == OutputFormat.JSON:
                return response.json()
        except httpx.TimeoutException:
            msg = f"Request timed out after {self.timeout_secs} seconds"
            _logger.error(msg)
            raise SyntheraClientError(msg)
        except httpx.RequestError as e:
            msg = f"A request error occurred: {e}"
            _logger.error(msg)
            raise SyntheraClientError(msg)
        except httpx.HTTPStatusError as e:
            msg = f"Error: {e.response.json()['detail']}"
            _logger.error(msg)
            raise SyntheraClientError(msg)
        except Exception as err:
            msg = f"An error occurred: {err}"
            _logger.error(msg)
            raise SyntheraClientError(msg)

    @retry(
        stop=stop_after_attempt(SYNTHERA_API_HTTP_RETRIES),
        wait=wait_fixed(SYNTHERA_API_HTTP_RETRY_WAIT_SECS),
        retry=retry_if_exception_type(SYNTHERA_API_HTTP_RETRY_EXCEPTIONS)
        & retry_if_exception(should_retry),
    )
    def _post_request(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Private method to make HTTP POST requests with retry logic."""
        _logger.debug(f"Making POST request to {url} with payload: {payload}")

        response: httpx.Response = httpx.post(
            url,
            json=payload,
            headers=self.headers,
            timeout=self.timeout_secs,
        )
        response.raise_for_status()
        return response.json()

    def make_post_request(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Centralized method to make HTTP POST requests."""
        url: str = f"{self.api_url}/{endpoint}"

        try:
            return self._post_request(url, payload)
        except RetryError as e:
            # Get the original exception that caused the retries to fail
            original_error = e.last_attempt.exception()
            err_msg = f"Request failed after {SYNTHERA_API_HTTP_RETRIES} attempts: {original_error}"
            _logger.error(err_msg)
            # re-raise from the original error
            raise SyntheraClientError(err_msg) from original_error
        except httpx.HTTPStatusError as e:
            msg = f"Error: {e.response.json()['detail']}"
            _logger.error(msg)
            raise SyntheraClientError(msg)
        except Exception as err:
            _logger.error(f"An error occurred: {err}")
            raise SyntheraClientError(f"An error occurred: {err}")

    def healthy(self) -> bool:
        """Check if the Synthera API is healthy."""
        endpoint: str = SYNTHERA_API_HEALTH_STATUS_ENDPOINT
        response = self.make_get_request(
            endpoint=endpoint,
            include_version=False,
            output_format=OutputFormat.TEXT,
        )

        if response == "ok":
            _logger.info("Synthera API is healthy")
            return True
        else:
            _logger.info("Synthera API is not healthy")
            return False

    @property
    def version(self) -> str:
        """Get the version of the Synthera SDK."""
        return get_version()
