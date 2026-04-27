"""
These are the decorators used by the functions in the model file.
functions.py
"""
from functools import wraps
import inspect


class Cache(object):
    """
    This is the class for the chache. Several cache types can be saved
    in dictionaries and acces using cache.data[cache_type].
    """
    def __init__(self):
        self.cached_funcs = set()
        self.data = {}

    def __call__(self, func, *args):
        """ Decorator for caching """

        @wraps(func)
        def cached_func(*args):
            """ Cache function """
            pass
        return cached_func

    def clean(self):
        """ Cleans the cache """
        pass


def constant_cache(function, *args):
    """
    Constant cache decorator for all the run
    The original function is saved in 'function' attribuite so we can
    recover it later.
    """
    pass
