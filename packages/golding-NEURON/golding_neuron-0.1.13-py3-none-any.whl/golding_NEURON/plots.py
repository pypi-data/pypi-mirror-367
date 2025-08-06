"""
This module provides plotting and visualization functions for NEURON cell simulations and analysis.
"""

import os
from pathlib import Path
import numpy as np
import random
from neuron import h
import matplotlib.pyplot as plt
import plotly
from .cell_calc import tiplist
from .sims import syn_place, propagation_test


def syntipplot(cell, sectionList, listName, normalized=False):
    """
    Plot the voltage response at the ends of dendritic sections after synaptic input.

    Parameters:
    - cell: The neuron cell object.
    - sectionList: List of sections to be included in the plot.
    - listName: Name of the list, used for naming saved files.
    - normalized: Boolean indicating whether to normalize the voltage axis.
    """
    # create and prepare plot
    currentsectionlist = sectionList
    if not os.path.isdir("ByPlot/SynapsesAtEnds"):
        os.mkdir("ByPlot/SynapsesAtEnds")
    if normalized == True:
        if not os.path.isdir("ByPlot/SynapsesAtEnds_Normalized"):
            os.mkdir("ByPlot/SynapsesAtEnds_Normalized")
    syntipsfig, syntipsax = plt.subplots(figsize=(10, 5))
    syntipsax.set_xlim(left=0.2, right=2.2)
    syntipsax.set_ylim(top=-50, bottom=-60)
    syntipsax.set_title(os.path.basename(cell.filepath))
    syntipsax.set_ylabel("Potential (mV)")
    syntipsax.set_xlabel("Time after EPSP (ms)")

    ends = tiplist(currentsectionlist)  # get a list of sections at ends of branches
    count = 0
    for sec in ends:
        print()
    for sec in ends:
        # create synapses at the ends of each section
        syntip = h.Exp2Syn(sec(1))
        syntip.tau1 = 0.271
        syntip.tau2 = 0.271
        syntip.e = 15
        netcon = h.NetCon(None, syntip, sec=sec)
        netcon.weight[0] = 0.025

        t = h.Vector().record(h._ref_t)
        v = h.Vector().record(cell.soma[0](0.5)._ref_v)

        h.finitialize()
        h.dt = 1
        h.continuerun(3000)
        h.dt = 0.001
        h.frecord_init()
        netcon.event(3000.2)
        h.continuerun(3002.5)
        # run sim and record vectors
        # convert to python lists
        t_python = t.to_python()
        v_python = v.to_python()
        # intializing arrays with first section test
        if count == 0:
            syntipTimeArray = t_python
            syntipVoltageArray = v_python
        # stacking the rest of the vectors in a 2d array
        else:
            syntipTimeArray = np.vstack((syntipTimeArray, t_python))
            syntipVoltageArray = np.vstack((syntipVoltageArray, v_python))
        count += 1

    count = 0
    # change it so that there is a temporarily accessed 1d array instead of indexing the 2d array
    for i in range(len(syntipTimeArray)):

        if len(list(ends)) == 1:  ###UPDATE WITH THIS IF CASE
            syntipsax.plot(syntipTimeArray - 3000, syntipVoltageArray)
            break
        else:
            syntipsax.plot(
                syntipTimeArray[i, :] - 3000, syntipVoltageArray[i, :]
            )  # plot each sim. data

    pdf = "{0}_endsynapses.pdf".format(
        "ByCell/"
        + Path(cell.filepath).stem
        + "/"
        + os.path.basename(cell.filepath)
        + "_"
        + listName
    )
    plt.savefig(pdf, bbox_inches="tight", pad_inches=0.5)
    pdf = "{0}_endsynapses.pdf".format(
        "ByPlot/SynapsesAtEnds/" + os.path.basename(cell.filepath) + "_" + listName
    )
    plt.savefig(pdf, bbox_inches="tight", pad_inches=0.5)
    syntipsax.clear()
    if normalized == True:  # check for normalized request
        syntipsax.set_xlim(left=0.2, right=1.2)
        syntipsax.set_title(os.path.basename(cell.filepath))
        syntipsax.set_ylabel("Normalized potential")
        syntipsax.set_xlabel("Time after EPSP (ms)")

        if len(list(ends)) == 1:  ###UPDATE WITH THIS IF CASE
            sectionRest = syntipVoltageArray[0]  # record resting pot. and max voltage
            sectionMax = np.max(syntipVoltageArray)
            for i in range(len(syntipVoltageArray)):
                # normalize the voltage (-1,0): repolarization& (0,1): depolarization
                syntipVoltageArray[i] = syntipVoltageArray[i] - sectionRest
                syntipVoltageArray[i] = syntipVoltageArray[i] / (
                    sectionMax - sectionRest
                )
            syntipsax.plot(
                syntipTimeArray - 3000, syntipVoltageArray
            )  # plot each sim. data

        else:
            for i in range(len(syntipTimeArray)):
                sectionRest = syntipVoltageArray[
                    i, 0
                ]  # record resting pot. and max voltage
                sectionMax = np.max(syntipVoltageArray[i, :])
                for j in range(len(syntipVoltageArray[i, :])):
                    # normalize the voltage (-1,0): repolarization& (0,1): depolarization
                    syntipVoltageArray[i, j] = syntipVoltageArray[i, j] - sectionRest
                    syntipVoltageArray[i, j] = syntipVoltageArray[i, j] / (
                        sectionMax - sectionRest
                    )
            for i in range(len(syntipTimeArray)):
                syntipsax.plot(
                    syntipTimeArray[i, :] - 3000, syntipVoltageArray[i, :]
                )  # plot each sim. data
        pdf = "{0}_endsynapses_Normalized.pdf".format(
            "ByCell/"
            + Path(cell.filepath).stem
            + "/"
            + os.path.basename(cell.filepath)
            + "_"
            + listName
        )
        plt.savefig(pdf, bbox_inches="tight", pad_inches=0.5)
        pdf = "{0}_endsynapses_Normalized.pdf".format(
            "ByPlot/SynapsesAtEnds_Normalized/"
            + os.path.basename(cell.filepath)
            + "_"
            + listName
        )
        plt.savefig(pdf, bbox_inches="tight", pad_inches=0.5)

        # adjust filename output

    plt.close(syntipsfig)


def plotlyplot(
    cell,
    timeArray,
    sectionList,
    print_out=True,
    name=None,
    param_min=None,
    param_max=None,
    scale=True,
):
    """
    Generate a 3D plot of the cell with voltage mapped to color using Plotly.

    Parameters:
    - cell: The neuron cell object.
    - timeArray: 2D array of time values for each segment in each section.
    - sectionList: List of sections to be included in the plot.
    - print_out: Boolean indicating whether to print the plot to a file.
    - name: Optional name for the output file.
    - param_min: Optional minimum value for scaling the color gradient.
    - param_max: Optional maximum value for scaling the color gradient.
    - scale: Boolean indicating whether to include scale bars in the plot.
    """
    currentsectionlist = h.SectionList(sectionList)
    sectionCount = 0
    minTime = timeArray[0][0]
    maxTime = timeArray[0][0]
    # setting all the voltage values to time after onset at max voltage values (weird workaround for neuron plotting)
    for sec in currentsectionlist:
        sectionDelayArray = np.zeros(sec.nseg)
        segmentCount = 0
        for seg in sec:
            segmentDelay = timeArray[sectionCount][segmentCount]
            sectionDelayArray[segmentCount] = segmentDelay

            seg.v = segmentDelay
            # print(seg.v)
            # checking for new max/min values for cell gradient
            if segmentDelay < minTime:
                minTime = segmentDelay
                # print("new min")
            if segmentDelay > maxTime:
                maxTime = segmentDelay
                # print("newmax")
            segmentCount += 1  # move on to next segment
        sectionCount += 1
    if print_out == True:
        if name != None and type(name) == str:
            file_name = name
        else:
            file_name = os.path.basename(cell.filepath)

        if not os.path.isdir("3Dplots"):
            os.mkdir("3Dplots")
        if not os.path.isdir("2Dplots"):
            os.mkdir("2Dplots")

        def scale_bars(cell, origin=(0, 0, 0), length=100):

            cell.x_scale = h.Section("z_scale")
            cell.y_scale = h.Section("y_scale")
            cell.z_scale = h.Section("x_scale")
            cell.scale_bars = [cell.x_scale, cell.y_scale, cell.z_scale]
            cell.scale_bars.append(cell.x_scale)
            cell.scale_bars.append(cell.y_scale)
            cell.scale_bars.append(cell.z_scale)

            cell.x_scale.pt3dclear()
            cell.x_scale.pt3dadd(origin[0], origin[1], origin[2], 1)
            cell.x_scale.pt3dadd(origin[0] + length, origin[1], origin[2], 1)
            cell.y_scale.pt3dclear()
            cell.y_scale.pt3dadd(origin[0], origin[1], origin[2], 1)
            cell.y_scale.pt3dadd(origin[0], origin[1] + length, origin[2], 1)
            cell.z_scale.pt3dclear()
            cell.z_scale.pt3dadd(origin[0], origin[1], origin[2], 1)
            cell.z_scale.pt3dadd(origin[0], origin[1], origin[2] + length, 1)

        if scale:
            scale_bars(cell)
            secs_to_plot = list(currentsectionlist) + cell.scale_bars
        else:
            secs_to_plot = list(currentsectionlist)
        visual = h.PlotShape(h.SectionList(secs_to_plot), True)
        visual.variable("v")
        # print(minTime, maxTime)
        if param_max != None:
            maxTime = param_max
        if param_min != None:
            minTime = param_min
        visual.scale(
            minTime, maxTime
        )  # sets gradient scaling to max and min value for cell

        visual.exec_menu("10% Zoom out")
        visual.exec_menu("10% Zoom out")
        visual.exec_menu("Shape Plot")
        # Set the view to the plot window for better visualization
        visual.exec_menu("View = plot")
        visual.exec_menu("View = plot")
        visual.show(0)
        visual.printfile("2Dplots/{0}.eps".format(file_name))
        # visual.printfile(
        #     "ByCell/"
        #     + Path(cell.filepath).stem
        #     + "/"
        #     + os.path.basename(cell.filepath)
        #     + ".eps"
        # )
        plotlyplot = visual.plot(plotly)
        plotlyplot.show()
        # plt.show()
        # outputs plotly model to an html file
        # html = "{0}_3D.html".format(
        #     "ByCell/" + Path(cell.filepath).stem + "/" + os.path.basename(cell.filepath)
        # )
        # plotlyplot.write_html(html)
        html = "{0}_3D.html".format("3Dplots/" + file_name)
        plotlyplot.write_html(html)
    return plotlyplot, minTime, maxTime
    # print(sectionDelayArray,"||||",sectionDistanceArray)


# In[9]:


def antlergram(cell, timeArray, sectionList, print_out=True, name=None):
    """
    Plot an antlergram: delay vs. distance for each section in the cell.

    Parameters:
    - cell: The neuron cell object.
    - timeArray: 2D array of time values for each segment in each section.
    - sectionList: List of sections to be included in the plot.
    - print_out: Boolean indicating whether to print the plot to a file.
    - name: Optional name for the output file.
    """
    currentsectionlist = sectionList
    if not os.path.isdir("Antlergrams"):
        os.mkdir("Antlergrams")
    # yticks = [0.5, 0.6, 0.7, 0.8]
    # xticks = [-200, -100, 0, 100, 200]
    antlergramFig, antlergramAx = plt.subplots(figsize=(2.1, 5), layout="constrained")
    antlergramFig.set_figheight(1.1)
    antlergramFig.set_figwidth(2)
    # antlergramAx.set_title(os.path.basename(cell.filepath))
    antlergramAx.set_xlim(left=-200, right=200)
    antlergramAx.set_ylim(top=55)
    antlergramAx.xaxis.set_tick_params(labelsize=8, labelfontfamily="arial")
    antlergramAx.yaxis.set_tick_params(labelsize=8, labelfontfamily="arial")
    # antlergramAx.set_xticks(xticks)
    # antlergramAx.set_yticks(yticks)
    # antlergramAx.set_aspect(675)
    antlergramAx.set_ylabel("Peak delay (ms)", fontsize=8, fontfamily="arial")
    antlergramAx.set_xlabel("Distance (µm)", fontsize=8, fontfamily="arial")
    antlergramAx.spines["top"].set_visible(False)
    antlergramAx.spines["right"].set_visible(False)
    # ratioMEP = mep(cell, cell.lateral) / mep(cell, cell.medial)
    # mepText = "MEP Ratio: " + str(ratioMEP)
    # antlergramAx.text(-200,0.15,mepText, fontsize = 8, fontfamily= 'arial')
    antlergramAx.grid(True, linestyle=":", alpha=0.75)
    sectionCount = 0
    segmentVoltageMax_TimeMin = timeArray[0][0]
    segmentVoltageMax_TimeMax = timeArray[0][0]
    for sec in currentsectionlist:
        sectionDelayArray = np.zeros(sec.nseg)
        sectionDistanceArray = np.zeros(sec.nseg)
        segmentCount = 0
        for seg in sec:
            segmentDelay = timeArray[sectionCount][segmentCount]
            segmentDistance = h.distance(
                cell.somatic[0](0.5),
                seg,
            ) + (cell.somatic[0].L / 2)
            print(segmentDelay, segmentDelay)
            sectionDelayArray[segmentCount] = segmentDelay
            if sec in cell.medial_nofilopodia:
                segmentDistance = -segmentDistance
            sectionDistanceArray[segmentCount] = segmentDistance
            segmentCount += 1
        antlergramAx.plot(
            sectionDistanceArray, sectionDelayArray, linewidth=0.5, c="black"
        )
        sectionCount += 1
    if print_out == True:
        if name != None:
            file_name = name
        else:
            file_name = os.path.basename(cell.filepath)
        # pdf = "{0}_antlergram.pdf".format(
        #     "ByCell/" + Path(cell.filepath).stem + "/" + os.path.basename(cell.filepath)
        # )
        # plt.savefig(pdf, bbox_inches="tight", pad_inches=0.5, transparent=True)
        pdf = "{0}_antlergram.pdf".format("Antlergrams/" + file_name)
        plt.savefig(pdf, transparent=True, pad_inches=0)
        # antlerFig.show(warn=False)
        # plt.close(antlergramFig)
        # antlergramFig.show(warn = False)
    return antlergramFig, antlergramAx


# In[8]:


def asymmetry(cell, samplenum, graph=True, save=True):
    """
    Analyze and plot the asymmetry in voltage response between two branches.

    Parameters:
    - cell: The neuron cell object.
    - samplenum: Number of samples to use for the analysis.
    - graph: Boolean indicating whether to generate a graph of the results.
    - save: Boolean indicating whether to save the results to a file.
    """
    branch1Synapses = h.List()
    branch2Synapses = h.List()
    samples = samplenum
    maxVbranch1 = np.zeros(samples)
    maxVbranch2 = np.zeros(samples)
    maxVtimebranch1 = np.zeros(samples)
    maxVtimebranch2 = np.zeros(samples)
    if graph == True or save == True:
        asymmetryFig, asymmetryAx = plt.subplots(nrows=2, figsize=(10, 10))
        branch1Fig, branch1Ax = plt.subplots()
        branch1Title = (
            os.path.basename(cell.filepath) + " branch 1 (n = " + str(samples) + ")"
        )
        branch2Title = (
            os.path.basename(cell.filepath) + " branch 2 (n = " + str(samples) + ")"
        )
        asymmetryAx[0].set_title(branch1Title)
        asymmetryAx[1].set_title(branch2Title)
        # asymmetryAx[0].set_ylim(top = -53.5, bottom = -58.5)
        # asymmetryAx[1].set_ylim(top = -53.5, bottom = -58.5)
        asymmetryAx[0].set_xlim(left=-0.5, right=3)
        asymmetryAx[1].set_xlim(left=-0.5, right=3)
        asymmetryAx[0].set_ylabel("Potential @ soma (mV)")
        asymmetryAx[1].set_ylabel("Potential @ soma (mV)")
        asymmetryAx[0].set_xlabel("Time after EPSP (ms)")
        asymmetryAx[1].set_xlabel("Time after EPSP (ms)")

    print("testing", samples, "points")
    for sec in cell.lateral:
        sectionSynapseList = synplace(sec)
        for syn in sectionSynapseList:
            branch1Synapses.append(syn)
    for sec in cell.medial:
        sectionSynapseList = synplace(sec)
        for syn in sectionSynapseList:
            branch2Synapses.append(syn)
    print("branch 1 synapses:", len(branch1Synapses))
    print("branch 2 synapses:", len(branch2Synapses))
    for i in range(samples):
        randomNumber = random.randint(0, len(branch1Synapses) - 1)
        netcon = h.NetCon(None, branch1Synapses[randomNumber])
        synt = h.Vector().record(h._ref_t)
        synv = h.Vector().record(cell.somatic[0](0.5)._ref_v)
        h.finitialize(-58)
        h.dt = 1
        h.continuerun(2999)
        netcon[0].weight = 0.017
        netcon.event(3000)
        h.dt = 0.001
        h.frecord_init()
        h.continuerun(3002)
        synt = synt - 3000
        asymmetryAx[0].plot(synt, synv)
        maxV = synv.max() - synv[0]
        maxVtime = synt[synv.max_ind()]
        maxVbranch1[i] = maxV
        maxVtimebranch1[i] = maxVtime
        print("\rbranch 1:", i + 1, "/", samples, end=" ")
    print("\r")
    branch1AverageV = np.average(maxVbranch1)
    branch1AverageTime = np.average(maxVtimebranch1)
    branch1string = (
        "Average depol.:"
        + f"{branch1AverageV:6.4f}"
        + "mV \nAverage delay:"
        + f"{(branch1AverageTime):6.4f}"
        + "ms"
    )
    print(branch1string)

    for i in range(samples):
        randomNumber = random.randint(0, len(branch2Synapses) - 1)
        netcon = h.NetCon(None, branch2Synapses[randomNumber])
        synt = h.Vector().record(h._ref_t)
        synv = h.Vector().record(cell.somatic[0](0.5)._ref_v)
        h.finitialize(-58)
        h.dt = 1
        h.continuerun(2999)
        netcon[0].weight = 0.017
        netcon.event(3000)
        h.dt = 0.001
        h.frecord_init()
        h.continuerun(3002)
        synt = synt - 3000
        asymmetryAx[1].plot(synt, synv)
        maxV = synv.max() - synv[0]
        maxVtime = synt[synv.max_ind()]
        maxVbranch1[i] = maxV
        maxVtimebranch1[i] = maxVtime
        print("\rbranch 2:", i + 1, "/", samples, end=" ")
    print("\r")

    branch2AverageV = np.average(maxVbranch2)
    branch2AverageTime = np.average(maxVtimebranch2)
    branch2string = (
        "Average depol.: "
        + f"{branch2AverageV:6.4f}"
        + "mV \nAverage delay: "
        + f"{(branch2AverageTime):6.4f}"
        + "ms"
    )
    print(branch2string)

    ratioV = branch1AverageV / branch2AverageV  # lateral over medial
    diffT = branch1AverageTime - branch2AverageTime  # lateral minus medial
    ratioVstring = "Average depol. ratio: " + f"{ratioV:4.3f}"
    diffTstring = "Average delay difference: " + f"{diffT:4.3f}"
    # print(ratioVstring)
    # print(ratioTstring)

    if graph == True or save == True:
        asymmetryAx[0].text(3.5, -57, branch1string)
        asymmetryAx[1].text(3.5, -57, branch2string)
        ratioText = asymmetryFig.text(0.925, 0.475, ratioVstring)
        ratioText = asymmetryFig.text(0.925, 0.5, diffTstring)
        if save == True:
            if not os.path.isdir("ByPlot/VoltageDelayAsymmetry"):
                os.mkdir("ByPlot/VoltageDelayAsymmetry")
            pdf = "{0}_asymmetry.pdf".format(
                "ByCell/"
                + Path(cell.filepath).stem
                + "/"
                + os.path.basename(cell.filepath)
            )
            asymmetryFig.savefig(pdf, bbox_inches="tight", pad_inches=0.5)
            pdf = "{0}_asymmetry.pdf".format(
                "ByPlot/VoltageDelayAsymmetry/" + os.path.basename(cell.filepath)
            )
            asymmetryFig.savefig(pdf, bbox_inches="tight", pad_inches=0.5)
        plt.close(asymmetryFig)
    return diffT, branch1AverageTime, branch2AverageTime


def shapeplot(cell, sectionlist=None, variable=None):
    """
    Plot the shape of the cell or a section list, optionally coloring by a variable.

    Parameters:
    - cell: The neuron cell object.
    - sectionlist: Optional list of sections to be included in the plot.
    - variable: Optional variable to color the sections by.
    """
    currentsectionlist = sectionlist
    if not os.path.isdir("ByPlot/CellPics"):
        os.mkdir("ByPlot/CellPics")
    visual = h.PlotShape(currentsectionlist, True)
    # print(minTime, maxTime)
    if variable:
        visual.variable(variable)
    visual.show(0)
    visual.printfile("ByPlot/CellPics/{0}.eps".format(os.path.basename(cell.filepath)))
    visual.printfile(
        "{0}_pic.eps".format(
            Path(cell.filepath).stem + "/" + os.path.basename(cell.filepath)
        )
    )
