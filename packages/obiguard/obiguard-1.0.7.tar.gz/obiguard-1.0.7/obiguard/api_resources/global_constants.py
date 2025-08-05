import httpx


MISSING_API_KEY_ERROR_MESSAGE = """Obiguard API Key Not Found \

Resolution: \

1. Get your Obiguard API key from https://obiguard.ai
2. Pass it while instantiating the Obiguard client with obiguard_api_key param.
"""

MISSING_BASE_URL = """No Base url provided. Please provide a valid base url.
For example: https://openai.obiguard.ai
"""

MISSING_CONFIG_MESSAGE = (
    """The 'config' parameter is not set. Please provide a valid Config object."""
)
MISSING_MODE_MESSAGE = (
    """The 'mode' parameter is not set. Please provide a valid mode literal."""
)

INVALID_OBIGUARD_MODE = """
Argument of type '{}' cannot be assigned to parameter "mode" of \
    type "ModesLiteral | Modes | None"
"""

LOCALHOST_CONNECTION_ERROR = """Could not instantiate the Obiguard client. \
You can either add a valid `api_key` parameter (from https://obiguard.ai)\
or check the `base_url` parameter in the Portkey client, \
for your AI Gateway's instance's URL.
"""

CUSTOM_HOST_CONNECTION_ERROR = """We could not connect to the AI Gateway's instance. \
Please check the `base_url` parameter in the Portkey client.
"""

DEFAULT_MAX_RETRIES = 2
VERSION = "0.1.0"
DEFAULT_TIMEOUT = 60
OBIGUARD_HEADER_PREFIX = "x-obiguard-"
# PORTKEY_HEADER_PREFIX = "x-portkey-"
# PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
OBIGUARD_BASE_URL = "https://gateway.obiguard.ai/v1"
OBIGUARD_TRACE_URL = "https://gateway.obiguard.ai/api/trace"
# PORTKEY_GATEWAY_URL = PORTKEY_BASE_URL
OBIGUARD_GATEWAY_URL = OBIGUARD_BASE_URL
LOCAL_BASE_URL = "http://localhost:8787/v1"
# PORTKEY_API_KEY_ENV = "PORTKEY_API_KEY"
OBIGUARD_API_KEY_ENV = "OBIGUARD_API_KEY"
# PORTKEY_PROXY_ENV = "PORTKEY_PROXY"
OBIGUARD_PROXY_ENV = "OBIGUARD_PROXY"
OPEN_AI_API_KEY = "OPENAI_API_KEY"
DEFAULT_CONNECTION_LIMITS = httpx.Limits(
    max_connections=1000, max_keepalive_connections=100
)
# AUDIO_FILE_DURATION_HEADER = "x-portkey-audio-file-duration"
AUDIO_FILE_DURATION_HEADER = "x-obiguard-audio-file-duration"
OBIGUARD_ADDITIONAL_HEADERS_KEY = "obiguard_additional_headers"