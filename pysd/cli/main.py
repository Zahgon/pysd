import sys
import os
from pathlib import Path

from datetime import datetime

import pysd
from pysd.translators.vensim.vensim_utils import supported_extensions as\
    vensim_extensions
from pysd.translators.xmile.xmile_utils import supported_extensions as\
    xmile_extensions

from .parser import parser


def main(args):
    """
    Main function. Reads user arguments, loads the models,
    runs it and saves the output

    Parameters
    ----------
    args: list
        User arguments.

    Returns
    -------
    None

    """
    pass


def load(model_file, data_files, missing_values, split_views, **kwargs):
    """
    Translate and load model file.

    Paramters
    ---------
    model_file: str
        Vensim, Xmile or PySD model file.

    data_files: list
        If given the list of files where the necessary data to run the model
        is given.

    missing_values : str ("warning", "error", "ignore", "keep")
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

    **kwargs: (optional)
        Additional keyword arguments.
        subview_sep:(str)
            Character used to separate views and subviews. If provided,
            and split_views=True, each submodule will be placed inside the
            folder of the parent view.

    Returns
    -------
    pysd.model

    """
    pass


def create_configuration(model, options):
    """
    create configuration dict to pass to the run method.

    Parameters
    ----------
    model: pysd.model object

    options: argparse.Namespace

    Returns
    -------
    conf_dict: dict

    """
    pass
