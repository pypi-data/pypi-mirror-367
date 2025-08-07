
from typing import List
from typing import Optional

from logging import Logger
from logging import getLogger

from os import linesep as osLineSep

from pathlib import Path

from click import command
from click import version_option
from click import option
from click import secho
from click import prompt
from click import ClickException

from versionoverlord import __version__

from versionoverlord.Common import EPILOG
from versionoverlord.Common import setUpLogging
from versionoverlord.EnvironmentBase import EnvironmentBase
from versionoverlord.commands.TagType import TagType

STANDARD_SOURCE_DIRECTORY: Path = Path('src')
STANDARD_VERSION_FILENAME: Path = Path('_version.py')

STRIP_LF_CHAR:      str = osLineSep
STRIP_SINGLE_QUOTE: str = "' "      # Including spaces
STRIP_DOUBLE_QUOTE: str = '" '      # Including spaces

VERSION_CODE_TEMPLATE: str = "__version__: str = '{}'{}"


class BumpVersion(EnvironmentBase):
    def __init__(self, packageName: Optional['str']):
        super().__init__()

        self.logger:       Logger          = getLogger(__name__)
        self._packageName: Optional['str'] = packageName

        directory:             Path = Path(self._projectDirectory)
        if packageName is None:
            packagePath: Path = directory
        else:
            packagePath = Path(packageName)
        self._versionFilePath: Path = Path(self._projectsBase) / directory / STANDARD_SOURCE_DIRECTORY / packagePath / STANDARD_VERSION_FILENAME

        # noinspection PySimplifyBooleanCheck
        if self._versionFilePath.exists() is False:
            raise ClickException(f'No such file: {self._versionFilePath}.  Perhaps specify package name.')

    def bumpIt(self):

        versionCode:  str       = self._versionFilePath.read_text()
        versionSplit: List[str] = versionCode.split('=')
        versionStr:   str       = versionSplit[1]

        versionStr = versionStr.strip(STRIP_LF_CHAR).strip(STRIP_SINGLE_QUOTE).strip(STRIP_DOUBLE_QUOTE)
        secho(f'Current version: `{versionStr}`')

        newVersion: TagType = prompt('Enter new version', type=TagType())
        secho(f'New version: {newVersion}')
        updateCodeLine: str = VERSION_CODE_TEMPLATE.format(newVersion, osLineSep)
        self._versionFilePath.write_text(updateCodeLine)


@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--package-name', '-p', help='Optional package name when repository does not match')
def bumpVersion(package_name: str):
    """
    \b
    Bump version looks for file in src/<moduleName>/_version.py.  It echoes it to stdout
    and asks the developer to provide an updated value.

    It uses the following environment variables:

    \b
        GH_TOKEN      – A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE – The local directory where the python projects are based
        PROJECT       – The name of the project;  It should be a directory name
    """
    bv: BumpVersion = BumpVersion(packageName=package_name)
    bv.bumpIt()


if __name__ == "__main__":

    setUpLogging()
    # noinspection SpellCheckingInspection
    # createSpecification(['-i', 'tests/resources/testdata/query.slg'])
    # createSpecification(['-s', 'hasii2011/code-ally-basic,codeallybasic'])

    # bumpVersion(['--version'])
    # bumpVersion(['--help'])
    bumpVersion([])