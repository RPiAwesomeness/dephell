import re
import subprocess
from pathlib import Path

from cached_property import cached_property

from ..base import Interface
from ...constants import CACHE_DIR
from ...utils import chdir
from ...models.release import Release

try:
    from dateutil.parser import isoparse
except ImportError:
    from dateutil.parser import parse as isoparse


rex_author = re.compile(r'$/([a-zA-Z_-])')


class GitRepo(Interface):
    _ready = False
    name = 'git'

    def __init__(self, link):
        self.link = link

    def _call(self, *args, path=None) -> tuple:
        if path is None:
            path = self.path
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        with chdir(path):
            result = subprocess.call([self.name] + args)
        return tuple(result.stdout.decode().split('\n'))

    def _get_tags(self) -> tuple:
        log = self._call('git', 'show-ref', '--tags')
        return tuple(line.split() for line in log)

    def _get_commits(self) -> tuple:
        log = self._call('log', r'format="%H %cI"')
        return tuple(line.split() for line in log)

    @cached_property
    def path(self):
        name = self.link.name
        path = Path(CACHE_DIR) / 'git' / name
        return path

    def _setup(self, *, force: bool=False) -> None:
        if self._ready and not force:
            return

        if not self.path.exists():
            self._call(
                'git', 'clone', self.link.short, self.path.name,
                path=self.path.parent,
            )
        else:
            self._call('git', 'fetch')
        if self.link.rev:
            self._call('git', 'checkout', self.link.rev)

    def get_releases(self, dep) -> tuple:
        releases = []
        self._setup()
        commits = dict(self._get_commits())

        # add tags to releases
        # rev -- commit hash (2d6989d9bcb7fe250a7e55d8e367ac1e0c7d7f55)
        # ref -- tag name (refs/tags/v0.1.0)
        for rev, ref in self._get_tags():
            release = Release(
                raw_name=dep.raw_name,
                version=ref.replace('refs/tags/', ''),
                time=isoparse(commits[rev]),
            )
            releases.append(release)

        # add current revision to releases
        if self.link.rev:
            release = Release(
                raw_name=dep.raw_name,
                version=self.link.rev,
                time=isoparse(commits[self.link.rev]),
            )
            releases.append(release)
        return tuple(releases)

    async def get_dependencies(self, name: str, version: str) -> tuple:
        ...
