from rosh.commands import RoshCommand

class RoshExitCommand(RoshCommand):
    def handler(self, cmd, *args):
        exit(0)

is_rosh_command = True
rosh_command = RoshExitCommand
