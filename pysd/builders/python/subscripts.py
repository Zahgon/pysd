import warnings
from pathlib import Path
import numpy as np
from typing import List

from pysd.translators.structures.abstract_model import AbstractSubscriptRange
from pysd.py_backend.external import ExtSubscript


class SubscriptManager:
    """
    SubscriptManager object allows saving the subscripts included in the
    Section, searching for elements or keys and simplifying them.

    Parameters
    ----------
    abstrac_subscripts: list
        List of the AbstractSubscriptRanges comming from the AbstractModel.

    _root: pathlib.Path
        Path to the model file. Needed to read subscript ranges from
        Excel files.

    """
    def __init__(self, abstract_subscripts: List[AbstractSubscriptRange],
                 _root: Path):
        self._root = _root
        self._copied = []
        self.mapping = {}
        self.subscripts = abstract_subscripts
        self.elements = {}
        self.subranges = self._get_main_subscripts()
        self.subscript2num = self._get_subscript2num()

    @property
    def subscripts(self) -> dict:
        pass

    @subscripts.setter
    def subscripts(self, abstract_subscripts: List[AbstractSubscriptRange]):
        pass

    def _get_main_subscripts(self) -> dict:
        """
        Reutrns a dictionary with the main ranges as keys and their
        subranges as values.
        """
        pass

    def _get_subscript2num(self) -> dict:
        """
        Build a dictionary to return the numeric value or values of a
        subscript or subscript range.
        """
        pass

    def _find_subscript_name(self, element: str, avoid: List[str] = []) -> str:
        """
        Given a member of a subscript family, return the first key of
        which the member is within the value list.

        Parameters
        ----------
        element: str
            Subscript or subscriptrange name to find.
        avoid: list (optional)
            List of subscripts to avoid. Default is an empty list.

        Returns
        -------
        name: str
            The first key of which the member is within the value list
            in the subscripts dictionary.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     'Dim1': ['A', 'B', 'C'],
        ...     'Dim2': ['A', 'B', 'C', 'D']}
        >>> sm._find_subscript_name('D')
        'Dim2'
        >>> sm._find_subscript_name('B')
        'Dim1'
        >>> sm._find_subscript_name('B', avoid=['Dim1'])
        'Dim2'

        """
        pass

    def make_coord_dict(self, subs: List[str]) -> dict:
        """
        This is for assisting with the lookup of a particular element.

        Parameters
        ----------
        subs: list of strings
            Coordinates, either as names of dimensions, or positions within
            a dimension.

        Returns
        -------
        coordinates: dict
            Coordinates needed to access the xarray quantities we are
            interested in.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     'Dim1': ['A', 'B', 'C'],
        ...     'Dim2': ['A', 'B', 'C', 'D']}
        >>> sm.make_coord_dict(['Dim1', 'D'])
        {'Dim1': ['A', 'B', 'C'], 'Dim2': ['D']}
        >>> sm.make_coord_dict(['A'])
        {'Dim1': ['A']}
        >>> sm.make_coord_dict(['A', 'B'])
        {'Dim1': ['A'], 'Dim2': ['B']}
        >>> sm.make_coord_dict(['A', 'Dim1'])
        {'Dim2': ['A'], 'Dim1': ['A', 'B', 'C']}

        """
        pass

    def make_merge_list(self, subs_list: List[List[str]],
                        element: str = "") -> List[str]:
        """
        This is for assisting when building xrmerge. From a list of subscript
        lists returns the final subscript list after merging. Necessary when
        merging variables with subscripts comming from different definitions.

        Parameters
        ----------
        subs_list: list of lists of strings
            Coordinates, either as names of dimensions, or positions within
            a dimension.
        element: str (optional)
            Element name, if given it will be printed with any error or
            warning message. Default is "".

        Returns
        -------
        dims: list
            Final subscripts after merging.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {"upper": ["A", "B"], "all": ["A", "B", "C"]}
        >>> sm.make_merge_list([['A'], ['B']])
        ['upper']
        >>> sm.make_merge_list([['A'], ['B'], ['C']])
        ['all']
        >>> sm.make_merge_list([['upper'], ['C']])
        ['all']
        >>> sm.make_merge_list([['A'], ['C']])
        ['all']

        """
        pass

    def simplify_subscript_input(self, coords: dict,
                                 merge_subs: List[str] = None) -> tuple:
        """
        Simplifies the subscripts input to avoid printing the coordinates
        list when the _subscript_dict can be used. Makes model code more
        simple.

        Parameters
        ----------
        coords: dict
            Coordinates to write in the model file.

        merge_subs: list of strings or None (optional)
            List of the final subscript range of the Python array after
            merging with other objects. If None the merge_subs will be
            taken from coords. Default is None.

        Returns
        -------
        final_subs, coords: dict, str
            Final subscripts and the equations to generate the coord
            dicttionary in the model file.

        Examples
        --------
        >>> sm = SubscriptManager([], Path(''))
        >>> sm._subscripts = {
        ...     "dim": ["A", "B", "C"],
        ...     "dim2": ["A", "B", "C", "D"]}
        >>> sm.simplify_subscript_input({"dim": ["A", "B", "C"]})
        ({"dim": ["A", "B", "C"]}, "{'dim': _subscript_dict['dim']}"
        >>> sm.simplify_subscript_input({"dim": ["A", "B", "C"]}, ["dim2"])
        ({"dim2": ["A", "B", "C"]}, "{'dim2': _subscript_dict['dim']}"
        >>> sm.simplify_subscript_input({"dim": ["A", "B"]})
        ({"dim": ["A", "B"]}, "{'dim': ['A', 'B']}"

        """
        pass
