#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize


def pair_data(data, pair, mask_level=0.1):
    if (pair is None): return data
    # Get order parameter
    c1 = data[...,pair[0]]
    c2 = data[...,pair[1]]
    op = c1 - c2
    # Apply mask
    mask = 1-(c1+c2) > mask_level
    return np.ma.masked_array(op, mask)


def interface_points(data, level):
    binary = data > level
    points = np.empty((data.ndim,0))
    for axis in range(data.ndim):
        # Get the points either side of the interface
        points1 = np.ma.where(np.diff(binary, axis=axis))
        points2 = tuple(p+(i_ax==axis) for i_ax, p in enumerate(points1))
        # Interpolate between the points
        values1 = data[points1]
        values2 = data[points2]
        interp = (level - values1) / (values2 - values1)
        # Add positions to array
        points_ax = np.array(points1, dtype=float)
        points_ax[axis] += interp
        points = np.concatenate((points, points_ax), axis=1)
    return points


def circle_eval(params, points):
    x0, y0, k0 = params
    r = np.sqrt((points[0]-x0)**2 + (points[1]-y0)**2)
    return np.sum((r-1/k0)**2)


def fit_circle(data, pair=None, params_init=None, level=0, plot=False, mask_level=0.1):
    # Get the points on the interface
    data = pair_data(data, pair, mask_level)
    points = interface_points(data, level)
    # Fit a circle
    if (params_init is None): params_init = [data.shape[0]/2, data.shape[1]/2, 20]
    params_init[2] = 1 / params_init[2] # Radius -> curvature
    res = scipy.optimize.minimize(circle_eval, params_init, points)
    x0, y0, k0 = res.x
    r0 = 1 / k0
    # Plot?
    if (plot):
        plt.imshow(data.data.T, origin='lower')
        plt.plot(points[0], points[1], 'r.')
        phi = np.linspace(-np.pi, np.pi, 100)
        x = x0 + r0 * np.cos(phi)
        y = y0 + r0 * np.sin(phi)
        plt.plot(x, y, 'k-')
        plt.xlim(0, data.shape[0])
        plt.ylim(0, data.shape[1])
        plt.show()
    return x0, y0, r0


def fit_y(data, pair=None, level=0, plot=False, mask_level=0.1):
    # Get the points on the interface
    data = pair_data(data, pair, mask_level)
    points = interface_points(data, level)
    # Fit a line
    line_eval = lambda y0, points: np.sum((points[1]-y0)**2)
    res = scipy.optimize.minimize(line_eval, [0], points)
    y0, = res.x
    # Plot?
    if (plot):
        plt.imshow(data.data.T, origin='lower')
        plt.plot(points[0], points[1], 'r.')
        plt.plot([0,data.shape[0]], [y0,y0], 'k-')
        plt.xlim(0, data.shape[0])
        plt.ylim(0, data.shape[1])
        plt.show()
    return y0
