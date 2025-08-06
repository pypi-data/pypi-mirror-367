"""
This module provides utility functions for the golding_NEURON package, such as file path helpers.
"""

import logging
import os
import json
import platformdirs
from importlib.resources import files
from shutil import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_cell_file_paths(*filenames: str) -> list[str]:
    """
    Return a list[str] of filepaths to cell morphology files inside the package's 'cells' directory. If no filenames are provided, it returns all cell files included in the package directory.
    Usage:
    >>> from golding_NEURON.utils import get_cell_file_paths
    >>> from golding_NEURON.cell import Cell
    >>> cell_file_path = get_cell_file_paths("example_cell.asc")
    >>> cell = Cell(cell_file_path)
    ...

    Parameters
    ----------
    filenames: str
        Optional variable number of filenames to search for in the package's 'cells' directory.

    Returns
    -------
    list:
        A list of file paths to the cell morphology files.
    """

    cell_files = []
    if not filenames:
        cell_files = [
            file for file in files("golding_NEURON").joinpath("cells").iterdir()
        ]
    else:
        for filename in filenames:
            if not isinstance(filename, str):
                raise TypeError(f"Filename ({filename}) must be a string.")
            files_with_name = [
                file_with_name
                for file_with_name in files("golding_NEURON")
                .joinpath("cells")
                .iterdir()
                if filename in file_with_name.name
            ]
            if len(files_with_name) > 1:
                raise FileNotFoundError(
                    f"Multiple cell files containing name {filename} found in package data. Please specify a unique filename."
                )
            if len(files_with_name) == 0:
                raise FileNotFoundError(
                    f"Cell file {filename} not found in package data."
                )
            cell_files.append(str(files_with_name[0]))
    return cell_files


def get_cell_file_path() -> str:
    """
    Get the path to the cell morphology files directory.

    Returns
    -------
    str:
        The path to the 'cells' directory within the golding_NEURON package.
    """
    return str(files("golding_NEURON").joinpath("cells"))


def reset_config():
    """
    Reset the configuration of the golding_NEURON package to its default state.
    This function is useful for testing purposes or when you want to clear any custom configurations.
    """

    try:
        if not platformdirs.user_config_path("golding_NEURON").is_dir():
            # Create the user config directory if it does not exist
            platformdirs.user_config_path("golding_NEURON").mkdir(
                parents=True, exist_ok=True
            )
        copy(
            files("golding_NEURON").joinpath("golding_NEURON_default_config.json"),
            str(platformdirs.user_config_path("golding_NEURON"))+"/golding_NEURON_config.json",
        )
        copy(
            files("golding_NEURON").joinpath("golding_NEURON_default_config.json"),
            str(platformdirs.user_config_path("golding_NEURON"))+"/golding_NEURON_default_config.json",
        )
        logger.info("Default configuration files copied to user config directory.")
    except FileNotFoundError:
        logger.exception(
            "Default configuration file 'golding_NEURON_default_config.json' not found. "
            "You may need to reinstall the golding_NEURON package or replace the file manually.",
        )
    return get_config()


def get_config(config_path: str = None) -> dict:
    """
    Get the current configuration of the golding_NEURON package.

    Returns
    -------
    dict:
        The current configuration as a dictionary.

    Raises
    ------
    FileNotFoundError:
        If the configuration file 'golding_NEURON_config.json' does not exist in the user config path.
    """

    if config_path is None:
        config_path = os.path.join(
            platformdirs.user_config_path("golding_NEURON")
            / "golding_NEURON_config.json"
        )

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            "Configuration directory 'golding_NEURON' not found in user config path. "
            "Please run reset_config() to create the default configuration."
        )

    with open(
        platformdirs.user_config_path("golding_NEURON") / "golding_NEURON_config.json",
        "r",
    ) as f:
        config = json.load(f)

    return config


def get_package_path() -> str:
    """
    Get the path to the golding_NEURON package directory.

    Returns
    -------
    str:
        The path to the golding_NEURON package directory.
    """
    return str(files("golding_NEURON").joinpath(""))
