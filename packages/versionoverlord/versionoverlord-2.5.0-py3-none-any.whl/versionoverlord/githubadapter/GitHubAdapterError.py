
class GitHubAdapterError(Exception):
    def __init__(self, message):
        self._message = message

    @property
    def message(self) -> str:
        return self._message
