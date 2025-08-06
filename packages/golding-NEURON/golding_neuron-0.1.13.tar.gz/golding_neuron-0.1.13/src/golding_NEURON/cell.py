"""
This module defines the Cell class for loading and manipulating neuronal morphologies in NEURON.
"""

import logging
import math
import numpy as np
import time
from pathlib import Path
from neuron import h
from collections.abc import Callable
from typing import Self
from .utils import get_config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ParamDict(dict):
    """
    A dictionary-like class that resets cell properties when cell attributes are changed,
    to force reevaluating old cell measurements with previous attributes.
    """

    def __init__(self, input_dict, cell):
        self.cell = cell
        super().__init__(input_dict)
        for item in self.items():
            if isinstance(item[1], dict):
                self[item[0]] = type(self)(item[1], self.cell)
            else:
                self[item[0]] = item[1]

    def __setitem__(self, key, value):
        self.cell._reset_properties()
        item = super().__setitem__(key, value)
        if getattr(self.cell, "channels_assigned", False):
            logger.info(f"Reassigning channels after changing {key} to {value}.")
            self.cell._reset()
        return item
    
    def convert_to_dict(self):
        """
        Returns a dictionary representation of the ParamDict.
        """
        tmp = {k: v for k, v in self.items()}
        for k, v in tmp.items():
            if isinstance(v, ParamDict):
                tmp[k] = v.convert_to_dict()
        return tmp
    
    def __dict__(self):
        """
        Returns a dictionary representation of the ParamDict.
        """
        return self.convert_to_dict()


class Cell:
    """
    Represents a neuron cell loaded from a morphology file, with methods for simulation and analysis in NEURON.
    """

    # Enable variable timestep to optimize simulation runtimes

    def __init__(self, cell_file: str, config_path: str = None) -> None:
        """
        Initializes the Cell instance by loading a morphology file.

        Parameters
        ----------
        cell_file : str
            Filepath to a morphology file in .asc format from Neurolucida.
        """
        self._load_default_values(config_path=config_path)
        self._initialize_cell(cell_file)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Cell instance.
        """
        return f"Cell('{self.cell_name}')"

    # TODO decide if this should be public
    def _assign_channels(
        self,
        parts: list[str] = None,
        **kwargs: dict[str, float | Callable[[Self], float]],
    ) -> None:

        parts_lookup = {
            "dendrite": getattr(self, "dendrites", None),
            "soma": getattr(self, "somatic", None),
            "node": getattr(self, "nodes", None),
            "internode": getattr(self, "internodes", None),
            "tais": [getattr(self, "tais", None)],
            "cais": [getattr(self, "cais", None)],
        }
        for part in parts:
            if parts_lookup.get(part) is None:
                raise ValueError(
                    f"Part '{part}' not found in the cell. Available parts: {list(parts_lookup.keys())}."
                )
            for sec in parts_lookup[part]:
                self.accessed_section = sec
                for channel in self.channels:
                    if self.conductances[part].get(channel, 0) != 0:
                        logger.debug(
                            f"Inserting channel '{channel}' with mechanism '{self.channels[channel]['mechanism']}' to section {sec.name()}"
                        )
                        sec.insert(self.channels[channel]["mechanism"])
                    else:
                        continue

                    if self.channels[channel]["ion"] is not None:
                        setattr(
                            sec,
                            f"e{self.channels[channel]['ion']}",
                            self.channels[channel]["reversal_potential"],
                        )
                    for seg in sec:
                        self.accessed_segment = seg
                        logger.debug(f"Setting channel conductance, {channel}, to {self.conductances[part][channel]} for section {sec.name()} at segment {seg.x}")
                        self._set_channel_cond(
                            seg,
                            channel,
                            self.channels[channel]["mechanism"],
                            part,
                            cond_label=self.channels[channel]["cond_label"],
                            **kwargs,
                        )
                        try:
                            setattr(
                                getattr(seg, self.channels["leak"]["mechanism"]),
                                "e",
                                self.channels["leak"]["reversal_potential"],
                            )
                        except:
                            pass
        self.channels_assigned = True

    def _create_axon_sections(self, num_nodes=5) -> None:
        self.axonal = []
        self.tais = h.Section(name="tais", cell=self)
        self.tais.nseg = 3
        self.tais.L = 10
        for segnum, seg in enumerate(self.tais):
            # tapering initial segment
            seg.diam = 1.64 - (((segnum + 1) / self.tais.nseg) * (1.64 - 0.66))
        self.tais.connect(self.somatic[0](0.5))
        self.allsec_nofilopodia.append(self.tais)
        self.axonal.append(self.tais)

        self.cais = h.Section(name="cais", cell=self)
        self.cais.nseg = 3
        self.cais.L = 10
        self.cais.diam = 0.66
        self.cais.connect(self.tais)
        self.allsec_nofilopodia.append(self.cais)
        self.axonal.append(self.cais)
        # creating and attaching node/internode pairs (default is 5)
        self.internodes = []
        self.nodes = []
        for ax_part_num in range(num_nodes):
            internode = h.Section(name=f"internode_{ax_part_num}", cell=self)
            internode.L = 100
            internode.diam = 0.98
            internode.cm = 0.0111
            internode.connect(self.axonal[-1])
            self.internodes.append(internode)
            self.axonal.append(self.internodes[ax_part_num])

            node = h.Section(name=f"node_{ax_part_num}", cell=self)
            node.L = 1
            node.diam = 0.66
            node.connect(self.axonal[-1])
            self.nodes.append(node)
            self.axonal.append(node)

        self.allsec_nofilopodia.extend(self.nodes)
        self.allsec_nofilopodia.extend(self.internodes)

    def _current_step_analysis(
        self, current_range=(-3, 3), current_step=1, traces: bool = False
    ) -> tuple[float, float, float]:
        """
        Calculates membrane resistance, input resistance, and resting potential.

        A current step is applied, and steady-state voltages are used to
        calculate resistances.

        Parameters
        ----------
        traces : bool, optional
            Whether to return voltage and time traces. Default is False.

        Returns
        -------
        input_resistance : float
            Input resistance in MΩ.
        membrane_resistance : float
            Membrane resistance in MΩ.
        """
        current_steps = np.arange(
            current_range[0], current_range[1] + current_step, current_step
        )  # Current steps in nA
        steady_state_pots = np.zeros(len(current_steps))
        peak_pots = np.zeros(len(current_steps))
        time_vectors = []
        voltage_vectors = []
        probe = h.IClamp(self.somatic[0](0.5))  # creation
        probe.dur = 100  # duration (ms)
        probe.delay = self.stabilization_time  # delay before input (ms)
        for current_ind, current_step in enumerate(current_steps):

            probe_current = current_step  # calculating current test level
            # create and set current clamp

            probe.amp = probe_current  # current level (nA)

            voltage_vector = h.Vector()
            time_vector = h.Vector()
            self.cvode.record(
                self.somatic[0](0.5)._ref_v,
                voltage_vector,
                time_vector,
                sec=self.somatic[0],
            )
            h.finitialize()
            h.continuerun(probe.delay - 5)
            h.frecord_init()
            h.continuerun(self.stabilization_time + 100)

            self.cvode.record_remove(voltage_vector)
            # taking voltage measurement at steady state
            v_rest = voltage_vector[0]
            steady_state_voltage = np.array(voltage_vector)[
                np.array(time_vector) > probe.delay + 75
            ][0]
            peak_voltage = (
                voltage_vector.max()
                if steady_state_voltage > v_rest
                else steady_state_voltage.min()
            )
            steady_state_pot = steady_state_voltage - v_rest
            peak_pot = peak_voltage - v_rest
            # recording steadystate potential

            steady_state_pots[current_ind] = (
                steady_state_pot if current_step != 0 else 0
            )
            peak_pots[current_ind] = peak_pot if current_step != 0 else 0
            print(steady_state_pot)
            time_vectors.append(np.array(time_vector) - probe.delay)
            voltage_vectors.append(np.array(voltage_vector))
            del (voltage_vector, time_vector)
        del probe
        # calculate line of best fit for resistance\\
        self._input_resistance, _ = np.polyfit(
            current_steps,
            steady_state_pots,
            1,
        )

        self._peak_input_resistance, _ = np.polyfit(
            current_steps,
            peak_pots,
            1,
        )

        self._membrane_resistance = self.surface_area * self.input_resistance * 100

        trace_dict = {"time": time_vectors, "voltage": voltage_vectors}

        if traces == True:
            return trace_dict

    def _define_section_lists(
        self,
        filopodia_maximum_length: float = None,
        filopodia_maximum_diameter: float = None,
    ) -> None:
        """
        Categorizes NEURON sections into various SectionLists.

        SectionLists include somatic, lateral, medial, dendrites, and their
        respective versions without filopodia (_nofilopodia).

        Parameters
        ----------
        minimum_length : float
            Minimum length (µm) of a section allowed before being deemed filopodia.
        minimum_diameter : float
            Minimum diameter (µm) of a section allowed before being deemed filopodia.
        """
        from .cell_calc import tiplist

        if filopodia_maximum_length is None:
            filopodia_maximum_length = self.filopodia_maximum_length
        if filopodia_maximum_diameter is None:
            filopodia_maximum_diameter = self.filopodia_maximum_diameter

        # apical & dend label used to identify dendritic poles
        # (labeled in Neurolucida)
        self.somatic = self.soma
        self.lateral = self.apic
        self.medial = self.dend
        self.dendrites = self.medial + self.lateral
        self.allsec = self.somatic + self.dendrites

        self.medial_nofilopodia = self.medial
        self.lateral_nofilopodia = self.lateral
        self.allsec_nofilopodia = self.allsec
        self.dendrites_nofilopodia = self.dendrites

        # Iteratively remove sections classified as filopodia
        while True:
            deleted = False
            for sec in tiplist(self.allsec):
                # Check if the section is too short and thin
                if (
                    sec.L < filopodia_maximum_length
                    and sec.diam < filopodia_maximum_diameter
                ):
                    sec.disconnect()  # Electrically detach filopodia
                    # Remove from all relevant SectionLists
                    self.allsec_nofilopodia.remove(sec)
                    if sec in self.dendrites_nofilopodia:
                        self.dendrites_nofilopodia.remove(sec)
                    if sec in self.lateral_nofilopodia:
                        self.lateral_nofilopodia.remove(sec)
                    if sec in self.medial_nofilopodia:
                        self.medial_nofilopodia.remove(sec)
                    deleted = True
            if not deleted:
                break  # Exit loop when no more filopodia are found

    def _get_threshold(
        self,
        current_range: tuple[float, float] = (0, 10),
        tolerance: float = 0.05,
        relative_threshold_voltage: float = 20,
        numtrial: int = 10,
        numloop: int = 20,
        traces: bool = False,
    ) -> tuple[float, float]:
        """
        Finds the current threshold for action potential generation.

        A current clamp is applied at the soma, and the minimum current
        that generates an action potential is determined.

        Parameters
        ----------
        current_step_size : float, optional
            Increment of applied DC current in nanoamps. Default is 0.1.
        start_current : float, optional
            Starting current for the sweep in nanoamps. Default is 0.
        end_current : float, optional
            Ending current for the sweep in nanoamps. Default is 10.
        relative_threshold_voltage : float, optional
        numtrial : int, optional
            Number of trials to run for each current step. Default is 10.
        Returns
        -------
        current_threshold : float
            The minimum current (in nanoamps) that generates an action potential.
        minimum_depolarization : float
            The minimum depolarization observed at the soma when no spike is generated.
        traces_dict : dict or None
            Dictionary containing traces if `traces` is True, otherwise None.
        """
        if not hasattr(self, "nodes"):
            raise ValueError(
                "No axon attached to the cell. Please attach an axon before finding the current threshold."
            )
        clamp = h.IClamp(self.somatic[0](0.5))
        clamp.delay = self.stabilization_time
        clamp.dur = 10**9  # maximum NEURON sim time
        clamp.amp = 0  # start with no current
        ax_time_vector = h.Vector()
        ax_voltage_vector = h.Vector()
        self.cvode.record(
            self.nodes[-1](0.5)._ref_v,
            ax_voltage_vector,
            ax_time_vector,
            sec=self.nodes[-1],
        )
        soma_voltage_vector = h.Vector()
        soma_time_vector = h.Vector()
        self.cvode.record(
            self.somatic[0](0.5)._ref_v,
            soma_voltage_vector,
            soma_time_vector,
            sec=self.somatic[0],
        )
        spike_count = 0
        prev_max_depol = 0
        traces_dict = {}
        loop_count = 0
        while (
            spike_count / numtrial > 0.5 + tolerance
            or spike_count / numtrial < 0.5 - tolerance
        ):
            spike_count = 0
            average_max_depol = []
            current = (current_range[0] + current_range[1]) / 2
            clamp.amp = current
            traces_dict[current] = []

            for _ in range(numtrial):
                h.finitialize()
                h.continuerun(self.stabilization_time - 2)
                h.frecord_init()
                h.continuerun(self.stabilization_time + 20)
                if (
                    max(ax_voltage_vector) - ax_voltage_vector[0]
                    > relative_threshold_voltage
                ):
                    spike_count += 1
                else:
                    average_max_depol.append(
                        (max(soma_voltage_vector) - soma_voltage_vector[0])
                    )
                (
                    traces_dict[current].append(
                        {
                            "time_axon": ax_time_vector.cl(),
                            "voltage_axon": ax_voltage_vector.cl(),
                            "time_soma": soma_time_vector.cl(),
                            "voltage_soma": soma_voltage_vector.cl(),
                        }
                    )
                    if traces
                    else ...
                )
            max_depol_without_spike = (
                (sum(average_max_depol) / len(average_max_depol))
                if len(average_max_depol) > 0
                else "N/A"
            )
            logger.debug(f"Tested current: {current} nA")
            logger.debug(f"Spike probability: {spike_count / numtrial}")
            logger.debug(f"Max depol. w/o spike (mV): {max_depol_without_spike}")

            if spike_count / numtrial > 0.5 + tolerance:
                current_range = (
                    current_range[0],
                    current_range[1] - (current_range[1] - current_range[0]) / 2,
                )
            elif spike_count / numtrial < 0.5 - tolerance:
                current_range = (
                    current_range[0] + (current_range[1] - current_range[0]) / 2,
                    current_range[1],
                )
            else:
                prev_max_depol = sum(average_max_depol) / len(average_max_depol)

            loop_count += 1
            if loop_count > numloop:
                break
        self.cvode.record_remove(ax_voltage_vector)
        self.cvode.record_remove(soma_voltage_vector)
        self._rheobase = clamp.amp
        self._potential_threshold = prev_max_depol
        return traces_dict if traces else ...

    def _get_time_constant(
        self, traces: bool = False
    ) -> tuple[float, dict[str, object]]:
        """
        Measures the time constant (tau) of the cell.

        A current clamp is applied at the soma, and the return to resting
        potential is used to calculate tau.

        Parameters
        ----------
        initv : float, optional
            Initial voltage for the simulation. Default is -58.0 mV.
        use_steady_state : bool, optional
            Whether to use steady-state voltage for tau calculation. Default is False.
        traces : bool, optional
            Whether to return voltage and time traces. Default is False.

        Returns
        -------
        tau : float
            Time constant in milliseconds.
        trace_dict : dict[str, Vector], optional
            Dictionary containing time, voltage, and current vectors if traces is True.
        """
        # Variable time step causes issues with this measurement
        # (voltage change may be too small?)
        # self.cvode.active(0)
        self.cvode.active(0)
        h.dt = 1
        time_vector = h.Vector()
        voltage_vector = h.Vector()
        self.cvode.record(
            self.somatic[0](0.5)._ref_v,
            voltage_vector,
            time_vector,
            sec=self.somatic[0],
        )

        probe = h.IClamp(self.somatic[0](0.5))
        probe.dur = 10
        probe.delay = self.stabilization_time
        probe.amp = -0.01

        trace_dict = {
            "time": time_vector,
            "voltage": voltage_vector,
        }
        h.finitialize()
        h.continuerun(self.stabilization_time - probe.dur / 2)
        h.dt = 0.01
        h.frecord_init()
        h.continuerun(self.stabilization_time + (3 / 2) * probe.dur)
        self.cvode.active(1)

        current_end_ind = time_vector.indwhere(">=", probe.delay + probe.dur)
        current_stopped_voltage_vector = voltage_vector.c(current_end_ind)
        current_stopped_time_vector = time_vector.c(current_end_ind)
        max_voltage = current_stopped_voltage_vector.max()

        resting_voltage = voltage_vector[
            time_vector.indwhere(">=", probe.delay + probe.dur) - 1
        ]
        two_thirds_voltage = (max_voltage - resting_voltage) * 0.63 + resting_voltage

        two_thirds_voltage_ind = current_stopped_voltage_vector.indwhere(
            ">=", two_thirds_voltage
        )
        time_at_two_thirds = current_stopped_time_vector[two_thirds_voltage_ind]
        trace_dict["twothirdspotential"] = two_thirds_voltage
        trace_dict["twothirdspoint"] = time_at_two_thirds
        trace_dict["endprobepoint"] = probe.delay + probe.dur
        trace_dict["depolpotential"] = resting_voltage
        trace_dict["maxpotential"] = max_voltage
        trace_dict["maxpotentialtime"] = time_vector[
            current_stopped_voltage_vector.max_ind()
        ]
        tau = time_at_two_thirds - (probe.delay + probe.dur)
        self._time_constant = tau
        self.cvode.maxstep()
        self.cvode.record_remove(voltage_vector)
        print("tau:", tau)
        if traces == True:
            return trace_dict

    def _get_resting_potential(self) -> float:
        """
        Runs a simulation to determine the cell's resting potential.

        Returns
        -------
        resting_potential : float
            The resting potential in millivolts (mV).
        """
        v = h.Vector()
        t = h.Vector()
        self.cvode.record(self.somatic[0](0.5)._ref_v, v, t, sec=self.somatic[0])
        h.finitialize()
        h.continuerun(self.stabilization_time)
        self._resting_potential = v[-1]
        self.cvode.record_remove(v)

    def _initialize_cell(self, cell_file: str) -> None:
        """
        Loads the morphology file and instantiates the cell in NEURON.
        """
        self.cvode = h.CVode()
        self.cvode.active(1)
        try:
            cell_file = Path(cell_file)
        except:
            raise TypeError(
                f"cell_file must be a Path-like object representing the morphology file. Not {type(cell_file)}."
            )
        self.filepath = cell_file
        self.cell_name = self.filepath.stem
        morph_reader = h.Import3d_Neurolucida3()
        morph_reader.input(str(cell_file))
        i3d = h.Import3d_GUI(morph_reader, False)
        i3d.instantiate(self)
        self.channels_assigned = False
        self._define_section_lists()
        self._set_compartments()

    def _load_default_values(self, config_path: str = None) -> None:
        """
        Loads default channel attributes and conductance values into SQLite databases.
        This is used to initialize the cell's channels and their properties.
        """
        # if not files("golding_NEURON").joinpath("golding_NEURON.ini").exists():
        #     raise FileNotFoundError(
        #         "Configuration file 'golding_NEURON.ini' not found in the golding_NEURON package."
        #     )

        config = get_config(config_path=config_path)
        for k, v in config["cell"]["initialization"].items():
            setattr(self, k, v)
            logger.debug(f"Setting {k} to {v}")
        cellchannels = config["cell"]["channels"]
        cellconductances = config["cell"]["conductances"]
        self.conductances = ParamDict(cellconductances, self)
        self.channels = ParamDict(cellchannels, self)

    def _reset_properties(self):
        self._time_constant = None
        self._resting_potential = None
        self._input_resistance = None
        self._membrane_resistance = None
        self._input_capacitance = None
        self._rheobase = None
        self._potential_threshold = None

    def _set_channel_cond(
        self, seg, channel, mech, part, cond_label="gbar", cond=None, **kwargs
    ):
        cond = kwargs.get(
            f"{part}_{channel}_{cond_label}",
            self.conductances[part].get(channel, 0),
        )
        cond = cond(self) if callable(cond) else cond
        setattr(
            getattr(seg, mech),
            cond_label,
            cond,
        )  # replace with nonarg

    def _remove_from_neuron(self):
        """
        Removes the cell from NEURON simulation space.
        """
        # Remove all attributes from NEURON memory
        for k in list(self.__dict__.keys()):
            delattr(self, k)

    def _reset(self) -> None:
        """
        Resets the cell's properties and removes it from NEURON.
        """
        self._reset_properties()
        self._set_compartments()
        self.unassign_channels()
        if hasattr(self, "channels_assigned"):
            self._assign_channels(
                ["dendrite", "soma"],
            )
        if hasattr(self, "axonal"):
            self._assign_channels(
                ["node", "internode", "tais", "cais"],
            )

    def _set_compartments(self, compartment_size: float = None) -> None:
        """
        Sets the number of segments in each section based on the compartment size.

        Parameters
        ----------
        compartment_size : float, optional
            Size of each compartment in microns. Default is the class attribute.
        """
        if not compartment_size:
            compartment_size = self.compartment_size

        for sec in self.allsec:
            sec.Ra = self.Ra
            sec.cm = (
                self.cm
                if sec not in getattr(self, "internodes", [])
                else self.internode_cm
            )
            length = sec.L
            seg_num = int(math.ceil(length * 1 / compartment_size))
            if sec in self.dendrites:
                sec.nseg = seg_num
            elif sec in self.somatic:
                sec.nseg = 3

    def _topology_to_string(self, subtree=None) -> str:

        topo_string = ""
        subtree_children = {sec: len(sec.subtree()) for sec in subtree}
        sorted_children = sorted(
            list(subtree_children.items()), key=lambda x: x[1], reverse=True
        )

        curr_sec = sorted_children[0][0]
        if curr_sec.parentseg() is not None:
            while curr_sec.parentseg() is not None:
                curr_sec = curr_sec.parentseg().sec
                for _ in range(int(curr_sec.L // 4)):
                    topo_string += "  "
                topo_string += "  "
            topo_string += "`"
        else:
            topo_string += "|"

        curr_sec = sorted_children[0][0]
        for _ in range(int(curr_sec.L // 4)):
            topo_string += "--"
        topo_string += "|   " + curr_sec.name().split(".")[-1] + "\n"

        subtree = [sec for sec in subtree if sec != curr_sec]
        next_up = [
            section
            for section in subtree
            if section.parentseg().sec == curr_sec
            or section.parentseg().sec not in subtree
        ]
        for section in next_up:
            new_subtree = section.subtree()
            topo_string += self._topology_to_string(subtree=new_subtree)
        return topo_string

    def assign_channels(
        self,
        parts: list[str] = None,
        **kwargs: dict[str, float | Callable[[Self], float]],
    ) -> None:
        logger.debug("Assigning channels to the cell sections.")
        if parts is None:
            parts = (
                ["dendrite", "soma"]
                if not hasattr(self, "axonal")
                else ["dendrite", "soma", "node", "internode", "tais", "cais"]
            )
        self._assign_channels(parts, **kwargs)

    def attach_axon(self) -> None:
        """
        Attaches an artificial axon to the soma of the Cell instance.

        The axon morphology is based on Lehnert et al. (2014) and includes a
        tapering initial segment, nodes, and internodes.
        """
        self._create_axon_sections()
        self._assign_channels(parts=["node", "internode", "tais", "cais"])
        self._reset()

    def disconnect_axon(self) -> None:
        """
        Disconnects the axon from the soma and removes it from the cell.
        """
        if not hasattr(self, "nodes"):
            raise ValueError("No axon attached to the cell.")
        for sec in self.axonal:
            sec.disconnect()
            del sec
        self._define_section_lists()

    def load_state(self, standards=None) -> list[list[list[list[object]]]]:
        """
        Loads a stored state of all mechanisms in the cell.
        """
        if not hasattr(self, "stored_cell_state") and standards is None:
            raise ValueError(
                "No stored cell state found. Please store a cell state first using Cell.store_state()."
            )
        cell_standards = self.stored_cell_state if standards is None else standards
        for sec, sec_standards in zip(self.allsec_nofilopodia, cell_standards):
            for seg_standards in sec_standards:
                for seg, seg_standard in zip(sec, seg_standards):
                    seg_standard.out(seg, sec=sec)
        self.stored_cell_state = cell_standards
        return cell_standards

    def move(self, x: float, y: float, z: float, relative: bool = True) -> None:
        """
        Moves the cell to a new location in 3D space.

        Parameters
        ----------
        x : float
            distance to translate or (if relative = False) new x-coordinate.
        y : float
            distance to translate or (if relative = False) new y-coordinate.
        z : float
            distance to translate or (if relative = False) new z-coordinate.
        """
        for sec in self.somatic:  # Moving the root section moves all children as well
            rel_sec_point = sec.x3d(0), sec.y3d(0), sec.z3d(0)
            for pt in range(sec.n3d()):
                x3d = sec.x3d(pt)
                y3d = sec.y3d(pt)
                z3d = sec.z3d(pt)
                diam3d = sec.diam3d(pt)

                if relative == True:
                    h.pt3dchange(pt, x3d + x, y3d + y, z3d + z, diam3d, sec=sec)
                else:
                    h.pt3dchange(
                        pt,
                        (rel_sec_point[0] - x3d) + x,
                        (rel_sec_point[1] - y3d) + y,
                        (rel_sec_point[2] - z3d) + z,
                        diam3d,
                        sec=sec,
                    )

    def psection(self, sections) -> dict:
        """
        Returns the section properties of the cell, or specific section(s)

        Parameters
        ----------
        sec : h.Section | list[h.Section], optional
            The section(s) to get properties for. If None, returns properties for all sections.

        Returns
        -------
        dict
            A dictionary containing section properties.
        """

        if sections is None:
            return {s.name(): s.psection() for s in self.allsec_nofilopodia}
        else:
            if not isinstance(sections, (list, tuple)):
                sections = [sections]
            psections = {}
            for sec in sections:
                psections.update({sec: sec.psection()})
            return psections

    def restore_state(self, cell_state: list[list[list[list[object]]]] = None):
        """
        Restores the cell's mechanisms to a previously stored state.
        """
        if hasattr(self, "stored_cell_state") and cell_state is None:
            cell_standards = self.stored_cell_state
        elif cell_state is None:
            raise ValueError(
                "No cell state provided. Please provide or store a cell state to restore one."
            )
        else:
            cell_standards = cell_state

        if len(cell_standards) != len(self.allsec_nofilopodia):
            raise ValueError(
                "Cell standards and cell sections do not match. Did the previous cell change after storing its state (axon, add/remove section,etc.)? Run Cell.store_state() again to update the state."
            )
        for sec_standards, sec in zip(cell_standards, self.allsec_nofilopodia):
            for (mech_standards,) in sec_standards:
                for seg, mech_standard in zip(sec, mech_standards):
                    mech_standard.out(seg)

    def set_artificial_resting_potential(
        self,
        resting_potential: float,
        current_limits: tuple[float, float] = (-1, 1),
        current_step: float = 0.1,
        current_override: float = None,
    ) -> None:
        """
        Sets an artificial resting potential with a measured indefinite current injection
        at the soma.
        Parameters
        ----------
        resting_potential : float
            Desired artificial resting potential.
        current_limits : tuple, optional
            Range of DC current sweeping test in nanoamps. Default is (-1, 1).
        current_step : float, optional
            Increment of applied DC current in nanoamps. Default is 0.1.
        current_override : float, optional
            If provided, directly sets the current without sweeping.
        """
        self.artificial_potential_clamp = h.IClamp(self.somatic[0](0.5))

        self.artificial_potential_clamp.delay = 0
        self.artificial_potential_clamp.dur = 10**9  # maximum NEURON sim time
        # ensures dc current is constant throughout sim
        if current_override != None:
            self.artificial_potential_clamp.amp = current_override
            h.finitialize()
            h.continuerun(self.stabilization_time)
            self.artificial_resting_potential = float(self.somatic[0](0.5).v)
            return
        else:
            self.artificial_potential_clamp.amp = 0

        current_steps = np.arange(
            current_limits[0], current_limits[1] + current_step, current_step
        )
        closest_current = current_steps[0]
        closest_resting_potential = 0
        # sweeping through current values
        for current in current_steps:
            self.artificial_potential_clamp.amp = current

            h.finitialize()
            h.continuerun(self.stabilization_time)
            if abs(float(self.somatic[0](0.5).v) - resting_potential) < abs(
                closest_resting_potential - resting_potential
            ):

                closest_current = current
                closest_resting_potential = float(self.somatic[0](0.5).v)
            if (closest_resting_potential - resting_potential) > 0:
                break
        self.artificial_potential_clamp.amp = closest_current
        self.artificial_resting_potential = closest_resting_potential

    def store_state(self) -> list[list[list[list[object]]]]:
        """
        Stores the current state of all mechanisms in the cell for later restoration.
        """
        cell_standards = []
        for sec in self.allsec_nofilopodia:
            sec_standards = []
            for mech in sec.psection()["density_mechs"]:
                mech_standards = []
                for seg in sec:
                    ms = h.MechanismStandard(mech, 0)
                    ms._in(seg)
                    mech_standards.append(ms)
                sec_standards.append(mech_standards)
            cell_standards.append(sec_standards)
        self.stored_cell_state = cell_standards
        return cell_standards

    def topology(self, subtree: list[object] = None) -> None:
        """
        Prints the topology of the cell in a human-readable format.
        """

        print(self._topology_to_string(subtree=subtree))

    def unassign_channels(self) -> None:
        """
        Unassigns all channels from the cell, resetting it to its initial state.
        """
        for sec in self.allsec:
            for mech in sec.psection()["density_mechs"]:
                sec.uninsert(mech)

        self._reset_properties()
        self.channels_assigned = False

    # TODO Add units to property docstrings
    @property
    def input_capacitance(self) -> float:
        """ """
        if getattr(self, "_input_capacitance", None) is None:
            logger.info("Evaluating property: input_capacitance")
            self._input_capacitance = self.surface_area * self.cm
        return self._input_capacitance

    @property
    def input_resistance(self) -> float:
        """
        getter for input resistance.

        Returns
        -------
        input_resistance : float
            The input resistance in MΩ.
        """
        if getattr(self, "_input_resistance", None) is None:
            logger.info("Evaluating property: input_resistance")
            self._current_step_analysis()
        return self._input_resistance

    @property
    def membrane_resistance(self) -> float:
        """
        membrane_resistance : float
            The membrane resistance in MΩ.
        """
        if getattr(self, "_membrane_resistance", None) is None:
            logger.info("Evaluating property: membrane_resistance")
            self._current_step_analysis()
        return self._membrane_resistance

    @property
    def potential_threshold(self) -> float:
        """
        Property to get the minimum depolarization observed at the soma when no spike is generated.
        Returns
        -------
        float
            The minimum depolarization in millivolts (mV).
        """
        if getattr(self, "_potential_threshold", None) is None:
            logger.info("Evaluating property: potential_threshold")
            self._get_threshold()
        return self._potential_threshold

    @property
    def resting_potential(self) -> float:
        """
        Property to get the resting potential of the cell.

        Returns
        -------
        float
            The resting potential in millivolts (mV).
        """
        if getattr(self, "_resting_potential", None) is None:
            logger.info("Evaluating property: resting_potential")
            self._get_resting_potential()
        return self._resting_potential

    @property
    def rheobase(self) -> tuple[float, float]:
        """
        Property to get the current threshold for action potential generation.
        Returns
        -------
        tuple[float, float]
            The current threshold in nanoamps and the minimum depolarization observed at the soma.
        """
        if getattr(self, "_rheobase", None) is None:
            logger.info("Evaluating property: rheobase")
            self._get_threshold()
        return self._rheobase

    @property
    def surface_area(
        self,
    ) -> float:
        """
        surface_area: float
            The surface area in square micrometers (µm²).
        """
        if getattr(self, "_surface_area", None) is None:
            logger.info("Evaluating property: surface_area")
            area = 0
            for sec in self.allsec_nofilopodia:
                for seg in sec:
                    area += seg.area()
            self._surface_area = area
        return self._surface_area

    @property
    def time_constant(self) -> float:
        """
        Property to get the time constant of the cell.

        Returns
        -------
        float
            The time constant in milliseconds.
        """
        if getattr(self, "_time_constant", None) is None:
            logger.info("Evaluating property: time_constant")
            self._get_time_constant()
        return self._time_constant

    def __hash__(self):
        """
        Returns a hash of the ParamDict based on its items.
        This allows it to be used as a key in other dictionaries.
        """
        return hash(tuple(sorted(self.items())))

    # Example usage:
    # cell = Cell("path/to/morphology.asc")
    # cell.assign_properties()
    # cell.attach_axon()
    # cell.set_artificial_resting_potential(-70)
    # tau, traces = cell.get_time_constant(traces=True)
    # print(f"Time constant: {tau} ms")
    # input_resistance, membrane_resistance, resting_potential = cell.get_resistances_and_resting_potential(traces=True)
    # print(f"Input resistance: {input_resistance} MΩ")
    # print(f"Membrane resistance: {membrane_resistance} MΩ")
    # print(f"Resting potential: {resting_potential} mV")
