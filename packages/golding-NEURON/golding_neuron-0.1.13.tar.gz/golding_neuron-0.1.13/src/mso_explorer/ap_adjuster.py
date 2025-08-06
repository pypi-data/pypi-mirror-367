# Standard library imports
import copy
import gc
import glob
import logging
import math
import os
import pickle
import platformdirs
import sys
from pathlib import Path
import time
# Third-party imports

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from neuron import h
from PyQt5.QtCore import Qt, QSize, QCoreApplication, QRunnable, QThreadPool, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QMovie, QImage
from PyQt5.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QToolBar,
    QAction,
    QFileDialog,
    QStyle,
    QCheckBox,
    QComboBox,
    QAbstractScrollArea
    
)

# Local imports
from golding_NEURON.cell import Cell
from golding_NEURON.compile_mechs import compile_mechs
from golding_NEURON.utils import get_cell_file_paths, reset_config
# reset_config()
h.nrnmpi_init()
pc = h.ParallelContext()

pc.runworker()
mpl.use("qtagg")
logger = logging.getLogger(__name__)
if not os.path.isdir(platformdirs.user_cache_dir("golding_NEURON")):
    os.makedirs(platformdirs.user_cache_dir("golding_NEURON"), exist_ok=True)
if not os.path.isdir(os.path.join(platformdirs.user_cache_dir("golding_NEURON"), ".matplotlib")):
    os.makedirs(os.path.join(platformdirs.user_cache_dir("golding_NEURON"), ".matplotlib"))
os.environ['MPLCONFIGDIR'] = str(os.path.join(platformdirs.user_cache_dir("golding_NEURON"), ".matplotlib"))

if not os.path.isfile(os.path.join(platformdirs.user_config_dir("golding_NEURON"), "golding_NEURON_config.json")):
    reset_config()
    
config_loc = os.path.join(platformdirs.user_config_dir('golding_NEURON'),"golding_NEURON_config.json")
working_directory = getattr(sys, '_MEIPASS', os.getcwd())

def ap_task(cell_loc, config_loc, current, conductances):
    cell = Cell(
        cell_loc,
        config_path=config_loc,
    )
    # cell.channels["hcn"]["mechanism"] = "khurana_hcn"
    cell.conductances = copy.copy(conductances)
    cell.assign_channels()
    cell.attach_axon()
    cell.stabilization_time = 100

    clamp = h.IClamp(cell.somatic[0](0.5))
    clamp.delay = 100
    clamp.dur = 5
    clamp.amp = current
    y_traces = []
    labels = []
    t_soma = h.Vector()
    v_soma = h.Vector()
    cell.cvode.record(cell.somatic[0](0.5)._ref_v, v_soma, t_soma, sec=cell.somatic[0])
    v_axon = {}
    t_axon = {}
    for sec in [cell.tais, cell.cais] + cell.nodes:
        t_axon[sec] = h.Vector()
        v_axon[sec] = h.Vector()
        cell.cvode.record(sec(0.5)._ref_v, v_axon[sec], t_axon[sec], sec=sec)
    h.finitialize()
    h.continuerun(100)
    h.frecord_init()
    h.continuerun(103)
    cell.cvode.record_remove(v_soma)
    for sec in [cell.tais, cell.cais] + cell.nodes:
        cell.cvode.record_remove(v_axon[sec])
    x_traces = [np.array(t_soma)]
    y_traces.append(np.array(v_soma))
    labels.append("Soma")
    for sec in v_axon:
        y_traces.append(np.array(v_axon[sec]))
        x_traces.append(np.array(t_axon[sec]))
        label = (
            f"{sec.name()}".split("[")[-1]
            .split("]")[0]
            .split(".")[-1]
            .replace("_", " ")
        )
        label = label.upper() if label in ["tais", "cais"] else label.capitalize()
        print(label)
        labels.append(label)
    sorted_args = np.flip(np.array(y_traces).max(axis=1).argsort())
    x_traces = np.array(x_traces)[sorted_args]
    y_traces = np.array(y_traces)[sorted_args]
    labels = np.array(labels)[sorted_args]
    print('returning ap')
    return x_traces, y_traces, labels
        

def curr_task(cell_loc, config_loc, conductances):
    step_cell = Cell(cell_loc, config_path=config_loc)
    # step_cell.channels["hcn"]["mechanism"] = 
    step_cell.stabilization_time = 100
    step_cell.conductances = conductances
    step_cell.assign_channels()
    step_cell.attach_axon()
    current_traces = step_cell._current_step_analysis(traces=True)
    resting_potential = step_cell.resting_potential
    input_resistance = step_cell.input_resistance
    return current_traces, input_resistance, resting_potential
    


def tc_task(cell_loc, config_loc, conductances):
    tau_cell = Cell(cell_loc, config_path=config_loc)
    # tau_cell.channels["hcn"]["mechanism"] = "khurana_hcn"
    tau_cell.stabilization_time = 500
    tau_cell.conductances = copy.copy(conductances)
    tau_cell.assign_channels()
    tau_cell.attach_axon()
    tau_trace = tau_cell._get_time_constant(traces=True)
    tau = tau_cell.time_constant
    return tau_trace, tau
        

        
        
class WorkerSignals(QObject):
    """Signals from a running worker thread.

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc())

    result
        object data returned from processing, anything
    """

    ap = pyqtSignal()
    current_step = pyqtSignal()
    time_constant = pyqtSignal()
    all = pyqtSignal()
    
class Thread(QRunnable):
    """
    Thread to run the simulation in the background.
    """
    def __init__(self, parent=None, **kwargs):
        super().__init__()
        self.parent = parent
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.results = {}

    def run(self):
        """
        Run the simulation.
        """
        self.submit_tasks(**self.kwargs)
        self.wait_for_tasks()
    
    def submit_tasks(self, cell_loc, config_loc, current, conductances):   
        pc.submit(0, ap_task, cell_loc, config_loc, current, conductances)   
        pc.submit(1, curr_task, cell_loc, config_loc, conductances)
        pc.submit(2, tc_task, cell_loc, config_loc, conductances)

    def wait_for_tasks(self):
        associations = {0: "ap", 1: "current_step", 2: "time_constant"}
        while pc.working():
            userid = pc.userid()
            self.results[userid] = pc.pyret()
            getattr(self.signals, associations[userid]).emit()
        self.signals.all.emit()

        
        

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=10, dpi=100):
        
        self.fig = Figure(
            figsize=(width, height), dpi=dpi, layout="tight", facecolor="none"
        )
        self.parent = parent
        self.text_color = self.parent.palette().text().color().getRgbF()
        super().__init__(self.fig)
    def color_update(self):
        """
        Update the text color based on the current palette.
        """
        self.text_color = self.parent.palette().text().color().getRgbF()

        if hasattr(self, "legend"):
            print("hasit")
            for text in self.legend.get_texts():
                text.set_color(self.text_color)
        
    def leave_off_ticks(self):
        
        self.axis.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        self.axis.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left=False,        # ticks along the left edge are off
            right=False,       # ticks along the right edge are off
            labelleft=False)  
    
    def put_on_ticks(self):
        self.axis.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=True,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=True,
            color=self.text_color)
        self.axis.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left=True,        # ticks along the left edge are off
            right=False,       # ticks along the right edge are off
            labelleft=True,
            color=self.text_color)
        
        
    def make_ap_axes(self):
        self.type = 'ap'
        axes = self.fig.subplots(ncols=2, nrows=1, width_ratios=[4, 1])
        self.axis = axes[0]
        self.axis_leg = axes[1]
        self.axis_leg.set_axis_off()
        self.axis.spines["top"].set_visible(False)
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set(color=self.text_color)
        self.axis.spines["left"].set(color=self.text_color)
        self.axis.tick_params(axis="both", colors=self.text_color)
        self.axis.set_ylabel("(mV)", color=self.text_color)
        self.axis.set_xlabel("(ms)", color=self.text_color)
        self.axis.set_xlim(0, 1.5)
        self.axis_leg.patch.set_alpha(0.0)
        self.axis.patch.set_alpha(0.0)
        self.leave_off_ticks()
        self.draw_idle()
        return self.axis, self.axis_leg

    def make_axes(self):
        self.axis = self.fig.subplots(nrows=1, ncols=1)
        self.axis.spines["top"].set_visible(False)
        self.axis.spines["right"].set_visible(False)
        self.axis.patch.set_alpha(0.0)
        self.axis.spines["bottom"].set(color=self.text_color)
        self.axis.spines["left"].set(color=self.text_color)
        self.axis.tick_params(axis="both", colors=self.text_color)
        self.axis.set_ylabel("(mV)", color=self.text_color)
        self.axis.set_xlabel("(ms)", color=self.text_color)
        self.leave_off_ticks()
        self.draw_idle()
        return self.axis


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cell_loc = get_cell_file_paths()[0]
        self.window_cell = Cell(self.cell_loc, config_path=config_loc)
        # self.window_cell.channels["hcn"]["mechanism"] = "baumann_hcn_ventral"
        self.window_cell.assign_channels()
        logger.debug(f"Assigned channels to window cell")
        self.window_cell.attach_axon()
        logger.debug(f"Attached axon to window cell")
        self.window_cell.stabilization_time = 100
        print(self.window_cell.channels) 
        self.setWindowTitle("GoldingMSO")
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignHCenter)
        plot_layout = QVBoxLayout()
        plot_layout.setAlignment(Qt.AlignTop)

        tabs = QTabWidget()
        tabs.setMinimumSize(QSize(410,100))
        tabs.setTabPosition(QTabWidget.South)
        tabs.setMovable(True)
        self.resetting = False

        self.attributes = {
            "Resting potential": {"unit": "mV", "val": 0.0},
            "Input resistance": {"unit": "MΩ", "val": 0.0},
            "Time constant": {"unit": "ms", "val": 0.0},
        }
        self.table = QTableWidget(3, 3, self)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.setMaximumSize(QSize(350, 125))
        self.table.setMinimumSize(QSize(350,125))
        self.table.setHorizontalHeaderLabels(["Attribute", "Value", "Unit"])
        for i, name in enumerate(self.attributes.keys()):
            item_name = QTableWidgetItem(name)
            item_val = QTableWidgetItem("N/A")
            item_unit = QTableWidgetItem(self.attributes[name]["unit"])
            self.table.setItem(i, 0, item_name)
            self.table.setItem(i, 1, item_val)
            self.table.setItem(i, 2, item_unit)
        self.table.resizeColumnsToContents()
        widget_layouts = []
        for part, part_display_name in zip(
            ["soma", "dendrite", "tais", "cais", "node", "internode"],
            ["Soma", "Dendrite", "TAIS", "CAIS", "Node", "Internode"],
        ):
            widget = QWidget()
            widget_layout = QVBoxLayout()
            widget_layout.setAlignment(Qt.AlignTop)
            widget.setLayout(widget_layout)
            widget_layouts.append(widget_layout)
            tabs.addTab(widget, part_display_name)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas.setStyleSheet("background-color:transparent;")
        self.ap_axis, self.leg_axis = self.canvas.make_ap_axes()
        self.current_plot = MplCanvas(self, width=5, height=4, dpi=100)
        self.current_plot.setStyleSheet("background-color:transparent;")
        self.current_axis = self.current_plot.make_axes()
        self.tau_plot = MplCanvas(self, width=5, height=4, dpi=100)
        self.tau_plot.setStyleSheet("background-color:transparent;")
        self.tau_axis = self.tau_plot.make_axes()
        plot_layout.addWidget(self.canvas, stretch=3)
        plot_layout.setAlignment(Qt.AlignHCenter)
        plot_widget = QWidget()
        plot_widget.setLayout(plot_layout)
        plot_widget.setMinimumSize(QSize(300, 600))
        current_label = QLabel("Current (nA)")
        current_label.setMaximumHeight(30)
        plot_layout.addWidget(current_label, stretch=0)
        
        self.current_spinbox = QDoubleSpinBox(
            value=1,
            minimum=0,
            maximum=10,
            singleStep=0.1,
            decimals=2,
            suffix="nA",
        )
        self.current_spinbox.setMaximumHeight(30)
        self.current_spinbox.valueChanged.connect(
            lambda value: self.update_current(value)
        )
        plot_layout.addWidget(self.current_spinbox, stretch=1)
        measurement_layout = QHBoxLayout()
        measurement_layout.addWidget(self.current_plot, stretch=2)
        measurement_layout.addWidget(self.tau_plot, stretch=2)
        plot_layout.addLayout(measurement_layout, stretch=2)
        widgets = []
        self.spinboxes = {part: {} for part in self.window_cell.conductances.keys()}
        self.spinbox_defaults = {
            part: {} for part in self.window_cell.conductances.keys()
        }

        # self.spinbox_defaults = {part:{part_channel} for part, part_channels in self.window_cell.conductances.items for part_channel in part_channels.keys()}

        # self.current_spinbox = 1
        self.tapers = {part: {} for part in self.window_cell.conductances.keys()}
        for layout, (part, part_channels) in zip(
            widget_layouts,
            {
                part: self.window_cell.conductances[part]
                for part in ["soma", "dendrite", "tais", "cais", "node", "internode"]
            }.items(),
        ):
            title = QLabel(f"Conductances (S/cm^2):")
            title.setAlignment(Qt.AlignCenter)

            widgets.append(title)
            layout.addWidget(title)
            # widgets.append(QLabel(f"{part}"))
            # layout.addWidget(widgets[-1])
            for part_channel, cond in part_channels.items():
                widgets.append(QLabel(f"{part_channel}"))
                layout.addWidget(widgets[-1])
                row_layout = QHBoxLayout()
                spinbox = QDoubleSpinBox(
                    minimum=0,
                    maximum=5,
                    singleStep=cond / 10,
                    decimals=5,
                )
                row_layout.addWidget(spinbox, stretch=2)
                self.tapers[part][part_channel] = QCheckBox("Taper?", self)
                self.tapers[part][part_channel].stateChanged.connect(
                    lambda state, p=part, pc=part_channel: self.set_taper(
                        p, pc, state == Qt.Checked
                    )
                )
                row_layout.setAlignment(Qt.AlignRight)
                row_layout.addWidget(self.tapers[part][part_channel], stretch=0)

                widgets.append(spinbox)
                self.spinboxes[part][part_channel] = spinbox
                self.spinbox_defaults[part][part_channel] = cond
                # widgets[-1].setDisplayIntegerBase(8)
                widgets[-1].setValue(cond)
                widgets[-1].valueChanged.connect(
                    lambda value, p=part, pc=part_channel: self.update_cond(
                        value, p, pc
                    )
                )
                layout.addLayout(row_layout)
        
        cell_names = [Path(cell_path).stem for cell_path in get_cell_file_paths()]
        self.cell_combo = QComboBox(self)
        self.cell_combo.setStyleSheet("QComboBox:editable{{ color: {} }}".format(self.palette().text().color().name()))
        # self.cell_combo.setMinimumHeight(
        self.cell_combo.addItems(cell_names)
        self.cell_combo.setMaxVisibleItems(5)
        self.cell_combo.setCurrentText(cell_names[0])
        self.cell_combo.currentTextChanged.connect(
            lambda text: self._swap_cell(text)
        )
        self.plot = plot_layout
        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        # left_layout.addLayout(plot_layout, stretch=2)
        run_button = QPushButton("Go")
        run_button.clicked.connect(lambda: self.sim_update())
        self.cell_pic = QLabel(self)
        self.cell_pic.setStyleSheet("background-color:transparent;")
        pixmap = self.change_image_color(
                str(Path(working_directory)/'cell_pics'/f'{self.cell_combo.currentText()}.png'),
                self.palette().text().color(),
            )
        pixmap = pixmap.scaled(
            QSize(175, 175), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.cell_pic.setPixmap(
            pixmap
        )
        self.cell_pic.setMinimumHeight(175)
        self.cell_pic.setMaximumHeight(175)
        cell_box = QVBoxLayout()
        cell_box.setAlignment(Qt.AlignRight)
        cell_label = QLabel("Cell:")
        # cell_box.addWidget()
        cell_box.addWidget(cell_label)
        cell_box.addWidget(self.cell_combo)
        self.cell_combo.setMaximumHeight(30)
        cell_label.setMaximumHeight(30)
        cell_layout = QHBoxLayout()
        cell_layout.setAlignment(Qt.AlignLeft)
        cell_layout.setAlignment(Qt.AlignTop)
        cell_layout.addWidget(self.cell_pic, stretch=1)
        cell_layout.addLayout(cell_box, stretch=0)
        right_layout.addLayout(cell_layout, stretch=0)
        
        

        tb = QToolBar("Toolbar")
        
        open = QAction(
            self.style().standardIcon(getattr(QStyle, "SP_DialogOpenButton")),
            "Open conductances from file",
            self,
        )
        save = QAction(
            self.style().standardIcon(getattr(QStyle, "SP_DialogSaveButton")),
            "Save conductances to file",
            self,
        )
        reset = QAction(
            self.style().standardIcon(getattr(QStyle, "SP_BrowserReload")),
            "Reset conductances",
            self,
        )
        tb.addAction(save)
        tb.addAction(open)
        tb.addAction(reset)

        tb.actionTriggered[QAction].connect(self.toolbtnpressed)
        tb.setOrientation(Qt.Vertical)
        self.addToolBar(tb)

        left_layout.addWidget(plot_widget, stretch=3)
        left_layout.addWidget(run_button, stretch=1)
        right_layout.addWidget(tabs, stretch=1)
        right_layout.addWidget(self.table, stretch=1)
        # left_layout.addLayout(master_widget_layout)
        
        total = QWidget()

        total_layout = QHBoxLayout()

        
        total_layout.addLayout(right_layout, stretch=1)
        total_layout.addLayout(left_layout, stretch=2)
        total.setLayout(total_layout)
        self.setCentralWidget(total)
        self.threadpool = QThreadPool()
       


        
    def set_taper(self, part, part_channel, state):
        """
        Set the taper state for a specific part and channel.
        """
        length_const = 74
        max_value = self.spinboxes[part][part_channel].value()

        def taper(cell):
            return max_value * math.e ** (
                h.distance(cell.accessed_segment, cell.somatic[0](0.5)) / length_const
            )

        if state:
            self.window_cell.conductances[part][part_channel] = taper
        else:
            self.window_cell.conductances[part][part_channel] = max_value
        print(self.window_cell.psection(self.window_cell.dendrites_nofilopodia[0]))
    def _swap_cell(self, cell_name):
        """
        Swap the current cell with a new one based on the cell name.
        """
        self.cell_loc = get_cell_file_paths(cell_name)[0]
        self.window_cell = Cell(self.cell_loc, config_path=config_loc)
        # self.window_cell.channels["hcn"]["mechanism"] = "khurana_hcn"
        self.window_cell.assign_channels()
        self.window_cell.attach_axon()
        self.window_cell.stabilization_time = 100
        
        pixmap = self.change_image_color(
                str(Path(working_directory)/'cell_pics'/f'{self.cell_combo.currentText()}.png'),
                self.palette().text().color(),
            )
        print(f"cell_pics/{self.cell_combo.currentText()}.png")
        pixmap = pixmap.scaled(
            QSize(175, 175), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.cell_pic.setPixmap(
            pixmap
        )
        
    def toolbtnpressed(self, action):
        if action.text() == "Open conductances from file":
            print("Opening file...")
            try:
                self.load_params()
            except Exception as e:
                print(f"Error loading conductances: {e}")
        elif action.text() == "Save conductances to file":
            try:
                self.save_params()
            except Exception as e:
                print(f"Error saving conductances: {e}")
        elif action.text() == "Reset conductances":
            print("Resetting conductances...")
            self.reset_params()

    def reset_params(self):
        for part, part_channels in self.spinbox_defaults.items():
            for part_channel, cond in part_channels.items():
                self.spinboxes[part][part_channel].setValue(cond)
        # self.sim_update()

    def save_params(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Cell parameters (*.gparam)"
        )
        if file_path:
            conds = {}
            for part, channels in self.window_cell.conductances.items():
                conds[part] = {}
                for channel, value in channels.items():
                    conds[part][channel] = self.spinboxes[part][channel].value()
                    conds[part][f"{channel}_taper"] = self.tapers[part][
                        channel
                    ].isChecked()
            with open(file_path, "wb") as f:
                pickle.dump(conds, f)
            print(f"Parameters saved to {file_path}")
        else:
            print("Save operation cancelled.")

    def assign_spinboxes(self, params):
        print(params)
        for part, part_channels in self.spinboxes.items():
            for part_channel, spinbox in part_channels.items():
                spinbox.setValue(params[part][part_channel])

    def assign_tapers(self, params):
        for part, channels in self.tapers.items():
            for channel, taper in channels.items():
                taper.setChecked(params[part][f"{channel}_taper"])

    def load_params(self):
        # cell._load_default_values()
        # cell._reset()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Cell parameters (*.gparam)"
        )
        with open(file_path, "rb") as f:
            params = pickle.load(f)
        self.resetting = True
        self.assign_spinboxes(params)
        self.assign_tapers(params)
        # self.sim_update()

    def sim_update(self):
        
        self.clear_axes()
        
        conductances = self.window_cell.conductances.convert_to_dict()
        current = self.current_spinbox.value()
        
        self.master_thread = Thread(parent=self, cell_loc=str(self.cell_loc),config_loc=config_loc, current=float(current), conductances=conductances)
        self.master_thread.signals.ap.connect(lambda: self.replot())
        self.master_thread.signals.current_step.connect(lambda: self.current_step_plotting())
        self.master_thread.signals.time_constant.connect(lambda: self.time_constant_plotting())
        self.master_thread.signals.all.connect(lambda: self.reset_gui())
        self.threadpool.start(self.master_thread)

    def clear_axes(self):
        """
        Clear the axes of the canvas and reset the plots.
        """
        self.texts = []
        axes = [self.ap_axis, self.leg_axis, self.current_axis, self.tau_axis]
        for ax in axes:
            for art in list(ax.lines+ax.collections+ax.patches+ax.texts):
                art.remove()
            if ax != self.leg_axis:
               self.texts.append(ax.text(sum(ax.get_xlim())/2, sum(ax.get_ylim())/2, "~loading~", fontdict={"size": 8}, color=self.palette().text().color().getRgbF(), ha="center", va="center"))
        for canvas in [self.canvas, self.current_plot, self.tau_plot]:
            canvas.draw_idle()
            

    def reset_gui(self):
        for row, (attribute, value) in enumerate(self.attributes.items()):
            self.table.item(row, 1).setText(
                f"{value['val']:.2f}"
            )
            self.table.item(row,1).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.resizeColumnsToContents()
        self.canvas.color_update()
        self.current_plot.color_update()
        self.tau_plot.color_update()
        self.cell_combo.setStyleSheet("QComboBox:editable{{ color: {} }}".format(self.palette().text().color().name()))
        self._swap_cell(self.cell_combo.currentText())
        gc.collect()

    
        
    def replot(self):
        data = self.master_thread.results[0]
        self.ap_axis.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=True,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=True) # labels along the bottom edge are off
        self.ap_axis.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left=True,        # ticks along the left edge are off
            right=False,       # ticks along the right edge are off
            labelleft=True)  
        for text in self.texts:
            if text.get_figure() == self.canvas.figure:
                text.remove()
        self.ap_axis.patch.set_alpha(0.0)
        self.leg_axis.patch.set_alpha(0.0)
        rainbow = mpl.colormaps["rainbow"].resampled(6)
        handles = []
        self.ap_axis.set_xlim(0, 1.5)
        for ind, (xtrace, trace, label) in enumerate(zip(data[0], data[1], data[2])):
            
            line = self.ap_axis.plot(
                xtrace - xtrace[0],
                trace,
                label=label,
                color=[col*0.75 for col in rainbow(ind / len(data[1]))[:-1]]+[rainbow(ind / len(data[1]))[-1]],
            )
            handles.append(*line)
            self.canvas.draw_idle()
        handles.reverse()
        self.canvas.legend = self.leg_axis.legend(
            handles=handles,
            loc="center",
            frameon=False,
            labelcolor=self.canvas.text_color,
        )
        self.ap_axis.set_xlabel("(ms)", color=self.canvas.text_color)
        self.ap_axis.set_ylabel("(mV)", color=self.canvas.text_color)
        self.ap_axis.set_ylim(-75, 40)
        self.ap_axis.spines["bottom"].set(color=self.canvas.text_color)
        self.ap_axis.spines["left"].set(color=self.canvas.text_color)
        self.ap_axis.tick_params(axis="both", colors=self.canvas.text_color)
        self.ap_axis.patch.set_alpha(0.0)
        self.leg_axis.patch.set_alpha(0.0)
        self.canvas.draw_idle()

    
        
    
    
        
    def current_step_plotting(self):
        self.current_axis.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=True,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=True) # labels along the bottom edge are off
        self.current_axis.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left=True,        # ticks along the left edge are off
            right=False,       # ticks along the right edge are off
            labelleft=True)  
        for text in self.texts:
            if text.get_figure() == self.current_plot.figure:
                text.remove()
        current_traces, input_resistance, resting_potential = self.master_thread.results[1]
        self.attributes["Input resistance"]["val"] = input_resistance
        self.attributes["Resting potential"]["val"] = resting_potential
        self.current_axis.set_xlim(0,100)
        self.current_axis.spines["bottom"].set(color=self.canvas.text_color)
        self.current_axis.spines["left"].set(color=self.canvas.text_color)
        self.current_axis.tick_params(axis="both", colors=self.canvas.text_color)
        self.current_plot.text_color = self.palette().text().color().getRgbF()
        self.current_axis.clear()
        self.current_axis.patch.set_alpha(0.0)
        for time_trace, voltage_trace in zip(current_traces["time"], current_traces["voltage"]):
            self.current_axis.plot(
                time_trace,
                voltage_trace,
                color=self.canvas.text_color,
            )
            self.current_plot.draw_idle()
        self.current_axis.set_ylabel("(mV)", color=self.canvas.text_color)
        self.current_axis.set_xlabel("(ms)", color=self.canvas.text_color)
        self.current_axis.patch.set_alpha(0.0)
        self.current_plot.draw_idle()
        
    def resting_potential_plotting(self, conductances):
        resting_cell = Cell(self.cell_loc, config_path=config_loc)
        # resting_cell.channels["hcn"]["mechanism"] = "khurana_hcn"
        resting_cell.stabilization_time = 100
        resting_cell.conductances = copy.copy(conductances)
        resting_cell.assign_channels()
        resting_cell.attach_axon()
        resting_potential = copy.copy(resting_cell.resting_potential)
        self.attributes["Resting potential"]["val"] = resting_potential

    def time_constant_plotting(self):
        self.tau_axis.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=True,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=True) # labels along the bottom edge are off
        self.tau_axis.tick_params(
            axis='y',          # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left=True,        # ticks along the left edge are off
            right=False,       # ticks along the right edge are off
            labelleft=True)  
        for text in self.texts:
            if text.get_figure() == self.tau_plot.figure:
                text.remove()
        tau_trace, tau = self.master_thread.results[2]
        self.tau_axis.spines["bottom"].set(color=self.canvas.text_color)
        self.tau_axis.spines["left"].set(color=self.canvas.text_color)
        self.tau_axis.tick_params(axis="both", colors=self.canvas.text_color)

        self.tau_axis.clear()
        self.tau_axis.patch.set_alpha(0.0)
        tau_trace["time"] = np.array(tau_trace["time"])-tau_trace["endprobepoint"]
        self.tau_axis.plot(
            tau_trace["time"],
            tau_trace["voltage"],
            color=self.canvas.text_color,
        )
        self.tau_axis.axvline(
            tau_trace["twothirdspoint"] - tau_trace["endprobepoint"], color=self.canvas.text_color, linestyle=":")
        self.tau_axis.axhline(
            tau_trace["twothirdspotential"],
            color=self.canvas.text_color, linestyle=":")
        
        self.tau_axis.scatter(
            tau_trace["twothirdspoint"]- tau_trace["endprobepoint"],
            tau_trace["twothirdspotential"],
            color=self.canvas.text_color,
        )

        self.tau_axis.set_xlim(
            0,
            tau_trace["time"][tau_trace["voltage"].max_ind()],
        )
        self.tau_axis.patch.set_alpha(0.0)
        self.tau_axis.set_ylabel("(mV)", color=self.canvas.text_color)
        self.tau_axis.set_xlabel("(ms)", color=self.canvas.text_color)
        self.tau_plot.draw_idle()
        self.attributes["Time constant"]["val"] = tau
        # self.tau_axis.set_axis_off()
        

    def update_cond(self, cond, part, part_channel):
        self.set_taper(part, part_channel, self.tapers[part][part_channel].isChecked())

    def update_current(self, current):
        return


    def change_image_color(self, image_path, qcolor):
        image= QPixmap()
        loaded = image.load(image_path)
        if not loaded:
            raise FileNotFoundError(f"Image file {image_path} not found.")
        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(image.rect(), qcolor)
        painter.end()
        return image
        # Create a QColor object from the new_color_rgb tuple
        # image = QImage(image_path)
        # for x in range(image.width()):
        #     for y in range(image.height()):
        #         # Get the current pixel color
        #         current_color = image.pixelColor(x, y)
        #         # Example: Change all non-transparent pixels to the new color
        #         if current_color.alpha() > 0:
        #             # print(image.pixelColor(x,y).getRgb())
        #             if current_color.getRgb() != (254, 254, 254, 255):
        #                 image.setPixelColor(x, y, qcolor)
        #             elif current_color.getRgb() == (254, 254, 254, 255):
        #                 image.setPixelColor(x, y, QColor(0, 0, 0, 0))
                    
        
        # return QPixmap.fromImage(image, flags=Qt.NoOpaqueDetection)
def main():
    cwd = getattr(sys, "_MEIPASS", os.getcwd())
    nrnivmodl_path = Path(cwd).joinpath("nrnivmodl")
    print("currentworkingdirectory", cwd)
    # print(os.listdir(cwd+'x'))
    dll_paths = ['/x86_64/.libs/libnrnmech.so', r"/nrnmech.dll"]
    # if any([Path(cwd+path).is_file() for path in dll_paths]):   
    #     for path in dll_paths:
    #         if Path(cwd+path).is_file():
    #             print(cwd+path)
    #             try: h.nrn_load_dll(str(Path(cwd).joinpath(path)))
    #             except: print('Failed to load NEURON DLL:', path)
    # else: compile_mechs(workdir=cwd)
    compile_mechs(workdir=cwd, nrnivmodl_path=nrnivmodl_path)
    

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("MSO Parameter Explorer")
    app.setApplicationVersion("1.0.0")
    app.setFont(QFont("Verdana", 13))
    plt.rcParams["font.family"] = "Verdana"
    plt.rcParams["font.size"] = 10
    window = MainWindow()
    window.show()
    app.exec_()



if __name__ == "__main__":
    main()
