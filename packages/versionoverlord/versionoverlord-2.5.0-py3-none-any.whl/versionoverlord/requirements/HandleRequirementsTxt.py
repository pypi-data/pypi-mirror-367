
from logging import Logger
from logging import getLogger

from os import sep as osSep

from pathlib import Path

from versionoverlord.Common import REQUIREMENTS_TXT
from versionoverlord.Common import Packages

from versionoverlord.IHandler import IHandler


class HandleRequirementsTxt(IHandler):

    def __init__(self, packages: Packages):

        self.logger: Logger = getLogger(__name__)

        super().__init__(packages)

        self._requirementsTxtPath: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{REQUIREMENTS_TXT}')

    @property
    def configurationExists(self) -> bool:
        return self._requirementsTxtPath.exists()

    def update(self):

        self._update(configurationFilePath=self._requirementsTxtPath)
