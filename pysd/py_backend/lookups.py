import warnings

import pandas as pd
import numpy as np
import xarray as xr

from . import utils


class Lookups(object):
    def set_values(self, values):
        """Set new values from user input"""
        pass

    def __call__(self, x, final_subs=None):
        try:
            return self._call(self.data, x, final_subs)
        except (TypeError, KeyError):
            # this except catch the errors when a lookups has been
            # changed to a constant value by the user
            if final_subs and isinstance(self.data, xr.DataArray):
                # self.data is an array, reshape it
                outdata = xr.DataArray(np.nan, final_subs, list(final_subs))
                return xr.broadcast(outdata, self.data)[1]
            elif final_subs:
                # self.data is a float, create an array
                return xr.DataArray(self.data, final_subs, list(final_subs))
            else:
                return self.data

    def _call(self, data, x, final_subs=None):
        pass


class HardcodedLookups(Lookups):
    """Class for lookups defined in the file"""

    def __init__(self, x, y, coords, interp, final_coords, py_name):
        # TODO: avoid add and merge all declarations in one definition
        self.is_float = not bool(coords)
        self.py_name = py_name
        self.final_coords = final_coords
        self.values = [(x, y, coords)]
        self.interp = interp

    def add(self, x, y, coords):
        pass

    def initialize(self):
        """
        Initialize all elements and create the self.data xarray.DataArray
        """
        pass

    def _fill_missing(self, series,  data):
        """
        Fills missing values in lookups to have a common series.
        Mutates the values in data.

        Returns
        -------
        None

        """
        pass
