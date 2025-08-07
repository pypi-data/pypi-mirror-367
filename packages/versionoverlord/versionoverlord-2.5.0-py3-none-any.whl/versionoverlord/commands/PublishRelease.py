
from click import command
from click import option
from click import version_option
from click import ClickException

from os import environ as osEnvironment

from requests.exceptions import ConnectionError

from versionoverlord import __version__
from versionoverlord.Common import ENV_REPO_SLUG

from versionoverlord.Common import EPILOG
from versionoverlord.Common import NO_REPO_SLUG_MSG
from versionoverlord.Common import RepositorySlug
from versionoverlord.Common import setUpLogging
from versionoverlord.Common import NO_INTERNET_CONNECTION_MSG

from versionoverlord.githubadapter.GitHubAdapter import GitHubAdapter
from versionoverlord.githubadapter.GitHubAdapterTypes import ReleaseTitle
from versionoverlord.githubadapter.GitHubAdapterError import GitHubAdapterError


@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--slug',          '-s', required=False,  help='GitHub slug')
@option('--release-title', '-r', required=True,   help='The title of the release to publish')
def publishRelease(slug: RepositorySlug, release_title: ReleaseTitle):
    """
    \b
    The short name is 'pub' instead of 'pr' so as not to conflict with the *nix command
    for print files

    \b
    This command publishes a draft release in the appropriate repository.
    You can provide a repository slug.

    \b
    It uses the following environment variables:

    \b
        GH_TOKEN      – A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE – The local directory where the python projects are based
        PROJECT       – The name of the project;  It should be a directory name
        REPO_SLUG     - Used if the developer does not provide the option --slug/-s
    """
    if slug is None:
        try:
            realSlug: RepositorySlug = RepositorySlug(osEnvironment[ENV_REPO_SLUG])
        except KeyError:
            raise ClickException(NO_REPO_SLUG_MSG)
    else:
        realSlug = slug

    try:
        gitHubAdapter: GitHubAdapter = GitHubAdapter()

        gitHubAdapter.publishRelease(repositorySlug=realSlug, releaseTitle=release_title)

    except GitHubAdapterError as e:
        raise ClickException(message=e.message)
    except ConnectionError:
        raise ClickException(NO_INTERNET_CONNECTION_MSG)


if __name__ == "__main__":
    setUpLogging()

    # publishRelease(['--version'])
    # publishRelease(['--help'])
    publishRelease(['--slug', 'hasii2011/TestRepository', '--release-title', 'Fake Release Name'])
