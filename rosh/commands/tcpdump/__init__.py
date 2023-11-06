import shutil

from rosh.commands import RoshSystemCommand


tcpdump_exe = shutil.which('tcpdump')

class RoshTcpdumpCommand(RoshSystemCommand):
    description = 'run tcpdump command'

    def __init__(self, rosh):
        super().__init__(rosh, tcpdump_exe)

is_rosh_command = tcpdump_exe is not None
rosh_command = RoshTcpdumpCommand
