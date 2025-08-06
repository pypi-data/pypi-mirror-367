"""
Golding Lab NEURON Tools - A package for neuronal modeling and simulation

This package provides tools for compartmental modeling using the NEURON simulator,
with specialized modules for handling cell morphologies, running simulations, and
analyzing data related to interaural time difference (ITD) processing.
"""

import logging
import os
import platformdirs
from logging.handlers import TimedRotatingFileHandler
from neuron import h
from importlib.resources import files

# Import key modules for ease of access
from .cell import Cell
from .utils import (
    get_cell_file_paths,
    get_cell_file_path,
    get_package_path,
    get_config,
    reset_config,
)
from .compile_mechs import compile_mechs


__version__ = "0.1.0"

# Load NEURON 3D import file
h.load_file("import3d.hoc")


# Source:
# https://stackoverflow.com/questions/49049044/python-setup-of-logging-allowing-multiline-strings-logging-infofoo-nbar
class NewLineFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        """
        Override format function
        """
        msg = logging.Formatter.format(self, record)

        if record.message != "":
            parts = msg.split(record.message)
            msg = msg.replace("\n", "\n" + parts[0])

        return msg


DATEFORMAT = "%d-%m-%Y %H:%M:%S"
LOGFORMAT = "%(asctime)s %(levelname)-8s %(funcName)30s-%(filename)15s-%(lineno)-4s: %(message)s"
CONSOLEFORMAT = "golding_NEURON: %(levelname)-8s %(message)s"

log_formatter = NewLineFormatter(LOGFORMAT, datefmt=DATEFORMAT)
console_formatter = NewLineFormatter(CONSOLEFORMAT, datefmt=DATEFORMAT)
# Set up logging for the package
logger = logging.getLogger(__name__)
has_log_folder = os.path.isdir(platformdirs.user_log_dir("golding_NEURON"))
if not has_log_folder:
    # If the logs directory does not exist, create it
    os.makedirs(platformdirs.user_log_dir("golding_NEURON"), exist_ok=True)
# Set up a console handler for real-time logging output
console_handler = logging.StreamHandler(stream=os.sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)
print(platformdirs.user_log_dir("golding_NEURON"))
# Set up a timed rotating file handler for log rotation
rotate_handler = TimedRotatingFileHandler(
    os.path.join(platformdirs.user_log_dir("golding_NEURON"), "golding_NEURON.log"),
    backupCount=2,  # Keep logs for 2 rotations
    when="h",  # Rotate logs every hour
    interval=8,  # Rotate every 8 hours
)
rotate_handler.setLevel(logging.DEBUG)
rotate_handler.setFormatter(log_formatter)
logging.getLogger().addHandler(rotate_handler)
