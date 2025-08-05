from typing import NamedTuple, Literal
import logging
from ..logger import Logger

class UvicornLog(NamedTuple):
  client_addr: str
  method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
  full_path: str
  http_version: Literal['1.1', '2']
  status_code: int

class AccessHandler(logging.Handler):
    def __init__(self, logger: Logger[UvicornLog]):
      super().__init__()
      self.logger = logger
  
    def emit(self, record):
      self.logger(UvicornLog(*record.args), level=record.levelname) # type: ignore
