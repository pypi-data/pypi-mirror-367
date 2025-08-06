import os
import pytest
from carestack.base.base_types import ClientConfig
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client_config() -> ClientConfig:
    """
    Provides a ClientConfig instance initialized with API credentials from environment variables.

    Raises:
        ValueError: If API_KEY or API_URL environment variables are not set.

    Returns:
        ClientConfig: Configured with API key and URL.
    """

    api_key = "b6f6c8fea5ae8ff8dc1fd8cde279225735dc105cbe0378383c50aab85da0535814dcc0737d75303a4d735d7daa9219fac8a152308e6eb695a567b52c7de69906a"
    api_url = "http://localhost:4000/"
    x_hpr_id = "71-3351-1707-4245"

    if not api_key or not api_url:
        raise ValueError(
            "Missing required environment variables for API configuration."
        )
    return ClientConfig(api_key=api_key, api_url=api_url, x_hpr_id=x_hpr_id)
