
from logging import Logger
from logging import getLogger

from click import secho

from versionoverlord.Common import SlugVersions

PACKAGE_VERSION_GAP: int = 2


class DisplayVersions:
    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    def displaySlugs(self, slugVersions: SlugVersions):

        longestSlug:    int = self._getLongestSlug(slugVersions) + PACKAGE_VERSION_GAP
        slug:           str = 'Slug'
        titleStr:       str = f'{slug:<{longestSlug}}Version'
        titleSeparator: str = '_' * (longestSlug + len('Version'))

        secho(f'{titleStr}')
        secho(f'{titleSeparator}')
        for slugVersion in slugVersions:

            secho(f'{slugVersion.slug:<{longestSlug}}{slugVersion.version}')

        secho('')

    def _getLongestSlug(self, slugVersions: SlugVersions) -> int:
        longest: int = 0
        for slugVersion in slugVersions:
            if len(slugVersion.slug) > longest:
                longest = len(slugVersion.slug)

        return longest
