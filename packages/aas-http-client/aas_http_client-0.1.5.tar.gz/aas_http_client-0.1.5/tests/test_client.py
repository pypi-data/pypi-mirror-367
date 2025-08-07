import pytest
from pathlib import Path
from aas_http_client.client import create_client_by_config, AasHttpClient

@pytest.fixture(scope="module")
def cloud_client() -> AasHttpClient:
    try:
        file = Path("./tests/test_server_config.json").resolve()
        
        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")
        
        client = create_client_by_config(file, password="")
    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    return client

def test_001_connect(cloud_client: AasHttpClient):
    print("Testing connection to the server...")
    assert cloud_client is not None