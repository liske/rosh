from socket import AF_INET

from rosh.commands.show.ipv6.neighbour import RoshShowIpv6NeighbourCommand

class RoshShowIpNeighbourCommand(RoshShowIpv6NeighbourCommand):
    def __init__(self, rosh):
        super().__init__(rosh)
        self.family = AF_INET


is_rosh_command = True
rosh_command = RoshShowIpNeighbourCommand
