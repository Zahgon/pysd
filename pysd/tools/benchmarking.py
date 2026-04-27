"""
Benchmarking tools for testing and comparing outputs between different files.
Some of these functions are also used for testing.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from pysd import read_vensim, read_xmile, load
from ..py_backend.utils import load_outputs, detect_encoding
from pysd.translators.vensim.vensim_utils import supported_extensions as\
    vensim_extensions
from pysd.translators.xmile.xmile_utils import supported_extensions as\
    xmile_extensions


def runner(model_file, canonical_file=None, transpose=False, data_files=None):
    """
    Translates and runs a model and returns its output and the
    canonical output.

    Parameters
    ----------
    model_file: str
        Name of the original model file. Must be '.mdl' or '.xmile'.

    canonical_file: str or None (optional)
        Canonical output file to read. If None, will search for 'output.csv'
        and 'output.tab' in the model directory. Default is None.

    transpose: bool (optional)
        If True reads transposed canonical file, i.e. one variable per row.
        Default is False.

    data_files: list (optional)
        List of the data files needed to run the model.

    Returns
    -------
    output, canon: (pandas.DataFrame, pandas.DataFrame)
        pandas.DataFrame of the model output and the canonical output.

    """
    pass


def assert_frames_close(actual, expected, assertion="raise",
                        verbose=False, precision=2, **kwargs):
    """
    Compare DataFrame items by column and
    raise AssertionError if any column is not equal.

    Ordering of columns is unimportant, items are compared only by label.
    NaN and infinite values are supported.

    Parameters
    ----------
    actual: pandas.DataFrame
        Actual value from the model output.

    expected: pandas.DataFrame
        Expected model output.

    assertion: str (optional)
        "raise" if an error should be raised when not able to assert
        that two frames are close. If "warning", it will show a warning
        message. If "return" it will return information. Default is "raise".

    verbose: bool (optional)
        If True, if any column is not close the actual and expected values
        will be printed in the error/warning message with the difference.
        Default is False.

    precision: int (optional)
        Precision to print the numerical values of assertion verbosed message.
        Default is 2.

    kwargs:
        Optional rtol and atol values for assert_allclose.

    Returns
    -------
    (cols, first_false_time, first_false_cols) or None: (set, float, set) or None
        If assertion is 'return', return the sets of the all columns that are
        different. The time when the first difference was found and the
        variables that what different at that time. If assertion is not
        'return' it returns None.

    Examples
    --------
    >>> assert_frames_close(
    ...     pd.DataFrame(100, index=range(5), columns=range(3)),
    ...     pd.DataFrame(100, index=range(5), columns=range(3)))

    >>> assert_frames_close(
    ...     pd.DataFrame(100, index=range(5), columns=range(3)),
    ...     pd.DataFrame(110, index=range(5), columns=range(3)),
    ...     rtol=.2)

    >>> assert_frames_close(
    ...     pd.DataFrame(100, index=range(5), columns=range(3)),
    ...     pd.DataFrame(150, index=range(5), columns=range(3)),
    ...     rtol=.2)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AssertionError:
    Following columns are not close:
    \t'0'

    >>> assert_frames_close(
    ...     pd.DataFrame(100, index=range(5), columns=range(3)),
    ...     pd.DataFrame(150, index=range(5), columns=range(3)),
    ...     verbose=True, rtol=.2)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AssertionError:
    Following columns are not close:
    \t'0'
    Column '0' is not close.
    Expected values:
    \t[150, 150, 150, 150, 150]
    Actual values:
    \t[100, 100, 100, 100, 100]
    Difference:
    \t[50, 50, 50, 50, 50]

    >>> assert_frames_close(
    ...     pd.DataFrame(100, index=range(5), columns=range(3)),
    ...     pd.DataFrame(150, index=range(5), columns=range(3)),
    ...     rtol=.2, assertion="warn")
    ...
    UserWarning:
    Following columns are not close:
    \t'0'

    References
    ----------
    Derived from:
        http://nbviewer.jupyter.org/gist/jiffyclub/ac2e7506428d5e1d587b

    """
    pass


def assert_allclose(x, y, rtol=1.e-5, atol=1.e-5):
    """
    Asserts if numeric values from two arrays are close.

    Parameters
    ----------
    x: ndarray
        Expected value.
    y: ndarray
        Actual value.
    rtol: float (optional)
        Relative tolerance on the error. Default is 1.e-5.
    atol: float (optional)
        Absolut tolerance on the error. Default is 1.e-5.

    Returns
    -------
    None

    """
    pass


def _remove_constant_nan(df):
    """
    Removes nana values in constant value columns produced by Vensim
    """
    pass
