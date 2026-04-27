"""
The translation from Abstract Syntax Tree to Python happens in both ways.
The outer expression is visited with its builder, which will split its
arguments and visit them with their respective builders. Once the lowest
level is reached, it will be translated into Python returning a BuildAST
object, this object will include the python expression, its subscripts,
its calls to other and its arithmetic order (see Build AST for more info).
BuildAST will be returned for each visited argument from the lower
lever to the top level, giving the final expression.
"""
import warnings
from dataclasses import dataclass
from typing import Union

import numpy as np
from pysd.py_backend.utils import compute_shape

from pysd.translators.structures.abstract_expressions import\
    AbstractSyntax, AllocateAvailableStructure, AllocateByPriorityStructure, \
    ArithmeticStructure, CallStructure, DataStructure, DelayFixedStructure, \
    DelayStructure, DelayNStructure, ForecastStructure, GameStructure, \
    GetConstantsStructure, GetDataStructure, GetLookupsStructure, \
    InitialStructure, InlineLookupsStructure, IntegStructure, \
    LogicStructure, LookupsStructure, ReferenceStructure, \
    SampleIfTrueStructure, SmoothNStructure, SmoothStructure, \
    SubscriptsReferenceStructure, TrendStructure

from .python_functions import functionspace
from .subscripts import SubscriptManager


@dataclass
class BuildAST:
    """
    Python expression holder.

    Parameters
    ----------
    expression: str
        The Python expression.
    calls: dict
        The calls to other variables for the dependencies dictionary.
    subscripts: dict
        The subscripts dict of the expression.
    order: int
        Arithmetic order of the expression. The arithmetic order depends
        on the last arithmetic operation. If the expression is a number,
        a call to a function, or is between parenthesis; its order will
        be 0. If the expression its an exponential of two terms its order
        will be 1. If the expression is a product or division its order
        will be 2. If the expression is a sum or substraction its order
        will be 3. If the expression is a logical comparison its order
        will be 4.

    """
    expression: str
    calls: dict
    subscripts: dict
    order: int

    def __str__(self) -> str:
        # makes easier building
        return self.expression

    def reshape(self, subscripts: SubscriptManager,
                final_subscripts: dict,
                final_element: bool = False) -> None:
        """
        Reshape the object to the desired subscripts. It will modify the
        expression and lower the order if it is not 0.

        Parameters
        ----------
        subscripts: SubscriptManager
            The subscripts of the section.
        final_subscripts: dict
            The desired final subscripts.
        final_element: bool (optional)
            If True the array will be reshaped with the final subscripts
            to have the shame shape. Otherwise, a length 1 dimension
            will be included in the position to allow arithmetic
            operations with other arrays. Default is False.

        """
        pass

    def lower_order(self, new_order: int) -> None:
        """
        Lower the order to maintain the correct order in arithmetic
        operations. If the requested order is smaller than the current
        order parenthesis will be added to the expression to lower its
        order to 0.

        Parameters
        ----------
        new_order: int
            The required new order of the expression. If 0 it will be
            assumed that the expression will be passed as an argument
            of a function and therefore no operations will be done. If
            order 0 is required, a negative value can be used for
            new_order.

        """
        pass


class StructureBuilder:
    """
    Main builder for Abstract Syntax Tree structures. All the builders
    are children of this class, which allows them inheriting the methods.
    """
    def __init__(self, value: object, component: object):
        # component typing should be ComponentBuilder, but importing it
        # for typing would create a circular dependency :S
        self.value = value
        self.arguments = {}
        self.component = component
        self.element = component.element
        self.section = component.section
        self.def_subs = component.subscripts_dict

    @staticmethod
    def join_calls(arguments: dict) -> dict:
        """
        Merge the calls of the arguments.

        Parameters
        ----------
        arguments: dict
            The dictionary of arguments. The keys should br strings of
            ordered integer numbers starting from 0.

        Returns
        -------
        calls: dict
            The merged dictionary of calls.

        """
        pass

    def reorder(self, arguments: dict, force: bool = None) -> dict:
        """
        Reorder the subscripts of the arguments to make them match.

        Parameters
        ----------
        arguments: dict
            The dictionary of arguments. The keys should br strings of
            ordered integer numbers starting from 0.
        force: 'component', 'equal', or None (optional)
            If force is 'component' it will force the arguments to have
            the subscripts of the component definition. If force is
            'equal' it will force all the arguments to have the same
            subscripts, includying the floats. If force is None, it
            will only modify the shape of the arrays adding length 1
            dimensions to allow operation between different shape arrays.
            Default is None.

        Returns
        -------
        final_subscripts: dict
            The final_subscripts after reordering all the elements.

        """
        pass

    def get_final_subscripts(self, arguments: dict) -> dict:
        """
        Get the final subscripts of a combination of arguments.

        Parameters
        ----------
        arguments: dict
            The dictionary of arguments. The keys should br strings of
            ordered integer numbers starting from 0.

        Returns
        -------
        final_subscripts: dict
            The final_subscripts of combining all the elements.

        """
        pass

    def _compute_final_subscripts(self, subscripts_list: list) -> dict:
        """
        Compute final subscripts from a list of subscript dictionaries.

        Parameters
        ----------
        subscript_list: list of dicts
            List of subscript dictionaries.

        """
        pass

    def update_object_subscripts(self, name: str,
                                 component_final_subs: dict) -> None:
        """
        Update the object subscripts. Needed for those objects that
        use 'add' method to load several components at once and mixed
        definitions are used.

        Parameters
        ----------
        name: str
            The name of the object in the objects dictionary from the
            element.
        component_final_subs: dict
            The subscripts of the component but with the element
            subscript ranges as keys. This can differ from the component
            subscripts when the component is defined with subranges of
            the final subscript ranges.

        """
        pass


class OperationBuilder(StructureBuilder):
    """Builder for arithmetic and logical operations."""
    _operators_build = {
        "^": ("%(left)s**%(right)s", None, 1),
        "*": ("%(left)s*%(right)s", None, 2),
        "/": ("%(left)s/%(right)s", None, 2),
        "+": ("%(left)s + %(right)s", None, 3),
        "-": ("%(left)s - %(right)s", None, 3),
        "=": ("%(left)s == %(right)s", None, 4),
        "<>": ("%(left)s != %(right)s", None, 4),
        ">=": ("%(left)s >= %(right)s", None, 4),
        ">": ("%(left)s > %(right)s", None, 4),
        "<=": ("%(left)s <= %(right)s", None, 4),
        "<": ("%(left)s < %(right)s", None, 4),
        ":NOT:": ("np.logical_not(%s)", ("numpy",), 0),
        ":AND:": ("np.logical_and(%(left)s, %(right)s)", ("numpy",), 0),
        ":OR:": ("np.logical_or(%(left)s, %(right)s)", ("numpy",), 0),
        "negative": ("-%s", None, 3),
    }

    def __init__(self, operation: Union[ArithmeticStructure, LogicStructure],
                 component: object):
        super().__init__(None, component)
        self.operators = operation.operators.copy()
        self.arguments = {
            str(i): arg for i, arg in enumerate(operation.arguments)}

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class GameBuilder(StructureBuilder):
    """Builder for GAME expressions."""
    def __init__(self, game_str: GameStructure, component: object):
        super().__init__(None, component)
        self.arguments = {"expr": game_str.expression}

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class CallBuilder(StructureBuilder):
    """Builder for calls to functions, macros and lookups."""
    def __init__(self, call_str: CallStructure, component: object):
        super().__init__(None, component)
        function_name = call_str.function.reference
        self.arguments = {
            str(i): arg for i, arg in enumerate(call_str.arguments)}

        if function_name in self.section.macrospace:
            # Build macro
            self.macro_name = function_name
            self.build = self.build_macro_call
        elif function_name in self.section.namespace.cleanspace:
            # Build lookupcall
            self.arguments["function"] = call_str.function
            self.build = self.build_lookups_call
        elif function_name in functionspace:
            # Build direct function
            self.function = function_name
            self.build = self.build_function_call
        elif function_name == "a_function_of":
            # Build incomplete function
            self.build = self.build_incomplete_call
        else:
            # Build missing function
            self.function = function_name
            self.build = self.build_not_implemented

    def build_not_implemented(self, arguments: dict) -> BuildAST:
        """
        Build method for not implemented function calls.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def build_incomplete_call(self, arguments: dict) -> BuildAST:
        """
        Build method for incomplete function calls.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def build_macro_call(self, arguments: dict) -> BuildAST:
        """
        Build method for macro calls.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def build_lookups_call(self, arguments: dict) -> BuildAST:
        """
        Build method for loookups calls.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def build_function_call(self, arguments: dict) -> BuildAST:
        """
        Build method for function calls.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def _compute_axis(self, subscripts: dict) -> tuple:
        """
        Compute the axis to apply a vectorial function.

        Parameters
        ----------
        subscripts: dict
            The final_subscripts after reordering all the elements.

        Returns
        -------
        coords: dict
            The final coordinates after executing the vectorial function
        axis: list
            The list of dimensions to apply the function. Uses the
            dimensions with "!" at the end.

        """
        pass


class AllocateAvailableBuilder(StructureBuilder):
    """Builder for allocate_available function."""

    def __init__(self, allocate_str: AllocateAvailableStructure,
                 component: object):
        super().__init__(None, component)

        pp = allocate_str.pp
        pp_sub = self.section.subscripts.elements[pp.reference][-1:]
        pp.subscripts.subscripts = pp.subscripts.subscripts[:-1] + pp_sub
        self.arguments = {
            "request": allocate_str.request,
            "pp": pp,
            "avail": allocate_str.avail
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class AllocateByPriorityBuilder(StructureBuilder):
    """Builder for allocate_by_priority function."""

    def __init__(self, allocate_str: AllocateByPriorityStructure,
                 component: object):
        super().__init__(None, component)
        self.arguments = {
            "request": allocate_str.request,
            "priority": allocate_str.priority,
            "width": allocate_str.width,
            "supply": allocate_str.supply
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class ExtLookupBuilder(StructureBuilder):
    """Builder for External Lookups."""
    def __init__(self, getlookup_str: GetLookupsStructure,  component: object):
        super().__init__(None, component)
        self.file = getlookup_str.file
        self.tab = getlookup_str.tab
        self.x_row_or_col = getlookup_str.x_row_or_col
        self.cell = getlookup_str.cell
        self.arguments = {}

    def build(self, arguments: dict) -> Union[BuildAST, None]:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST or None
            The built object, unless the component has been added to an
            existing object using the 'add' method.

        """
        pass


class ExtDataBuilder(StructureBuilder):
    """Builder for External Data."""
    def __init__(self, getdata_str: GetDataStructure,  component: object):
        super().__init__(None, component)
        self.file = getdata_str.file
        self.tab = getdata_str.tab
        self.time_row_or_col = getdata_str.time_row_or_col
        self.cell = getdata_str.cell
        self.keyword = component.keyword
        self.arguments = {}

    def build(self, arguments: dict) -> Union[BuildAST, None]:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST or None
            The built object, unless the component has been added to an
            existing object using the 'add' method.

        """
        pass


class ExtConstantBuilder(StructureBuilder):
    """Builder for External Constants."""
    def __init__(self, getconstant_str: GetConstantsStructure,
                 component: object):
        super().__init__(None, component)
        self.file = getconstant_str.file
        self.tab = getconstant_str.tab
        self.cell = getconstant_str.cell
        self.arguments = {}

    def build(self, arguments: dict) -> Union[BuildAST, None]:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST or None
            The built object, unless the component has been added to an
            existing object using the 'add' method.

        """
        pass


class TabDataBuilder(StructureBuilder):
    """Builder for empty DATA expressions."""
    def __init__(self, data_str: DataStructure,  component: object):
        super().__init__(None, component)
        self.keyword = component.keyword
        self.arguments = {}

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class InitialBuilder(StructureBuilder):
    """Builder for Initials."""
    def __init__(self, initial_str: InitialStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "initial": initial_str.initial
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class IntegBuilder(StructureBuilder):
    """Builder for Integs/Stocks."""
    def __init__(self, integ_str: IntegStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "flow": integ_str.flow,
            "initial": integ_str.initial
        }
        self.non_negative = integ_str.non_negative

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class DelayBuilder(StructureBuilder):
    """Builder for regular Delays."""
    def __init__(self, dtype: str,
                 delay_str: Union[DelayStructure, DelayNStructure],
                 component: object):
        super().__init__(None, component)
        self.arguments = {
            "input": delay_str.input,
            "delay_time": delay_str.delay_time,
            "initial": delay_str.initial,
            "order": delay_str.order
        }
        self.dtype = dtype

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class DelayFixedBuilder(StructureBuilder):
    """Builder for Delay Fixed."""
    def __init__(self, delay_str: DelayFixedStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "input": delay_str.input,
            "delay_time": delay_str.delay_time,
            "initial": delay_str.initial,
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class SmoothBuilder(StructureBuilder):
    """Builder for Smooths."""
    def __init__(self, smooth_str: Union[SmoothStructure, SmoothNStructure],
                 component: object):
        super().__init__(None, component)
        self.arguments = {
            "input": smooth_str.input,
            "smooth_time": smooth_str.smooth_time,
            "initial": smooth_str.initial,
            "order": smooth_str.order
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class TrendBuilder(StructureBuilder):
    """Builder for Trends."""
    def __init__(self, trend_str: TrendStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "input": trend_str.input,
            "average_time": trend_str.average_time,
            "initial_trend": trend_str.initial_trend,
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class ForecastBuilder(StructureBuilder):
    """Builder for Forecasts."""
    def __init__(self, forecast_str: ForecastStructure, component: object):
        super().__init__(None, component)
        self.arguments = {
            "input": forecast_str.input,
            "average_time": forecast_str.average_time,
            "horizon": forecast_str.horizon,
            "initial_trend": forecast_str.initial_trend
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class SampleIfTrueBuilder(StructureBuilder):
    """Builder for Sample If True."""
    def __init__(self, sampleiftrue_str: SampleIfTrueStructure,
                 component: object):
        super().__init__(None, component)
        self.arguments = {
            "condition": sampleiftrue_str.condition,
            "input": sampleiftrue_str.input,
            "initial": sampleiftrue_str.initial,
        }

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class LookupsBuilder(StructureBuilder):
    """Builder for regular Lookups."""
    def __init__(self, lookups_str: LookupsStructure, component: object):
        super().__init__(None, component)
        self.arguments = {}
        self.x = lookups_str.x
        self.y = lookups_str.y
        self.keyword = lookups_str.type

    def build(self, arguments: dict) -> Union[BuildAST, None]:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST or None
            The built object, unless the component has been added to an
            existing object using the 'add' method.

        """
        pass


class InlineLookupsBuilder(StructureBuilder):
    """Builder for inline Lookups."""
    def __init__(self, inlinelookups_str: InlineLookupsStructure,
                 component: object):
        super().__init__(None, component)
        self.arguments = {
            "value": inlinelookups_str.argument
        }
        self.lookups = inlinelookups_str.lookups

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class ReferenceBuilder(StructureBuilder):
    """Builder for references to other variables."""
    def __init__(self, reference_str: ReferenceStructure, component: object):
        super().__init__(None, component)
        self.mapping_subscripts = {}
        self.reference = reference_str.reference
        self.subscripts = reference_str.subscripts
        self.arguments = {}

    @property
    def subscripts(self):
        pass

    @subscripts.setter
    def subscripts(self, subscripts: SubscriptsReferenceStructure):
        """Get subscript dictionary from reference"""
        pass

    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass

    def _visit_subscripts(self, expression: str, original_subs: dict) -> tuple:
        """
        Visit the subcripts of a reference to subset a subarray if neccessary
        or apply mapping.

        Parameters
        ----------
        expression: str
            The expression of visiting the variable.
        original_subs: dict
            The original subscript dict of the variable.

        Returns
        -------
        expression: str
            The expression with the necessary operations.
        mapping_subscirpts: dict
            The final subscripts of the reference after applying mapping.

        """
        pass


class NumericBuilder(StructureBuilder):
    """Builder for numeric and nan values."""
    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


class ArrayBuilder(StructureBuilder):
    """Builder for arrays."""
    def build(self, arguments: dict) -> BuildAST:
        """
        Build method.

        Parameters
        ----------
        arguments: dict
            The dictionary of builded arguments.

        Returns
        -------
        built_ast: BuildAST
            The built object.

        """
        pass


def merge_dependencies(*dependencies: dict, inplace: bool = False) -> dict:
    """
    Merge two dependencies dicts of an element.

    Parameters
    ----------
    dependencies: dict
        The dictionaries of dependencies to merge.

    inplace: bool (optional)
        If True the final dependencies dict will be updated in the first
        dependencies argument, mutating it. Default is False.

    Returns
    -------
    current: dict
        The final dependencies dict.

    """
    pass


def visit_loc(current_subs: dict, original_subs: dict,
              keep_shape: bool = False) -> tuple:
    """
    Compares the original subscripts and the current subscripts and
    returns subindexing information if needed.

    Parameters
    ----------
    current_subs: dict
        The dictionary of the subscripts that are used in the variable.

    original_subs: dict
        The dictionary of the original subscripts of the variable.

    keep_shape: bool (optional)
        If True will keep the number of dimensions of the original element
        and return only loc. Default is False.

    Returns
    -------
    loc: list of str or None
        List of the subscripting in each dimensions. If all are full (":"),
        None is rerned wich means that array indexing is not needed.

    rename: dict
        Dictionary of the dimensions to rename.

    final_subs: dict
        Dictionary of the final subscripts of the variable.

    reset_coords: bool
        Boolean indicating if the coords need to be reseted.

    to_float: bool
        Boolean indicating if the variable should be converted to a float.

    """
    pass


class ASTVisitor:
    """
    ASTVisitor allows visiting the Abstract Synatx Tree of a component
    returning the Python object and generating the neccessary objects.

    Parameters
    ----------
    component: ComponentBuilder
        The component builder to build.

    """
    _builders = {
        InitialStructure: InitialBuilder,
        IntegStructure: IntegBuilder,
        DelayStructure: lambda x, y: DelayBuilder("Delay", x, y),
        DelayNStructure: lambda x, y: DelayBuilder("DelayN", x, y),
        DelayFixedStructure: DelayFixedBuilder,
        SmoothStructure: SmoothBuilder,
        SmoothNStructure: SmoothBuilder,
        TrendStructure: TrendBuilder,
        ForecastStructure: ForecastBuilder,
        SampleIfTrueStructure: SampleIfTrueBuilder,
        GetConstantsStructure: ExtConstantBuilder,
        GetDataStructure: ExtDataBuilder,
        GetLookupsStructure: ExtLookupBuilder,
        LookupsStructure: LookupsBuilder,
        InlineLookupsStructure: InlineLookupsBuilder,
        DataStructure: TabDataBuilder,
        ReferenceStructure: ReferenceBuilder,
        CallStructure: CallBuilder,
        GameStructure: GameBuilder,
        AllocateAvailableStructure: AllocateAvailableBuilder,
        AllocateByPriorityStructure: AllocateByPriorityBuilder,
        LogicStructure: OperationBuilder,
        ArithmeticStructure: OperationBuilder,
        int: NumericBuilder,
        float: NumericBuilder,
        np.ndarray: ArrayBuilder,
    }

    def __init__(self, component: object):
        # component typing should be ComponentBuilder, but importing it
        # for typing would create a circular dependency :S
        self.ast = component.ast
        self.subscripts = component.subscripts_dict
        self.component = component

    def visit(self) -> Union[None, BuildAST]:
        """
        Visit the Abstract Syntax Tree of the component.

        Returns
        -------
        visit_out: BuildAST or None
            The BuildAST object resulting from visiting the AST. If the
            component content has been added to an existing object
            using the 'add' method it will return None.

        """
        pass

    def _visit(self, ast_object: AbstractSyntax) -> AbstractSyntax:
        """
        Visit one Builder and its arguments.
        """
        pass
