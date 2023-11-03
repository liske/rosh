from rosh.commands import RoshSystemCommand

class RoshPingCommand(RoshSystemCommand):
    def __init__(self, rosh):
        super().__init__(rosh, 'ping')

is_rosh_command = True
rosh_command = RoshPingCommand
