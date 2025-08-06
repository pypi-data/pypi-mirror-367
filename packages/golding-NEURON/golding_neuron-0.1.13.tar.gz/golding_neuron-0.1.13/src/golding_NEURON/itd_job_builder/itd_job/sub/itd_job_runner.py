from golding_NEURON.cell_calc import parentlist, section_list_length, tiplist
from golding_NEURON.cell import Cell
from golding_NEURON.sims import itd_test_sweep
from golding_NEURON.utils import get_cell_file_paths
from golding_NEURON import console_handler
import glob
import logging
import os

import pickle
import numpy as np
import pandas
from neuron import h

console_handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
h.nrnmpi_init()


def itd_task(kwargs):
    """
    Executes a single ITD test task.

    Parameters
    ----------
    kwargs : dict
        Dictionary of parameters for the ITD test.

    Returns
    -------
    tuple
        ITD threshold probabilities and cell name, optionally with traces.
    """
    logger.debug(f"Starting ITD task with parameters: {kwargs}")
    
    current_cell = Cell(*get_cell_file_paths(kwargs["temp_file_name"]))
    kwargs.pop("temp_file_name")
    name = current_cell.cell_name
    # list to store data
    itd_threshold_probabilities = np.zeros(
        int(kwargs["itd_range"] / kwargs["itd_step"]) + 1
    )

    # assign properties and categorized section lists
    current_cell.assign_properties(seg_density=0.5)
    # for key, kwarg in kwargs.items():
    # logger.info(f"{key}: {kwarg}")
    if kwargs["axon"]:
        current_cell.attach_axon()
        kwargs["record_axon"] = kwargs.pop("axon")
    if kwargs["excitation"]:
        if kwargs["innervation_pattern"] == "total" and  kwargs.pop("exc_gmax_csv",False) and os.path.isfile(
            "itd_cond_tuning.csv"
        ):
            # load the total innervation from the csv file
            logger.info("Loading total innervation from itd_cond_tuning.csv")
            cond_tuning = pandas.read_csv("itd_cond_tuning.csv").set_index("cell", drop=False)
            try: kwargs["exc_fiber_gmax"] = cond_tuning.loc[(cond_tuning["cell"]==name)&(cond_tuning["ipsp_mag"]==kwargs["inh_fiber_gmax"])].get("gmax")
            except: kwargs["exc_fiber_gmax"] = cond_tuning.loc[name,"gmax"]
                
        else:
            kwargs["exc_fiber_gmax"] = (
                kwargs["exc_fiber_gmax"]
            )
    else:
        kwargs["exc_fiber_gmax"] = 0
    kwargs.pop("excitation")

    dendrite_tips = tiplist(current_cell.dendrites_nofilopodia)
    # Check if the cell has dendrites that are too short to fit a synapse
    for tip in dendrite_tips:
        tip_path = parentlist(tip)
        path_length = section_list_length(current_cell, tip_path)[0]
        if path_length < kwargs["numsyn"] * kwargs["synspace"]:
            return {
                "name": name,
                "spike_counts": np.zeros(
                    (int(kwargs["itd_range"] / kwargs["itd_step"]) + 1)
                    if kwargs["itd_vals"] is None
                    else len(kwargs["itd_vals"])
                ),
                "traces": None,
            }

    # Run itd tests and return results
    test_results = itd_test_sweep(
        current_cell,
        current_cell.lateral_nofilopodia,
        current_cell.medial_nofilopodia,
        numtrial=1,
        **kwargs,
    )
    logger.info(f"Cell, {name}, finished ITD test")
    # print("kwargs",kwargs)
    test_results["name"] = name
    del current_cell

    return test_results


def save_csv(itd, name, *iterable_keys, **job_args):
    """
    Appends ITD test results into a CSV file.

    Parameters
    ----------
    itd : np.ndarray
        Array of ITD threshold probabilities.
    name : str
        Name of the cell.
    iterable_keys : tuple
        Keys of iterables used in the job.
    job_args : dict
        Arguments used for the ITD job.
    """
    logger.debug(f"Saving CSV for cell: {name}")
    sweep_data = {"name": name}
    for key in job_args:
        sweep_data[key] = job_args[key]
    
    if job_args["itd_vals"]:
        sort_inds = np.argsort(np.array(job_args["itd_vals"]))
        itd_vals = np.array(job_args["itd_vals"])[sort_inds]
        itd = np.array(itd)[sort_inds]
    else:
        itd_vals = np.arange(
            -job_args["itd_range"] / 2,
            job_args["itd_range"] / 2 + job_args["itd_step"],
            job_args["itd_step"],
        )
    if len(itd_vals) != len(itd):
        raise ValueError(
            f"Number of itd steps ({len(itd_vals)}) does not match number of itds tested ({len(itd)})"
        )
    for index, i in enumerate(itd_vals):
        sweep_data[i] = itd[index]
    df = pandas.DataFrame(sweep_data, index=[0])

    spreadsheetname = f"itd_data_{name}.csv"
    if os.path.isfile(spreadsheetname):
        df.to_csv(spreadsheetname, mode="a", header=False)
    else:
        df.to_csv(spreadsheetname, mode="a")
    logger.info(f"CSV saved successfully for cell: {name}")


def save_pickle(trace_ret, name, id, job_name=None, *iterable_keys, **job_args):
    """
    Saves trace data into a pickle file.

    Parameters
    ----------
    trace_ret : np.ndarray
        Trace data to be saved.
    name : str
        Name of the cell.
    id : int
        Unique identifier for the task.
    job_name : str, optional
        Name of the job. Default is None.
    iterable_keys : tuple
        Keys of iterables used in the job.
    job_args : dict
        Arguments used for the ITD job.
    """
    logger.debug(f"Saving pickle for cell: {name}, ID: {id}")
    folder_string = ""
    path_without_iter = (
        f"traces/{job_name}/{name}" if job_name is not None else f"traces/{name}"
    )

    if len(iterable_keys) != 0:
        for iterable in iterable_keys:
            folder_string += f"{iterable}_{job_args[iterable]}"
    else:
        folder_string = "no_iter"

    os.makedirs(f"{path_without_iter}/{folder_string}", exist_ok=True)
    with open(f"{path_without_iter}/{folder_string}/{id}.pkl", "wb") as handle:
        pickle.dump(trace_ret, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logger.info(f"Pickle saved successfully for cell: {name}, ID: {id}")


def load_jobinfo(pickle_path):
    """
    Loads job information from a pickle file.

    Parameters
    ----------
    pickle_path : str
        Path to the pickle file.

    Returns
    -------
    dict
        Dictionary containing tasks and iterables.
    """
    with open(pickle_path, "rb") as handle:
        tasks_and_iterables = pickle.load(handle)
    return tasks_and_iterables


def run_tasks(tasks, iterables, job_name="itd_job"):
    """
    Runs ITD tasks using NEURON's parallel context.

    Parameters
    ----------
    tasks : list
        List of tasks to be executed.
    iterables : dict
        Dictionary of iterables used in the job.
    job_name : str, optional
        Name of the job. Default is "itd_job".
    """
    logger.info(f"Running tasks for job: {job_name}")
    pc = h.ParallelContext()
    pc.runworker()

    iterated_dict = iterables
    submission_str = "Tasks submitted:\nargs:\n"
    for task in tasks:
        pc.submit(itd_task, task)
        submission_str += f"{task}\n"
    logger.debug(submission_str)
    while pc.working():
        # Retrieve the finished data from the parallel context
        id = pc.userid()
        submit_args = pc.upkpyobj()
        task_ret = pc.pyret()
        if submit_args["traces"]:
            save_pickle(
                task_ret,
                task_ret["name"],
                id,
                job_name,
                *iterated_dict.keys(),
                **submit_args,
            )
            logger.info(f"Traces saved for cell: {task_ret['name']}, ID: {id}")

        # log_string = f"{task_ret['name']} ({id}) data retrieved\nargs:\n"
        log_string = ""
        for arg, val in submit_args.items():
            if arg in iterated_dict:
                log_string += f"\033[1m{arg}:{val}\033[0m\n"
            else:
                log_string += f"{arg}:{val}\n"
        logger.debug(f"Task arguments: {submit_args}")
        logger.debug(log_string)

        # Save data into csv
        save_csv(
            task_ret["spike_counts"],
            task_ret["name"],
            *iterated_dict.keys(),
            **submit_args,
        )
        logger.info(f"{task_ret['name']} ({id}) csv entry saved")
    pc.done()
    logger.info("All tasks completed.")


def main(search_path=None):
    search_results = glob.glob(
        os.path.join(search_path, "*.pkl") if search_path is not None else "*.pkl"
    )
    if len(search_results) == 0:
        raise ValueError("No .pkl file found in the current directory.")
    elif len(search_results) > 1:
        raise ValueError("Multiple .pkl files found in the current directory.")
    task_path = search_results[0]
    logging.info(f"Using {task_path} as task file")
    tasks_and_iterables = load_jobinfo(task_path)
    iterables = tasks_and_iterables["iterables"]
    tasks = tasks_and_iterables["tasks"]
    run_tasks(tasks, iterables)


if __name__ == "__main__":
    main()
