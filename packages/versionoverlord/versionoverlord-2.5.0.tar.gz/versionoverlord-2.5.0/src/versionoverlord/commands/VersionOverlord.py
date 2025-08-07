from click import clear
from click import command
from click import secho

from click import version_option


from versionoverlord import __version__
from versionoverlord.Common import EPILOG


@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
def versionOverlord():
    clear()
    secho('Commands are:')
    secho('\tvo - versionOverlord')
    secho('\tqs - querySlugs')
    secho('\tcs - createSpecification')
    secho('\tud - updateDependencies')
    secho('\tdr - draftRelease')
    secho('\tbv - bumpVersion')
    secho('\tpd - pickDependencies')
    secho('\tpub - publishRelease')
