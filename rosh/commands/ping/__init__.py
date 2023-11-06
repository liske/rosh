import shutil

from rosh.commands import RoshSystemCommand


ping_exe = shutil.which('ping')

class RoshPingCommand(RoshSystemCommand):
    description = 'run ping command'

    def __init__(self, rosh):
        super().__init__(rosh, ping_exe)

is_rosh_command = ping_exe is not None
rosh_command = RoshPingCommand
