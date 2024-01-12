import shutil
import os
from prompt_toolkit.formatted_text import FormattedText

from rosh.commands import RoshSystemCommand

shell_exe = os.environ.get('SHELL', shutil.which('sh'))

class RoshShellCommand(RoshSystemCommand):
    description = 'launch a interactive system shell'

    def __init__(self, rosh):
        super().__init__(rosh, shell_exe, env=self.get_env)

    def get_env(self):
        ps1 = [f'\[\e[37;42m\] {self.rosh.symbols.router} \h ']

        if getattr(self.rosh.ipr, 'netns', None):
            ps1.append(f'\[\e[32;43m\]{self.rosh.symbols.delimiter}\[\e[37;43m\] {self.rosh.ipr.netns} \[\e[0;33m\]{self.rosh.symbols.delimiter}')
        else:
            ps1.append(f'\[\e[0;32m\]{self.rosh.symbols.delimiter}')

        ps1.append('\[\e[0m\] \w# ')

        env = os.environ.copy()
        env['PS1'] = ''.join(ps1)

        return env

    def handler(self, filters, cmd, *args):
        if self.cmd == 'bash' or self.cmd.endswith('/bash'):
            super().handler(filters, cmd, '--norc', *args)
        else:
            super().handler(filters, cmd, *args)

is_rosh_command = shell_exe is not None
rosh_command = RoshShellCommand
