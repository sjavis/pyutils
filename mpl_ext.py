#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms

def autoscale_based_on(ax, lines):
    ax.dataLim = mtransforms.Bbox.unit()
    for line in lines:
        xy = np.vstack(line.get_data()).T
        ax.dataLim.update_from_data_xy(xy, ignore=False)
    ax.autoscale_view()
