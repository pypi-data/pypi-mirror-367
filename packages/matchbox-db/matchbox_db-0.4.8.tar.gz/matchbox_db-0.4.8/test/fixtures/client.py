from os import environ
from typing import Callable, Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from matchbox.client._settings import settings as client_settings
from matchbox.server import app
from matchbox.server.api.dependencies import backend, settings


@pytest.fixture(scope="function")
def env_setter() -> Generator[Callable[[str, str], None], None, None]:
    """Set temporary env variable and refresh client settings."""
    original_values = {}

    def setter(var_name: str, var_value: str):
        original_values[var_name] = environ.get(var_name)

        environ[var_name] = var_value
        client_settings.__init__()

    yield setter

    for var_name, original_value in original_values.items():
        if original_value is None:
            del environ[var_name]
        else:
            environ[var_name] = original_value
    client_settings.__init__()


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """Return a configured TestClient with patched backend and settings."""
    with (
        patch("matchbox.server.api.dependencies.settings") as mock_settings,
        patch("matchbox.server.api.dependencies.backend") as mock_backend,
    ):
        mock_settings.api_key = SecretStr("test-api-key")

        app.dependency_overrides[backend] = lambda: mock_backend
        app.dependency_overrides[settings] = lambda: mock_settings

        yield TestClient(app, headers={"X-API-Key": "test-api-key"})

        app.dependency_overrides.clear()
