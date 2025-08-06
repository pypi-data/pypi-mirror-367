from typing import Optional

import httpx

from obiguard.api_resources.global_constants import OBIGUARD_HEADER_PREFIX


def parse_headers(headers: Optional[httpx.Headers]) -> dict:
    if headers is None:
        return {}

    _headers = {}
    for k, v in headers.items():
        if k.startswith(OBIGUARD_HEADER_PREFIX):
            k = k.replace(OBIGUARD_HEADER_PREFIX, "")
            _headers[k] = v

    return _headers
