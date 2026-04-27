"""
The provided functions have no direct analog in the standard Python data
analytics stack, or require information about the internal state of the
system beyond what is present in the function call. They are provided
in a structure that makes it easy for the model elements to call. The
functions may be similar to the original functions given by Vensim or
Stella, but sometimes the number or order of arguments may change.
"""
import warnings
from datetime import datetime

import numpy as np
import xarray as xr

from . import utils

SMALL_VENSIM = 1e-6  # What is considered zero according to Vensim Help


def ramp(time, slope, start, finish=None):
    """
    Implements vensim's and xmile's RAMP function.

    Parameters
    ----------
    time: pysd.py_backend.components.Time
        Model time object.
    slope: float or xarray.DataArray
        The slope of the ramp starting at zero at time start.
    start: float or xarray.DataArray
        Time at which the ramp begins.
    finish: float or xarray.DataArray or None (oprional)
        Time at which the ramp ends. If None the ramp will never end.
        Default is None.

    Returns
    -------
    float or xarray.DataArray:
        If prior to ramp start, returns zero.
        If after ramp ends, returns top of ramp.

    """
    pass


def step(time, value, tstep):
    """"
    Implements vensim's STEP function.

    Parameters
    ----------
    time: pysd.py_backend.components.Time
        Model time object.
    value: float or xarray.DataArray
        The height of the step.
    tstep: float or xarray.DataArray
        The time at and after which `result` equals `value`.

    Returns
    -------
    float or xarray.DataArray:
        - In range [-inf, tstep):
            returns 0
        - In range [tstep, +inf]:
            returns `value`
    """
    pass


def pulse(time, start, repeat_time=0, width=None, magnitude=None, end=None):
    """
    Implements Vensim's PULSE and PULSE TRAIN functions and Xmile's PULSE
    function.

    Parameters
    ----------
    time: pysd.py_backend.components.Time
        Model time object.
    start: float
        Starting time of the pulse.
    repeat_time: float (optional)
        Time interval of the pulse repetition. If 0 it will return a
        single pulse. Default is 0.
    width: float or None (optional)
        Duration of the pulse. If None only one-time_step pulse will be
        generated. Default is None.
    magnitude: float or None (optional)
        The magnitude of the pulse. If None it will return 1 when the
        pulse happens, similar to magnitude=time_step(). Default is None.
    end: float or None (optional)
        Final time of the pulse. If None there is no final time.
        Default is None.

    Returns
    -------
    float or xarray.DataArray:
        - In range [-inf, start):
            returns 0
        - In range [start + n*repeat_time, start + n*repeat_time + width):
            returns magnitude/time_step or 1
        - In range [start + n*repeat_time + width, start + (n+1)*repeat_time):
            returns 0

    """
    pass


def if_then_else(condition, val_if_true, val_if_false):
    """
    Implements Vensim's IF THEN ELSE function.
    https://www.vensim.com/documentation/20475.htm

    Parameters
    ----------
    condition: bool or xarray.DataArray of bools
    val_if_true: callable
        Value to evaluate and return when condition is true.
    val_if_false: callable
        Value to evaluate and return when condition is false.

    Returns
    -------
    float or xarray.DataArray:
        The value depending on the condition.

    """
    pass


def xidz(numerator, denominator, x):
    """
    Implements Vensim's XIDZ function.
    https://www.vensim.com/documentation/fn_xidz.htm

    This function executes a division, robust to denominator being zero.
    In the case of zero denominator, the final argument is returned.

    Parameters
    ----------
    numerator: float or xarray.DataArray
        Numerator of the operation.
    denominator: float or xarray.DataArray
        Denominator of the operation.
    x: float or xarray.DataArray
        The value to return if the denominator is zero.

    Returns
    -------
    float or xarray.DataArray:
        - numerator/denominator if denominator > small_vensim
        - value_if_denom_is_zero otherwise

    """
    pass


def zidz(numerator, denominator):
    """
    This function bypasses divide-by-zero errors,
    implementing Vensim's ZIDZ function.
    https://www.vensim.com/documentation/fn_zidz.htm

    Parameters
    ----------
    numerator: float or xarray.DataArray
        value to be divided
    denominator: float or xarray.DataArray
        value to devide by

    Returns
    -------
    float or xarray.DataArray:
        - numerator/denominator if denominator > small_vensim
        - 0 or 0s array otherwise

    """
    pass


def active_initial(stage, expr, init_val):
    """
    Implements vensim's ACTIVE INITIAL function

    Parameters
    ----------
    stage: str
        The stage of the model.
    expr: callable
        Running stage value
    init_val: float or xarray.DataArray
        Initialization stage value.

    Returns
    -------
    float or xarray.DataArray:
        - inti_val if stage='Initialization'
        - expr() otherwise
    """
    pass


def incomplete(*args):
    """
    Implements an incomplete functions.
    Prompts a RuntimeWarning.

    Parameters
    ----------
    *args: arguments

    Returns
    -------
    numpy.nan

    """
    pass


def not_implemented_function(*args):
    """
    Implements a not implemented functions.
    Raises a NotImplementedError if it is called.

    Parameters
    ----------
    *args: arguments
        The first argument must be the name of the function as str to
        properly print the error message.

    """
    raise NotImplementedError(f"Not implemented function '{args[0]}'")


def integer(x):
    """
    Implements Vensim's INTEGER function.

    Parameters
    ----------
    x: float or xarray.DataArray
        Input value.

    Returns
    -------
    integer: float or xarray.DataArray
        Returns integer part of x.

    """
    pass


def quantum(a, b):
    """
    Implements Vensim's QUANTUM function.

    Parameters
    ----------
    a: float or xarray.DataArray
        Input value.
    b: float or xarray.DataArray
        Input value.

    Returns
    -------
    quantum: float or xarray.DataArray
        If b > 0 returns b * integer(a/b). Otherwise, returns a.

    """
    pass


def modulo(x, m):
    """
    Implements Vensim's MODULO function.

    Parameters
    ----------
    x: float or xarray.DataArray
        Input value.
    m: float or xarray.DataArray
        Modulo to compute.

    Returns
    -------
    modulo: float or xarray.DataArray
        Returns x modulo m, if x is smaller than 0 the result is given
        in the range (-m, 0] as Vensim does. x - quantum(x, m)

    """
    pass


def sum(x, dim=None):
    """
    Implements Vensim's SUM function.

    Parameters
    ----------
    x: xarray.DataArray
        Input value.
    dim: list of strs (optional)
        Dimensions to apply the function over.
        If not given the function will be applied over all dimensions.

    Returns
    -------
    sum: xarray.DataArray or float
        The result of the sum operation in the given dimensions.

    """
    pass


def prod(x, dim=None):
    """
    Implements Vensim's PROD function.

    Parameters
    ----------
    x: xarray.DataArray
        Input value.
    dim: list of strs (optional)
        Dimensions to apply the function over.
        If not given the function will be applied over all dimensions.

    Returns
    -------
    prod: xarray.DataArray or float
        The result of the product operation in the given dimensions.

    """
    pass


def vmin(x, dim=None):
    """
    Implements Vensim's Vmin function.

    Parameters
    ----------
    x: xarray.DataArray
        Input value.
    dim: list of strs (optional)
        Dimensions to apply the function over.
        If not given the function will be applied over all dimensions.

    Returns
    -------
    vmin: xarray.DataArray or float
        The result of the minimum value over the given dimensions.

    """
    pass


def vmax(x, dim=None):
    """
    Implements Vensim's VMAX function.

    Parameters
    ----------
    x: xarray.DataArray
        Input value.
    dim: list of strs (optional)
        Dimensions to apply the function over.
        If not given the function will be applied over all dimensions.

    Returns
    -------
    vmax: xarray.DataArray or float
        The result of the maximum value over the dimensions.

    """
    pass


def invert_matrix(mat):
    """
    Implements Vensim's INVERT MATRIX function.

    Invert the matrix defined by the last two dimensions of xarray.DataArray.

    Parameters
    -----------
    mat: xarray.DataArray
        The matrix to invert.

    Returns
    -------
    mat1: xarray.DataArray
        Inverted matrix.

    """
    pass


def vector_select(selection_array, expression_array, dim,
                  missing_vals, numerical_action, error_action):
    """
    Implements Vensim's VECTOR SELECT function.
    http://vensim.com/documentation/fn_vector_select.html

    Parameters
    ----------
    selection_array: xr.DataArray
        This specifies a selection array with a mixture of zeroes and
        non-zero values.
    expression_array: xarray.DataArray
        This is the expression that elements are being selected from
        based on the selection array.
    dim: list of strs
        Dimensions to apply the function over.
    missing_vals: float
        The value to use in the case where there are only zeroes in the
        selection array.
    numerical_action: int
        The action to take:
            - 0 It will calculate the weighted sum.
            - 1 When values in the selection array are non-zero, this
              will calculate the product of the
              selection_array * expression_array.
            - 2 The weighted minimum, for non zero values of the
              selection array, this is minimum of
              selection_array * expression_array.
            - 3 The weighted maximum, for non zero values of the
              selection array, this is maximum of
              selection_array * expression_array.
            - 4 For non zero values of the selection array, this is
              the average of selection_array * expression_array.
            - 5 When values in the selection array are non-zero,
              this will calculate the product of the
              expression_array ^ selection_array.
            - 6 When values in the selection array are non-zero,
              this will calculate the sum of the expression_array.
              The same as the SUM function for non-zero values in
              the selection array.
            - 7 When values in the selection array are non-zero,
              this will calculate the product of the expression_array.
              The same as the PROD function for non-zero values in
              the selection array.
            - 8 The unweighted minimum, for non zero values of the
              selection array, this is minimum of the expression_array.
              The same as the VMIN function for non-zero values in
              the selection array.
            - 9 The unweighted maximum, for non zero values of the
              selection array, this is maximum of expression_array.
              The same as the VMAX function for non-zero values in
              the selection array.
            - 10 For non zero values of the selection array,
              this is the average of expression_array.
    error_action: int
        Indicates how to treat too many or too few entries in the selection:
            - 0 No error is raised.
            - 1 Raise a floating point error is selection array only
              contains zeros.
            - 2 Raise an error if the selection array contains more
              than one non-zero value.
            - 3 Raise an error if all elements in selection array are
              zero, or more than one element is non-zero
              (this is a combination of error_action = 1 and error_action = 2).

    Returns
    -------
    result: xarray.DataArray or float
        The output of the numerical action.

    """
    pass


def vector_sort_order(vector, direction):
    """
    Implements Vensim's VECTOR SORT ORDER function. Sorting is done on
    the complete vector relative to the last subscript.
    https://www.vensim.com/documentation/fn_vector_sort_order.html

    Parameters
    -----------
    vector: xarray.DataArray
        The vector to sort.
    direction: float
        The direction to sort the vector. If direction > 0 it will sort
        the vector entries from smallest to biggest, otherwise from
        biggest to smallest.

    Returns
    -------
    vector_sorted: xarray.DataArray
        The sorted vector.

    """
    pass


def vector_reorder(vector, svector):
    """
    Implements Vensim's VECTOR REORDER function. Reordering is done on
    the complete vector relative to the last subscript.
    https://www.vensim.com/documentation/fn_vector_reorder.html

    Parameters
    -----------
    vector: xarray.DataArray
        The vector to sort.
    svector: xarray.DataArray
        The vector to specify the order.

    Returns
    -------
    vector_sorted: xarray.DataArray
        The sorted vector.

    """
    pass


def vector_rank(vector, direction):
    """
    Implements Vensim's VECTOR RANK function. Ranking is done on the
    complete vector relative to the last subscript.
    https://www.vensim.com/documentation/fn_vector_rank.html

    Parameters
    -----------
    vector: xarray.DataArray
        The vector to sort.
    direction: float
        The direction to sort the vector. If direction > 1 it will rank
        the vector entries from smallest to biggest, otherwise from
        biggest to smallest.

    Returns
    -------
    vector_rank: xarray.DataArray
        The rank of the vector.

    """
    pass


def get_time_value(time, relativeto, offset, measure):
    """
    Implements Vensim's GET TIME VALUE function. Warning, not all the
    cases are implemented.
    https://www.vensim.com/documentation/fn_get_time_value.html

    Parameters
    ----------
    time: pysd.py_backend.components.Time
        Model time object.
    relativeto: int
        The time to take as a reference:
            - 0 for the current simulation time.
            - 1 for the initial simulation time.
            - 2 for the current computer clock time.
    offset: float or xarray.DataArray
        The difference in time, as measured in the units of Time for
        the  model, to move before computing the value. offset is
        ignored when relativeto is 2.
    measure: int
        The units or measure of time:
            - 0 units of Time in the model (only for relativeto 0 and 1)
            - 1 years since 1 BC (an integer, same as the normal calendar year)
            - 2 quarter of year (1-4)
            - 3 month of year (1-12)
            - 4 day of month (1-31)
            - 5 day of week (0-6 where 0 is Sunday)
            - 6 days since Jan 1., 1 BC (year 1 BC is treated as year 0)
            - 7 hour of day (0-23)
            - 8 minute of hour (0-59)
            - 9 second of minute (0-59.999999 â€“ not an integer)
            - 10 elapsed seconds modulo 500,000 (0-499,999)

    Returns
    -------
    time_value: float or int
        The resulting time value.

    """
    pass
