from rosh.commands import RoshSystemCommand

class RoshTracerouteCommand(RoshSystemCommand):
    def __init__(self, rosh):
        super().__init__(rosh, 'traceroute')

is_rosh_command = True
rosh_command = RoshTracerouteCommand
