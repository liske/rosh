import shutils

from rosh.commands import RoshSystemCommand


traceroute_exe = shutil.which('ping')

class RoshTracerouteCommand(RoshSystemCommand):
    def __init__(self, rosh):
        super().__init__(rosh, traceroute_exe)

is_rosh_command = traceroute_exe is not None
rosh_command = RoshTracerouteCommand
