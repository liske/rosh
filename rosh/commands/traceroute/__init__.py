import shutil

from rosh.commands import RoshSystemCommand


traceroute_exe = shutil.which('traceroute')

class RoshTracerouteCommand(RoshSystemCommand):
    description = 'run traceroute command'

    def __init__(self, rosh):
        super().__init__(rosh, traceroute_exe)

is_rosh_command = traceroute_exe is not None
rosh_command = RoshTracerouteCommand
