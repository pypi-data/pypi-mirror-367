from typing import Any


class ClientConfig:
    """
    Configuration object for initializing API clients.

    Attributes:
        api_key (str): The API key used for authenticating requests.
        api_url (str): The base URL of the API endpoint.
        hprid_auth (str): The HPR ID or additional authentication header value.
    """

    def __init__(self, api_key: str, api_url: str, x_hpr_id: str) -> None:
        self.api_key = api_key
        self.api_url = api_url
        self.hprid_auth = x_hpr_id


class ApiResponse:
    """
    Standardized structure for API responses.

    Attributes:
        data (Any): The response payload or data returned from the API.
        status (int): The HTTP status code or custom status indicator.
        message (str): Informational or error message related to the response.
    """

    def __init__(self, data: Any, status: int, message: str) -> None:
        self.data = data
        self.status = status
        self.message = message
