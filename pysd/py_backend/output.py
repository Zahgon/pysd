"""
ModelOutput class is used to build different output objects based on
user input. For now, available output types are pandas DataFrame or
netCDF4 Dataset.
The OutputHandlerInterface class is an interface for the creation of handlers
for other output object types.
"""
import abc
import time as t

from csv import QUOTE_NONE
from pathlib import Path
from collections import defaultdict

import regex as re

import numpy as np
import xarray as xr
import pandas as pd

from pysd._version import __version__
from pysd.tools.ncfiles import NCFile

from . utils import xrsplit


class OutputHandlerInterface(metaclass=abc.ABCMeta):
    """
    Interface for the creation of different output handlers.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'initialize') and
                callable(subclass.initialize) and
                hasattr(subclass, 'update') and
                callable(subclass.update) and
                hasattr(subclass, 'postprocess') and
                callable(subclass.postprocess) and
                hasattr(subclass, 'add_run_elements') and
                callable(subclass.add_run_elements) or
                NotImplemented)

    @abc.abstractmethod
    def initialize(self, model):
        """
        Create the results object and its elements based on capture_elemetns.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, model):
        """
        Update the results object at each iteration at which resutls are
        stored.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def postprocess(self, **kwargs):
        """
        Perform different tasks at the time of returning the results object.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_run_elements(self, model):
        """
        Add elements with run cache to the results object.
        """
        raise NotImplementedError


class DatasetHandler(OutputHandlerInterface):
    """
    Manages simulation results stored as netCDF4 Dataset.
    """

    def __init__(self, out_file):
        self.out_file = out_file
        self.ds = None
        self.__step = 0
        self.nc = __import__("netCDF4")

    def initialize(self, model):
        """
        Creates a netCDF4 Dataset and adds model dimensions and
        variables present in the capture elements to it.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def update(self, model):
        """
        Writes values of cache step variables from the capture_elements
        list in the netCDF4 Dataset.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def __update_run_elements(self, model):
        """
        Writes values of cache run elements from the capture_elements
        set in the netCDF4 Dataset.
        Cache run elements do not have the time dimension.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def postprocess(self, **kwargs):
        """
        Closes netCDF4 Dataset.

        Returns
        -------
        None

        """
        pass

    def add_run_elements(self, model):
        """
        Adds constant elements to netCDF4 Dataset.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def __create_ds_vars(self, model, capture_elements, time_dim=True):
        """
        Create new variables in a netCDF4 Dataset from the capture_elements.
        Data is zlib compressed by default for netCDF4 1.6.0 and above.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object.
        capture_elements: list
            List of variable or parameter names to include as variables in the
            dataset.
        time_dim: bool
            Whether to add time as the first dimension for the variable.

        Returns
        -------
        None

        """
        pass


class DataFrameHandler(OutputHandlerInterface):
    """
    Manages simulation results stored as pandas DataFrame.
    """
    def __init__(self, out_file):
        self.out_file = out_file
        self.ds = None
        self.__step = 0

    def initialize(self, model):
        """
        Creates an empty dictionary to save the outputs.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def update(self, model):
        """
        Add new values to the data dictionary.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    def postprocess(self, **kwargs):
        """
        Convert the output dictionary to a pandas DataFrame and flatten
        xarrays if required.

        Returns
        -------
        ds: pandas.DataFrame
            Simulation results stored as a pandas DataFrame.

        """
        pass

    def add_run_elements(self, model):
        """
        Adds constant elements to the output data dictionary.

        Parameters
        ----------
        model: pysd.Model
            PySD Model object

        Returns
        -------
        None

        """
        pass

    @staticmethod
    def make_flat_df(df, return_addresses, flatten=False):
        """
        Takes a dataframe from the outputs of the integration processes,
        renames the columns as the given return_adresses and splits
        xarrays if needed.

        Parameters
        ----------
        df: pandas.DataFrame
            Dataframe to process.

        return_addresses: dict
            Keys will be column names of the resulting dataframe, and are what
            the user passed in as 'return_columns'. Values are a tuple:
            (py_name, {coords dictionary}) which tells us where to look for the
            value to put in that specific column.

        flatten: bool (optional)
                If True, once the output dataframe has been formatted will
                split the xarrays in new columns following vensim's naming
                to make a totally flat output. Default is False.

        Returns
        -------
        new_df: pandas.DataFrame
            Formatted dataframe.

        """
        pass

    @staticmethod
    def __add_flat(savedict, name, values):
        """
        Add float lists from a list of xarrays to a provided dictionary.

        Parameters
        ----------
        savedict: dict
            Dictionary to save the data on.

        name: str
            The base name of the variable to save the data.

        values: list
            List of xarrays to convert to split in floats.

        Returns
        -------
        None

        """
        pass


class ModelOutput():
    """
    Manages outputs from simulations. Handles different types of outputs
    by dispatchinging the tasks to adequate object handlers.

    Parameters
    ----------
    out_file: str or pathlib.Path
        Path to the file where the results will be written.

    """
    out_handlers = {
        "__default__": DataFrameHandler,
        ".csv": DataFrameHandler,
        ".tab": DataFrameHandler,
        ".nc": DatasetHandler,
    }

    def __init__(self, out_file=None):
        self.handler = ModelOutput.get_handler(out_file)

    @staticmethod
    def get_handler(out_file):
        pass

    def set_capture_elements(self, capture_elements):
        pass

    def initialize(self, model):
        """
        Delegating the creation of the results object and its elements
        to the appropriate handler.
        """
        pass

    def update(self, model):
        """
        Delegating the update of the results object and its elements
        to the appropriate handler.
        """
        pass

    def postprocess(self, **kwargs):
        """
        Delegating the postprocessing of the results object
        to the appropriate handler.
        """
        pass

    def add_run_elements(self, model):
        """
        Delegating the addition of results with run cache in the
        output object to the appropriate handler.
        """
        pass

    @staticmethod
    def collect(model, flatten_output=True):
        """
        Collect results after one or more simulation steps, and save to
        desired output format (DataFrame, csv, tab or netCDF).

        Parameters
        ----------
        model: pysd.py_backend.model.Model
            PySD Model object.

        flatten_output: bool (optional)
            If True, once the output dataframe has been formatted will
            split the xarrays in new columns following Vensim's naming
            to make a totally flat output. Default is True.
            This argument will be ignored when passing a netCDF4 file
            path in the output_file argument.

        """
        pass
