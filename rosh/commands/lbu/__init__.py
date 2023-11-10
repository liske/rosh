from prompt_toolkit.completion import WordCompleter
import shutil

from rosh.commands import RoshSystemCommand


lbu_exe = shutil.which('lbu')

class RoshLbuCommand(RoshSystemCommand):
    description = 'run lbu command'

    def __init__(self, rosh):
        completer = WordCompleter([
            'commit',
            'ci',
            'diff',
            'exclude',
            'include',
            'list',
            'ls',
            'list-backup',
            'lb',
            'package',
            'pkg',
            'revert',
            'status',
            'st'
        ])
        super().__init__(rosh, lbu_exe, completer)

is_rosh_command = lbu_exe is not None
rosh_command = RoshLbuCommand
