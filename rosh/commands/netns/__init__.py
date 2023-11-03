from pyroute2 import IPRoute, netns, NetNS

from rosh.commands import RoshCommand
from rosh.completer import netns_completer

class RoshNetnsCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, netns_completer)

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.rosh.ipr = IPRoute()
            return

        ns = args[0]
        if ns not in netns.listnetns():
            print("ERR: netns '{}' does not exist".format(ns))
            return

        self.rosh.ipr = NetNS(ns)

    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in netns.listnetns():
            return (0, f"{args[0]} does not exist")

        return (None, None)

is_rosh_command = True
rosh_command = RoshNetnsCommand
