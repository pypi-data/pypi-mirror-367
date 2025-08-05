from typing import TypedDict, NotRequired, Unpack
import logging
from ..stdlib import StdHandler
from .. import Logger
from .format import DEFAULT_FORMATTER, ACCESS_FORMATTER

class UvicornLoggers(TypedDict):
  access: NotRequired[Logger[logging.LogRecord]]
  uvicorn: NotRequired[Logger[logging.LogRecord]]
  error: NotRequired[Logger[logging.LogRecord]]

def setup_loggers(**loggers: Unpack[UvicornLoggers]):
  """
  Overrides the default uvicorn loggers with the provided loggers.
  - `access`: used for `'uvicorn.access'`. Defaults to the usual uvicorn style
  - `uvicorn`: used for `'uvicorn'`. Defaults to the usual uvicorn style`
  - `error`: used for `'uvicorn.error'. Defaults to `Logger.etmpy()`

  Note that `'uvicorn'` and `'error'` tend do overlap, so setting `'uvicorn'` only should suffice
  """
  access = loggers.get('access') or Logger.click().format(ACCESS_FORMATTER)
  uvicorn = loggers.get('uvicorn') or Logger.click().format(DEFAULT_FORMATTER)
  error = loggers.get('error') or Logger.empty()
  logging.getLogger('uvicorn.access').handlers = [StdHandler(access)]
  logging.getLogger('uvicorn').handlers = [StdHandler(uvicorn)]
  logging.getLogger('uvicorn.error').handlers = [StdHandler(error)]

def setup_loggers_lifespan(**loggers: Unpack[UvicornLoggers]):
  """
  Lifespan to override the default uvicorn loggers with the provided loggers.
  - `access`: used for `'uvicorn.access'`. Defaults to the usual uvicorn style
  - `uvicorn`: used for `'uvicorn'`. Defaults to the usual uvicorn style`
  - `error`: used for `'uvicorn.error'. Defaults to `Logger.etmpy()`

  Note that `'uvicorn'` and `'error'` tend do overlap, so setting `'uvicorn'` only should suffice
  """
  from contextlib import asynccontextmanager
  @asynccontextmanager
  async def lifespan(app):
    setup_loggers(**loggers)
    yield
  return lifespan