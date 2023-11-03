from rosh.commands import RoshCommand

class RoshExitCommand(RoshCommand):
    def handler(self, cmd, *args):
        exit(0)

    def validate(self, cmd, args):
        if len(args) != 0:
            return (0, "no parameters allowed")

        return (None, None)

is_rosh_command = True
rosh_command = RoshExitCommand
