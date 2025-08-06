"""
This module provides the ITDJob class for managing and generating interaural time difference (ITD) simulation tasks.
"""

# Import necessary libraries and define global variables for parameters
import copy
import itertools
import logging
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ITDJob:
    """
    Represents a job for interaural time difference (ITD) testing.

    This class handles the configuration, task generation, and parameter
    management for ITD simulations.
    """

    def __init__(
        self,
        filenames,
        iterables,
        **kwargs,
    ):
        """
        Initializes the ITDJob instance.

        Parameters
        ----------
        filenames : list
            List of filenames for the cells to be tested.
        iterables : list
            List of parameters to iterate over during task generation.
        kwargs : dict
            Additional arguments passed to itd_task
        """
        # Set attributes from kwargs
        self.__dict__.update(kwargs)

        self.itd_args = {
            "axon": self.axon,
            "inhibition": self.inhibition,
            "excitation": self.excitation,
            "threshold": self.threshold,
            "numsyn": self.numsyn,
            "synspace": self.synspace,
            "numfiber": self.numfiber,
            "exc_fiber_gmax": self.exc_fiber_gmax,
            "inh_fiber_gmax": self.inh_fiber_gmax,
            "inh_timing": self.inh_timing,
            "axonspeed": self.axonspeed,
            "absolute_threshold": self.absolute_threshold,
            "traces": self.traces,
            "itd_range": kwargs["itd_range"],
            "itd_step": kwargs["itd_step"],
            "parallel": False,
            "itd_vals": kwargs["itd_vals"],
            "innervation_pattern": kwargs["innervation_pattern"],
            "exc_gmax_csv": kwargs.get("use_csv", None),
        }
        if self.itd_args["itd_vals"] is None:
            self.itd_vals = np.arange(
                -(self.itd_args["itd_range"] / 2),
                self.itd_args["itd_range"] / 2 + self.itd_args["itd_step"],
                self.itd_args["itd_step"]
            )
        else:
            self.itd_vals = self.itd_args["itd_vals"]
        logger.info(f"itd_vals: {self.itd_args['itd_vals']}")
        self.iterables = iterables
        self.filenames = filenames


    def generate_tasks(self) -> list[dict[str, any]]:
        """
        Generates a list of tasks for ITD testing.

        Tasks are created based on the provided cell names, iterables and passed itd_task arguments
        """
        task_list = []



        for temp_filename in self.filenames:
            
            iterable_arrays = {}
            self.itd_args["temp_file_name"] = temp_filename

            if self.iterables:
                for iterable_key in self.iterables:
                    start, stop, step = self.iterables[iterable_key]
                    if start > stop:
                        step = -step
                    iterable_arrays[iterable_key] = list(
                        np.arange(start, stop + step / 2, step)
                    )

                logger.info(f"iterable_arrays: {list(iterable_arrays.values())}")
                combinations = itertools.product(*list(iterable_arrays.values()))
                for combination in combinations:
                    logger.info(f"combo: {combination}")
                    for val, key in zip(combination, self.iterables):
                        self.itd_args[key] = val
                    task_list.extend([copy.deepcopy(self.itd_args) for _ in range(int(self.itd_trials))])
            else:
                task_list.extend([copy.deepcopy(self.itd_args) for _ in range(int(self.itd_trials))])
        return task_list

    # Make a list of all iterated delay values
    # create a function to be called several times by NEURON's parellel context