from os import path
import sys

from loguru import logger


ROOT_DIR = path.dirname(path.abspath(__file__))

LOG_DIR = path.join(ROOT_DIR, "", "data", "log_file.log")

log_format = "<green>{time:DD-MM-YYYY at HH:mm:ss}</green> | <level>{level: <6}</level> | " \
             "<level><normal>{message}</normal></level>"

config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": log_format,
            "colorize": True,
            "enqueue": True,
            "backtrace": True,
            "diagnose": True,
        }
    ]
}

logger.configure(**config)


logger.add(LOG_DIR, enqueue=True, format=log_format, backtrace=True, diagnose=True)
