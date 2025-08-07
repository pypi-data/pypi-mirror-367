from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SyntheraClientProtocol(Protocol):
    """Protocol defining the interface that FixedIncome needs from SyntheraClient."""

    def make_post_request(
        self, endpoint: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Make a POST request to the Synthera API."""
        ...

    def make_get_request(
        self, endpoint: str, params: dict[str, Any] = {}
    ) -> dict[str, Any]:
        """Make a GET request to the Synthera API."""
        ...
