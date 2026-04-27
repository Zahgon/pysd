"""
The VensimFile class allows reading the original Vensim model file,
parsing it into Section elements using the FileSectionsVisitor,
parsing its sketch using SketchVisitor in order to classify the varibales
per view. The final result can be exported to an AbstractModel class in
order to build the model in another programming language.
"""
import re
from typing import Union, List
from pathlib import Path
import warnings
import parsimonious
from collections.abc import Mapping

from ..structures.abstract_model import AbstractModel

from . import vensim_utils as vu
from .vensim_section import Section
from .vensim_utils import supported_extensions


class VensimFile():
    """
    The VensimFile class allows parsing an mdl file.
    When the object is created, the model file is automatically opened;
    unnecessary tabs, whitespaces, and linebreaks are removed; and
    the sketch is split from the model equations.

    Parameters
    ----------
    mdl_path: str or pathlib.Path
        Path to the Vensim model.

    encoding: str or None (optional)
        Encoding of the source model file. If None, the encoding will be
        read from the model, if the encoding is not defined in the model
        file it will be set to 'UTF-8'. Default is None.

    """
    def __init__(self, mdl_path: Union[str, Path],
                 encoding: Union[None, str] = None):
        self.mdl_path = Path(mdl_path)
        self.root_path = self.mdl_path.parent
        self.model_text = self._read(encoding)
        self.sketch = ""
        self.view_elements = None
        self._split_sketch()

    def __str__(self):  # pragma: no cover
        return "\nVensim model file, loaded from:\n\t%s\n" % self.mdl_path

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get model information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print model information to standard output."""
        pass

    def _read(self, encoding: Union[None, str]) -> str:
        """
        Read a Vensim file and assign its content to self.model_text

        Returns
        -------
        str: model file content

        """
        pass

    def _split_sketch(self) -> None:
        """Split model from the sketch."""
        pass

    def _clean(self, text: str) -> str:
        """Remove unnecessary characters."""
        pass

    def parse(self, parse_all: bool = True) -> None:
        """
        Parse model file with parsimonious using the grammar given in
        'parsing_grammars/file_sections.peg' and the class FileSectionsVisitor
        to visit the parsed expressions.

        This breaks the model file in VensimSections, which correspond to the
        main model section and the macros.

        Parameters
        ----------
        parse_all: bool (optional)
            If True, the VensimSection objects created will be
            automatically parsed. Otherwise, these objects will only be
            added to self.sections but not parsed. Default is True.

        """
        pass

    def parse_sketch(self, subview_sep: List[str]) -> None:
        """
        Parse the sketch of the model with parsimonious using the grammar
        given in 'parsing_grammars/sketch.peg' and the class SketchVisitor
        to visit the parsed expressions.

        It will modify the views_dict of the first section, including
        the dictionary of the classification of variables by views. This,
        method should be called after calling the self.parse method.

        Parameters
        ----------
        subview_sep: list
           List of the separators to use to classify the model views in
           folders and subfolders. The sepparator must be ordered in the
           same order they appear in the view name. For example,
           if a view is named "economy:demand.exports" if
           subview_sep=[":", "."] this view's variables will be included
           in the file 'exports.py' and inside the folders economy/demand.


        """
        pass

    def get_abstract_model(self) -> AbstractModel:
        """
        Instantiate the AbstractModel object used during building. This,
        method should be called after parsing the model (self.parse) and,
        in case you want to split the variables per views, also after
        parsing the sketch (self.parse_sketch). This automatically calls the
        get_abstract_section method from the model sections.

        Returns
        -------
        AbstractModel: AbstractModel
          Abstract Model object that can be used for building the model
          in another language.

        """
        pass

    @staticmethod
    def _clean_file_names(*args):
        """
        Removes special characters and makes clean file names.

        Parameters
        ----------
        *args: tuple
            Any number of strings to clean.

        Returns
        -------
        clean: list
            List containing the clean strings.

        """
        pass

    @staticmethod
    def _merge_nested_dicts(original, to_merge):
        """
        Merge dictionaries recursively, preserving common keys.

        Parameters
        ----------
        original: dict
            Dictionary onto which the merge is executed.

        to_merge: dict or set
            Dictionary to be merged to the original_dict.

        Returns
        -------
        None

        """
        pass


class FileSectionsVisitor(parsimonious.NodeVisitor):
    """Parse file sections"""
    def __init__(self, ast):
        self.entries = [None]
        self.visit(ast)

    def visit_main(self, n, vc):
        # main will always be stored as the first entry
        pass

    def visit_macro(self, n, vc):
        pass

    def generic_visit(self, n, vc):
        pass


class SketchVisitor(parsimonious.NodeVisitor):
    """Sketch visitor to save the view names and the variables in each"""
    def __init__(self, ast):
        self.variable_name = None
        self.view_name = None
        self.visit(ast)

    def visit_view_name(self, n, vc):
        pass

    def visit_var_definition(self, n, vc):
        pass

    def generic_visit(self, n, vc):
        pass
