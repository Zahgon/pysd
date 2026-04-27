"""
The Section class allows parsing a model section into Elements. The
final result can be exported to an AbstractSection class in order to
build a model in other language. A section could be either the main model
(without the macros), or a macro definition (not supported yet for Xmile).
"""
from typing import List, Union
from lxml import etree
from pathlib import Path

from ..structures.abstract_model import AbstractSection

from .xmile_element import ControlElement, SubscriptRange, Aux, Flow, Gf, Stock


class Section():
    """
    Section object allows parsing the elements of that section.

    Parameters
    ----------
    name: str
        Section name. '__main__' for the main section or the macro name.

    path: pathlib.Path
        Section path. It should be the model name for main  section and
        the clean macro name for a macro.

    section_type: str ('main' or 'macro')
        The section type.

    params: list
        List of params that takes the section. In the case of main
        section it will be an empty list.

    returns: list
        List of variables that returns the section. In the case of main
        section it will be an empty list.

    content_root: etree._Element
        Section parsed tree content.

    namespace: str
        The namespace of the section given after parsing its content
        with etree.

    split: bool
        If split is True the created section will split the variables
        depending on the views_dict.

    views_dict: dict
        The dictionary of the views. Giving the variables classified at
        any level in order to split them by files.

    """
    _control_vars = ["initial_time", "final_time", "time_step", "saveper"]

    def __init__(self, name: str, path: Path, section_type: str,
                 params: List[str], returns: List[str],
                 content_root: etree._Element, namespace: str, split: bool,
                 views_dict: Union[dict, None]):
        self.name = name
        self.path = path
        self.type = section_type
        self.params = params
        self.returns = returns
        self.content = content_root
        self.ns = {"ns": namespace}
        self.split = split
        self.views_dict = views_dict
        self.elements = None
        self.behaviors = {}

    def __str__(self):  # pragma: no cover
        return "\nSection: %s\n" % self.name

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get section information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print section information to standard output."""
        pass

    def parse(self, parse_all: bool = True) -> None:
        """
        Parse section object. The subscripts of the section will be added
        to self subscripts. The variables defined as Flows, Auxiliary, Gf,
        and Stock will be converted in XmileElements. The control variables,
        if the section is __main__, will be converted to a ControlElement.

        Parameters
        ----------
        parse_all: bool (optional)
            If True then the created VensimElement objects will be
            automatically parsed. Otherwise, this objects will only be
            added to self.elements but not parser. Default is True.

        """
        pass

    def _parse_behavior(self) -> List[SubscriptRange]:
        """Parse the behavior the section."""
        pass

    def _parse_subscripts(self) -> List[SubscriptRange]:
        """Parse the subscripts of the section."""
        pass

    def _parse_components(self) -> List[Union[Flow, Aux, Gf, Stock]]:
        """
        Parse model components. Four groups defined:
        Aux: auxiliary variables
        Flow: flows
        Gf: lookups
        Stock: integs

        """
        pass

    def _parse_control_vars(self) -> List[ControlElement]:
        """Parse control vars and rename them with Vensim standard."""
        pass

    def get_abstract_section(self) -> AbstractSection:
        """
        Get Abstract Section used for building. This, method should be
        called after parsing the section (self.parse). This method is
        automatically called by Model's get_abstract_model and
        automatically generates the AbstractSubscript ranges and merge
        the components in elements calling also the get_abstract_components
        method from each model component.

        Returns
        -------
        AbstractSection: AbstractSection
          Abstract Section object that can be used for building the model
          in another language.

        """
        pass
