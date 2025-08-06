"""
This module provides functions for geometric and mathematical calculations used in neuronal modeling.
"""

import math


def get_line_from_points(point1: tuple[float,float], point2:tuple[float,float]) -> tuple[float, float]:
    """
    Calculate the slope and y-intercept of a line given two points.

    Parameters:
    ----------
    point1 : tuple
        Coordinates of the first point (x, y).
    point2 : tuple
        Coordinates of the second point (x, y).

    Returns:
    -------
    m : float
        Slope of the line.
    b : float
        Y-intercept of the line.
    """
    xdiff = point1[0] - point2[0]
    ydiff = point1[1] - point2[1]
    m = ydiff / xdiff if xdiff != 0 else float("inf")  # slope
    b = point1[1] - m * point1[0]  # y-intercept
    return m, b


def dist_from_line(line: tuple[float,float], point: tuple[float,float]) -> float:
    """
    Calculates the distance from a point to a line defined by its slope and y-intercept.
    The line is defined in the x-y plane, and the point is a 2D point (x, y).

    Parameters:
    ----------
    line : tuple
        Slope (m) and y-intercept (b) of the line.
    point : tuple
        Coordinates of the point (x, y).

    Returns:
    -------
    distance : float
        Perpendicular distance from the point to the line.
    """
    m, b = line
    if m == float("inf"):
        # Vertical line case
        return abs(point[0] - b)
    else:
        # Distance from point (x0, y0) to line y = mx + b
        x0, y0 = point
        return abs(m * x0 - y0 + b) / math.sqrt(m**2 + 1)


def define_xy_line(point1: tuple[float,float], point2: tuple[float,float], point3: tuple[float,float]) -> tuple[float, float]:
    """
    Defines a line in 3D space using two points and a third point to determine the plane.
    Returns the slope (m) and y-intercept (b) of the line in the x-y plane.

    Parameters:
    ----------
    point1 : tuple
        Coordinates of the first point (x, y, z).
    point2 : tuple
        Coordinates of the second point (x, y, z).
    point3 : tuple
        Coordinates of the third point (x, y, z) used to define the plane.

    Returns:
    -------
    m : float
        Slope of the line in the x-y plane.
    b : float
        Y-intercept of the line in the x-y plane.
    """
    xdiff = point1[0] - point2[0]
    ydiff = point1[1] - point2[1]

    if xdiff == 0:
        m = -float("inf")  # vertical line
        b = None
    else:
        m = -xdiff / ydiff
        b = point3[1] - m * point3[0]

    return m, b


def distance3D(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    """
    Calculates the Euclidean distance between two 3D points.

    Parameters:
    ----------
    a : tuple
        Coordinates of the first point (x, y, z).
    b : tuple
        Coordinates of the second point (x, y, z).

    Returns:
    -------
    distance : float
        Euclidean distance between the two points.
    """
    distance = abs(
        math.sqrt(((a[0] - b[0]) ** 2) + ((a[1] - b[1]) ** 2) + ((a[2] - b[2]) ** 2))
    )
    return distance

