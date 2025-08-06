import glob
from importlib.resources import files
from .itd_job import ITDJob
from .nsg_portal import NSGWindow
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import numpy as np
from tkinter import scrolledtext
import logging
import pickle
import threading
import tkinter as tk
import tkinter.ttk as ttk

# import sv_ttk
from shutil import copytree, copyfile, make_archive, rmtree
import datetime
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from golding_NEURON.cell_calc import parentlist, section_list_length, tiplist
from golding_NEURON.cell import Cell
from golding_NEURON.sims import itd_test_sweep
import glob
import logging
import os

import pickle
import pandas
from neuron import h

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



from tkinter import scrolledtext
import logging
import pickle
import threading
import tkinter as tk
import tkinter.ttk as ttk

# import sv_ttk
from shutil import copytree, copyfile, make_archive, rmtree
import datetime
from matplotlib.figure import Figure
from golding_NEURON.cell_calc import parentlist, section_list_length, tiplist
from golding_NEURON.cell import Cell
from golding_NEURON.sims import itd_test_sweep
import glob
import logging
import os

import pickle
import numpy as np
import pandas
from neuron import h

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy as np
from tkinter import scrolledtext
import logging
import pickle
import threading
import tkinter as tk
import tkinter.ttk as ttk

# import sv_ttk
from shutil import copytree, copyfile, make_archive, rmtree
import datetime
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from golding_NEURON.cell_calc import parentlist, section_list_length, tiplist
from golding_NEURON.cell import Cell
from golding_NEURON.sims import itd_test_sweep
from importlib.resources import files
import glob
import logging
import os

import pickle
import numpy as np
import pandas
from neuron import h

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



# Based on
#   https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw):

        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind("<Configure>", _configure_canvas)

    def create(self):
        self.interior_id = self.canvas.create_window(
            0, 0, window=self.interior, anchor=tk.NW, tags="self.interior"
        )


class ITDBuildGUI(tk.Frame):

    job_file_dir = str(files("golding_NEURON").joinpath("itd_job_builder/job_files"))
    temp_dir = os.path.join(job_file_dir, "temp_archive")
    temp_subdir = os.path.join(temp_dir, "sub")
    day = datetime.datetime.now().strftime("%y%m%d")
    iterables = {}

    def __init__(self):
        self.window = tk.Tk()
        super().__init__(self.window)
        self.pack(fill=tk.BOTH, expand=True)
        self.wind_height = self.window.winfo_screenheight()
        self.wind_width = self.window.winfo_screenwidth()
        self.window.geometry(
            f"{int(self.wind_width*0.99)}x{int(self.wind_height*0.99)}"
        )

        self.section_locs = {
            "Excitation": (1, 0),
            "Inhibition": (2, 0),
            "Axon": (3, 0),
            "Cells": (1, 1),
            "ITD": (2, 1),
            "Send": (3, 1),
            "Name": (0, 0),
            "Output": (0, 1),
        }
        # self.grid_propagate(False)
        self.create_grid()
        self.radiobutton_vars = {}
        self.cell_files = glob.glob(os.path.join(str(files("golding_NEURON").joinpath("cells")), "*.asc"))
        self.cell_names = [Path(f).stem for f in self.cell_files]
        # self.after(10000)
        self.create_label("IΤD Test", self.subframes[self.section_locs["ITD"]])
        self.image_frame = tk.Frame(self.subframes[self.section_locs["Send"]])
        self.image_frame.grid(row=0, column=3, rowspan=3)
        file_path = os.path.join(
            str(files("golding_NEURON").joinpath("itd_job_builder/cell_pics")), "151124_03.png"
        )
        self.img = Image.open(file_path)
        self.img = self.img.resize([200, 200])
        self.img = ImageTk.PhotoImage(master=self.image_frame, image=self.img)
        self.label = tk.Label(self.image_frame, image=self.img)
        self.label.pack()
        self.label.image = self.img
        # Listbox

        # self.create_menubar()
        cell_list = self.create_listbox(
            "Cells",
            "selected_cells",
            self.cell_names,
            parent=self.subframes[self.section_locs["Send"]],
            reveal_cat="Cells",
            pack=False,
        )
        cell_list.grid(row=0, column=2, rowspan=3, sticky=tk.EW)

        # Checkboxes
        self.checkbox_vars = {}
        self.create_checkbox(
            "Attach axon",
            "axon",
            parent=self.subframes[self.section_locs["Axon"]],
            reveal_cat="Axon",
        )
        self.create_checkbox(
            "Inhibition",
            "inhibition",
            parent=self.subframes[self.section_locs["Inhibition"]],
            reveal_cat="Inhibition",
        )
        self.create_checkbox(
            "Excitation",
            "excitation",
            parent=self.subframes[self.section_locs["Excitation"]],
            reveal_cat="Excitation",
        )
        trace_box = self.create_checkbox(
            "Output traces",
            "traces",
            parent=self.subframes[self.section_locs["Send"]],
            reveal_cat="Send",
            pack=False,
        )
        trace_box.grid(row=0, column=0, columnspan=1)
        self.create_checkbox(
            "Custom ITD?",
            "itd_custom",
            parent=self.subframes[self.section_locs["ITD"]],
            reveal_cat="Custom ITD",
        )
        # Spinboxes
        self.spinbox_vars = {}

        self.create_total_spinbox(
            "ITD range",
            "itd_range",
            0,
            5,
            increment=0.1,
            default=2,
            parent=self.subframes[self.section_locs["ITD"]],
            reveal_cat="ITD",
        )
        self.create_total_spinbox(
            "ITD step",
            "itd_step",
            0,
            1,
            increment=0.005,
            default=0.01,
            parent=self.subframes[self.section_locs["ITD"]],
            reveal_cat="ITD",
        )
        self.create_total_spinbox(
            "Number of trials",
            "itd_trials",
            0,
            1000,
            increment=1,
            default=400,
            parent=self.subframes[self.section_locs["ITD"]],
            reveal_cat="ITD",
        )
        self.create_checkbox(
            "Threshold options",
            "threshold_bool",
            parent=self.subframes[self.section_locs["ITD"]],
            reveal_cat="Threshold",
        )

        self.advanced_widget_args = {
            "entry": {
                "List of ITDs, separated by commas": {
                    "label": "List of ITDs, separated by commas",
                    "var_name": "itd_vals",
                    "parent": self.subframes[self.section_locs["ITD"]],
                    "reveal_cat": "Custom ITD",
                },
            },
            "spinbox": {
                "Number of synapses per group": {
                    "var_label": "Number of synapses per group",
                    "var_name": "numsyn",
                    "from_": 0,
                    "to": 20,
                    "increment": 1,
                    "default": 4,
                    "parent": self.subframes[self.section_locs["Excitation"]],
                    "reveal_cat": "Excitation",
                    "iterable": True,
                },
                "Synapse space": {
                    "var_label": "Synapse space",
                    "var_name": "synspace",
                    "from_": 0,
                    "to": 20,
                    "increment": 1,
                    "default": 7,
                    "parent": self.subframes[self.section_locs["Excitation"]],
                    "reveal_cat": "Excitation",
                    "iterable": True,
                },
                "Simultaneous": {
                    "var_label": "Number of syn. fibers",
                    "var_name": "numfiber",
                    "from_": 0,
                    "to": 10,
                    "increment": 1,
                    "default": 2,
                    "parent": self.subframes[self.section_locs["Excitation"]],
                    "reveal_cat": "Excitation",
                    "iterable": True,
                },
                "Excitatory fiber conductance": {
                    "var_label": "Excitatory fiber conductance",
                    "var_name": "exc_fiber_gmax",
                    "from_": 0,
                    "to": 0.1,
                    "increment": 0.005,
                    "default": 0.015,
                    "parent": self.subframes[self.section_locs["Excitation"]],
                    "reveal_cat": "Excitation",
                    "iterable": True,
                },

                "Threshold": {
                    "var_label": "Threshold",
                    "var_name": "threshold",
                    "from_": -100,
                    "to": 100,
                    "increment": 1,
                    "default": 25,
                    "parent": self.subframes[self.section_locs["ITD"]],
                    "reveal_cat": "Threshold",
                },
                "Inhibitory fiber gmax": {
                    "var_label": "Inhibitory fiber gmax",
                    "var_name": "inh_fiber_gmax",
                    "from_": 0,
                    "to": 1,
                    "increment": 0.001,
                    "default": 0.022,
                    "parent": self.subframes[self.section_locs["Inhibition"]],
                    "reveal_cat": "Inhibition",
                    "iterable": True,
                },
                "Inhibitory timing": {
                    "var_label": "Inhibitory timing",
                    "var_name": "inh_timing",
                    "from_": 0,
                    "to": 20,
                    "increment": 0.01,
                    "default": -0.32,
                    "parent": self.subframes[self.section_locs["Inhibition"]],
                    "reveal_cat": "Inhibition",
                    "iterable": True,
                },
                "Axon speed": {
                    "var_label": "Axon speed",
                    "var_name": "axonspeed",
                    "from_": 0,
                    "to": 5,
                    "increment": 0.25,
                    "default": 1,
                    "parent": self.subframes[self.section_locs["Axon"]],
                    "reveal_cat": "Axon",
                    "iterable": True,
                },
            },
            "checkbox": {
                "Absolute threshold": {
                    "label": "Absolute threshold",
                    "var_name": "absolute_threshold",
                    "default": False,
                    "parent": self.subframes[self.section_locs["ITD"]],
                    "reveal_cat": "Threshold",
                    "reveal": False,
                },
                "Excitatory conductance source": {
                    "label": "Use csv for exc. cond.?",
                    "var_name": "use_csv",
                    "default": False,
                    "parent": self.subframes[self.section_locs["Excitation"]],
                    "reveal_cat": "Excitation",
                },
            },
        }
        self.create_advanced_widgets(self.advanced_widget_args)
        # Run button
        self.subframes[self.section_locs["Send"]].columnconfigure(0, weight=1)
        self.subframes[self.section_locs["Send"]].columnconfigure(1, weight=1)
        self.run_button = ttk.Button(
            self.subframes[self.section_locs["Send"]],
            text="Run local",
            command=self.run_procedure,
        )
        self.run_button.grid(column=0, row=2, sticky=tk.EW)

        self.job_file_button = ttk.Button(
            self.subframes[self.section_locs["Send"]],
            text="Create job file",
            command=self.create_job,
        )
        self.job_file_button.grid(column=0, row=1, sticky=tk.EW)
        self.send_button = ttk.Button(
            self.subframes[self.section_locs["Send"]],
            text="Send job",
            command=self.send,
            state=tk.DISABLED,
        )
        self.send_button.grid(column=1, row=1, sticky=tk.EW)
        self.name_entry = self.create_name_entry(
            "Name", parent=self.subframes[self.section_locs["Name"]]
        )

        self.innervation_listbox = self.create_radiobuttons(
            "Innervation pattern",
            ["total", "random"],
            "innervation_pattern",
            parent=self.subframes[self.section_locs["Name"]],
            reveal_cat="Innervation",
        )

        # Set up matplotlib embedding

        # self.toolbar = NavigationToolbar2Tk(self.canvas_mpl, self.subframes[self.section_locs['Output']], pack_toolbar=False)
        # self.toolbar.update()

        self.update_frames()

    def update_cell_pic(self, cell_name):
        cell_pic_path = os.path.join(
            str(files("golding_NEURON").joinpath("itd_job_builder/cell_pics")), f"{cell_name}.png"
        )
        self.img = Image.open(cell_pic_path)
        self.img = self.img.resize([200, 200])
        self.img = ImageTk.PhotoImage(master=self.image_frame, image=self.img)
        self.label.config(image=self.img)
        self.label.pack()
        self.label.image = self.img
        self.update()

    def create_name_entry(self, label, parent=None):

        name_entered = tk.StringVar(value=label)
        entry = ttk.Entry(parent, textvariable=name_entered)
        entry.pack(pady=10, padx=10, anchor=tk.W)
        self.name_entered = name_entered
        return entry

    def create_textbox(self, label, parent=None):
        text_widget = scrolledtext.ScrolledText(parent)
        text_widget.pack(pady=10, padx=10, anchor=tk.CENTER, fill=tk.BOTH)
        text_widget.mark_set(tk.INSERT, tk.END)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.INSERT, label)
        text_widget.configure(state="disabled")
        return text_widget

    def update_textbox(self, textbox, text):
        textbox.configure(state="normal")
        textbox.delete(1.0, tk.END)
        textbox.insert(tk.INSERT, text)
        textbox.configure(state="disabled")

    def create_label(self, text, parent):
        label = ttk.Label(parent, text=text)
        label.pack(side=tk.TOP)
        return label

    def create_grid(self, rows=4, columns=2):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid = ttk.Frame(self, relief=tk.RAISED, padding=5)
        self.grid.grid(row=0, column=0, sticky="nsew")
        self.subgrids = np.empty((rows, columns), dtype=object)
        self.subframes = np.empty((rows, columns), dtype=object)
        self.super_subframes = np.empty((rows, columns), dtype=object)
        for i in range(rows):
            self.grid.rowconfigure(i, weight=1, minsize=200)
        for i in range(columns):
            if i == 0:
                self.grid.columnconfigure(i, weight=1, minsize=800, uniform="column")
            else:
                self.grid.columnconfigure(i, weight=1, minsize=450, uniform="column")
        for i in range(rows):
            for j in range(columns):
                self.subgrids[i, j] = ttk.Frame(self.grid, padding=5, relief=tk.RAISED)
                (
                    self.subgrids[i, j].grid(row=i, column=j, rowspan=2, sticky="nsew")
                    if i == 0 and j == 1
                    else self.subgrids[i, j].grid(row=i, column=j, sticky="nsew")
                )
                if i == 1 and j == 1:
                    self.subgrids[i, j].grid_forget()
                self.super_subframes[i, j] = VerticalScrolledFrame(self.subgrids[i, j])
                self.subframes[i, j] = self.super_subframes[i, j].interior
                self.super_subframes[i, j].pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def update_frames(self):
        for super_subframe in self.super_subframes.flatten():
            super_subframe.create()

    def create_advanced_widgets(self, advanced_widget_args):
        self.advanced_widgets = {
            "Excitation": [],
            "Inhibition": [],
            "Axon": [],
            "Send": [],
            "ITD": [],
            "Threshold": [],
            "Custom ITD": [],
            "Innervation": [],
        }
        for type_name, type_ in advanced_widget_args.items():
            # print(type_name),
            func = None
            if type_name == "spinbox":
                func = lambda widget_args: self.create_total_spinbox(**widget_args)
            elif type_name == "checkbox":
                func = lambda widget_args: self.create_checkbox(**widget_args)
            elif type_name == "radiobuttons":
                func = lambda widget_args: self.create_radiobuttons(**widget_args)
            elif type_name == "listbox":
                func = lambda widget_args: self.create_listbox(**widget_args)
            elif type_name == "entry":
                func = lambda widget_args: self.create_entry(**widget_args)
            for widget_key, widget_args in type_.items():
                # print(widget_args["reveal_cat"])
                widget_in_cat = func(widget_args)
                widget_in_cat.pack_forget()
                self.advanced_widgets[widget_args["reveal_cat"]].append(widget_in_cat)

    def create_entry(self, label, var_name, parent=None, reveal_cat=None):
        entered_vals = tk.StringVar(value=label)
        entry = tk.Entry(
            parent,
            textvariable=entered_vals,
            justify=tk.CENTER,
        )
        return entry

    def create_menubar(self):
        self.option_add("*tearOff", tk.FALSE)
        menubar = tk.Menu(self)
        self["menu"] = menubar
        menu_options = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_options, label="Options")
        self.advanced_option_state = tk.BooleanVar(value=False)
        menu_options.add_checkbutton(
            label="Advanced",
            command=self.update_advanced_view,
            onvalue=True,
            offvalue=False,
            variable=self.advanced_option_state,
        )
        return menubar

    def reveal_advanced(self, val, category):
        if val.get():
            for widget in self.advanced_widgets[category]:
                widget.pack(padx=4, pady=4, fill=tk.X, anchor=tk.CENTER)
        else:
            for widget in self.advanced_widgets[category]:
                widget.pack_forget()
        # self.update_frames()

    def create_listbox(
        self, label, var_name, values, parent=None, reveal_cat=None, pack=True
    ):
        choicesvar = tk.StringVar(value=values)
        listbox = tk.Listbox(
            parent,
            listvariable=choicesvar,
            selectmode=tk.EXTENDED,
            justify=tk.CENTER,
            height=10,
        )
        listbox.bind("<<ListboxSelect>>", lambda e: self.on_cell_select(e))
        if pack:
            listbox.pack(pady=1, padx=1, anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        return listbox

    def on_cell_select(self, event):
        # print("Selected cells:", event.widget.curselection())
        self.cell_selection = event.widget.curselection()
        self.update_cell_pic(self.cell_names[self.cell_selection[-1]])

    def create_checkbox(
        self,
        label,
        var_name,
        default=False,
        parent=None,
        pack=True,
        reveal_cat=None,
        command=None,
        reveal=True,
    ):
        var = tk.BooleanVar(value=default)
        if reveal_cat is not None and reveal:
            checkbox = ttk.Checkbutton(
                parent,
                text=label,
                variable=var,
                command=lambda: self.reveal_advanced(var, reveal_cat),
            )
        elif command is not None:
            checkbox = ttk.Checkbutton(
                parent, text=label, variable=var, command=command
            )
        else:
            checkbox = ttk.Checkbutton(parent, text=label, variable=var)
        if pack:
            checkbox.pack(padx=1, pady=1, anchor=tk.W)
        self.checkbox_vars[var_name] = var
        return checkbox

    def create_radiobuttons(
        self,
        major_label,
        minor_labels,
        var_name,
        default=False,
        parent=None,
        reveal_cat=None,
    ):
        var = tk.StringVar(value=minor_labels[0])
        frame = ttk.Frame(parent)
        frame.pack(pady=1, padx=1, anchor=tk.CENTER)
        label_string = tk.StringVar(value=major_label)
        label = ttk.Label(frame, textvariable=label_string)
        label.pack(side=tk.TOP, padx=1)
        for minor_label in minor_labels:
            radiobutton = ttk.Radiobutton(
                frame,
                text=minor_label,
                variable=var,
                value=minor_label,
                command=lambda: print(var.get()),
            )
            radiobutton.pack(padx=1, pady=1, side=tk.LEFT)
        self.radiobutton_vars[var_name] = var
        return frame

    def create_spinbox_frame(self, parent):
        frame = ttk.Frame(parent, borderwidth=1)
        frame.pack(pady=1, padx=1, anchor=tk.E, fill=tk.BOTH)
        frame.grid_columnconfigure(0, weight=1, uniform="spinbox")
        frame.grid_columnconfigure(1, weight=1, uniform="spinbox")
        frame.grid_columnconfigure(2, weight=1, uniform="spinbox")
        return frame

    def create_spinbox_label(self, frame, var_label, pos=(1, 0), **kwargs):
        label_string = tk.StringVar(value=var_label)
        label = ttk.Label(frame, text=label_string.get(), width=30, **kwargs)
        label.grid(row=pos[0], column=pos[1], padx=1, pady=1, sticky=tk.NSEW)
        return label

    def create_spinbox_widget(
        self, from_, to, increment, frame, default=0.0, pos=(1, 1)
    ):
        var = tk.DoubleVar(value=default)
        spinbox = ttk.Spinbox(
            frame,
            textvariable=var,
            from_=from_,
            to=to,
            increment=increment,
            width=10,
            justify=tk.CENTER,
        )
        row, col = pos
        spinbox.grid(
            column=col,
            row=row,
            padx=1,
            pady=1,
            sticky=tk.EW,
        )
        return spinbox, var

    def create_total_spinbox(
        self,
        var_label,
        var_name,
        from_,
        to,
        increment,
        default,
        parent,
        reveal_cat,
        iterable=False,
    ):
        frame = self.create_spinbox_frame(parent)
        label = self.create_spinbox_label(
            frame, var_label, justify=tk.RIGHT, pos=(0, 0)
        )
        spinbox, var = self.create_spinbox_widget(
            from_, to, increment, frame, default, pos=(0, 1)
        )
        if iterable:
            check = self.create_checkbox(
                "Iterate",
                f"{var_name}_iterable",
                parent=frame,
                pack=False,
                command=lambda: self.check_iteration(
                    var_name, reveal_cat, frame, spinbox, default, increment, from_, to
                ),
            )
            check.grid(row=0, column=2)

        self.spinbox_vars[f"{var_name}_base"] = var
        return frame

    def forget_widget(self, widget):
        try:
            widget.grid_forget()
            # print("Grid forget")
        except:
            try:
                widget.pack_forget()
                # print("Pack forget")
            except Exception:
                "Widget not found"

    def unforget_widget(self, widget, loc=None):
        try:
            widget.grid(
                row=loc[0],
                column=loc[1],
                padx=1,
                pady=1,
                sticky=tk.EW,
            )
        except:
            try:
                widget.pack()
            except Exception:
                "Widget not found"

    def check_iteration(
        self, var_name, reveal_cat, parent, basic_spinbox, default, increment, from_, to
    ):
        if self.checkbox_vars[f"{var_name}_iterable"].get():
            # self.forget_widgets(basic_spinbox)
            self.create_iteration(
                var_name,
                reveal_cat,
                parent,
                basic_spinbox,
                default,
                increment,
                from_,
                to,
            )

        else:
            for widget in self.iterables[var_name]["spinboxes"]:
                self.forget_widget(widget)
            for widget in self.iterables[var_name]["labels"]:
                self.forget_widget(widget)
            self.unforget_widget(basic_spinbox, loc=(0, 1))

    def create_iteration(
        self, var_name, reveal_cat, parent, basic_spinbox, default, increment, from_, to
    ):
        self.forget_widget(basic_spinbox)
        self.iterables[var_name] = {}
        iterable_labels = [
            self.create_spinbox_label(
                parent,
                "From",
                pos=(4, 0),
                anchor=tk.CENTER,
            ),
            self.create_spinbox_label(
                parent,
                "To",
                pos=(4, 1),
                anchor=tk.CENTER,
            ),
            self.create_spinbox_label(
                parent,
                "Increment",
                pos=(4, 2),
                anchor=tk.CENTER,
            ),
        ]
        iterables = [
            self.create_spinbox_widget(
                from_,
                to,
                increment=increment,
                default=default,
                frame=parent,
                pos=(3, 0),
            ),
            self.create_spinbox_widget(
                from_,
                to,
                increment=increment,
                default=default + increment,
                frame=parent,
                pos=(3, 1),
            ),
            self.create_spinbox_widget(
                increment * 0.1,
                increment * 10,
                increment=increment,
                default=increment,
                frame=parent,
                pos=(3, 2),
            ),
        ]
        self.iterables[var_name]["spinboxes"] = [x[0] for x in iterables]
        self.iterables[var_name]["labels"] = iterable_labels
        self.iterables[var_name]["values"] = [x[1] for x in iterables]

    def get_simulation_values(self):
        checkbox_values = {
            k: v.get() for k, v in self.checkbox_vars.items() if "iterable" not in k
        }
        active_iterable_keys = [
            k for k, v in self.checkbox_vars.items() if "iterable" in k and v.get()
        ]
        spinbox_values = {
            "_".join(k.split("_")[:-1]): v.get() for k, v in self.spinbox_vars.items()
        }
        radio_values = {
            k: v.get() for k, v in self.radiobutton_vars.items() if "iterable" not in k
        }
        listbox_values = self.cell_selection
        logger.info(f"Arguments with iterated values:{active_iterable_keys}")
        iterables = {}
        for key in active_iterable_keys:
            tagless_key = "_".join(key.split("_")[:-1])
            iterables[tagless_key] = [
                v.get() for v in self.iterables[tagless_key]["values"]
            ]
        # Call the itd_test function with the collected values
        # itd_test(**checkbox_values, **spinbox_values)
        filenames = [self.cell_names[i] for i in listbox_values]
        if checkbox_values["itd_custom"]:
            itd_vals = self.advanced_widgets["Custom ITD"][0].get()
            if itd_vals == "":
                logging.exception("No ITD values entered, but custom ITDs requested")
                raise ValueError("No ITD values entered, but custom ITDs requested")
            itd_vals = [float(x) for x in itd_vals.split(",")]
            checkbox_values["itd_vals"] = itd_vals
            logger.warning(f"itd vals:{itd_vals}")
        else:
            checkbox_values["itd_vals"] = None

        itd_tester = ITDJob(
            filenames=filenames,
            iterables=iterables,
            **checkbox_values,
            **spinbox_values,
            **radio_values,
        )
        return itd_tester

    def create_job(self, pickled=True, local=False):
        logger.info("Creating job")
        day = datetime.datetime.now().strftime("%y%m%d")
        namedate = f"{self.name_entered.get()}_{day}"
        itd_tester = self.get_simulation_values()
        self.itd_vals = itd_tester.itd_vals
        tasks = itd_tester.generate_tasks()
        iterables = itd_tester.iterables
        path = os.path.join(str(files("golding_NEURON").joinpath("itd_job_builder/job_files")), namedate)
        os.makedirs(path, exist_ok=True)
        try:
            with open(
                os.path.join(
                    path,
                    f"{namedate}.pkl",
                ),
                "wb",
            ) as f:
                pickle.dump({"tasks": tasks, "iterables": iterables}, f)
        except Exception as e:
            logger.error(f"Error dumpin,g run tasks/iterables to pickle", exc_info=e)
        logger.debug(f"Job tasks: {tasks}, iterables: {iterables}")
        logger.info("Job created successfully")
        self.create_paramlog(itd_tester, path)
        self.create_archive(temp=False if local else True, paramlog=itd_tester)
        self.send_button.configure(state="normal")
        return itd_tester

    def run_procedure(self, itd_tester=None):
        self.checkbox_vars["traces"].set(True)
        self.create_job(local=True)
        self.temp_subdir = os.path.join(self.temp_dir, "sub")
        self.itd_visual = ITDVisual(
            parent=self.subframes[self.section_locs["Output"]],
            itd_vals=self.itd_vals,
        )
        self.itd_visual.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        threading.Thread(target=JobRunner().run, args=(self.temp_subdir,)).start()
        self.itd_visual.search_for_new_pickles(self.temp_subdir)

    def open_send_window(self, **kwargs):
        self.send_window = NSGWindow(**kwargs)

    def open_send_window_bg(self, **kwargs):
        self.send_window = NSGWindow(**kwargs)
        # threading.Thread(target=self.open_send_window).start()

    def send(self):
        logger.info("Sending job")
        self.create_job()
        self.open_send_window(
            archive_dir=os.path.join(self.job_file_dir, self.namedate, self.namedate),
            job_name=self.name_entered.get(),
        )

    def create_paramlog(self, job, path):
        with open(os.path.join(path, "paramlog.txt"), "w") as f:
            f.write(f"Job name: {self.name_entered.get()}\n")
            f.write(f"Job date: {self.day}\n\n")
            f.write(f"Cells:\n")
            for cell in job.filenames:
                f.write(f"    {cell}\n")
            f.write(f"\nIterables:\n")
            for iterable, span in job.iterables.items():
                f.write(
                    f"    {iterable}:\n        {span[0]} -- +{span[2]} --> {span[1]}\n"
                )
            f.write(f"\nParameters:\n")
            for key, value in job.itd_args.items():
                if key not in ["tasks", "iterables"]:
                    if isinstance(value, list):
                        if len(value) > 10:
                            f.write(
                                f"    {key}: {', '.join(map(str, value[:10]))}, ...\n"
                            )
                    f.write(f"    {key}: {value}\n")

    def create_archive(self, temp=False, paramlog=None):
        try:
            rmtree(self.temp_dir)
        except:
            pass
        self.day = datetime.datetime.now().strftime("%y%m%d")
        self.namedate = f"{self.name_entered.get()}_{self.day}"
        os.makedirs(os.path.join(self.job_file_dir, self.namedate), exist_ok=True)

        copytree(
            os.path.join(str(files("golding_NEURON").joinpath("itd_job_builder")), "itd_job", "sub"),
            self.temp_subdir,
            dirs_exist_ok=True,
        )
        copyfile(
            os.path.join(
                str(files("golding_NEURON").joinpath("itd_job_builder")),
                "job_files",
                self.namedate,
                f"{self.namedate}.pkl",
            ),
            os.path.join(self.temp_subdir, f"{self.namedate}.pkl"),
        )
        os.mkdir(os.path.join(self.temp_subdir, "golding_NEURON"))
        for module in glob.glob(os.path.join(str(files("golding_NEURON")), "*.py")):
            if "itd_job" not in module:
                copyfile(
                    module,
                    os.path.join(
                        self.temp_subdir, "golding_NEURON", os.path.basename(module)
                    ),
                )
        if paramlog is not None:
            self.create_paramlog(paramlog, self.temp_subdir)
        make_archive(
            os.path.join(self.job_file_dir, self.namedate, self.namedate),
            "zip",
            self.temp_dir,
        )
        if temp:
            rmtree(self.temp_dir)
        try:
            os.mkdir(os.path.join(self.temp_subdir, "golding_NEURON", "logs"))
        except:
            pass
        logger.info("Archive created")


def main():
    logger.info("Starting ITD job builder")

    app = ITDBuildGUI()
    main_thread = app.window
    # sv_ttk.set_theme("dark")
    main_thread.mainloop()
    logger.info("ITD job builder closed")


if __name__ == "__main__":
    main()
