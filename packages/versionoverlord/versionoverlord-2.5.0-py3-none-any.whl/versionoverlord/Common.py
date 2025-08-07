
from typing import Callable
from typing import Dict
from typing import List
from typing import NewType
from typing import Tuple

import logging
import logging.config

from importlib.resources.abc import Traversable
from importlib.resources import files

from platform import platform as osPlatform

from subprocess import CompletedProcess
from subprocess import run as subProcessRun

from json import load as jsonLoad

from dataclasses import dataclass
from dataclasses import field

from semantic_version import Version as SemanticVersion

THE_GREAT_MAC_PLATFORM: str = 'macOS'

CURL_CMD:         str = 'curl'
JQ_CMD:           str = 'jq'

MAC_OS_CURL_PATH: str = f'/usr/bin/{CURL_CMD} --help'
MAC_OS_JQ_PATH:   str = f'/opt/homebrew/bin/{JQ_CMD} --version'

LINUX_OS_JQ_PATH: str = f'/usr/bin/{JQ_CMD} --version'


EPILOG:               str = 'Written by Humberto A. Sanchez II (humberto.a.sanchez.ii@gmail.com)'

NO_INTERNET_CONNECTION_MSG: str = 'You are not connected to the internet'
NO_REPO_SLUG_MSG:           str = 'Provide a repository slug either as an option or in the environment variable (REPO_SLUG)'

ENV_PROJECTS_BASE:    str = 'PROJECTS_BASE'
ENV_PROJECT:          str = 'PROJECT'
ENV_APPLICATION_NAME: str = 'APPLICATION_NAME'
ENV_GH_TOKEN:         str = 'GH_TOKEN'
ENV_REPO_SLUG:        str = 'REPO_SLUG'

DEPENDENCIES:     str = 'dependencies'

SETUP_PY:         str = 'setup.py'
REQUIREMENTS_TXT: str = 'requirements.txt'
PYPROJECT_TOML:   str = 'pyproject.toml'
INSTALL_REQUIRES: str = 'install_requires'

CIRCLE_CI_DIRECTORY: str = '.circleci'
CIRCLE_CI_YAML:      str = 'config.yml'

TRAVIS_CI_YAML:      str = '.travis.yml'

SPECIFICATION_FILE:           str = 'versionSpecification.csv'
RESOURCES_PACKAGE_NAME:       str = 'versionoverlord.resources'
JSON_LOGGING_CONFIG_FILENAME: str = "loggingConfiguration.json"


EQUAL_EQUAL:           str = '=='
APPROXIMATELY_EQUAL:   str = '~='
GREATER_THAN_OR_EQUAL: str = '>='
LESS_THAN_OR_EQUAL:    str = '<='
GREATER_THAN:          str = '>'
LESS_THAN:             str = '<'

MATCH_PATTERNS: List[str] = [
    EQUAL_EQUAL, APPROXIMATELY_EQUAL, GREATER_THAN_OR_EQUAL, LESS_THAN_OR_EQUAL, GREATER_THAN, LESS_THAN
]

PYPROJECT_TOML_TRAILING_CHARACTERS: str = "\"',"


def versionFactory() -> SemanticVersion:
    return SemanticVersion('0.0.0')


PackageName = NewType('PackageName', str)


@dataclass
class UpdatePackage:
    """
    Defines the package to update
    """
    packageName: PackageName     = PackageName('')
    oldVersion:  SemanticVersion = field(default_factory=versionFactory)
    newVersion:  SemanticVersion = field(default_factory=versionFactory)


Packages                 = NewType('Packages', List[UpdatePackage])
PackageLookupType        = NewType('PackageLookupType', Dict[PackageName, UpdatePackage])
UpdateDependencyCallback = NewType('UpdateDependencyCallback', Callable[[str], str])    # type: ignore
CLISlugs                 = NewType('CLISlugs', Tuple[str])

RepositorySlug = NewType('RepositorySlug', str)


@dataclass
class AdvancedSlug:
    slug:        str = ''
    packageName: str = ''


AdvancedSlugs = NewType('AdvancedSlugs', List[AdvancedSlug])


@dataclass
class SlugVersion(AdvancedSlug):
    version:     str = ''


SlugVersions = NewType('SlugVersions', List[SlugVersion])


def setUpLogging():
    """
    """
    traversable: Traversable = files(RESOURCES_PACKAGE_NAME) / JSON_LOGGING_CONFIG_FILENAME

    # loggingConfigFilename: str = resource_filename(RESOURCES_PACKAGE_NAME, JSON_LOGGING_CONFIG_FILENAME)
    loggingConfigFilename: str = str(traversable)

    with open(loggingConfigFilename, 'r') as loggingConfigurationFile:
        configurationDictionary = jsonLoad(loggingConfigurationFile)

    logging.config.dictConfig(configurationDictionary)
    logging.logProcesses = False
    logging.logThreads = False


def extractPackageName(slug: str) -> str:
    splitSlug: List[str] = slug.split(sep='/')

    pkgName: str = splitSlug[1]
    return pkgName


def extractCLISlugs(slugs: CLISlugs) -> AdvancedSlugs:

    cliSlugs: AdvancedSlugs = AdvancedSlugs([])

    for slug in slugs:

        advancedSlug: AdvancedSlug = AdvancedSlug()
        slugPackage: List[str] = slug.split(',')
        if len(slugPackage) > 1:
            advancedSlug.slug = slugPackage[0]
            advancedSlug.packageName = slugPackage[1]
        else:
            advancedSlug.slug = slug
            advancedSlug.packageName = extractPackageName(slug)

        cliSlugs.append(advancedSlug)

    return cliSlugs


def checkJQInstalled() -> bool:
    """
    Returns: `True` if the JSON processor is installed else `False`
    """
    platform: str = osPlatform(terse=True)
    if platform.startswith(THE_GREAT_MAC_PLATFORM) is True:
        return checkInstallation(MAC_OS_JQ_PATH)
    else:
        return checkInstallation(LINUX_OS_JQ_PATH)


def checkCurlInstalled() -> bool:
    return checkInstallation(MAC_OS_CURL_PATH)


def checkInstallation(commandToCheck) -> bool:
    ans:    bool = False
    status: int  = runCommand(commandToCheck)
    if status == 0:
        ans = True

    return ans


def runCommand(programToRun: str) -> int:
    """

    Args:
        programToRun:  What must be executed

    Returns:  The status return of the executed program
    """
    completedProcess: CompletedProcess = subProcessRun([programToRun], shell=True, capture_output=True, text=True, check=False)
    return completedProcess.returncode
