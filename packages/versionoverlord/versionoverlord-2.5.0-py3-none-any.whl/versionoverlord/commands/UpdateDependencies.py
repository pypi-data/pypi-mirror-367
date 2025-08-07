
from typing import Dict
from typing import List
from typing import NewType
from typing import cast

from logging import Logger
from logging import getLogger

from dataclasses import dataclass
import csv

from pathlib import Path as PyPath

from click import Path
from click import command
from click import echo
from click import option
from click import secho
from click import version_option

from semantic_version import Version as SemanticVersion

from versionoverlord import __version__
from versionoverlord.Common import EPILOG

from versionoverlord.Common import PackageName
from versionoverlord.Common import Packages
from versionoverlord.Common import UpdatePackage
from versionoverlord.Common import runCommand
from versionoverlord.Common import setUpLogging
from versionoverlord.IHandler import IHandler

from versionoverlord.setup.HandleSetupPy import HandleSetupPy

from versionoverlord.circleci.HandleCircleCI import HandleCircleCI

from versionoverlord.pyprojecttoml.HandlePyProjectToml import HandlePyProjectToml

from versionoverlord.requirements.HandleRequirementsTxt import HandleRequirementsTxt
from versionoverlord.travisci.HandleTravisCI import HandleTravisCI


@dataclass
class HandlerSpecification:
    fileName: str      = ''
    handler:  IHandler = cast(IHandler, None)


HandlerSpecifications = NewType('HandlerSpecifications', List[HandlerSpecification])


class UpdateDependencies:
    def __init__(self, specification: PyPath):
        """

        Args:
            specification:  Path to the CSV file
        """
        self.logger: Logger = getLogger(__name__)

        self._packages: Packages = self._buildAPackageList(specification=specification)

        self._handlers: HandlerSpecifications = HandlerSpecifications([
            HandlerSpecification('setup.py',         HandleSetupPy(packages=self._packages)),
            HandlerSpecification('config.yml',       HandleCircleCI(packages=self._packages)),
            HandlerSpecification('requirements.txt', HandleRequirementsTxt(packages=self._packages)),
            HandlerSpecification('pyproject.toml',   HandlePyProjectToml(packages=self._packages)),
            HandlerSpecification('.travis.yml',      HandleTravisCI(packages=self._packages))
        ])

    @property
    def packages(self) -> Packages:
        return self._packages

    def update(self):

        assert len(self._packages) != 0,  'Developer error; package list not initialized'

        for spec in self._handlers:
            handlerSpecification: HandlerSpecification = cast(HandlerSpecification, spec)
            handler:              IHandler             = handlerSpecification.handler
            name:                 str                  = handlerSpecification.fileName
            # noinspection PySimplifyBooleanCheck
            if handler.configurationExists is True:
                # echo(f'Update {name}', color=True)    # This could be misleading if there were no changes
                handler.update()
            else:
                echo(f'No {name}')

    def _buildAPackageList(self, specification: PyPath) -> Packages:
        """
        Transforms the CSV file to a list of Package objects

        Args:
            specification:  The path to the csv file

        Returns:  A list of packages
        """
        with open(specification) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            packages: Packages = Packages([])

            for dictRow in csvreader:
                row: Dict[str, str] = cast(Dict[str, str], dictRow)
                self.logger.debug(row['PackageName'], row['OldVersion'], row['NewVersion'])
                packageName: PackageName = PackageName(row['PackageName'])
                updatePackage: UpdatePackage = UpdatePackage()
                updatePackage.packageName = packageName
                try:
                    updatePackage.oldVersion = SemanticVersion(row['OldVersion'])
                    updatePackage.newVersion = SemanticVersion(row['NewVersion'])
                    packages.append(updatePackage)
                except ValueError:
                    eMsg: str = (
                        f'Package: `{packageName}` '
                        'has invalid semantic version: '
                        '{row["OldVersion"]} or {row["NewVersion"]} ignored '
                        'not updated'
                    )
                    secho(eMsg, reverse=True)

        return packages


@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--specification', '-s', is_flag=False, flag_value='versionSpecification.csv', default='versionSpecification.csv',
        type=Path(exists=True, path_type=PyPath),
        required=False,
        help='Update the project using a specification file')
@option('--update-packages', '-u', is_flag=True,  help='Run pip install on the packages')
def updateDependencies(specification: PyPath, update_packages: bool):
    """
    \b
    This command uses the .csv file created by createSpec.  It updates existing
    files that have dependencies in them.  It can optionally run
    `pip install --upgrade ` for each package

    \b
        - setup.py
        - .circleci/config.yml
        - requirements.txt
        - pyproject.toml
        - .travis.yml

    It uses the following environment variables:

    \b
        GH_TOKEN      - A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE -  The local directory where the python projects are based
        PROJECT       -  The name of the project;  It should be a directory name
    """
    setUpLogging()
    vUpdate: UpdateDependencies = UpdateDependencies(specification=specification)
    vUpdate.update()

    # noinspection PySimplifyBooleanCheck
    if update_packages is True:
        packages: Packages = vUpdate.packages
        for p in packages:
            package: UpdatePackage = cast(UpdatePackage, p)
            secho(f'Updating: {package.packageName} to {package.newVersion}', reverse=True)
            runCommand(f'pip install --upgrade {package.packageName}')


if __name__ == "__main__":
    updateDependencies(['--help'])
