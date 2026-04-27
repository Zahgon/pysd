"""
The Element class child classes alow parsing the expressions of a
given model element. There are four tipes of elements:

- Auxiliars (Aux class): Auxiliary elements, defined with <aux>.
- Flows (Flow class): Flow elements, defined with <flow>.
- Gfs (Gf class): Lookup elements, defined with <gf>.
- Stocks (Stock class): Data component, defined with <stock>

Moreover, a fith type element is defined ControlElement, which allows parsing
the values of the model control variables (time step, initialtime, final time).

The final result from a parsed element can be exported to an
AbstractElement object in order to build a model in other language.
"""
import re
from typing import Tuple, Union, List
from lxml import etree
import parsimonious
import numpy as np

from ..structures.abstract_model import\
    AbstractElement, AbstractControlElement,\
    AbstractLookup, AbstractComponent, AbstractSubscriptRange

from ..structures.abstract_expressions import\
    AbstractSyntax, CallStructure, ReferenceStructure

from . import xmile_utils as vu
from .xmile_structures import structures, parsing_ops


class Element():
    """
    Element class. This class provides the shared methods for its
    children: Aux, Flow, Gf, Stock, and ControlElement.

    Parameters
    ----------
    node: etree._Element
        The element node content.

    ns: dict
        The namespace of the section.

    subscripts: dict
        The subscript dictionary of the section, necessary to parse
        some subscripted elements.

    """
    _interp_methods = {
        "continuous": "interpolate",
        "extrapolate": "extrapolate",
        "discrete": "hold_backward"
    }

    _kind = "Element"

    def __init__(self, node: etree._Element, ns: dict, subscripts):
        self.node = node
        self.ns = ns
        self.name = node.attrib["name"].replace("\\n", " ")
        self.units = self._get_xpath_text(node, "ns:units") or ""
        self.documentation = self._get_xpath_text(node, "ns:doc") or ""
        self.limits = (None, None)
        self.components = []
        self.subscripts = subscripts

    def __str__(self):  # pragma: no cover
        text = "\n%s definition: %s" % (self._kind, self.name)
        text += "\nSubscrips: %s" % repr(self.subscripts)\
            if self.subscripts else ""
        text += "\n\t%s" % self._expression
        return text

    @property
    def _expression(self):  # pragma: no cover
        pass

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get element information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print element information to standard output."""
        pass

    def _get_xpath_text(self, node: etree._Element,
                        xpath: str) -> Union[str, None]:
        """Safe access of occassionally missing text"""
        pass

    def _get_xpath_attrib(self, node: etree._Element,
                          xpath: str, attrib: str) -> Union[str, None]:
        """Safe access of occassionally missing attributes"""
        pass

    def _get_limits(self) -> Tuple[Union[None, str], Union[None, str]]:
        """Get the limits of the element"""
        pass

    def _get_non_negative(self, behavior):
        pass

    def _parse_lookup_xml_node(self, node: etree._Element) -> AbstractSyntax:
        """
        Parse lookup definition

        Returns
        -------
        AST: AbstractSyntax

        """
        pass

    def parse(self, behaviors: dict) -> None:
        """
        Parse all the components of an element

        Parameters
        ----------
        behaviors: dict
            Dictionary with keys 'non_negative_flow' and 'non_negative_stock'
            and boolean values defining the global behavior for the
            stocks and flows.

        Returns
        -------
        None

        """
        pass

    def _smile_parser(self, expression: str) -> AbstractSyntax:
        """
        Parse expression with parsimonious.

        Returns
        -------
        AST: AbstractSyntax

        """
        pass

    def _get_empty_abstract_element(self) -> AbstractElement:
        """
        Get empty Abstract used for building

        Returns
        -------
        AbstractElement
        """
        pass


class Aux(Element):
    """
    Auxiliary variable defined by <aux> in Xmile.

    Parameters
    ----------
    node: etree._Element
        The element node content.

    ns: dict
        The namespace of the section.

    subscripts: dict
        The subscript dictionary of the section, necessary to parse
        some subscripted elements.

    """
    _kind = "Flow"

    def __init__(self, node, ns, subscripts):
        super().__init__(node, ns, subscripts)
        self.limits = self._get_limits()

    def _parse_component(self, node: etree._Element,
                         behaviors: dict) -> List[AbstractSyntax]:
        """
        Parse one Aux component

        Returns
        -------
        AST: AbstractSyntax

        """
        pass

    def get_abstract_element(self) -> AbstractElement:
        """
        Get Abstract Element used for building. This method is
        automatically called by Sections's get_abstract_section.

        Returns
        -------
        AbstractElement: AbstractElement
          Abstract Element object that can be used for building
          the model in another language. It contains a list of
          AbstractComponents with the Abstract Syntax Tree of each of
          the expressions.

        """
        pass


class Flow(Aux):
    """
    Flow defined by <flow> in Xmile.

    Parameters
    ----------
    node: etree._Element
        The element node content.

    ns: dict
        The namespace of the section.

    subscripts: dict
        The subscript dictionary of the section, necessary to parse
        some subscripted elements.

    """
    _kind = "Flow"

    def __init__(self, node, ns, subscripts):
        super().__init__(node, ns, subscripts)

    def _parse_component(self, node: etree._Element,
                         behaviors: dict) -> List[AbstractSyntax]:
        """
        Parse one Flow component

        Returns
        -------
        AST: AbstractSyntax

        """
        pass


class Gf(Element):
    """
    Gf variable (lookup) defined by <gf> in Xmile.

    Parameters
    ----------
    node: etree._Element
        The element node content.

    ns: dict
        The namespace of the section.

    subscripts: dict
        The subscript dictionary of the section, necessary to parse
        some subscripted elements.

    """
    _kind = "Gf component"

    def __init__(self, node, ns, subscripts):
        super().__init__(node, ns, subscripts)
        self.limits = self.get_limits()

    def get_limits(self) -> Tuple[Union[None, str], Union[None, str]]:
        """Get the limits of the Gf element"""
        pass

    def _parse_component(self, node: etree._Element,
                         behaviors: dict) -> AbstractSyntax:
        """
        Parse one Gf component

        Returns
        -------
        AST: AbstractSyntax

        """
        pass

    def get_abstract_element(self) -> AbstractElement:
        """
        Get Abstract Element used for building. This method is
        automatically called by Sections's get_abstract_section.

        Returns
        -------
        AbstractElement: AbstractElement
          Abstract Element object that can be used for building
          the model in another language. It contains a list of
          AbstractComponents with the Abstract Syntax Tree of each of
          the expressions.

        """
        pass


class Stock(Element):
    """
    Stock variable defined by <stock> in Xmile.

    Parameters
    ----------
    node: etree._Element
        The element node content.

    ns: dict
        The namespace of the section.

    subscripts: dict
        The subscript dictionary of the section, necessary to parse
        some subscripted elements.

    """

    _kind = "Stock component"

    def __init__(self, node, ns, subscripts):
        super().__init__(node, ns, subscripts)
        self.limits = self._get_limits()

    def _parse_component(self, node, behaviors: dict) -> AbstractSyntax:
        """
        Parse one Stock component

        Returns
        -------
        AST: AbstractSyntax

        """
        pass

    def get_abstract_element(self) -> AbstractElement:
        """
        Get Abstract Element used for building. This method is
        automatically called by Sections's get_abstract_section.

        Returns
        -------
        AbstractElement: AbstractElement
          Abstract Element object that can be used for building
          the model in another language. It contains a list of
          AbstractComponents with the Abstract Syntax Tree of each of
          the expressions.

        """
        pass


class ControlElement(Element):
    """Control variable (lookup)"""
    _kind = "Control variable"

    def __init__(self, name, units, documentation, eqn):
        self.name = name
        self.units = units
        self.documentation = documentation
        self.limits = (None, None)
        self.eqn = eqn

    def parse(self, behaviors: dict) -> None:
        """
        Parse control elment.

        Parameters
        ----------
        behaviors: dict
            Dictionary with keys 'non_negative_flow' and 'non_negative_stock'
            and boolean values defining the global behavior for the
            stocks and flows.

        Returns
        -------
        None

        """
        pass

    def get_abstract_element(self) -> AbstractElement:
        """
        Get Abstract Element used for building. This method is
        automatically called by Sections's get_abstract_section.

        Returns
        -------
        AbstractElement: AbstractElement
          Abstract Element object that can be used for building
          the model in another language. It contains an AbstractComponent
          with the Abstract Syntax Tree of the expression.

        """
        pass


class SubscriptRange():
    """Subscript range definition."""

    def __init__(self, name: str, definition: List[str],
                 mapping: List[str] = []):
        self.name = name
        self.definition = definition
        self.mapping = mapping

    def __str__(self):  # pragma: no cover
        return "\nSubscript range definition:  %s\n\t%s\n" % (
            self.name,
            self.definition)

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get subscript range information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print subscript range information to standard output."""
        pass

    def get_abstract_subscript_range(self) -> AbstractSubscriptRange:
        """
        Get Abstract Subscript Range used for building. This method is
        automatically called by Sections's get_abstract_section.

        Returns
        -------
        AbstractSubscriptRange: AbstractSubscriptRange
          Abstract Subscript Range object that can be used for building
          the model in another language.

        """
        pass


class EquationVisitor(parsimonious.NodeVisitor):
    """Visit the elements of a equation to get the AST"""
    def __init__(self, ast):
        self.translation = None
        self.elements = {}
        self.subs = None  # the subscripts if given
        self.negatives = set()
        self.visit(ast)

    def visit_expr_type(self, n, vc):
        pass

    def visit_logic2_expr(self, n, vc):
        # expressions with logical binary operators (and, or)
        pass

    def visit_logic_expr(self, n, vc):
        # expressions with logical unitary operators (not)
        pass

    def visit_comp_expr(self, n, vc):
        # expressions with comparisons (=, <>, <, <=, >, >=)
        pass

    def visit_add_expr(self, n, vc):
        # expressions with additions (+, -)
        pass

    def visit_mod_expr(self, n, vc):
        # modulo expressions (mod)
        pass

    def visit_prod_expr(self, n, vc):
        # expressions with products (*, /)
        pass

    def visit_exp_expr(self, n, vc):
        # expressions with exponentials (^)
        pass

    def visit_neg_expr(self, n, vc):
        pass

    def visit_call(self, n, vc):
        pass

    def visit_conditional_statement(self, n, vc):
        pass

    def visit_reference(self, n, vc):
        pass

    def visit_array(self, n, vc):
        pass

    def visit_subscript_list(self, n, vc):
        pass

    def visit_name(self, n, vc):
        pass

    def visit_expr(self, n, vc):
        pass

    def visit_arguments(self, n, vc):
        pass

    def visit_parens(self, n, vc):
        pass

    def visit__(self, n, vc):
        # handles whitespace characters
        pass

    def generic_visit(self, n, vc):
        pass

    def add_element(self, element):
        pass
