"""
The provided allocation functions have no direct analog in the standard
Python data analytics stack. They are provided in a structure that makes
it easy for the model elements to call. The functions may be similar to
the original functions given by Vensim, but sometimes the number or
order of arguments may change. The allocation functions may call a
protected function or class method thatintegrates the algorithm to
compute the allocation. The algorithms are briefly explained in these
functions docstring.

Note
----
The Allocation functions basis is explained in the Vensim documentation.
https://www.vensim.com/documentation/allocation_overview.html

Warning
-------
Some allocation function's results may differ from the result given by
Vensim as optimization functions are used to solve the allocation
problems. Those algorithms may not work in the same way or may
have differences in the numerical error propagation.

"""
import itertools
from math import erfc

import numpy as np
import xarray as xr
from scipy.optimize import least_squares
import portion as p


class Priorities:
    @classmethod
    def get_functions(cls, q0, pp, kind):
        """
        Get priority functions based on the demand/supply and priority profile.

        Parameters
        ----------
        q0: numpy.array
            values of maximum demand or supply of each component.
            Its shape should be (n,)
        pp: numpy.array
            pp values array. Its shape should be (n, m).
        kind: str ("demand" or "supply")
            The kind of priority "demand" or "supply".

        Returns
        -------
        functions: list of functions
            List of allocation supply or demand function for each element.

        full_allocation: function
            Full allocation function. It is the result function of
            addying all the functions.

        def_intervals: list of tuples
            List of (supply interval, priority interval, mean priority)
            where the full_allocation function is extrictly monotonous
            (injective). Givin a supply value, this is used to compute
            the limits and starting point of the optimization problem.

        """
        pass

    @classmethod
    def get_function_demand(cls, q0, pp):
        """
        Get priority functions for demand based on the priority profile.

        Parameters
        ----------
        q0: float [0, +np.inf)
            The demand of the target.
        pp: numpy.array
            pp values array.

        Returns
        -------
        priority_func: function
            Priority function.
        interval: portion.interval
            The interval where the priority function is strictly monotonous.

        """
        pass

    @classmethod
    def get_function_supply(cls, q0, pp):
        """
        Get priority functions for supply based on the priority profile.

        Parameters
        ----------
        q0: float [0, +np.inf)
            The supply of the producer.
        pp: numpy.array
            pp values array.

        Returns
        -------
        priority_func: function
            Priority function.
        interval: portion.interval
            The interval where the priority function is strictly monotonous.

        """
        # TODO: This function should be similar to the demand function
        # it is neccessary for the many-to-many allocation given by
        # the set FIND MARKET PLACE, DEMAND AT PRICE, SUPPLY AT PRICE
        raise NotImplementedError("get_function_supply is not implemented.")

    @staticmethod
    def fixed_quantity(q0, ppriority, pwidth, pextra):
        raise NotImplementedError(
            "fixed_quantity priority profile is not implemented.")

    @staticmethod
    def rectangular(q0, ppriority, pwidth, pextra):
        """
        Demand curve for rectangular shape.
        The supply curve will be shaped as the integral of a rectangle.

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve.
        pwidth: float
            Determines the speed with which the curve goes from 0 to
            the specified quantity.
        pextra: float
            Ignore.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        pass

    @staticmethod
    def triangular(q0, ppriority, pwidth, pextra):
        """
        Demand curve for triangular shape.
        The supply curve will be shaped as the integral of a triangle.

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve.
        pwidth: float
            Determines the speed with which the curve goes from 0 to the
            specified quantity.
        pextra: float
            Ignore.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        pass

    @staticmethod
    def normal(q0, ppriority, pwidth, pextra):
        """
        Demand curve for normal shape.
        The supply curve will be shaped as the integral of a normal
        distribution.

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve (the mean of the
            underlying distribution).
        pwidth: float
            Standard deviation of the underlying distribution.
        pextra: float
            Ignore.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        pass

    @staticmethod
    def exponential(q0, ppriority, pwidth, pextra):
        """
        Demand curve for exponential shape
        The supply curve will be shaped as the integral of an
        exponential distribution that is symmetric around its mean
        (0.5*exp(-ABS(x-ppriority)/pwidth) on -âˆž to âˆž).

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve (the mean of the
            underlying distribution).
        pwidth: float
            Multiplier on x in the underlying distribution.
        pextra: float
            Ignore.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        pass

    @staticmethod
    def constant_elasticity_demand(q0, ppriority, pwidth, pextra):
        """
        Demand constant elasticity curve.
        The curve will be a constant elasticity curve.

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve (the mean of the
            underlying distribution).
        pwidth: float
            Standard deviation of the underlying distribution.
        pextra: positive float
            Elasticity exponent.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        raise NotImplementedError(
            "Some results for Vensim showed some bugs when using this "
            "priority curve. Therefore, the curve is not implemented in "
            "PySD as it cannot be properly tested."
        )

    @staticmethod
    def constant_elasticity_supply(ppriority, pwidth,
                                   pextra):   # pragma: no cover
        """
        Supply constant elasticity curve.
        The curve will be a constant elasticity curve.

        Parameters
        ----------
        q0: float
            The total demand/supply of the element.
        ppriority: float
            Specifies the midpoint of the curve (the mean of the
            underlying distribution).
        pwidth: float
            Standard deviation of the underlying distribution.
        pextra: positive float
            Elasticity exponent.

        Returns
        -------
        priority_func: function
            The priority function.

        """
        raise NotImplementedError(
            "Some results for Vensim showed some bugs when using this "
            "priority curve. Therefore, the curve is not implemented in "
            "PySD as it cannot be properly tested."
        )


def _allocate_available_1d(request, pp, avail):
    """
    This function implements the algorithm for allocate_available
    to be passed for 1d numpy.arrays. The algorithm works as follows:

    0. If supply > sum(request): return request. In the same way,
       if supply = 0: return request*0
    1. Based on the priority profiles and demands, the priority profiles
       are computed. This profiles are returned with the interval where
       each of them is strictly monotonous (or injective).
    2. Using the intervals of injectivity the initial guess is
       selected depending on the available supply.
    3. The initial guess and injectivity interval are used to compute
       the value where the sum of all priority functions is equal to
       the avilable supply. This porcess is done using a least_squares
       optimization function.
    4. The output from the previous step is used to compute the supply
       to each target.

    Parameters
    ----------
    request: numpy.ndarray (1D)
        The request by target. Values must be non-negative.
    pp: numpy.ndarray (2D)
        The priority profiles of each target.
    avail: float
        The available supply. Must be non-negative.

    Returns
    -------
    out: numpy.ndarray (1D)
        The distribution of the supply.

    """
    pass


def allocate_available(request, pp, avail):
    """
    Implements Vensim's ALLOCATE AVAILABLE function.
    https://www.vensim.com/documentation/fn_allocate_available.html

    Parameters
    -----------
    request: xarray.DataArray
        Request of each target. Its shape should be the one of the
        expected output of the function, having the allocation dimension
        in the last position.
    pp: xarray.DataArray
        Priority of each target. Its shape should be the same as
        request with an extra dimension for the priority profiles
        in the last position. See Vensim's documentation for more
        information https://www.vensim.com/documentation/24335.html
    avail: float or xarray.DataArray
        The total supply available to fulfill all requests. If the
        supply exceeds total requests, all requests are filled, but
        none are overfilled. If you wish to conserve material you must
        compute supply minus total allocations explicitly. Its shape,
        should be the same of request without the last dimension.

    Returns
    -------
    out: xarray.DataArray
        The distribution of the supply.

    Warning
    -------
    This function uses an optimization method for resolution and the
    given solution could differ from the one from Vensim. Particularly,
    when close to the boundaries of the defined priority profiles.

    """
    pass


def _allocate_by_priority_1d(request, priority, width, supply):
    """
    This function implements the algorithm for allocate_by_priority
    to be passed for 1d numpy.arrays. The algorithm works as follows:

    0. If supply > sum(request): return request.
    1. Order the request and priorities from bigger to lower priorities.
    2. Compute the 'distances' between the target, the 'distance' is
       defined as the difference between priorities divided by width
       multiplied by the target request. If the difference in priorities
       over width is bigger than 1, set it to 1, having the distance
       equal to the request. For example, priorities = [10, 9, 7, 2],
       request = [3, 6, 2.5, 2] and width = 3 will have the following
       'distances' vector, distance = [(10-9)/3*3, (9-7)/3*6, 1*2.5]
       = [1, 4, 2.5]
    3. The supply is assigned with linear functions. The fraction
       (or slope) of supply that a target receives is its total request
       divided by the request of all the targets that are receiving
       supply at that point.
    4. The supply is assigned from bigger to lower priority. Starts
       assigning the supply to the first target, when it reaches the
       quantity of the 'distance,' to the second target, the second
       target will start receiving its supply. When the second target
       receives its 'distance' to the third target, the third target
       will start receiving supply and so on.
    5. Each time a target reaches its request or a new target starts
       receiving supply the slope of each target is computed again.
    6. It finishes when all the supply is distributed between targets

    Parameters
    ----------
    request: numpy.ndarray (1D)
        The request by target. Values must be non-negative.
    priority: numpy.ndarray (1D)
        The priority of each target.
    width: float
        The width between priorities. Must be positive.
    supply: float
        The available supply. Must be non-negative.

    Returns
    -------
    out: numpy.ndarray (1D)
        The distribution of the supply.

    """
    pass


def allocate_by_priority(request, priority, width, supply):
    """
    Implements Vensim's ALLOCATE BY PRIORITY function.
    https://www.vensim.com/documentation/fn_allocate_by_priority.html

    Parameters
    -----------
    request: xarray.DataArray
        Request of each target. Its shape should be the same as
        priority. width and supply must have the same shape except the
        last dimension.
    priority: xarray.DataArray
        Priority of each target. Its shape should be the same as
        request. width and supply must have the same shape except the
        last dimension.
    width: float or xarray.DataArray
        Specifies how big a gap in priority is required to have the
        allocation go first to higher priority with only leftovers going
        to lower priority. When the distance between any two priorities
        exceeds width and the higher priority does not receive its full
        request the lower priority will receive nothing. Its shape
        should be the same as supply.
    supply: float or xarray.DataArray
        The total supply available to fulfill all requests. If the
        supply exceeds total requests, all requests are filled, but
        none are overfilled.  If you wish to conserve material you must
        compute supply minus total allocations explicitly. Its shape
        should be the same as width.

    Returns
    -------
    out: xarray.DataArray
        The distribution of the supply.

    """
    pass
