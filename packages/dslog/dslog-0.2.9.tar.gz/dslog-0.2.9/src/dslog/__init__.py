"""
### Dslog
> Dead-simple logging: just function composition

```
from dslog import Logger

logger = Logger.of(rich.print) \\
  .limit('WARNING') \\
  .format(lambda level, *objs, (f'[green][{level}][/]', *objs))

logger('My message', ..., level='INFO')
# doesn't print anything
logger('Oops!', { 'more': 'details' }, level='WARNING')
# [WARNING] Oops! { 'more', 'details' }     ([WARNING] in green)
```
"""
import lazy_loader as lazy
__getattr__, __dir__, __all__ = lazy.attach_stub(__name__, __file__)