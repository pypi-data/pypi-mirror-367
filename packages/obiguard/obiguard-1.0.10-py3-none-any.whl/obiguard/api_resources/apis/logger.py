import json
import os
from typing import Optional
import requests

from obiguard.api_resources.global_constants import OBIGUARD_TRACE_URL


class Logger:
    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        api_key = api_key or os.getenv("PORTKEY_API_KEY")
        if api_key is None:
            raise ValueError("API key is required to use the Logger API")

        self.headers = {
            "Content-Type": "application/json",
            "x-obiguard-api-key": api_key,
        }

        self.url = (base_url or OBIGUARD_BASE_URL) + "/logs"

    def log(
        self,
        log_object,
    ):
        response = requests.post(
            url=self.url, data=json.dumps(log_object), headers=self.headers
        )

        return response
