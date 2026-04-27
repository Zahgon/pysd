"""
The Element class allows parsing the LHS of a model equation.
Depending on the LHS value, either a SubscriptRange object or a Component
object will be returned. There are four components types:

- Component: Regular component, defined with '='.
- UnchangeableConstant: Unchangeable constant, defined with '=='.
- Data: Data component, defined with ':='
- Lookup: Lookup component, defined with '()'

Lookup components have their own parser for the RHS of the expression,
while the other 3 components share the same parser. The final result
from a parsed component can be exported to an AbstractComponent object
in order to build a model in other programming languages. Two more
element-like objects could be defined, which are only used for testing:

- Constraint: constraint for Reality check, defined with ':THE CONDITION:'
- TestInput: inputs for testing, defined with ':TESTÂ INPUT:'

"""
import re
from typing import Union, Tuple, List
import warnings

import parsimonious
import numpy as np

from ..structures.abstract_model import\
    AbstractData, AbstractLookup, AbstractComponent,\
    AbstractUnchangeableConstant, AbstractSubscriptRange,\
    AbstractConstraint, AbstractTestInput

from . import vensim_utils as vu
from .vensim_structures import structures, parsing_ops


class Element():
    """
    Element object allows parsing the LHS of the Vensim expressions.

    Parameters
    ----------
    equation: str
        Original equation in the Vensim file.

    units: str
        The units of the element with the limits, i.e., the content after
        the first '~' symbol.

    documentation: str
        The comment of the element, i.e., the content after the second
        '~' symbol.

    """
    def __init__(self, equation: str, units: str, documentation: str):
        self.equation = equation
        self.units, self.limits = self._parse_units(units)
        self.documentation = documentation

    def __str__(self):  # pragma: no cover
        return "Model element:\n\t%s\nunits: %s\ndocs: %s\n" % (
            self.equation, self.units, self.documentation)

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get element information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print element information to standard output."""
        pass

    def _parse_units(self, units_str: str) -> Tuple[str, tuple]:
        """Separate the limits from the units."""
        pass

    def parse(self) -> object:
        """
        Parse an Element object with parsimonious using the grammar
        given in 'parsing_grammars/element_object.peg' and the class
        ElementsComponentVisitor to visit the parsed expressions.

        Splits the LHS from the RHS of the equation. If the returned
        object is a SubscriptRange, no more parsing is needed.
        Otherwise, the RHS of the returned object (Component) should
        be parsed to get the AbstractSyntax Tree.

        Returns
        -------
        self.component: SubscriptRange or Component
            The subscript range definition object or component object.

        """
        pass


class ElementsComponentVisitor(parsimonious.NodeVisitor):
    """Visit model element definition to get the component object."""

    def __init__(self, ast):
        self.mapping = []
        self.subscripts = []
        self.subscripts_except = []
        self.subscripts_except_groups = []
        self.qargs = []
        self.name = None
        self.expression = None
        self.keyword = None
        self.visit(ast)

    def visit_subscript_definition(self, n, vc):
        pass

    def visit_lookup_definition(self, n, vc):
        pass

    def visit_unchangeable_constant(self, n, vc):
        pass

    def visit_component(self, n, vc):
        pass

    def visit_data_definition(self, n, vc):
        pass

    def visit_keyword(self, n, vc):
        pass

    def visit_imported_subscript(self, n, vc):
        pass

    def visit_string(self, n, vc):
        pass

    def visit_subscript_copy(self, n, vc):
        pass

    def visit_subscript_mapping(self, n, vc):
        pass

    def visit_subscript_range(self, n, vc):
        pass

    def visit_constraint_definition(self, n, vc):
        pass

    def visit_test_inputs_definition(self, n, vc):
        pass

    def visit_name(self, n, vc):
        pass

    def visit_subscript(self, n, vc):
        pass

    def visit_subscript_except(self, n, vc):
        pass

    def visit_subscript_except_group(self, n, vc):
        pass

    def visit_expression(self, n, vc):
        pass

    def generic_visit(self, n, vc):
        pass


class SubscriptRange():
    """
    Subscript range definition, defined by ":" or "<->" in Vensim.
    """

    def __init__(self, name: str, definition: Union[List[str], str, dict],
                 mapping: List[str] = []):
        self.name = name
        self.definition = definition
        self.mapping = mapping

    def __str__(self):  # pragma: no cover
        return "\nSubscript range definition:  %s\n\t%s\n" % (
            self.name,
            "%s <- %s" % (self.definition, self.mapping)
            if self.mapping else self.definition)

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
        Instantiates an AbstractSubscriptRange object used for building.
        This method is automatically called by the Sections's
        get_abstract_section method.

        Returns
        -------
        AbstractSubscriptRange: AbstractSubscriptRange
          AbstractSubscriptRange object that can be used for building
          the model in another programming language.

        """
        pass


class GenericComponent():
    """
    Class to define common methods for Components, Constraints and TestInputs.
    """
    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        self.name = name
        self.subscripts = subscripts
        self.expression = expression
        self.lookup = False
        self.ast = None
        self._kind = None

    def __str__(self):  # pragma: no cover
        text = "\n%s definition: %s" % (self._kind, self.name)
        text += "\nSubscrips: %s" % repr(self.subscripts[0])\
            if self.subscripts[0] else ""
        text += "  EXCEPT  %s" % repr(self.subscripts[1])\
            if self.subscripts[1] else ""
        text += "\n\t%s" % self._expression
        return text

    @property
    def _expression(self):  # pragma: no cover
        pass

    @property
    def _verbose(self) -> str:  # pragma: no cover
        """Get component information."""
        pass

    @property
    def verbose(self):  # pragma: no cover
        """Print component information to standard output."""
        pass


class Component(GenericComponent):
    """
    Model component defined by "name = expr" in Vensim.

    Parameters
    ----------
    name: str
        The original name of the component.

    subscripts: tuple
        Tuple of length two with the list of subscripts
        in the variable definition as first argument and the list of
        subscripts that appears after the :EXCEPT: keyword (if used) as
        the second argument.

    expression: str
        The RHS of the element, expression to parse.

    """
    _kind = "Model component"

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        super().__init__(name, subscripts, expression)

    def parse(self) -> None:
        """
        Parse Component object with parsimonious using the grammar given
        in 'parsing_grammars/components.peg' and the class EquationVisitor
        to visit the RHS of the expressions.

        """
        pass

    def get_abstract_component(self) -> Union[AbstractComponent,
                                              AbstractLookup]:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractComponent or AbstractLookup
          Abstract Component object that can be used for building
          the model in another language. If the component equations
          include external lookups (GET XLS/DIRECT LOOKUPS), an
          AbstractLookup class will be used.

        """
        pass


class UnchangeableConstant(Component):
    """
    Unchangeable constant defined by "name == expr" in Vensim.
    This class inherits from the Component class.

    Parameters
    ----------
    name: str
        The original name of the component.

    subscripts: tuple
        Tuple of length two with the list of subscripts
        in the variable definition as first argument and the list of
        subscripts that appears after the :EXCEPT: keyword (if used) as
        second argument.

    expression: str
        The RHS of the element, expression to parse.

    """
    _kind = "Unchangeable constant component"

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        super().__init__(name, subscripts, expression)

    def get_abstract_component(self) -> AbstractUnchangeableConstant:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractUnchangeableConstant
          Abstract Component object that can be used for building
          the model in another language.

        """
        pass


class Lookup(Component):
    """
    Lookup component, defined by "name(expr)" in Vensim.
    This class inherits from the Component class.

    Parameters
    ----------
    name: str
        The original name of the component.

    subscripts: tuple
        Tuple of length two with the list of subscripts in the variable
        definition as first argument and the list of subscripts that appear
        after the :EXCEPT: keyword (if used) as second argument.

    expression: str
        The RHS of the element, expression to parse.

    """
    _kind = "Lookup component"

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        super().__init__(name, subscripts, expression)

    def parse(self) -> None:
        """
        Parse component object with parsimonious using the grammar given
        in 'parsing_grammars/lookups.peg' and the class LookupsVisitor
        to visit the RHS of the expressions.
        """
        pass

    def get_abstract_component(self) -> AbstractLookup:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractLookup
          Abstract Component object that may be used for building
          the model in another language.

        """
        pass


class Data(Component):
    """
    Data component, defined by "name := expr" in Vensim.
    This class inherits from the Component class.

    Parameters
    ----------
    name: str
        The original name of the component.

    subscripts: tuple
        Tuple of length two with the list of subscripts in the variable
        definition as first argument and the list of subscripts that appear
        after the :EXCEPT: keyword (if used) as second argument.

    keyword: str
        The keyword used before the ":=" symbol. The following values are
        possible:  'interpolate', 'raw', 'hold_backward' and 'look_forward'.

    expression: str
        The RHS of the element, expression to parse.

    """
    _kind = "Data component"

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 keyword: str, expression: str):
        super().__init__(name, subscripts, expression)
        self.keyword = keyword

    def __str__(self):  # pragma: no cover
        text = "\n%s definition: %s" % (self._kind, self.name)
        text += "\nSubscrips: %s" % repr(self.subscripts[0])\
            if self.subscripts[0] else ""
        text += "  EXCEPT  %s" % repr(self.subscripts[1])\
            if self.subscripts[1] else ""
        text += "\nKeyword: %s" % self.keyword if self.keyword else ""
        text += "\n\t%s" % self._expression
        return text

    def parse(self) -> None:
        """
        Parse component object with parsimonious using the grammar given
        in 'parsing_grammars/components.peg' and the class EquationVisitor
        to visit the RHS of the expressions.

        If the expression is None, the data will be read from a VDF file in
        Vensim.

        """
        pass

    def get_abstract_component(self) -> AbstractData:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractData
          Abstract Component object that can be used for building
          the model in another language.

        """
        pass


class Constraint(GenericComponent):
    """
    Constraint definition, defined by :THE CONDITION: in Vensim.
    """

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        super().__init__(name, subscripts, expression)

    def __str__(self):  # pragma: no cover
        return "\nConstraint definition:  %s\n\t%s\n\t%s\n" % (
            self.name,
            self.subscripts,
            "%s" % (self.expression)
            )

    def parse(self):
        # It doesn't really parse anything, it assigns the matched expression
        # to the ast attribute
        pass

    def get_abstract_component(self) -> AbstractConstraint:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractConstraint
          Abstract Component object that can be used for building
          the model in another language.

        """
        pass


class TestInput(GenericComponent):
    """
    Test Inputs definition, defined by :TEST INPUT: in Vensim.
    """

    def __init__(self, name: str, subscripts: Tuple[list, list],
                 expression: str):
        super().__init__(name, subscripts, expression)

    def __str__(self):  # pragma: no cover
        return "\nTest Inputs definition:  %s\n\t%s\n\t%s\n" % (
            self.name,
            self.subscripts,
            "%s" % (self.expression)
            )

    def parse(self):
        # It doesn't really parse anything, it assigns the matched expression
        # to the ast attribute
        pass

    def get_abstract_component(self) -> AbstractTestInput:
        """
        Get Abstract Component used for building. This method is
        automatically called by Sections's get_abstract_section method.

        Returns
        -------
        AbstractComponent: AbstractTestInput
          Abstract Component object that can be used for building
          the model in another language.

        """
        pass


class LookupsVisitor(parsimonious.NodeVisitor):
    """Visit the elements of a lookups to get the AST"""
    def __init__(self, ast):
        self.translation = None
        self.qargs = []
        self.visit(ast)

    def visit_limits(self, n, vc):
        pass

    def visit_regularLookup(self, n, vc):
        pass

    def visit_excelLookup(self, n, vc):
        pass

    def visit_string(self, n, vc):
        pass

    def generic_visit(self, n, vc):
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

    def visit_final_expr(self, n, vc):
        # expressions with logical binary operators (:AND:, :OR:)
        pass

    def visit_logic_expr(self, n, vc):
        # expressions with logical unitary operators (:NOT:)
        pass

    def visit_comp_expr(self, n, vc):
        # expressions with comparisons (=, <>, <, <=, >, >=)
        pass

    def visit_add_expr(self, n, vc):
        # expressions with additions (+, -)
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

    def visit_reference(self, n, vc):
        pass

    def visit_limits(self, n, vc):
        pass

    def visit_lookup_with_def(self, n, vc):
        pass

    def visit_array(self, n, vc):
        pass

    def visit_tabbed_array_call(self, n, vc):
        pass

    def visit_array_tabbed(self, n, vc):
        pass

    def visit_subscript_list(self, n, vc):
        pass

    def visit_name(self, n, vc):
        pass

    def visit_expr(self, n, vc):
        pass

    def visit_string(self, n, vc):
        pass

    def visit_arguments(self, n, vc):
        pass

    def visit_parens(self, n, vc):
        pass

    def visit__(self, n, vc):
        # handles whitespace characters
        pass

    def visit_nan(self, n, vc):
        pass

    def generic_visit(self, n, vc):
        pass

    def add_element(self, element):
        pass
