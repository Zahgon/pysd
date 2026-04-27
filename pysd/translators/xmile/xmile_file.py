"""
The XmileFile class allows reading the original Xmile model file and
parsing it into Section elements. The final result can be exported to an
AbstractModel class in order to build a model in another programming language.
"""
from typing import Union
from pathlib import Path
from lxml import etree

from ..structures.abstract_model import AbstractModel

from .xmile_section import Section
from .xmile_utils import supported_extensions


class XmileFile():
    """
    The XmileFile class allows parsing an Xmile file.
    When the object is created, the model file is automatically opened
    and parsed with lxml.etree.

    Parameters
    ----------
    xmile_path: str or pathlib.Path
        Path to the Xmile model.

    """
    def __init__(self, xmile_path: Union[str, Path]):
        self.xmile_path = Path(xmile_path)
        self.root_path = self.xmile_path.parent
        self.xmile_root = self._get_root()
        self.ns = self.xmile_root.nsmap[None]  # namespace of the xmile
        self.view_elements = None

    def __str__(self):  # pragma: no cover
        return "\nXmile model file, loaded from:\n\t%s\n" % self.xmile_path

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get model information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print model information to standard output."""
        pass

    def _get_root(self) -> etree._Element:
        """
        Read an Xmile file and assign its content to self.model_text

        Returns
        -------
        lxml.etree._Element: parsed xml object

        """
        pass

    def parse(self, parse_all: bool = True) -> None:
        """
        Create a XmileSection object from the model content and parse it.
        As macros are currently not supported, all models will
        have a single section. This function should split the macros in
        independent sections in the future.

        Parameters
        ----------
        parse_all: bool (optional)
            If True, the created XmileSection objects will be
            automatically parsed. Otherwise, these objects will only be
            added to self.sections but not parsed. Default is True.

        """
        pass

    def get_abstract_model(self) -> AbstractModel:
        """
        Get Abstract Model used for building. This, method should be
        called after parsing the model (self.parse). This automatically
        calls the get_abstract_section method from the model sections.

        Returns
        -------
        AbstractModel: AbstractModel
          Abstract Model object that can be used for building the model
          in another language.

        """
        pass
