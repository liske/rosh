from prompt_toolkit import print_formatted_text as print
from pyroute2.netlink.exceptions import NetlinkError

from rosh.commands import RoshCommand
from rosh.completer import link_completer


class RoshDisableInterfaceCommand(RoshCommand):
    description = 'disable (shutdown) an interface'

    def __init__(self, rosh):
        super().__init__(rosh, link_completer, min_args=1)

    def handler(self, filters, cmd, *args):
        for link in self.rosh.ipr.link_lookup(ifname=args[0]):
            try:
                self.handle_link(link)
            except NetlinkError as ex:
                print(f'ERR: {ex.args[1]}')

    def handle_link(self, index):
        self.rosh.ipr.link('set', index=index, state='down')

is_rosh_command = True
rosh_command = RoshDisableInterfaceCommand
