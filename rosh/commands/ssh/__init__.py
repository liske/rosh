import shutil

from rosh.commands import RoshSystemCommand


ssh_exe = shutil.which('ssh')

class RoshSshCommand(RoshSystemCommand):
    description = 'execute ssh command'

    def __init__(self, rosh):
        super().__init__(rosh, ssh_exe)

is_rosh_command = ssh_exe is not None
rosh_command = RoshSshCommand
