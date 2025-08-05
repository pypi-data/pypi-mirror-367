
from logging import Logger
from logging import getLogger

from os import sep as osSep

from click import secho

from buildlackey.Environment import Environment


class RunMypy(Environment):

    def __init__(self, packageName: str, sourceSubDirectory: str, deleteCache: bool):
        super().__init__()
        self.logger:       Logger = getLogger(__name__)

        self._packageName:        str  = packageName
        self._sourceSubDirectory: str  = sourceSubDirectory
        self._deleteCache:        bool = deleteCache

    def execute(self):
        self._changeToProjectRoot()

        if self._packageName is None:
            packageName:        str = self._projectDirectory
        else:
            packageName = self._packageName

        # noinspection PySimplifyBooleanCheck
        if self._deleteCache is True:
            deleteCmd: str = 'rm -rf .mypy_cache'
            secho(f'{deleteCmd}')
            deleteStatus: int = self._runCommand(command=deleteCmd)
            secho(f'{deleteStatus=}')

        sourceSubDirectory: str = self._sourceSubDirectory

        # noinspection SpellCheckingInspection
        cmd: str = (
            f'mypy --config-file .mypi.ini --pretty --no-color-output --show-error-codes --check-untyped-defs '
            f'{sourceSubDirectory}{osSep}{packageName} tests'
        )
        secho(f'{cmd}')

        status: int = self._runCommand(command=cmd)
        secho(f'{status=}')
