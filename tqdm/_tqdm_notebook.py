"""
IPython/Jupyter Notebook progressbar decorator for iterators.
Includes a default (x)range iterator printing to stderr.

Usage:
  >>> from tqdm_notebook import tnrange[, tqdm_notebook]
  >>> for i in tnrange(10): #same as: for i in tqdm_notebook(xrange(10))
  ...     ...
"""
# future division is important to divide integers and get as
# a result precise floating numbers (instead of truncated int)
from __future__ import division, absolute_import
# import compatibility functions and utilities
import sys
from ._utils import _range

# import IPython/Jupyter base widget and display utilities
try:  # pragma: no cover
    # For IPython 4.x using ipywidgets
    from ipywidgets import IntProgress, HBox, HTML
except ImportError:  # pragma: no cover
    try:  # pragma: no cover
        # For IPython 3.x
        from IPython.html.widgets import IntProgress, HBox, HTML
    except ImportError:  # pragma: no cover
        try:  # pragma: no cover
            # For IPython 2.x
            from IPython.html.widgets import IntProgressWidget as IntProgress
            from IPython.html.widgets import ContainerWidget as HBox
            from IPython.html.widgets import HTML
        except ImportError:  # pragma: no cover
            pass
try:  # pragma: no cover
    from IPython.display import display  # , clear_output
except ImportError:  # pragma: no cover
    pass

# HTML encoding
try:  # pragma: no cover
    from html import escape  # python 3.x
except ImportError:  # pragma: no cover
    from cgi import escape  # python 2.x

# to inherit from the tqdm class
from ._tqdm import tqdm, format_meter, StatusPrinter


__author__ = {"github.com/": ["lrq3000", "casperdcl"]}
__all__ = ['tqdm_notebook', 'tnrange']


def NotebookPrinter(file, total=None, desc=None):  # pragma: no cover
    """
    Manage the printing of an IPython/Jupyter Notebook progress bar widget.
    """
    # Fallback to text bar if there's no total
    if not total:
        return StatusPrinter(file)

    fp = file
    if not getattr(fp, 'flush', False):  # pragma: no cover
        fp.flush = lambda: None

    # Prepare IPython progress bar
    pbar = IntProgress(min=0, max=total)
    if desc:
        pbar.description = desc
    # Prepare status text
    ptext = HTML()
    # Only way to place text to the right of the bar is to use a container
    container = HBox(children=[pbar, ptext])
    display(container)

    def print_status(s='', close=False):
        # Clear previous output (really necessary?)
        # clear_output(wait=1)

        # Get current iteration value from format_meter string
        n = None
        if s:
            npos = s.find(r'/|/')  # because we use bar_format=r'{n}|...'
            # Check that n can be found in s (else n > total)
            if npos >= 0:
                n = int(s[:npos])  # get n from string
                s = s[npos+3:]  # remove from string

                # Update bar with current n value
                if n is not None:
                    pbar.value = n

        # Print stats
        s = s.replace('||', '')  # remove inesthetical pipes
        s = escape(s)  # html escape special characters (like '?')
        ptext.value = s

        # Special signal to close the bar
        if close:
            container.visible = False

    return print_status


class tqdm_notebook(tqdm):  # pragma: no cover
    """
    Experimental IPython/Jupyter Notebook widget using tqdm!
    """
    def __init__(self, *args, **kwargs):

        # Setup default output
        if not kwargs.get('file', None) or kwargs['file'] == sys.stderr:
            kwargs['file'] = sys.stdout  # avoid the red block in IPython

        # Remove the bar from the printed string, only print stats
        if not kwargs.get('bar_format', None):
            kwargs['bar_format'] = r'{n}/|/{l_bar}{r_bar}'

        super(tqdm_notebook, self).__init__(*args, **kwargs)

        # Delete the text progress bar display
        self.sp('')
        # Replace with IPython progress bar display
        self.sp_nb = NotebookPrinter(self.fp, self.total, self.desc)
        self.sp = self.sprinter
        self.desc = None  # trick to place description before the bar

        # Print initial bar state
        if not self.disable:
            self.sp(format_meter(self.n, self.total, 0,
                    (self.dynamic_ncols(self.file) if self.dynamic_ncols
                     else self.ncols),
                    self.desc, self.ascii, self.unit, self.unit_scale, None,
                    self.bar_format))

    def sprinter(self, s=''):
        self.sp_nb(s)

    def close(self, *args, **kwargs):
        super(tqdm_notebook, self).close(*args, **kwargs)
        if not self.leave:
            self.sp_nb(s='', close=True)


def tnrange(*args, **kwargs):  # pragma: no cover
    """
    A shortcut for tqdm_notebook(xrange(*args), **kwargs).
    On Python3+ range is used instead of xrange.
    """
    return tqdm_notebook(_range(*args), **kwargs)
