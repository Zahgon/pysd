"""
pysd.py

Contains all the code that will be directly accessed by the user in
normal operation.
"""

import sys
from warnings import warn

from pysd.py_backend.model import Model


if sys.version_info[:2] < (3, 9):  # pragma: no cover
    raise RuntimeError(
        "\n\n"
        + "Your Python version is no longer supported by PySD.\n"
        + "The current version needs to run at least Python 3.9."
        + " You are running:\n\tPython "
        + sys.version
        + "\nPlease update your Python version or use the last "
        + " supported version:\n\t"
        + "https://github.com/SDXorg/pysd/releases/tag/LastPy2"
    )


def read_xmile(xmile_file, data_files=None, data_files_encoding=None,
               initialize=True, missing_values="warning"):
    """
    Construct a model from a Xmile file.

    Parameters
    ----------
    xmile_file:  str or pathlib.Path
        The relative path filename for a raw Xmile file.

    initialize: bool (optional)
        If False, the model will not be initialize when it is loaded.
        Default is True.

    data_files: dict or list or str or None
        The dictionary with keys the name of file and variables to
        load the data from there. Or the list of names or name of the
        file to search the data in. Only works for TabData type object
        and it is neccessary to provide it. Default is None.

    data_files_encoding: list or str or dict or None (optional)
        Encoding for data_files. If a string or None is passed this
        value will be used for all the files. If data_files is a list,
        a list of the same length could be used to specify different
        encodings. If data_files is a dictionary, a dictionary with the
        same keys could be used, being the values the encodings. See
        documentation from pandas.read_table for further information.
        Default is None.

    missing_values: str ("warning", "error", "ignore", "keep") (optional)
        What to do with missing values. If "warning" (default)
        shows a warning message and interpolates the values.
        If "raise" raises an error. If "ignore" interpolates
        the values without showing anything. If "keep" it will keep
        the missing values, this option may cause the integration to
        fail, but it may be used to check the quality of the data.

    Returns
    -------
    model: a PySD class object
        Elements from the Python model are loaded into the PySD class
        and ready to run

    Examples
    --------
    >>> model = read_xmile('../tests/test-models/samples/teacup/teacup.xmile')

    """
    pass


def read_vensim(mdl_file, data_files=None, data_files_encoding=None,
                initialize=True, missing_values="warning",
                split_views=False, encoding=None, **kwargs):
    """
    Construct a model from Vensim `.mdl` file.

    Parameters
    ----------
    mdl_file: str or pathlib.Path
        The relative path filename for a raw Vensim `.mdl` file.

    initialize: bool (optional)
        If False, the model will not be initialize when it is loaded.
        Default is True.

    data_files: dict or list or str or None
        The dictionary with keys the name of file and variables to
        load the data from there. Or the list of names or name of the
        file to search the data in. Only works for TabData type object
        and it is neccessary to provide it. Default is None.

    data_files_encoding: list or str or dict or None (optional)
        Encoding for data_files. If a string or None is passed this
        value will be used for all the files. If data_files is a list,
        a list of the same length could be used to specify different
        encodings. If data_files is a dictionary, a dictionary with the
        same keys could be used, being the values the encodings. See
        documentation from pandas.read_table for further information.
        Default is None.

    data_files_encoding: list or str or dict or None (optional)
        Encoding for data_files. If a string or None is passed this
        value will be used for all the files. If data_files is a list,
        a list of the same length could be used to specify different
        encodings. If data_files is a dictionary, a dictionary with the
        same keys could be used, being the values the encodings. See
        documentation from pandas.read_table for further information.
        Default is None.

    missing_values: str ("warning", "error", "ignore", "keep") (optional)
        What to do with missing values. If "warning" (default)
        shows a warning message and interpolates the values.
        If "raise" raises an error. If "ignore" interpolates
        the values without showing anything. If "keep" it will keep
        the missing values, this option may cause the integration to
        fail, but it may be used to check the quality of the data.

    split_views: bool (optional)
        If True, the sketch is parsed to detect model elements in each
        model view, and then translate each view in a separate Python
        file. Setting this argument to True is recommended for large
        models split in many different views. Default is False.

    encoding: str or None (optional)
        Encoding of the source model file. If None, the encoding will be
        read from the model, if the encoding is not defined in the model
        file it will be set to 'UTF-8'. Default is None.

    subview_sep: list
        Characters used to separate views and subviews (e.g. [",", "."]).
        If provided, and split_views=True, each submodule will be placed
        inside the directory of the parent view.

    **kwargs: (optional)
        Additional keyword arguments for translation.

    Returns
    -------
    model: a PySD class object
        Elements from the Python model are loaded into the PySD class
        and ready to run

    Examples
    --------
    >>> model = read_vensim('../tests/test-models/samples/teacup/teacup.mdl')

    """
    pass


def load(py_model_file, data_files=None, data_files_encoding=None,
         initialize=True, missing_values="warning"):
    """
    Load a Python-converted model file.

    Parameters
    ----------
    py_model_file : str
        Filename of a model which has already been converted into a
        Python format.

    initialize: bool (optional)
        If False, the model will not be initialize when it is loaded.
        Default is True.

    data_files: dict or list or str or None
        The dictionary with keys the name of file and variables to
        load the data from there. Or the list of names or name of the
        file to search the data in. Only works for TabData type object
        and it is neccessary to provide it. Default is None.

    data_files_encoding: list or str or dict or None (optional)
        Encoding for data_files. If a string or None is passed this
        value will be used for all the files. If data_files is a list,
        a list of the same length could be used to specify different
        encodings. If data_files is a dictionary, a dictionary with the
        same keys could be used, being the values the encodings. See
        documentation from pandas.read_table for further information.
        Default is None.

    missing_values : str ("warning", "error", "ignore", "keep") (optional)
        What to do with missing values. If "warning" (default)
        shows a warning message and interpolates the values.
        If "raise" raises an error. If "ignore" interpolates
        the values without showing anything. If "keep" it will keep
        the missing values, this option may cause the integration to
        fail, but it may be used to check the quality of the data.

    Examples
    --------
    >>> model = load('../tests/test-models/samples/teacup/teacup.py')

    """
    pass
