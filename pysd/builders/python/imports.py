from typing import Union


class ImportsManager():
    """
    Class to save the imported modules information for intelligent import
    """
    _external_libs = {"numpy": "np", "xarray": "xr"}
    _external_submodules = ["scipy"]
    _internal_libs = [
        "functions", "statefuls", "external", "data", "lookups", "utils",
        "allocation", "model"
    ]

    def __init__(self):
        self._numpy, self._xarray = False, False
        self._functions, self._statefuls, self._external, self._data,\
            self._lookups, self._utils, self._scipy, self._allocation,\
            self._model =\
            set(), set(), set(), set(), set(), set(), set(), set(), set()

    def add(self, module: str, function: Union[str, None] = None) -> None:
        """
        Add a function from module.

        Parameters
        ----------
        module: str
          module name.

        function: str or None
          function name. If None module will be set to true.

        """
        pass

    def get_header(self, outfile: str) -> str:
        """
        Returns the importing information to print in the model file

        Parameters
        ----------
        outfile: str
            Name of the outfile to print in the header.

        Returns
        -------
        text: str
            Header of the translated model file.

        """
        pass
