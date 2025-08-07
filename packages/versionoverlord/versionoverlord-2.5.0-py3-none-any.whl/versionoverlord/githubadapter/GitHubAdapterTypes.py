
from typing import NewType

from datetime import date

from dataclasses import dataclass

from semantic_version import Version as SemanticVersion

ReleaseTitle   = NewType('ReleaseTitle', str)
ReleaseId      = NewType('ReleaseId',   int)
ReleaseNumber  = NewType('ReleaseNumber', int)


@dataclass
class AdapterMilestone:
    """
    Synthetic class for github.Milestone.Milestone
    """
    title:       str = ''
    state:       str = ''
    description: str = ''
    dueDate:     date | None = date.today()

    releaseNumber: ReleaseNumber = ReleaseNumber(0)
    milestoneUrl:  str           = ''


@dataclass
class AdapterRelease:
    """
    Synthetic class for GitRelease
    """
    body:  str = ''
    draft: bool = True

    title: ReleaseTitle    = ReleaseTitle('')
    tag:   SemanticVersion = SemanticVersion('0.0.0')
    id:    ReleaseId       = ReleaseId(0)
