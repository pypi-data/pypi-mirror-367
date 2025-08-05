from typing import Literal, Protocol, Generic, TypeVarTuple, TYPE_CHECKING
if TYPE_CHECKING:
  import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .types import Level, Handler, Formatter, value
from . import loggers, formatters

Objs = TypeVarTuple('Objs')

class LogFn(Protocol, Generic[*Objs]):
  def __call__(self, *objs: *Objs, level: Level = 'INFO'):
    ...

class Logger(ABC, LogFn[*Objs], Generic[*Objs]):
  @abstractmethod
  def __call__(self, *objs: *Objs, level: Level = 'INFO'):
    ...

  @classmethod
  def of(cls, handler: Handler) -> 'Logger':
    return LoggerOf(handler)

  @classmethod
  def click(cls) -> 'Logger':
    """`print` logger formatted with `click`"""
    return Logger.of(lambda *objs, **_: print(*objs)).format(formatters.click) 

  @classmethod
  def rich(cls) -> 'Logger':
    """Nicely formatted rich logger (use `loggers.rich` aka `Logger.of(rich.print)` for a non-formatted version)"""
    return loggers.rich().format(formatters.rich) 
  
  @classmethod
  def file(cls, filepath: str, *, mode: Literal['w', 'a'] = 'a') -> 'Logger[*Objs]':
    """Default formatted file logger (use `loggers.file` for a non-formatted version)"""
    return loggers.file(filepath, mode=mode).format(formatters.default) # type: ignore

  @classmethod
  def stderr(cls) -> 'Logger':
    import sys
    return Logger.of(lambda *objs, **_: print(*objs, file=sys.stderr))
  
  @classmethod
  def stdlib(cls, logger: 'logging.Logger | None' = None) -> 'Logger':
    """Logger from a `logging.Logger`. If not provided, uses `logging.getLogger()`"""
    import logging
    from .stdlib import handler
    return LoggerOf(handler(logger or logging.getLogger()))
  
  @classmethod
  def empty(cls) -> 'Logger':
    """*Objs logger that doesn't do anything"""
    return LoggerOf(lambda *_, **_kw: None)

  def limit(self, min_level: Level) -> 'Logger':
    return Limited(min_level, self)
  
  def format(self, format: Formatter[*Objs]) -> 'Logger[*Objs]':
    return Formatted(format, self)
  
  def prefix(self, prefix: str) -> 'Logger[*Objs]':
    return self.format(lambda *objs, **_: (prefix, *objs)) # type: ignore
  
  def postfix(self, postfix: str) -> 'Logger[*Objs]':
    return self.format(lambda *objs, **_: (*objs, postfix)) # type: ignore
  
@dataclass
class LoggerOf(Logger):
  handler: Handler
  def __call__(self, *objs, level: Level = 'INFO'):
    self.handler(*objs, level=level)

@dataclass
class Limited(Logger):
  min_level: Level | int
  logger: Logger

  def __call__(self, *objs, level: Level = 'INFO'):
    if value(level) >= value(self.min_level):
      self.logger(*objs, level=level)

@dataclass
class Formatted(Logger[*Objs]):
  formatter: Formatter[*Objs]
  logger: Logger

  def __call__(self, *objs, level: Level = 'INFO'):
    formatted_objs = self.formatter(*objs, level=level)
    self.logger(*formatted_objs, level=level)