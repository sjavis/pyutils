import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

latex_width_pt = 455.244  # Get this from LaTeX using \the\textwidth

def update_width(width):
    ''' Update the latex page width, found using \the\textwidth. Default: 455.244'''
    global latex_width_pt
    latex_width_pt = width

def figsize(scale, ratio=None):
    inches_per_pt = 1.0/72.27                           # Convert pt to inch
    if ratio is None: ratio = 2.0/(np.sqrt(5.0)-1.0)    # Aesthetic ratio
    fig_width = latex_width_pt*inches_per_pt*scale      # width in inches
    fig_height = fig_width/ratio                        # height in inches
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


### User functions ###
def figure(width, ratio=None, **kwargs):
    fig = plt.figure(figsize=figsize(width, ratio), **kwargs)
    return fig

def subplots(width, ratio=None, **kwargs):
    fig, ax = plt.subplots(figsize=figsize(width, ratio), **kwargs)
    return fig, ax

def savefig(filename, fig=None, **kwargs):
    if fig is None: fig = plt.gcf()
    fig.savefig('{}.pgf'.format(filename), **kwargs)
    fig.savefig('{}.pdf'.format(filename), **kwargs)


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

    # Ensure IPython reloads the module
    import sys
    del sys.modules['pyutils']
    del sys.modules['pyutils.latexify']
