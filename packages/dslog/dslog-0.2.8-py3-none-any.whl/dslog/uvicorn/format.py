from uvicorn.logging import AccessFormatter, DefaultFormatter
from ..stdlib import StdFormatter

ACCESS_FORMATTER = StdFormatter(AccessFormatter())
DEFAULT_FORMATTER = StdFormatter(DefaultFormatter())