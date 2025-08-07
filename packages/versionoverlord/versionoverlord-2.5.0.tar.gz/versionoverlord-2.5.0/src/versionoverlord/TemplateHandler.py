
from logging import Logger
from logging import getLogger

from pathlib import Path

from os import linesep as osLineSep

from re import search as regExSearch
from re import Match

from semantic_version import Version as SemanticVersion

from click import ClickException

from versionoverlord.Common import AdvancedSlugs
from versionoverlord.Common import MATCH_PATTERNS
from versionoverlord.Common import PYPROJECT_TOML
from versionoverlord.Common import PYPROJECT_TOML_TRAILING_CHARACTERS
from versionoverlord.Common import REQUIREMENTS_TXT
from versionoverlord.Common import SPECIFICATION_FILE
from versionoverlord.Common import SlugVersion
from versionoverlord.Common import SlugVersions

from versionoverlord.EnvironmentBase import EnvironmentBase
from versionoverlord.githubadapter.GitHubAdapter import GitHubAdapter


class TemplateHandler(EnvironmentBase):
    """
    Creates a CSV file in the following format:

        PackageName, OldVersion,NewVersion
    """

    def __init__(self, advancedSlugs: AdvancedSlugs):

        super().__init__()

        self.logger:         Logger        = getLogger(__name__)
        self._advancedSlugs: AdvancedSlugs = advancedSlugs

        self._requirementsTxt: str = self._getRequirementsText()

    def createSpecification(self):
        print(f'Creating a specification')
        gitHubAdapter: GitHubAdapter = GitHubAdapter()

        slugVersions: SlugVersions = SlugVersions([])
        for advancedSlug in self._advancedSlugs:

            semanticVersion: SemanticVersion = gitHubAdapter.getLatestVersionNumber(advancedSlug.slug)
            slugVersion:     SlugVersion     = SlugVersion(slug=advancedSlug.slug, version=str(semanticVersion), packageName=advancedSlug.packageName)

            slugVersions.append(slugVersion)

        versionUpdateSpecification: Path = Path(SPECIFICATION_FILE)
        with versionUpdateSpecification.open(mode='w') as fd:
            fd.write(f'PackageName,OldVersion,NewVersion{osLineSep}')
            for slugVersion in slugVersions:

                oldVersion: str = self._findRequirementVersion(slugVersion.packageName)

                if oldVersion == '':
                    print(f'{slugVersion.slug} Did not find requirement')
                else:
                    fd.write(f'{slugVersion.packageName},{oldVersion},{slugVersion.version}{osLineSep}')

    def _findRequirementVersion(self, packageName: str) -> str:
        """
        Can handle requirements specifications like those specified in MATCH_PATTERNS

        For pyproject.toml we have to strip the trailing quote (single or double) and comma

        Args:
            packageName:   The package name to search for

        Returns:  A version number from the requirements text that matches the package name
                  If the requirement is not listed returns an empty string
        """
        match:            Match | None = None
        requirementValue: str          = ''
        for matchPattern in MATCH_PATTERNS:
            lookupRequirement: str = f'{packageName}{matchPattern}.*{osLineSep}'

            # TODO: This regex does not work if the requirement is the last one in the file
            # and there is no blank line at the end
            match = regExSearch(pattern=lookupRequirement, string=self._requirementsTxt)

            self.logger.info(f'{match}')
            if match is None:
                continue
            else:
                fullStr: str = (self._requirementsTxt[match.start():match.end()]).strip(osLineSep)
                splitRequirement = fullStr.split(matchPattern)
                self.logger.info(f'{splitRequirement}')
                requirementValue = splitRequirement[1]
                requirementValue = requirementValue.rstrip(PYPROJECT_TOML_TRAILING_CHARACTERS)
                break

        if match is None:
            return ''
        else:
            return requirementValue

    def _getRequirementsText(self) -> str:
        """

        Returns:  The text of either a requirements.txt or pyproject.toml
        """
        requirementsPath: Path = Path(self._projectsBase) / self._projectDirectory / REQUIREMENTS_TXT
        pyprojectPath:    Path = Path(self._projectsBase) / self._projectDirectory / PYPROJECT_TOML
        if requirementsPath.exists() is True:
            requirementsTxt: str = requirementsPath.read_text()
        elif pyprojectPath.exists() is True:
            requirementsTxt = pyprojectPath.read_text()
        else:
            raise ClickException(f'Cannot find {REQUIREMENTS_TXT} or {PYPROJECT_TOML}')

        return requirementsTxt
