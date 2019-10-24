# project
from dephell.commands import VersionCommand
from dephell.config import Config
from dephell import __version__ as dephell_version


def test_version(capsys):
    config = Config()
    config.attach({
        'level': 'WARNING',
        'silent': True,
    })

    command = VersionCommand(argv=[], config=config)
    result = command()

    assert result is True
    assert capsys.readouterr().out.strip() == 'Dephell version: {}'.format(dephell_version)
