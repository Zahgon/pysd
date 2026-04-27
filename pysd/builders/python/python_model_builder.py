"""
The ModelBuilder class allows converting the AbstractModel into a
PySD model writing the Python code in files that can be loaded later
with PySD Model class. Each Abstract level has its own Builder. However,
the user is only required to create a ModelBuilder object using the
AbstractModel and call the `build_model` method.
"""
from warnings import warn
import textwrap
import black
import json
from pathlib import Path
from typing import Union

from pysd.translators.structures.abstract_model import\
    AbstractComponent, AbstractElement, AbstractControlElement,\
    AbstractModel, AbstractSection

from . import python_expressions_builder as vs
from .namespace import NamespaceManager
from .subscripts import SubscriptManager
from .imports import ImportsManager
from pysd._version import __version__


class ModelBuilder:
    """
    ModelBuilder allows building a PySD Python model from the
    Abstract Model.

    Parameters
    ----------
    abstract_model: AbstractModel
        The abstract model to build.

    """

    def __init__(self, abstract_model: AbstractModel):
        self.__dict__ = abstract_model.__dict__.copy()
        # load sections
        self.sections = [
            SectionBuilder(section)
            for section in abstract_model.sections
        ]
        # create the macrospace (namespace of macros)
        self.macrospace = {
            section.name: section for section in self.sections[1:]}

    def build_model(self) -> Path:
        """
        Build the Python model in a file callled as the orginal model
        but with '.py' suffix.

        Returns
        -------
        path: pathlib.Path
            The path to the new PySD model.

        """
        pass


class SectionBuilder:
    """
    SectionBuilder allows building a section of the PySD model. Each
    section will be a file unless the model has been set to be split
    in modules.

    Parameters
    ----------
    abstract_section: AbstractSection
        The abstract section to build.

    """
    def __init__(self, abstract_section: AbstractSection):
        self.__dict__ = abstract_section.__dict__.copy()
        self.root = self.path.parent  # the folder where the model is
        self.model_name = self.path.with_suffix("").name  # name of the model
        # Create subscript manager object with subscripts_dict
        self.subscripts = SubscriptManager(
            abstract_section.subscripts, self.root)
        # Load the elements in the section
        self.elements = [
            ElementBuilder(element, self)
            for element in abstract_section.elements
        ]
        # Create the namespace of the section
        self.namespace = NamespaceManager(self.params)
        # Create an imports manager
        self.imports = ImportsManager()
        # Create macrospace (namespace of macros)
        self.macrospace = {}
        # Create parameters dict necessary in macros
        self.params = {
            key: self.namespace.namespace[key]
            for key in self.params
        }
        # Import xarray if there are any subscripts defined in the section
        if self.subscripts.subscripts:
            self.imports.add("xarray")

    def build_section(self) -> None:
        """
        Build the Python section in a file callled as the orginal model
        if the section is main or in a file called as the macro name
        if the section is a macro.
        """
        pass

    def _process_views_tree(self, view_name: str,
                            view_content: Union[dict, set],
                            wdir: Path) -> dict:
        """
        Creates a directory tree based on the elements_per_view dictionary.
        If it's the final view, it creates a file, if not, it creates a folder.
        """
        pass

    def _build_modular(self, elements_per_view: dict) -> None:
        """ Build modular section """
        pass

    def _build_separate_module(self, elements: list, module_name: str,
                               module_dir: str) -> None:
        """
        Constructs and writes the Python representation of a specific model
        module, when the split_views=True in the read_vensim function.

        Parameters
        ----------
        elements: list
            Elements belonging to the module module_name.

        module_name: str
            Name of the module

        module_dir: str
            Path of the directory where module files will be stored.

        Returns
        -------
        None

        """
        pass

    def _build_main_module(self, elements: list) -> None:
        """
        Constructs and writes the Python representation of the main model
        module, when the split_views=True in the read_vensim function.

        Parameters
        ----------
        elements: list
            Elements belonging to the main module. Ideally, there should
            only be the initial_time, final_time, saveper and time_step,
            functions, though there might be others in some situations.
            Each element is a dictionary, with the various components
            needed to assemble a model component in Python syntax. This
            will contain multiple entries for elements that have multiple
            definitions in the original file, and which need to be combined.

        Returns
        -------
        None

        """
        pass

    def _build(self) -> None:
        """
        Constructs and writes the Python representation of a section.

        Returns
        -------
        None

        """
        pass

    def _build_variables(self, elements: dict) -> tuple:
        """
        Build model variables (functions) and separate then in control
        variables and regular variables.

        Returns
        -------
        control_vars, regular_vars: tuple, str
            control_vars is a tuple of length 2. First element is the
            dictionary of original control vars. Second is the string to
            add the control variables' functions. regular_vars is the
            string to add the regular variables' functions.

        """
        pass

    def _generate_functions(self, elements: dict) -> str:
        """
        Builds all model elements as functions in string format.
        NOTE: this function calls the build_element function, which
        updates the import_modules.
        Therefore, it needs to be executed before the method
        _generate_automatic_imports.

        Parameters
        ----------
        elements: dict
            Each element is a dictionary, with the various components
            needed to assemble a model component in Python syntax. This
            will contain multiple entries for elements that have multiple
            definitions in the original file, and which need to be combined.

        Returns
        -------
        funcs: str
            String containing all formated model functions

        """
        pass

    def _get_control_vars(self, control_vars: str) -> str:
        """
        Create the section of control variables

        Parameters
        ----------
        control_vars: str
            Functions to define control variables.

        Returns
        -------
        text: str
            Control variables section and header of model variables section.

        """
        pass


class ElementBuilder:
    """
    ElementBuilder allows building an element of the PySD model.

    Parameters
    ----------
    abstract_element: AbstractElement
        The abstract element to build.
    section: SectionBuilder
        The section where the element is defined. Necessary to give the
        acces to the subscripts and namespace.

    """
    def __init__(self, abstract_element: AbstractElement,
                 section: SectionBuilder):
        self.__dict__ = abstract_element.__dict__.copy()
        self.control_var = isinstance(abstract_element, AbstractControlElement)
        # Set element type and subtype to None
        self.type = None
        self.subtype = None
        # Get the arguments of the element
        self.arguments = getattr(self.components[0], "arguments", "")
        # Load the components of the element
        self.components = [
            ComponentBuilder(component, self, section)
            for component in abstract_element.components
        ]
        self.section = section
        # Get the subscripts of the element after merging all the components
        self.subscripts = section.subscripts.make_merge_list(
            [component.subscripts[0] for component in self.components])
        # Get the subscript dictionary of the element
        self.subs_dict = section.subscripts.make_coord_dict(self.subscripts)
        # Dictionaries to save dependencies and objects related to the element
        self.dependencies = {}
        self.other_dependencies = {}
        self.objects = {}

    def build_element(self) -> None:
        """
        Build the element. Returns the string to include in the section which
        will be a decorated function definition and possible objects.
        """
        pass

    def _manage_multi_def(self, expression: dict) -> str:
        """
        Manage multiline definitions when some of them (not all) are
        merged to one object.
        """
        pass

    def _manage_except(self, expression: dict) -> str:
        """
        Manage except declarations by not asigning its values.
        """
        pass

    def _build_element_out(self) -> str:
        """
        Returns a string that has processed a single element dictionary.

        Returns
        -------
        func: str
            The function to write in the model file.

        """
        pass

    def _format_limits(self, limits: tuple) -> str:
        """Format the limits of an element to print them properly"""
        pass


class ComponentBuilder:
    """
    ComponentBuilder allows building a component of the PySD model.

    Parameters
    ----------
    abstract_component: AbstracComponent
        The abstract component to build.
    element: ElementBuilder
        The element where the component is defined. Necessary to give the
        acces to the merging subscripts and other components.
    section: SectionBuilder
        The section where the element is defined. Necessary to give the
        acces to the subscripts and namespace.

    """
    def __init__(self, abstract_component: AbstractComponent,
                 element: ElementBuilder, section: SectionBuilder):
        self.__dict__ = abstract_component.__dict__.copy()
        self.element = element
        self.section = section
        if not hasattr(self, "keyword"):
            self.keyword = None

    def build_component(self) -> None:
        """
        Build model component parsing the Abstract Syntax Tree.
        """
        pass

    def get(self) -> tuple:
        """
        Get build component to build the element.

        Returns
        -------
        ast_build: BuildAST
            Parsed AbstractSyntaxTree.
        subscript_dict: dict or list of dicts
            The subscripts of the component.
        except_subscripts: list of dicts
            The subscripts to avoid.

        """
        pass
