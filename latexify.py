import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

latex_width_pt = 455.244  # Get this from LaTeX using \the\textwidth
dpi = 500
axis_formatter = None

def update_width(width):
    ''' Update the latex page width, found using \the\textwidth. Default: 455.244
    Can also use 'r4', 'r4-single', and 'r4-double' for revtex4 sizes.'''
    global latex_width_pt
    if (width == 'r4'):
        latex_width_pt = 455.244
    elif (width == 'r4-single'):
        latex_width_pt = 246
    elif (width == 'r4-double'):
        latex_width_pt = 510
    elif (width == 'natcomm-single'):
        latex_width_pt = 255.118
    elif (width == 'natcomm-double'):
        latex_width_pt = 510.236
    elif (width == 'nature-single'):
        latex_width_pt = 252.283
    elif (width == 'nature-double'):
        latex_width_pt = 518.74
    else:
        latex_width_pt = width

def figsize(scale_width, ratio=None):
    inches_per_pt = 1.0/72.27                            # Convert pt to inch
    if ratio is None: ratio = (np.sqrt(5.0)-1.0)/2.0     # Aesthetic ratio (height/width)
    fig_width = latex_width_pt*inches_per_pt*scale_width # width in inches
    fig_height = fig_width*ratio                         # height in inches
    fig_size = [fig_width,fig_height]
    return fig_size


### Matplotlib parameters (LaTeX, fontsize, etc.) ###
options = {
    "text.usetex": True,                  # use LaTeX to write all text
    "pgf.texsystem": "pdflatex",          # change this if using xetex or lautex
    "pgf.preamble": "\n".join([
        r"\usepackage[utf8x]{inputenc}",  # use utf8 fonts becasue your computer can handle it :)
        r"\usepackage[T1]{fontenc}",      # plots will be generated using this preamble
        ]),
    "text.latex.preamble": "\n".join([
        r"\usepackage{amsmath}",
        r"\usepackage{bm}",               # bold math symbols
        ]),

    "font.family": "serif",
    "font.serif": [],                     # blank entries should cause plots to inherit fonts from the document
    "font.sans-serif": [],
    "font.monospace": [],
    "font.size": 10,
    "axes.labelsize": 10,                 # LaTeX default is 10pt font.
    "legend.fontsize": 8,                 # Make the legend/label fonts a little smaller

    "xtick.labelsize": 8,
    "xtick.direction": "in",
    "xtick.top": True,
    "ytick.labelsize": 8,
    "ytick.direction": "in",
    "ytick.right": True,
    "axes.linewidth": 0.7,

    "figure.figsize": figsize(0.9),       # default fig size of 0.9 textwidth
    }
mpl.rcParams.update(options)

def format_axes(ax):
    if (axis_formatter is not None):
        ax.xaxis.set_major_formatter(axis_formatter)
        ax.yaxis.set_major_formatter(axis_formatter)

class FigureWrapper():
    def __init__(self, fig=None, *args, **kwargs):
        if (fig is None):
            fig = plt.Figure(*args, **kwargs)
        self.fig = fig
    def add_axes(self, *args, **kwargs):
        ax = self.fig.add_axes(*args, **kwargs)
        format_axes(ax)
        return ax
    def __getattr__(self, attr):
        return getattr(self.fig, attr)


### User functions ###
def figure(width, ratio=None, **kwargs):
    fig = plt.figure(figsize=figsize(width, ratio), **kwargs)
    return FigureWrapper(fig)

def subplots(width, ratio=None, **kwargs):
    fig, ax_list = plt.subplots(figsize=figsize(width, ratio), **kwargs)
    for ax in ax_list:
        format_axes(ax)
    return FigureWrapper(fig), ax_list

def savefig(filename, fig=None, dpi=dpi, **kwargs):
    if fig is None: fig = plt.gcf()
    if (filename[-4:] in [".pgf", ".pdf", ".png"]):
        fig.savefig(filename, dpi=dpi, **kwargs)
    else:
        fig.savefig('{}.pgf'.format(filename), dpi=dpi, **kwargs)
        fig.savefig('{}.pdf'.format(filename), dpi=dpi, **kwargs)


### Reset Matplotlib rc params at end of script ###
# exit_register runs at the end of ipython %run or the end of the python interpreter
from IPython import get_ipython
ip = get_ipython()
if (ip == None):
    from atexit import register as exit_register
else:
    def exit_register(fun, *args, **kwargs):
        """ Decorator that registers at post_execute. After its execution it
        unregisters itself for subsequent runs. """
        def callback():
            fun()
            ip.events.unregister('post_execute', callback)
        ip.events.register('post_execute', callback)
@exit_register
def reset_rcparams():
    mpl.rcParams.update(mpl.rcParamsDefault)
    mpl.rcParams["text.latex.preamble"] = "\\usepackage{amsmath}\n\\usepackage{bm}"

    # Ensure IPython reloads the module
    import sys
    del sys.modules['pyutils']
    del sys.modules['pyutils.latexify']
