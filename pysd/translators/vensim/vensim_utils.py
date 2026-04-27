import re
import warnings
import uuid

import parsimonious
from typing import Dict
from pathlib import Path
from chardet import detect


supported_extensions = [".mdl"]


class Grammar():
    _common_grammar = None
    _grammar_path: Path = Path(__file__).parent.joinpath("parsing_grammars")
    _grammar: Dict = {}

    @classmethod
    def get(cls, grammar: str, subs: dict = {}) -> parsimonious.Grammar:
        """Get parsimonious grammar for parsing"""
        pass

    @classmethod
    def _read_grammar(cls, grammar: str) -> str:
        """Read grammar from a file and include common grammar"""
        pass

    @classmethod
    def _include_common_grammar(cls, source_grammar: str) -> str:
        """Include common grammar"""
        pass

    @classmethod
    def _gpath(cls, grammar: str) -> Path:
        """Get the grammar file path"""
        pass


def split_arithmetic(structure: object, parsing_ops: dict,
                     expression: str, elements: dict,
                     negatives: set = set()) -> object:
    """
    Split arithmetic pattern and return the corresponding object.

    Parameters
    ----------
    structure: callable
       Callable that generates the arithmetic object to return.
    parsing_ops: dict
       The parsing operators dictionary.
    expression: str
       Original expression with the operator and the hex code to the objects.
    elements: dict
       Dictionary of the hex identifiers and the objects that represent.
    negative: set
       Set of element hex values that must change their sign.

    Returns
    -------
    object: structure
        Final object of the arithmetic operation or initial object if
        no operations are performed.

    """
    pass


def add_element(elements: dict, element: object) -> str:
    """
    Add element to elements dict using an unique hex identifier

    Parameters
    ----------
    elements: dict
      Dictionary of all elements.

    element: object
      Element to add.

    Returns
    -------
    id: str (hex)
      The name of the key where element is saved in elements.

    """
    pass


def _detect_encoding_from_file(mdl_file: Path) -> str:
    """Detect and return the encoding from a Vensim file"""
    pass
