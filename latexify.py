import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

latex_width_pt = 455.244  # Get this from LaTeX using \the\textwidth
dpi = 500
axis_formatter = None

def update_width(width):
    ''' Update the latex page width (in pt), found using \the\textwidth. Default: 455.244
    Can also use 'r4', 'r4-single', and 'r4-double' for revtex4 sizes.'''
    global latex_width_pt
    if (width == 'r4'):
        latex_width_pt = 455.244
    elif (width == 'r4-single'):
        latex_width_pt = 246
    elif (width == 'r4-double'):
        latex_width_pt = 510
    elif (width == 'aip-single'):
        latex_width_pt = 242.64
    elif (width == 'aip-double'):
        latex_width_pt = 481.68
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

class Formatter(mpl.ticker.Formatter):
    def __init__(self, base_formatter):
        self.base_formatter = base_formatter
    def format_ticks(self, values):
        base_labels = self.base_formatter.format_ticks(values)
        return [axis_formatter(l) for l in base_labels]

class FigureWrapper():
    def __getattr__(self, attr):
        return getattr(self.fig, attr)
    def __init__(self, fig=None, *args, **kwargs):
        if (fig is None):
            fig = plt.Figure(*args, **kwargs)
        self.fig = fig
    def add_axes(self, *args, **kwargs):
        ax = self.fig.add_axes(*args, **kwargs)
        return AxesWrapper(ax)

class AxesWrapper():
    def __getattr__(self, attr):
        return getattr(self.ax, attr)
    def __init__(self, ax=None, *args, **kwargs):
        if (ax is None):
            ax = plt.Axes(*args, **kwargs)
        self.xformatted = False
        self.yformatted = False
        self.ax = ax
        self.format_axes()
    def semilogx(self):
        self.ax.semilogx()
        self.xformatted = False
        self.format_axes(which='x')
    def semilogy(self):
        self.ax.semilogy()
        self.yformatted = False
        self.format_axes(which='y')
    def format_axes(self, which='both'):
        if (axis_formatter is not None):
            if (which in ['x','both']) and (not self.xformatted):
                # if (self.ax._sharex is None):
                base_formatter = self.ax.xaxis.get_major_formatter()
                self.ax.xaxis.set_major_formatter(Formatter(base_formatter))
                self.xformatted = True
            if (which in ['y','both']) and (not self.yformatted):
                # if (self.ax._sharey is not None) and (self.ax._sharey.yformatted):
                base_formatter = self.ax.yaxis.get_major_formatter()
                self.ax.yaxis.set_major_formatter(Formatter(base_formatter))
                self.yformatted = True


### User functions ###
def figure(width, ratio=None, **kwargs):
    fig = plt.figure(figsize=figsize(width, ratio), **kwargs)
    return FigureWrapper(fig)

def subplots(width, ratio=None, **kwargs):
    fig, ax_list = plt.subplots(figsize=figsize(width, ratio), **kwargs)
    for i, ax in enumerate(ax_list):
        ax_list[i] = AxesWrapper(ax)
    return FigureWrapper(fig), ax_list

def savefig(filename, fig=None, dpi=dpi, **kwargs):
    if fig is None: fig = plt.gcf()
    if (filename[-4:] in [".pgf", ".pdf", ".png", ".eps", ".tif"]):
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
