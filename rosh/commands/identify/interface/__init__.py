from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import DummyCompleter
from pyroute2.netlink.exceptions import NetlinkError
import shutil

from rosh.commands import RoshSystemCommand
from rosh.completer import phy_link_completer, RoshPeerCompleter, RoshWordCompleter


ethtool_exe = shutil.which('ethtool')

class RoshIdentifyInterfaceCommand(RoshSystemCommand):
    description = 'initiate the adapter identify by sight procedure'

    def __init__(self, rosh):
        completer = RoshPeerCompleter(
            phy_link_completer,
            DummyCompleter()
        )
        super().__init__(rosh, ethtool_exe, completer, min_args=1)

    def handler(self, filters, cmd, *args):
        super().handler(cmd, '--identify', *args)

is_rosh_command = ethtool_exe is not None
rosh_command = RoshIdentifyInterfaceCommand
