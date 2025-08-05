from typing import Protocol, Literal, Sequence, TypeVar, TypeVarTuple, Generic

Level = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LEVELS: Sequence[Level] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LEVEL_VALUES: dict[Level, int] = {
  'DEBUG': 10,
  'INFO': 20,
  'WARNING': 30,
  'ERROR': 40,
  'CRITICAL': 50,
}

def value(level: Level | int) -> int:
  return level if isinstance(level, int) else LEVEL_VALUES[level]

Objs = TypeVarTuple('Objs')
Objs2 = TypeVarTuple('Objs2')
A = TypeVar('A')
B = TypeVar('B')

class Handler(Protocol, Generic[*Objs]):
  """Just prints out shit"""
  def __call__(self, *objs: *Objs, level: Level):
    ...

As = TypeVarTuple('As')

class Formatter(Protocol, Generic[*Objs]):
  """Formats log inputs"""
  def __call__(self, *objs: *Objs, level: Level) -> Sequence:
    ...

