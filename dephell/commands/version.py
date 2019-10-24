# built-in
from argparse import ArgumentParser

# app
from .base import BaseCommand
from ..config import builders
from dephell import __version__ as dephell_version


class VersionCommand(BaseCommand):
    """Prints out current Dephell version
    """

    @classmethod
    def get_parser(cls) -> ArgumentParser:
        parser = cls._get_default_parser()
        builders.build_config(parser)
        builders.build_output(parser)
        builders.build_other(parser)
        return parser

    def __call__(self) -> bool:
        print('Dephell version: {}'.format(dephell_version))
        return True
