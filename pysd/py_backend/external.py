"""
These classes are a collection of the needed tools to read external data.
The External type objects created by these classes are initialized before
the Stateful objects by functions.Model.initialize.
"""

import re
import warnings

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

import numpy as np
import xarray as xr
import pandas as pd

from . import utils
from .data import Data
from .lookups import Lookups


_SPREADSHEET_EXTS = {'.xls', '.xlsx', '.xlsm', '.xlsb', '.odf', '.ods', '.odt'}


class Excels():
    """
    Class to save the read Excel files and thus avoid double reading
    """
    _Excels, _Excels_opyxl = {}, {}

    @classmethod
    def read(cls, file_name, tab):
        """
        Read the Excel file or return the previously read one
        """
        pass

    @classmethod
    def read_opyxl(cls, file_name):
        """
        Read the Excel file using OpenPyXL or return the previously read one
        """
        pass

    @classmethod
    def clean(cls):
        """
        Clean the dictionary of read files
        """
        pass


class External(object):
    """
    Main class of external objects

    Attributes
    ----------
    py_name: str
        The Python name of the object
    missing: str ("warning", "error", "ignore", "keep")
        What to do with missing values. If "warning" (default)
        shows a warning message and interpolates the values.
        If "raise" raises an error. If "ignore" interpolates
        the values without showing anything. If "keep" it will keep
        the missing values, this option may cause the integration to
        fail, but it may be used to check the quality of the data.
    file: str
        File name from which the data is read.
    tab: str
        Tab name from which the data is read. If file type is not a
        spreadsheet this will be used as a separator.

    """
    missing = "warning"

    def __init__(self, py_name):
        self.py_name = py_name
        self.file = None
        self.tab = None

    def __str__(self):
        return self.py_name

    def _get_data_from_file(self, rows, cols):
        """
        Function to read data from excel file using rows and columns

        Parameters
        ----------
        rows: list of len 2
            first row and last row+1 to be read, starting from 0
        cols:  list of len 2
            first col and last col+1 to be read, starting from 0

        Returns
        -------
        data: pandas.DataFrame, pandas.Series or float
            depending on the shape of the requested data

        """
        pass

    def _get_data_from_file_opyxl(self, cellname):
        """
        Function to read data from excel file using cell range name

        Parameters
        ----------
        cellname: str
            the cell range name

        Returns
        -------
        data: numpy.ndarray or float
            depending on the shape of the requested data
        shape: list
            The shape of the data in 2D.

        """
        pass

    def _get_series_data(self, series_across, series_row_or_col, cell, size):
        """
        Function thar reads series and data from excel file for
        DATA and LOOKUPS.

        Parameters
        ----------
        series_across: "row", "column" or "name"
            The way to read series file.
        series_row_or_col: int or str
            If series_across is "row" the row number where the series data is.
            If series_across is "column" the column name where the series
            data is.
            If series_across is "name" the cell range name where the series
            data is.
        cell:
            If series_across is not "name, the top left cell where the
            data table starts.
            Else the name of the cell range where the data is.
        size:
            The size of the 2nd dimension of the data.

        Returns
        -------
        series, data: ndarray (1D), ndarray(1D/2D)
            The values of the series and data.

        """
        pass

    def _resolve_file(self, root):
        """
        Resolve input file path. Joining the file with the root and
        checking if it exists.

        Parameters
        ----------
        root: pathlib.Path or str
            The root path to the model file.

        Returns
        -------
        None

        """
        pass

    def _initialize_data(self, element_type):
        """
        Initialize one element of DATA or LOOKUPS

        Parameters
        ----------
        element_type: str
            "lookup" for LOOKUPS, "data" for data.

        Returns
        -------
        data: xarray.DataArray
            Dataarray with the time or interpolation dimension
            as first dimension.

        """
        pass

    def _fill_missing(self, series, data):
        """
        Fills missing values in excel read data. Mutates the values in data.

        Parameters
        ----------
        series:
          the time series without missing values
        data:
          the data with missing values

        Returns
        -------
        None
        """
        pass

    def _interpolate_missing(self, x, xr, yr):
        """
        Interpolates a list of missing values from _fill_missing

        Parameters
        ----------
        x:
          list of missing values interpolate
        xr:
          non-missing x values
        yr:
          non-missing y values

        Returns
        -------
        y:
          Result after interpolating x with self.interp method

        """
        pass

    @property
    def _file_sheet(self):
        """
        Returns file and sheet name in a string
        """
        pass

    @staticmethod
    def _col_to_num(col):
        """
        Transforms the column name to int

        Parameters
        ----------
        col: str
          Column name

        Returns
        -------
        int
          Column number
        """
        pass

    def _split_excel_cell(self, cell):
        """
        Splits a cell value given in a string.
        Returns None for non-valid cell formats.

        Parameters
        ----------
        cell: str
          Cell like string, such as "A1", "b16", "AC19"...
          If it is not a cell like string will return None.

        Returns
        -------
        row number, column number: int, int
          If the cell input is valid. Both numbers are given in Python
          enumeration, i.e., first row and first column are 0.

        """
        pass

    @staticmethod
    def _reshape(data, dims):
        """
        Reshapes an pandas.DataFrame, pandas.Series, xarray.DataArray
        or np.ndarray in the given dimensions.

        Parameters
        ----------
        data: xarray.DataArray/numpy.ndarray
          Data to be reshaped
        dims: tuple
          The dimensions to reshape.

        Returns
        -------
        numpy.ndarray
          reshaped array
        """
        pass

    def _series_selector(self, x_row_or_col, cell):
        """
        Selects if a series data (DATA/LOOKUPS), should be read by columns,
        rows or cellrange name.
        Based on the input format of x_row_or_col and cell.
        The format of the 2 variables must be consistent.

        Parameters
        ----------
        x_row_or_col: str
          String of a number if series is given in a row, letter if series is
          given in a column or name if the series is given by cellrange name.
        cell: str
          Cell identificator, such as "A1", or name if the data is given
          by cellrange name.

        Returns
        -------
        series_across: str
          "row" if series is given in a row
          "column" if series is given in a column
          "name" if series and data are given by range name

        """
        pass


class ExtData(External, Data):
    """
    Class for Vensim GET XLS DATA/GET DIRECT DATA
    """

    def __init__(self, file_name, tab, time_row_or_col, cell,
                 interp, coords, root, final_coords, py_name):
        super().__init__(py_name)
        self.files = [file_name]
        self.tabs = [tab]
        self.time_row_or_cols = [time_row_or_col]
        self.cells = [cell]
        self.coordss = [coords]
        self.root = root
        self.final_coords = final_coords
        self.interp = interp or "interpolate"
        self.is_float = not bool(coords)

        # check if the interpolation method is valid
        if self.interp not in ["interpolate", "raw",
                               "look_forward", "hold_backward"]:
            raise ValueError(self.py_name + "\n"
                             + " The interpolation method (interp) must be "
                             + "'raw', 'interpolate', "
                             + "'look_forward' or 'hold_backward'")

    def add(self, file_name, tab, time_row_or_col, cell, interp, coords):
        """
        Add information to retrieve new dimension in an already declared object
        """
        pass

    def initialize(self):
        """
        Initialize all elements and create the self.data xarray.DataArray
        """
        pass


class ExtLookup(External, Lookups):
    """
    Class for Vensim GET XLS LOOKUPS/GET DIRECT LOOKUPS
    """

    def __init__(self, file_name, tab, x_row_or_col, cell, coords,
                 root, final_coords, py_name):
        super().__init__(py_name)
        self.files = [file_name]
        self.tabs = [tab]
        self.x_row_or_cols = [x_row_or_col]
        self.cells = [cell]
        self.coordss = [coords]
        self.root = root
        self.final_coords = final_coords
        self.interp = "interpolate"
        self.is_float = not bool(coords)

    def add(self, file_name, tab, x_row_or_col, cell, coords):
        """
        Add information to retrieve new dimension in an already declared object
        """
        pass

    def initialize(self):
        """
        Initialize all elements and create the self.data xarray.DataArray
        """
        pass


class ExtConstant(External):
    """
    Class for Vensim GET XLS CONSTANTS/GET DIRECT CONSTANTS
    """

    def __init__(self, file_name, tab, cell, coords,
                 root, final_coords, py_name):
        super().__init__(py_name)
        self.files = [file_name]
        self.tabs = [tab]
        self.transposes = [
            cell[-1] == '*' and np.prod(utils.compute_shape(coords)) > 1]
        self.cells = [cell.strip('*')]
        self.coordss = [coords]
        self.root = root
        self.final_coords = final_coords

    def add(self, file_name, tab, cell, coords):
        """
        Add information to retrieve new dimension in an already declared object
        """
        pass

    def initialize(self):
        """
        Initialize all elements and create the self.data xarray.DataArray
        """
        pass

    def _initialize(self):
        """
        Initialize one element
        """
        pass

    def _get_constant_data(self, data_across, cell, shape):
        """
        Function thar reads data from excel file for CONSTANT

        Parameters
        ----------
        data_across: "cell" or "name"
            The way to read data file.
        cell: int or str
            If data_across is "cell" the lefttop split cell value where
            the data is.
            If data_across is "name" the cell range name where the data is.
        shape: list
            The shape of the data in 2D.

        Returns
        -------
        data: float/ndarray(1D/2D)
            The values of the data.

        """
        pass

    def __call__(self):
        return self.data


class ExtSubscript(External):
    """
    Class for Vensim GET XLS SUBSCRIPT/GET DIRECT SUBSCRIPT
    """

    def __init__(self, file_name, tab, firstcell, lastcell, prefix, root):
        super().__init__("Hardcoded external subscript")
        self.file = file_name
        self.tab = tab
        self.prefix = prefix
        self._resolve_file(root=root)
        split = self._split_excel_cell(firstcell)
        if split:
            subs = self.get_subscripts_cell(*split, lastcell)
        else:
            subs = self.get_subscripts_name(firstcell)

        self.subscript = [
            self.prefix + str(d) for d in subs.flatten()
            if self._not_nan(d)
            ]

    def get_subscripts_cell(self, row_first, col_first, lastcell):
        """Get subscripts from common cell definition"""
        pass

    def get_subscripts_name(self, cellname):
        """Get subscripts from cell range name definition"""
        pass

    @staticmethod
    def _not_nan(value):
        """Check if a value is not nan"""
        pass
