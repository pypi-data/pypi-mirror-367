
from typing import List

from logging import Logger
from logging import getLogger

from pathlib import Path

from os import linesep as osLineSep

from versionoverlord.Common import AdvancedSlug
from versionoverlord.Common import AdvancedSlugs
from versionoverlord.Common import extractPackageName


class FileNameToSlugs:
    def __init__(self, path: Path):
        self.logger: Logger = getLogger(__name__)

        self._fqFileName: Path = path

    def getSlugs(self) -> AdvancedSlugs:

        slugString: str        = self._fqFileName.read_text()
        slugList:   List[str] = slugString.split(sep=osLineSep)

        cleanList: List[str] = list(filter(None, slugList))

        advancedSlugs: AdvancedSlugs = AdvancedSlugs([])
        for slug in cleanList:
            splitSlug:    List[str]    = slug.split(',')
            advancedSlug: AdvancedSlug = AdvancedSlug()
            if len(splitSlug) > 1:
                advancedSlug.slug        = splitSlug[0]
                advancedSlug.packageName = splitSlug[1]
            else:
                advancedSlug.slug        = slug
                advancedSlug.packageName = extractPackageName(slug=slug)
            advancedSlugs.append(advancedSlug)

        return advancedSlugs
