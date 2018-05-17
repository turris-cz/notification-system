import logging

# TODO: logger config file

logger = logging.getLogger("notifylib")
# just use DEBUG level for now...
logger.setLevel(logging.DEBUG)

# log to file for now...
fh = logging.FileHandler("notifylib.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

# TODO: log to syslog
