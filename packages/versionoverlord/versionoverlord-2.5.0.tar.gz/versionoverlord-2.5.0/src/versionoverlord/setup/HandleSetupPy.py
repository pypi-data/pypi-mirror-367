
from logging import Logger
from logging import getLogger

from pathlib import Path

from os import sep as osSep

from versionoverlord.Common import SETUP_PY
from versionoverlord.Common import Packages


from versionoverlord.IHandler import IHandler


class HandleSetupPy(IHandler):
    """
    Handles the setup.py file
    """
    def __init__(self, packages: Packages):

        self.logger: Logger = getLogger(__name__)
        super().__init__(packages)

        self._setupPyPath: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{SETUP_PY}')

    @property
    def configurationExists(self) -> bool:
        return self._setupPyPath.exists()

    def update(self):
        """
        Updates a project's setup.py file.  Updates the "requires"
        """
        self._update(configurationFilePath=self._setupPyPath)
