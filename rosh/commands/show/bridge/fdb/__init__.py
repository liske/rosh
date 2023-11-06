from socket import AF_BRIDGE

from rosh.commands.show.ipv6.neighbour import RoshShowIpv6NeighbourCommand


class RoshShowBridgeFdbCommand(RoshShowIpv6NeighbourCommand):
    description = 'show bridge forwarding database'

    def __init__(self, rosh):
        super().__init__(rosh, AF_BRIDGE)


is_rosh_command = True
rosh_command = RoshShowBridgeFdbCommand
