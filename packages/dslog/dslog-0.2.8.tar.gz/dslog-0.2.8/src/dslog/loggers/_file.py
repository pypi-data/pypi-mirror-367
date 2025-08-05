from typing import Literal
from ..types import Handler, Level
from ..logger import Logger

class FileHandler(Handler):

  def __init__(self, filepath: str, mode: Literal['a', 'w'] = 'w'):
    self.filepath = filepath
    if mode == 'w':
      with open(filepath, 'w'):
        ...

  def __call__(self, *objs, level: Level = 'INFO'):
    with open(self.filepath, 'a') as f:
      print(*objs, file=f)


def file(filepath: str, mode: Literal['a', 'w'] = 'w'):
  return Logger.of(FileHandler(filepath, mode))
