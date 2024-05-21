import numpy as np


def get_slice(data, slice_axes):
    # slice_axes is a dict with keywords as the axes to slice and values for the positions to slice at.
    # If the value is between zero and one, it will take the fractional position
    assert isinstance(data, np.ndarray), "Input must be a numpy array"
    slc = [slice(None)] * data.ndim
    for ax in slice_axes:
        idx = slice_axes[ax]
        if (idx is None): continue
        if (idx>0 and idx<1): idx = int(idx*(data.shape[ax]-1))
        slc[ax] = idx
    return data[tuple(slc)]
