import shutil

from rosh.commands import RoshCommand


class RoshHelpCommand(RoshCommand):
    description = 'show command help'

    def __init__(self, rosh):
        super().__init__(rosh)

    def handler(self, filters, cmd, *args):
        self.rosh.dump_commands(filters)

is_rosh_command = True
rosh_command = RoshHelpCommand
