"""
Model components and time managing classes.
"""

from warnings import warn
import os
import random
import inspect
import importlib.util
from copy import deepcopy

import numpy as np

from pysd._version import __version__


class Component(object):

    def __init__(self):
        self.namespace = {}
        self.dependencies = {}

    def add(self, name, units=None, limits=(np.nan, np.nan),
            subscripts=None, comp_type=None, comp_subtype=None,
            depends_on={}, other_deps={}):
        """
        This decorators allows assigning metadata to a function.
        """
        pass


class Components(object):
    """
    Workaround class to let the user do:
        model.components.var = value
    """
    def __init__(self, py_model_file, set_components):
        object.__setattr__(self, "_components", self._load(py_model_file))
        object.__setattr__(self, "_set_components", set_components)

    def _load(self, py_model_file):
        """
        Load model components.

        Parameters
        ----------
        py_model_file: str
            Model file to be loaded.

        Returns
        -------
        components: module
            The imported file content.

        """
        pass

    def __getattribute__(self, name):
        """
        Get attribute from the class. Try Except vlock is used to load directly
        model components in order to avoid making the model slower during the
        integration.
        """
        try:
            return getattr(object.__getattribute__(self, "_components"), name)
        except AttributeError:
            if name in ["_components", "_set_components",
                        "_set_component", "_load"]:
                # The attribute is from the class Components
                return object.__getattribute__(self, name)
            else:
                raise NameError(f"Component '{name}' not found in the model.")

    def __setattr__(self, name, value):
        """
        Workaround calling the Macro._set_components method
        """
        self._set_components({name: value})

    def _set_component(self, name, value):
        """
        Replaces the previous setter.
        """
        pass


class Time(object):
    rprec = 1e-5  # relative precision for final time and saving time

    def __init__(self):
        self._time = None
        self.stage = None
        self.return_timestamps = None
        self._next_return = None
        self._control_vars_tracker = {}

    def __call__(self):
        return self._time

    def export(self):
        """Exports time values to a dictionary."""
        pass

    def _get_control_vars(self):
        """
        Make control vars changes exportable.
        """
        pass

    def _set_time(self, time_dict):
        """Copy values from other Time object, used by Model.copy"""
        pass

    def set_control_vars(self, **kwargs):
        """
        Set the control variables values

        Parameters
        ----------
        **kwards:
            initial_time: float, callable or None
                Initial time.
            final_time: float, callable or None
                Final time.
            time_step: float, callable or None
                Time step.
            saveper: float, callable or None
                Saveper.

        """
        pass

    def _set_control_vars(self, **kwargs):
        """
        Set the control variables values. Private version to be used
        to avoid tracking changes.
        """
        pass

    def in_bounds(self):
        """
        Check if time is smaller than current final time value.

        Returns
        -------
        bool:
            True if time is smaller than final time. Otherwise, returns Fase.

        """
        pass

    def in_return(self):
        """ Check if current time should be returned """
        pass

    def round(self):
        """ Return rounded time to outputs to avoid float precision error"""
        pass

    def add_return_timestamps(self, return_timestamps):
        """ Add return timestamps """
        pass

    def update(self, value):
        """ Update current time value """
        pass

    def _update_next_return(self):
        """ Update the next_return value """
        pass

    def reset(self):
        """ Reset time value to the initial """
        pass
