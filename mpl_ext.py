#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.colors import to_rgb


def autoscale_based_on(ax, lines):
    ax.dataLim = mtransforms.Bbox.unit()
    for line in lines:
        xy = np.vstack(line.get_data()).T
        ax.dataLim.update_from_data_xy(xy, ignore=False)
    ax.autoscale_view()


def map_colors(data, colors):
    assert data.shape[-1] == len(colors)
    colors = np.array([to_rgb(c) for c in colors])**2 # Square to linearise RGB intensities
    return np.sqrt(1 - np.dot(data, 1-colors).clip(0,1)) # 1-color so that empty=white
