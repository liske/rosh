from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import DummyCompleter
from pyroute2.netlink.exceptions import NetlinkError
import shutil

from rosh.commands import RoshSystemCommand
from rosh.completer import phy_link_completer, RoshPeerCompleter, RoshWordCompleter


ethtool_exe = shutil.which('ethtool')

class RoshResetInterfaceCommand(RoshSystemCommand):
    description = 'reset an interface'

    def __init__(self, rosh):
        completer = RoshPeerCompleter(
            phy_link_completer,
            RoshPeerCompleter(
                RoshWordCompleter([
                    'flags',
                    'mgmt',
                    'irq',
                    'dma',
                    'filter',
                    'offload',
                    'mac',
                    'phy',
                    'ram',
                    'dedicated',
                    'all'
                ]),
                DummyCompleter()
            )
        )
        super().__init__(rosh, ethtool_exe, completer, min_args=2)

    def handler(self, cmd, *args):
        super().handler(cmd, '--reset', *args)

is_rosh_command = ethtool_exe is not None
rosh_command = RoshResetInterfaceCommand
