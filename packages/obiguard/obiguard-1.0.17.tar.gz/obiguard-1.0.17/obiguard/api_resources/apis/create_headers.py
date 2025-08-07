import uuid
import json
from typing import Mapping

from obiguard_trace_python_sdk.constants.instrumentation.common import LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY
from opentelemetry import trace, baggage
from opentelemetry.trace import SpanKind, set_span_in_context, format_trace_id, format_span_id

from obiguard.api_resources.global_constants import OBIGUARD_ADDITIONAL_HEADERS_KEY
from obiguard.api_resources.utils import get_obiguard_header, traceparent_from_span

__all__ = ['createHeaders']


class CreateHeaders:
    def __init__(self, **kwargs) -> None:  # type: ignore
        self.kwargs = kwargs

    def json(self) -> Mapping:
        headers = {}
        forward_headers = self.kwargs.get("forward_headers", [])
        # Logic to accept both _ and - in forward_headers for devex
        if forward_headers:
            forward_headers = [
                "-".join(header.split("_")) for header in forward_headers
            ]
        for k, v in self.kwargs.items():
            # logic for boolean type headers
            if isinstance(v, bool):
                v = str(v).lower()
            if k == "mode" and "proxy" not in v:
                v = f"proxy {v}"
            k = "-".join(k.split("_"))
            if isinstance(v, Mapping):
                v = json.dumps(v)

            # James: k is now dash-separated.
            k_lower = k.lower()
            if v:
                if k_lower == 'traceparent':
                    headers['traceparent'] = v
                    continue

                if k_lower == 'request-id':
                    headers['x-request-id'] = v
                    continue

                if k_lower == 'obiguard-api-key':
                    headers['x-obiguard-api-key'] = v
                    continue

                if k_lower != "authorization":
                    if forward_headers and k in forward_headers:
                        headers[k] = str(v)
                    else:
                        headers[get_obiguard_header(k)] = str(v)
                else:
                    # Logic to add Bearer only if it is not present.
                    # Else it would be added everytime a request is made
                    if v.startswith("Bearer "):
                        headers[k] = v
                    else:
                        headers[k] = str("Bearer " + v)

                # logic for List of str to comma separated string
                if k == "forward-headers":
                    headers[get_obiguard_header(k)] = ",".join(v)

        return headers


def createHeaders(**kwargs):
    with trace.get_tracer(__name__).start_as_current_span(
        'obiguard.create.headers',
        kind=SpanKind.INTERNAL,
        context=set_span_in_context(trace.get_current_span()),
    ) as span:
        extra_attributes = baggage.get_baggage(LANGTRACE_ADDITIONAL_SPAN_ATTRIBUTES_KEY)
        if extra_attributes:
            span.set_attributes(extra_attributes)

        headers = CreateHeaders(**kwargs).json()

        extra_headers = baggage.get_baggage(OBIGUARD_ADDITIONAL_HEADERS_KEY)
        if extra_headers:
            headers.update(**extra_headers)

        headers['traceparent'] = traceparent_from_span(span)
        return headers
