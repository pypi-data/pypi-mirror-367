
from logging import Logger
from logging import getLogger

from requests.exceptions import ConnectionError

from click import ClickException
from click import secho

from semantic_version import Version as SemanticVersion

from versionoverlord.Common import AdvancedSlugs
from versionoverlord.Common import SlugVersion
from versionoverlord.Common import SlugVersions
from versionoverlord.Common import NO_INTERNET_CONNECTION_MSG

from versionoverlord.DisplayVersions import DisplayVersions

from versionoverlord.githubadapter.GitHubAdapter import GitHubAdapter

from versionoverlord.githubadapter.GitHubAdapterError import GitHubAdapterError


class SlugHandler:
    def __init__(self, advancedSlugs: AdvancedSlugs):

        self.logger:         Logger        = getLogger(__name__)
        self._advancedSlugs: AdvancedSlugs = advancedSlugs

    def handleSlugs(self):
        try:
            gitHubAdapter: GitHubAdapter = GitHubAdapter()

            slugVersions: SlugVersions = SlugVersions([])
            for advancedSlug in self._advancedSlugs:

                version:     SemanticVersion = gitHubAdapter.getLatestVersionNumber(advancedSlug.slug)
                slugVersion: SlugVersion     = SlugVersion(slug=advancedSlug.slug, version=str(version))
                slugVersions.append(slugVersion)

            if len(slugVersions) == 0:
                secho('Nothing to see here')
            else:
                displayVersions: DisplayVersions = DisplayVersions()
                displayVersions.displaySlugs(slugVersions=slugVersions)
        except GitHubAdapterError as e:
            raise ClickException(message=e.message)
        except ConnectionError:
            raise ClickException(NO_INTERNET_CONNECTION_MSG)
