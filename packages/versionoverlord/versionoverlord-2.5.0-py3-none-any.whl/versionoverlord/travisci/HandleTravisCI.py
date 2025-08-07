
from logging import Logger
from logging import getLogger

from os import sep as osSep
from pathlib import Path

from versionoverlord.Common import Packages
from versionoverlord.Common import TRAVIS_CI_YAML
from versionoverlord.IHandler import IHandler


class HandleTravisCI(IHandler):

    def __init__(self, packages: Packages):

        self.logger: Logger = getLogger(__name__)

        super().__init__(packages)

        self._travisCIYAML: Path = Path(f'{self._projectsBase}{osSep}{self._projectDirectory}{osSep}{TRAVIS_CI_YAML}')

    @property
    def configurationExists(self) -> bool:
        return self._travisCIYAML.exists()

    def update(self):
        self._update(configurationFilePath=self._travisCIYAML)
