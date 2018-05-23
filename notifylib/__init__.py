import logging

from .config import config

# TODO: logger config file

logger = logging.getLogger(config["logging"]["logger_name"])
# just use DEBUG level for now...
logger.setLevel(logging.DEBUG)

# log to file for now...
fh = logging.FileHandler("notifylib.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

# TODO: log to syslog
