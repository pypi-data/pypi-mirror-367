def uvicorn_logconfig(prefix: str):
  return {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
      "default": {
        "()": "uvicorn.logging.DefaultFormatter",
        "fmt": f"{prefix}%(levelprefix)s %(message)s",
        "use_colors": None,
      },
      "access": {
        "()": "uvicorn.logging.AccessFormatter",
        "fmt": f'{prefix}%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
      },
    },
    "handlers": {
      "default": {
        "formatter": "default",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stderr",
      },
      "access": {
        "formatter": "access",
        "class": "logging.StreamHandler",
        "stream": "ext://sys.stdout",
      },
    },
    "loggers": {
      "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
      "uvicorn.error": {"level": "INFO"},
      "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
  }