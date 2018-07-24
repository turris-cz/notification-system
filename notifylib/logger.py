import logging

from .config import config
# TODO: logger config file

logger = logging.getLogger("notifylib")
# just use DEBUG level for now...
logger.setLevel(logging.DEBUG)

# log to file for now...
fh = logging.FileHandler(config.get("settings", "logfile"))
fh.setLevel(logging.DEBUG)

#formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(filename)s:%(lineno)s - %(levelname)s - %(funcName)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

# TODO: log to syslog
