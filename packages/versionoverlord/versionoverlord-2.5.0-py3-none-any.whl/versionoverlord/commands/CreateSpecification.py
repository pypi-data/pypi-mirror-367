
from pathlib import Path

from click import ClickException
from click import command
from click import option
from click import secho
from click import version_option

from versionoverlord import __version__

from versionoverlord.Common import AdvancedSlugs
from versionoverlord.Common import CLISlugs
from versionoverlord.Common import EPILOG
from versionoverlord.Common import extractCLISlugs

from versionoverlord.Common import setUpLogging

from versionoverlord.FileNameToSlugs import FileNameToSlugs
from versionoverlord.TemplateHandler import TemplateHandler

from versionoverlord.githubadapter.GitHubAdapterError import GitHubAdapterError


# noinspection SpellCheckingInspection
@command(epilog=EPILOG)
@version_option(version=f'{__version__}', message='%(prog)s version %(version)s')
@option('--slugs',     '-s',  multiple=True, required=False, help='Create package update specification')
@option('--input-file', '-i', required=False,                help='Use input file for slug list')
def createSpecification(slugs: CLISlugs, input_file: str):
    """
    \b
    This command creates .csv specification file
    It uses the following environment variables:
    \b
        GH_TOKEN      – A personal GitHub access token necessary to read repository release information
        PROJECTS_BASE – The local directory where the python projects are based
        PROJECT – The name of the project;  It should be a directory name
    """

    try:
        if len(slugs) != 0:
            cliSlugs:        AdvancedSlugs   = extractCLISlugs(slugs=slugs)
            templateHandler: TemplateHandler = TemplateHandler(cliSlugs)

            templateHandler.createSpecification()
        elif input_file is not None:
            fqFileName: Path = Path(input_file)
            # noinspection PySimplifyBooleanCheck
            if fqFileName.exists() is False:
                secho('                          ', fg='red', bg='black', bold=True)
                secho('Input file does not exist ', fg='red', bg='black', bold=True)
                secho('                          ', fg='red', bg='black', bold=True)
            else:
                fileNameToSlugs: FileNameToSlugs = FileNameToSlugs(path=fqFileName)
                fileSlugs:       AdvancedSlugs   = fileNameToSlugs.getSlugs()
                handler:         TemplateHandler = TemplateHandler(advancedSlugs=fileSlugs)

                handler.createSpecification()
    except GitHubAdapterError as e:
        raise ClickException(message=e.message)


if __name__ == "__main__":
    setUpLogging()
    # noinspection SpellCheckingInspection
    # createSpecification(['-i', 'tests/resources/testdata/query.slg'])
    # createSpecification(['-s', 'hasii2011/code-ally-basic,codeallybasic'])
    # -s hasii2011/ -s hasii2011/buildlackey

    createSpecification(['-i', 'docs/query.slg'])
