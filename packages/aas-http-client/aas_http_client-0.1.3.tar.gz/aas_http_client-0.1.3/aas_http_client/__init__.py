from datetime import datetime
import importlib.metadata

__copyright__ = f"Copyright (C) {datetime.now().year} :em engineering methods AG. All rights reserved."
__author__ = "Daniel Klein"

__version__ = importlib.metadata.version(__name__)
__project__ = "aas-http-client"
__package__ = "aas-http-client"

from aas_http_client.client import create_client_by_config, create_client_by_url, AasxServerInterface

__all__ = ["create_client_by_config", "create_client_by_url"]