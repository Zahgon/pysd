"""
These are general utilities used by the builder.py, functions.py or the
model file. Vensim's function equivalents should not go here but in
functions.py
"""

import json
from datetime import datetime
from pathlib import Path
from chardet.universaldetector import UniversalDetector
from dataclasses import dataclass
from typing import Dict, Set

import progressbar
import numpy as np
import xarray as xr
import pandas as pd


def xrsplit(array):
    """
    Split an array to a list of all the components.

    Parameters
    ----------
    array: xarray.DataArray
        Array to split.

    Returns
    -------
    sp_list: list of xarray.DataArrays
        List of shape 0 xarray.DataArrays with coordinates.

    """
    pass


def get_current_computer_time():
    """
    Returns the current machine time. Needed to mock the machine time in
    the tests.

    Parameters
    ---------
    None

    Returns
    -------
    datetime.now(): datetime.datetime
        Current machine time.

    """
    pass


def get_return_elements(return_columns, namespace):
    """
    Takes a list of return elements formatted in vensim's format
    Varname[Sub1, SUb2]
    and returns first the model elements (in Python safe language)
    that need to be computed and collected, and secondly the addresses
    that each element in the return columns list translates to

    Parameters
    ----------
    return_columns: list of strings

    namespace: dict

    Returns
    -------
    capture_elements
    return_addresses

    """
    pass


def compute_shape(coords, reshape_len=None, py_name=""):
    """
    Computes the 'shape' of a coords dictionary.
    Function used to rearange data in xarrays and
    to compute the number of rows/columns to be read in a file.

    Parameters
    ----------
    coords: dict
      Ordered dictionary of the dimension names as a keys with their values.

    reshape_len: int (optional)
      Number of dimensions of the output shape.
      The shape will ony compute the corresponent table
      dimensions to read from Excel, then, the dimensions
      with length one will be ignored at first.
      Lately, it will complete with 1 on the left of the shape
      if the reshape_len value is bigger than the length of shape.
      Will raise a ValueError if we try to reshape to a reshape_len
      smaller than the initial shape.

    py_name: str
      Name to print if an error is raised.

    Returns
    -------
    shape: list
      Shape of the ordered dictionary or of the desired table or vector.

    """
    pass


def get_key_and_value_by_insensitive_key_or_value(key, dict):
    """
    Providing a key or value in a dictionary search for the real key and value
    in the dictionary ignoring case sensitivity.

    Parameters
    ----------
    key: str
        Key or value to look for in the dictionary.
    dict: dict
        Dictionary to search in.

    Returns
    -------
    real key, real value: (str, str) or (None, None)
        The real key and value that appear in the dictionary or a tuple
        of Nones if the input key is not in the dictionary.

    """
    pass


def rearrange(data, dims, coords):
    """
    Returns a xarray.DataArray object with the given coords and dims

    Parameters
    ---------
    data: float or xarray.DataArray
        The input data to rearrange.

    dims: list
        Ordered list of the dimensions.

    coords: dict
        Dictionary of the dimension names as a keys with their values.

    Returns
    -------
    xarray.DataArray

    """
    pass


def load_model_data(root, model_name):

    """
    Used for models split in several files.
    Loads subscripts and modules dictionaries

    Parameters
    ----------
    root: pathlib.Path
        Path to the model file.

    model_name: str
        Name of the model without file type extension (e.g. "my_model").

    Returns
    -------
    subscripts: dict
        Dictionary describing the possible dimensions of the stock's
        subscripts.

    modules: dict
        Dictionary containing view (module) names as keys and a list of the
        corresponding variables as values.

    """
    pass


def load_modules(module_name, module_content, work_dir, submodules):
    """
    Used to load model modules from the main model file, when
    split_views=True in the read_vensim function. This function is used
    to iterate over the different layers of the nested dictionary that
    describes which model variables belong to each module/submodule.

    Parameters
    ----------
    module_name: str
        Name of the module to load.

    module_content: dict or list
        Content of the module. If it's a dictionary, it means that the
        module has submodules, whereas if it is a list it means that that
        particular module/submodule is a final one.

    work_dir: pathlib.Path
        Path to the module file.

    submodules: list
        This list gets updated at every recursive iteration, and each element
        corresponds to the string representation of each module/submodule that
        is read.

    Returns
    -------
    str:
        String representations of the modules/submodules to execute in the main
        model file.

    """
    pass


def load_outputs(file_name, transpose=False, columns=None, encoding=None):
    """
    Load outputs file

    Parameters
    ----------
    file_name: str or pathlib.Path
        Output file to read. Must be csv or tab.

    transpose: bool (optional)
        If True reads transposed outputs file, i.e. one variable per row.
        Default is False.

    columns: list or None (optional)
        List of the column names to load. If None loads all the columns.
        Default is None.
        NOTE: if transpose=False, the loading will be faster as only
        selected columns will be loaded. If transpose=True the whole
        file must be read and it will be subselected later.

    encoding: str or None (optional)
        Encoding type to read output file. Needed if the file has special
        characters. Default is None.

    Returns
    -------
    pandas.DataFrame
        A pandas.DataFrame with the outputs values.

    """
    pass


def detect_encoding(filename):
    """
    Detects the encoding of a file.

    Parameters
    ----------
    filename: str
        Name of the file to detect the encoding.

    Returns
    -------
    encoding: str
        The encoding of the file.

    """
    pass


def print_objects_format(object_set, text):
    """
    Return a printable version of the variables in object_sect with the
    header given with text.
    """
    pass


@dataclass
class Dependencies():
    """
    Representation of variables dependencies.

    Parameters
    ----------
    c_vars: set
        Set of all selected model variables.
    d_deps: dict
        Dictionary of dependencies needed to run vars and modules.
    s_deps: set
        Set of stateful objects to update when integrating selected
        model variables.

    """
    c_vars: Set[str]
    d_deps: Dict[str, set]
    s_deps: Set[str]

    def __str__(self):
        text = print_objects_format(self.c_vars, "Selected variables")

        if self.d_deps["initial"]:
            text += print_objects_format(
                self.d_deps["initial"],
                "\nDependencies for initialization only")
        if self.d_deps["step"]:
            text += print_objects_format(
                self.d_deps["step"],
                "\nDependencies that may change over time")
        if self.d_deps["lookup"]:
            text += print_objects_format(
                self.d_deps["lookup"],
                "\nLookup table dependencies")

        text += print_objects_format(
            self.s_deps,
            "\nStateful objects integrated with the selected variables")

        return text


class ProgressBar:
    """
    Progress bar for integration
    """

    def __init__(self, max_value=None):

        self.max_value = max_value
        if self.max_value is None:
            return

        self.counter = 0

        self.bar = progressbar.ProgressBar(
            max_value=self.max_value,
            widgets=[
                progressbar.ETA(),
                " ",
                progressbar.Bar("#", "[", "]", "-"),
                progressbar.Percentage(),
            ],
        )

        self.bar.start()

    def update(self):
        """Update progress bar"""
        pass

    def finish(self):
        """Finish progress bar"""
        pass


class UniqueDims():
    """
    Helper class to create unique dimension names for data_vars with the
    same dimension name but different coords in xarray Datasets.
    """
    def __init__(self, original_dim_name):
        self.dim_name = original_dim_name
        self.dim_prefix = self.dim_name + "_#"
        self.unique_dims = []
        self.num = 1

    def name_new_dim(self, dim_name, coords):
        """
        Returns either a new name (original_dim_name + _# + num) if the coords
        list is not in unique_dims, or the preexisting dimension name if it is.
        Parameters
        ----------
        dim_name: str
            This argument is used to verify that we are passing the right
            dimension name to the class.
        coords: list
            List of coordinates of a dimension.

        Returns
        -------
        Updated name of the original dimension.
        """
        pass

    def is_new(self, coords):
        """
        Checks if coords is already in the unique_dims list or not.

        Parameters
        ----------
        coords: list
            List of coordinates of a dimension.

        Returns
        -------
        bool
        """
        pass
