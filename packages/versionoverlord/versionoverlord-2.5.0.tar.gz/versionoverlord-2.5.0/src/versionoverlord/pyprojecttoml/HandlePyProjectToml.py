
from logging import Logger
from logging import getLogger

from os import sep as osSep

from pathlib import Path

from versionoverlord.IHandler import IHandler

from versionoverlord.Common import PYPROJECT_TOML
from versionoverlord.Common import Packages


class HandlePyProjectToml(IHandler):
    """
    Handles the pyproject.toml file
    """

    def __init__(self, packages: Packages):
        self.logger: Logger = getLogger(__name__)
        super().__init__(packages)

        self._pyProjectToml: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{PYPROJECT_TOML}')

    @property
    def configurationExists(self) -> bool:
        """
        Returns:  'True' if the project has this type of configuration file, else 'False'
        """
        return self._pyProjectToml.exists()

    def update(self):
        """
        Updates a project's pyproject.toml  Updates the "dependencies" section
        """
        self._update(configurationFilePath=self._pyProjectToml)
