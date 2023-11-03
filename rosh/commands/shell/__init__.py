import shutil
import os

from rosh.commands import RoshSystemCommand

shell_exe = os.environ.get('SHELL', shutil.which('sh'))

class RoshShellCommand(RoshSystemCommand):
    def __init__(self, rosh):
        super().__init__(rosh, shell_exe)

is_rosh_command = shell_exe is not None
rosh_command = RoshShellCommand
