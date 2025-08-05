from typing import TypeVarTuple
from rich import print
from ..logger import Logger
from ..types import Level

Objs = TypeVarTuple('Objs')

class rich(Logger[*Objs]):
  def __call__(self, *objs: *Objs, level: Level = 'INFO'):
    print(*objs)