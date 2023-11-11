from rosh.commands.disable.interface import RoshDisableInterfaceCommand


class RoshEnableInterfaceCommand(RoshDisableInterfaceCommand):
    description = 'enable (no shutdown) an interface'

    def handle_link(self, index):
        self.rosh.ipr.link('set', index=index, state='up')

is_rosh_command = True
rosh_command = RoshEnableInterfaceCommand
