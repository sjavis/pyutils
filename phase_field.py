#!/usr/bin/env python3
import numpy as np
import scipy.optimize


def pair_data(data, pair, mask_level=0.1):
    if (pair is None): return np.ma.array(data)
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


def fit_circle(data, level=0, pair=None, params_init=None, plot=False, mask_level=0.1):
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
        import matplotlib.pyplot as plt
        phi = np.linspace(-np.pi, np.pi, 100)
        x = x0 + r0 * np.cos(phi)
        y = y0 + r0 * np.sin(phi)
        plt.imshow(data.data.T, origin='lower')
        plt.plot(points[0], points[1], 'r.')
        plt.plot(x, y, 'k-')
        plt.xlim(0, data.shape[0])
        plt.ylim(0, data.shape[1])
        plt.show()
    return x0, y0, r0


def fit_y(data, level=0, pair=None, plot=False, mask_level=0.1):
    # Get the points on the interface
    data = pair_data(data, pair, mask_level)
    points = interface_points(data, level)
    # Fit a line
    line_eval = lambda y0, points: np.sum((points[1]-y0)**2)
    res = scipy.optimize.minimize(line_eval, [0], points)
    y0, = res.x
    # Plot?
    if (plot):
        import matplotlib.pyplot as plt
        plt.imshow(data.data.T, origin='lower')
        plt.plot(points[0], points[1], 'r.')
        plt.plot([0,data.shape[0]], [y0,y0], 'k-')
        plt.xlim(0, data.shape[0])
        plt.ylim(0, data.shape[1])
        plt.show()
    return y0


def plane_eval(params, points):
    r0, xnorm, ynorm, znorm = params
    normal = [xnorm, ynorm] if (points.ndim == 2) else [xnorm, ynorm, znorm]
    r = np.dot(normal, points) / np.linalg.norm(normal)
    return np.sum((r - r0)**2)

def fit_plane(data, level=0, pair=None, plot=False, mask_level=0.1):
    # Get the points on the interface
    data = pair_data(data, pair, mask_level)
    points = interface_points(data, level)
    # Fit a line
    res = scipy.optimize.minimize(plane_eval, [0, 1, 1, 0], points)
    r0 = res.x[0]
    normal = np.array(res.x[1:points.ndim+1])
    # Make normal a unit vector
    norm_mag = np.linalg.norm(normal)
    normal = normal / norm_mag
    # Plot?
    if (plot):
        import matplotlib.pyplot as plt
        if (np.abs(normal[0])/data.shape[0] < np.abs(normal[1])/data.shape[1]):
            x = np.array([0, data.shape[0]])
            y = (r0 - x*normal[0]) / normal[1]
        else:
            y = np.array([0, data.shape[1]])
            x = (r0 - y*normal[1]) / normal[0]
        plt.imshow(data.data.T, origin='lower')
        plt.plot(points[0], points[1], 'r.')
        plt.plot(x, y, 'k-')
        plt.xlim(0, data.shape[0])
        plt.ylim(0, data.shape[1])
        plt.show()
    return r0, normal


def measure_angle2d(solid, order_param, plot=False, mask_level=0.1):
    order_param = np.ma.masked_where(solid>mask_level, order_param)

    xc, yc, rad = fit_circle(order_param, 0)
    r0, normal = fit_plane(solid, 0.5)
    centre_height = np.sqrt(((xc - r0)*normal[0])**2 + ((yc - r0)*normal[1])**2)
    contact_angle = np.arccos(np.clip(-centre_height / rad, -1, 1)) * 180 / np.pi

    # Plot?
    if (plot):
        import matplotlib.pyplot as plt
        lx, ly = solid.shape
        plt.pcolormesh(solid.T, cmap='Blues')
        plt.pcolormesh(order_param.T, cmap='PRGn')

        phi = np.linspace(-np.pi, np.pi, 100)
        xcirc = xc + rad * np.cos(phi)
        ycirc = yc + rad * np.sin(phi)
        if (np.abs(normal[0])/lx < np.abs(normal[1])/ly):
            xplane = np.array([0, lx])
            yplane = (r0 - xplane*normal[0]) / normal[1]
        else:
            yplane = np.array([0, ly])
            xplane = (r0 - yplane*normal[1]) / normal[0]
        plt.plot(xcirc, ycirc, lw=2, c='k')
        plt.plot(xplane, yplane, lw=2, c='k')

        points_circ = interface_points(order_param, 0)
        points_plane = interface_points(solid, 0.5)
        plt.plot(points_circ[0], points_circ[1], 'r.', ms=2)
        plt.plot(points_plane[0], points_plane[1], 'r.', ms=2)

        plt.xlim(0, lx)
        plt.ylim(0, ly)
        plt.show()
    return contact_angle
