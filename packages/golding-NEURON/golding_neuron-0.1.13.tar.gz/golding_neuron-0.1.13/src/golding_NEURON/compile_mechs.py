"""
This module provides a command-line utility to compile NEURON mechanisms using nrnivmodl.
"""

import argparse
import logging
import os
import shutil
import subprocess

from importlib.resources import files
from neuron import h
from pathlib import Path
from shutil import rmtree


parser = argparse.ArgumentParser(description="A script to compile NEURON mechanisms.")
parser.add_argument(
    "mechdir", help="The name of the directory holding the mechanisms to compile"
)
parser.add_argument(
    "-wd",
    "--workdir",
    default=None,
    help="The working directory to compile the mechanisms in. Defaults to the current directory.",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose output"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def load_dll(dll_path: str):
    """
    Load a compiled NEURON mechanism DLL.
    """
    if os.path.exists(dll_path):
        logger.info(f"Loading compiled mechanisms from {dll_path}")
        try:
            h.nrn_load_dll(dll_path)
        except Exception as e:
            logger.error(f"Error loading DLL: {e}")
            raise e
    else:
        logger.error(f"Compiled mechanism library not found at {dll_path}")
        raise FileNotFoundError(f"Compiled mechanism library not found at {dll_path}")
    
def compile_mechs(mech_path: str = None, workdir: str = None, nrnivmodl_path: str = None):
    """
    Compile NEURON mechanisms in the specified directory using nrnivmodl.
    """
    logger.info("Starting mechanism compilation")
    # if mech_path is None:
    #     raise ValueError("mech_path not specified.")
    mech_path = (
        mech_path if mech_path else files("golding_NEURON").joinpath("mechanisms")
    )
    cwd = workdir if workdir is not None else os.getcwd()
    nrnivmodl_path = nrnivmodl_path if nrnivmodl_path is not None else 'nrnivmodl'
    
    logger.debug(f"Current working directory: {cwd}")
    logger.debug(f"Mechanism path: {mech_path}")
    if os.path.isdir(cwd + "/x86_64"):
        os.rename(cwd + "/x86_64", cwd + "/x86_64_old")
        rmtree(cwd + "/x86_64_old")
    try:
        logger.debug(f"Running nrnivmodl with command: {f'{nrnivmodl_path} {str(Path(mech_path))}'}")
        logger.debug(subprocess.run(f'{nrnivmodl_path} {str(Path(mech_path))}', cwd=str(cwd), check = True, shell=True, capture_output=True))
    except: 
        try:
            logger.error("Failed to run with shell = True.")
            logger.debug(subprocess.run([nrnivmodl_path, str(Path(mech_path))], cwd=str(cwd), check=True,  capture_output=True))
        except: 
            logger.error("Failed to run nrnivmodl. Ensure it is installed and in your PATH.")
    dll_paths = ['/x86_64/.libs/libnrnmech.so', r"\nrnmech.dll"]
    for dll_path in dll_paths:
        full_path = cwd + dll_path
        if os.path.exists(full_path):
            logger.info(f"Loading compiled mechanism from {full_path}")
            try:h.nrn_load_dll(full_path)
            except: pass
    # try:
    #     if os.path.exists(cwd + "/x86_64/.libs/libnrnmech.so"):
    #         h.nrn_load_dll(f"{cwd}/x86_64/.libs/libnrnmech.so")
    #     elif os.path.exists(cwd + r"\nrnmech.dll"):
    #         h.nrn_load_dll(f'{cwd}\nrnmech.dll')
    #     else:
    #         raise FileNotFoundError(
    #             "Compiled mechanism library not found."
    #         )
    # except Exception as e:
        # logger.error(f"Error loading compiled mechanisms: {e}")
        # raise e


def main():
    """
    Parse command-line arguments and compile NEURON mechanisms.
    """
    args = parser.parse_args()
    mechdir = (
        Path(os.getcwd())/args.mechdir
        if args.mechdir
        else files("golding_NEURON").joinpath("mechanisms")
    )
    workdir = args.workdir if args.workdir else os.path.dirname(mechdir)
    print(mechdir, workdir)
    logger.info(f"Current directory: {workdir}")
    logger.info(f"Mechanism directory: {mechdir}")
    compile_mechs(workdir=workdir, mech_path=mechdir)


if __name__ == "__main__":
    main()
