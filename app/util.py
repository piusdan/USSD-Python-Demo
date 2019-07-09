import datetime
import logging
import logging.config
import os

import yaml


def kenya_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=3)


def setup_logging(file_name="app_logger.yaml", default_level=logging.INFO, logger_file_path=None):
    """
    Logging configuration.
    """
    if logger_file_path is None:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "../", file_name))
    if os.path.exists(logger_file_path):
        with open(logger_file_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
