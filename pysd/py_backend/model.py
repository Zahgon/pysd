"""
Macro and Model classes are the main classes for loading and interacting
with a PySD model. Model class allows loading and running a PySD model.
Several methods and propierties are inherited from Macro class, which
allows integrating a model or a Macro expression (set of functions in
a separate file).
"""
import time
import warnings
import inspect
import pickle
from pathlib import Path
from copy import deepcopy
from typing import Union

import numpy as np
import xarray as xr
import pandas as pd

from pysd._version import __version__

from . import utils
from .statefuls import DynamicStateful, Stateful
from .external import External, Excels, ExtLookup, ExtData

from .cache import Cache, constant_cache
from .data import TabData
from .lookups import HardcodedLookups
from .components import Components, Time
from .output import ModelOutput


class Macro(DynamicStateful):
    """
    The Macro class implements a stateful representation of the system,
    and contains the majority of methods for accessing and modifying
    components.

    When the instance in question also serves as the root model object
    (as opposed to a macro or submodel within another model) it will have
    added methods to facilitate execution.

    The Macro object will be created with components drawn from a
    translated Python model file.

    Parameters
    ----------
    py_model_file: str or pathlib.Path
        Filename of a model or macro which has already been converted
        into a Python format.
    params: dict or None (optional)
        Dictionary of the macro parameters. Default is None.
    return_func: str or None (optional)
        The name of the function to return from the macro. Default is None.
    time: components.Time or None (optional)
        Time object for integration. If None a new time object will
        be generated (for models), if passed the time object will be
        used (for macros). Default is None.
    time_initialization: callable or None
        Time to set at the begginning of the Macro. Default is None.
    data_files: dict or list or str or None
        The dictionary with keys the name of file and variables to
        load the data from. Or the list of names or name of the file
        to search the data in. Only works for TabData type object
        and it is neccessary to provide it. Default is None.
    py_name: str or None
        The name of the Macro object. Default is None.

    See also
    --------
    :class:`pysd.py_backend.model.Model`

    """
    def __init__(self, py_model_file, params=None, return_func=None,
                 time=None, time_initialization=None, data_files=None,
                 data_files_encoding=None, py_name=None):
        super().__init__()
        self.time = time
        self.time_initialization = time_initialization
        # Initialize the cache object
        self.cache = Cache()
        # Python name of the object (for Macros)
        self.py_name = py_name
        # Booleans to avoid loading again external data or lookups
        self.external_loaded = False
        self.lookups_loaded = False
        # Functions with constant cache
        self._constant_funcs = set()
        # Attributes that are set later
        self.stateful_initial_dependencies = None
        self.initialize_order = None
        self.cache_type = None
        self._components_setter_tracker = {}
        # Load model/macro from file and save in components
        self.components = Components(str(py_model_file), self.set_components)

        if __version__.split(".")[0]\
           != self.get_pysd_compiler_version().split(".")[0]:
            raise ImportError(
                "\n\nNot able to import the model. "
                + "The model was translated with a "
                + "not compatible version of PySD:"
                + "\n\tPySD " + self.get_pysd_compiler_version()
                + "\n\nThe current version of PySd is:"
                + "\n\tPySD " + __version__ + "\n\n"
                + "Please translate again the model with the function"
                + " read_vensim or read_xmile.")

        # Assing some protected attributes for easier access
        self._namespace = self.components._components.component.namespace
        self._dependencies =\
            self.components._components.component.dependencies.copy()
        self._subscript_dict = getattr(
            self.components._components, "_subscript_dict", {})
        self._modules = getattr(
            self.components._components, "_modules", {})

        self._doc = self._build_doc()

        if params is not None:
            # add params to namespace
            self._namespace.update(self.components._components._params)
            # create new components with the params
            self._set_components(params, new=True)
            # update dependencies
            for param in params:
                self._dependencies[
                    self._namespace[param]] = {"time"}

        # Get the collections of stateful elements and external elements
        self._stateful_elements = {
            name: getattr(self.components, name)
            for name in dir(self.components)
            if isinstance(getattr(self.components, name), Stateful)
        }
        self._dynamicstateful_elements = [
            getattr(self.components, name) for name in dir(self.components)
            if isinstance(getattr(self.components, name), DynamicStateful)
        ]
        self._external_elements = [
            getattr(self.components, name) for name in dir(self.components)
            if isinstance(getattr(self.components, name), External)
        ]
        self._macro_elements = [
            getattr(self.components, name) for name in dir(self.components)
            if isinstance(getattr(self.components, name), Macro)
        ]

        self._data_elements = [
            getattr(self.components, name) for name in dir(self.components)
            if isinstance(getattr(self.components, name), TabData)
        ]

        self._lookup_elements = [
            getattr(self.components, name) for name in dir(self.components)
            if isinstance(getattr(self.components, name), HardcodedLookups)
        ]

        # Load data files
        if data_files:
            self._get_data(data_files, data_files_encoding)

        # Assign the cache type to each variable
        self._assign_cache_type()
        # Get the initialization order of Stateful elements
        self._get_initialize_order()

        if return_func is not None:
            # Assign the return value of Macros
            self.return_func = getattr(self.components, return_func)
        else:
            self.return_func = lambda: 0

        self.py_model_file = str(py_model_file)

    def __call__(self):
        return self.return_func()

    @property
    def doc(self) -> pd.DataFrame:
        """
        The documentation of the model.
        """
        pass

    @property
    def namespace(self) -> dict:
        """
        The namespace dictionary of the model.
        """
        pass

    @property
    def dependencies(self) -> dict:
        """
        The dependencies dictionary of the model.
        """
        pass

    @property
    def subscripts(self) -> dict:
        """
        The subscripts dictionary of the model.
        """
        pass

    @property
    def modules(self) -> Union[dict, None]:
        """
        The dictionary of modules of the model. If the model is not
        split by modules it returns None.
        """
        pass

    def clean_caches(self):
        """
        Clean the cache of the object and the macros objects that it
        contains
        """
        pass

    def _get_data(self, data_files, encoding):
        """Load Data for TabData objects"""
        pass

    def _get_initialize_order(self):
        """
        Get the initialization order of the stateful elements
        and their the full dependencies.
        """
        pass

    def _get_full_dependencies(self, element, dep_set, stateful_deps):
        """
        Get all dependencies of an element, i.e., also get the dependencies
        of the dependencies. When finding an stateful element only dependencies
        for initialization are considered.

        Parameters
        ----------
        element: str
            Element to get the full dependencies.
        dep_set: set
            Set to include the dependencies of the element.
        stateful_deps: "initial" or "step"
            The type of dependencies to take in the case of stateful objects.

        Returns
        -------
        None

        """
        pass

    def _add_constant_cache(self):
        pass

    def _remove_constant_cache(self):
        pass

    def _assign_cache_type(self):
        """
        Assigns the cache type to all the elements from the namespace.
        """
        pass

    def _count_calls(self, element):
        pass

    def _assign_cache(self, element):
        """
        Assigns the cache type to the given element and its dependencies if
        needed.

        Parameters
        ----------
        element: str
            Element name.

        Returns
        -------
        None

        """
        pass

    def _isdynamic(self, dependencies):
        """

        Parameters
        ----------
        dependencies: iterable
            List of dependencies.

        Returns
        -------
        isdynamic: bool
            True if 'time' or a dynamic stateful objects is in dependencies.

        """
        pass

    def get_pysd_compiler_version(self):
        """
        Returns the version of pysd complier that used for generating
        this model
        """
        pass

    def initialize(self):
        """
        This function initializes the external objects and stateful objects
        in the given order.
        """
        pass

    def ddt(self):
        pass

    @property
    def state(self):
        pass

    @state.setter
    def state(self, new_value):
        pass

    def initialize_external_data(self, externals=None):

        """
        Initializes external data.

        If a path to a netCDF file containing serialized values of some or
        all of the model external data is passed in the external argument,
        those will be loaded from the file.

        To get the full performance gain of loading the externals from a netCDF
        file, the model should be loaded with initialize=False first.

        Examples of usage are available at
        `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#initializing-external-data-from-netcdf-file>`__.

        Parameters
        ----------
        externals: str or pathlib.Path (optional)
            Path to the netCDF file that contains the model external objects.

        Returns
        -------
        None

        See also
        --------
        :func:`pysd.py_backend.model.Macro.serialize_externals`

        Note
        ----
        To load externals from a netCDF file you need to have installed
        the optional dependency `netCDF4`.

        """
        pass

    def serialize_externals(self, export_path="externals.nc",
                            include_externals="all", exclude_externals=None):
        """
        Stores a netCDF file with the data and metadata for all model external
        objects.

        This method is useful for models with lots of external inputs, which
        are slow to load into memory. Once exported, the resulting netCDF file
        can be passed as argument to the initialize_external_data method.

        Names of variables should be those in the model (python safe,
        without the _ext_type_ string in front).

        Examples of usage are available at
        `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#initializing-external-data-from-netcdf-file>`__.

        Parameters
        ----------
        export_path: str or pathlib.Path (optional)
            Path of the resulting *.nc* file.
        include_externals: list or str (optional)
            External objects to export to netCDF.
            If 'all', then all externals are exported to the *.nc* file.
            The argument also accepts a list containing spreadsheet file names,
            external variable names or a combination of both. If a spreadsheet
            file path is passed, all external objects defined in it will be
            included in the *.nc* file. Spreadsheet tab names are not currently
            supported, because the same may be used in different files.
            Better customisation can be achieved by combining the
            include_externals and exclude_externals (see description below)
            arguments.
        exclude_externals: list or None (optional)
            Exclude external objects from being included in the exported nc
            file. It accepts either variable names, spreadsheet files or a
            combination of both.

        Returns
        -------
        None

        See also
        --------
        :func:`pysd.py_backend.model.Macro.initialize_external_data`

        Note
        ----
        To run this function you need to have installed the optional
        dependency `netCDF4`.

        """
        pass

    def __include_for_serialization(self, ext, py_name_clean, data, metadata,
                                    lookup_dims, data_dims):
        """
        Initialize the external object and get the data and metadata for
        inclusion in the netCDF.

        This function updates the metadata dict with the metadata corresponding
        to each external object, which is collected from model.doc. It also
        updates the data dict, with the data from the external object (ext).

        It renames the "time" dimension of ExtData types by appending _#
        followed by a unique number at the end of it. For large models, this
        prevents having an unnecessary large time dimension, which then causes
        all ExtData objects to have many nans when stored in a xarray Dataset.
        It does the same for the "lookup_dim" of all ExtLookup objects.

        Note
        ----
        Though subscripts can be read from Excel, they are hardcoded
        during the model building process. Therefore they will not be
        serialized.

        Parameters
        ----------
        ext: pysd.py_backend.externals.External
            External object. It can be any of the External subclasses
            (ExtConstant, ExtData, ExtLookup)
        py_name_clean: str
            Name of the variable without _ext_[constant|data|lookup] prefix.
        data: dict
            Collects all the data for each external, which is later used to
            build the xarray Dataset.
        metadata: dict
            Collects the metadata for each external, which is later included
            as data_vars attributes in the xarray Dataset.
        lookup_dims: utils.UniqueDims
            UniqueDims object for "lookup_dim" dimension.
        data_dims: utils.UniqueDims
            UniqueDims object for "time" dimension.

        Returns
        -------
        None

        """
        pass

    def __get_varname_from_ext_name(self, varname):
        """
        Returns the name of the variable that depends on the external object
        named varname. If that is not possible (see warning in the code to
        understand when that may happen), it gets the name by removing the
        _ext_[constant|data|lookup] prefix from the varname.

        Parameters
        ----------
        varname: str
            Variable name to which the External object is assigned.

        Returns
        -------
        var: str
            Name of the variable that calls the variable with name varname.

        """
        pass

    def get_args(self, param):
        """
        Returns the arguments of a model element.

        Parameters
        ----------
        param: str or func
            The model element name or function.

        Returns
        -------
        args: list
            List of arguments of the function.

        Examples
        --------
        >>> model.get_args('birth_rate')
        >>> model.get_args('Birth Rate')

        See also
        --------
        :func:`pysd.py_backend.model.Macro.get_coords`

        """
        pass

    def get_coords(self, param):
        """
        Returns the coordinates and dims of a model element.

        Parameters
        ----------
        param: str or func
            The model element name or function.

        Returns
        -------
        (coords, dims) or None: (dict, list) or None
            The coords and the dimensions of the element if it has.
            Otherwise, returns None.

        Examples
        --------
        >>> model.get_coords('birth_rate')
        >>> model.get_coords('Birth Rate')

        See also
        --------
        :func:`pysd.py_backend.model.Macro.get_args`

        """
        pass

    def __getitem__(self, param):
        """
        Returns the current value of a model component.

        Parameters
        ----------
        param: str or func
            The model element name.

        Returns
        -------
        value: float or xarray.DataArray
            The value of the model component.

        Examples
        --------
        >>> model['birth_rate']
        >>> model['Birth Rate']

        Note
        ----
        It will crash if the model component takes arguments.

        See also
        --------
        :func:`pysd.py_backend.model.Macro.get_series_data`

        """
        func_name = utils.get_key_and_value_by_insensitive_key_or_value(
            param,
            self._namespace)[1] or param

        if self.get_args(getattr(self.components, func_name)):
            raise ValueError(
                "Trying to get the current value of a lookup "
                "to get all the values with the series data use "
                "model.get_series_data(param)\n\n")

        return getattr(self.components, func_name)()

    def get_series_data(self, param):
        """
        Returns the original values of a model lookup/data component.

        Parameters
        ----------
        param: str
            The model lookup/data element name.

        Returns
        -------
        value: xarray.DataArray
            Array with the value of the interpolating series
            in the first dimension.

        Examples
        --------
        >>> model['room_temperature']
        >>> model['Room temperature']

        """
        pass

    def set_components(self, params):
        """
        Set the value of exogenous model elements.
        Element values should be passed with a dictionary in the
        function call. Values can be numeric type or pandas Series.
        Series will be interpolated by integrator.

        Parameters
        ----------
        params: dict
            Dictionary with the name of the elements to modify and the
            value that they would take. If the passed value is a
            :class:`float` or a :class:`xarray.DataArray` (must be
            compatible with the dimensions of the variable). In this
            case, the variable will have a constant value, returning
            the past value and broadcasting to all dimensions, if
            necessary. If a :class:`pandas.Series` is passed, the
            variable will be of type data and will use the time of the
            model to interpolate the result having as reference the
            indexes of the series. In this case, the series 'data' can
            also be a :class:`float` or a :class:`xarray.DataArray`,
            as with constant values. In the case of the target using
            a :class:`pysd.py_backend.lookups.Lookup` object, it will
            modify the object values to use the original arguments when
            being call. More detailed information and examples of usage
            are available at
            `Getting Started <https://pysd.readthedocs.io/en/master/getting_started.html#setting-parameter-values>`__.

            To write more complex relationships, which may or may not
            include other model variables, a callable, e.g. a function,
            can be passed that takes the same arguments as the original
            function and returns a :class:`float` or a
            :class:`xarray.DataArray` with exactly the same dimensions
            as the original function. More detailed information and
            examples of usage are available at
            `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#replacing-model-components-with-more-complex-objects>`__.


        Note
        ----
        This function is to modify the value or equations of the
        variables, it won't work properly with Stateful objects, e.g.
        Integ, DelayFixed... In order to modify them it will be
        necessary to do it manually, if you have other inputs it is
        recommended to modify these ones. To change their initial
        value :func:`pysd.py_backend.model.Model.set_initial_condition`
        method could be used.


        Examples
        --------
        >>> model.set_components({'birth_rate': 10})
        >>> model.set_components({'Birth Rate': 10})

        >>> br = pandas.Series(index=range(30), data=np.sin(range(30))
        >>> model.set_components({'birth_rate': br})

        See also
        --------
        :func:`pysd.py_backend.model.Model.set_initial_condition`
        :func:`pysd.py_backend.model.Macro.get_coords`
        :func:`pysd.py_backend.model.Macro.get_args`

        """
        pass

    def _set_components(self, params, new):
        """
        Set the value of exogenous model elements, giving the option to
        set new components (used in Macros).
        """
        pass

    def _timeseries_component(self, series, dims):
        """ Internal function for creating a timeseries model element """
        pass

    def _constant_component(self, value, dims):
        """ Internal function for creating a constant model element """
        pass

    def set_initial_value(self, time, initial_value):
        """
        Set the system initial value.

        Parameters
        ----------
        time : float or int
            The system intial time to be set.

        initial_value : dict
            A (possibly partial) dictionary of the system initial values.
            The keys to this dictionary may be either pysafe names or
            original model file names.

        See also
        --------
        :func:`pysd.py_backend.model.Model.set_initial_condition`

        """
        pass

    def _get_elements_to_initialize(self, modified_statefuls):
        pass

    def export(self):
        """Exports stateful values to a dictionary."""
        pass

    def _set_stateful(self, stateful_dict):
        """
        Set stateful values.

        Parameters
        ----------
        stateful_dict: dict
          Dictionary of the stateful elements and the attributes to change.

        """
        pass

    def _build_doc(self):
        """
        Formats a table of documentation strings to help users remember
        variable names, and understand how they are translated into
        Python safe names.

        Returns
        -------
        docs_df: pandas dataframe
            Dataframe with columns for the model components:
                - Real names
                - Python safe identifiers (as used in model.components)
                - Units string
                - Documentation strings from the original model file
        """
        pass

    def __str__(self):
        """ Return model source files """

        # JT: Might be helpful to return not only the source file, but
        # also how the instance differs from that source file. This
        # would give a more accurate view of the current model.
        string = 'Translated Model File: ' + self.py_model_file
        if hasattr(self, 'mdl_file'):
            string += '\n Original Model File: ' + self.mdl_file

        return string


class Model(Macro):
    """
    The Model class implements a stateful representation of the system.
    It inherits methods from the Macro class to integrate the model and
    access and modify model components. It also contains the main
    methods for running the model.

    The Model object will be created with components drawn from a
    translated Python model file.

    Parameters
    ----------
    py_model_file: str or pathlib.Path
        Filename of a model which has already been converted into a
        Python format.
    data_files: dict or list or str or None
        The dictionary with keys the name of file and variables to
        load the data from there. Or the list of names or name of the
        file to search the data in. Only works for TabData type object
        and it is neccessary to provide it. Default is None.
    initialize: bool
        If False, the model will not be initialize when it is loaded.
        Default is True.
    missing_values : str ("warning", "error", "ignore", "keep") (optional)
        What to do with missing values. If "warning" (default)
        shows a warning message and interpolates the values.
        If "raise" raises an error. If "ignore" interpolates
        the values without showing anything. If "keep" it will keep
        the missing values, this option may cause the integration to
        fail, but it may be used to check the quality of the data.

    See also
    --------
    :class:`pysd.py_backend.model.Macro`

    """
    def __init__(self, py_model_file, data_files, data_files_encoding,
                 initialize, missing_values):
        """ Sets up the Python objects """
        super().__init__(py_model_file, None, None, Time(),
                         data_files=data_files)
        self.data_files = data_files
        self.data_files_encoding = data_files_encoding
        self.missing_values = missing_values
        # set time component
        self.time.stage = 'Load'
        # set control var privately to do not change it when copying
        self.time._set_control_vars(**self.components._control_vars)
        # Attributes that are set later
        self.progress = None
        self.output = None
        self.capture_elements = None
        self.return_addresses = None
        self._stepper_mode = None
        self._submodel_tracker = {}

        if initialize:
            self.initialize()

    def initialize(self):
        """
        Initializes the simulation model.

        See also
        --------
        :func:`pysd.py_backend.model.Macro.initialize`
        :func:`pysd.py_backend.model.Model.reload`

        """
        pass

    def run(self, params=None, return_columns=None, return_timestamps=None,
            initial_condition='original', final_time=None, time_step=None,
            saveper=None, reload=False, progress=False, flatten_output=True,
            cache_output=True, output_file=None):
        """
        Simulate the model's behavior over time.
        Return a pandas dataframe with timestamps as rows and model
        elements as columns. More detailed information and examples
        of usage are available at
        `Getting Started <https://pysd.readthedocs.io/en/master/getting_started.html#running-the-model>`__.

        Parameters
        ----------
        params: dict (optional)
            Keys are strings of model component names.
            Values are numeric or pandas Series.
            Numeric values represent constants over the model integration.
            Timeseries will be interpolated to give time-varying input.
            For more information, check the documentation of
            :func:`pysd.py_backend.model.Macro.set_components`.

        return_timestamps: list, numeric, ndarray (1D) (optional)
            Timestamps in model execution at which to return state information.
            Defaults to model-file specified timesteps.

        return_columns: list, 'step' or None (optional)
            List of string model component names, returned dataframe
            will have corresponding columns. If 'step' only variables with
            cache step will be returned. If None, variables with cache step
            and run will be returned. Default is None.

        initial_condition: str or (float, dict) (optional)
            The starting time, and the state of the system (the values of
            all the stocks) at that starting time. 'original' or 'o' uses
            model-file specified initial condition. 'current' or 'c' uses
            the state of the model after the previous execution. Other str
            objects, loads initial conditions from the pickle file with the
            given name.(float, dict) tuple lets the user specify a starting
            time (float) and (possibly partial) dictionary of initial values
            for stock (stateful) objects. Default is 'original'.
            For more information, check the documentation of
            :func:`pysd.py_backend.model.Model.set_initial_condition`

        final_time: float or None
            Final time of the simulation. If float, the given value will be
            used to compute the return_timestamps (if not given) and as a
            final time. If None the last value of return_timestamps will be
            used as a final time. Default is None.

        time_step: float or None
            Time step of the simulation. If float, the given value will be
            used to compute the return_timestamps (if not given) and
            euler time series. If None the default value from components
            will be used. Default is None.

        saveper: float or None
            Saving step of the simulation. If float, the given value will be
            used to compute the return_timestamps (if not given). If None
            the default value from components will be used. Default is None.

        reload : bool (optional)
            If True, reloads the model from the translated model file
            before making changes. Default is False.

        progress : bool (optional)
            If True, a progressbar will be shown during integration.
            Default is False.

        flatten_output: bool (optional)
            If True, once the output dataframe has been formatted will
            split the xarrays in new columns following Vensim's naming
            to make a totally flat output. Default is True.
            This argument will be ignored when passing a netCDF4 file
            path in the output_file argument.

        cache_output: bool (optional)
           If True, the number of calls of outputs variables will be increased
           in 1. This helps caching output variables if they are called only
           once. For performance reasons, if time step = saveper it is
           recommended to activate this feature, if time step << saveper
           it is recommended to deactivate it. Default is True.

        output_file: str, pathlib.Path or None (optional)
           Path of the file in which to save simulation results.
           Currently, csv, tab and nc (netCDF4) files are supported.


        Examples
        --------
        >>> model.run(params={'exogenous_constant': 42})
        >>> model.run(params={'exogenous_variable': timeseries_input})
        >>> model.run(return_timestamps=[1, 2, 3, 4, 10])
        >>> model.run(return_timestamps=10)
        >>> model.run(return_timestamps=np.linspace(1, 10, 20))
        >>> model.run(output_file="results.nc")

        See also
        --------
        :func:`pysd.py_backend.model.Macro.set_components`
        :func:`pysd.py_backend.model.Model.set_initial_condition`
        :func:`pysd.py_backend.model.Model.reload`

        """
        pass

    def set_stepper(self, output_obj, params=None, step_vars=[],
                    return_columns=None, return_timestamps=None,
                    initial_condition='original', final_time=None,
                    time_step=None, saveper=None, cache_output=True):
        """
        Configure the model stepping behavior. Examples of usage are
        available at
        `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#running-models-one-or-more-step-s-at-a-time>`__.

        Parameters
        ----------
        output_obj: ModelOutput
            Instance of ModelOutput where the simulation results will be
            stored.

        params: dict (optional)
            Keys are strings of model component names.
            Values are numeric or pandas Series.
            Numeric values represent constants over the model integration.
            Timeseries will be interpolated to give time-varying input.

        step_vars: list
            List of variable or parameter names whose values might be
            updated after one or more simulation steps.

        return_columns: list, 'step' or None (optional)
            List of string model component names, returned dataframe
            will have corresponding columns. If 'step' only variables
            with cache step will be returned. If None, variables with
            cache step and run will be returned. Default is None.

        return_timestamps: list, numeric, ndarray (1D) (optional)
            Timestamps in model execution at which to return state
            information. Defaults to model-file specified timesteps.

        initial_condition: str or (float, dict) (optional)
            The starting time, and the state of the system (the values
            of all the stocks) at that starting time. 'original' or 'o'
            uses model-file specified initial condition. 'current' or
            'c' uses the state of the model after the previous
            execution. Other str objects, loads initial conditions from
            the pickle file with the given name.(float, dict) tuple lets
            the user specify a starting time (float) and (possibly
            partial) dictionary of initial values for stock (stateful)
            objects. Default is 'original'.

        final_time: float or None
            Final time of the simulation. If float, the given value will
            be used to compute the return_timestamps (if not given) and
            as a final time. If None the last value of return_timestamps
            will be used as a final time. Default is None.

        time_step: float or None
            Time step of the simulation. If float, the given value will
            be used to compute the return_timestamps (if not given) and
            euler time series. If None the default value from components
            will be used. Default is None.

        saveper: float or None
            Saving step of the simulation. If float, the given value will
            be used to compute the return_timestamps (if not given). If None
            the default value from components will be used. Default is None.

        cache_output: bool (optional)
           If True, the number of calls of outputs variables will be increased
           in 1. This helps caching output variables if they are called only
           once. For performance reasons, if time step = saveper it is
           recommended to activate this feature, if time step << saveper
           it is recommended to deactivate it. Default is True.

        See also
        --------
        :func:`pysd.py_backend.model.Model.step`

        """
        pass

    def step(self, num_steps=1, step_vars={}):
        """
        Run a model step. Updates model variables first (optional), and then
        runs any number of model steps. To collect the outputs after one or
        more steps, use the collect method of the ModelOutput class.
        Examples of usage are available at
        `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#running-models-one-or-more-step-s-at-a-time>`__

        Parameters
        ----------
        num_steps: int
            Number of steps that the iterator should run with the values
            of variables defined in step_vars argument.

        step_vars: dict
            Varibale names that should be updated before running the step
            as keys, and the actual values of the variables as values.

        Returns
        -------
        None

        See also
        --------
        :func:`pysd.py_backend.model.Model.set_stepper`

        """
        pass

    def _config_simulation(self, params, return_columns, return_timestamps,
                           initial_condition, final_time, time_step,
                           saveper, cache_output, **kwargs):
        """
        Internal method to set all simulation config parameters. Arguments
        to this function are those of the run and set_stepper methods.
        """
        pass

    def _set_capture_elements(self, return_columns):
        """
        Define which variables will be stored in the output object, according
        to the return_columns passed by the user. The list is stored in the
        capture_elements attribute, which is a dictionary with keys "run" and
        "step".

        Parameters
        ----------

        return_columns:list, 'step' or None (optional)
            List of string model component names, returned dataframe
            will have corresponding columns. If 'step' only variables with
            cache step will be returned. If None, variables with cache step
            and run will be returned. Default is None.

        Returns
        -------
        capture_elements: dict
            Dictionary of list with keywords step and run.

        """
        pass

    def _set_progressbar(self, progress):
        """
        Configures the progressbar, according to the user provided argument.
        If final_time or time_step are functions, then the progressbar is
        automatically disabled, regardless of the value of the progress
        argument.

        Parameters
        ----------
        progress: bool

        """
        pass

    def _set_control_vars(self, return_timestamps, final_time, time_step,
                          saveper):
        pass

    def select_submodel(self, vars=[], modules=[], exogenous_components={},
                        inplace=True):
        """
        Select a submodel from the original model. After selecting a submodel
        only the necessary stateful objects for integrating this submodel will
        be computed. Examples of usage are available at
        `Advanced Usage <https://pysd.readthedocs.io/en/master/advanced_usage.html#selecting-and-running-a-submodel>`__.

        Parameters
        ----------
        vars: set or list of strings (optional)
            Variables to include in the new submodel.
            It can be an empty list if the submodel is only selected by
            module names. Default is an empty list.

        modules: set or list of strings (optional)
            Modules to include in the new submodel.
            It can be an empty list if the submodel is only selected by
            variable names. Default is an empty list. Can select a full
            module or a submodule by passing the path without the .py, e.g.:
            "view_1/submodule1".

        exogenous_components: dictionary of parameters (optional)
            Exogenous value to fix to the model variables that are needed
            to run the selected submodel. The exogenous_components should
            be passed as a dictionary in the same way it is done for
            set_components method. By default it is an empty dict and
            the needed exogenous components will be set to a numpy.nan value.

        inplace: bool (optional)
            If True it will modify current object and will return None.
            If False it will create a copy of the model and return it
            keeping the original model unchange. Default is True.

        Returns
        -------
        None or pysd.py_backend.model.Model
            If inplace=False it will return a modified copy of the
            original model.

        Note
        ----
        modules can be only passed when the model has been split in
        different files during translation.

        Examples
        --------
        >>> model.select_submodel(
        ...     vars=["Room Temperature", "Teacup temperature"])
        UserWarning: Selecting submodel, to run the full model again use model.reload()

        >>> model.select_submodel(
        ...     modules=["view_1", "view_2/subview_1"])
        UserWarning: Selecting submodel, to run the full model again use model.reload()
        UserWarning: Exogenous components for the following variables are necessary but not given:
            initial_value_stock1, stock3

        >>> model.select_submodel(
        ...     vars=["stock3"],
        ...     modules=["view_1", "view_2/subview_1"])
        UserWarning: Selecting submodel, to run the full model again use model.reload()
        UserWarning: Exogenous components for the following variables are necessary but not given:
            initial_value_stock1, initial_value_stock3
        Please, set them before running the model using set_components method...

        >>> model.select_submodel(
        ...     vars=["stock3"],
        ...     modules=["view_1", "view_2/subview_1"],
        ...     exogenous_components={
        ...         "initial_value_stock1": 3,
        ...         "initial_value_stock3": 5})
        UserWarning: Selecting submodel, to run the full model again use model.reload()

        See also
        --------
        :func:`pysd.py_backend.model.Model.get_vars_in_module`
        :func:`pysd.py_backend.model.Model.get_dependencies`

        """
        pass

    def _select_submodel(self, vars, modules, exogenous_components={}):
        pass

    def get_dependencies(self, vars=[], modules=[]):
        """
        Get the dependencies of a set of variables or modules.

        Parameters
        ----------
        vars: set or list of strings (optional)
            Variables to get the dependencies from.
            It can be an empty list if the dependencies are computed only
            using modules. Default is an empty list.
        modules: set or list of strings (optional)
            Modules to get the dependencies from.
            It can be an empty list if the dependencies are computed only
            using variables. Default is an empty list. Can select a full
            module or a submodule by passing the path without the .py, e.g.:
            "view_1/submodule1".

        Returns
        -------
        dependencies: pysd.py_backend.utils.Dependencies
            Dependencies data object.

        Note
        ----
        modules can be only passed when the model has been split in
        different files during translation.

        Examples
        --------
        >>> print(model.get_dependencies(
        ...     vars=["Room Temperature", "Teacup temperature"]))
        Selected variables (total 1):
            room_temperature, teacup_temperature
        Stateful objects integrated with the selected variables (total 1):
            _integ_teacup_temperature

        >>> print(model.get_dependencies(
        ...     modules=["view_1", "view_2/subview_1"]))
        Selected variables (total 4):
            var1, var2, stock1, delay1
        Dependencies for initialization only (total 1):
            initial_value_stock1
        Dependencies that may change over time (total 2):
            stock3
        Stateful objects integrated with the selected variables (total 1):
            _integ_stock1, _delay_fixed_delay1

        >>> print(model.get_dependencies(
        ...     vars=["stock3"],
        ...     modules=["view_1", "view_2/subview_1"]))
        Selected variables (total 4):
            var1, var2, stock1, stock3, delay1
        Dependencies for initialization only (total 1):
            initial_value_stock1, initial_value_stock3
        Stateful objects integrated with the selected variables (total 1):
            _integ_stock1, _integ_stock3, _delay_fixed_delay1

        See also
        --------
        :func:`pysd.py_backend.model.Model.get_vars_in_module`

        """
        pass

    def get_vars_in_module(self, module):
        """
        Return the name of Python vars in a module.

        Parameters
        ----------
        module: str
            Name of the module to search in.

        Returns
        -------
        vars: set
            Set of varible names in the given module.

        See also
        --------
        :func:`pysd.py_backend.model.Model.get_dependencies`

        """
        pass

    def copy(self, reload=False):
        """
        Create a copy of the current model.

        Parameters
        ----------
        reload: bool (optional)
            If True the model will be copied without applying to it any
            change, the copy will simply load the model again from the
            translated file. This would be equivalent to doing
            :py:func:`pysd.load` with the same arguments. Otherwise, it
            will apply the same changes that have been applied to the
            original model and update the states (faithful copy).
            Default is False.

        Warning
        -------
        The copy function will load a new model from the file and apply
        the same changes to it. If any of these changes have replaced a
        variable with a function that references other variables in the
        model, the copy will not work properly since the function will
        still reference the variables in the original model, in which
        case the function should be redefined.

        See also
        --------
        :func:`pysd.py_backend.model.Model.reload`

        """
        pass

    def reload(self):
        """
        Reloads the model from the translated model file, so that all the
        parameters are back to their original value.

        See also
        --------
        :func:`pysd.py_backend.model.Model.copy`
        :func:`pysd.py_backend.model.Model.initialize`

        """
        pass

    def _default_return_columns(self, which):
        """
        Return a list of the model elements tha change on time that
        does not include lookup other functions that take parameters
        or run-cached functions.

        Parameters
        ----------
        which: str or None
            If it is 'step' only cache step elements will be returned.
            Else cache 'step' and 'run' elements will be returned.
            Default is None.

        Returns
        -------
        return_columns: list
            List of columns to return

        """
        pass

    def _split_capture_elements(self, capture_elements):
        """
        Splits the capture elements list between those with run cache
        and others.

        Parameters
        ----------
        capture_elements: list
            Captured elements list

        Returns
        -------
        capture_dict: dict
            Dictionary of list with keywords step and run.

        """
        pass

    def set_initial_condition(self, initial_condition):
        """ Set the initial conditions of the integration.

        Parameters
        ----------
        initial_condition : str or (float, dict) or pathlib.Path
            The starting time, and the state of the system (the values of
            all the stocks) at that starting time. 'original' or 'o'uses
            model-file specified initial condition. 'current' or 'c' uses
            the state of the model after the previous execution. Other str
            objects, loads initial conditions from the pickle file with the
            given name.(float, dict) tuple lets the user specify a starting
            time (float) and (possibly partial) dictionary of initial values
            for stock (stateful) objects.

        Examples
        --------
        >>> model.set_initial_condition('original')
        >>> model.set_initial_condition('current')
        >>> model.set_initial_condition('exported_pickle.pic')
        >>> model.set_initial_condition((10, {'teacup_temperature': 50}))

        See also
        --------
        :func:`pysd.py_backend.model.Macro.set_initial_value`

        """
        pass

    def _euler_step(self, dt):
        """
        Performs a single step in the euler integration,
        updating stateful components

        Parameters
        ----------
        dt : float
            This is the amount to increase time by this step

        """
        pass

    def _integrate(self):
        """
        Performs euler integration and writes results to the out_obj.

        Returns
        -------
        None

        """
        pass

    def _integrate_step(self):
        pass

    def export(self, file_name):
        """
        Export stateful values to pickle file.

        Parameters
        ----------
        file_name: str or pathlib.Path
          Name of the file to export the values.

        See also
        --------
        :func:`pysd.py_backend.model.Model.import_pickle`

        """
        pass

    def import_pickle(self, file_name):
        """
        Import stateful values from pickle file.

        Parameters
        ----------
        file_name: str or pathlib.Path
          Name of the file to import the values from.

        See also
        --------
        :func:`pysd.py_backend.model.Model.export_pickle`

        """
        pass
