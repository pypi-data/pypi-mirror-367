
from typing import Any
from typing import Optional

from logging import Logger
from logging import getLogger

from click import ParamType
from click import Parameter
from click import Context

from semantic_version import Version as SemanticVersion


class TagType(ParamType):
    name: str = 'TagType'

    def __init__(self):
        self.logger: Logger = getLogger(__name__)

    def convert(self, value: Any, param: Optional['Parameter'], ctx: Optional['Context']) -> Any:

        try:
            version: SemanticVersion = SemanticVersion(value)
            return version
        except ValueError:
            self.fail(f"{value!r} is not a valid semantic version", param, ctx)
