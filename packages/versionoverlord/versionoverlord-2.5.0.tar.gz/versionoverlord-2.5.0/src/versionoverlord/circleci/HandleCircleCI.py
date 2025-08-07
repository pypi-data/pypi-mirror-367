
from logging import Logger
from logging import getLogger

from os import sep as osSep

from pathlib import Path

from versionoverlord.Common import CIRCLE_CI_DIRECTORY
from versionoverlord.Common import CIRCLE_CI_YAML

from versionoverlord.IHandler import IHandler
from versionoverlord.Common import Packages


class HandleCircleCI(IHandler):

    def __init__(self, packages: Packages):

        self.logger: Logger = getLogger(__name__)

        super().__init__(packages)

        self._circleCIYAML: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{CIRCLE_CI_DIRECTORY}{osSep}{CIRCLE_CI_YAML}')

    @property
    def configurationExists(self) -> bool:
        return self._circleCIYAML.exists()

    def update(self):

        self._update(configurationFilePath=self._circleCIYAML)
