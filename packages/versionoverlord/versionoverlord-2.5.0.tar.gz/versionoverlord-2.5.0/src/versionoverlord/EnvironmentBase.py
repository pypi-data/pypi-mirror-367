
from logging import Logger
from logging import getLogger

from os import environ as osEnvironment

from versionoverlord.Common import ENV_PROJECT
from versionoverlord.Common import ENV_PROJECTS_BASE
from versionoverlord.exceptions.ProjectNotSetException import ProjectNotSetException
from versionoverlord.exceptions.ProjectsBaseNotSetException import ProjectsBaseNotSetException


class EnvironmentBase:
    """

    """
    def __init__(self):

        self.ebLogger: Logger = getLogger(__name__)

        self._projectsBase:     str = ''
        self._projectDirectory: str = ''

        try:
            self._projectsBase = osEnvironment[ENV_PROJECTS_BASE]
        except KeyError:
            self.ebLogger.error(f'Project Base not set')
            raise ProjectsBaseNotSetException
        try:
            self._projectDirectory = osEnvironment[ENV_PROJECT]
        except KeyError:
            self.ebLogger.error(f'Project Directory not set')
            raise ProjectNotSetException
        except (ValueError, Exception) as e:
            self.ebLogger.error(f'{e}')
