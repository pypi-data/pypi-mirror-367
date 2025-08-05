# Dead Simple Logging

> What python's `logging` should've been

## Installation

```bash
pip install dslog
```

## Usage

- Any custom "handler" (aka function to actually print)

```python
import rich
from dslog import Logger

logger = Logger.of(rich.print) \
  .limit('WARNING') \
  .format(lambda *objs, level: (f'[bold][{level}][/]', *objs))

logger('My message', ..., level='INFO')
# doesn't print anything
logger('Oops!', { 'more': 'details' }, level='WARNING')
# [WARNING] Oops! { 'more', 'details' }     ([WARNING] in bold text)
```

- Or some of the predefined ones, which come already formatted

```python
Logger.rich()
Logger.file('log.txt')
```

- Or the best default logger

```python
Logger.empty()
```

## `uvicorn`/`fastapi` Logging

If you've used it before, you know it sucks. No more:

```python
from fastapi import FastAPI
import uvicorn
from dslog import Logger
from dslog.uvicorn import setup_loggers_lifespan, DEFAULT_FORMATTER, ACCESS_FORMATTER

logger = Logger.click().prefix('[MY API]')

app = FastAPI(lifespan=setup_loggers_lifespan(
  access=logger.prefix('[ACCESS]').format(ACCESS_FORMATTER).limit('WARNING'),
  uvicorn=logger.format(DEFAULT_FORMATTER).limit('INFO'),
))

uvicorn.run(app)

# The initial logs will run (uvicorn is quite stubborn):

# INFO: Started server process [95349]
# INFO: Waiting for application startup.

# But then, all the logs are controlled by you (ie. your logger)

# [INFO] [MY API] Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# [WARNING] [MY API] [ACCESS] ...
```