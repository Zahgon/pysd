import warnings
import re
import random
from pathlib import Path

import numpy as np
import xarray as xr
import pandas as pd

from .utils import load_outputs


class Columns():
    """
    Class to save the read columns in data files
    """
    _files = {}

    @classmethod
    def read(cls, file_name, encoding=None):
        """
        Read the columns from the data file or return the previously read ones
        """
        pass

    @classmethod
    def read_file(cls, file_name, encoding=None):
        """
        Get the columns from an output csv or tab file.

        Parameters
        ----------
        file_name: str
            Output file to read. Must be csv or tab.

        encoding: str or None (optional)
            Encoding type to read output file. Needed if the file has special
            characters. Default is None.

        Returns
        -------
        out, transposed: list, bool
            The list of the columns in the output file and a boolean flag
            to indicate if the output file is transposed.

        """
        pass

    @classmethod
    def read_line(cls, file_name, encoding=None):
        """
        Read the firts row and return a set of it.
        """
        pass

    @classmethod
    def read_col(cls, file_name, encoding=None):
        """
        Read the firts column and return a it.
        """
        pass

    @classmethod
    def get_columns(cls, file_name, vars=None, encoding=None):
        """
        Get columns names from a tab or csv file and return those that
        match with the given ones.

        Parameters
        ----------
        file_name: str
            Output file to read. Must be csv or tab.

        vars: list or None (optional)
            List of var names to find in the file. If None all variables
            will be returned. Default is None.

        encoding: str or None (optional)
            Encoding type to read output file. Needed if the file has special
            characters. Default is None.

        Return
        ------
        columns, transpose: set, bool
            The set of columns as they are named in the input file and a
            boolean flag to indicate if the input file is transposed or
            not.

        """
        pass

    @classmethod
    def clean(cls):
        """
        Clean the dictionary of read files
        """
        pass


class Data(object):
    # TODO add __init__ and use this class for used input pandas.Series
    # as Data
    # def __init__(self, data, coords, interp="interpolate"):

    def set_values(self, values):
        """Set new values from user input"""
        pass

    def __call__(self, time):
        try:
            if time in self.data['time'].values:
                outdata = self.data.sel(time=time)
            elif self.interp == "raw":
                return self.nan
            elif time > self.data['time'].values[-1]:
                warnings.warn(
                    self.py_name + "\n"
                    + "extrapolating data above the maximum value of the time")
                outdata = self.data[-1]
            elif time < self.data['time'].values[0]:
                warnings.warn(
                    self.py_name + "\n"
                    + "extrapolating data below the minimum value of the time")
                outdata = self.data[0]
            elif self.interp == "interpolate":
                outdata = self.data.interp(time=time)
            elif self.interp == 'look_forward':
                outdata = self.data.sel(time=time, method="backfill")
            elif self.interp == 'hold_backward':
                outdata = self.data.sel(time=time, method="pad")

            if self.is_float:
                # if data has no-coords return a float
                return float(outdata)
            else:
                # Remove time coord from the DataArray
                return outdata.reset_coords('time', drop=True)
        except (TypeError, KeyError):
            if self.data is None:
                raise ValueError(
                    self.py_name + "\n"
                    "Trying to interpolate data variable before loading"
                    " the data...")

            # this except catch the errors when a data has been
            # changed to a constant value by the user
            return self.data
        except Exception as err:
            raise err


class TabData(Data):
    """
    Data from tabular file tab/csv, it could be from Vensim output.
    """
    def __init__(self, real_name, py_name, coords, interp="interpolate"):
        self.real_name = real_name
        self.py_name = py_name
        self.coords = coords
        self.final_coords = coords
        self.interp = interp.replace(" ", "_") if interp else None
        self.is_float = not bool(coords)
        self.data = None

        if self.interp not in ["interpolate", "raw",
                               "look_forward", "hold_backward"]:
            raise ValueError(self.py_name + "\n"
                             + "The interpolation method (interp) must be "
                             + "'raw', 'interpolate', "
                             + "'look_forward' or 'hold_backward'")

    def load_data(self, file_names, encoding=None):
        """
        Load data values from files.

        Parameters
        ----------
        file_names: list or str or pathlib.Path
            Name of the files to search the variable in.
        encoding: list or str or None (optional)
            Encoding to be used by the data readers. If a list is given,
            then file_names should be a list of the same lenght. If
            None or a string is given, this value will be used for all
            of them. See documentation from pandas.read_table for
            further information. Default is None.

        Returns
        -------
        out: xarray.DataArray
            Resulting data array with the time in the first dimension.

        """
        pass

    def _load_data(self, file_name, encoding):
        """
        Load data values from output

        Parameters
        ----------
        file_name: pathlib.Path
            Name of the file to search the variable in.

        Returns
        -------
        out: xarray.DataArray or None
            Resulting data array with the time in the first dimension.

        """
        pass
