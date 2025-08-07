
from typing import Any
from typing import Dict
from typing import List
from typing import NewType

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from subprocess import CompletedProcess
from subprocess import run as subProcessRun

from pathlib import Path

from tomllib import load as tomlLoad

from click import command
from click import option
from click import version_option
from click import secho
from click import prompt
from click import pass_context
from click import ClickException

from click import edit as clickEdit
from click import confirm as clickConfirm

from versionoverlord import __version__

from versionoverlord.Common import CURL_CMD
from versionoverlord.Common import EPILOG
from versionoverlord.Common import JQ_CMD
from versionoverlord.Common import MATCH_PATTERNS
from versionoverlord.Common import PYPROJECT_TOML
from versionoverlord.Common import SPECIFICATION_FILE
from versionoverlord.Common import checkCurlInstalled
from versionoverlord.Common import checkJQInstalled
from versionoverlord.Common import setUpLogging

from versionoverlord.EnvironmentBase import EnvironmentBase

from versionoverlord.commands.UpdateDependencies import updateDependencies

StringList     = NewType('StringList', List[str])
StringDict     = NewType('StringDict', Dict[str, str])

TomlDict       = Dict[str, Any]
ProjectDict    = NewType('ProjectDict',    Dict[str, Any])
DependencyList = NewType('DependencyList', StringList)
OptionalDict   = NewType('OptionalDict',   Dict[str, DependencyList])

OldPackageDict = NewType('OldPackageDict', Dict[str, str])

PYPROJECT_TOML_PROJECT_KEY:             str = 'project'
PYPROJECT_TOML_DEPENDENCY_KEY:          str = 'dependencies'
PYPROJECT_TOML_OPTIONAL_DEPENDENCY_KEY: str = 'optional-dependencies'


class PickDependencies(EnvironmentBase):
    """

    """
    def __init__(self):
        super().__init__()

        self.logger: Logger = getLogger(__name__)

        directory: Path = Path(self._projectDirectory)

        self._pyProjectTomlFilePath: Path = Path(self._projectsBase) / directory / Path(PYPROJECT_TOML)

        # noinspection PySimplifyBooleanCheck
        if self._pyProjectTomlFilePath.exists() is False:
            raise ClickException(f'No such file: {self._pyProjectTomlFilePath}.')

    def pickThem(self, optional_dependencies: bool):

        with open(self._pyProjectTomlFilePath, "rb") as f:

            data:         TomlDict       = tomlLoad(f)
            project:      ProjectDict    = data[PYPROJECT_TOML_PROJECT_KEY]

            # noinspection PySimplifyBooleanCheck
            if optional_dependencies is False:
                dependencies: DependencyList = project[PYPROJECT_TOML_DEPENDENCY_KEY]
            else:
                optionalDict: OptionalDict = project[PYPROJECT_TOML_OPTIONAL_DEPENDENCY_KEY]
                projectKeys    = optionalDict.keys()

                secho('Found the following optional dependencies', reverse=True, overline=True)
                for projectKey in projectKeys:
                    secho(f'{projectKey}')

                depToUpdate: str = prompt('Enter one of the above dependencies that you wish to update', type=str)
                if depToUpdate not in projectKeys:
                    raise ClickException(f'That dependency is not valid.')
                dependencies = optionalDict[depToUpdate]

        self.logger.debug(f'{dependencies}')
        self._pickDependencies(dependencies=dependencies)

    def _getDelimiter(self, dependency: str) -> str:

        matchPattern: str = ''
        for mp in MATCH_PATTERNS:
            if mp in dependency:
                matchPattern = mp
                break

        return matchPattern

    def _getLatestVersion(self, packageName: str) -> str:
        """
        Run a pair of commands to get a pypi version for a particular
        package;  Assumes that external command existence has already been
        done

        TODO:  This code goes in Common.py
        TODO:  Remove the magic strings in the curl command

        Args:
            packageName:  The name of the package on pypi

        Returns:  The last pypi package version;  If package not found return empty string
        """

        self.logger.info(f'{packageName=}')
        checkCmd: str = (
            f"curl -s https://pypi.org/pypi/{packageName}/json | jq -r '.info.version'"
        )
        completedProcess: CompletedProcess = subProcessRun([checkCmd], shell=True, capture_output=True, text=True, check=False)
        if completedProcess.returncode == 0:
            versionDescription: str = completedProcess.stdout.strip(osLineSep)
            self.logger.debug(versionDescription)
        else:
            versionDescription = ''

        return versionDescription

    def _pickDependencies(self, dependencies: DependencyList):
        """

        Args:
            dependencies:  A dependency list

        """
        dependenciesStr: str = self._makeEditString(dependencies=dependencies)

        secho('Remove any dependencies in the editor that you do not wish to update.')
        if clickConfirm('Do you want to continue?', abort=True):
            picked: str | None = clickEdit(dependenciesStr, require_save=False)
            if picked is None:
                secho('No selections.  bye bye')
            else:
                oldPkgDict: OldPackageDict = self._makeOldPackageDictionary(dependencies=dependencies)

                self._writeTheSpecificationFile(pickedPackages=picked, oldPkgDict=oldPkgDict)

    def _makeEditString(self, dependencies: DependencyList) -> str:
        """
        Turn the pyproject.toml list into string with EOL characters that
        the developer can edit in order to pick the dependencies to update

        Args:
            dependencies: The dependency list from pyproject.toml

        Returns:  A multi-line string that can be displayed in an editor
        """
        dependenciesStr: str = ''
        for dep in dependencies:
            delimiter: str       = self._getDelimiter(dep)
            splitDep:  List[str] = dep.split(delimiter)
            dependenciesStr = f'{dependenciesStr}{splitDep[0]}{osLineSep}'

        return dependenciesStr

    def _makeOldPackageDictionary(self, dependencies: DependencyList) -> OldPackageDict:
        """

        Args:
            dependencies:  The dependency list from pyproject.toml

        Returns:  A dictionary that maps a package name to its old versio
        """

        pkgDict: OldPackageDict = OldPackageDict({})
        for dep in dependencies:
            delimiter: str       = self._getDelimiter(dep)
            splitDep:  List[str] = dep.split(delimiter)
            pkgDict[splitDep[0]] = splitDep[1]

        return pkgDict

    def _writeTheSpecificationFile(self, pickedPackages: str, oldPkgDict: OldPackageDict):
        """

        Args:
            pickedPackages:   The list of packages picked by developer
            oldPkgDict:       A dictionary that has the old versions
        """

        packageList:                List[str] = pickedPackages.split(osLineSep)
        versionUpdateSpecification: Path      = Path(SPECIFICATION_FILE)

        with versionUpdateSpecification.open(mode='w') as fd:
            fd.write(f'PackageName,OldVersion,NewVersion{osLineSep}')

            for package in packageList:
                if len(package) > 0:
                    newVersion: str = self._getLatestVersion(packageName=package)

                    specificationLine: str = f'{package},{oldPkgDict[package]},{newVersion}{osLineSep}'
                    fd.write(specificationLine)


@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--optional-dependencies', '-o', is_flag=True,  help='Update optional dependencies')
@option('--update-packages',       '-u', is_flag=True,  help='Run pip install on the packages')
@pass_context
def pickDependencies(ctx, optional_dependencies: bool, update_packages: bool):
    """
    \b
    * Reads pyproject.toml and picks the dependencies from the `dependencies` section or optionally
    one of the optional dependencies
    * It displays them in an editor.
    * The developer removes dependencies he/she does not want to update.
    * This command creates the dependency csv file in the same format as the `createSpecification` command.
    * It then invokes the `updateDependencies` command to update the files.  Unlike `createSpecification`, pickDependencies queries pypi to get the module versions


    It uses the following environment variables:

    \b
        GH_TOKEN      – A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE – The local directory where the python projects are based
        PROJECT       – The name of the project;  It should be a directory name
    """
    # noinspection PySimplifyBooleanCheck
    if checkJQInstalled() is False:
        raise ClickException(f'{JQ_CMD} is not installed')

    # noinspection PySimplifyBooleanCheck
    if checkCurlInstalled() is False:
        raise ClickException(f'{CURL_CMD} not installed')

    pd: PickDependencies = PickDependencies()
    pd.pickThem(optional_dependencies=optional_dependencies)

    # noinspection PySimplifyBooleanCheck
    if update_packages is True:
        ctx.invoke(updateDependencies(['--update-packages']))
    else:
        ctx.invoke(updateDependencies())


if __name__ == "__main__":

    setUpLogging()

    # pickDependencies(['--version'])
    # pickDependencies(['--help'])
    pickDependencies(['--optional-dependencies'])
