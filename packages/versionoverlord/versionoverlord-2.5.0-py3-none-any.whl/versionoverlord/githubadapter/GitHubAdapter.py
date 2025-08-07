
from typing import cast

from logging import Logger
from logging import getLogger

from collections import Counter

from os import environ as osEnvironment

from re import sub as regExSub

from datetime import date
from datetime import timedelta

from github import Github
from github import UnknownObjectException
from github import GithubException

from github.GitRelease import GitRelease
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from github.Milestone import Milestone
from github.Auth import Token

from semantic_version import Version as SemanticVersion

from codeallybasic.Common import fixURL

from versionoverlord.Common import ENV_GH_TOKEN

from versionoverlord.Common import RepositorySlug

from versionoverlord.githubadapter.GitHubAdapterTypes import AdapterMilestone
from versionoverlord.githubadapter.GitHubAdapterTypes import AdapterRelease
from versionoverlord.githubadapter.GitHubAdapterTypes import ReleaseId
from versionoverlord.githubadapter.GitHubAdapterTypes import ReleaseTitle
from versionoverlord.githubadapter.GitHubAdapterTypes import ReleaseNumber

from versionoverlord.githubadapter.GitHubAdapterError import GitHubAdapterError

DEFAULT_MILESTONE_DUE_DATE_DELTA: int = 7
DEFAULT_MILESTONE_STATE:          str = 'open'
DEFAULT_MILESTONE_DESCRIPTION:    str = 'See the associated issues'


class GitHubAdapter:
    """
    TODO:  As more methods get added I need to stop the leakage of GitHub objects

    """
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

        try:
            gitHubToken: str = osEnvironment[ENV_GH_TOKEN]
        except KeyError:
            raise GitHubAdapterError(message=f'No GitHub token specified in `{ENV_GH_TOKEN}`')

        self._github: Github = Github(auth=Token(gitHubToken))

    def getLatestVersionNumber(self, repositorySlug: str) -> SemanticVersion:

        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')
        except UnknownObjectException:
            raise GitHubAdapterError(message=f'Unknown {repositorySlug}')

        releases: PaginatedList = repo.get_releases()

        latestReleaseVersion: SemanticVersion = SemanticVersion('0.0.0')
        for release in releases:
            gitRelease: GitRelease = cast(GitRelease, release)

            # noinspection PySimplifyBooleanCheck
            if gitRelease.draft is True:
                self.logger.warning(f'{repo.full_name} Ignore pre-release {gitRelease.tag_name}')
                continue
            releaseNumber: str = gitRelease.tag_name
            numPeriods: int = self._countPeriods(releaseNumber)
            if numPeriods < 2:
                releaseNumber = f'{releaseNumber}.0'

            releaseVersion: SemanticVersion = SemanticVersion.coerce(releaseNumber)
            self.logger.debug(f'{releaseVersion=}')
            if latestReleaseVersion < releaseVersion:
                latestReleaseVersion = releaseVersion

        return latestReleaseVersion

    def createDraftRelease(self, repositorySlug: RepositorySlug, tag: SemanticVersion, message: str) -> AdapterRelease:
        """

        Args:
            repositorySlug:   A GitHub repository slug
            tag:              The tag number
            message:          Text to put into release

        Returns:  The GitHub AdapterRelease Id

        """
        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')
            releaseName: ReleaseTitle = ReleaseTitle(f'Release {tag}')

            gitRelease: GitRelease = repo.create_git_release(tag=str(tag),
                                                             name=releaseName,
                                                             message=message,
                                                             draft=True,
                                                             prerelease=False,
                                                             generate_release_notes=False)

        except UnknownObjectException:
            raise GitHubAdapterError(message=f'Unknown {repositorySlug}')

        release: AdapterRelease = AdapterRelease(
            id=ReleaseId(gitRelease.id),
            draft=gitRelease.draft,
            title=ReleaseTitle(gitRelease.title),
            body=gitRelease.body,
            tag=SemanticVersion(gitRelease.tag_name)
        )
        return release

    def createMilestone(self, repositorySlug: RepositorySlug, title: str) -> AdapterMilestone:
        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')

            today: date = date.today() + timedelta(days=DEFAULT_MILESTONE_DUE_DATE_DELTA)

            milestone: Milestone = repo.create_milestone(title=title,
                                                         state=DEFAULT_MILESTONE_STATE,
                                                         description=DEFAULT_MILESTONE_DESCRIPTION,
                                                         due_on=today)
            #
            # Milestone does not provide the HTML URL;  I have to coerce one
            #
            fixedURL:   str = fixURL(milestone.url)
            coercedURL: str = regExSub(pattern=r'milestones', repl='milestone', string=fixedURL)
            adapterMilestone: AdapterMilestone = AdapterMilestone(
                releaseNumber=ReleaseNumber(milestone.number),
                title=milestone.title,
                state=milestone.state,
                description=milestone.description,
                dueDate=milestone.due_on,
                milestoneUrl=coercedURL,
            )
            return adapterMilestone

        except GithubException as ge:
            raise GitHubAdapterError(message=ge.__str__())

    def deleteMilestone(self, repositorySlug: RepositorySlug, releaseNumber: ReleaseNumber):
        """

        Args:
            repositorySlug: A GitHub repository slug
            releaseNumber:  An adapter ReleaseNumber
        """
        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')

            milestone: Milestone = repo.get_milestone(number=releaseNumber)
            milestone.delete()

        except GithubException as ge:
            raise GitHubAdapterError(message=ge.__str__())

    def deleteRelease(self, repositorySlug: RepositorySlug, releaseId: int):
        """

        Args:
            repositorySlug: A GitHub repository slug
            releaseId:      A git release ID

        """
        try:
            repo: Repository = self._github.get_repo(repositorySlug)
            self.logger.debug(f'{repo.full_name=}')

            gitRelease: GitRelease = repo.get_release(id=releaseId)
            gitRelease.delete_release()

        except UnknownObjectException as e:
            # self.logger.error(f'{releaseId=} {e=}')
            raise GitHubAdapterError(message=f'Release ID not found. {e=}')

    def publishRelease(self, repositorySlug: RepositorySlug, releaseTitle: ReleaseTitle):

        try:
            repo: Repository = self._github.get_repo(repositorySlug)

            releases: PaginatedList = repo.get_releases()
            # list comprehension;  Aren't I cute . . . . . .
            matchedReleases = [r for r in releases if r.title == releaseTitle]

            if len(matchedReleases) != 1:
                raise GitHubAdapterError(f'Cannot find that release: {releaseTitle}')

            matchedRelease: GitRelease = matchedReleases[0]
            matchedRelease.update_release(name=matchedRelease.title, message=matchedRelease.body, draft=False)

        except GithubException as ge:
            raise GitHubAdapterError(message=ge.__str__())

    def _countPeriods(self, releaseNumber: str) -> int:

        cnt = Counter(list(releaseNumber))
        return cnt['.']
