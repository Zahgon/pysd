"""
The Stateful objects are used and updated each time step with an update
method. This include Integs, Delays, Forecasts, Smooths, and Trends,
between others. The Macro class and Model class are also Stateful type.
However, they are defined appart as they are more complex.
"""
import warnings

import numpy as np
import xarray as xr

from .functions import zidz, if_then_else


SMALL_VENSIM = 1e-6  # What is considered zero according to Vensim Help


class Stateful(object):
    # the integrator needs to be able to 'get' the current state of the object,
    # and get the derivative. It calculates the new state, and updates it.
    # The state can be any object which is subject to basic (element-wise)
    # algebraic operations
    def __init__(self):
        self._state = None
        self.shape_info = None
        self.py_name = ""

    def __call__(self, *args, **kwargs):
        return self.state

    @property
    def state(self):
        pass

    @state.setter
    def state(self, new_value):
        pass


class DynamicStateful(Stateful):

    def __init__(self):
        super().__init__()

    def update(self, state):
        pass


class Integ(DynamicStateful):
    """
    Implements INTEG function.

    Parameters
    ----------
    ddt: callable
        Derivate to integrate.
    initial_value: callable
        Initial value.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. Value of the stock.

    """
    def __init__(self, ddt, initial_value, py_name):
        super().__init__()
        self.init_func = initial_value
        self.ddt = ddt
        self.shape_info = None
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def export(self):
        pass


class NonNegativeInteg(Integ):
    """
    Implements non negative INTEG function.

    Parameters
    ----------
    ddt: callable
        Derivate to integrate.
    initial_value: callable
        Initial value.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. Value of the stock.

    """
    def __init__(self, ddt, initial_value, py_name):
        super().__init__(ddt, initial_value, py_name)

    def update(self, state):
        pass


class Delay(DynamicStateful):
    """
    Implements DELAY function.

    Parameters
    ----------
    delay_input: callable
        Input of the delay.
    delay_time: callable
        Delay time.
    initial_value: callable
        Initial value.
    order: callable
        Delay order.
    tsetp: callable
        The time step of the model.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: numpy.array or xarray.DataArray
        Current state of the object. Array of the delays values multiplied
        by their corresponding average time.

    """
    # note that we could have put the `delay_input` argument as a parameter to
    # the `__call__` function, and more closely mirrored the vensim syntax.
    # However, people may get confused this way in thinking that they need
    # only one delay object and can call it with various arguments to delay
    # whatever is convenient. This method forces them to acknowledge that
    # additional structure is being created in the delay object.

    def __init__(self, delay_input, delay_time, initial_value, order, tstep,
                 py_name):
        super().__init__()
        self.init_func = initial_value
        self.delay_time_func = delay_time
        self.input_func = delay_input
        self.order_func = order
        self.order = None
        self.tstep = tstep
        self.shape_info = None
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def __call__(self):
        if self.shape_info:
            return self.state[-1].reset_coords('_delay', drop=True)\
                   / self.delay_time_func()
        else:
            return self.state[-1] / self.delay_time_func()

    def ddt(self):
        pass

    def export(self):
        pass


class DelayN(DynamicStateful):
    """
    Implements DELAY N function.

    Parameters
    ----------
    delay_input: callable
        Input of the delay.
    delay_time: callable
        Delay time.
    initial_value: callable
        Initial value.
    order: callable
        Delay order.
    tsetp: callable
        The time step of the model.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: numpy.array or xarray.DataArray
        Current state of the object. Array of the delays values multiplied
        by their corresponding average time.

    times: numpy.array or xarray.DataArray
        Array of delay times used for computing the delay output.
        If delay_time is constant, this array will be constant and
        DelayN will behave ad Delay.

    """
    # note that we could have put the `delay_input` argument as a parameter to
    # the `__call__` function, and more closely mirrored the vensim syntax.
    # However, people may get confused this way in thinking that they need
    # only one delay object and can call it with various arguments to delay
    # whatever is convenient. This method forces them to acknowledge that
    # additional structure is being created in the delay object.

    def __init__(self, delay_input, delay_time, initial_value, order, tstep,
                 py_name):
        super().__init__()
        self.init_func = initial_value
        self.delay_time_func = delay_time
        self.input_func = delay_input
        self.order_func = order
        self.order = None
        self.times = None
        self.tstep = tstep
        self.shape_info = None
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def __call__(self):
        if self.shape_info:
            return self.state[-1].reset_coords('_delay', drop=True)\
                   / self.times[0].reset_coords('_delay', drop=True)
        else:
            return self.state[-1] / self.times[0]

    def ddt(self):
        pass

    def export(self):
        pass


class DelayFixed(DynamicStateful):
    """
    Implements DELAY FIXED function.

    Parameters
    ----------
    delay_input: callable
        Input of the delay.
    delay_time: callable
        Delay time.
    initial_value: callable
        Initial value.
    tsetp: callable
        The time step of the model.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object, equal to pipe[pointer].
    pipe: list
        List of the delays values.
    pointer: int
        Pointer to the last value in the pipe

    """

    def __init__(self, delay_input, delay_time, initial_value, tstep,
                 py_name):
        super().__init__()
        self.init_func = initial_value
        self.delay_time_func = delay_time
        self.input_func = delay_input
        self.tstep = tstep
        self.order = None
        self.pointer = 0
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def __call__(self):
        return self.state

    def ddt(self):
        pass

    def update(self, state):
        pass

    def export(self):
        pass


class Forecast(DynamicStateful):
    """
    Implements FORECAST function.

    Parameters
    ----------
    forecast_input: callable
        Input of the forecast.
    average_time: callable
        Average time.
    horizon: callable
        Forecast horizon.
    initial_trend: callable
        Initial trend of the forecast.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. AV value by Vensim docs.

    """
    def __init__(self, forecast_input, average_time, horizon, initial_trend,
                 py_name):
        super().__init__()
        self.horizon = horizon
        self.average_time = average_time
        self.input = forecast_input
        self.initial_trend = initial_trend
        self.py_name = py_name

    def initialize(self, init_trend=None):

        # self.state = AV in the vensim docs
        pass

    def __call__(self):
        return self.input() * (
            1 + zidz(self.input() - self.state,
                     self.average_time() * self.state
                     )*self.horizon()
        )

    def ddt(self):
        pass

    def export(self):
        pass


class Smooth(DynamicStateful):
    """
    Implements SMOOTH function.

    Parameters
    ----------
    smooth_input: callable
        Input of the smooth.
    smooth_time: callable
        Smooth time.
    initial_value: callable
        Initial value.
    order: callable
        Delay order.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: numpy.array or xarray.DataArray
        Current state of the object. Array of the inputs having the
        value to return in the last position.

    """
    def __init__(self, smooth_input, smooth_time, initial_value, order,
                 py_name):
        super().__init__()
        self.init_func = initial_value
        self.smooth_time_func = smooth_time
        self.input_func = smooth_input
        self.order_func = order
        self.order = None
        self.shape_info = None
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def __call__(self):
        if self.shape_info:
            return self.state[-1].reset_coords('_smooth', drop=True)
        else:
            return self.state[-1]

    def ddt(self):
        pass

    def export(self):
        pass


class Trend(DynamicStateful):
    """
    Implements TREND function.

    Parameters
    ----------
    trend_input: callable
        Input of the trend.
    average_time: callable
        Average time.
    initial_trend: callable
        Initial trend.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. AV value by Vensim docs.

    """
    def __init__(self, trend_input, average_time, initial_trend, py_name):
        super().__init__()
        self.init_func = initial_trend
        self.average_time_function = average_time
        self.input_func = trend_input
        self.py_name = py_name

    def initialize(self, init_trend=None):
        pass

    def __call__(self):
        return zidz(self.input_func() - self.state,
                    self.average_time_function() * np.abs(self.state))

    def ddt(self):
        pass

    def export(self):
        pass


class SampleIfTrue(DynamicStateful):
    """
    Implements SAMPLE IF TRUE function.

    Parameters
    ----------
    condition: callable
        Condition for sample.
    actual_value: callable
        Value to update if condition is true.
    initial_value: callable
        Initial value.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object. Last actual_value when condition
        was true or the initial_value if condition has never been true.

    """
    def __init__(self, condition, actual_value, initial_value, py_name):
        super().__init__()
        self.condition = condition
        self.actual_value = actual_value
        self.init_func = initial_value
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def __call__(self):
        return if_then_else(self.condition(),
                            self.actual_value,
                            lambda: self.state)

    def ddt(self):
        pass

    def update(self, state):
        pass

    def export(self):
        pass


class Initial(Stateful):
    """
    Implements INITIAL function.

    Parameters
    ----------
    initial_value: callable
        Initial value.
    py_name: str
        Python name to identify the object.

    Attributes
    ----------
    state: float or xarray.DataArray
        Current state of the object, which will always be the initial_value.

    """
    def __init__(self, initial_value, py_name):
        super().__init__()
        self.init_func = initial_value
        self.py_name = py_name

    def initialize(self, init_val=None):
        pass

    def export(self):
        pass
