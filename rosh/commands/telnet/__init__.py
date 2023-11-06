import shutil

from rosh.commands import RoshSystemCommand


telnet_exe = shutil.which('telnet')

class RoshTelnetCommand(RoshSystemCommand):
    description = 'run telnet command'

    def __init__(self, rosh):
        super().__init__(rosh, telnet_exe)
        self.enable_sigterm = False

is_rosh_command = telnet_exe is not None
rosh_command = RoshTelnetCommand
